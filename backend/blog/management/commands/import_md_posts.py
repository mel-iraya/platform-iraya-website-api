from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from pathlib import Path
from blog.models import Post, Author, Tag
from django.utils.text import slugify
import re


class Command(BaseCommand):
    help = 'Import markdown files from content/blog into Post model (creates or updates)'

    def add_arguments(self, parser):
        parser.add_argument('--author', type=int, default=1, help='Author ID to assign to imported posts')
        parser.add_argument('--path', type=str, default=None, help='Path to content/blog folder (optional)')

    def _parse_frontmatter(self, text):
        """Return (meta_dict, body_text) from a markdown string.

        Simple parser: looks for leading '---' and parses lines of 'key: value'.
        """
        if not text:
            return {}, ''
        lines = text.splitlines()
        if len(lines) >= 1 and lines[0].strip() == '---':
            end_idx = None
            for i in range(1, len(lines)):
                if lines[i].strip() == '---':
                    end_idx = i
                    break
            if end_idx is None:
                return {}, text
            fm_lines = lines[1:end_idx]
            body_lines = lines[end_idx+1:]
            meta = {}
            for l in fm_lines:
                if ':' in l:
                    k, v = l.split(':', 1)
                    meta[k.strip()] = v.strip().strip('"').strip("'")
            return meta, '\n'.join(body_lines).lstrip('\n')
        return {}, text

    def handle(self, *args, **options):
        author_id = options.get('author')
        custom_path = options.get('path')

        # Determine content/blog path; by default it's one level above backend
        base = Path(settings.BASE_DIR)
        content_dir = Path(custom_path) if custom_path else base.parent / 'content' / 'blog'

        if not content_dir.exists() or not content_dir.is_dir():
            raise CommandError(f'Content blog directory not found: {content_dir}')

        try:
            author = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            raise CommandError(f'Author with id={author_id} not found. Create an author first or pass --author another_id')

        files = sorted([p for p in content_dir.iterdir() if p.suffix.lower() == '.md'])
        if not files:
            self.stdout.write(self.style.WARNING('No markdown files found in %s' % content_dir))
            return

        created = 0
        updated = 0

        for f in files:
            text = f.read_text(encoding='utf-8')
            meta, body = self._parse_frontmatter(text)

            title = meta.get('title') or meta.get('Title') or ''
            slug = meta.get('slug') or slugify(f.stem)
            category = meta.get('category') or meta.get('Category') or ''
            image = meta.get('image') or meta.get('img') or ''
            date = meta.get('date') or None
            status = meta.get('status') or 'published'

            # Prepare defaults
            defaults = {
                'author': author,
                'title': title or f.stem,
                'content': body,
                'status': status.lower(),
            }
            if date:
                defaults['published_at'] = date

            post, created_flag = Post.objects.update_or_create(slug=slug, defaults=defaults)

            # Update image field if path present
            if image:
                # Try to set the ImageField value directly (may point to static path)
                post.image = image
                post.save()

            # Tags: allow comma-separated tags in frontmatter
            tags_raw = meta.get('tags') or meta.get('Tags')
            if tags_raw:
                tag_names = [t.strip() for t in re.split('[,;]', tags_raw) if t.strip()]
                tag_objs = []
                for name in tag_names:
                    tag_obj, _ = Tag.objects.get_or_create(name=name)
                    tag_objs.append(tag_obj)
                post.tags.set(tag_objs)

            if created_flag:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(f'Imported {len(files)} files: created={created} updated={updated}'))