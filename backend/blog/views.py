from django.shortcuts import render
from django.db.models import Q
from rest_framework import viewsets
from .models import Author, Post, Comment, Tag
from .serializers import AuthorSerializer, PostSerializer, CommentSerializer, TagSerializer

# Create your views here.
class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer

    def get_queryset(self):
        """
        Optionally filter posts by tag name using the `?tag=` query parameter.
        Example: /api/posts/?tag=Events
        """
        # By default only return published posts so drafts are not exposed to the public frontend
        qs = Post.objects.filter(status=Post.STATUS_PUBLISHED).order_by('-created_at')
        tag = self.request.query_params.get('tag')
        if tag:
            # allow either tag name or tag slug (case-insensitive)
            qs = qs.filter(Q(tags__name__iexact=tag) | Q(tags__slug__iexact=tag))
        return qs.distinct()

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer