import os
import django
import shutil
import sys
from django.core.files import File

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blog_project.settings")
django.setup()

from blog.models import WelcomePopup

def import_popup():
    source_image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'images', 'somethingMoreIntelligent.png')
    
    if not os.path.exists(source_image_path):
        print(f"Error: Original image not found at {source_image_path}")
        return

    # Create the model instance
    popup, created = WelcomePopup.objects.get_or_create(
        title='Something More Intelligent',
        defaults={'is_active': True}
    )
    
    if created or not popup.image:
        print("Importing image...")
        with open(source_image_path, 'rb') as f:
            popup.image.save('somethingMoreIntelligent.png', File(f), save=True)
        # Ensure it's active
        popup.is_active = True
        popup.save()
        print("Image imported successfully!")
    else:
        print("Popup already exists and has an image.")

if __name__ == '__main__':
    import_popup()
