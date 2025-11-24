from django.db import models


class PublicationType(models.TextChoices):
    PUBLICATION = 'publication', 'Publication'
    BROCHURE = 'brochure', 'Brochure'


class Publication(models.Model):
    """Model for storing publications and brochures with PDF files"""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, help_text="Optional description of the publication/brochure")
    pdf_file = models.FileField(upload_to='publications/', help_text="Upload PDF file for this publication/brochure")
    publication_type = models.CharField(
        max_length=20,
        choices=PublicationType.choices,
        default=PublicationType.PUBLICATION,
        help_text="Select whether this is a publication or brochure"
    )
    # Event/Conference information (optional, for publications presented at events)
    event_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Name of the event or conference (e.g., 'EAGE Annual')"
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        help_text="Location or venue (e.g., 'Vienna, Austria')"
    )
    event_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of the event or publication (e.g., June 2023)"
    )
    published = models.BooleanField(default=False, help_text="Check to make this available for download")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Publication'
        verbose_name_plural = 'Publications'

    def __str__(self):
        return f"{self.get_publication_type_display()}: {self.title}"

