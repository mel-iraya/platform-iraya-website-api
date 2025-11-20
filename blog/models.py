from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
# Create your models here.

class Author(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    author = models.ForeignKey(Author, related_name='posts', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    content = models.TextField()
    published = models.BooleanField(default=False, help_text="Check to mark this post as published.")
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField('Tag', related_name='posts', blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:255]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=64, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:64]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class PostImage(models.Model):
    """Model for storing multiple images per post with gallery support"""
    post = models.ForeignKey(Post, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='post_images/')
    caption = models.CharField(max_length=255, blank=True, help_text="Optional caption for the image")
    order = models.PositiveIntegerField(default=0)
    is_cover = models.BooleanField(default=False, help_text="Mark this image as the cover/featured image")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'Post Image'
        verbose_name_plural = 'Post Images'

    def __str__(self):
        return f"Image for {self.post.title} (Order: {self.order})"

    def save(self, *args, **kwargs):
        # Auto-assign order if not set or duplicate
        if self.order == 0 or PostImage.objects.filter(post=self.post, order=self.order).exclude(pk=self.pk).exists():
            max_order = PostImage.objects.filter(post=self.post).exclude(pk=self.pk).aggregate(models.Max('order'))['order__max']
            self.order = (max_order or 0) + 1
        # If this is marked as cover, unmark all other images for this post
        if self.is_cover:
            PostImage.objects.filter(post=self.post, is_cover=True).exclude(pk=self.pk).update(is_cover=False)
        super().save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='comments', on_delete=models.SET_NULL, null=True, blank=True, help_text="Logged-in user who made the comment")
    author_name = models.CharField(max_length=100, blank=True, help_text="Name for anonymous comments (when user is not logged in)")
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=True)

    def __str__(self):
        if self.user:
            return f"Comment by {self.user.username} on {self.post.title}"
        return f"Comment by {self.author_name or 'Anonymous'} on {self.post.title}"

    def get_author_display(self):
        if self.user:
            return self.user.get_full_name() or self.user.username
        return self.author_name or 'Anonymous'