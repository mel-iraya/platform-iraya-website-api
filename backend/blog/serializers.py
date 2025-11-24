from rest_framework import serializers
from django.conf import settings
from .models import Post, Comment, PostImage, Tag, Author
import markdown as md

class PostImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = PostImage
        fields = ['id', 'image', 'created_at']
    
    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            # Fallback: build absolute URL for development
            # This ensures frontend always gets absolute URLs
            if settings.DEBUG:
                # For local development, use localhost
                return f"http://127.0.0.1:8000{obj.image.url}"
            # For production, you should set up proper domain handling
            return obj.image.url
        return None

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'email', 'bio', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    author_display = serializers.CharField(source='get_author_display', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'author_name', 'author_display', 'body', 'created_at', 'approved']
        read_only_fields = ['author_display']


class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    cover_image = serializers.SerializerMethodField()
    content_html = serializers.SerializerMethodField()
    tags = serializers.StringRelatedField(many=True, read_only=True)
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'author', 'title', 'slug', 'content', 'content_html', 
                  'published', 'published_at', 'created_at', 'updated_at', 'comments', 'images', 
                  'cover_image', 'tags']
        read_only_fields = ['published', 'images', 'cover_image', 'comments', 'tags', 'content_html']
    
    def get_content_html(self, obj):
        """Convert markdown content to HTML"""
        if obj.content:
            return md.markdown(
                obj.content,
                extensions=['extra', 'nl2br', 'sane_lists']
            )
        return ""
    
    def get_cover_image(self, obj):
        """Get the first image from the gallery as cover image"""
        first_image = obj.images.first()
        if first_image and first_image.image:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(first_image.image.url)
            # Fallback: build absolute URL for development
            if settings.DEBUG:
                return f"http://127.0.0.1:8000{first_image.image.url}"
            return first_image.image.url
        
        return None


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id', 'name', 'slug']