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
        """Create a personalized birthday image"""
        # Create image dimensions
        width, height = 800, 600
        
        # Create a new image with gradient background
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Create gradient background
        for y in range(height):
            # Purple to pink gradient
            r = int(255 * (y / height))
            g = int(100 + 155 * (1 - y / height))
            b = int(255 * (1 - y / height))
            color = (min(255, r), min(255, g), min(255, b))
            draw.line([(0, y), (width, y)], fill=color)
        
        # Try to load a nice font, fallback to default if not available
        try:
            title_font = ImageFont.truetype("arial.ttf", 60)
            name_font = ImageFont.truetype("arial.ttf", 40)
            subtitle_font = ImageFont.truetype("arial.ttf", 30)
        except:
            # Fallback to default font with different sizes
            title_font = ImageFont.load_default()
            name_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # Add text elements
        # Main title
        title_text = "🎉 HAPPY BIRTHDAY! 🎉"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        draw.text((title_x, 100), title_text, fill='white', font=title_font)
        
        # Employee name
        name_text = f"Dear {name}!"
        name_bbox = draw.textbbox((0, 0), name_text, font=name_font)
        name_width = name_bbox[2] - name_bbox[0]
        name_x = (width - name_width) // 2
        draw.text((name_x, 220), name_text, fill='white', font=name_font)
        
        # Birthday message
        message_lines = [
            "Wishing you a fantastic day filled with",
            "happiness, joy, and wonderful surprises!",
            "🎂🎈🎁"
        ]
        
        y_pos = 320
        for line in message_lines:
            line_bbox = draw.textbbox((0, 0), line, font=subtitle_font)
            line_width = line_bbox[2] - line_bbox[0]
            line_x = (width - line_width) // 2
            draw.text((line_x, y_pos), line, fill='white', font=subtitle_font)
            y_pos += 50
        
        # Add decorative elements
        # Draw some celebration circles
        for i in range(20):
            import random
            x = random.randint(50, width - 50)
            y = random.randint(50, height - 50)
            radius = random.randint(5, 15)
            color = random.choice(['yellow', 'orange', 'pink', 'lightblue'])
            draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color)
        
        return img
    
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
                    <p>Best wishes from everyone in the {department} department and the entire team!</p>
                    <br>
                    <img src="cid:birthday_image" alt="Birthday Wishes" style="max-width: 100%; height: auto;">
                    <br><br>
                    <p>Have a wonderful birthday!</p>
                    <p>Warm regards,<br>The Team</p>
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