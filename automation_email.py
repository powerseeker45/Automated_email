import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from PIL import Image, ImageDraw, ImageFont
import datetime
import os
import io
from typing import Optional

class EmailAutomation:
    def __init__(self, smtp_server: str, smtp_port: int, email: str, password: str):
        """
        Initialize email automation system
        
        Args:
            smtp_server: SMTP server (e.g., 'smtp.gmail.com')
            smtp_port: SMTP port (e.g., 587 for TLS)
            email: Sender email address
            password: Email password or app password
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = email
        self.password = password
        
    def load_employee_data(self, csv_file: str) -> pd.DataFrame:
        """
        Load employee data from CSV file
        
        Expected CSV columns:
        - first_name: Employee's first name
        - last_name: Employee's last name
        - email: Employee's email address
        - birthday: Birthday in YYYY-MM-DD format
        - anniversary: Work anniversary in YYYY-MM-DD format
        """
        try:
            df = pd.read_csv(csv_file)
            # Convert date columns to datetime
            df['birthday'] = pd.to_datetime(df['birthday'], errors='coerce')
            df['anniversary'] = pd.to_datetime(df['anniversary'], errors='coerce')
            return df
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            return pd.DataFrame()
    
    def add_text_to_image(self, image_path: str, text: str, 
                         position: tuple = (50, 50), 
                         font_size: int = 40,
                         font_color: tuple = (0, 0, 0)) -> bytes:
        """
        Add personalized text to greeting card image
        
        Args:
            image_path: Path to the greeting card image
            text: Text to add (e.g., "Dear John")
            position: (x, y) position for text placement
            font_size: Size of the font
            font_color: RGB color tuple for text
            
        Returns:
            Modified image as bytes
        """
        try:
            # Open the image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Create drawing context
                draw = ImageDraw.Draw(img)
                
                # Try to use a nice font, fallback to default if not available
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    try:
                        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)  # macOS
                    except:
                        font = ImageFont.load_default()
                
                # Add text to image
                draw.text(position, text, font=font, fill=font_color)
                
                # Save to bytes
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='JPEG', quality=95)
                img_bytes.seek(0)
                
                return img_bytes.getvalue()
                
        except Exception as e:
            print(f"Error processing image: {e}")
            return None
    
    def create_email_message(self, recipient_email: str, recipient_name: str, 
                           subject: str, body: str, image_bytes: bytes) -> MIMEMultipart:
        """
        Create email message with personalized greeting card
        """
        msg = MIMEMultipart('related')
        msg['From'] = self.sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # Create HTML body that references the embedded image
        html_body = f"""
        <html>
            <body>
                <p>{body}</p>
                <br>
                <img src="cid:greeting_card" style="max-width: 600px; height: auto;">
                <br><br>
                <p>Best wishes,<br>HR Team</p>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Attach the personalized image
        if image_bytes:
            img = MIMEImage(image_bytes)
            img.add_header('Content-ID', '<greeting_card>')
            msg.attach(img)
        
        return msg
    
    def send_email(self, msg: MIMEMultipart) -> bool:
        """
        Send email using SMTP
        """
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.password)
            
            text = msg.as_string()
            server.sendmail(self.sender_email, msg['To'], text)
            server.quit()
            
            print(f"Email sent successfully to {msg['To']}")
            return True
            
        except Exception as e:
            print(f"Error sending email to {msg['To']}: {e}")
            return False
    
    def check_and_send_birthday_emails(self, df: pd.DataFrame, 
                                     birthday_card_path: str,
                                     text_position: tuple = (50, 50)):
        """
        Check for today's birthdays and send emails
        """
        today = datetime.date.today()
        
        # Filter employees with birthdays today
        birthday_employees = df[
            (df['birthday'].dt.month == today.month) & 
            (df['birthday'].dt.day == today.day)
        ]
        
        for _, employee in birthday_employees.iterrows():
            first_name = employee['first_name']
            email = employee['email']
            
            # Create personalized greeting
            greeting_text = f"Dear {first_name}"
            
            # Add text to birthday card
            personalized_image = self.add_text_to_image(
                birthday_card_path, 
                greeting_text, 
                text_position
            )
            
            if personalized_image:
                # Create email
                subject = f"Happy Birthday, {first_name}! 🎉"
                body = f"Dear {first_name},<br><br>Wishing you a very happy birthday! May this special day bring you joy, happiness, and wonderful memories."
                
                msg = self.create_email_message(
                    email, first_name, subject, body, personalized_image
                )
                
                # Send email
                self.send_email(msg)
    
    def check_and_send_anniversary_emails(self, df: pd.DataFrame, 
                                        anniversary_card_path: str,
                                        text_position: tuple = (50, 50)):
        """
        Check for today's work anniversaries and send emails
        """
        today = datetime.date.today()
        
        # Filter employees with anniversaries today
        anniversary_employees = df[
            (df['anniversary'].dt.month == today.month) & 
            (df['anniversary'].dt.day == today.day)
        ]
        
        for _, employee in anniversary_employees.iterrows():
            first_name = employee['first_name']
            email = employee['email']
            
            # Calculate years of service
            years = today.year - employee['anniversary'].year
            
            # Create personalized greeting
            greeting_text = f"Dear {first_name}"
            
            # Add text to anniversary card
            personalized_image = self.add_text_to_image(
                anniversary_card_path, 
                greeting_text, 
                text_position
            )
            
            if personalized_image:
                # Create email
                subject = f"Happy Work Anniversary, {first_name}! 🎊"
                body = f"Dear {first_name},<br><br>Congratulations on completing {years} wonderful years with us! Thank you for your dedication and valuable contributions to our team."
                
                msg = self.create_email_message(
                    email, first_name, subject, body, personalized_image
                )
                
                # Send email
                self.send_email(msg)
    
    def run_daily_check(self, csv_file: str, birthday_card_path: str, 
                       anniversary_card_path: str, 
                       birthday_text_pos: tuple = (50, 50),
                       anniversary_text_pos: tuple = (50, 50)):
        """
        Run daily check for birthdays and anniversaries
        """
        print(f"Running daily email check for {datetime.date.today()}")
        
        # Load employee data
        df = self.load_employee_data(csv_file)
        
        if df.empty:
            print("No employee data found.")
            return
        
        # Check and send birthday emails
        if os.path.exists(birthday_card_path):
            print("Checking for birthdays...")
            self.check_and_send_birthday_emails(df, birthday_card_path, birthday_text_pos)
        else:
            print(f"Birthday card image not found: {birthday_card_path}")
        
        # Check and send anniversary emails
        if os.path.exists(anniversary_card_path):
            print("Checking for anniversaries...")
            self.check_and_send_anniversary_emails(df, anniversary_card_path, anniversary_text_pos)
        else:
            print(f"Anniversary card image not found: {anniversary_card_path}")


# Example usage and configuration
def main():
    # Email configuration
    SMTP_SERVER = "smtp.gmail.com"  # Change based on your email provider
    SMTP_PORT = 587
    SENDER_EMAIL = "shashwat.airtel@gmail.com"  # Replace with your email
    EMAIL_PASSWORD = "glws titd eisr lslz"  # Replace with your app password
    
    # File paths
    CSV_FILE = "employees.csv"
    BIRTHDAY_CARD = "birthday_card.png"
    ANNIVERSARY_CARD = "anniversery_card.png"
    
    # Text positioning on cards (adjust based on your card design)
    BIRTHDAY_TEXT_POSITION = (100, 80)
    ANNIVERSARY_TEXT_POSITION = (100, 80)
    
    # Initialize email automation
    email_system = EmailAutomation(SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, EMAIL_PASSWORD)
    
    # Run daily check
    email_system.run_daily_check(
        CSV_FILE, 
        BIRTHDAY_CARD, 
        ANNIVERSARY_CARD,
        BIRTHDAY_TEXT_POSITION,
        ANNIVERSARY_TEXT_POSITION
    )

if __name__ == "__main__":
    main()


# Example CSV structure (save as employees.csv)
"""
first_name,last_name,email,birthday,anniversary
John,Doe,john.doe@company.com,1990-06-09,2020-03-15
Jane,Smith,jane.smith@company.com,1985-12-25,2019-06-09
Bob,Johnson,bob.johnson@company.com,1992-06-09,2021-01-10
"""