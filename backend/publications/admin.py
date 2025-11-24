from django.contrib import admin
from django.utils.html import format_html
from .models import Publication


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'publication_type', 'event_name', 'location', 'event_date', 'published', 'pdf_file_link', 'created_at')
    list_editable = ('published',)
    list_filter = ('publication_type', 'published', 'event_date', 'created_at')
    search_fields = ('title', 'description', 'event_name', 'location')
    
    fields = (
        'title',
        'description',
        'publication_type',
        'event_name',
        'location',
        'event_date',
        'pdf_file',
        'published',
    )

    def pdf_file_link(self, obj):
        """Display a link to the PDF file"""
        if obj.pdf_file:
            return format_html(
                '<a href="{}" target="_blank">View PDF</a>',
                obj.pdf_file.url
            )
        return 'No file'
    pdf_file_link.short_description = 'PDF File'

