import os
import sys
import django
from glob import glob

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_project.settings')
django.setup()

from blog.models import Post, Author, Tag
from blog.serializers import PostSerializer

def import_blogs():
    print("Starting import of markdown blogs...")
    blog_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'content', 'blog')
    
    # Get or create a default author
    author, created = Author.objects.get_or_create(
        email='admin@irayaenergies.com',
        defaults={'name': 'Iraya Admin', 'bio': 'Default Admin'}
    )
    
    md_files = glob(os.path.join(blog_dir, '*.md'))
    print(f"Found {len(md_files)} markdown files.")
    
    for md_file in md_files:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        print(f"Processing {os.path.basename(md_file)}...")
        
        # We can extract the slug manually to check if it exists
        lines = content.splitlines()
        slug = None
        category = None
        if len(lines) >= 1 and lines[0].strip() == '---':
            for l in lines[1:]:
                if l.strip() == '---':
                    break
                if l.startswith('slug:'):
                    slug = l.split(':', 1)[1].strip().strip('"').strip("'")
                if l.startswith('category:'):
                    category = l.split(':', 1)[1].strip().strip('"').strip("'")
                    
        if not slug:
            slug = os.path.basename(md_file).replace('.md', '')
            
        if not category:
            category = "News"
            
        post_qs = Post.objects.filter(slug=slug)
        if post_qs.exists():
            print(f"  -> Post '{slug}' already exists. Updating...")
            post = post_qs.first()
            serializer = PostSerializer(post, data={
                'markdown': content,
                'author': author.id,
                'status': 'published'
            }, partial=True)
        else:
            print(f"  -> Creating new post '{slug}'...")
            serializer = PostSerializer(data={
                'markdown': content,
                'author': author.id,
                'status': 'published'
            })
            
        if serializer.is_valid():
            post = serializer.save()
            
            # assign tag matching category if present
            if category:
                tag, _ = Tag.objects.get_or_create(name=category)
                post.tags.add(tag)
        else:
            print(f"  -> Error saving {slug}: {serializer.errors}")

if __name__ == '__main__':
    import_blogs()
