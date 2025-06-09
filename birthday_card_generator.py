from PIL import Image, ImageDraw, ImageFont
import random
import os

class BirthdayImageCreator:
    def __init__(self, base_image_path=None):
        self.base_image_path = base_image_path
        self.fonts_loaded = False
        self.fonts = {}
        self.base_image = None
        self.assets_folder = "assets"

    def load_fonts(self):
        if self.fonts_loaded:
            return
        try:
            self.fonts = {
                'header': ImageFont.truetype("arialbd.ttf", 32),
                'main': ImageFont.truetype("arialbd.ttf", 72),
                'sub': ImageFont.truetype("arialbd.ttf", 24)
            }
        except:
            default_font = ImageFont.load_default()
            self.fonts = {k: default_font for k in ['header', 'main', 'sub']}
        self.fonts_loaded = True

    def create_base_image(self):
        self.load_fonts()

        if self.base_image_path and os.path.exists(self.base_image_path):
            self.base_image = Image.open(self.base_image_path).convert('RGB')
            return self.base_image

        width, height = 800, 600
        img = Image.new('RGB', (width, height), color='#e40000')
        draw = ImageDraw.Draw(img)

        # Airtel logo
        try:
            logo_path = os.path.join(self.assets_folder, "airtel_logo.png")
            logo = Image.open(logo_path).convert("RGBA")
            logo.thumbnail((100, 100))
            img.paste(logo, (width - logo.width - 20, 20), mask=logo)
        except Exception as e:
            print(f"Logo load failed: {e}")

        # Leave space at the top for name
        vertical_offset = 160

        # Header
        header_text = "Wishing you a very"
        header_w = draw.textlength(header_text, font=self.fonts['header'])
        draw.text(((width - header_w) // 2, vertical_offset), header_text, fill="white", font=self.fonts['header'])

        # Main text
        main_text = "Happy Birthday!"
        main_w = draw.textlength(main_text, font=self.fonts['main'])
        draw.text(((width - main_w) // 2, vertical_offset + 50), main_text, fill="white", font=self.fonts['main'])

        # Cake image
        try:
            cake_path = os.path.join(self.assets_folder, "cake.png")
            cake = Image.open(cake_path).convert("RGBA")
            cake.thumbnail((150, 150))
            cake_x = (width - cake.width) // 2
            cake_y = vertical_offset + 160
            img.paste(cake, (cake_x, cake_y), mask=cake)
            y = cake_y + cake.height + 15
        except Exception as e:
            print(f"Cake load failed: {e}")
            y = vertical_offset + 160 + 150 + 15

        # Message
        message = (
            "May your birthday be full of happy hours\n"
            "and special moments to remember for a\n"
            "long long time!"
        )
        for line in message.split('\n'):
            line_w = draw.textlength(line, font=self.fonts['sub'])
            draw.text(((width - line_w) // 2, y), line, fill="white", font=self.fonts['sub'])
            y += 30

        # Confetti
        confetti_colors = ['#ffffff', '#ffd700', '#00ffcc', '#ff69b4', '#add8e6']
        confetti_img = Image.new('RGBA', img.size, (255, 0, 0, 0))
        confetti_draw = ImageDraw.Draw(confetti_img)

        for _ in range(100):
            x = random.randint(0, width)
            y = random.randint(height - 120, height)
            r = random.randint(2, 4)
            color = random.choice(confetti_colors)
            alpha = int(255 * (y - (height - 120)) / 120)
            rgba = tuple(int(color[i:i+2], 16) for i in (1, 3, 5)) + (alpha,)
            confetti_draw.ellipse((x - r, y - r, x + r, y + r), fill=rgba)

        img = Image.alpha_composite(img.convert('RGBA'), confetti_img)
        self.base_image = img.convert('RGB')
        return self.base_image

# Example usage
if __name__ == "__main__":
    creator = BirthdayImageCreator()
    img = creator.create_base_image()

    # Ensure assets folder exists
    os.makedirs(creator.assets_folder, exist_ok=True)

    # Save image to assets folder
    output_path = os.path.join(creator.assets_folder, "birthday_card.png")
    img.save(output_path)
    print(f"Image saved to {output_path}")
