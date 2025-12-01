from django.db import models





class Publication(models.Model):
    """Model for storing publications matching the frontend structure"""
    TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    CONTENT_TYPE_CHOICES = [
        ('content', 'Content'),
        ('list', 'List'),
    ]

    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='image')
    image = models.ImageField(upload_to='publications/images/', blank=True, null=True)
    alt = models.CharField(max_length=255, blank=True)
    video_id = models.CharField(max_length=255, blank=True, help_text="YouTube Video ID")
    
    title = models.CharField(max_length=255)
    sub_text = models.CharField(max_length=255, blank=True)
    
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES, default='content')
    content = models.TextField(blank=True)
    content1 = models.TextField(blank=True, help_text="First list item")
    content2 = models.TextField(blank=True, help_text="Second list item")
    
    show_button = models.BooleanField(default=True)
    button_on_hover = models.BooleanField(default=False)
    button_color = models.CharField(max_length=50, default='primary')
    
    email = models.BooleanField(default=False)
    rounded_img = models.BooleanField(default=False)
    elevation = models.CharField(max_length=10, blank=True, default='0')

    # Keep existing useful fields
    pdf_file = models.FileField(upload_to='publications/', blank=True, null=True, help_text="Upload PDF file for download button")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Publication'
        verbose_name_plural = 'Publications'

    def __str__(self):
        return self.title


class PublicationImage(models.Model):
    """Model for storing multiple images per publication with gallery support"""
    publication = models.ForeignKey(Publication, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='publication_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Publication Image'
        verbose_name_plural = 'Publication Images'

    def __str__(self):
        return f"Image for {self.publication.title}"

