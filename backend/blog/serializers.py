from rest_framework import serializers
from .models import Author, Post, Comment, Tag
import re

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author_name', 'body', 'created_at', 'approved']

class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    author = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())
    image = serializers.SerializerMethodField()
    # allow posting `markdown` without separately sending title/content fields
    title = serializers.CharField(required=False)
    content = serializers.CharField(required=False)
    # Accept markdown (optionally with YAML frontmatter) on create/update.
    # This is write-only and simple: frontmatter keys like `title` and `slug`
    # will be copied into the model when present. The markdown body is
    # stored into `content`.
    markdown = serializers.CharField(write_only=True, required=False)
    # represent tags as a list of tag names
    tags = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Tag.objects.all(), required=False)

    class Meta:
        model = Post
        fields = ['id', 'author', 'title', 'slug', 'content', 'status', 'published', 'published_at', 'created_at', 'updated_at', 'comments', 'image', 'tags', 'markdown']

    def get_image(self, obj):
        request = self.context.get('request')
        if hasattr(obj, 'image') and obj.image:
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def _parse_frontmatter(self, markdown_text):
        """Return (meta_dict, body_text).

        Very small frontmatter parser: looks for leading '---' block and parses
        simple key: value pairs. Values are returned as raw strings.
        """
        if not markdown_text:
            return {}, ''
        lines = markdown_text.splitlines()
        if len(lines) >= 1 and lines[0].strip() == '---':
            # find closing '---'
            end_idx = None
            for i in range(1, len(lines)):
                if lines[i].strip() == '---':
                    end_idx = i
                    break
            if end_idx is None:
                # no closing frontmatter, treat whole as body
                return {}, markdown_text
            fm_lines = lines[1:end_idx]
            body_lines = lines[end_idx+1:]
            meta = {}
            for l in fm_lines:
                if ':' in l:
                    k, v = l.split(':', 1)
                    meta[k.strip()] = v.strip().strip('"').strip("'")
            return meta, '\n'.join(body_lines).lstrip('\n')
        # no frontmatter
        return {}, markdown_text

    def create(self, validated_data):
        md = validated_data.pop('markdown', None)
        if md:
            meta, body = self._parse_frontmatter(md)
            # fill in basic fields if present
            if 'title' in meta and not validated_data.get('title'):
                validated_data['title'] = meta['title']
            if 'slug' in meta and not validated_data.get('slug'):
                validated_data['slug'] = meta['slug']
            # store body into content
            validated_data['content'] = body

        return super().create(validated_data)

    def update(self, instance, validated_data):
        md = validated_data.pop('markdown', None)
        if md:
            meta, body = self._parse_frontmatter(md)
            if 'title' in meta and not validated_data.get('title'):
                validated_data['title'] = meta['title']
            if 'slug' in meta and not validated_data.get('slug'):
                validated_data['slug'] = meta['slug']
            validated_data['content'] = body

        return super().update(instance, validated_data)
    

class AuthorSerializer(serializers.ModelSerializer):
    posts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Author
        fields = ['id', 'name', 'email', 'bio', 'created_at', 'posts']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']