import os
import glob
import re
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from blog.models import Post, Author, Tag

class Command(BaseCommand):
    help = 'Seed database with blog posts from local markdown files'

    def handle(self, *args, **options):
        # Define path to local markdown content
        # Update this path if necessary to match your project structure
        # Assuming the command is run from api root, pointing to ../content/blog
        base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
        blog_content_dir = base_dir / 'content' / 'blog'
        
        self.stdout.write(f"Looking for markdown files in: {blog_content_dir}")
        
        if not blog_content_dir.exists():
            self.stdout.write(self.style.ERROR(f"Directory not found: {blog_content_dir}"))
            return

        # Ensure a default author exists
        default_author, created = Author.objects.get_or_create(
            email='admin@iraya.com',
            defaults={'name': 'Iraya Admin', 'bio': 'System Administrator'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created default author: {default_author.name}"))

        # Glob all markdown files
        md_files = list(blog_content_dir.glob('*.md'))
        
        if not md_files:
            self.stdout.write(self.style.WARNING("No markdown files found."))
            return

        for md_file in md_files:
            try:
                self.process_file(md_file, default_author)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to process {md_file.name}: {e}"))

    def process_file(self, file_path, author):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse Frontmatter
        # Very customized simple parser
        frontmatter = {}
        body = content
        
        if content.startswith('---'):
            parts = re.split(r'^---$', content, maxsplit=2, flags=re.MULTILINE)
            if len(parts) >= 3:
                fm_text = parts[1]
                body = parts[2].strip()
                
                # Parse lines
                for line in fm_text.splitlines():
                    if ':' in line:
                        key, val = line.split(':', 1)
                        frontmatter[key.strip()] = val.strip().strip('"\'')
        else:
            self.stdout.write(self.style.WARNING(f"No frontmatter in {file_path.name}"))

        # Extract Fields
        title = frontmatter.get('title', file_path.stem)
        slug = frontmatter.get('slug', slugify(title))
        date_str = frontmatter.get('date')
        image_path = frontmatter.get('image') or frontmatter.get('img')
        category = frontmatter.get('category')
        tags_list = frontmatter.get('tags', []) 
        
        # Tags might need parsing if it looks like a list string "[a, b]"
        # But simple key: val usually implies single string or yaml list which simple parser might miss
        # For this simple parser, let's assume single category -> Tag
        
        # Create or Update Post
        post, created = Post.objects.update_or_create(
            slug=slug,
            defaults={
                'author': author,
                'title': title,
                'content': body,
                'static_image_path': image_path,
                'status': Post.STATUS_PUBLISHED,
                'published_at': timezone.now() if not date_str else None # If date_str exists, we might parse it, but for now allow null or set to now
            }
        )
        
        # Handle Date manually if present
        if date_str:
            # Try parsing date - simple fallback
            try:
                # Assuming YYYY-MM-DD
                from datetime import datetime
                dt = datetime.strptime(date_str, '%Y-%m-%d')
                post.published_at = timezone.make_aware(dt)
                post.created_at = timezone.make_aware(dt)
                post.save()
            except ValueError:
                self.stdout.write(self.style.WARNING(f"Could not parse date {date_str} for {slug}"))

        # Handle Tags from Category
        if category:
            tag, _ = Tag.objects.get_or_create(name=category)
            post.tags.add(tag)
            
        # Additional heuristic tags based on title/subtitle
        if 'event' in title.lower() or 'conference' in title.lower():
            t, _ = Tag.objects.get_or_create(name='Events')
            post.tags.add(t)
        
        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} post: {title}"))
