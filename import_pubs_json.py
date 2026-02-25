import os
import sys
import django
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_project.settings')
django.setup()

from blog.models import Publication

def import_pubs():
    print("Starting import of publications from JSON...")
    
    with open('pubs.json', 'r', encoding='utf-8') as f:
        pubs_data = json.load(f)
        
    count = 0
    for data in pubs_data:
        if 'title' not in data:
            continue
            
        print(f"Importing: {data.get('title')[:30]}...")
        
        pub, created = Publication.objects.get_or_create(
            title=data.get('title'),
            defaults={
                'sub_text': data.get('subText', ''),
                'content': data.get('content', ''),
                'content_type': data.get('contentType', 'content'),
                'content1': data.get('content1', ''),
                'content2': data.get('content2', ''),
                'type': data.get('type', 'image'),
                'static_image_path': data.get('img', '') if data.get('type') == 'image' else '',
                'video_id': data.get('videoId', '') if data.get('type') == 'video' else '',
                'show_button': data.get('showButton', True),
                'button_on_hover': data.get('buttonOnHover', False),
                'button_color': data.get('buttonColor', 'primary'),
                'elevation': data.get('elevation', '0'),
                'email': data.get('email', False),
                'rounded_img': data.get('roundedImg', False),
                'status': 'published'
            }
        )
        if not created:
            pub.sub_text = data.get('subText', '')
            pub.content = data.get('content', '')
            pub.content_type = data.get('contentType', 'content')
            pub.content1 = data.get('content1', '')
            pub.content2 = data.get('content2', '')
            pub.type = data.get('type', 'image')
            if pub.type == 'image':
                pub.static_image_path = data.get('img', '')
            else:
                pub.video_id = data.get('videoId', '')
            pub.show_button = data.get('showButton', True)
            pub.button_on_hover = data.get('buttonOnHover', False)
            pub.button_color = data.get('buttonColor', 'primary')
            pub.elevation = data.get('elevation', '0')
            pub.email = data.get('email', False)
            pub.rounded_img = data.get('roundedImg', False)
            pub.save()
            
        count += 1
        
    print(f"Successfully imported {count} publications.")

if __name__ == '__main__':
    import_pubs()
