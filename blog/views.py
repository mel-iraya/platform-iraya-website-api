from django.shortcuts import render
from django.db.models import Q
from rest_framework.permissions import AllowAny
from rest_framework import viewsets, mixins
from django.core.mail import send_mail
from django.conf import settings
from .models import Author, Post, Comment, Tag, Publication, WelcomePopup, Brochure, TrialRequest
from .serializers import AuthorSerializer, PostSerializer, CommentSerializer, TagSerializer, PublicationSerializer, WelcomePopupSerializer, BrochureSerializer, TrialRequestSerializer

# Create your views here.
class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.prefetch_related('posts').all()
    serializer_class = AuthorSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related('author').prefetch_related('comments', 'tags').all().order_by('-created_at')
    serializer_class = PostSerializer

    def get_queryset(self):
        """
        Optionally filter posts by tag name using the `?tag=` query parameter.
        Example: /api/posts/?tag=Events
        """
        # By default only return published posts so drafts are not exposed to the public frontend
        qs = Post.objects.filter(status=Post.STATUS_PUBLISHED).select_related('author').prefetch_related('comments', 'tags').order_by('-created_at')
        tag = self.request.query_params.get('tag')
        if tag:
            # allow either tag name or tag slug (case-insensitive)
            qs = qs.filter(Q(tags__name__iexact=tag) | Q(tags__slug__iexact=tag))
        return qs.distinct()

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related('post').all().order_by('-created_at')
    serializer_class = CommentSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer


class PublicationViewSet(viewsets.ModelViewSet):
    queryset = Publication.objects.all().order_by('-created_at')
    serializer_class = PublicationSerializer
    pagination_class = None

class WelcomePopupViewSet(viewsets.ModelViewSet):
    queryset = WelcomePopup.objects.all().order_by('-created_at')
    serializer_class = WelcomePopupSerializer
    pagination_class = None

    def get_queryset(self):
        qs = WelcomePopup.objects.all().order_by('-created_at')
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            active_bool = is_active.lower() == 'true'
            qs = qs.filter(is_active=active_bool)
        return qs

class BrochureViewSet(viewsets.ModelViewSet):
    queryset = Brochure.objects.all().order_by('-created_at')
    serializer_class = BrochureSerializer
    pagination_class = None

class TrialRequestViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = TrialRequest.objects.all().order_by('-created_at')
    serializer_class = TrialRequestSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        instance = serializer.save()
        
        subject = f"New Trial/Demo Request: {instance.first_name} {instance.last_name}"
        message = (
            f"A new trial/demo request has been received:\n\n"
            f"Name: {instance.first_name} {instance.last_name}\n"
            f"Email: {instance.email}\n"
            f"Company: {instance.company}\n"
            f"Product: {instance.product or 'N/A'}\n"
            f"Message: {instance.message or 'N/A'}\n\n"
            f"Date: {instance.created_at}"
        )
        
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@irayaenergies.com')
        admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@irayaenergies.com')
        
        try:
            send_mail(subject, message, from_email, [admin_email], fail_silently=True)
        except Exception as e:
            print(f"Failed to send email: {e}")
            pass