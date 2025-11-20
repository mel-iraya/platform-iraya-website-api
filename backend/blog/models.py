from django.db import models
from django.utils.text import slugify
from django.utils import timezone
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
    # status: draft or published
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Tags: allow multiple labels such as 'News', 'Events', 'Conference', etc.
    tags = models.ManyToManyField('Tag', related_name='posts', blank=True)
    
        def get_content_markdown(self):
            import markdown
            return markdown.markdown(self.content)

    @property
    def published(self):
        """Derived property from status field - returns True if status is 'published'"""
        return self.status == self.STATUS_PUBLISHED

    def save(self, *args, **kwargs):
        # auto-generate slug when missing
        if not self.slug:
            self.slug = slugify(self.title)[:255]

        # set published_at timestamp when publishing
        if self.status == self.STATUS_PUBLISHED:
            if not self.published_at:
                self.published_at = timezone.now()

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
    order = models.PositiveIntegerField(default=0, help_text="Order of image in gallery (lower numbers appear first)")
    is_cover = models.BooleanField(default=False, help_text="Mark this image as the cover/featured image")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'Post Image'
        verbose_name_plural = 'Post Images'

    def __str__(self):
        return f"Image for {self.post.title} (Order: {self.order})"

    def save(self, *args, **kwargs):
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
        """Returns the display name for the comment author"""
        if self.user:
            return self.user.get_full_name() or self.user.username
        return self.author_name or 'Anonymous'