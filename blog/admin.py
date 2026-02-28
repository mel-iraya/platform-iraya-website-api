from django.contrib import admin
from django import forms
from django.forms import CheckboxSelectMultiple
from django.utils.html import format_html
from .models import Author, Post, Comment, Tag, Publication, WelcomePopup, PostImage

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1

@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
	list_display = ('id', 'post', 'image')
	search_fields = ('post__title',)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'email', 'created_at')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
	# show status (Draft/Published) in the list;
	# add `is_published` boolean column (derived from status) so admin shows the green/red icon
	list_display = ('id', 'title', 'author', 'is_published', 'status', 'created_at', 'tags_list', 'thumbnail_tag')
	list_filter = ('author', 'status', 'tags')
	readonly_fields = ('thumbnail_tag',)
	search_fields = ('title', 'author__name', 'tags__name')
	# CheckboxSelectMultiple and a simple checklist of tags.
	# Speed up author lookups for large user sets
	raw_id_fields = ('author',)
	inlines = [PostImageInline]


	class PostForm(forms.ModelForm):
		class Meta:
			model = Post
			fields = '__all__'
			widgets = {
				'tags': CheckboxSelectMultiple,
			}

		def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)
			from .models import Tag
			DEFAULT_NAMES = ['News', 'Events', 'Conference', 'New Energy']
			self.fields['tags'].queryset = Tag.objects.filter(name__in=DEFAULT_NAMES)

	form = PostForm

	def thumbnail_tag(self, obj):
		if obj.thumbnail:
			return format_html('<img src="{}" style="max-height: 100px;" />', obj.thumbnail.url)
		return ''
	thumbnail_tag.short_description = 'Thumbnail'

	def is_published(self, obj):
		"""Boolean column derived from `status`.
		Returns True when status == 'published'. Django admin will render a green icon for True.
		"""
		return getattr(obj, 'status', '') == 'published'
	is_published.boolean = True
	is_published.short_description = 'Published'

	def tags_list(self, obj):
		"""Return a comma-separated list of tag names for the post."""
		return ", ".join([t.name for t in obj.tags.all()])
	tags_list.short_description = 'Tags'
	tags_list.admin_order_field = 'tags__name'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
	list_display = ('id', 'post', 'author_name', 'approved', 'created_at')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'slug')
	search_fields = ('name',)
	prepopulated_fields = {'slug': ('name',)}


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'type', 'status', 'created_at')
	list_filter = ('type', 'status', 'content_type')
	search_fields = ('title', 'sub_text')


@admin.register(WelcomePopup)
class WelcomePopupAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'is_active', 'created_at')
	list_filter = ('is_active',)
	search_fields = ('title',)
