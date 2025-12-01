from django.contrib import admin
from django.utils.html import format_html
from .models import Publication, PublicationImage


class PublicationImageInline(admin.TabularInline):
    """Inline admin for managing multiple images per publication"""
    model = PublicationImage
    extra = 1  # Show 1 empty form by default
    fields = ('image', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 150px;" />', obj.image.url)
        return 'No image'
    image_preview.short_description = 'Preview'


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'type', 'content_type', 'show_button', 'email', 'created_at')
    list_filter = ('type', 'content_type', 'show_button', 'email', 'created_at')
    search_fields = ('title', 'sub_text', 'content')
    
    fieldsets = (
        ('Main Info', {
            'fields': ('type', 'image', 'alt', 'video_id', 'title', 'sub_text')
        }),
        ('Content', {
            'fields': ('content_type', 'content', 'content1', 'content2')
        }),
        ('Button Settings', {
            'fields': ('show_button', 'button_on_hover', 'button_color', 'pdf_file')
        }),
        ('Other Settings', {
            'fields': ('email', 'rounded_img', 'elevation')
        }),
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


@admin.register(PublicationImage)
class PublicationImageAdmin(admin.ModelAdmin):
    """Admin for managing publication images directly"""
    list_display = ('id', 'image', 'publication', 'image_preview', 'created_at')
    list_display_links = ('id',)
    list_filter = ('created_at',)
    search_fields = ('publication__title',)
    readonly_fields = ('image_preview',)
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        # Remove icons/links for publication field
        if db_field.name == 'publication':
            formfield.widget.can_add_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_view_related = False
            formfield.widget.can_delete_related = False
        return formfield
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 150px;" />', obj.image.url)
        return 'No image'
    image_preview.short_description = 'Preview'

