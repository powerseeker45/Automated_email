import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
from PIL import Image, ImageDraw, ImageFont
import datetime
import os
import io
import logging
import traceback
from typing import Optional, List, Dict
import json

class EmailAutomation:
    def __init__(self, smtp_server: str, smtp_port: int, email: str, password: str, output_folder: str = "output"):
        """
        Initialize email automation system
        
        Args:
            smtp_server: SMTP server (e.g., 'smtp.gmail.com')
            smtp_port: SMTP port (e.g., 587 for TLS)
            email: Sender email address
            password: Email password or app password
            output_folder: Folder to save generated images and logs
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = email
        self.password = password
        self.output_folder = output_folder
        
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Track statistics for daily report
        self.stats = {
            'birthday_emails_sent': 0,
            'anniversary_emails_sent': 0,
            'birthday_emails_failed': 0,
            'anniversary_emails_failed': 0,
            'errors': [],
            'birthdays_today': [],
            'anniversaries_today': [],
            'start_time': datetime.datetime.now(),
            'end_time': None
        }
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_filename = os.path.join(self.output_folder, "email_automation.log")
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
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
        self.logger = logging.getLogger('EmailAutomation')
        self.logger.setLevel(logging.INFO)
        
        # Clear existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.log_file_path = log_filename
        
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
        
    def load_employee_data(self, csv_file: str) -> pd.DataFrame:
        """
        Load employee data from CSV file with error handling
        """
        try:
            if not os.path.exists(csv_file):
                raise FileNotFoundError(f"CSV file not found: {csv_file}")
                
            df = pd.read_csv(csv_file)
            self.logger.info(f"Loaded {len(df)} employee records from {csv_file}")
            
            # Validate required columns
            required_columns = ['first_name', 'last_name', 'email', 'birthday']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Convert date columns to datetime with error handling
            try:
                df['birthday'] = pd.to_datetime(df['birthday'], errors='coerce')
                invalid_birthdays = df[df['birthday'].isna()]['email'].tolist()
                if invalid_birthdays:
                    self.logger.warning(f"Invalid birthday dates for employees: {invalid_birthdays}")
            except Exception as e:
                self.log_error("Error parsing birthday dates", e)
                
            if 'marriage_anniversary' in df.columns:
                try:
                    df['marriage_anniversary'] = pd.to_datetime(df['marriage_anniversary'], errors='coerce')
                    invalid_anniversaries = df[df['marriage_anniversary'].isna() & df['marriage_anniversary'].notna()]['email'].tolist()
                    if invalid_anniversaries:
                        self.logger.warning(f"Invalid anniversary dates for employees: {invalid_anniversaries}")
                except Exception as e:
                    self.log_error("Error parsing anniversary dates", e)
            
            return df
            
        except Exception as e:
            self.log_error(f"Error loading CSV file: {csv_file}", e)
            return pd.DataFrame()
    
    def add_text_to_image(self, image_path: str, text: str, 
                         position: tuple = (50, 50), 
                         font_size: int = 40,
                         font_color: tuple = (0, 0, 0),
                         output_filename: Optional[str] = None) -> tuple:
        """
        Add personalized text to greeting card image and save to output folder
        
        Returns:
            tuple: (image_bytes, saved_file_path)
        """
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
                
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
                        try:
                            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)  # Linux
                        except:
                            font = ImageFont.load_default()
                            self.logger.warning("Using default font - personalized text may not display optimally")
                
                # Add text to image
                draw.text(position, text, font=font, fill=font_color)
                
                # Save to bytes
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='JPEG', quality=95)
                img_bytes.seek(0)
                
                # Save to output folder
                if output_filename:
                    output_path = os.path.join(self.output_folder, output_filename)
                    img.save(output_path, format='JPEG', quality=95)
                    self.logger.info(f"Personalized image saved: {output_path}")
                    return img_bytes.getvalue(), output_path
                
                return img_bytes.getvalue(), None
                
        except Exception as e:
            self.log_error(f"Error processing image: {image_path}", e)
            return None, None
    
    def create_email_message(self, recipient_email: str, recipient_name: str, 
                           subject: str, body: str, image_bytes: bytes) -> Optional[MIMEMultipart]:
        """
        Create email message with personalized greeting card
        """
        try:
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
            
        except Exception as e:
            self.log_error(f"Error creating email message for {recipient_email}", e)
            return None
    
    def send_email(self, msg: Optional[MIMEMultipart]) -> bool:
        """
        Send email using SMTP with error handling
        """
        if not msg:
            return False
            
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.password)
            
            text = msg.as_string()
            server.sendmail(self.sender_email, msg['To'], text)
            server.quit()
            
            self.logger.info(f"Email sent successfully to {msg['To']}")
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
    
    def check_and_send_birthday_emails(self, df: pd.DataFrame, 
                                     birthday_card_path: str,
                                     text_position: tuple = (50, 50)):
        """
        Check for today's birthdays and send emails
        """
        try:
            today = datetime.date.today()
            self.logger.info("Checking for birthday emails...")
            
            # Filter employees with birthdays today
            birthday_employees = df[
                (df['birthday'].dt.month == today.month) & 
                (df['birthday'].dt.day == today.day) &
                (df['birthday'].notna())
            ]
            
            self.logger.info(f"Found {len(birthday_employees)} employees with birthdays today")
            
            for _, employee in birthday_employees.iterrows():
                try:
                    first_name = employee['first_name']
                    last_name = employee['last_name']
                    email = employee['email']
                    
                    self.stats['birthdays_today'].append({
                        'name': f"{first_name} {last_name}",
                        'email': email
                    })
                    
                    # Create personalized greeting
                    greeting_text = f"Dear {first_name}"
                    
                    # Generate unique filename for this image
                    output_filename = f"birthday_{first_name}_{last_name}_{today.strftime('%Y%m%d')}.jpg"
                    
                    # Add text to birthday card
                    personalized_image, saved_path = self.add_text_to_image(
                        birthday_card_path, 
                        greeting_text, 
                        text_position,
                        output_filename=output_filename
                    )
                    
                    if personalized_image:
                        # Create email
                        subject = f"Happy Birthday, {first_name}! 🎉"
                        body = f"Dear {first_name},<br><br>Wishing you a very happy birthday! May this special day bring you joy, happiness, and wonderful memories."
                        
                        msg = self.create_email_message(
                            email, first_name, subject, body, personalized_image
                        )
                        
                        # Send email
                        if self.send_email(msg):
                            self.stats['birthday_emails_sent'] += 1
                        else:
                            self.stats['birthday_emails_failed'] += 1
                    else:
                        self.stats['birthday_emails_failed'] += 1
                        self.log_error(f"Failed to create personalized image for {first_name} {last_name}")
                        
                except Exception as e:
                    self.stats['birthday_emails_failed'] += 1
                    self.log_error(f"Error processing birthday email for employee: {employee.get('email', 'Unknown')}", e)
                    
        except Exception as e:
            self.log_error("Error in birthday email processing", e)
    
    def check_and_send_marriage_anniversary_emails(self, df: pd.DataFrame, 
                                                 anniversary_card_path: str,
                                                 text_position: tuple = (50, 50)):
        """
        Check for today's marriage anniversaries and send emails
        """
        try:
            today = datetime.date.today()
            self.logger.info("Checking for marriage anniversary emails...")
            
            # Check if marriage_anniversary column exists
            if 'marriage_anniversary' not in df.columns:
                self.logger.warning("No marriage_anniversary column found in employee data")
                return
            
            # Filter employees with marriage anniversaries today
            anniversary_employees = df[
                (df['marriage_anniversary'].dt.month == today.month) & 
                (df['marriage_anniversary'].dt.day == today.day) &
                (df['marriage_anniversary'].notna())
            ]
            
            self.logger.info(f"Found {len(anniversary_employees)} employees with marriage anniversaries today")
            
            for _, employee in anniversary_employees.iterrows():
                try:
                    first_name = employee['first_name']
                    last_name = employee['last_name']
                    email = employee['email']
                    
                    # Calculate years of marriage
                    years = today.year - employee['marriage_anniversary'].year
                    
                    self.stats['anniversaries_today'].append({
                        'name': f"{first_name} {last_name}",
                        'email': email,
                        'years': years
                    })
                    
                    # Create personalized greeting
                    greeting_text = f"Dear {first_name}"
                    
                    # Generate unique filename for this image
                    output_filename = f"anniversary_{first_name}_{last_name}_{today.strftime('%Y%m%d')}.jpg"
                    
                    # Add text to anniversary card
                    personalized_image, saved_path = self.add_text_to_image(
                        anniversary_card_path, 
                        greeting_text, 
                        text_position,
                        output_filename=output_filename
                    )
                    
                    if personalized_image:
                        # Create email with appropriate marriage anniversary message
                        subject = f"Happy Anniversary, {first_name}! 💕"
                        
                        if years == 1:
                            body = f"Dear {first_name},<br><br>Congratulations on your first wedding anniversary! Wishing you both a lifetime of love, happiness, and beautiful memories together."
                        else:
                            body = f"Dear {first_name},<br><br>Congratulations on {years} wonderful years of marriage! May your love continue to grow stronger with each passing year. Wishing you both happiness and joy on this special day."
                        
                        msg = self.create_email_message(
                            email, first_name, subject, body, personalized_image
                        )
                        
                        # Send email
                        if self.send_email(msg):
                            self.stats['anniversary_emails_sent'] += 1
                        else:
                            self.stats['anniversary_emails_failed'] += 1
                    else:
                        self.stats['anniversary_emails_failed'] += 1
                        self.log_error(f"Failed to create personalized image for {first_name} {last_name}")
                        
                except Exception as e:
                    self.stats['anniversary_emails_failed'] += 1
                    self.log_error(f"Error processing anniversary email for employee: {employee.get('email', 'Unknown')}", e)
                    
        except Exception as e:
            self.log_error("Error in anniversary email processing", e)
    
    def create_summary_report(self) -> str:
        """Create a summary report of the day's activities"""
        self.stats['end_time'] = datetime.datetime.now()
        duration = self.stats['end_time'] - self.stats['start_time']
        
        report = f"""
        Daily Email Automation Report - {datetime.date.today().strftime('%B %d, %Y')}
        ================================================================
        
        EXECUTION SUMMARY:
        - Start Time: {self.stats['start_time'].strftime('%H:%M:%S')}
        - End Time: {self.stats['end_time'].strftime('%H:%M:%S')}
        - Duration: {duration}
        
        BIRTHDAY EMAILS:
        - Sent Successfully: {self.stats['birthday_emails_sent']}
        - Failed: {self.stats['birthday_emails_failed']}
        - Birthdays Today: {len(self.stats['birthdays_today'])}
        
        ANNIVERSARY EMAILS:
        - Sent Successfully: {self.stats['anniversary_emails_sent']}
        - Failed: {self.stats['anniversary_emails_failed']}
        - Anniversaries Today: {len(self.stats['anniversaries_today'])}
        
        TOTAL EMAILS SENT: {self.stats['birthday_emails_sent'] + self.stats['anniversary_emails_sent']}
        TOTAL ERRORS: {len(self.stats['errors'])}
        
        """
        
        if self.stats['birthdays_today']:
            report += "\nBIRTHDAYS TODAY:\n"
            for birthday in self.stats['birthdays_today']:
                report += f"- {birthday['name']} ({birthday['email']})\n"
        
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
        
        return report
    
    def send_daily_report(self):
        """Send daily report to self"""
        try:
            report = self.create_summary_report()
            
            # Save report to file
            report_filename = os.path.join(self.output_folder, f"daily_report_{datetime.date.today().strftime('%Y%m%d')}.txt")
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.sender_email
            msg['Subject'] = f"Email Automation Daily Report - {datetime.date.today().strftime('%Y-%m-%d')}"
            
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
            except Exception as e:
                self.logger.warning(f"Could not attach report file: {e}")
            
            # Send the report
            if self.send_email(msg):
                self.logger.info("Daily report sent successfully")
            else:
                self.logger.error("Failed to send daily report")
                
        except Exception as e:
            self.log_error("Error creating/sending daily report", e)
    
    def run_daily_check(self, csv_file: str, birthday_card_path: str, 
                       anniversary_card_path: str, 
                       birthday_text_pos: tuple = (50, 50),
                       anniversary_text_pos: tuple = (50, 50)):
        """
        Run daily check for birthdays and marriage anniversaries
        """
        try:
            self.logger.info(f"Starting daily email automation check for {datetime.date.today()}")
            self.logger.info(f"Output folder: {self.output_folder}")
            
            # Load employee data
            df = self.load_employee_data(csv_file)
            
            if df.empty:
                self.log_error("No employee data found or failed to load CSV file")
                return
            
            # Check and send birthday emails
            if os.path.exists(birthday_card_path):
                self.check_and_send_birthday_emails(df, birthday_card_path, birthday_text_pos)
            else:
                self.log_error(f"Birthday card image not found: {birthday_card_path}")
            
            # Check and send marriage anniversary emails
            if os.path.exists(anniversary_card_path):
                self.check_and_send_marriage_anniversary_emails(df, anniversary_card_path, anniversary_text_pos)
            else:
                self.log_error(f"Anniversary card image not found: {anniversary_card_path}")
            
            # Send daily report
            self.send_daily_report()
            
            self.logger.info("Daily email automation check completed")
            
        except Exception as e:
            self.log_error("Critical error in daily check execution", e)
            # Still try to send a report even if there was a critical error
            try:
                self.send_daily_report()
            except:
                pass


# Example usage and configuration
def main():
    try:
        # Email configuration
        SMTP_SERVER = "smtp.gmail.com"  # Change based on your email provider
        SMTP_PORT = 587
        SENDER_EMAIL = "shashwat.airtel@gmail.com"  # Replace with your email
        EMAIL_PASSWORD = "glws titd eisr lslz"  # Replace with your app password
        
        # Folder and file paths
        OUTPUT_FOLDER = "output"  # Folder for saved images and logs
        CSV_FILE = "employees.csv"
        BIRTHDAY_CARD = "birthday_card.png"
        ANNIVERSARY_CARD = "anniversary_card.png"
        
        # Text positioning on cards (adjust based on your card design)
        BIRTHDAY_TEXT_POSITION = (100, 80)
        ANNIVERSARY_TEXT_POSITION = (100, 80)
        
        # Initialize email automation
        email_system = EmailAutomation(SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, EMAIL_PASSWORD, OUTPUT_FOLDER)
        
        # Run daily check
        email_system.run_daily_check(
            CSV_FILE, 
            BIRTHDAY_CARD, 
            ANNIVERSARY_CARD,
            BIRTHDAY_TEXT_POSITION,
            ANNIVERSARY_TEXT_POSITION
        )
        
    except Exception as e:
        print(f"Critical error in main execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


# Example CSV structure (save as employees.csv)
"""
first_name,last_name,email,birthday,marriage_anniversary
John,Doe,john.doe@company.com,1990-06-09,2018-05-20
Jane,Smith,jane.smith@company.com,1985-12-25,2015-08-15
Bob,Johnson,bob.johnson@company.com,1992-06-09,2020-10-12
Alice,Brown,alice.brown@company.com,1988-03-14,
Sarah,Wilson,sarah.wilson@company.com,1991-06-09,2019-09-14
"""