from rest_framework import serializers
from .models import Post, Comment, PostImage, Tag
import markdown as md

class PostImageSerializer(serializers.ModelSerializer):
    """Serializer for post image gallery"""
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = PostImage
        fields = ['id', 'image', 'caption', 'order', 'is_cover', 'created_at']
    
    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

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
    tags = serializers.StringRelatedField(many=True, read_only=True)  # Simple tag names
    author_name = serializers.CharField(source='author.name', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'author', 'author_name', 'title', 'slug', 'content', 'content_html', 'status', 
                  'published', 'published_at', 'created_at', 'updated_at', 'comments', 'images', 
                  'cover_image', 'tags']
        read_only_fields = ['published', 'author_name', 'images', 'cover_image', 'comments', 'tags', 'content_html']
    
    def get_content_html(self, obj):
        """Convert markdown content to HTML"""
        if obj.content:
            return md.markdown(
                obj.content,
                extensions=[
                    'extra',      # Tables, fenced code blocks, footnotes, etc.
                    'nl2br',      # New line to <br>
                    'sane_lists'  # Better list handling
                ]
            )
        return ""
    
    def get_cover_image(self, obj):
        """Get the marked cover image from gallery, or first image"""
        request = self.context.get('request')
        
        # Check if there's a cover image in the gallery
        cover = obj.images.filter(is_cover=True).first()
        if cover and cover.image:
            if request is not None:
                return request.build_absolute_uri(cover.image.url)
            return cover.image.url
        
        # If no cover, use first image in gallery
        first_image = obj.images.first()
        if first_image and first_image.image:
            if request is not None:
                return request.build_absolute_uri(first_image.image.url)
            return first_image.image.url
        
        return None


class TagSerializer(serializers.ModelSerializer):
    """Read-only serializer for tags"""
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id', 'name', 'slug']