import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from PIL import Image, ImageDraw, ImageFont
import datetime
import os
from io import BytesIO

class BirthdayImageGenerator:
    def __init__(self, csv_file, smtp_server, smtp_port, email_user, email_password):
        """
        Initialize the birthday image generator
        
        Args:
            csv_file: Path to CSV file with employee data
            smtp_server: SMTP server for sending emails
            smtp_port: SMTP port
            email_user: Sender email address
            email_password: Sender email password
        """
        self.csv_file = csv_file
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_user = email_user
        self.email_password = email_password
        
    def load_employee_data(self):
        """Load employee data from CSV file"""
        try:
            df = pd.read_csv(self.csv_file)
            # Ensure required columns exist
            required_columns = ['empid', 'first_name', 'second_name', 'email', 'dob', 'department']
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"Missing required column: {col}")
            
            # Create full name by combining first and second name
            df['full_name'] = df['first_name'].astype(str) + ' ' + df['second_name'].astype(str)
            
            # Convert dob column to datetime with flexible format handling
            df['birthday'] = pd.to_datetime(df['dob'], format='mixed', dayfirst=True)
            return df
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            return None
    
    def get_todays_birthdays(self, df):
        """Get employees with birthdays today"""
        today = datetime.date.today()
        birthday_employees = []
        
        for _, employee in df.iterrows():
            emp_birthday = employee['birthday'].date()
            # Check if birthday matches today (month and day)
            if emp_birthday.month == today.month and emp_birthday.day == today.day:
                birthday_employees.append(employee)
        
        return birthday_employees
        
    def create_birthday_image(self, name):
        """Create a personalized Airtel-themed birthday image with larger logo, cake, and gradient confetti"""
        from PIL import ImageFont

        # Image size
        width, height = 800, 600
        img = Image.new('RGB', (width, height), color='#e40000')
        draw = ImageDraw.Draw(img)

        # Load bold/enlarged fonts
        try:
            header_font = ImageFont.truetype("arialbd.ttf", 36)  # Bold header
            main_font = ImageFont.truetype("arialbd.ttf", 80)    # Bold main message
            sub_font = ImageFont.truetype("arialbd.ttf", 28)     # Sub-message
            name_font = ImageFont.truetype("arialbd.ttf", 32)    # Name
        except:
            header_font = ImageFont.load_default()
            main_font = ImageFont.load_default()
            sub_font = ImageFont.load_default()
            name_font = ImageFont.load_default()

        # Airtel logo (top-right) - Larger
        try:
            logo = Image.open("airtel_logo.png").convert("RGBA")
            logo.thumbnail((150, 150))  # Bigger logo
            img.paste(logo, (width - logo.width - 20, 20), mask=logo)
        except Exception as e:
            print(f"Could not load Airtel logo: {e}")

        # Draw "Dear <name>"
        dear_text = f"Dear {name},"
        dear_bbox = draw.textbbox((0, 0), dear_text, font=name_font)
        dear_w = dear_bbox[2] - dear_bbox[0]
        draw.text(((width - dear_w) // 2, 50), dear_text, fill="white", font=name_font)

        # "Wishing you a very"
        header_text = "Wishing you a very"
        header_bbox = draw.textbbox((0, 0), header_text, font=header_font)
        header_w = header_bbox[2] - header_bbox[0]
        draw.text(((width - header_w) // 2, 140), header_text, fill="white", font=header_font)

        # "Happy Birthday!"
        main_text = "Happy Birthday!"
        main_bbox = draw.textbbox((0, 0), main_text, font=main_font)
        main_w = main_bbox[2] - main_bbox[0]
        draw.text(((width - main_w) // 2, 200), main_text, fill="white", font=main_font)

        # Add Cake image (larger)
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

        # Sub-message
        message = (
            "May your birthday be full of happy hours\n"
            "and special moments to remember for a\n"
            "long long time!"
        )
        for line in message.split('\n'):
            line_bbox = draw.textbbox((0, 0), line, font=sub_font)
            line_w = line_bbox[2] - line_bbox[0]
            draw.text(((width - line_w) // 2, y), line, fill="white", font=sub_font)
            y += 35

        # Add confetti (gradient, soft, sparse)
        import random
        confetti_colors = ['#ffffff', '#ffd700', '#00ffcc', '#ff69b4', '#add8e6']
        confetti_img = Image.new('RGBA', img.size, (255, 0, 0, 0))
        confetti_draw = ImageDraw.Draw(confetti_img)

        for _ in range(100):  # Reduced count
            x = random.randint(0, width)
            y = random.randint(height - 150, height)
            r = random.randint(2, 4)
            color = random.choice(confetti_colors)
            alpha = int(255 * (y - (height - 150)) / 150)  # Gradient opacity
            confetti_color = tuple(int(color[i:i+2], 16) for i in (1, 3, 5)) + (alpha,)
            confetti_draw.ellipse((x - r, y - r, x + r, y + r), fill=confetti_color)

        # Merge confetti with main image
        img = Image.alpha_composite(img.convert('RGBA'), confetti_img)

        return img.convert('RGB')  # Return RGB image for saving/sending


    
    def send_birthday_email(self, employee_email, first_name, full_name, department, image_data):
        """Send birthday email with generated image"""
        try:
            # Create message
            msg = MIMEMultipart('related')
            msg['From'] = self.email_user
            msg['To'] = employee_email
            msg['Subject'] = f"🎉 Happy Birthday {first_name}! 🎉"
            
            # Create HTML body
            html_body = f"""
            <html>
                <body>
                    <h2>Happy Birthday, {first_name}!</h2>
                    <p>Dear {full_name},</p>
                    <p>We hope your special day is filled with happiness, laughter, and joy!</p>
                    <p>Best wishes from everyone from Bharti Airtel Family!</p>
                    <br>
                    <img src="cid:birthday_image" alt="Birthday Wishes" style="max-width: 100%; height: auto;">
                    <br><br>
                    <p>Have a wonderful birthday!</p>
                    <p>Warm regards,<br>CEO,<br> Bharti Airtel</p>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Attach image
            img_attachment = MIMEImage(image_data)
            img_attachment.add_header('Content-ID', '<birthday_image>')
            msg.attach(img_attachment)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_user, employee_email, text)
            server.quit()
            
            print(f"Birthday email sent successfully to {full_name} ({employee_email})")
            return True
            
        except Exception as e:
            print(f"Error sending email to {full_name}: {e}")
            return False
    
    def process_birthdays(self, save_images=True):
        """Main function to process today's birthdays"""
        # Load employee data
        df = self.load_employee_data()
        if df is None:
            return
        
        # Get today's birthday employees
        birthday_employees = self.get_todays_birthdays(df)
        
        if not birthday_employees:
            print("No birthdays today!")
            return
        
        print(f"Found {len(birthday_employees)} birthday(s) today!")
        
        # Create images and send emails for each birthday employee
        for employee in birthday_employees:
            empid = employee['empid']
            first_name = employee['first_name']
            full_name = employee['full_name']
            email = employee['email']
            department = employee['department']
            
            print(f"Processing birthday for {full_name} (ID: {empid}, Dept: {department})...")
            
            # Generate birthday image using first name for personalization
            birthday_img = self.create_birthday_image(first_name)
            
            # Convert image to bytes
            img_byte_arr = BytesIO()
            birthday_img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Save image locally if requested
            if save_images:
                img_filename = f"birthday_{empid}_{full_name.replace(' ', '_')}_{datetime.date.today().strftime('%Y%m%d')}.png"
                birthday_img.save(img_filename)
                print(f"Image saved as {img_filename}")
            
            # Send email
            self.send_birthday_email(email, first_name, full_name, department, img_byte_arr)

def main():
    """
    Main function to run the birthday image generator
    
    Setup instructions:
    1. Create a CSV file with columns: empid, first_name, second_name, email, dob, department
    2. DOB format should be YYYY-MM-DD (e.g., 1990-12-25)
    3. Configure your email settings below
    """
    
    # Configuration
    CSV_FILE = "employees.csv"  # Path to your CSV file
    
    # Email configuration (update with your SMTP settings)
    SMTP_SERVER = "smtp.gmail.com"  # For Gmail
    SMTP_PORT = 587
    EMAIL_USER = "parikshit.cansat@gmail.com"  # Your email
    
    # Option 1: Direct password (less secure)
    EMAIL_PASSWORD = "uvwj adhp gvfd ahww"  # Replace with your actual app password
    
    # Option 2: Environment variable (more secure) - Uncomment line below and comment line above
    # EMAIL_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')  # Set this in your environment
    
    # Create birthday generator instance
    birthday_gen = BirthdayImageGenerator(
        csv_file=CSV_FILE,
        smtp_server=SMTP_SERVER,
        smtp_port=SMTP_PORT,
        email_user=EMAIL_USER,
        email_password=EMAIL_PASSWORD
    )
    
    # Process today's birthdays
    birthday_gen.process_birthdays(save_images=True)

if __name__ == "__main__":
  
    # Run the main birthday processor
    main()