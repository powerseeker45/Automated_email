import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from PIL import Image, ImageDraw, ImageFont
import datetime
import os
from io import BytesIO
import random

class BirthdayImageGenerator:
    def __init__(self, csv_file, smtp_server, smtp_port, email_user, email_password, base_image_path=None):
        self.csv_file = csv_file
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_user = email_user
        self.email_password = email_password
        self.base_image_path = base_image_path
        self.base_image = None
        self.fonts_loaded = False
        self.fonts = {}
        
    def load_fonts(self):
        """Load fonts once and reuse them"""
        if self.fonts_loaded:
            return
            
        try:
            self.fonts = {
                'header': ImageFont.truetype("arialbd.ttf", 36),
                'main': ImageFont.truetype("arialbd.ttf", 80),
                'sub': ImageFont.truetype("arialbd.ttf", 28),
                'name': ImageFont.truetype("arialbd.ttf", 32)
            }
        except:
            default_font = ImageFont.load_default()
            self.fonts = {
                'header': default_font,
                'main': default_font,
                'sub': default_font,
                'name': default_font
            }
        
        self.fonts_loaded = True

    def load_employee_data(self):
        try:
            df = pd.read_csv(self.csv_file)
            required_columns = ['empid', 'first_name', 'second_name', 'email', 'dob', 'department']
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"Missing required column: {col}")

            df['full_name'] = df['first_name'].astype(str) + ' ' + df['second_name'].astype(str)
            df['birthday'] = pd.to_datetime(df['dob'], format='mixed', dayfirst=True)
            return df
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            return None

    def get_todays_birthdays(self, df):
        today = datetime.date.today()
        birthday_employees = []

        for _, employee in df.iterrows():
            emp_birthday = employee['birthday'].date()
            if emp_birthday.month == today.month and emp_birthday.day == today.day:
                birthday_employees.append(employee)

        return birthday_employees

    def create_base_image(self):
        """Create the base birthday image template once"""
        if self.base_image is not None:
            return self.base_image
            
        # Load fonts
        self.load_fonts()
        
        # If user provided a custom base image, use it
        if self.base_image_path and os.path.exists(self.base_image_path):
            try:
                self.base_image = Image.open(self.base_image_path).convert('RGB')
                print(f"Using custom base image: {self.base_image_path}")
                return self.base_image
            except Exception as e:
                print(f"Error loading custom base image: {e}")
                print("Falling back to generated base image...")
        
        # Generate base image
        width, height = 800, 624
        img = Image.new('RGB', (width, height), color='#e40000')
        draw = ImageDraw.Draw(img)

        # Add Airtel logo
        try:
            logo = Image.open("airtel_logo.png").convert("RGBA")
            logo.thumbnail((150, 150))
            img.paste(logo, (width - logo.width - 20, 20), mask=logo)
        except Exception as e:
            print(f"Could not load Airtel logo: {e}")

        # Add static text elements
        header_text = "Wishing you a very"
        header_bbox = draw.textbbox((0, 0), header_text, font=self.fonts['header'])
        header_w = header_bbox[2] - header_bbox[0]
        draw.text(((width - header_w) // 2, 120), header_text, fill="white", font=self.fonts['header'])

        main_text = "Happy Birthday!"
        main_bbox = draw.textbbox((0, 0), main_text, font=self.fonts['main'])
        main_w = main_bbox[2] - main_bbox[0]
        draw.text(((width - main_w) // 2, 180), main_text, fill="white", font=self.fonts['main'])

        # Add cake image
        try:
            cake = Image.open("cake.png").convert("RGBA")
            cake.thumbnail((200, 200))
            cake_x = (width - cake.width) // 2
            cake_y = 300
            img.paste(cake, (cake_x, cake_y), mask=cake)
            y = cake_y + cake.height + 10
        except Exception as e:
            print(f"Could not load cake image: {e}")
            y = 330

        # Add birthday message
        message = (
            "May your birthday be full of happy hours\n"
            "and special moments to remember for a\n"
            "long long time!"
        )
        for line in message.split('\n'):
            line_bbox = draw.textbbox((0, 0), line, font=self.fonts['sub'])
            line_w = line_bbox[2] - line_bbox[0]
            draw.text(((width - line_w) // 2, y), line, fill="white", font=self.fonts['sub'])
            y += 35

        # Add confetti effect
        confetti_colors = ['#ffffff', '#ffd700', '#00ffcc', '#ff69b4', '#add8e6']
        confetti_img = Image.new('RGBA', img.size, (255, 0, 0, 0))
        confetti_draw = ImageDraw.Draw(confetti_img)

        for _ in range(100):
            x = random.randint(0, width)
            y = random.randint(height - 150, height)
            r = random.randint(2, 4)
            color = random.choice(confetti_colors)
            alpha = int(255 * (y - (height - 150)) / 150)
            confetti_color = tuple(int(color[i:i+2], 16) for i in (1, 3, 5)) + (alpha,)
            confetti_draw.ellipse((x - r, y - r, x + r, y + r), fill=confetti_color)

        img = Image.alpha_composite(img.convert('RGBA'), confetti_img)
        self.base_image = img.convert('RGB')
        print("Base birthday image created successfully")
        return self.base_image

    def add_name_to_image(self, name):
        """Add a name to the base image and return the personalized version"""
        # Get base image
        base_img = self.create_base_image()
        
        # Create a copy to modify
        img = base_img.copy()
        draw = ImageDraw.Draw(img)
        
        # Ensure fonts are loaded
        self.load_fonts()
        
        # Add personalized greeting
        dear_text = f"Dear {name},"
        dear_bbox = draw.textbbox((0, 0), dear_text, font=self.fonts['name'])
        dear_w = dear_bbox[2] - dear_bbox[0]
        
        # Position the name text (adjust coordinates as needed for your layout)
        name_y_position = 50
        if self.base_image_path:
            # For custom images, you might want to adjust this position
            name_y_position = 50
            
        draw.text(((img.width - dear_w) // 2, name_y_position), dear_text, fill="white", font=self.fonts['name'])
        
        return img

    def send_birthday_email(self, employee_email, first_name, full_name, department, image_data):
        try:
            msg = MIMEMultipart('related')
            msg['From'] = self.email_user
            msg['To'] = employee_email
            msg['Subject'] = f"\U0001F389 Happy Birthday {first_name}! \U0001F389"

            html_body = f"""
            <html>
                <body>
                    <h2>Happy Birthday, {first_name}!</h2>
                    <p>Dear {full_name},</p>
                    <p>We hope your special day is filled with happiness, laughter, and joy!</p>
                    <p>Best wishes from everyone from Bharti Airtel Family!</p>
                    <br>
                    <img src=\"cid:birthday_image\" alt=\"Birthday Wishes\" style=\"max-width: 100%; height: auto;\">
                    <br><br>
                    <p>Have a wonderful birthday!</p>
                    <p>Warm regards,<br>CEO,<br> Bharti Airtel</p>
                </body>
            </html>
            """

            msg.attach(MIMEText(html_body, 'html'))

            img_attachment = MIMEImage(image_data)
            img_attachment.add_header('Content-ID', '<birthday_image>')
            msg.attach(img_attachment)

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.sendmail(self.email_user, employee_email, msg.as_string())
            server.quit()

            print(f"Birthday email sent successfully to {full_name} ({employee_email})")
            return True

        except Exception as e:
            print(f"Error sending email to {full_name}: {e}")
            return False

    def process_birthdays(self, save_images=True):
        df = self.load_employee_data()
        if df is None:
            return

        birthday_employees = self.get_todays_birthdays(df)

        if not birthday_employees:
            print("No birthdays today!")
            return

        print(f"Found {len(birthday_employees)} birthday(s) today!")
        
        # Create base image once
        print("Creating base birthday image template...")
        self.create_base_image()

        output_dir = "output_img"
        if save_images and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for employee in birthday_employees:
            empid = employee['empid']
            first_name = employee['first_name']
            full_name = employee['full_name']
            email = employee['email']
            department = employee['department']

            print(f"Processing birthday for {full_name} (ID: {empid}, Dept: {department})...")

            # Add name to base image (much faster than creating from scratch)
            birthday_img = self.add_name_to_image(first_name)
            
            # Convert to bytes for email
            img_byte_arr = BytesIO()
            birthday_img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            if save_images:
                img_filename = f"birthday_{empid}_{full_name.replace(' ', '_')}_{datetime.date.today().strftime('%Y%m%d')}.png"
                img_path = os.path.join(output_dir, img_filename)
                birthday_img.save(img_path)
                print(f"Image saved as {img_path}")

            self.send_birthday_email(email, first_name, full_name, department, img_byte_arr)

def main():
    CSV_FILE = "employees.csv"
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    EMAIL_USER = "shashwat.airtel@gmail.com"
    EMAIL_PASSWORD = "rhar coyy iggw faia"
    
    # Optional: Use a custom base image instead of generating one
    # Set to None to use the generated image, or provide path to your PNG file
    CUSTOM_BASE_IMAGE ="visual_test_outputs/base_template.png"   # Example: "custom_birthday_template.png"

    birthday_gen = BirthdayImageGenerator(
        csv_file=CSV_FILE,
        smtp_server=SMTP_SERVER,
        smtp_port=SMTP_PORT,
        email_user=EMAIL_USER,
        email_password=EMAIL_PASSWORD,
        base_image_path=CUSTOM_BASE_IMAGE
    )

    birthday_gen.process_birthdays(save_images=True)

if __name__ == "__main__":
    main()