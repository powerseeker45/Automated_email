from PIL import Image, ImageDraw, ImageFont
import random

def create_birthday_card(name=None, width=800, height=600):
    """
    Create a birthday card matching the provided design
    """
    # Create image with red background
    img = Image.new('RGB', (width, height), color='#E63946')  # Red color similar to the image
    draw = ImageDraw.Draw(img)
    
    # Load fonts - try different font options
    try:
        # Try to load a clean, modern font similar to the image
        header_font = ImageFont.truetype("arial.ttf", 28)
        main_font = ImageFont.truetype("arial.ttf", 72)
        message_font = ImageFont.truetype("arial.ttf", 24)
        name_font = ImageFont.truetype("arial.ttf", 32)
    except:
        try:
            # Fallback to system fonts
            header_font = ImageFont.truetype("calibri.ttf", 28)
            main_font = ImageFont.truetype("calibri.ttf", 72)
            message_font = ImageFont.truetype("calibri.ttf", 24)
            name_font = ImageFont.truetype("calibri.ttf", 32)
        except:
            # Final fallback to default font
            header_font = ImageFont.load_default()
            main_font = ImageFont.load_default()
            message_font = ImageFont.load_default()
            name_font = ImageFont.load_default()
    
    # Draw cake outline icon (simplified version)
    cake_x = 60
    cake_y = 80
    cake_width = 80
    cake_height = 60
    
    # Draw cake base
    draw.rectangle([cake_x, cake_y + 20, cake_x + cake_width, cake_y + cake_height], 
                  outline='white', width=2, fill=None)
    
    # Draw cake top with wavy lines
    wave_points = []
    for i in range(0, cake_width + 1, 10):
        y_offset = 5 * (1 if (i // 10) % 2 == 0 else -1)
        wave_points.extend([cake_x + i, cake_y + 20 + y_offset])
    
    if len(wave_points) >= 4:
        draw.line(wave_points, fill='white', width=2)
    
    # Draw candles
    candle_positions = [cake_x + 20, cake_x + 40, cake_x + 60]
    for candle_x in candle_positions:
        # Candle stick
        draw.line([candle_x, cake_y, candle_x, cake_y + 20], fill='white', width=2)
        # Candle flame (small circle)
        draw.ellipse([candle_x - 3, cake_y - 8, candle_x + 3, cake_y + 2], 
                    outline='white', width=1, fill=None)
    
    # Add confetti dots
    confetti_colors = ['white', '#FFD700', '#87CEEB', '#FF69B4', '#98FB98']
    
    # Create scattered confetti
    random.seed(42)  # For consistent placement
    for _ in range(80):
        x = random.randint(20, width - 20)
        y = random.randint(20, height - 20)
        
        # Skip area where text will be
        if (40 < x < width - 40 and 150 < y < 450):
            continue
            
        color = random.choice(confetti_colors)
        size = random.randint(3, 8)
        draw.ellipse([x - size//2, y - size//2, x + size//2, y + size//2], 
                    fill=color)
    
    # Add personalized greeting if name provided
    current_y = 40
    if name:
        dear_text = f"Dear {name},"
        dear_bbox = draw.textbbox((0, 0), dear_text, font=name_font)
        dear_width = dear_bbox[2] - dear_bbox[0]
        draw.text(((width - dear_width) // 2, current_y), dear_text, 
                 fill='white', font=name_font)
        current_y += 60
    
    # Header text
    header_text = "Wishing you a very"
    header_bbox = draw.textbbox((0, 0), header_text, font=header_font)
    header_width = header_bbox[2] - header_bbox[0]
    draw.text(((width - header_width) // 2, current_y + 120), header_text, 
             fill='white', font=header_font)
    
    # Main "Happy Birthday!" text
    main_text = "Happy"
    main_bbox = draw.textbbox((0, 0), main_text, font=main_font)
    main_width = main_bbox[2] - main_bbox[0]
    draw.text(((width - main_width) // 2, current_y + 160), main_text, 
             fill='white', font=main_font)
    
    birthday_text = "Birthday!"
    birthday_bbox = draw.textbbox((0, 0), birthday_text, font=main_font)
    birthday_width = birthday_bbox[2] - birthday_bbox[0]
    draw.text(((width - birthday_width) // 2, current_y + 240), birthday_text, 
             fill='white', font=main_font)
    
    # Message text
    message_lines = [
        "May your birthday be full of happy hours",
        "and special moments to remember for a",
        "long long time!"
    ]
    
    message_start_y = current_y + 350
    for i, line in enumerate(message_lines):
        line_bbox = draw.textbbox((0, 0), line, font=message_font)
        line_width = line_bbox[2] - line_bbox[0]
        draw.text(((width - line_width) // 2, message_start_y + i * 30), line, 
                 fill='white', font=message_font)
    
    return img

def create_advanced_birthday_card(name=None, width=800, height=600):
    """
    Create an even more accurate version with better cake design
    """
    # Create image with red background
    img = Image.new('RGB', (width, height), color='#E63946')
    draw = ImageDraw.Draw(img)
    
    # Load fonts
    try:
        header_font = ImageFont.truetype("arial.ttf", 26)
        main_font_happy = ImageFont.truetype("arial.ttf", 68)
        main_font_birthday = ImageFont.truetype("arial.ttf", 68)
        message_font = ImageFont.truetype("arial.ttf", 22)
        name_font = ImageFont.truetype("arial.ttf", 30)
    except:
        try:
            header_font = ImageFont.truetype("calibri.ttf", 26)
            main_font_happy = ImageFont.truetype("calibri.ttf", 68)
            main_font_birthday = ImageFont.truetype("calibri.ttf", 68)
            message_font = ImageFont.truetype("calibri.ttf", 22)
            name_font = ImageFont.truetype("calibri.ttf", 30)
        except:
            header_font = ImageFont.load_default()
            main_font_happy = ImageFont.load_default()
            main_font_birthday = ImageFont.load_default()
            message_font = ImageFont.load_default()
            name_font = ImageFont.load_default()
    
    # Create scattered confetti first (background layer)
    confetti_colors = ['#FFFFFF', '#FFD700', '#87CEEB', '#FF69B4', '#98FB98', '#FFA500']
    
    random.seed(42)
    for _ in range(100):
        x = random.randint(0, width)
        y = random.randint(0, height)
        color = random.choice(confetti_colors)
        size = random.randint(2, 6)
        draw.ellipse([x - size//2, y - size//2, x + size//2, y + size//2], 
                    fill=color)
    
    # Draw cake icon - more detailed version
    cake_center_x = 80
    cake_center_y = 120
    
    # Cake base (rectangle)
    cake_base_width = 60
    cake_base_height = 40
    cake_left = cake_center_x - cake_base_width // 2
    cake_right = cake_center_x + cake_base_width // 2
    cake_top = cake_center_y
    cake_bottom = cake_center_y + cake_base_height
    
    # Draw cake base outline
    draw.rectangle([cake_left, cake_top, cake_right, cake_bottom], 
                  outline='white', width=2, fill=None)
    
    # Draw decorative wavy top
    wave_y = cake_top
    wave_points = []
    for x in range(cake_left, cake_right + 1, 8):
        offset = 4 if ((x - cake_left) // 8) % 2 == 0 else -4
        wave_points.extend([x, wave_y + offset])
    
    if len(wave_points) >= 4:
        draw.line(wave_points, fill='white', width=2)
    
    # Draw three candles
    candle_positions = [cake_center_x - 15, cake_center_x, cake_center_x + 15]
    for candle_x in candle_positions:
        # Candle stick
        draw.line([candle_x, cake_top - 20, candle_x, cake_top], fill='white', width=2)
        # Flame (teardrop shape approximation)
        flame_points = [
            candle_x, cake_top - 25,
            candle_x - 3, cake_top - 20,
            candle_x + 3, cake_top - 20
        ]
        draw.polygon(flame_points, fill='white', outline='white')
    
    # Text positioning
    current_y = 40
    
    # Add personalized greeting if name provided
    if name:
        dear_text = f"Dear {name},"
        dear_bbox = draw.textbbox((0, 0), dear_text, font=name_font)
        dear_width = dear_bbox[2] - dear_bbox[0]
        draw.text(((width - dear_width) // 2, current_y), dear_text, 
                 fill='white', font=name_font)
        current_y += 50
    
    # Header text "Wishing you a very"
    header_text = "Wishing you a very"
    header_bbox = draw.textbbox((0, 0), header_text, font=header_font)
    header_width = header_bbox[2] - header_bbox[0]
    draw.text(((width - header_width) // 2, current_y + 180), header_text, 
             fill='white', font=header_font)
    
    # Main text "Happy"
    happy_text = "Happy"
    happy_bbox = draw.textbbox((0, 0), happy_text, font=main_font_happy)
    happy_width = happy_bbox[2] - happy_bbox[0]
    draw.text(((width - happy_width) // 2, current_y + 220), happy_text, 
             fill='white', font=main_font_happy)
    
    # Main text "Birthday!"
    birthday_text = "Birthday!"
    birthday_bbox = draw.textbbox((0, 0), birthday_text, font=main_font_birthday)
    birthday_width = birthday_bbox[2] - birthday_bbox[0]
    draw.text(((width - birthday_width) // 2, current_y + 290), birthday_text, 
             fill='white', font=main_font_birthday)
    
    # Bottom message
    message_lines = [
        "May your birthday be full of happy hours",
        "and special moments to remember for a",
        "long long time!"
    ]
    
    message_start_y = current_y + 400
    for i, line in enumerate(message_lines):
        line_bbox = draw.textbbox((0, 0), line, font=message_font)
        line_width = line_bbox[2] - line_bbox[0]
        draw.text(((width - line_width) // 2, message_start_y + i * 28), line, 
                 fill='white', font=message_font)
    
    return img

# Example usage and test function
def main():
    """Generate sample birthday cards"""
    
    # Create cards with and without names
    print("Generating birthday cards...")
    
    # Card without name
    card1 = create_advanced_birthday_card()
    card1.save("birthday_card_template.png")
    print("✓ Template card saved as 'birthday_card_template.png'")
    
    # Card with name
    card2 = create_advanced_birthday_card(name="Alice")
    card2.save("birthday_card_alice.png")
    print("✓ Personalized card saved as 'birthday_card_alice.png'")
    
    # Test different names
    test_names = ["Bob", "Carol", "David", "Emma"]
    for name in test_names:
        card = create_advanced_birthday_card(name=name)
        card.save(f"birthday_card_{name.lower()}.png")
        print(f"✓ Card for {name} saved as 'birthday_card_{name.lower()}.png'")
    
    print("\nAll birthday cards generated successfully!")
    print("Files are saved in the current directory.")

if __name__ == "__main__":
    main()