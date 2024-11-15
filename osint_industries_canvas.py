import csv
import json
import datetime
import sys
import re
import requests
from urllib.parse import quote

def is_valid_image_url(url):
    if not url or not isinstance(url, str):
        return False
    if url.startswith('data:image'):
        return True
    url_lower = url.lower()
    
    trusted_domains = [
        'googleusercontent.com',
        'google.com',
        'whatsapp.net',
        'plex.tv',
        'githubusercontent.com',
        'github.com'
    ]
    
    if any(domain in url_lower for domain in trusted_domains):
        return True
        
    image_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
    if any(url_lower.endswith(ext) for ext in image_extensions):
        return True
        
    image_patterns = [
        r'avatars?\.?',
        r'profile.*\.',
        r'photos?\.?',
        r'images?\.?',
        r'cdn\.?',
        r'/t61\.',
        r'/avatar\?'
    ]
    
    return any(re.search(pattern, url_lower) for pattern in image_patterns)

def clean_base64_image(base64_string):
    if 'base64,' in base64_string:
        base64_string = base64_string.split('base64,')[1]
    base64_string = base64_string.strip()
    return f'data:image/jpeg;base64,{base64_string}'

def embed_image_in_markdown(image_url):
    if not image_url:
        return ""
    if 'base64' in image_url:
        cleaned_url = clean_base64_image(image_url)
        return f'<img src="{cleaned_url}" alt="Profile Picture" style="max-width:200px;" />'
    else:
        return f'<img src="{image_url}" alt="Profile Picture" style="max-width:200px;" />'

def format_value(key, value):
    if isinstance(value, str):
        if any(date_indicator in key.lower() for date_indicator in ['date', 'seen', 'time']):
            if '+' in value:
                value = value.split('+')[0]
            if 'T' in value:
                date_part, time_part = value.split('T')
                if '.' in time_part:
                    time_part = time_part.split('.')[0]
                value = f"{date_part} {time_part}"
    return value

def icon_exists(icon_name):
    try:
        url = f'https://cdn.simpleicons.org/{quote(icon_name)}/white'
        response = requests.head(url)
        return response.status_code == 200
    except:
        return False

_icon_cache = {}
def get_icon_name(platform):
    if not platform:
        return 'sharp'
        
    if platform in _icon_cache:
        return _icon_cache[platform]
        
    platform = platform.lower().strip()
    
    # Common platform name variations
    variations = [
        platform,
        platform.replace(' ', ''),
        platform.replace(' ', '-'),
        platform.replace('_', ''),
        platform.replace('_', '-')
    ]
    
    # Special cases
    if platform == 'twitter':
        variations.append('x')
    elif platform == 'maps':
        variations.append('googlemaps')
    elif platform == 'email':
        variations.append('gmail')
    elif platform == 'teams':
        variations.append('microsoftteams')
    
    # Try each variation
    for name in variations:
        if icon_exists(name):
            _icon_cache[platform] = name
            return name
            
    # Fallback to sharp icon
    _icon_cache[platform] = 'sharp'
    return 'sharp'
def get_platform_icon(platform_name):
    icon_name = get_icon_name(platform_name)
    return f'<img src="https://cdn.simpleicons.org/{quote(icon_name)}/white" alt="{platform_name}" width="24" height="24" style="display:inline-block; vertical-align:middle;" />'

def get_platform_color(platform_name):
    social_media = ["Facebook", "Instagram", "Twitter", "LinkedIn", "Snapchat", "TikTok", "X"]
    entertainment = ["Spotify", "YouTube", "Twitch", "Vimeo", "Dailymotion", "Netflix", "Plex"]
    professional = ["GitHub", "LinkedIn", "Dropbox", "Google", "Microsoft", "Apple"]
    gaming = ["EA", "Steam", "PlayStation", "Xbox", "Nintendo", "EpicGames"]
    messaging = ["WhatsApp", "Telegram", "Signal", "Discord", "Slack", "WeChat", "Line"]
    
    platform_name = platform_name.capitalize()
    
    if platform_name in social_media:
        return "1"
    elif platform_name in entertainment:
        return "2"
    elif platform_name in professional:
        return "3"
    elif platform_name in gaming:
        return "4"
    elif platform_name in messaging:
        return "5"
    return "6"

def create_canvas_card(platform_data, x_pos, y_pos):
    platform_name = platform_data['module'].capitalize()
    icon = get_platform_icon(platform_name)
    
    # Extract all data points except module and breach
    data_points = {k: v for k, v in platform_data.items() 
                  if v and v.strip() and k != 'module' and k != 'breach'}
    
    # Handle GitHub bio if present in multiple fields
    bio_content = None
    bio_fields = ['bio', 'description', 'about']
    
    for field in bio_fields:
        if field in data_points and data_points[field].strip():
            bio_content = data_points[field]
            break
    
    card_content = f"""# {icon} {platform_name}\n\n>[!info]+ Profile Information"""

    if platform_data.get('picture_url') and platform_data['picture_url'].strip():
        pic_url = platform_data['picture_url']
        if is_valid_image_url(pic_url):
            card_content += f"\n\n{embed_image_in_markdown(pic_url)}\n"

    if data_points:
        # Priority information first
        priority_keys = ['name', 'username', 'email', 'creation_date', 'id', 'last_seen']
        processed_keys = set()
        
        for key in priority_keys:
            if key in data_points:
                display_key = key.replace('_', ' ').title()
                value = format_value(key, data_points[key])
                card_content += f"\n• {display_key}: {value}"
                processed_keys.add(key)

        # Add bio if found
        if bio_content:
            card_content += f"\n• Bio: {bio_content[:200]}{'...' if len(bio_content) > 200 else ''}"
            processed_keys.update(bio_fields)

        # Add remaining fields
        for key, value in sorted(data_points.items()):
            if key in ['picture_url', 'module'] or key in processed_keys:
                continue
            display_key = key.replace('_', ' ').title()
            formatted_value = format_value(key, value)
            card_content += f"\n• {display_key}: {formatted_value}"
    else:
        card_content += "\n• Status: Account Found"

    if platform_data.get('breach') == 'true':
        card_content += "\n\n>[!danger]+ Breach Detected"
        if platform_data.get('creation_date'):
            breach_date = format_value('creation_date', platform_data['creation_date'])
            card_content += f"\n• Date: {breach_date}"

    return {
        "id": f"card-{platform_name.lower().replace(' ', '-')}",
        "type": "text",
        "text": card_content,
        "x": x_pos,
        "y": y_pos,
        "width": 300,
        "height": 250,
        "color": get_platform_color(platform_name),
        "fontSize": 16,
        "background": "2B2D31",
        "textColor": "FFFFFF"
    }
def create_canvas_file(csv_data, output_filename):
    canvas = {
        "nodes": [],
        "edges": [],
        "settings": {
            "backgroundColor": "1E1E1E",
            "gridSize": 50,
            "defaultTextColor": "FFFFFF",
            "defaultBackgroundColor": "2B2D31",
            "defaultFontSize": 16
        }
    }
    
    x = 100
    y = 100
    max_cards_per_row = 3
    card_spacing_x = 350
    card_spacing_y = 300
    card_count = 0
    
    for platform in csv_data:
        if platform['module'].strip():
            current_x = x + (card_count % max_cards_per_row) * card_spacing_x
            current_y = y + (card_count // max_cards_per_row) * card_spacing_y
            card = create_canvas_card(platform, current_x, current_y)
            if card:
                canvas["nodes"].append(card)
                card_count += 1

    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(canvas, f, indent=2, ensure_ascii=False)

def main():
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        import glob
        csv_files = glob.glob("*.csv")
        if not csv_files:
            print("Error: No CSV file found!")
            print("Please either:")
            print("1. Provide CSV file as argument: python osint_industries_canvas.py your_file.csv")
            print("2. Place a CSV file in the same directory as the script")
            sys.exit(1)
        input_file = csv_files[0]
        print(f"Using CSV file: {input_file}")

    output_file = f"OSINT_Results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.canvas"
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            csv_data = list(csv.DictReader(f))
        create_canvas_file(csv_data, output_file)
        print(f"Canvas file created successfully: {output_file}")
    except Exception as e:
        print(f"Error processing file '{input_file}': {str(e)}")
        print("\nUsage:")
        print("1. Provide CSV file as argument: python osint_industries_canvas.py your_file.csv")
        print("2. Place a CSV file in the same directory as the script")
        raise

if __name__ == "__main__":
    main()