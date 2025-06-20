import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
import datetime
import os
import logging
import traceback
from typing import Optional, List, Dict
from dotenv import load_dotenv

# Import the card generator
from card_generation import BirthdayAnniversaryGenerator

class SMTPEmailAutomation:
    def __init__(self, smtp_server: Optional[str] = None, smtp_port: Optional[int] = None, 
                 email: Optional[str] = None, password: Optional[str] = None, 
                 output_folder: str = "output"):
        """
        Initialize SMTP email automation system with card generation
        
        Args:
            smtp_server: SMTP server (e.g., 'smtp.gmail.com') - will use env var if None
            smtp_port: SMTP port (e.g., 587 for TLS) - will use env var if None
            email: Sender email address - will use env var if None
            password: Email password or app password - will use env var if None
            output_folder: Folder to save generated images and logs
        """
        # Load environment variables
        load_dotenv()
        
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = email or os.getenv('SENDER_EMAIL')
        self.password = password or os.getenv('EMAIL_PASSWORD')
        self.output_folder = output_folder
        
        # Validate required configuration
        if not all([self.smtp_server, self.sender_email, self.password]):
            raise ValueError("Missing required email configuration. Please set environment variables or pass parameters.")
        
        # Type guard: Ensure we have valid string values after validation
        if not isinstance(self.smtp_server, str):
            raise ValueError("SMTP server must be a valid string")
        if not isinstance(self.sender_email, str):
            raise ValueError("Sender email must be a valid string")
        if not isinstance(self.password, str):
            raise ValueError("Email password must be a valid string")
        
        # Create output and logs folders if they don't exist
        os.makedirs(output_folder, exist_ok=True)
        self.logs_folder = os.path.join(output_folder, "logs")
        os.makedirs(self.logs_folder, exist_ok=True)
        
        # Initialize card generator
        self.card_generator = BirthdayAnniversaryGenerator(output_folder)
        
        # Setup logging
        self.setup_logging()
        
        # Track statistics for daily report
        self.stats = {
            'birthday_emails_sent': 0,
            'anniversary_emails_sent': 0,
            'birthday_emails_failed': 0,
            'anniversary_emails_failed': 0,
            'birthday_cards_generated': 0,
            'anniversary_cards_generated': 0,
            'errors': [],
            'birthdays_today': [],
            'anniversaries_today': [],
            'start_time': datetime.datetime.now(),
            'end_time': None
        }
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_filename = os.path.join(self.logs_folder, "email_log.log")
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Setup file handler
        file_handler = logging.FileHandler(log_filename, mode='a', encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        
        # Setup console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        
        # Setup logger
        self.logger = logging.getLogger('SMTPEmailAutomation')
        self.logger.setLevel(logging.INFO)
        
        # Clear existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.log_file_path = log_filename
        self.logger.info("SMTP Email Automation system initialized")
        self.logger.info(f"Output folder: {self.output_folder}")
        self.logger.info(f"Logs folder: {self.logs_folder}")
        self.logger.info(f"SMTP Server: {self.smtp_server}:{self.smtp_port}")
        self.logger.info(f"Sender Email: {self.sender_email}")
        
    def log_error(self, error_msg: str, exception: Optional[Exception] = None):
        """Log error and add to stats"""
        if exception:
            full_error = f"{error_msg}: {str(exception)}\n{traceback.format_exc()}"
        else:
            full_error = error_msg
            
        self.logger.error(full_error)
        self.stats['errors'].append({
            'timestamp': datetime.datetime.now().isoformat(),
            'message': error_msg,
            'exception': str(exception) if exception else None,
            'traceback': traceback.format_exc() if exception else None
        })
    
    def create_email_message(self, recipient_email: str, recipient_name: str, 
                           subject: str, body: str, image_bytes: Optional[bytes]) -> Optional[MIMEMultipart]:
        """
        Create email message with personalized greeting card
        """
        try:
            self.logger.info(f"Creating email message for {recipient_name} ({recipient_email})")
            
            # Type safety: Ensure sender_email is a string
            if not isinstance(self.sender_email, str):
                self.log_error("Invalid sender email configuration")
                return None
                
            msg = MIMEMultipart('related')
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Create HTML body that references the embedded image
            html_body = f"""
            <html>
                <body>
                    <img src="cid:greeting_card" style="max-width: 600px; height: auto;">
                </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Attach the personalized image
            if image_bytes:
                img = MIMEImage(image_bytes)
                img.add_header('Content-ID', '<greeting_card>')
                msg.attach(img)
                self.logger.info(f"Image attached to email for {recipient_name}")
            
            self.logger.info(f"Email message created successfully for {recipient_name}")
            return msg
            
        except Exception as e:
            self.log_error(f"Error creating email message for {recipient_email}", e)
            return None
    
    def send_email(self, msg: Optional[MIMEMultipart]) -> bool:
        """
        Send email using SMTP with error handling
        """
        if not msg:
            self.logger.error("Cannot send email: message is None")
            return False
            
        try:
            recipient = msg['To']
            self.logger.info(f"Attempting to send email to {recipient}")
            
            # Type safety: Ensure required attributes are strings
            if not isinstance(self.smtp_server, str) or not isinstance(self.sender_email, str) or not isinstance(self.password, str):
                self.log_error("Invalid email configuration - missing required string values")
                return False
                
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            self.logger.info(f"SMTP connection established, authenticating...")
            
            server.login(self.sender_email, self.password)
            self.logger.info(f"SMTP authentication successful")
            
            text = msg.as_string()
            server.sendmail(self.sender_email, recipient, text)
            server.quit()
            
            self.logger.info(f"Email sent successfully to {recipient}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            self.log_error(f"SMTP Authentication failed when sending to {msg['To']}", e)
        except smtplib.SMTPRecipientsRefused as e:
            self.log_error(f"Recipient refused when sending to {msg['To']}", e)
        except smtplib.SMTPServerDisconnected as e:
            self.log_error(f"SMTP server disconnected when sending to {msg['To']}", e)
        except Exception as e:
            self.log_error(f"Error sending email to {msg['To']}", e)
            
        return False
    
    def process_birthday_emails(self, birthdays: List[Dict], birthday_cards: List[str]):
        """
        Process and send birthday emails with generated cards
        
        Args:
            birthdays: List of birthday information dictionaries
            birthday_cards: List of paths to generated birthday cards
        """
        self.logger.info(f"Processing {len(birthdays)} birthday emails")
        
        for i, (birthday_info, card_path) in enumerate(zip(birthdays, birthday_cards)):
            try:
                first_name = birthday_info['first_name']
                last_name = birthday_info['last_name']
                email = birthday_info['email']
                age = birthday_info['age']
                
                self.logger.info(f"Processing birthday email {i+1}/{len(birthdays)} for {first_name} {last_name} (age {age})")
                
                # Read the generated card image
                try:
                    with open(card_path, 'rb') as f:
                        image_bytes = f.read()
                    self.logger.info(f"Loaded birthday card image: {card_path}")
                except Exception as e:
                    self.log_error(f"Failed to read birthday card image: {card_path}", e)
                    self.stats['birthday_emails_failed'] += 1
                    continue
                
                # Create email
                subject = f"Happy Birthday, {first_name}! 🎉"
                body = ""  # No body text needed as image contains the message
                
                msg = self.create_email_message(
                    email, first_name, subject, body, image_bytes
                )
                
                # Send email
                if msg and self.send_email(msg):
                    self.stats['birthday_emails_sent'] += 1
                    self.logger.info(f"Birthday email sent successfully to {first_name} {last_name}")
                    
                    # Add to stats
                    self.stats['birthdays_today'].append({
                        'name': f"{first_name} {last_name}",
                        'email': email,
                        'age': age
                    })
                else:
                    self.stats['birthday_emails_failed'] += 1
                    self.log_error(f"Failed to send birthday email to {first_name} {last_name}")
                        
            except Exception as e:
                self.stats['birthday_emails_failed'] += 1
                self.log_error(f"Error processing birthday email for {birthday_info.get('first_name', 'Unknown')}", e)
    
    def process_anniversary_emails(self, anniversaries: List[Dict], anniversary_cards: List[str]):
        """
        Process and send anniversary emails with generated cards
        
        Args:
            anniversaries: List of anniversary information dictionaries
            anniversary_cards: List of paths to generated anniversary cards
        """
        self.logger.info(f"Processing {len(anniversaries)} anniversary emails")
        
        for i, (anniversary_info, card_path) in enumerate(zip(anniversaries, anniversary_cards)):
            try:
                first_name = anniversary_info['first_name']
                last_name = anniversary_info['last_name']
                email = anniversary_info['email']
                years = anniversary_info['years']
                
                self.logger.info(f"Processing anniversary email {i+1}/{len(anniversaries)} for {first_name} {last_name} ({years} years)")
                
                # Read the generated card image
                try:
                    with open(card_path, 'rb') as f:
                        image_bytes = f.read()
                    self.logger.info(f"Loaded anniversary card image: {card_path}")
                except Exception as e:
                    self.log_error(f"Failed to read anniversary card image: {card_path}", e)
                    self.stats['anniversary_emails_failed'] += 1
                    continue
                
                # Create email
                subject = f"Happy Anniversary, {first_name}! 💕"
                body = ""  # No body text needed as image contains the message
                
                msg = self.create_email_message(
                    email, first_name, subject, body, image_bytes
                )
                
                # Send email
                if msg and self.send_email(msg):
                    self.stats['anniversary_emails_sent'] += 1
                    self.logger.info(f"Anniversary email sent successfully to {first_name} {last_name} ({years} years)")
                    
                    # Add to stats
                    self.stats['anniversaries_today'].append({
                        'name': f"{first_name} {last_name}",
                        'email': email,
                        'years': years
                    })
                else:
                    self.stats['anniversary_emails_failed'] += 1
                    self.log_error(f"Failed to send anniversary email to {first_name} {last_name}")
                        
            except Exception as e:
                self.stats['anniversary_emails_failed'] += 1
                self.log_error(f"Error processing anniversary email for {anniversary_info.get('first_name', 'Unknown')}", e)
    
    def create_summary_report(self) -> str:
        """Create a summary report of the day's activities"""
        self.stats['end_time'] = datetime.datetime.now()
        duration = self.stats['end_time'] - self.stats['start_time']
        
        report = f"""
Daily SMTP Email Automation Report - {datetime.date.today().strftime('%B %d, %Y')}
================================================================

EXECUTION SUMMARY:
- Start Time: {self.stats['start_time'].strftime('%H:%M:%S')}
- End Time: {self.stats['end_time'].strftime('%H:%M:%S')}
- Duration: {duration}

BIRTHDAY PROCESSING:
- Cards Generated: {self.stats['birthday_cards_generated']}
- Emails Sent Successfully: {self.stats['birthday_emails_sent']}
- Emails Failed: {self.stats['birthday_emails_failed']}
- Birthdays Today: {len(self.stats['birthdays_today'])}

ANNIVERSARY PROCESSING:
- Cards Generated: {self.stats['anniversary_cards_generated']}
- Emails Sent Successfully: {self.stats['anniversary_emails_sent']}
- Emails Failed: {self.stats['anniversary_emails_failed']}
- Anniversaries Today: {len(self.stats['anniversaries_today'])}

TOTAL SUMMARY:
- Total Cards Generated: {self.stats['birthday_cards_generated'] + self.stats['anniversary_cards_generated']}
- Total Emails Sent: {self.stats['birthday_emails_sent'] + self.stats['anniversary_emails_sent']}
- Total Errors: {len(self.stats['errors'])}

        """
        
        if self.stats['birthdays_today']:
            report += "\nBIRTHDAYS TODAY:\n"
            for birthday in self.stats['birthdays_today']:
                report += f"- {birthday['name']} ({birthday['email']}) - Age: {birthday['age']}\n"
        
        if self.stats['anniversaries_today']:
            report += "\nANNIVERSARIES TODAY:\n"
            for anniversary in self.stats['anniversaries_today']:
                report += f"- {anniversary['name']} ({anniversary['email']}) - {anniversary['years']} years\n"
        
        if self.stats['errors']:
            report += f"\nERRORS ENCOUNTERED ({len(self.stats['errors'])}):\n"
            for i, error in enumerate(self.stats['errors'], 1):
                report += f"{i}. {error['timestamp']} - {error['message']}\n"
                if error['exception']:
                    report += f"   Exception: {error['exception']}\n"
        
        self.logger.info("Summary report generated")
        return report
    
    def send_daily_report(self):
        """Send daily report to self"""
        try:
            self.logger.info("Generating and sending daily report")
            
            # Type safety: Ensure sender_email is a string
            if not isinstance(self.sender_email, str):
                self.log_error("Invalid sender email configuration for daily report")
                return
                
            report = self.create_summary_report()
            
            # Save report to file
            report_filename = os.path.join(self.output_folder, f"daily_report_{datetime.date.today().strftime('%Y%m%d')}.txt")
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(report)
            self.logger.info(f"Daily report saved to: {report_filename}")
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.sender_email
            msg['Subject'] = f"SMTP Email Automation Daily Report - {datetime.date.today().strftime('%Y-%m-%d')}"
            
            # Add report as email body
            msg.attach(MIMEText(report, 'plain'))
            
            # Attach log file
            try:
                with open(self.log_file_path, 'rb') as f:
                    log_attachment = MIMEBase('application', 'octet-stream')
                    log_attachment.set_payload(f.read())
                    encoders.encode_base64(log_attachment)
                    log_attachment.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {os.path.basename(self.log_file_path)}'
                    )
                    msg.attach(log_attachment)
                self.logger.info("Log file attached to daily report")
            except Exception as e:
                self.logger.warning(f"Could not attach log file: {e}")
            
            # Attach report file
            try:
                with open(report_filename, 'rb') as f:
                    report_attachment = MIMEBase('application', 'octet-stream')
                    report_attachment.set_payload(f.read())
                    encoders.encode_base64(report_attachment)
                    report_attachment.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {os.path.basename(report_filename)}'
                    )
                    msg.attach(report_attachment)
                self.logger.info("Report file attached to daily report")
            except Exception as e:
                self.logger.warning(f"Could not attach report file: {e}")
            
            # Send the report
            if self.send_email(msg):
                self.logger.info("Daily report sent successfully")
            else:
                self.logger.error("Failed to send daily report")
                
        except Exception as e:
            self.log_error("Error creating/sending daily report", e)
    
    def run_daily_automation(self, csv_file: str, birthday_card_path: str, 
                           anniversary_card_path: str, 
                           birthday_text_pos: tuple = (50, 50),
                           anniversary_text_pos: tuple = (0, 300),
                           birthday_font_size: int = 40,
                           anniversary_font_size: int = 40,
                           birthday_font_color: str = "#000000",
                           anniversary_font_color: str = "#000000",
                           birthday_font_path: Optional[str] = None,
                           anniversary_font_path: Optional[str] = None,
                           birthday_center_align: bool = False,
                           anniversary_center_align: bool = True):
        """
        Run complete daily automation: generate cards and send emails
        
        Args:
            csv_file: Path to employee CSV file
            birthday_card_path: Path to birthday card template
            anniversary_card_path: Path to anniversary card template
            birthday_text_pos: (x, y) position for birthday text
            anniversary_text_pos: (x, y) position for anniversary text
            birthday_font_size: Font size for birthday cards
            anniversary_font_size: Font size for anniversary cards
            birthday_font_color: Hex color for birthday text
            anniversary_font_color: Hex color for anniversary text
            birthday_font_path: Path to custom font for birthday cards
            anniversary_font_path: Path to custom font for anniversary cards
            birthday_center_align: Center align birthday text
            anniversary_center_align: Center align anniversary text
        """
        try:
            self.logger.info(f"Starting daily SMTP email automation for {datetime.date.today()}")
            self.logger.info(f"CSV file: {csv_file}")
            self.logger.info(f"Birthday card template: {birthday_card_path}")
            self.logger.info(f"Anniversary card template: {anniversary_card_path}")
            
            # Step 1: Generate cards using card_generation.py
            self.logger.info("Step 1: Generating birthday and anniversary cards")
            result = self.card_generator.process_daily_cards(
                csv_file=csv_file,
                birthday_card_path=birthday_card_path,
                anniversary_card_path=anniversary_card_path,
                birthday_text_pos=birthday_text_pos,
                anniversary_text_pos=anniversary_text_pos,
                birthday_font_size=birthday_font_size,
                anniversary_font_size=anniversary_font_size,
                birthday_font_color=birthday_font_color,
                anniversary_font_color=anniversary_font_color,
                birthday_font_path=birthday_font_path,
                anniversary_font_path=anniversary_font_path,
                birthday_center_align=birthday_center_align,
                anniversary_center_align=anniversary_center_align
            )
            
            if not result['success']:
                self.log_error(f"Card generation failed: {result.get('error', 'Unknown error')}")
                return False
            
            self.stats['birthday_cards_generated'] = len(result['birthday_cards_created'])
            self.stats['anniversary_cards_generated'] = len(result['anniversary_cards_created'])
            
            self.logger.info(f"Cards generated successfully - Birthday: {self.stats['birthday_cards_generated']}, Anniversary: {self.stats['anniversary_cards_generated']}")
            
            # Step 2: Send birthday emails
            if result['birthday_cards_created']:
                self.logger.info("Step 2: Sending birthday emails")
                self.process_birthday_emails(
                    result['birthdays_today'], 
                    result['birthday_cards_created']
                )
            else:
                self.logger.info("No birthday emails to send today")
            
            # Step 3: Send anniversary emails
            if result['anniversary_cards_created']:
                self.logger.info("Step 3: Sending anniversary emails")
                self.process_anniversary_emails(
                    result['anniversaries_today'], 
                    result['anniversary_cards_created']
                )
            else:
                self.logger.info("No anniversary emails to send today")
            
            # Step 4: Send daily report
            self.logger.info("Step 4: Sending daily report")
            self.send_daily_report()
            
            # Final statistics
            self.stats['end_time'] = datetime.datetime.now()
            duration = self.stats['end_time'] - self.stats['start_time']
            
            self.logger.info("=== SMTP EMAIL AUTOMATION COMPLETE ===")
            self.logger.info(f"Duration: {duration}")
            self.logger.info(f"Total cards generated: {self.stats['birthday_cards_generated'] + self.stats['anniversary_cards_generated']}")
            self.logger.info(f"Birthday emails sent: {self.stats['birthday_emails_sent']}")
            self.logger.info(f"Anniversary emails sent: {self.stats['anniversary_emails_sent']}")
            self.logger.info(f"Total emails sent: {self.stats['birthday_emails_sent'] + self.stats['anniversary_emails_sent']}")
            self.logger.info(f"Failed emails: {self.stats['birthday_emails_failed'] + self.stats['anniversary_emails_failed']}")
            
            return True
            
        except Exception as e:
            self.log_error("Critical error in daily automation", e)
            # Still try to send a report even if there was a critical error
            try:
                self.send_daily_report()
            except:
                pass
            return False


def main():
    """
    Main function to run the SMTP email automation
    """
    try:
        print("🚀 Starting SMTP Email Automation with Card Generation")
        print("=" * 60)
        
        # Load environment variables from .env file
        load_dotenv()
        
        # Email configuration from environment variables
        SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
        SENDER_EMAIL = os.getenv('SENDER_EMAIL')
        EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
        
        # File and folder configuration from environment variables
        OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'output')
        CSV_FILE = os.getenv('CSV_FILE', 'employees_test_today.csv')
        BIRTHDAY_CARD = os.getenv('BIRTHDAY_CARD', 'assets\\Slide2.PNG')
        ANNIVERSARY_CARD = os.getenv('ANNIVERSARY_CARD', 'assets\\Slide1.PNG')
        
        # Text positioning for 1280x720 images from .env
        BIRTHDAY_TEXT_X = int(os.getenv('BIRTHDAY_TEXT_X', '50'))
        BIRTHDAY_TEXT_Y = int(os.getenv('BIRTHDAY_TEXT_Y', '300'))
        ANNIVERSARY_TEXT_X = int(os.getenv('ANNIVERSARY_TEXT_X', '0'))
        ANNIVERSARY_TEXT_Y = int(os.getenv('ANNIVERSARY_TEXT_Y', '200'))
        
        BIRTHDAY_TEXT_POSITION = (BIRTHDAY_TEXT_X, BIRTHDAY_TEXT_Y)
        ANNIVERSARY_TEXT_POSITION = (ANNIVERSARY_TEXT_X, ANNIVERSARY_TEXT_Y)
        
        # Font customization from .env
        BIRTHDAY_FONT_SIZE = int(os.getenv('BIRTHDAY_FONT_SIZE', '64'))
        ANNIVERSARY_FONT_SIZE = int(os.getenv('ANNIVERSARY_FONT_SIZE', '72'))
        BIRTHDAY_FONT_COLOR = os.getenv('BIRTHDAY_FONT_COLOR', '#4b446a')
        ANNIVERSARY_FONT_COLOR = os.getenv('ANNIVERSARY_FONT_COLOR', '#72719f')
        
        # Font paths from .env
        BIRTHDAY_FONT_PATH = os.getenv('BIRTHDAY_FONT_PATH', 'fonts/Inkfree.ttf')
        ANNIVERSARY_FONT_PATH = os.getenv('ANNIVERSARY_FONT_PATH', 'C:/Windows/Fonts/HTOWERT.TTF')
        
        # Alignment from .env
        BIRTHDAY_CENTER_ALIGN = os.getenv('BIRTHDAY_CENTER_ALIGN', 'false').lower() == 'true'
        ANNIVERSARY_CENTER_ALIGN = os.getenv('ANNIVERSARY_CENTER_ALIGN', 'true').lower() == 'true'
        
        # Validate required environment variables
        if not SENDER_EMAIL or not EMAIL_PASSWORD:
            print("❌ Error: SENDER_EMAIL and EMAIL_PASSWORD environment variables are required!")
            print("Please create a .env file with your email configuration.")
            return
        
        print("📋 Configuration Summary:")
        print(f"   📧 Sender Email: {SENDER_EMAIL}")
        print(f"   🏢 SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
        print(f"   📁 Output Folder: {OUTPUT_FOLDER}")
        print(f"   📊 CSV File: {CSV_FILE}")
        print(f"   🎂 Birthday Template: {BIRTHDAY_CARD}")
        print(f"   💕 Anniversary Template: {ANNIVERSARY_CARD}")
        print(f"   🎨 Birthday Font: {BIRTHDAY_FONT_PATH} (Size: {BIRTHDAY_FONT_SIZE}, Color: {BIRTHDAY_FONT_COLOR})")
        print(f"   🎨 Anniversary Font: {ANNIVERSARY_FONT_PATH} (Size: {ANNIVERSARY_FONT_SIZE}, Color: {ANNIVERSARY_FONT_COLOR})")
        print(f"   📍 Birthday Position: {BIRTHDAY_TEXT_POSITION} {'(Center Aligned)' if BIRTHDAY_CENTER_ALIGN else ''}")
        print(f"   📍 Anniversary Position: {ANNIVERSARY_TEXT_POSITION} {'(Center Aligned)' if ANNIVERSARY_CENTER_ALIGN else ''}")
        print()
        
        # Initialize SMTP email automation
        email_system = SMTPEmailAutomation(
            smtp_server=SMTP_SERVER,
            smtp_port=SMTP_PORT,
            email=SENDER_EMAIL,
            password=EMAIL_PASSWORD,
            output_folder=OUTPUT_FOLDER
        )
        
        # Run daily automation
        success = email_system.run_daily_automation(
            csv_file=CSV_FILE, 
            birthday_card_path=BIRTHDAY_CARD, 
            anniversary_card_path=ANNIVERSARY_CARD,
            birthday_text_pos=BIRTHDAY_TEXT_POSITION,
            anniversary_text_pos=ANNIVERSARY_TEXT_POSITION,
            birthday_font_size=BIRTHDAY_FONT_SIZE,
            anniversary_font_size=ANNIVERSARY_FONT_SIZE,
            birthday_font_color=BIRTHDAY_FONT_COLOR,
            anniversary_font_color=ANNIVERSARY_FONT_COLOR,
            birthday_font_path=BIRTHDAY_FONT_PATH,
            anniversary_font_path=ANNIVERSARY_FONT_PATH,
            birthday_center_align=BIRTHDAY_CENTER_ALIGN,
            anniversary_center_align=ANNIVERSARY_CENTER_ALIGN
        )
        
        if success:
            print("✅ SMTP Email automation completed successfully!")
        else:
            print("❌ SMTP Email automation completed with errors. Check logs for details.")
        
    except Exception as e:
        print(f"❌ Critical error in main execution: {e}")
        import traceback
        traceback.print_exc()


def create_env_template():
    """Create a template .env file for SMTP configuration"""
    env_template = """# SMTP Email Automation Configuration
# Copy this file to .env and update with your settings

# SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Email Credentials (REQUIRED)
SENDER_EMAIL=your.email@gmail.com
EMAIL_PASSWORD=your_app_password_here

# File Paths
OUTPUT_FOLDER=output
CSV_FILE=employees_test_today.csv
BIRTHDAY_CARD=assets\\Slide2.PNG
ANNIVERSARY_CARD=assets\\Slide1.PNG

# IMAGE SPECIFICATIONS
# ===================
# This configuration is optimized for 1280x720 greeting card images
# Birthday cards: Display "Happy Birthday {Name}" 
# Anniversary cards: Display "Happy Anniversary" with name on next line, center-aligned

# BIRTHDAY CARD CUSTOMIZATION (1280x720)
# =======================================
# Text Position (pixels from top-left corner)
BIRTHDAY_TEXT_X=50
BIRTHDAY_TEXT_Y=300

# Font Size (larger number = bigger text)
BIRTHDAY_FONT_SIZE=64

# Font Color (hex format)
# Popular choices for birthdays:
# Bright Gold: #FFD700
# Party Pink: #FF69B4  
# Vibrant Blue: #1E90FF
# Classic Black: #000000
# Purple: #4b446a
BIRTHDAY_FONT_COLOR=#4b446a

# Custom Font Path (optional)
# Examples:
# BIRTHDAY_FONT_PATH=fonts/Inkfree.ttf
# BIRTHDAY_FONT_PATH=C:/Windows/Fonts/HTOWERT.TTF
# BIRTHDAY_FONT_PATH=fonts/Arial-Bold.ttf
BIRTHDAY_FONT_PATH=fonts/Inkfree.ttf

# Text Alignment (center birthday text horizontally if desired)
BIRTHDAY_CENTER_ALIGN=false

# ANNIVERSARY CARD CUSTOMIZATION (1280x720)
# ==========================================
# Text Position - X is ignored due to center alignment, Y controls vertical position
ANNIVERSARY_TEXT_X=0
ANNIVERSARY_TEXT_Y=200

# Font Size (larger number = bigger text)
ANNIVERSARY_FONT_SIZE=72

# Font Color (hex format)
# Popular choices for anniversaries:
# Romantic Purple: #800080
# Deep Red: #8B0000
# Elegant Navy: #000080
# Classic Black: #000000
# Rose Gold: #E8B4B8
# Light Purple: #72719f
ANNIVERSARY_FONT_COLOR=#72719f

# Custom Font Path (optional) - Can be different from birthday font
# Examples:
# ANNIVERSARY_FONT_PATH=C:/Windows/Fonts/HTOWERT.TTF
# ANNIVERSARY_FONT_PATH=fonts/Times-New-Roman.ttf
# ANNIVERSARY_FONT_PATH=fonts/Brush-Script.ttf
ANNIVERSARY_FONT_PATH=C:/Windows/Fonts/HTOWERT.TTF

# Text Alignment (anniversary cards are center-aligned by default)
ANNIVERSARY_CENTER_ALIGN=true

# LAYOUT EXPLANATION:
# ==================
# Birthday Layout:    "Happy Birthday John"     (single line)
# Anniversary Layout: "Happy Anniversary"       (first line, centered)
#                     "      John      "        (second line, centered)

# SMTP EMAIL SETTINGS:
# ====================
# For Gmail, you need to:
# 1. Enable 2-factor authentication
# 2. Generate an App Password
# 3. Use the App Password as EMAIL_PASSWORD (not your regular password)
#
# For other email providers:
# - Outlook/Hotmail: smtp-mail.outlook.com, port 587
# - Yahoo: smtp.mail.yahoo.com, port 587
# - Custom/Corporate: Check with your IT department

# LOGGING:
# ========
# All logs will be saved to: {OUTPUT_FOLDER}/logs/email_log.log
# Daily reports will be saved to: {OUTPUT_FOLDER}/daily_report_YYYYMMDD.txt
# Generated cards will be saved to: {OUTPUT_FOLDER}/
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_template)
    
    print("📋 Created .env.template file for SMTP Email Automation")
    print("📝 Copy this to .env and update with your settings")
    print("\n🔧 SMTP SETUP GUIDE:")
    print("===================")
    print("1. For Gmail:")
    print("   - Enable 2-factor authentication")
    print("   - Generate an App Password")
    print("   - Use App Password as EMAIL_PASSWORD")
    print("   - SMTP_SERVER=smtp.gmail.com")
    print("   - SMTP_PORT=587")
    print("\n2. For Outlook/Hotmail:")
    print("   - SMTP_SERVER=smtp-mail.outlook.com")
    print("   - SMTP_PORT=587")
    print("\n3. For Yahoo:")
    print("   - SMTP_SERVER=smtp.mail.yahoo.com")
    print("   - SMTP_PORT=587")
    print("\n📁 LOGGING:")
    print("===========")
    print("- Email logs: output/logs/email_log.log")
    print("- Card generation logs: output/card_generator.log")
    print("- Daily reports: output/daily_report_YYYYMMDD.txt")


if __name__ == "__main__":
    # Uncomment the line below to create a .env template file
    # create_env_template()
    
    main()


# Example CSV structure (save as employees_test_today.csv)
"""
first_name,last_name,email,birthday,anniversary
John,Doe,john.doe@company.com,1990-06-20,2018-05-20
Jane,Smith,jane.smith@company.com,1985-12-25,2015-08-15
Bob,Johnson,bob.johnson@company.com,1992-06-20,2020-10-12
Alice,Brown,alice.brown@company.com,1988-03-14,
Sarah,Wilson,sarah.wilson@company.com,1991-06-20,2019-09-14
"""