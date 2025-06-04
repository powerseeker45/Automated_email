import pandas as pd
import smtplib
import schedule
import time
import logging
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, date
from io import BytesIO
import random
from pathlib import Path
from typing import List, Dict, Optional, Union
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class Employee:
    """Data class for employee information"""
    empid: str
    first_name: str
    second_name: str
    email: str
    dob: date
    department: str
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.second_name}"

class BirthdayEmailAutomation:
    """Enhanced Birthday Email Automation System"""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize the birthday automation system"""
        self.setup_logging()
        self.load_configuration(config_file)
        self.base_image: Optional[Image.Image] = None
        self.fonts_loaded = False
        self.fonts: Dict[str, ImageFont.FreeTypeFont] = {}
        
    def setup_logging(self) -> None:
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('birthday_automation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_configuration(self, config_file: Optional[str] = None) -> None:
        """Load configuration from environment variables"""
        self.csv_file = os.getenv('EMPLOYEE_CSV_FILE', 'employees.csv')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        
        # Get required email configuration
        email_user = os.getenv('EMAIL_USER')
        email_password = os.getenv('EMAIL_PASSWORD')
        
        if not email_user or not email_password:
            raise ValueError("EMAIL_USER and EMAIL_PASSWORD environment variables are required")
        
        self.email_user = email_user
        self.email_password = email_password
        
        self.base_image_path = os.getenv('CUSTOM_BASE_IMAGE')
        self.output_dir = os.getenv('OUTPUT_DIR', 'output_img')
        self.company_name = os.getenv('COMPANY_NAME', 'Bharti Airtel')
        self.sender_title = os.getenv('SENDER_TITLE', 'CEO')
        
        self.logger.info("Configuration loaded successfully")
    
    def load_fonts(self) -> None:
        """Load fonts once and cache them"""
        if self.fonts_loaded:
            return
            
        font_paths = {
            'arial_bold': ['arialbd.ttf', 'Arial-Bold.ttf', 'arial-bold.ttf'],
            'arial_regular': ['arial.ttf', 'Arial.ttf', 'arial-regular.ttf'],
            'arial_italic': ['ariali.ttf', 'Arial-Italic.ttf', 'arial-italic.ttf']
        }
        
        def try_load_font(paths: List[str], size: int) -> ImageFont.FreeTypeFont:
            for path in paths:
                try:
                    return ImageFont.truetype(path, size)
                except (OSError, IOError):
                    continue
            # Return default font if no TrueType fonts found
            return ImageFont.load_default()
        
        self.fonts = {
            'header': try_load_font(font_paths['arial_bold'], 36),
            'main': try_load_font(font_paths['arial_bold'], 80),
            'sub': try_load_font(font_paths['arial_bold'], 28),
            'name': try_load_font(font_paths['arial_bold'], 32),
            'cursive': try_load_font(font_paths['arial_italic'], 32)
        }
        
        self.fonts_loaded = True
        self.logger.info("Fonts loaded successfully")

    def load_employee_data(self) -> List[Employee]:
        """Load and validate employee data from CSV"""
        try:
            if not Path(self.csv_file).exists():
                raise FileNotFoundError(f"CSV file not found: {self.csv_file}")
            
            df = pd.read_csv(self.csv_file)
            required_columns = ['empid', 'first_name', 'second_name', 'email', 'dob', 'department']
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")

            employees = []
            for _, row in df.iterrows():
                try:
                    # Parse date with multiple format support
                    birthday = pd.to_datetime(row['dob'], format='mixed', dayfirst=True).date()
                    employee = Employee(
                        empid=str(row['empid']),
                        first_name=str(row['first_name']).strip(),
                        second_name=str(row['second_name']).strip(),
                        email=str(row['email']).strip(),
                        dob=birthday,
                        department=str(row['department']).strip()
                    )
                    employees.append(employee)
                except Exception as e:
                    self.logger.warning(f"Skipping invalid employee record {row.get('empid', 'unknown')}: {e}")
                    continue
            
            self.logger.info(f"Loaded {len(employees)} employee records")
            return employees
            
        except Exception as e:
            self.logger.error(f"Error loading employee data: {e}")
            return []

    def get_birthday_employees(self, employees: List[Employee], target_date: Optional[date] = None) -> List[Employee]:
        """Get employees with birthdays on target date (default: today)"""
        if target_date is None:
            target_date = date.today()
        
        birthday_employees = [
            emp for emp in employees
            if emp.dob.month == target_date.month and emp.dob.day == target_date.day
        ]
        
        self.logger.info(f"Found {len(birthday_employees)} employees with birthdays on {target_date}")
        return birthday_employees

    def create_base_image(self) -> Image.Image:
        """Create or load the base birthday image template"""
        if self.base_image is not None:
            return self.base_image
            
        self.load_fonts()
        
        # Try to load custom base image
        if self.base_image_path and Path(self.base_image_path).exists():
            try:
                self.base_image = Image.open(self.base_image_path).convert('RGB')
                self.logger.info(f"Using custom base image: {self.base_image_path}")
                return self.base_image
            except Exception as e:
                self.logger.warning(f"Error loading custom base image: {e}. Using generated template.")
        
        # Generate base image
        width, height = 800, 650
        img = Image.new('RGB', (width, height), color='#e40000')
        draw = ImageDraw.Draw(img)

        # Add company logo
        logo_paths = ['airtel_logo.png', 'assets/airtel_logo.png', 'logo.png']
        for logo_path in logo_paths:
            if Path(logo_path).exists():
                try:
                    logo = Image.open(logo_path).convert("RGBA")
                    logo.thumbnail((150, 150))
                    img.paste(logo, (width - logo.width - 20, 20), mask=logo)
                    break
                except Exception as e:
                    self.logger.warning(f"Could not load logo from {logo_path}: {e}")

        # Add static text elements
        self._add_centered_text(draw, width, 120, "Wishing you a very", self.fonts['header'], "white")
        self._add_centered_text(draw, width, 180, "Happy Birthday!", self.fonts['main'], "white")

        # Add cake image
        cake_y = 300
        cake_paths = ['cake.png', 'assets/cake.png', 'birthday_cake.png']
        for cake_path in cake_paths:
            if Path(cake_path).exists():
                try:
                    cake = Image.open(cake_path).convert("RGBA")
                    cake.thumbnail((200, 200))
                    cake_x = (width - cake.width) // 2
                    img.paste(cake, (cake_x, cake_y), mask=cake)
                    cake_y += cake.height + 10
                    break
                except Exception as e:
                    self.logger.warning(f"Could not load cake image from {cake_path}: {e}")

        # Add birthday message
        message_lines = [
            "May your birthday be full of happy hours",
            "and special moments to remember for a",
            "long long time!"
        ]
        
        y_pos = cake_y + 20
        for line in message_lines:
            self._add_centered_text(draw, width, y_pos, line, self.fonts['sub'], "white")
            y_pos += 35

        # Add confetti effect
        self._add_confetti_effect(img)
        
        self.base_image = img
        self.logger.info("Base birthday image created successfully")
        return self.base_image

    def _add_centered_text(self, draw: ImageDraw.ImageDraw, width: int, y: int, text: str, font: ImageFont.FreeTypeFont, color: str) -> None:
        """Add centered text to image"""
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y), text, fill=color, font=font)

    def _add_confetti_effect(self, img: Image.Image) -> Image.Image:
        """Add confetti effect to image"""
        confetti_colors = ['#ffffff', '#ffd700', '#00ffcc', '#ff69b4', '#add8e6']
        confetti_img = Image.new('RGBA', img.size, (255, 0, 0, 0))
        confetti_draw = ImageDraw.Draw(confetti_img)

        for _ in range(100):
            x = random.randint(0, img.width)
            y = random.randint(img.height - 150, img.height)
            r = random.randint(2, 4)
            color = random.choice(confetti_colors)
            alpha = int(255 * (y - (img.height - 150)) / 150)
            confetti_color = tuple(int(color[i:i+2], 16) for i in (1, 3, 5)) + (alpha,)
            confetti_draw.ellipse((x - r, y - r, x + r, y + r), fill=confetti_color)

        img_rgba = img.convert('RGBA')
        final_img = Image.alpha_composite(img_rgba, confetti_img)
        return final_img.convert('RGB')

    def create_personalized_image(self, employee: Employee) -> Image.Image:
        """Create personalized birthday image for employee"""
        base_img = self.create_base_image()
        img = base_img.copy()
        draw = ImageDraw.Draw(img)
        
        self.load_fonts()
        
        # Add personalized greeting
        dear_text = f"Dear {employee.first_name},"
        name_y_position = 50
        self._add_centered_text(draw, img.width, name_y_position, dear_text, self.fonts['name'], "white")
        
        return img

    def create_email_content(self, employee: Employee) -> str:
        """Create HTML email content"""
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #e40000; text-align: center;">
                        🎉 Happy Birthday, {employee.first_name}! 🎉
                    </h2>
                    
                    <p>Dear {employee.full_name},</p>
                    
                    <p>On behalf of everyone at {self.company_name}, I want to wish you a very happy birthday!</p>
                    
                    <p>We hope your special day is filled with happiness, laughter, and joy. 
                    Your contributions to the {employee.department} team are truly valued, 
                    and we're grateful to have you as part of our {self.company_name} family.</p>
                    
                    <div style="text-align: center; margin: 20px 0;">
                        <img src="cid:birthday_image" alt="Birthday Wishes" 
                             style="max-width: 100%; height: auto; border-radius: 10px;">
                    </div>
                    
                    <p>May this new year of your life bring you success, happiness, and many wonderful moments!</p>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                        <p>Warm regards,<br>
                        <strong>{self.sender_title}</strong><br>
                        {self.company_name}</p>
                    </div>
                </div>
            </body>
        </html>
        """

    def send_birthday_email(self, employee: Employee, image_data: bytes) -> bool:
        """Send birthday email to employee"""
        try:
            msg = MIMEMultipart('related')
            msg['From'] = self.email_user
            msg['To'] = employee.email
            msg['Subject'] = f"🎉 Happy Birthday {employee.first_name}! 🎉"

            # Add HTML content
            html_content = self.create_email_content(employee)
            msg.attach(MIMEText(html_content, 'html'))

            # Add image attachment
            img_attachment = MIMEImage(image_data)
            img_attachment.add_header('Content-ID', '<birthday_image>')
            msg.attach(img_attachment)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.sendmail(self.email_user, employee.email, msg.as_string())

            self.logger.info(f"Birthday email sent successfully to {employee.full_name} ({employee.email})")
            return True

        except Exception as e:
            self.logger.error(f"Error sending email to {employee.full_name}: {e}")
            return False

    def save_image(self, employee: Employee, image: Image.Image) -> Optional[str]:
        """Save birthday image to disk"""
        try:
            Path(self.output_dir).mkdir(exist_ok=True)
            
            filename = f"birthday_{employee.empid}_{employee.full_name.replace(' ', '_')}_{date.today().strftime('%Y%m%d')}.png"
            filepath = Path(self.output_dir) / filename
            
            image.save(filepath)
            self.logger.info(f"Image saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error saving image for {employee.full_name}: {e}")
            return None

    def process_birthdays(self, save_images: bool = True, target_date: Optional[date] = None) -> Dict[str, int]:
        """Process all birthday emails for the target date"""
        self.logger.info("Starting birthday processing...")
        
        # Load employee data
        employees = self.load_employee_data()
        if not employees:
            self.logger.warning("No employee data loaded")
            return {"processed": 0, "successful": 0, "failed": 0}
        
        # Get birthday employees
        birthday_employees = self.get_birthday_employees(employees, target_date)
        if not birthday_employees:
            self.logger.info("No birthdays today!")
            return {"processed": 0, "successful": 0, "failed": 0}
        
        # Create base image template
        self.logger.info("Creating base birthday image template...")
        self.create_base_image()
        
        # Process each birthday employee
        results = {"processed": 0, "successful": 0, "failed": 0}
        
        for employee in birthday_employees:
            self.logger.info(f"Processing birthday for {employee.full_name} (ID: {employee.empid}, Dept: {employee.department})")
            
            try:
                # Generate personalized image
                birthday_img = self.create_personalized_image(employee)
                
                # Convert to bytes for email
                img_byte_arr = BytesIO()
                birthday_img.save(img_byte_arr, format='PNG')
                img_data = img_byte_arr.getvalue()
                
                # Save image if requested
                if save_images:
                    self.save_image(employee, birthday_img)
                
                # Send email
                if self.send_birthday_email(employee, img_data):
                    results["successful"] += 1
                else:
                    results["failed"] += 1
                
                results["processed"] += 1
                
            except Exception as e:
                self.logger.error(f"Error processing birthday for {employee.full_name}: {e}")
                results["failed"] += 1
                results["processed"] += 1
        
        self.logger.info(f"Birthday processing completed. Results: {results}")
        return results

    def run_daily_check(self) -> None:
        """Run daily birthday check (for scheduling)"""
        self.logger.info("Running daily birthday check...")
        results = self.process_birthdays()
        
        if results["processed"] > 0:
            self.logger.info(f"Processed {results['processed']} birthdays - "
                           f"Successful: {results['successful']}, Failed: {results['failed']}")
        else:
            self.logger.info("No birthdays today")

    def start_scheduler(self, run_time: str = "09:00") -> None:
        """Start the automatic scheduler"""
        self.logger.info(f"Starting birthday automation scheduler - will run daily at {run_time}")
        
        schedule.every().day.at(run_time).do(self.run_daily_check)
        
        # Run once immediately for testing
        self.logger.info("Running initial birthday check...")
        self.run_daily_check()
        
        # Keep the scheduler running
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.logger.info("Scheduler stopped by user")


def create_env_template() -> None:
    """Create a template .env file"""
    env_template = """# Birthday Email Automation Configuration

# Required: Email Configuration
EMAIL_USER=your-email@company.com
EMAIL_PASSWORD=your-app-password-here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Optional: File Paths
EMPLOYEE_CSV_FILE=employees.csv
CUSTOM_BASE_IMAGE=
OUTPUT_DIR=output_img

# Optional: Company Information
COMPANY_NAME=Your Company Name
SENDER_TITLE=CEO

# Optional: Logging
LOG_LEVEL=INFO
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_template)
    
    print("Created .env.template file. Copy it to .env and fill in your configuration.")


def main() -> int:
    """Main function to run the birthday automation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Birthday Email Automation System')
    parser.add_argument('--run-once', action='store_true', help='Run once and exit')
    parser.add_argument('--create-env', action='store_true', help='Create .env template file')
    parser.add_argument('--schedule-time', default='09:00', help='Time to run daily (HH:MM format)')
    parser.add_argument('--no-save-images', action='store_true', help='Don\'t save images to disk')
    parser.add_argument('--date', help='Target date for birthdays (YYYY-MM-DD format)')
    
    args = parser.parse_args()
    
    if args.create_env:
        create_env_template()
        return 0
    
    try:
        automation = BirthdayEmailAutomation()
        
        if args.run_once:
            target_date: Optional[date] = None
            if args.date:
                target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
            
            automation.process_birthdays(
                save_images=not args.no_save_images,
                target_date=target_date
            )
        else:
            automation.start_scheduler(args.schedule_time)
            
    except Exception as e:
        logging.error(f"Failed to start birthday automation: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())