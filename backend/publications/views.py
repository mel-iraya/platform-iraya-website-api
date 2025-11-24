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
    search_fields = ['title', 'description', 'event_name', 'location']
    ordering_fields = ['created_at', 'title', 'event_date']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter to show only published publications by default"""
        queryset = super().get_queryset()
        
        # Filter by publication_type if provided
        publication_type = self.request.query_params.get('publication_type')
        if publication_type:
            queryset = queryset.filter(publication_type=publication_type)
        
        # By default, only show published items unless explicitly requested
        show_all = self.request.query_params.get('show_all', 'false').lower() == 'true'
        if not show_all:
            queryset = queryset.filter(published=True)
        
        return queryset

    def get_serializer_context(self):
        """Ensure request context is passed to serializer"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

