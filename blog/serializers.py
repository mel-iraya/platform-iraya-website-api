from rest_framework import serializers
from .models import Author, Post, Comment, Tag, Publication, WelcomePopup, Brochure
import re

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author_name', 'body', 'created_at', 'approved']

class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    author = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())
    thumbnail = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()
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
    images = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'title', 'slug', 'content', 'status', 'published', 'published_at', 'created_at', 'updated_at', 'comments', 'thumbnail', 'images', 'video', 'tags', 'markdown']

    def get_thumbnail(self, obj):
        request = self.context.get('request')
        if hasattr(obj, 'thumbnail') and obj.thumbnail:
            if request is not None:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None

    def get_video(self, obj):
        request = self.context.get('request')
        if hasattr(obj, 'video') and obj.video:
            if request is not None:
                return request.build_absolute_uri(obj.video.url)
            return obj.video.url
        return None

    def get_images(self, obj):
        request = self.context.get('request')
        image_urls = []
        for img_obj in obj.uploaded_images.all():
            if img_obj.image:
                if request is not None:
                    image_urls.append(request.build_absolute_uri(img_obj.image.url))
                else:
                    image_urls.append(img_obj.image.url)
        return image_urls

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
            current_array_key = None
            for l in fm_lines:
                clean_l = l.strip()
                if clean_l.startswith('- ') and current_array_key:
                    val = clean_l[2:].strip().strip('"').strip("'")
                    if current_array_key not in meta:
                        meta[current_array_key] = []
                    meta[current_array_key].append(val)
                elif ':' in l:
                    k, v = l.split(':', 1)
                    k_clean = k.strip()
                    v_clean = v.strip().strip('"').strip("'")
                    if not v_clean:
                        current_array_key = k_clean
                        meta[k_clean] = []
                    elif v_clean.startswith('[') and v_clean.endswith(']'):
                        # inline array
                        current_array_key = None
                        items = [s.strip().strip('"').strip("'") for s in v_clean[1:-1].split(',')]
                        meta[k_clean] = [i for i in items if i]
                    else:
                        current_array_key = None
                        meta[k_clean] = v_clean
            return meta, '\n'.join(body_lines).lstrip('\n')
        # no frontmatter
        return {}, markdown_text

    def create(self, validated_data):
        md = validated_data.pop('markdown', None)
        if md:
            meta, body = self._parse_frontmatter(md)
            if 'title' in meta and not validated_data.get('title'):
                validated_data['title'] = meta['title']
            if 'slug' in meta and not validated_data.get('slug'):
                validated_data['slug'] = meta['slug']
            if 'thumbnail' in meta and not validated_data.get('thumbnail'):
                # Handle how thumbnail from markdown should be applied. 
                # previously it mapped to static_image_path. We can just ignore it or log it since we removed static_image_path.
                pass
            if 'video' in meta and not validated_data.get('video'):
                validated_data['video'] = meta['video']
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
            if 'thumbnail' in meta and not validated_data.get('thumbnail'):
                pass
            if 'video' in meta and not validated_data.get('video'):
                validated_data['video'] = meta['video']
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


class PublicationSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    download_link = serializers.SerializerMethodField()

    class Meta:
        model = Publication
        fields = '__all__'

    def get_image(self, obj):
        request = self.context.get('request')
        if hasattr(obj, 'image') and obj.image:
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def get_download_link(self, obj):
        request = self.context.get('request')
        if hasattr(obj, 'pdf_file') and obj.pdf_file:
            if request is not None:
                return request.build_absolute_uri(obj.pdf_file.url)
            return obj.pdf_file.url
        return None

class WelcomePopupSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = WelcomePopup
        fields = '__all__'

    def get_image(self, obj):
        request = self.context.get('request')
        if hasattr(obj, 'image') and obj.image:
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class BrochureSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    file = serializers.SerializerMethodField()

    class Meta:
        model = Brochure
        fields = '__all__'

    def get_image(self, obj):
        request = self.context.get('request')
        if hasattr(obj, 'image') and obj.image:
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
        
    def get_file(self, obj):
        request = self.context.get('request')
        if hasattr(obj, 'file') and obj.file:
            if request is not None:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None