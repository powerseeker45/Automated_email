from PIL import Image, ImageDraw, ImageFont
import random
import os

class AnniversaryImageCreator:
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

    def draw_star(self, draw, x, y, size, color):
        # A simple 5-point star approximation
        points = [
            (x, y - size),
            (x + size * 0.4, y + size * 0.3),
            (x + size, y + size * 0.3),
            (x + size * 0.5, y + size * 0.6),
            (x + size * 0.6, y + size),
            (x, y + size * 0.8),
            (x - size * 0.6, y + size),
            (x - size * 0.5, y + size * 0.6),
            (x - size, y + size * 0.3),
            (x - size * 0.4, y + size * 0.3)
        ]
        draw.polygon(points, fill=color)

    def draw_heart(self, draw, x, y, size, color):
        top_curve_radius = size // 2
        draw.pieslice([x, y, x + size, y + size], 180, 360, fill=color)
        draw.pieslice([x - size, y, x, y + size], 180, 360, fill=color)
        draw.polygon([
            (x - size, y + top_curve_radius),
            (x + size, y + top_curve_radius),
            (x, y + size * 2)
        ], fill=color)

    def create_base_image(self):
        self.load_fonts()

        if self.base_image_path and os.path.exists(self.base_image_path):
            self.base_image = Image.open(self.base_image_path).convert('RGB')
            return self.base_image

        width, height = 800, 600
        img = Image.new('RGB', (width, height), color='#ffc0cb')  # Baby pink
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
        draw.text(((width - header_w) // 2, vertical_offset), header_text, fill="black", font=self.fonts['header'])

        # Main text
        main_text = "Happy Anniversary!"
        main_w = draw.textlength(main_text, font=self.fonts['main'])
        draw.text(((width - main_w) // 2, vertical_offset + 50), main_text, fill="black", font=self.fonts['main'])

        y = vertical_offset + 160

        # Message
        message = (
            "Wishing you both a lifetime\n"
            "of love, laughter and endless\n"
            "cherished moments together."
        )
        for line in message.split('\n'):
            line_w = draw.textlength(line, font=self.fonts['sub'])
            draw.text(((width - line_w) // 2, y), line, fill="black", font=self.fonts['sub'])
            y += 30

        # Confetti (stars and hearts)
        shapes = ['star', 'heart']
        confetti_colors = ['#ffffff', '#ff69b4', '#ff1493', '#ffd700', '#ffb6c1']
        confetti_img = Image.new('RGBA', img.size, (255, 0, 0, 0))
        confetti_draw = ImageDraw.Draw(confetti_img)

        for _ in range(80):
            x = random.randint(0, width)
            y = random.randint(height - 150, height)
            size = random.randint(8, 16)
            color = random.choice(confetti_colors)
            shape = random.choice(shapes)

            if shape == 'star':
                self.draw_star(confetti_draw, x, y, size // 2, color)
            else:
                self.draw_heart(confetti_draw, x, y, size // 2, color)

        img = Image.alpha_composite(img.convert('RGBA'), confetti_img)
        self.base_image = img.convert('RGB')
        return self.base_image

def create_anniversary_card():
    creator = AnniversaryImageCreator()
    img = creator.create_base_image()

    os.makedirs(creator.assets_folder, exist_ok=True)
    output_path = os.path.join(creator.assets_folder, "anniversary_card.png")
    img.save(output_path)
    print(f"Image saved to {output_path}")

if __name__ == "__main__":
    create_anniversary_card()