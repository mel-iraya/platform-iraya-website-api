from rest_framework import serializers
from django.conf import settings
from .models import Publication, PublicationImage


class PublicationImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = PublicationImage
        fields = ['id', 'image', 'created_at']
    
    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            # Fallback: build absolute URL for development
            if settings.DEBUG:
                return f"http://127.0.0.1:8000{obj.image.url}"
            return obj.image.url
        return None


class PublicationSerializer(serializers.ModelSerializer):
    """Serializer for Publication model matching frontend structure"""
    img = serializers.SerializerMethodField()
    subText = serializers.CharField(source='sub_text', read_only=True)
    videoId = serializers.CharField(source='video_id', read_only=True)
    contentType = serializers.CharField(source='content_type', read_only=True)
    showButton = serializers.BooleanField(source='show_button', read_only=True)
    buttonOnHover = serializers.BooleanField(source='button_on_hover', read_only=True)
    buttonColor = serializers.CharField(source='button_color', read_only=True)
    roundedImg = serializers.BooleanField(source='rounded_img', read_only=True)
    
    # Keep pdf_url for download button
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = Publication
        fields = [
            'id',
            'type',
            'img',
            'alt',
            'videoId',
            'title',
            'subText',
            'contentType',
            'content',
            'content1',
            'content2',
            'showButton',
            'buttonOnHover',
            'buttonColor',
            'email',
            'roundedImg',
            'elevation',
            'pdf_url',
        ]

    def get_img(self, obj):
        """Return the full URL to the image"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            # Fallback for dev
            if settings.DEBUG:
                return f"http://127.0.0.1:8000{obj.image.url}"
            return obj.image.url
        return None

    def get_pdf_url(self, obj):
        """Return the full URL to the PDF file"""
        if obj.pdf_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
            return obj.pdf_file.url
        return None





