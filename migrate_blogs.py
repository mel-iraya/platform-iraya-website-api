import os
import re
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_project.settings')
django.setup()

from blog.models import Post, Tag, Author

def parse_frontmatter(content):
    match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}, content
        
    frontmatter = match.group(1)
    lines = frontmatter.split('\n')
    data = {}
    
    for line in lines:
        if ':' in line:
            key, val = line.split(':', 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if val:
                data[key] = val
                
    main_content = content[match.end():].strip()
    return data, main_content

def main():
    blog_dir = r"d:\Iraya\platform-iraya-website\content\blog"
    
    # ensure an author exists
    author, _ = Author.objects.get_or_create(
        name="Iraya Admin", 
        email="admin@irayaenergies.com",
        defaults={"bio": "System Administrator"}
    )
    
    count = 0
    for filename in os.listdir(blog_dir):
        if not filename.endswith('.md'):
            continue
            
        filepath = os.path.join(blog_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        data, main_content = parse_frontmatter(content)
        
        title = data.get('title', filename.replace('.md', ''))
        slug = data.get('slug', '')
        date_str = data.get('date', '')
        category = data.get('category', '')
        
        # We explicitly omit media fields (thumbnail, images/gallery, video) 
        # as requested by the user
        
        post, created = Post.objects.get_or_create(
            slug=slug or None, # get_or_create using slug if exists
            defaults={
                'title': title,
                'content': main_content,
                'author': author,
                'status': Post.STATUS_PUBLISHED,
                'published': True,
            }
        )
        
        if not created:
            # Update existing post
            post.title = title
            post.content = main_content
            post.status = Post.STATUS_PUBLISHED
            post.published = True
            
        if date_str:
            try:
                # Basic parsing, might need adjustment based on date format
                dt = datetime.strptime(date_str, '%Y-%m-%d')
                post.published_at = dt
                post.created_at = dt # Not strictly accurate to override auto_now_add in all models, but attempting for historical accuracy
            except ValueError:
                pass
                
        post.save()
        
        if category:
            tag, _ = Tag.objects.get_or_create(name=category)
            post.tags.add(tag)
            
        count += 1
        print(f"{'Created' if created else 'Updated'}: {title}")
        
    print(f"\nSuccessfully processed {count} markdown files.")

if __name__ == '__main__':
    main()
