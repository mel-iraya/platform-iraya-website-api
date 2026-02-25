import os
import sys
import django
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_project.settings')
django.setup()

from blog.models import Publication

def import_pubs():
    print("Starting import of publications...")
    pub_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'publications.js')
    
    with open(pub_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # extract imports mapping variable to string path
    import_pattern = re.compile(r"import\s+(\w+)\s+from\s+['\"]([^'\"]+)['\"]")
    imports = {}
    for match in import_pattern.finditer(content):
        var_name = match.group(1)
        path = match.group(2)
        # replace alias
        if path.startswith('@/'):
            path = '/' + path[2:]
        imports[var_name] = path

    # find the array content
    array_match = re.search(r'export\s+const\s+publications1\s*=\s*\[(.*?)\];', content, re.DOTALL)
    if not array_match:
        # Sometimes there's no trailing semicolon
        array_match = re.search(r'export\s+const\s+publications1\s*=\s*\[(.*)\]\s*$', content, re.DOTALL)
        
    if not array_match:
        print("Could not find publications1 array!")
        return

    array_str = array_match.group(1)
    
    # split by { ... }
    obj_pattern = re.compile(r'\{(.*?)\}', re.DOTALL)
    
    count = 0
    for obj_match in obj_pattern.finditer(array_str):
        obj_text = obj_match.group(1)
        
        # parse keys and values
        data = {}
        # remove comments
        obj_text = re.sub(r'//.*', '', obj_text)
        
        # simple key-value parser 
        # (note: only works for simple strings/booleans as found in publications.js)
        kv_pattern = re.compile(r'(\w+)\s*:\s*(.*?)(?=(?:,\s*\w+\s*:)|$)', re.DOTALL)
        for kv_match in kv_pattern.finditer(obj_text + ','):
            k = kv_match.group(1).strip()
            v = kv_match.group(2).strip()
            if v.endswith(','):
                v = v[:-1].strip()
            
            # resolve strings
            if v.startswith("'") and v.endswith("'"):
                v = v[1:-1]
            elif v.startswith('"') and v.endswith('"'):
                v = v[1:-1]
            # resolve booleans
            v_lower = v.lower()
            if v_lower == 'true':
                v = True
            elif v_lower == 'false':
                v = False
            # resolve variable references (images)
            elif v in imports:
                v = imports[v]
                
            data[k] = v
            
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
            # Update existing
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
