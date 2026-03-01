from django.db import models
from django.utils.text import slugify
from django.utils import timezone
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
    # add optional thumbnail upload for posts
    thumbnail = models.ImageField(upload_to='posts/', null=True, blank=True)
    video = models.FileField(upload_to='posts/videos/', null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    content = models.TextField()
    # status: draft or published
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT, db_index=True)
    # kept for compatibility; derived from status on save
    published = models.BooleanField(default=False, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Tags: allow multiple labels such as 'News', 'Events', 'Conference', etc.
    tags = models.ManyToManyField('Tag', related_name='posts', blank=True)

    def save(self, *args, **kwargs):
        # auto-generate slug when missing
        if not self.slug:
            self.slug = slugify(self.title)[:255]

        # derive published boolean and published_at from status
        if self.status == self.STATUS_PUBLISHED:
            self.published = True
            if not self.published_at:
                self.published_at = timezone.now()
        else:
            self.published = False

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class PostImage(models.Model):
    post = models.ForeignKey(Post, related_name='uploaded_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='posts/gallery/')

    def __str__(self):
        return f"Image for {self.post.title}"

class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=64, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)[:64]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author_name = models.CharField(max_length=100)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=True)

    def __str__(self):
        return f"Comment by {self.author_name} on {self.post_id}"


class Publication(models.Model):
    # Core explicit UI fields matched from publications.js
    title = models.CharField(max_length=255)
    sub_text = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    
    # either 'content' or 'list'
    content_type = models.CharField(max_length=20, default='content') 
    content1 = models.TextField(blank=True, null=True)
    content2 = models.TextField(blank=True, null=True)

    # either 'image' or 'video'
    type = models.CharField(max_length=20, default='image')
    image = models.ImageField(upload_to='publications/', null=True, blank=True)
    static_image_path = models.CharField(max_length=255, null=True, blank=True)
    video_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Download link to be filled later
    download_link = models.URLField(max_length=500, blank=True, null=True)
    
    # UI Control Flags
    show_button = models.BooleanField(default=True)
    button_on_hover = models.BooleanField(default=False)
    button_color = models.CharField(max_length=50, default='primary')
    elevation = models.CharField(max_length=10, default='0')
    email = models.BooleanField(default=False)
    rounded_img = models.BooleanField(default=False)
    
    # DB Metadata
    status = models.CharField(max_length=10, choices=Post.STATUS_CHOICES, default=Post.STATUS_PUBLISHED)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class WelcomePopup(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='popups/', null=True, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.is_active:
            # ensure only one popup is active at a time
            WelcomePopup.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Brochure(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='brochures/', null=True, blank=True)
    image_max_width = models.CharField(default="400px", max_length=50)
    image_max_height = models.CharField(default="380px", max_length=50)
    card_height = models.IntegerField(default=350)
    text_content = models.TextField()
    text_column_classes = models.CharField(default="pl-xl-2 pl-md-16 mt-6", max_length=255)
    button_elevation = models.CharField(default='3', max_length=50)
    button_color = models.CharField(default='primary-lighten-1', max_length=50)
    button_hover_success = models.BooleanField(default=True)
    file = models.FileField(upload_to='brochures/pdfs/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title