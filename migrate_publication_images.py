import os
import django
import sys
import shutil
from django.core.files import File

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_project.settings')
django.setup()

from blog.models import Publication
from django.conf import settings

# Vue project roots
VUE_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VUE_PUBLIC_DIR = os.path.join(VUE_PROJECT_ROOT, 'public')
VUE_ASSETS_DIR = os.path.join(VUE_PROJECT_ROOT, 'assets')


def main():
    print("Starting Publication Image Migration...")
    
    publications = Publication.objects.all()
    updated_count = 0
    
    for pub in publications:
        # Check if it has a populated 'image' field already
        if pub.image:
            print(f"Skipping '{pub.title}', already has an uploaded image.")
            continue
            
        print(f"Processing '{pub.title}'...")
        
        # We need to map the hardcoded title to the expected image names from publications.js
        # Or alternatively, look up by the slug/filename if we can infer it.
        # Since we removed `static_image_path`, we will try to infer the image from
        # the title based on the original data format, or if there's any temporary backup logic.
        
        import re
        try:
            with open(os.path.join(VUE_PROJECT_ROOT, 'data', 'publications.js'), 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find the image variable name, e.g. img: greenWorld
            # We match the title, then look ahead for img: variable
            var_pattern = re.compile(rf'img:\s*([a-zA-Z0-9_]+).*?title:\s*[\'"]{re.escape(pub.title)}[\'"]', re.DOTALL | re.IGNORECASE)
            match = var_pattern.search(content)
            
            if not match:
                # the title might come before the img
                var_pattern = re.compile(rf'title:\s*[\'"]{re.escape(pub.title)}[\'"].*?img:\s*([a-zA-Z0-9_]+)', re.DOTALL | re.IGNORECASE)
                match = var_pattern.search(content)

            if match:
                var_name = match.group(1)
                
                # Now find the import for that variable
                # import greenWorld from '@/assets/publications/Earth-green.webp'
                import_pattern = re.compile(rf'import\s+{var_name}\s+from\s+[\'"]([^(\'|")]+)[\'"]', re.IGNORECASE)
                import_match = import_pattern.search(content)
                
                if import_match:
                    img_path = import_match.group(1)
                    print(f"  Found image mapping: {var_name} -> {img_path}")
                    
                    filename = os.path.basename(img_path)
                    
                    # The path is usually '@/assets/publications/filename'
                    possible_paths = [
                        os.path.join(VUE_ASSETS_DIR, 'publications', filename),
                        os.path.join(VUE_ASSETS_DIR, 'blog', filename),
                        os.path.join(VUE_PUBLIC_DIR, 'assets', 'publications', filename),
                    ]
                    
                    found_path = None
                    for p in possible_paths:
                        if os.path.exists(p):
                            found_path = p
                            break
                            
                    if found_path:
                        print(f"  Found file at: {found_path}")
                        with open(found_path, 'rb') as f:
                            pub.image.save(filename, File(f), save=True)
                        updated_count += 1
                        print(f"  Successfully uploaded image for '{pub.title}'")
                    else:
                        print(f"  ERROR: Could not locate file {filename} in Vue project.")
                else:
                    print(f"  ERROR: Found variable {var_name} but no import statement.")
            else:
                 print(f"  ERROR: Could not find image variable mapping for '{pub.title}' in publications.js")
                 
        except Exception as e:
            print(f"  ERROR processing {pub.title}: {str(e)}")

    print(f"\nMigration complete. Updated {updated_count} publications.")

if __name__ == '__main__':
    main()
