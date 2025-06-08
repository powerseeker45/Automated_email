# Project Structure:
# email_automation_project/
# ├── app/
# │   ├── __init__.py
# │   ├── main.py
# │   ├── email_sender.py
# │   ├── image_processor.py
# │   ├── data_manager.py
# │   └── web_interface.py
# ├── config/
# │   ├── __init__.py
# │   ├── settings.py
# │   └── email_templates.py
# ├── data/
# │   ├── employees.csv
# │   └── sample_employees.csv
# ├── images/
# │   ├── birthday_card.jpg
# │   └── anniversary_card.jpg
# ├── logs/
# │   └── .gitkeep
# ├── tests/
# │   ├── __init__.py
# │   ├── test_email_sender.py
# │   └── test_data_manager.py
# ├── templates/
# │   ├── index.html
# │   ├── upload.html
# │   └── logs.html
# ├── static/
# │   ├── css/
# │   │   └── style.css
# │   └── js/
# │       └── main.js
# ├── requirements.txt
# ├── setup.py
# ├── README.md
# ├── .env.example
# ├── .gitignore
# ├── run_scheduler.py
# └── docker-compose.yml

# =============================================================================
# requirements.txt
# =============================================================================
"""
pandas==2.1.4
Pillow==10.1.0
python-dotenv==1.0.0
schedule==1.2.0
flask==3.0.0
flask-wtf==1.2.1
wtforms==3.1.1
smtplib-ssl==1.3.0
python-dateutil==2.8.2
jinja2==3.1.2
gunicorn==21.2.0
pytest==7.4.3
pytest-cov==4.1.0
"""

# =============================================================================
# .env.example
# =============================================================================
"""
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SENDER_NAME=HR Team

# Application Configuration
DEBUG=False
SECRET_KEY=your_secret_key_here
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# Paths
CSV_FILE_PATH=data/employees.csv
BIRTHDAY_CARD_PATH=images/birthday_card.jpg
ANNIVERSARY_CARD_PATH=images/anniversary_card.jpg
LOG_FILE_PATH=logs/email_automation.log

# Text Positioning (x, y coordinates)
BIRTHDAY_TEXT_X=100
BIRTHDAY_TEXT_Y=80
ANNIVERSARY_TEXT_X=100
ANNIVERSARY_TEXT_Y=80

# Email Settings
FONT_SIZE=40
FONT_COLOR_R=0
FONT_COLOR_G=0
FONT_COLOR_B=0
"""

# =============================================================================
# config/settings.py
# =============================================================================
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Email settings
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SENDER_EMAIL = os.getenv('SENDER_EMAIL')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    SENDER_NAME = os.getenv('SENDER_NAME', 'HR Team')
    
    # Application settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    
    # File paths
    CSV_FILE_PATH = os.getenv('CSV_FILE_PATH', 'data/employees.csv')
    BIRTHDAY_CARD_PATH = os.getenv('BIRTHDAY_CARD_PATH', 'images/birthday_card.jpg')
    ANNIVERSARY_CARD_PATH = os.getenv('ANNIVERSARY_CARD_PATH', 'images/anniversary_card.jpg')
    LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', 'logs/email_automation.log')
    
    # Text positioning
    BIRTHDAY_TEXT_POSITION = (
        int(os.getenv('BIRTHDAY_TEXT_X', 100)),
        int(os.getenv('BIRTHDAY_TEXT_Y', 80))
    )
    ANNIVERSARY_TEXT_POSITION = (
        int(os.getenv('ANNIVERSARY_TEXT_X', 100)),
        int(os.getenv('ANNIVERSARY_TEXT_Y', 80))
    )
    
    # Font settings
    FONT_SIZE = int(os.getenv('FONT_SIZE', 40))
    FONT_COLOR = (
        int(os.getenv('FONT_COLOR_R', 0)),
        int(os.getenv('FONT_COLOR_G', 0)),
        int(os.getenv('FONT_COLOR_B', 0))
    )

# =============================================================================
# config/email_templates.py
# =============================================================================
class EmailTemplates:
    BIRTHDAY_SUBJECT = "Happy Birthday, {first_name}! 🎉"
    BIRTHDAY_BODY = """
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4CAF50;">Happy Birthday, {first_name}!</h2>
                <p>Dear {first_name},</p>
                <p>Wishing you a very happy birthday! May this special day bring you joy, happiness, and wonderful memories.</p>
                <p>We're grateful to have you as part of our team and hope you have a fantastic celebration!</p>
                <br>
                <img src="cid:greeting_card" style="max-width: 100%; height: auto; border-radius: 10px;">
                <br><br>
                <p>Warm wishes,<br><strong>{sender_name}</strong></p>
            </div>
        </body>
    </html>
    """
    
    ANNIVERSARY_SUBJECT = "Happy Work Anniversary, {first_name}! 🎊"
    ANNIVERSARY_BODY = """
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2196F3;">Happy Work Anniversary, {first_name}!</h2>
                <p>Dear {first_name},</p>
                <p>Congratulations on completing {years} wonderful year{plural} with us!</p>
                <p>Thank you for your dedication, hard work, and valuable contributions to our team. Your commitment has made a significant impact on our success.</p>
                <p>Here's to many more years of growth and achievements together!</p>
                <br>
                <img src="cid:greeting_card" style="max-width: 100%; height: auto; border-radius: 10px;">
                <br><br>
                <p>Best regards,<br><strong>{sender_name}</strong></p>
            </div>
        </body>
    </html>
    """

# =============================================================================
# app/data_manager.py
# =============================================================================
import pandas as pd
import datetime
import logging
from typing import List, Dict, Optional
from config.settings import Config

logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self, csv_path: str = None):
        self.csv_path = csv_path or Config.CSV_FILE_PATH
        
    def load_employee_data(self) -> pd.DataFrame:
        """Load and validate employee data from CSV"""
        try:
            df = pd.read_csv(self.csv_path)
            
            # Validate required columns
            required_columns = ['first_name', 'last_name', 'email', 'birthday', 'anniversary']
            missing_columns = set(required_columns) - set(df.columns)
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Convert date columns
            df['birthday'] = pd.to_datetime(df['birthday'], errors='coerce')
            df['anniversary'] = pd.to_datetime(df['anniversary'], errors='coerce')
            
            # Remove rows with invalid dates
            initial_count = len(df)
            df = df.dropna(subset=['birthday', 'anniversary'])
            
            if len(df) < initial_count:
                logger.warning(f"Removed {initial_count - len(df)} rows with invalid dates")
            
            logger.info(f"Loaded {len(df)} employee records")
            return df
            
        except FileNotFoundError:
            logger.error(f"CSV file not found: {self.csv_path}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error loading employee data: {e}")
            return pd.DataFrame()
    
    def get_today_birthdays(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get employees with birthdays today"""
        today = datetime.date.today()
        return df[
            (df['birthday'].dt.month == today.month) & 
            (df['birthday'].dt.day == today.day)
        ]
    
    def get_today_anniversaries(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get employees with work anniversaries today"""
        today = datetime.date.today()
        return df[
            (df['anniversary'].dt.month == today.month) & 
            (df['anniversary'].dt.day == today.day)
        ]
    
    def validate_csv_format(self, file_path: str) -> Dict[str, any]:
        """Validate CSV file format and return validation result"""
        try:
            df = pd.read_csv(file_path)
            
            required_columns = ['first_name', 'last_name', 'email', 'birthday', 'anniversary']
            missing_columns = set(required_columns) - set(df.columns)
            
            # Check date formats
            date_errors = []
            try:
                pd.to_datetime(df['birthday'], errors='raise')
            except:
                date_errors.append('birthday')
            
            try:
                pd.to_datetime(df['anniversary'], errors='raise')
            except:
                date_errors.append('anniversary')
            
            return {
                'valid': len(missing_columns) == 0 and len(date_errors) == 0,
                'missing_columns': list(missing_columns),
                'date_errors': date_errors,
                'row_count': len(df)
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }

# =============================================================================
# app/image_processor.py
# =============================================================================
from PIL import Image, ImageDraw, ImageFont
import io
import logging
from config.settings import Config

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self):
        self.font_size = Config.FONT_SIZE
        self.font_color = Config.FONT_COLOR
    
    def add_text_to_image(self, image_path: str, text: str, 
                         position: tuple, font_size: int = None) -> bytes:
        """Add personalized text to greeting card image"""
        try:
            font_size = font_size or self.font_size
            
            with Image.open(image_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                draw = ImageDraw.Draw(img)
                
                # Try to load a nice font
                font = self._get_font(font_size)
                
                # Add text with shadow for better visibility
                shadow_offset = 2
                # Shadow
                draw.text((position[0] + shadow_offset, position[1] + shadow_offset), 
                         text, font=font, fill=(128, 128, 128))
                # Main text
                draw.text(position, text, font=font, fill=self.font_color)
                
                # Convert to bytes
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='JPEG', quality=95)
                img_bytes.seek(0)
                
                logger.info(f"Successfully processed image with text: {text}")
                return img_bytes.getvalue()
                
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            return None
    
    def _get_font(self, size: int):
        """Get the best available font"""
        font_paths = [
            "arial.ttf",  # Windows
            "/System/Library/Fonts/Arial.ttf",  # macOS
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            "/usr/share/fonts/TTF/arial.ttf"  # Some Linux distributions
        ]
        
        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, size)
            except:
                continue
        
        # Fallback to default font
        return ImageFont.load_default()

# =============================================================================
# app/email_sender.py
# =============================================================================
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import logging
from typing import Dict, List
from config.settings import Config
from config.email_templates import EmailTemplates

logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self):
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.sender_email = Config.SENDER_EMAIL
        self.password = Config.EMAIL_PASSWORD
        self.sender_name = Config.SENDER_NAME
        
    def create_email_message(self, recipient_email: str, subject: str, 
                           html_body: str, image_bytes: bytes = None) -> MIMEMultipart:
        """Create email message with optional image attachment"""
        msg = MIMEMultipart('related')
        msg['From'] = f"{self.sender_name} <{self.sender_email}>"
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(html_body, 'html'))
        
        if image_bytes:
            img = MIMEImage(image_bytes)
            img.add_header('Content-ID', '<greeting_card>')
            msg.attach(img)
        
        return msg
    
    def send_email(self, msg: MIMEMultipart) -> bool:
        """Send email using SMTP"""
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.password)
                
                text = msg.as_string()
                server.sendmail(self.sender_email, msg['To'], text)
                
            logger.info(f"Email sent successfully to {msg['To']}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email to {msg['To']}: {e}")
            return False
    
    def send_birthday_email(self, employee_data: Dict, image_bytes: bytes) -> bool:
        """Send birthday email to employee"""
        first_name = employee_data['first_name']
        email = employee_data['email']
        
        subject = EmailTemplates.BIRTHDAY_SUBJECT.format(first_name=first_name)
        body = EmailTemplates.BIRTHDAY_BODY.format(
            first_name=first_name,
            sender_name=self.sender_name
        )
        
        msg = self.create_email_message(email, subject, body, image_bytes)
        return self.send_email(msg)
    
    def send_anniversary_email(self, employee_data: Dict, years: int, image_bytes: bytes) -> bool:
        """Send anniversary email to employee"""
        first_name = employee_data['first_name']
        email = employee_data['email']
        
        subject = EmailTemplates.ANNIVERSARY_SUBJECT.format(first_name=first_name)
        body = EmailTemplates.ANNIVERSARY_BODY.format(
            first_name=first_name,
            years=years,
            plural='s' if years != 1 else '',
            sender_name=self.sender_name
        )
        
        msg = self.create_email_message(email, subject, body, image_bytes)
        return self.send_email(msg)
    
    def test_email_connection(self) -> Dict[str, any]:
        """Test email connection and credentials"""
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.password)
            
            return {'success': True, 'message': 'Email connection successful'}
            
        except Exception as e:
            return {'success': False, 'message': f'Email connection failed: {str(e)}'}

# =============================================================================
# app/main.py
# =============================================================================
import datetime
import logging
import os
from typing import Dict, List
from app.data_manager import DataManager
from app.image_processor import ImageProcessor
from app.email_sender import EmailSender
from config.settings import Config

# Setup logging
def setup_logging():
    os.makedirs(os.path.dirname(Config.LOG_FILE_PATH), exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(Config.LOG_FILE_PATH),
            logging.StreamHandler()
        ]
    )

class EmailAutomationSystem:
    def __init__(self):
        self.data_manager = DataManager()
        self.image_processor = ImageProcessor()
        self.email_sender = EmailSender()
        self.logger = logging.getLogger(__name__)
    
    def run_daily_check(self) -> Dict[str, any]:
        """Run daily check for birthdays and anniversaries"""
        self.logger.info(f"Starting daily email check for {datetime.date.today()}")
        
        results = {
            'date': datetime.date.today().isoformat(),
            'birthdays_sent': 0,
            'anniversaries_sent': 0,
            'errors': []
        }
        
        try:
            # Load employee data
            df = self.data_manager.load_employee_data()
            if df.empty:
                self.logger.warning("No employee data found")
                results['errors'].append("No employee data found")
                return results
            
            # Process birthdays
            birthday_results = self._process_birthdays(df)
            results['birthdays_sent'] = birthday_results['sent']
            results['errors'].extend(birthday_results['errors'])
            
            # Process anniversaries
            anniversary_results = self._process_anniversaries(df)
            results['anniversaries_sent'] = anniversary_results['sent']
            results['errors'].extend(anniversary_results['errors'])
            
            self.logger.info(f"Daily check completed. Birthdays: {results['birthdays_sent']}, Anniversaries: {results['anniversaries_sent']}")
            
        except Exception as e:
            error_msg = f"Error in daily check: {str(e)}"
            self.logger.error(error_msg)
            results['errors'].append(error_msg)
        
        return results
    
    def _process_birthdays(self, df) -> Dict[str, any]:
        """Process birthday emails"""
        results = {'sent': 0, 'errors': []}
        
        birthday_employees = self.data_manager.get_today_birthdays(df)
        
        if birthday_employees.empty:
            self.logger.info("No birthdays today")
            return results
        
        if not os.path.exists(Config.BIRTHDAY_CARD_PATH):
            error_msg = f"Birthday card image not found: {Config.BIRTHDAY_CARD_PATH}"
            self.logger.error(error_msg)
            results['errors'].append(error_msg)
            return results
        
        for _, employee in birthday_employees.iterrows():
            try:
                first_name = employee['first_name']
                greeting_text = f"Dear {first_name}"
                
                # Create personalized image
                image_bytes = self.image_processor.add_text_to_image(
                    Config.BIRTHDAY_CARD_PATH,
                    greeting_text,
                    Config.BIRTHDAY_TEXT_POSITION
                )
                
                if image_bytes:
                    success = self.email_sender.send_birthday_email(
                        employee.to_dict(), image_bytes
                    )
                    if success:
                        results['sent'] += 1
                    else:
                        results['errors'].append(f"Failed to send birthday email to {employee['email']}")
                else:
                    results['errors'].append(f"Failed to process birthday card for {first_name}")
                    
            except Exception as e:
                error_msg = f"Error processing birthday for {employee.get('first_name', 'Unknown')}: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        
        return results
    
    def _process_anniversaries(self, df) -> Dict[str, any]:
        """Process anniversary emails"""
        results = {'sent': 0, 'errors': []}
        
        anniversary_employees = self.data_manager.get_today_anniversaries(df)
        
        if anniversary_employees.empty:
            self.logger.info("No anniversaries today")
            return results
        
        if not os.path.exists(Config.ANNIVERSARY_CARD_PATH):
            error_msg = f"Anniversary card image not found: {Config.ANNIVERSARY_CARD_PATH}"
            self.logger.error(error_msg)
            results['errors'].append(error_msg)
            return results
        
        today = datetime.date.today()
        
        for _, employee in anniversary_employees.iterrows():
            try:
                first_name = employee['first_name']
                years = today.year - employee['anniversary'].year
                greeting_text = f"Dear {first_name}"
                
                # Create personalized image
                image_bytes = self.image_processor.add_text_to_image(
                    Config.ANNIVERSARY_CARD_PATH,
                    greeting_text,
                    Config.ANNIVERSARY_TEXT_POSITION
                )
                
                if image_bytes:
                    success = self.email_sender.send_anniversary_email(
                        employee.to_dict(), years, image_bytes
                    )
                    if success:
                        results['sent'] += 1
                    else:
                        results['errors'].append(f"Failed to send anniversary email to {employee['email']}")
                else:
                    results['errors'].append(f"Failed to process anniversary card for {first_name}")
                    
            except Exception as e:
                error_msg = f"Error processing anniversary for {employee.get('first_name', 'Unknown')}: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        
        return results

def main():
    """Main function to run the email automation system"""
    setup_logging()
    system = EmailAutomationSystem()
    results = system.run_daily_check()
    
    print(f"Email automation completed:")
    print(f"Date: {results['date']}")
    print(f"Birthdays sent: {results['birthdays_sent']}")
    print(f"Anniversaries sent: {results['anniversaries_sent']}")
    
    if results['errors']:
        print(f"Errors: {len(results['errors'])}")
        for error in results['errors']:
            print(f"  - {error}")

if __name__ == "__main__":
    main()

# =============================================================================
# app/web_interface.py
# =============================================================================
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from app.main import EmailAutomationSystem, setup_logging
from app.data_manager import DataManager
from app.email_sender import EmailSender
from config.settings import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    setup_logging()
    
    @app.route('/')
    def index():
        """Main dashboard"""
        return render_template('index.html')
    
    @app.route('/upload', methods=['GET', 'POST'])
    def upload_files():
        """Upload CSV and image files"""
        if request.method == 'POST':
            try:
                # Handle CSV upload
                if 'csv_file' in request.files:
                    csv_file = request.files['csv_file']
                    if csv_file.filename:
                        filename = secure_filename(csv_file.filename)
                        csv_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        csv_file.save(csv_path)
                        
                        # Validate CSV
                        data_manager = DataManager()
                        validation = data_manager.validate_csv_format(csv_path)
                        
                        if validation['valid']:
                            # Move to data folder
                            os.rename(csv_path, Config.CSV_FILE_PATH)
                            flash(f'CSV file uploaded successfully! {validation["row_count"]} records found.', 'success')
                        else:
                            flash(f'CSV validation failed: {validation.get("error", "Invalid format")}', 'error')
                
                # Handle image uploads
                for file_type in ['birthday_card', 'anniversary_card']:
                    if file_type in request.files:
                        image_file = request.files[file_type]
                        if image_file.filename:
                            filename = secure_filename(image_file.filename)
                            if file_type == 'birthday_card':
                                image_path = Config.BIRTHDAY_CARD_PATH
                            else:
                                image_path = Config.ANNIVERSARY_CARD_PATH
                            
                            os.makedirs(os.path.dirname(image_path), exist_ok=True)
                            image_file.save(image_path)
                            flash(f'{file_type.replace("_", " ").title()} uploaded successfully!', 'success')
                
                return redirect(url_for('upload_files'))
                
            except Exception as e:
                flash(f'Upload error: {str(e)}', 'error')
        
        return render_template('upload.html')
    
    @app.route('/test-email', methods=['POST'])
    def test_email():
        """Test email configuration"""
        try:
            email_sender = EmailSender()
            result = email_sender.test_email_connection()
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
    
    @app.route('/run-check', methods=['POST'])
    def run_check():
        """Manually run the daily check"""
        try:
            system = EmailAutomationSystem()
            results = system.run_daily_check()
            return jsonify(results)
        except Exception as e:
            return jsonify({'error': str(e)})
    
    @app.route('/logs')
    def view_logs():
        """View system logs"""
        try:
            with open(Config.LOG_FILE_PATH, 'r') as f:
                logs = f.readlines()[-100:]  # Last 100 lines
            return render_template('logs.html', logs=logs)
        except FileNotFoundError:
            return render_template('logs.html', logs=['No logs found'])
    
    @app.route('/status')
    def system_status():
        """Get system status"""
        status = {
            'csv_file_exists': os.path.exists(Config.CSV_FILE_PATH),
            'birthday_card_exists': os.path.exists(Config.BIRTHDAY_CARD_PATH),
            'anniversary_card_exists': os.path.exists(Config.ANNIVERSARY_CARD_PATH),
            'email_configured': bool(Config.SENDER_EMAIL and Config.EMAIL_PASSWORD)
        }
        
        if status['csv_file_exists']:
            try:
                data_manager = DataManager()
                df = data_manager.load_employee_data()
                status['employee_count'] = len(df)
                status['today_birthdays'] = len(data_manager.get_today_birthdays(df))
                status['today_anniversaries'] = len(data_manager.get_today_anniversaries(df))
            except:
                status['employee_count'] = 0
                status['today_birthdays'] = 0
                status['today_anniversaries'] = 0
        
        return jsonify(status)
    
    return app

# =============================================================================
# run_scheduler.py
# =============================================================================
import schedule
import time
import logging
from app.main import EmailAutomationSystem, setup_logging

def job():
    """Scheduled job to run daily email check"""
    system = EmailAutomationSystem()
    results = system.run_daily_check()
    
    logger = logging.getLogger(__name__)
    logger.info(f"Scheduled job completed: {results}")

def main():
    """Run the scheduler"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting email automation scheduler")
    
    # Schedule the job to run daily at 9:00 AM
    schedule.every().day.at("09:00").do(job)
    
    # For testing, you can also schedule it to run every minute
    # schedule.every().minute.do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()

# =============================================================================
# templates/index.html
# =============================================================================
"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Automation Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="#">📧 Email Automation System</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="{{ url_for('index') }}">Dashboard</a>
                <a class="nav-link" href="{{ url_for('upload_files') }}">Upload Files</a>
                <a class="nav-link" href="{{ url_for('view_logs') }}">Logs</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-md-12">
                <h1 class="mb-4">Email Automation Dashboard</h1>
                
                <!-- System Status Cards -->
                <div class="row mb-4">
                    <div class="col-md-3">
                        <div class="card text-white bg-info">
                            <div class="card-body">
                                <h5 class="card-title">📋 CSV File</h5>
                                <p class="card-text" id="csv-status">Loading...</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-white bg-success">
                            <div class="card-body">
                                <h5 class="card-title">🎂 Birthday Card</h5>
                                <p class="card-text" id="birthday-card-status">Loading...</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-white bg-warning">
                            <div class="card-body">
                                <h5 class="card-title">🎊 Anniversary Card</h5>
                                <p class="card-text" id="anniversary-card-status">Loading...</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-white bg-secondary">
                            <div class="card-body">
                                <h5 class="card-title">📧 Email Config</h5>
                                <p class="card-text" id="email-config-status">Loading...</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Today's Events -->
                <div class="row mb-4">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h5>🎂 Today's Birthdays</h5>
                            </div>
                            <div class="card-body">
                                <h3 class="text-primary" id="today-birthdays">-</h3>
                                <p class="text-muted">Employees celebrating today</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h5>🎊 Today's Anniversaries</h5>
                            </div>
                            <div class="card-body">
                                <h3 class="text-warning" id="today-anniversaries">-</h3>
                                <p class="text-muted">Work anniversaries today</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Control Panel -->
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>🎛️ Control Panel</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4">
                                <button class="btn btn-primary btn-lg w-100 mb-2" onclick="testEmail()">
                                    📧 Test Email Connection
                                </button>
                            </div>
                            <div class="col-md-4">
                                <button class="btn btn-success btn-lg w-100 mb-2" onclick="runDailyCheck()">
                                    🚀 Run Daily Check
                                </button>
                            </div>
                            <div class="col-md-4">
                                <button class="btn btn-info btn-lg w-100 mb-2" onclick="refreshStatus()">
                                    🔄 Refresh Status
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Results Panel -->
                <div class="card">
                    <div class="card-header">
                        <h5>📊 Last Run Results</h5>
                    </div>
                    <div class="card-body">
                        <div id="results-panel">
                            <p class="text-muted">No recent activity</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Loading Modal -->
    <div class="modal fade" id="loadingModal" tabindex="-1">
        <div class="modal-dialog modal-sm">
            <div class="modal-content">
                <div class="modal-body text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Processing...</p>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
"""

# =============================================================================
# templates/upload.html
# =============================================================================
"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload Files - Email Automation</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="#">📧 Email Automation System</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="{{ url_for('index') }}">Dashboard</a>
                <a class="nav-link active" href="{{ url_for('upload_files') }}">Upload Files</a>
                <a class="nav-link" href="{{ url_for('view_logs') }}">Logs</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <h1 class="mb-4">📁 Upload Files</h1>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <form method="POST" enctype="multipart/form-data">
            <div class="row">
                <!-- CSV File Upload -->
                <div class="col-md-12 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <h5>📋 Employee Data CSV</h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label for="csv_file" class="form-label">Choose CSV File</label>
                                <input type="file" class="form-control" id="csv_file" name="csv_file" accept=".csv">
                                <div class="form-text">
                                    CSV should contain columns: first_name, last_name, email, birthday, anniversary
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Birthday Card Upload -->
                <div class="col-md-6 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <h5>🎂 Birthday Card Image</h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label for="birthday_card" class="form-label">Choose Birthday Card</label>
                                <input type="file" class="form-control" id="birthday_card" name="birthday_card" accept="image/*">
                                <div class="form-text">
                                    Supported formats: JPG, PNG, GIF
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Anniversary Card Upload -->
                <div class="col-md-6 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <h5>🎊 Anniversary Card Image</h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label for="anniversary_card" class="form-label">Choose Anniversary Card</label>
                                <input type="file" class="form-control" id="anniversary_card" name="anniversary_card" accept="image/*">
                                <div class="form-text">
                                    Supported formats: JPG, PNG, GIF
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="text-center">
                <button type="submit" class="btn btn-primary btn-lg">📤 Upload Files</button>
                <a href="{{ url_for('index') }}" class="btn btn-secondary btn-lg ms-2">🔙 Back to Dashboard</a>
            </div>
        </form>

        <!-- CSV Format Guide -->
        <div class="card mt-4">
            <div class="card-header">
                <h5>📖 CSV Format Guide</h5>
            </div>
            <div class="card-body">
                <h6>Required Columns:</h6>
                <ul>
                    <li><strong>first_name:</strong> Employee's first name</li>
                    <li><strong>last_name:</strong> Employee's last name</li>
                    <li><strong>email:</strong> Employee's email address</li>
                    <li><strong>birthday:</strong> Date in YYYY-MM-DD format</li>
                    <li><strong>anniversary:</strong> Work start date in YYYY-MM-DD format</li>
                </ul>
                
                <h6>Example CSV Content:</h6>
                <pre class="bg-light p-3">first_name,last_name,email,birthday,anniversary
John,Doe,john.doe@company.com,1990-06-09,2020-03-15
Jane,Smith,jane.smith@company.com,1985-12-25,2019-06-09
Bob,Johnson,bob.johnson@company.com,1992-06-09,2021-01-10</pre>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# =============================================================================
# templates/logs.html
# =============================================================================
"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Logs - Email Automation</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="#">📧 Email Automation System</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="{{ url_for('index') }}">Dashboard</a>
                <a class="nav-link" href="{{ url_for('upload_files') }}">Upload Files</a>
                <a class="nav-link active" href="{{ url_for('view_logs') }}">Logs</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h1>📋 System Logs</h1>
            <button class="btn btn-primary" onclick="location.reload()">🔄 Refresh</button>
        </div>

        <div class="card">
            <div class="card-header">
                <h5>Recent Activity (Last 100 entries)</h5>
            </div>
            <div class="card-body">
                <div class="log-container" style="height: 500px; overflow-y: auto; font-family: monospace; font-size: 12px;">
                    {% for log in logs %}
                        <div class="log-entry mb-1 p-1 
                            {% if 'ERROR' in log %}bg-danger text-white
                            {% elif 'WARNING' in log %}bg-warning text-dark
                            {% elif 'INFO' in log %}bg-light
                            {% else %}bg-secondary text-white{% endif %}">
                            {{ log.strip() }}
                        </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# =============================================================================
# static/css/style.css
# =============================================================================
"""
.card {
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    border: 1px solid rgba(0, 0, 0, 0.125);
    transition: all 0.3s ease;
}

.card:hover {
    box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
}

.log-container {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 0.375rem;
}

.log-entry {
    border-radius: 0.25rem;
    word-wrap: break-word;
}

.navbar-brand {
    font-weight: bold;
}

.btn {
    transition: all 0.2s ease;
}

.btn:hover {
    transform: translateY(-1px);
}

.alert {
    border: none;
    border-radius: 0.5rem;
}

.spinner-border {
    width: 3rem;
    height: 3rem;
}

@media (max-width: 768px) {
    .btn-lg {
        font-size: 0.9rem;
        padding: 0.5rem 1rem;
    }
    
    .card-body h3 {
        font-size: 1.5rem;
    }
}
"""

# =============================================================================
# static/js/main.js
# =============================================================================
"""
// Global variables
let loadingModal;

document.addEventListener('DOMContentLoaded', function() {
    loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    refreshStatus();
});

function refreshStatus() {
    fetch('/status')
        .then(response => response.json())
        .then(data => {
            updateStatusCards(data);
        })
        .catch(error => {
            console.error('Error fetching status:', error);
            showAlert('Error fetching system status', 'danger');
        });
}

function updateStatusCards(status) {
    // CSV Status
    const csvStatus = document.getElementById('csv-status');
    if (status.csv_file_exists) {
        csvStatus.innerHTML = `✅ Loaded<br><small>${status.employee_count || 0} employees</small>`;
        csvStatus.parentElement.parentElement.className = 'card text-white bg-success';
    } else {
        csvStatus.innerHTML = '❌ Not found';
        csvStatus.parentElement.parentElement.className = 'card text-white bg-danger';
    }

    // Birthday Card Status
    const birthdayStatus = document.getElementById('birthday-card-status');
    if (status.birthday_card_exists) {
        birthdayStatus.innerHTML = '✅ Ready';
        birthdayStatus.parentElement.parentElement.className = 'card text-white bg-success';
    } else {
        birthdayStatus.innerHTML = '❌ Missing';
        birthdayStatus.parentElement.parentElement.className = 'card text-white bg-danger';
    }

    // Anniversary Card Status
    const anniversaryStatus = document.getElementById('anniversary-card-status');
    if (status.anniversary_card_exists) {
        anniversaryStatus.innerHTML = '✅ Ready';
        anniversaryStatus.parentElement.parentElement.className = 'card text-white bg-success';
    } else {
        anniversaryStatus.innerHTML = '❌ Missing';
        anniversaryStatus.parentElement.parentElement.className = 'card text-white bg-danger';
    }

    // Email Config Status
    const emailStatus = document.getElementById('email-config-status');
    if (status.email_configured) {
        emailStatus.innerHTML = '✅ Configured';
        emailStatus.parentElement.parentElement.className = 'card text-white bg-success';
    } else {
        emailStatus.innerHTML = '❌ Not configured';
        emailStatus.parentElement.parentElement.className = 'card text-white bg-danger';
    }

    // Today's events
    document.getElementById('today-birthdays').textContent = status.today_birthdays || 0;
    document.getElementById('today-anniversaries').textContent = status.today_anniversaries || 0;
}

function testEmail() {
    loadingModal.show();
    
    fetch('/test-email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        loadingModal.hide();
        if (data.success) {
            showAlert('Email connection test successful!', 'success');
        } else {
            showAlert(`Email test failed: ${data.message}`, 'danger');
        }
    })
    .catch(error => {
        loadingModal.hide();
        console.error('Error testing email:', error);
        showAlert('Error testing email connection', 'danger');
    });
}

function runDailyCheck() {
    loadingModal.show();
    
    fetch('/run-check', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        loadingModal.hide();
        displayResults(data);
        refreshStatus(); // Refresh status after run
    })
    .catch(error => {
        loadingModal.hide();
        console.error('Error running daily check:', error);
        showAlert('Error running daily check', 'danger');
    });
}

function displayResults(results) {
    const resultsPanel = document.getElementById('results-panel');
    
    if (results.error) {
        resultsPanel.innerHTML = `
            <div class="alert alert-danger">
                <h6>❌ Error</h6>
                <p>${results.error}</p>
            </div>
        `;
        return;
    }

    let html = `
        <div class="row">
            <div class="col-md-4">
                <div class="card bg-light">
                    <div class="card-body text-center">
                        <h5>📅 Date</h5>
                        <p>${results.date}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card bg-primary text-white">
                    <div class="card-body text-center">
                        <h5>🎂 Birthday Emails</h5>
                        <h3>${results.birthdays_sent}</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card bg-warning text-white">
                    <div class="card-body text-center">
                        <h5>🎊 Anniversary Emails</h5>
                        <h3>${results.anniversaries_sent}</h3>
                    </div>
                </div>
            </div>
        </div>
    `;

    if (results.errors && results.errors.length > 0) {
        html += `
            <div class="alert alert-warning mt-3">
                <h6>⚠️ Errors/Warnings:</h6>
                <ul class="mb-0">
        `;
        results.errors.forEach(error => {
            html += `<li>${error}</li>`;
        });
        html += `
                </ul>
            </div>
        `;
    }

    if (results.birthdays_sent === 0 && results.anniversaries_sent === 0 && results.errors.length === 0) {
        html += `
            <div class="alert alert-info mt-3">
                <h6>ℹ️ No emails sent today</h6>
                <p>No birthdays or anniversaries found for today.</p>
            </div>
        `;
    }

    resultsPanel.innerHTML = html;
}

function showAlert(message, type) {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Insert at top of container
    const container = document.querySelector('.container');
    const firstChild = container.firstElementChild;
    const alertDiv = document.createElement('div');
    alertDiv.innerHTML = alertHtml;
    container.insertBefore(alertDiv.firstElementChild, firstChild.nextSibling);
}
"""

# =============================================================================
# README.md
# =============================================================================
"""
# 📧 Email Automation System

A comprehensive Python application for automating birthday and anniversary emails with personalized greeting cards.

## ✨ Features

- 🎂 **Automated Birthday Emails**: Sends personalized birthday wishes
- 🎊 **Anniversary Recognition**: Celebrates work anniversaries automatically  
- 🖼️ **Custom Greeting Cards**: Adds "Dear [Name]" to uploaded card images
- 🌐 **Web Interface**: Easy-to-use dashboard for management
- 📊 **Dashboard**: Real-time status monitoring
- 📋 **CSV Integration**: Bulk employee data management
- 🕰️ **Scheduled Execution**: Daily automated checks
- 📝 **Comprehensive Logging**: Detailed activity tracking
- 🔧 **Configuration Management**: Environment-based settings

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Gmail account with App Password (or other email provider)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd email_automation_project
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Create directory structure**
   ```bash
   mkdir -p data images logs uploads
   ```

5. **Prepare your data**
   - Add employee CSV to `data/employees.csv`
   - Add birthday card image to `images/birthday_card.jpg`
   - Add anniversary card image to `images/anniversary_card.jpg`

### Running the Application

#### Web Interface
```bash
python -m flask --app app.web_interface run --host=0.0.0.0 --port=5000
```

#### Command Line
```bash
python app/main.py
```

#### Scheduler (Daily automation)
```bash
python run_scheduler.py
```

## 📁 Project Structure

```
email_automation_project/
├── app/                    # Main application code
│   ├── main.py            # Core automation logic
│   ├── email_sender.py    # Email handling
│   ├── image_processor.py # Image manipulation
│   ├── data_manager.py    # CSV data management
│   └── web_interface.py   # Flask web app
├── config/                # Configuration files
│   ├── settings.py        # Application settings
│   └── email_templates.py # Email templates
├── data/                  # Employee data
├── images/                # Greeting card images
├── logs/                  # Application logs
├── templates/             # HTML templates
├── static/                # CSS/JS assets
└── tests/                 # Unit tests
```

## 📋 CSV Format

Your employee CSV file should contain these columns:

```csv
first_name,last_name,email,birthday,anniversary
John,Doe,john.doe@company.com,1990-06-09,2020-03-15
Jane,Smith,jane.smith@company.com,1985-12-25,2019-06-09
```

## ⚙️ Configuration

Key environment variables in `.env`:

```env
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# File Paths
CSV_FILE_PATH=data/employees.csv
BIRTHDAY_CARD_PATH=images/birthday_card.jpg
ANNIVERSARY_CARD_PATH=images/anniversary_card.jpg

# Customization
BIRTHDAY_TEXT_X=100
BIRTHDAY_TEXT_Y=80
FONT_SIZE=40
```

## 🔐 Email Setup

### Gmail Setup
1. Enable 2-Factor Authentication
2. Generate App Password:
   - Google Account → Security → App passwords
   - Select "Mail" and "Other"
   - Use generated password in `.env`

### Other Providers
- **Outlook**: smtp-mail.outlook.com:587
- **Yahoo**: smtp.mail.yahoo.com:587
- **Custom**: Configure SMTP_SERVER and SMTP_PORT

## 🕰️ Scheduling

### Linux/macOS (Cron)
```bash
# Run daily at 9 AM
0 9 * * * /path/to/python /path/to/project/run_scheduler.py
```

### Windows (Task Scheduler)
1. Open Task Scheduler
2. Create Basic Task
3. Set daily trigger at 9:00 AM
4. Action: Start program `python run_scheduler.py`

### Docker
```bash
docker-compose up -d
```

## 🔧 Customization

### Email Templates
Edit `config/email_templates.py` to modify email content.

### Text Positioning
Adjust `BIRTHDAY_TEXT_X`, `BIRTHDAY_TEXT_Y` in `.env` based on your card design.

### Styling
Modify `static/css/style.css` for web interface appearance.

## 🧪 Testing

```bash
# Run tests
python -m pytest tests/

# Test email connection
python -c "from app.email_sender import EmailSender; print(EmailSender().test_email_connection())"

# Validate CSV
python -c "from app.data_manager import DataManager; print(DataManager().validate_csv_format('data/employees.csv'))"
```

## 📊 Monitoring

- **Web Dashboard**: http://localhost:5000
- **Logs**: Check `logs/email_automation.log`
- **Status API**: http://localhost:5000/status

## 🐳 Docker Deployment

```yaml
# docker-compose.yml included
version: '3.8'
services:
  email-automation:
    build: .
    environment:
      - SENDER_EMAIL=${SENDER_EMAIL}
      - EMAIL_PASSWORD=${EMAIL_PASSWORD}
    volumes:
      - ./data:/app/data
      - ./images:/app/images
      - ./logs:/app/logs
```

## 🔒 Security

- Never commit `.env` file
- Use App Passwords, not regular passwords
- Store sensitive data in environment variables
- Regular security updates

## 🐛 Troubleshooting

### Common Issues

1. **Email sending fails**
   - Check credentials in `.env`
   - Verify App Password setup
   - Test with `/test-email` endpoint

2. **Images not processing**
   - Ensure PIL/Pillow is installed
   - Check image file permissions
   - Verify image format (JPG/PNG)

3. **CSV validation errors**
   - Check column names match exactly
   - Verify date format (YYYY-MM-DD)
   - Remove special characters

### Debug Mode
Set `DEBUG=True` in `.env` for detailed error messages.

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📧 Support

For issues and questions:
- Create GitHub issue
- Check logs in `logs/` directory
- Review configuration in `.env`
"""

# =============================================================================
# .gitignore
# =============================================================================
"""
# Environment
.env
.venv/
env/
venv/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Data files
data/*.csv
!data/sample_employees.csv

# Images
images/*.jpg
images/*.png
images/*.gif

# Logs
logs/*.log

# Uploads
uploads/*
!uploads/.gitkeep

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Flask
instance/
.webassets-cache

# Testing
.pytest_cache/
.coverage
htmlcov/

# Docker
.dockerignore
"""

# =============================================================================
# setup.py
# =============================================================================
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="email-automation-system",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Automated birthday and anniversary email system with personalized greeting cards",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/email-automation-system",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Email",
        "Topic :: Office/Business :: Human Resources",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "email-automation=app.main:main",
            "email-scheduler=run_scheduler:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["templates/*.html", "static/css/*.css", "static/js/*.js"],
    },
)

# =============================================================================
# docker-compose.yml
# =============================================================================
"""
version: '3.8'

services:
  email-automation:
    build: .
    container_name: email_automation_system
    restart: unless-stopped
    environment:
      - SMTP_SERVER=${SMTP_SERVER:-smtp.gmail.com}
      - SMTP_PORT=${SMTP_PORT:-587}
      - SENDER_EMAIL=${SENDER_EMAIL}
      - EMAIL_PASSWORD=${EMAIL_PASSWORD}
      - SENDER_NAME=${SENDER_NAME:-HR Team}
      - DEBUG=${DEBUG:-False}
      - SECRET_KEY=${SECRET_KEY:-production-secret-key}
    volumes:
      - ./data:/app/data
      - ./images:/app/images
      - ./logs:/app/logs
      - ./uploads:/app/uploads
    ports:
      - "5000:5000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/status"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - email-automation-network

  scheduler:
    build: .
    container_name: email_automation_scheduler
    restart: unless-stopped
    environment:
      - SMTP_SERVER=${SMTP_SERVER:-smtp.gmail.com}
      - SMTP_PORT=${SMTP_PORT:-587}
      - SENDER_EMAIL=${SENDER_EMAIL}
      - EMAIL_PASSWORD=${EMAIL_PASSWORD}
      - SENDER_NAME=${SENDER_NAME:-HR Team}
    volumes:
      - ./data:/app/data
      - ./images:/app/images
      - ./logs:/app/logs
    command: python run_scheduler.py
    networks:
      - email-automation-network

networks:
  email-automation-network:
    driver: bridge

volumes:
  app_data:
  app_images:
  app_logs:
"""

# =============================================================================
# Dockerfile
# =============================================================================
"""
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data images logs uploads

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=app.web_interface

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/status || exit 1

# Default command (can be overridden)
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
"""

# =============================================================================
# data/sample_employees.csv
# =============================================================================
"""
first_name,last_name,email,birthday,anniversary
John,Doe,john.doe@company.com,1990-06-09,2020-03-15
Jane,Smith,jane.smith@company.com,1985-12-25,2019-06-09
Bob,Johnson,bob.johnson@company.com,1992-06-09,2021-01-10
Alice,Williams,alice.williams@company.com,1988-03-22,2018-07-01
Michael,Brown,michael.brown@company.com,1993-11-15,2022-02-14
Sarah,Davis,sarah.davis@company.com,1991-08-08,2020-09-30
David,Miller,david.miller@company.com,1987-05-17,2019-11-11
Lisa,Wilson,lisa.wilson@company.com,1994-02-29,2021-04-05
"""

# =============================================================================
# tests/test_email_sender.py
# =============================================================================
import unittest
from unittest.mock import Mock, patch
from app.email_sender import EmailSender
from config.settings import Config

class TestEmailSender(unittest.TestCase):
    def setUp(self):
        self.email_sender = EmailSender()
    
    def test_create_email_message(self):
        """Test email message creation"""
        msg = self.email_sender.create_email_message(
            "test@example.com",
            "Test Subject",
            "<p>Test Body</p>",
            b"fake_image_data"
        )
        
        self.assertEqual(msg['To'], "test@example.com")
        self.assertEqual(msg['Subject'], "Test Subject")
        self.assertIn(Config.SENDER_NAME, msg['From'])
    
    @patch('smtplib.SMTP')
    def test_email_connection_success(self, mock_smtp):
        """Test successful email connection"""
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = self.email_sender.test_email_connection()
        
        self.assertTrue(result['success'])
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_email_connection_failure(self, mock_smtp):
        """Test failed email connection"""
        mock_smtp.side_effect = Exception("Connection failed")
        
        result = self.email_sender.test_email_connection()
        
        self.assertFalse(result['success'])
        self.assertIn("Connection failed", result['message'])

if __name__ == '__main__':
    unittest.main()

# =============================================================================
# tests/test_data_manager.py
# =============================================================================
import unittest
import pandas as pd
import tempfile
import os
from datetime import date
from app.data_manager import DataManager

class TestDataManager(unittest.TestCase):
    def setUp(self):
        self.data_manager = DataManager()
        
        # Create test CSV data
        self.test_data = """first_name,last_name,email,birthday,anniversary
John,Doe,john@test.com,1990-06-09,2020-01-15
Jane,Smith,jane@test.com,1985-12-25,2019-06-09"""
        
        # Create temporary CSV file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.temp_file.write(self.test_data)
        self.temp_file.close()
        
        self.data_manager.csv_path = self.temp_file.name
    
    def tearDown(self):
        os.unlink(self.temp_file.name)
    
    def test_load_employee_data(self):
        """Test loading employee data from CSV"""
        df = self.data_manager.load_employee_data()
        
        self.assertEqual(len(df), 2)
        self.assertIn('first_name', df.columns)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df['birthday']))
    
    def test_get_today_birthdays(self):
        """Test getting today's birthdays"""
        df = self.data_manager.load_employee_data()
        
        # Mock today's date to match test data
        with unittest.mock.patch('datetime.date.today') as mock_date:
            mock_date.return_value = date(2024, 6, 9)
            birthdays = self.data_manager.get_today_birthdays(df)
            
            self.assertEqual(len(birthdays), 1)
            self.assertEqual(birthdays.iloc[0]['first_name'], 'John')
    
    def test_validate_csv_format(self):
        """Test CSV format validation"""
        result = self.data_manager.validate_csv_format(self.temp_file.name)
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['row_count'], 2)
        self.assertEqual(len(result['missing_columns']), 0)

if __name__ == '__main__':
    unittest.main()

# =============================================================================
# Makefile
# =============================================================================
"""
.PHONY: install run test clean docker-build docker-run

# Install dependencies
install:
	pip install -r requirements.txt

# Run the web application
run:
	python -m flask --app app.web_interface run --host=0.0.0.0 --port=5000

# Run the scheduler
scheduler:
	python run_scheduler.py

# Run the command line version
cli:
	python app/main.py

# Run tests
test:
	python -m pytest tests/ -v

# Run tests with coverage
test-coverage:
	python -m pytest tests/ --cov=app --cov-report=html

# Clean cache files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/

# Docker commands
docker-build:
	docker build -t email-automation .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Development setup
dev-setup:
	cp .env.example .env
	mkdir -p data images logs uploads
	cp data/sample_employees.csv data/employees.csv

# Lint code
lint:
	flake8 app/ tests/
	black --check app/ tests/

# Format code
format:
	black app/ tests/

# Security check
security:
	bandit -r app/

# Create distribution package
package:
	python setup.py sdist bdist_wheel

# Install in development mode
install-dev:
	pip install -e .

# Run all checks
check: lint test security

# Help
help:
	@echo "Available commands:"
	@echo "  install      - Install dependencies"
	@echo "  run          - Run web application"
	@echo "  scheduler    - Run scheduler"
	@echo "  cli          - Run command line version"
	@echo "  test         - Run tests"
	@echo "  clean        - Clean cache files"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run with Docker Compose"
	@echo "  dev-setup    - Setup development environment"
	@echo "  lint         - Check code style"
	@echo "  format       - Format code"
	@echo "  help         - Show this help"
"""