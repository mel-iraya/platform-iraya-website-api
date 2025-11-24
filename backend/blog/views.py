from django.db.models import Q
from rest_framework import viewsets
from .models import Post, Comment, Tag
from .serializers import PostSerializer, CommentSerializer, TagSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer

    def get_queryset(self):
        """Filter published posts, optionally by tag using ?tag= query parameter"""
        qs = Post.objects.filter(published=True).order_by('-created_at')
        tag = self.request.query_params.get('tag')
        if tag:
            qs = qs.filter(Q(tags__name__iexact=tag) | Q(tags__slug__iexact=tag))
        return qs
    
    def get_serializer_context(self):
        """Ensure request context is passed to serializer"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer

