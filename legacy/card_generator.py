import os
import random
import math
from PIL import Image, ImageDraw, ImageFont

class CardGenerator:
    def __init__(
        self,
        width=600,
        height=800,
        output_dir="gen_img",
        cake_path="assets/cake.png",
        logo_path="assets/airtel_logo.png"
    ):
        self.width = width
        self.height = height
        self.output_dir = output_dir
        self.cake_path = cake_path
        self.logo_path = logo_path

        os.makedirs(output_dir, exist_ok=True)
        self.load_fonts()

    def load_fonts(self):
        try:
            # Regular & Bold fonts
            self.bold_font = ImageFont.truetype("arialbd.ttf", 60)
            self.title_font = ImageFont.truetype("arialbd.ttf", 56)
            self.regular_font = ImageFont.truetype("arial.ttf", 34)
            self.small_font = ImageFont.truetype("arial.ttf", 26)

            # Cursive font for "Dear <Name>"
            try:
                self.cursive_font = ImageFont.truetype("lucon.ttf", 54)  # Lucida Console fallback
            except:
                self.cursive_font = ImageFont.truetype("ariali.ttf", 54)  # Arial Italic as fallback
        except:
            print("System fonts not found. Using defaults.")
            self.bold_font = self.title_font = self.regular_font = self.small_font = self.cursive_font = ImageFont.load_default()

    def draw_centered_text(self, draw, y, text, font, color="white"):
        text_width = draw.textlength(text, font=font)
        x = (self.width - text_width) // 2
        draw.text((x, y), text, fill=color, font=font)

    def generate(self, first_name, output_name="birthday_card.png"):
        img = Image.new('RGB', (self.width, self.height), color=(220, 38, 38))
        draw = ImageDraw.Draw(img)

        # Airtel Logo
        try:
            logo = Image.open(self.logo_path).convert("RGBA").resize((150, 75))
            img.paste(logo, (self.width - 160, 10), logo)
        except:
            print("Logo not found.")

        # Cake
        try:
            cake = Image.open(self.cake_path).convert("RGBA").resize((250, 250))
            cake_x = (self.width - cake.width) // 2
            img.paste(cake, (cake_x, 200), cake)
        except:
            print("Cake image not found.")

        # Confetti
        for _ in range(120):
            x, y = random.randint(0, self.width), random.randint(0, self.height)
            r = random.choice([2, 3, 4])
            dist = math.sqrt((self.width - x) ** 2 + y ** 2)
            max_dist = math.sqrt(self.width ** 2 + self.height ** 2)
            opacity = int(255 * (1 - dist / max_dist))
            base_color = random.choice([(255, 255, 255), (255, 200, 0), (150, 150, 255), (255, 100, 100)])
            color = base_color + (opacity,)
            confetti = Image.new('RGBA', (r * 2, r * 2), (0, 0, 0, 0))
            ImageDraw.Draw(confetti).ellipse((0, 0, r * 2, r * 2), fill=color)
            img.paste(confetti, (x, y), confetti)

        # Draw text
        draw.text((40, 100), f"Dear {first_name},", fill="white", font=self.cursive_font)
        self.draw_centered_text(draw, 180, "Wishing you a very", self.regular_font)
        self.draw_centered_text(draw, 470, "Happy", self.title_font)
        self.draw_centered_text(draw, 540, "Birthday!", self.title_font)
        self.draw_centered_text(draw, 640, "May your birthday be full of happy hours", self.small_font)
        self.draw_centered_text(draw, 680, "and special moments to remember for a", self.small_font)
        self.draw_centered_text(draw, 720, "long long time!", self.small_font)

        # Save
        output_path = os.path.join(self.output_dir, output_name)
        img.save(output_path)
        print(f"Birthday card saved to: {output_path}")
        return output_path

def main():
    generator = CardGenerator()
    generator.generate("Alice")

if __name__ == "__main__":
    main()
