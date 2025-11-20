from django.contrib import admin
from django import forms
from django.forms import CheckboxSelectMultiple
from django.utils.html import format_html
from .models import Author, Post, Comment, Tag, PostImage
from django.db.models import Max



from django.forms.models import BaseInlineFormSet
class AutoOrderInlineFormSet(BaseInlineFormSet):
    def save_new(self, form, commit=True):
        obj = super().save_new(form, commit=False)
        # Assign order if not set or duplicate
        if not obj.order or obj.order == 0 or obj.post.images.filter(order=obj.order).exists():
            max_order = obj.post.images.aggregate(Max('order'))['order__max']
            obj.order = (max_order or 0) + 1
        if commit:
            obj.save()
        return obj
        return obj

class PostImageInline(admin.TabularInline):

    """Inline admin for managing multiple images per post"""
    model = PostImage
    extra = 1  # Show 1 empty form by default
    fields = ('order', 'image', 'image_preview')
    readonly_fields = ('order', 'image_preview')
    formset = AutoOrderInlineFormSet

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
    # show status (Draft/Published) in the list;
    # add `is_published` boolean column (derived from status) so admin shows the green/red icon
    list_display = ('id', 'title', 'author', 'published', 'created_at', 'tags_list', 'gallery_count')
    list_editable = ('published',)
    list_filter = ('author', 'published', 'tags')
    readonly_fields = ()
    search_fields = ('title', 'author__name', 'tags__name')
    # CheckboxSelectMultiple and a simple checklist of tags.
    # Speed up author lookups for large user sets
    raw_id_fields = ('author',)
    inlines = [PostImageInline]  # Add inline image management


    class PostForm(forms.ModelForm):
        class Meta:
            model = Post
            fields = '__all__'
            widgets = {
                'tags': CheckboxSelectMultiple,
            }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Remove green plus button for tags
            self.fields['tags'].widget.can_add_related = False
            # Remove green plus button for tags
            # This disables the add-another button for tags in the admin form
            autocomplete_fields = []

    form = PostForm

    # No need for is_published method; use boolean field directly

    def tags_list(self, obj):
        """Return a comma-separated list of tag names for the post."""
        return ", ".join([t.name for t in obj.tags.all()])
    tags_list.short_description = 'Tags'
    tags_list.admin_order_field = 'tags__name'

    def gallery_count(self, obj):
        """Show the number of images in the gallery"""
        count = obj.images.count()
        if count > 0:
            return format_html('<span style="color: green;">📷 {}</span>', count)
        return '—'
    gallery_count.short_description = 'Gallery Images'


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

@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    """Admin for managing post images directly"""
    list_display = ('order', 'image', 'id', 'post', 'caption', 'is_cover', 'image_preview', 'created_at')
    list_display_links = ('id',)
    list_filter = ('is_cover', 'created_at')
    search_fields = ('post__title', 'caption')
    list_editable = ('order', 'is_cover')
    readonly_fields = ('image_preview',)
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 150px;" />', obj.image.url)
        return 'No image'
    image_preview.short_description = 'Preview'
