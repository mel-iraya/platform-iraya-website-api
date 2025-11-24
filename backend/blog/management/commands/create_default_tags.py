from django.core.management.base import BaseCommand
from blog.models import Tag


class Command(BaseCommand):
    help = 'Create default tags used by the frontend: News, Events, Conference, New Energy'

    DEFAULT_TAGS = ['News', 'Events', 'Conference', 'New Energy']

    def handle(self, *args, **options):
        created = []
        for name in self.DEFAULT_TAGS:
            tag, was_created = Tag.objects.get_or_create(name=name)
            if was_created:
                created.append(name)
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created tags: {', '.join(created)}"))
        else:
            self.stdout.write('Default tags already exist')
