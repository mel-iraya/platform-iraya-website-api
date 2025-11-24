from django.contrib import admin
from django import forms
from django.forms import CheckboxSelectMultiple
from django.utils.html import format_html
from .models import Author, Post, Comment, Tag, PostImage


class PostImageInline(admin.TabularInline):
    """Inline admin for managing multiple images per post"""
    model = PostImage
    extra = 1  # Show 1 empty form by default
    fields = ('image', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 150px;" />', obj.image.url)
        return 'No image'
    image_preview.short_description = 'Preview'


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'created_at')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'published', 'created_at', 'tags_list', 'cover_photo')
    list_editable = ('published',)
    list_filter = ('author', 'published', 'tags')
    readonly_fields = ()
    search_fields = ('title', 'author__name', 'tags__name')
    inlines = [PostImageInline]


    class PostForm(forms.ModelForm):
        class Meta:
            model = Post
            fields = '__all__'
            widgets = {
                'tags': CheckboxSelectMultiple,  # Use checkboxes instead of dropdown
            }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Disable "add another" button for tags (tags should be managed separately)
            self.fields['tags'].widget.can_add_related = False

    form = PostForm
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        # Remove icons/links for author field
        if db_field.name == 'author':
            formfield.widget.can_add_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_view_related = False
            formfield.widget.can_delete_related = False
        return formfield

    def tags_list(self, obj):
        """Return a comma-separated list of tag names for the post."""
        return ", ".join([t.name for t in obj.tags.all()])
    tags_list.short_description = 'Tags'
    tags_list.admin_order_field = 'tags__name'

    def cover_photo(self, obj):
        """Display the cover photo (first image) for the post"""
        first_image = obj.images.first()
        if first_image and first_image.image:
            return format_html('<img src="{}" style="max-height: 60px; max-width: 80px; object-fit: cover; border-radius: 4px;" />', first_image.image.url)
        return '—'
    cover_photo.short_description = 'COVER PHOTO'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'author_name', 'approved', 'created_at')
    list_filter = ('approved', 'created_at')
    search_fields = ('post__title', 'author_name', 'body')
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        # Remove icons/links for post and user fields
        if db_field.name in ['post', 'user']:
            formfield.widget.can_add_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_view_related = False
            formfield.widget.can_delete_related = False
        return formfield


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    """Admin for managing post images directly"""
    list_display = ('id', 'image', 'post', 'image_preview', 'created_at')
    list_display_links = ('id',)
    list_filter = ('created_at',)
    search_fields = ('post__title',)
    readonly_fields = ('image_preview',)
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        # Remove icons/links for post field
        if db_field.name == 'post':
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
