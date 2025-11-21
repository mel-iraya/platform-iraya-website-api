from rest_framework import serializers
from .models import Publication


class PublicationSerializer(serializers.ModelSerializer):
    """Serializer for Publication model"""
    pdf_url = serializers.SerializerMethodField()
    publication_type_display = serializers.CharField(source='get_publication_type_display', read_only=True)

    class Meta:
        model = Publication
        fields = [
            'id',
            'title',
            'description',
            'pdf_file',
            'pdf_url',
            'publication_type',
            'publication_type_display',
            'event_name',
            'location',
            'event_date',
            'published',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ('created_at', 'updated_at')

    def get_pdf_url(self, obj):
        """Return the full URL to the PDF file"""
        if obj.pdf_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
            return obj.pdf_file.url
        return None

