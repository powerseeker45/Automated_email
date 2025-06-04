#!/usr/bin/env python3
"""
Script to create sample assets for birthday automation
This creates placeholder images when actual assets are not available
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import random

def create_sample_logo():
    """Create a sample company logo"""
    # Create a simple logo with company name
    width, height = 200, 100
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Background circle
    draw.ellipse([10, 10, width-10, height-10], fill='#e40000', outline='#ffffff', width=3)
    
    # Company text
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    text = "COMPANY"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    draw.text((x, y), text, fill='white', font=font)
    
    return img

def create_sample_cake():
    """Create a sample birthday cake image"""
    width, height = 200, 200
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Cake base (rectangle)
    cake_width = 140
    cake_height = 80
    cake_x = (width - cake_width) // 2
    cake_y = height - cake_height - 20
    
    # Cake layers
    draw.rectangle([cake_x, cake_y, cake_x + cake_width, cake_y + cake_height], 
                  fill='#8B4513', outline='#654321', width=2)
    
    # Frosting
    frosting_height = 15
    draw.rectangle([cake_x, cake_y, cake_x + cake_width, cake_y + frosting_height], 
                  fill='#FFB6C1', outline='#FF69B4', width=1)
    
    # Candles
    candle_count = 5
    candle_width = 4
    candle_height = 25
    candle_spacing = cake_width // (candle_count + 1)
    
    for i in range(candle_count):
        candle_x = cake_x + candle_spacing * (i + 1) - candle_width // 2
        candle_y = cake_y - candle_height
        
        # Candle
        draw.rectangle([candle_x, candle_y, candle_x + candle_width, cake_y], 
                      fill='#FFFF00', outline='#FFD700', width=1)
        
        # Flame
        flame_size = 6
        flame_x = candle_x + candle_width // 2 - flame_size // 2
        flame_y = candle_y - flame_size
        
        draw.ellipse([flame_x, flame_y, flame_x + flame_size, flame_y + flame_size], 
                    fill='#FF4500')
    
    # Add some decorative elements
    for _ in range(10):
        x = random.randint(0, width)
        y = random.randint(0, height // 2)
        size = random.randint(2, 5)
        color = random.choice(['#FFD700', '#FF69B4', '#00FFFF', '#90EE90'])
        draw.ellipse([x, y, x + size, y + size], fill=color)
    
    return img

def create_custom_template():
    """Create a sample custom birthday template"""
    width, height = 800, 624
    img = Image.new('RGB', (width, height), '#e40000')
    draw = ImageDraw.Draw(img)
    
    # Gradient effect (simple)
    for y in range(height):
        color_val = int(228 - (y / height) * 50)  # Fade from 228 to 178
        color = (color_val, 64, 0)
        draw.line([(0, y), (width, y)], fill=color)
    
    # Decorative border
    border_width = 10
    draw.rectangle([border_width, border_width, width-border_width, height-border_width], 
                  outline='#FFD700', width=5)
    
    # Title area (leave space for name at top)
    title_y = 100
    
    try:
        title_font = ImageFont.truetype("arial.ttf", 48)
        header_font = ImageFont.truetype("arial.ttf", 32)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
    
    # Main title
    title_text = "HAPPY BIRTHDAY!"
    bbox = draw.textbbox((0, 0), title_text, font=title_font)
    text_width = bbox[2] - bbox[0]
    x = (width - text_width) // 2
    
    # Text shadow
    draw.text((x + 2, title_y + 2), title_text, fill='#000000', font=title_font)
    draw.text((x, title_y), title_text, fill='#FFFFFF', font=title_font)
    
    # Subtitle
    subtitle_y = title_y + 80
    subtitle_text = "Wishing you joy and happiness!"
    bbox = draw.textbbox((0, 0), subtitle_text, font=header_font)
    text_width = bbox[2] - bbox[0]
    x = (width - text_width) // 2
    
    draw.text((x + 1, subtitle_y + 1), subtitle_text, fill='#000000', font=header_font)
    draw.text((x, subtitle_y), subtitle_text, fill='#FFFFFF', font=header_font)
    
    # Decorative elements
    center_x, center_y = width // 2, height // 2 + 50
    
    # Stars
    star_positions = [
        (center_x - 150, center_y - 50),
        (center_x + 150, center_y - 50),
        (center_x - 200, center_y + 50),
        (center_x + 200, center_y + 50),
        (center_x, center_y + 100)
    ]
    
    for star_x, star_y in star_positions:
        # Simple star shape
        star_size = 15
        points = []
        for i in range(10):
            angle = i * 36  # 360/10 = 36 degrees
            if i % 2 == 0:
                radius = star_size
            else:
                radius = star_size // 2
            
            import math
            x = star_x + radius * math.cos(math.radians(angle - 90))
            y = star_y + radius * math.sin(math.radians(angle - 90))
            points.append((x, y))
        
        draw.polygon(points, fill='#FFD700', outline='#FFA500')
    
    # Bottom message
    bottom_y = height - 100
    bottom_text = "May all your wishes come true!"
    
    try:
        bottom_font = ImageFont.truetype("arial.ttf", 24)
    except:
        bottom_font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), bottom_text, font=bottom_font)
    text_width = bbox[2] - bbox[0]
    x = (width - text_width) // 2
    
    draw.text((x + 1, bottom_y + 1), bottom_text, fill='#000000', font=bottom_font)
    draw.text((x, bottom_y), bottom_text, fill='#FFFFFF', font=bottom_font)
    
    return img

def main():
    """Create sample assets"""
    print("🎨 Creating sample assets...")
    
    # Create assets directory
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    # Create sample logo
    print("Creating sample logo...")
    logo = create_sample_logo()
    logo.save(assets_dir / "logo.png")
    logo.save(assets_dir / "airtel_logo.png")  # Alternative name
    print("✅ Sample logo created")
    
    # Create sample cake
    print("Creating sample cake...")
    cake = create_sample_cake()
    cake.save(assets_dir / "cake.png")
    cake.save("cake.png")  # Also save in root directory
    print("✅ Sample cake created")
    
    # Create custom template
    print("Creating custom birthday template...")
    template = create_custom_template()
    template.save(assets_dir / "custom_birthday_template.png")
    print("✅ Custom template created")
    
    print("\n🎉 Sample assets created successfully!")
    print("\nCreated files:")
    print("- assets/logo.png")
    print("- assets/airtel_logo.png")
    print("- assets/cake.png")
    print("- cake.png")
    print("- assets/custom_birthday_template.png")
    
    print("\n📝 To use custom template, add this to your .env file:")
    print("CUSTOM_BASE_IMAGE=assets/custom_birthday_template.png")

if __name__ == "__main__":
    main()