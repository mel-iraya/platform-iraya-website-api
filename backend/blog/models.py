from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


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
        # Auto-generate slug from title if not provided
        if not self.slug:
            self.slug = slugify(self.title)[:255]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=64, unique=True, blank=True)

    def save(self, *args, **kwargs):
        # Auto-generate slug from name if not provided
        if not self.slug:
            self.slug = slugify(self.name)[:64]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class PostImage(models.Model):
    """Model for storing multiple images per post with gallery support"""
    post = models.ForeignKey(Post, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='post_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Post Image'
        verbose_name_plural = 'Post Images'

    def __str__(self):
        return f"Image for {self.post.title}"


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