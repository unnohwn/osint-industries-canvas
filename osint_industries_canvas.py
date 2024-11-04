import csv
import json
import datetime
import sys
import re

PLATFORM_SVG_ICONS = {
    "facebook": """<svg width="24" height="24" viewBox="0 0 24 24" fill="white"><path d="M12.001 2.002c-5.522 0-9.999 4.477-9.999 9.999 0 4.99 3.656 9.126 8.437 9.879v-6.988h-2.54v-2.891h2.54V9.798c0-2.508 1.493-3.891 3.776-3.891 1.094 0 2.24.195 2.24.195v2.459h-1.264c-1.24 0-1.628.772-1.628 1.563v1.875h2.771l-.443 2.891h-2.328v6.988C18.344 21.129 22 16.992 22 12.001c0-5.522-4.477-9.999-9.999-9.999z"/></svg>""",
    "instagram": """<svg width="24" height="24" viewBox="0 0 24 24" fill="white"><path d="M12 2.982c2.937 0 3.285.011 4.445.064 1.072.049 1.655.228 2.043.379.513.2.88.437 1.265.822.385.385.622.752.822 1.265.151.388.33.971.379 2.043.053 1.16.064 1.508.064 4.445s-.011 3.285-.064 4.445c-.049 1.072-.228 1.655-.379 2.043-.2.513-.437.88-.822 1.265-.385.385-.752.622-1.265.822-.388.151-.971.33-2.043.379-1.16.053-1.508.064-4.445.064s-3.285-.011-4.445-.064c-1.072-.049-1.655-.228-2.043-.379-.513-.2-.88-.437-1.265-.822-.385-.385-.622-.752-.822-1.265-.151-.388-.33-.971-.379-2.043-.053-1.16-.064-1.508-.064-4.445s.011-3.285.064-4.445c.049-1.072.228-1.655.379-2.043.2-.513.437-.88.822-1.265.385-.385.752-.622 1.265-.822.388-.151.971-.33 2.043-.379 1.16-.053 1.508-.064 4.445-.064M12 1c-2.987 0-3.362.013-4.535.066-1.171.054-1.97.24-2.67.512-.724.281-1.339.656-1.951 1.268-.612.612-.987 1.227-1.268 1.951-.272.7-.458 1.499-.512 2.67C1.013 8.638 1 9.013 1 12s.013 3.362.066 4.535c.054 1.171.24 1.97.512 2.67.281.724.656 1.339 1.268 1.951.612.612 1.227.987 1.951 1.268.7.272 1.499.458 2.67.512C8.638 22.987 9.013 23 12 23s3.362-.013 4.535-.066c1.171-.054 1.97-.24 2.67-.512.724-.281 1.339-.656 1.951-1.268.612-.612.987-1.227 1.268-1.951.272-.7.458-1.499.512-2.67C22.987 15.362 23 14.987 23 12s-.013-3.362-.066-4.535c-.054-1.171-.24-1.97-.512-2.67-.281-.724-.656-1.339-1.268-1.951-.612-.612-1.227-.987-1.951-1.268-.7-.272-1.499-.458-2.67-.512C15.362 1.013 14.987 1 12 1zm0 5.351c-3.121 0-5.649 2.528-5.649 5.649S8.879 17.649 12 17.649s5.649-2.528 5.649-5.649S15.121 6.351 12 6.351z"/></svg>""",
    "snapchat": """<svg width="24" height="24" viewBox="0 0 24 24" fill="white"><path d="M12.206.793c.99 0 4.347.276 5.93 3.821.529 1.193.403 3.219.299 4.847l-.003.06c-.012.18-.022.345-.03.51.075.045.203.109.401.195.3.129.677.29.88.41.203.12.321.24.321.405 0 .165-.12.285-.3.345-.179.06-.624.135-1.07.21-.431.074-.882.15-1.156.195-.078.015-.146.029-.208.044.008.18-.059.726-.071.93-.475.886-2.06 1.875-4.127 1.875s-3.652-.989-4.127-1.875c-.013-.204-.079-.75-.071-.93a5.526 5.526 0 0 1-.208-.044c-.274-.045-.725-.121-1.156-.195-.446-.075-.891-.15-1.07-.21-.18-.06-.3-.18-.3-.345 0-.165.12-.285.321-.405.203-.12.58-.281.88-.41.198-.086.326-.15.401-.195-.007-.165-.018-.331-.03-.51-.003-.021-.003-.042-.003-.06-.105-1.628-.23-3.654.299-4.847 1.583-3.545 4.939-3.821 5.929-3.821z"/></svg>""",
    "linkedin": """<svg width="24" height="24" viewBox="0 0 24 24" fill="white"><path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.32 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.79M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z"/></svg>""",
    "twitter": """<svg width="24" height="24" viewBox="0 0 24 24" fill="white"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>"""
}

PLATFORM_EMOJI_ICONS = {
    "Google": "🔍",
    "Apple": "🍎",
    "Garmin": "⌚",
    "Samsung": "📱",
    "Dropbox": "📦",
    "Google Maps": "🗺️",
    "Pinterest": "📌",
    "Spotify": "🎧",
    "EA": "🎮",
    "Nvidia": "🖥️",
    "Wix": "🌐",
    "DeviantArt": "🎨",
    "Dailymotion": "📺",
    "Vimeo": "🎬",
    "MySpace": "🎵",
    "Discord": "💬",
    "Reddit": "📱",
    "TikTok": "📱",
    "YouTube": "▶️",
    "Twitch": "🎮",
    "GitHub": "💻",
    "Steam": "🎮",
    "WhatsApp": "📱"
}

def is_valid_image_url(url):
    """Check if URL is a valid image URL"""
    image_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
    
    if any(url.lower().endswith(ext) for ext in image_extensions):
        return True
        
    if any(domain in url.lower() for domain in ['googleusercontent.com', 'google.com']):
        return True
        
    image_patterns = [
        r'avatars?\.', # Matches avatar URLs
        r'profile.*\.', # Matches profile picture URLs
        r'photos?\.', # Matches photo URLs
        r'images?\.', # Matches image URLs
        r'cdn\.', # Matches CDN URLs
    ]
    
    return any(re.search(pattern, url.lower()) for pattern in image_patterns)

def get_platform_icon(platform_name):
    """Get the appropriate icon for the platform"""
    platform_lower = platform_name.lower()
    
    if platform_lower in PLATFORM_SVG_ICONS:
        return f'<svg-icon>{PLATFORM_SVG_ICONS[platform_lower]}</svg-icon>'
    
    return PLATFORM_EMOJI_ICONS.get(platform_name.capitalize(), "ℹ️")

def get_platform_color(platform_name):
    """Get color based on platform category"""
    social_media = ["Facebook", "Instagram", "Twitter", "LinkedIn", "Snapchat", "TikTok"]
    entertainment = ["Spotify", "YouTube", "Twitch", "Vimeo", "Dailymotion"]
    professional = ["GitHub", "LinkedIn", "Dropbox", "Google"]
    gaming = ["EA", "Steam", "PlayStation", "Xbox"]
    
    if platform_name in social_media:
        return "1"
    elif platform_name in entertainment:
        return "2"
    elif platform_name in professional:
        return "3"
    elif platform_name in gaming:
        return "4"
    return "5"
def create_canvas_card(platform_data, x_pos, y_pos):
    """Create card for platform, even if only name is available"""
    platform_name = platform_data['module'].capitalize()
    icon = get_platform_icon(platform_name)
    
    data_points = {k: v for k, v in platform_data.items() 
                  if v and v.strip() and k != 'module' and k != 'breach'}
    
    card_content = f"""# {icon} {platform_name}

>[!info]+ Profile Information"""

    if platform_data.get('picture_url') and platform_data['picture_url'].strip():
        pic_url = platform_data['picture_url']
        if is_valid_image_url(pic_url):
            card_content += f"\n\n![]({pic_url})"

    if data_points:
        for key, value in sorted(data_points.items()):
            if key == 'picture_url':
                continue
            if key == 'module':
                continue
            display_key = key.replace('_', ' ').title()
            if key == 'bio':
                value = value[:100] + "..." if len(value) > 100 else value
            card_content += f"\n• {display_key}: {value}"
    else:
        card_content += "\n• Status: Account Found"

    if platform_data.get('breach') == 'true':
        card_content += "\n\n>[!danger]+ Breach Detected"
        if platform_data.get('creation_date'):
            card_content += f"\n• Date: {platform_data['creation_date']}"

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
            print("1. Provide CSV file as argument: python social_radar_canvas.py your_file.csv")
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
        print("1. Provide CSV file as argument: python social_radar_canvas.py your_file.csv")
        print("2. Place a CSV file in the same directory as the script")
        raise

if __name__ == "__main__":
    main()