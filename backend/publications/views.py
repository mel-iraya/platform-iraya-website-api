from rest_framework import viewsets, filters
from .models import Publication
from .serializers import PublicationSerializer


class PublicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing publications and brochures.
    Supports filtering by publication_type and only shows published items by default.
    """
    queryset = Publication.objects.all().order_by('-created_at')
    serializer_class = PublicationSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'sub_text', 'content']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter to show only published publications by default"""
        queryset = super().get_queryset()
        
        # Filter by type if provided
        type_param = self.request.query_params.get('type')
        if type_param:
            queryset = queryset.filter(type=type_param)
        
        return queryset

    def get_serializer_context(self):
        """Ensure request context is passed to serializer"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

