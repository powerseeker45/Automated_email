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
from dotenv import load_dotenv

class EmailAutomation:
    def __init__(self, smtp_server: Optional[str] = None, smtp_port: Optional[int] = None, 
                 email: Optional[str] = None, password: Optional[str] = None, 
                 output_folder: str = "output"):
        """
        Initialize email automation system
        
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
        log_filename = os.path.join(self.logs_folder, "email_automation.log")
        
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
                
            if 'anniversary' in df.columns:
                try:
                    df['anniversary'] = pd.to_datetime(df['anniversary'], errors='coerce')
                    invalid_anniversaries = df[df['anniversary'].isna() & df['anniversary'].notna()]['email'].tolist()
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
        
        CUSTOMIZATION GUIDE:
        ===================
        
        1. FONT SIZE:
           - Change font_size parameter: font_size=60 (larger) or font_size=20 (smaller)
           - Default is 40
        
        2. TEXT POSITION:
           - Change position parameter: position=(x, y)
           - (0, 0) = top-left corner
           - (100, 50) = 100 pixels right, 50 pixels down
           - For center text: calculate based on image size
        
        3. FONT COLOR:
           - Change font_color parameter: font_color=(R, G, B)
           - (0, 0, 0) = Black (default)
           - (255, 255, 255) = White
           - (255, 0, 0) = Red
           - (0, 255, 0) = Green
           - (0, 0, 255) = Blue
        
        4. CUSTOM FONTS:
           - Add your font file to project folder
           - Modify the font loading section below
           - Example: font = ImageFont.truetype("your_font.ttf", font_size)
        
        Args:
            image_path: Path to the greeting card image
            text: Text to add (e.g., "Dear John")
            position: (x, y) position for text placement
            font_size: Size of the font
            font_color: RGB color tuple for text
            output_filename: Optional filename to save the image
            
        Returns:
            tuple: (image_bytes, saved_file_path) or (None, None) on error
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
                
                # ================================================================
                # FONT CUSTOMIZATION SECTION
                # ================================================================
                # 
                # To use a CUSTOM FONT:
                # 1. Download a .ttf or .otf font file
                # 2. Place it in your project folder
                # 3. Uncomment and modify one of these lines:
                #
                # font = ImageFont.truetype("fonts/Arial_Bold.ttf", font_size)
                # font = ImageFont.truetype("fonts/Times_New_Roman.ttf", font_size)
                # font = ImageFont.truetype("fonts/Comic_Sans.ttf", font_size)
                # font = ImageFont.truetype("fonts/Calibri.ttf", font_size)
                #
                # Popular font locations by OS:
                # Windows: C:\Windows\Fonts\
                # macOS: /System/Library/Fonts/ or /Library/Fonts/
                # Linux: /usr/share/fonts/
                #
                # Examples with full paths:
                # font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)  # Windows
                # font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)  # macOS
                # font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)  # Linux
                #
                # ================================================================
                
                # Try to load fonts in order of preference
                font = None
                
                # Option 1: Try custom font (uncomment to use)
                try:
                    font = ImageFont.truetype("fonts/Edwardian Script ITC/edwardianscriptitc.ttf", font_size)
                    self.logger.info(f"Using custom font with size {font_size}")
                except:
                    pass
                
                # Option 2: Try system fonts
                if not font:
                    font_paths = [
                        # Windows fonts
                        "arial.ttf",
                        "calibri.ttf", 
                        "times.ttf",
                        "C:/Windows/Fonts/arial.ttf",
                        "C:/Windows/Fonts/calibri.ttf",
                        "C:/Windows/Fonts/times.ttf",
                        
                        # macOS fonts
                        "/System/Library/Fonts/Arial.ttf",
                        "/System/Library/Fonts/Times.ttc", 
                        "/System/Library/Fonts/Helvetica.ttc",
                        
                        # Linux fonts
                        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
                    ]
                    
                    for font_path in font_paths:
                        try:
                            font = ImageFont.truetype(font_path, font_size)
                            self.logger.info(f"Using font: {font_path} with size {font_size}")
                            break
                        except:
                            continue
                
                # Option 3: Fallback to default font
                if not font:
                    font = ImageFont.load_default()
                    self.logger.warning(f"Using default font with size {font_size} - text may not display optimally")
                
                # ================================================================
                # TEXT POSITIONING EXAMPLES
                # ================================================================
                #
                # BASIC POSITIONING:
                # position = (50, 50)    # 50 pixels from left, 50 pixels from top
                # position = (100, 200)  # 100 pixels from left, 200 pixels from top
                #
                # ADVANCED POSITIONING (get image dimensions first):
                img_width, img_height = img.size
                #
                # CENTER HORIZONTALLY:
                # text_width = draw.textlength(text, font=font)
                # center_x = (img_width - text_width) // 2
                # position = (center_x, 100)  # Centered horizontally, 100px from top
                #
                # CENTER BOTH HORIZONTALLY AND VERTICALLY:
                # text_width = draw.textlength(text, font=font)
                # # Note: textsize is deprecated, use textbbox for height
                # bbox = draw.textbbox((0, 0), text, font=font)
                # text_height = bbox[3] - bbox[1]
                # center_x = (img_width - text_width) // 2
                # center_y = (img_height - text_height) // 2
                # position = (center_x, center_y)
                #
                # BOTTOM RIGHT:
                # text_width = draw.textlength(text, font=font)
                # bbox = draw.textbbox((0, 0), text, font=font)
                # text_height = bbox[3] - bbox[1]
                # position = (img_width - text_width - 20, img_height - text_height - 20)
                #
                # ================================================================
                
                # Add text to image with the specified position, font, and color
                draw.text(position, text, font=font, fill=font_color)
                
                # Optional: Add text shadow or outline for better visibility
                # Uncomment these lines to add a shadow effect:
                #
                # shadow_offset = 2
                # shadow_color = (128, 128, 128)  # Gray shadow
                # draw.text((position[0] + shadow_offset, position[1] + shadow_offset), 
                #          text, font=font, fill=shadow_color)
                # draw.text(position, text, font=font, fill=font_color)
                #
                # Or add an outline:
                # outline_color = (255, 255, 255)  # White outline
                # outline_width = 2
                # for adj in range(-outline_width, outline_width+1):
                #     for adj2 in range(-outline_width, outline_width+1):
                #         draw.text((position[0]+adj, position[1]+adj2), text, font=font, fill=outline_color)
                # draw.text(position, text, font=font, fill=font_color)
                
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
                           subject: str, body: str, image_bytes: Optional[bytes]) -> Optional[MIMEMultipart]:
        """
        Create email message with personalized greeting card
        """
        try:
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
            # Type safety: Ensure required attributes are strings
            if not isinstance(self.smtp_server, str) or not isinstance(self.sender_email, str) or not isinstance(self.password, str):
                self.log_error("Invalid email configuration - missing required string values")
                return False
                
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
                                     text_position: tuple = (50, 50),
                                     font_size: int = 40,
                                     font_color: tuple = (0, 0, 0)):
        """
        Check for today's birthdays and send emails
        
        CUSTOMIZATION PARAMETERS:
        ========================
        text_position: (x, y) tuple for text placement
        font_size: Size of the font (default: 40)
        font_color: (R, G, B) tuple for text color (default: black)
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
                    
                    # Add text to birthday card with custom styling
                    personalized_image, saved_path = self.add_text_to_image(
                        birthday_card_path, 
                        greeting_text, 
                        text_position,
                        font_size,
                        font_color,
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
    
    def check_and_send_anniversary_emails(self, df: pd.DataFrame, 
                                                 anniversary_card_path: str,
                                                 text_position: tuple = (50, 50),
                                                 font_size: int = 40,
                                                 font_color: tuple = (0, 0, 0)):
        """
        Check for today's marriage anniversaries and send emails
        
        CUSTOMIZATION PARAMETERS:
        ========================
        text_position: (x, y) tuple for text placement
        font_size: Size of the font (default: 40)
        font_color: (R, G, B) tuple for text color (default: black)
        """
        try:
            today = datetime.date.today()
            self.logger.info("Checking for marriage anniversary emails...")
            
            # Check if anniversary column exists
            if 'anniversary' not in df.columns:
                self.logger.warning("No anniversary column found in employee data")
                return
            
            # Filter employees with marriage anniversaries today
            anniversary_employees = df[
                (df['anniversary'].dt.month == today.month) & 
                (df['anniversary'].dt.day == today.day) &
                (df['anniversary'].notna())
            ]
            
            self.logger.info(f"Found {len(anniversary_employees)} employees with marriage anniversaries today")
            
            for _, employee in anniversary_employees.iterrows():
                try:
                    first_name = employee['first_name']
                    last_name = employee['last_name']
                    email = employee['email']
                    
                    # Calculate years of marriage
                    years = today.year - employee['anniversary'].year
                    
                    self.stats['anniversaries_today'].append({
                        'name': f"{first_name} {last_name}",
                        'email': email,
                        'years': years
                    })
                    
                    # Create personalized greeting
                    greeting_text = f"Dear {first_name}"
                    
                    # Generate unique filename for this image
                    output_filename = f"anniversary_{first_name}_{last_name}_{today.strftime('%Y%m%d')}.jpg"
                    
                    # Add text to anniversary card with custom styling
                    personalized_image, saved_path = self.add_text_to_image(
                        anniversary_card_path, 
                        greeting_text, 
                        text_position,
                        font_size,
                        font_color,
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
            # Type safety: Ensure sender_email is a string
            if not isinstance(self.sender_email, str):
                self.log_error("Invalid sender email configuration for daily report")
                return
                
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
                       anniversary_text_pos: tuple = (50, 50),
                       birthday_font_size: int = 40,
                       anniversary_font_size: int = 40,
                       birthday_font_color: tuple = (0, 0, 0),
                       anniversary_font_color: tuple = (0, 0, 0)):
        """
        Run daily check for birthdays and marriage anniversaries
        
        CUSTOMIZATION PARAMETERS:
        ========================
        birthday_text_pos: (x, y) position for birthday text
        anniversary_text_pos: (x, y) position for anniversary text
        birthday_font_size: Font size for birthday cards
        anniversary_font_size: Font size for anniversary cards
        birthday_font_color: (R, G, B) color for birthday text
        anniversary_font_color: (R, G, B) color for anniversary text
        """
        try:
            self.logger.info(f"Starting daily email automation check for {datetime.date.today()}")
            self.logger.info(f"Output folder: {self.output_folder}")
            self.logger.info(f"Logs folder: {self.logs_folder}")
            
            # Load employee data
            df = self.load_employee_data(csv_file)
            
            if df.empty:
                self.log_error("No employee data found or failed to load CSV file")
                return
            
            # Check and send birthday emails with custom styling
            if os.path.exists(birthday_card_path):
                self.check_and_send_birthday_emails(
                    df, 
                    birthday_card_path, 
                    birthday_text_pos,
                    birthday_font_size,
                    birthday_font_color
                )
            else:
                self.log_error(f"Birthday card image not found: {birthday_card_path}")
            
            # Check and send marriage anniversary emails with custom styling
            if os.path.exists(anniversary_card_path):
                self.check_and_send_anniversary_emails(
                    df, 
                    anniversary_card_path, 
                    anniversary_text_pos,
                    anniversary_font_size,
                    anniversary_font_color
                )
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
        # Load environment variables from .env file
        load_dotenv()
        
        # Email configuration from environment variables
        # If environment variables are not set, use defaults (not recommended for production)
        SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
        SENDER_EMAIL = os.getenv('SENDER_EMAIL')
        EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
        
        # File and folder configuration from environment variables
        OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'output')
        CSV_FILE = os.getenv('CSV_FILE', 'employees.csv')
        BIRTHDAY_CARD = os.getenv('BIRTHDAY_CARD', 'birthday_card.png')
        ANNIVERSARY_CARD = os.getenv('ANNIVERSARY_CARD', 'anniversary_card.png')
        
        # Text positioning (can be set via environment variables)
        # 
        # HOW TO CUSTOMIZE TEXT POSITION:
        # ===============================
        # The position is (X, Y) coordinates where:
        # - X = pixels from LEFT edge (0 = far left)
        # - Y = pixels from TOP edge (0 = very top)
        #
        # Examples:
        # (50, 50)   = Near top-left
        # (200, 100) = More to the right and down
        # (0, 0)     = Exact top-left corner
        #
        # For environment variables, set:
        # BIRTHDAY_TEXT_X=150     # 150 pixels from left
        # BIRTHDAY_TEXT_Y=120     # 120 pixels from top
        #
        BIRTHDAY_TEXT_X = int(os.getenv('BIRTHDAY_TEXT_X', '100'))
        BIRTHDAY_TEXT_Y = int(os.getenv('BIRTHDAY_TEXT_Y', '80'))
        ANNIVERSARY_TEXT_X = int(os.getenv('ANNIVERSARY_TEXT_X', '100'))
        ANNIVERSARY_TEXT_Y = int(os.getenv('ANNIVERSARY_TEXT_Y', '80'))
        
        BIRTHDAY_TEXT_POSITION = (BIRTHDAY_TEXT_X, BIRTHDAY_TEXT_Y)
        ANNIVERSARY_TEXT_POSITION = (ANNIVERSARY_TEXT_X, ANNIVERSARY_TEXT_Y)
        
        # FONT SIZE CUSTOMIZATION:
        # ========================
        # Add these to your .env file to customize font sizes:
        # BIRTHDAY_FONT_SIZE=50    # Larger font for birthdays
        # ANNIVERSARY_FONT_SIZE=45 # Slightly smaller for anniversaries
        #
        # Default font size is 40 if not specified
        BIRTHDAY_FONT_SIZE = int(os.getenv('BIRTHDAY_FONT_SIZE', '40'))
        ANNIVERSARY_FONT_SIZE = int(os.getenv('ANNIVERSARY_FONT_SIZE', '40'))
        
        # FONT COLOR CUSTOMIZATION:
        # =========================
        # Add these to your .env file for custom colors:
        # BIRTHDAY_FONT_COLOR_R=255    # Red component (0-255)
        # BIRTHDAY_FONT_COLOR_G=0      # Green component (0-255)  
        # BIRTHDAY_FONT_COLOR_B=0      # Blue component (0-255)
        # Result: (255, 0, 0) = Red text
        #
        # Common colors:
        # Black: (0, 0, 0)
        # White: (255, 255, 255)
        # Red: (255, 0, 0)
        # Blue: (0, 0, 255)
        # Green: (0, 255, 0)
        # Purple: (128, 0, 128)
        # Orange: (255, 165, 0)
        #
        BIRTHDAY_FONT_R = int(os.getenv('BIRTHDAY_FONT_COLOR_R', '0'))    # Default: Black
        BIRTHDAY_FONT_G = int(os.getenv('BIRTHDAY_FONT_COLOR_G', '0'))
        BIRTHDAY_FONT_B = int(os.getenv('BIRTHDAY_FONT_COLOR_B', '0'))
        BIRTHDAY_FONT_COLOR = (BIRTHDAY_FONT_R, BIRTHDAY_FONT_G, BIRTHDAY_FONT_B)
        
        ANNIVERSARY_FONT_R = int(os.getenv('ANNIVERSARY_FONT_COLOR_R', '0'))  # Default: Black
        ANNIVERSARY_FONT_G = int(os.getenv('ANNIVERSARY_FONT_COLOR_G', '0'))
        ANNIVERSARY_FONT_B = int(os.getenv('ANNIVERSARY_FONT_COLOR_B', '0'))
        ANNIVERSARY_FONT_COLOR = (ANNIVERSARY_FONT_R, ANNIVERSARY_FONT_G, ANNIVERSARY_FONT_B)
        
        # Validate required environment variables
        if not SENDER_EMAIL or not EMAIL_PASSWORD:
            print("❌ Error: SENDER_EMAIL and EMAIL_PASSWORD environment variables are required!")
            print("Please create a .env file with your email configuration.")
            return
        
        print("🚀 Starting Email Automation System")
        print(f"📧 Sender Email: {SENDER_EMAIL}")
        print(f"🏢 SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
        print(f"📁 Output Folder: {OUTPUT_FOLDER}")
        print(f"📊 CSV File: {CSV_FILE}")
        
        # Initialize email automation
        email_system = EmailAutomation(
            smtp_server=SMTP_SERVER,
            smtp_port=SMTP_PORT,
            email=SENDER_EMAIL,
            password=EMAIL_PASSWORD,
            output_folder=OUTPUT_FOLDER
        )
        
        # Run daily check with all customization options
        email_system.run_daily_check(
            csv_file=CSV_FILE, 
            birthday_card_path=BIRTHDAY_CARD, 
            anniversary_card_path=ANNIVERSARY_CARD,
            birthday_text_pos=BIRTHDAY_TEXT_POSITION,
            anniversary_text_pos=ANNIVERSARY_TEXT_POSITION,
            birthday_font_size=BIRTHDAY_FONT_SIZE,
            anniversary_font_size=ANNIVERSARY_FONT_SIZE,
            birthday_font_color=BIRTHDAY_FONT_COLOR,
            anniversary_font_color=ANNIVERSARY_FONT_COLOR
        )
        
        print("✅ Email automation completed successfully!")
        
    except Exception as e:
        print(f"❌ Critical error in main execution: {e}")
        import traceback
        traceback.print_exc()

def create_env_template():
    """Create a template .env file for configuration"""
    env_template = """# Email Automation Configuration
# Copy this file to .env and update with your settings

# SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Email Credentials (REQUIRED)
SENDER_EMAIL=your.email@gmail.com
EMAIL_PASSWORD=your_app_password_here

# File Paths
OUTPUT_FOLDER=output
CSV_FILE=employees.csv
BIRTHDAY_CARD=birthday_card.png
ANNIVERSARY_CARD=anniversary_card.png

# BIRTHDAY CARD CUSTOMIZATION
# ============================
# Text Position (pixels from top-left corner)
BIRTHDAY_TEXT_X=100
BIRTHDAY_TEXT_Y=80

# Font Size (larger number = bigger text)
BIRTHDAY_FONT_SIZE=40

# Font Color (RGB values 0-255)
# Examples:
# Black: R=0, G=0, B=0
# White: R=255, G=255, B=255  
# Red: R=255, G=0, B=0
# Blue: R=0, G=0, B=255
# Gold: R=255, G=215, B=0
BIRTHDAY_FONT_COLOR_R=0
BIRTHDAY_FONT_COLOR_G=0
BIRTHDAY_FONT_COLOR_B=0

# ANNIVERSARY CARD CUSTOMIZATION
# ==============================
# Text Position (pixels from top-left corner)
ANNIVERSARY_TEXT_X=100
ANNIVERSARY_TEXT_Y=80

# Font Size (larger number = bigger text)
ANNIVERSARY_FONT_SIZE=40

# Font Color (RGB values 0-255)
ANNIVERSARY_FONT_COLOR_R=0
ANNIVERSARY_FONT_COLOR_G=0
ANNIVERSARY_FONT_COLOR_B=0

# Optional: Company-specific settings
# COMPANY_NAME=Your Company Name
# HR_SIGNATURE=HR Team

# QUICK CUSTOMIZATION EXAMPLES:
# =============================
# For larger birthday text in red color at bottom-right:
# BIRTHDAY_TEXT_X=400
# BIRTHDAY_TEXT_Y=300
# BIRTHDAY_FONT_SIZE=60
# BIRTHDAY_FONT_COLOR_R=255
# BIRTHDAY_FONT_COLOR_G=0
# BIRTHDAY_FONT_COLOR_B=0
#
# For smaller anniversary text in blue at top-center:
# ANNIVERSARY_TEXT_X=200
# ANNIVERSARY_TEXT_Y=50
# ANNIVERSARY_FONT_SIZE=30
# ANNIVERSARY_FONT_COLOR_R=0
# ANNIVERSARY_FONT_COLOR_G=0
# ANNIVERSARY_FONT_COLOR_B=255
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_template)
    
    print("📋 Created .env.template file")
    print("📝 Copy this to .env and update with your settings")
    print("\n🎨 FONT & POSITION CUSTOMIZATION GUIDE:")
    print("======================================")
    print("1. TEXT POSITION: (X, Y) coordinates")
    print("   - X = pixels from LEFT (0 = far left)")
    print("   - Y = pixels from TOP (0 = very top)")
    print("   - Example: X=200, Y=100 = 200px right, 100px down")
    print("\n2. FONT SIZE: Number (bigger = larger text)")
    print("   - Small: 20-30")
    print("   - Medium: 40-50") 
    print("   - Large: 60-80")
    print("\n3. FONT COLOR: RGB values (0-255 each)")
    print("   - Black: R=0, G=0, B=0")
    print("   - White: R=255, G=255, B=255")
    print("   - Red: R=255, G=0, B=0")
    print("   - Gold: R=255, G=215, B=0")
    print("\n4. CUSTOM FONTS: Edit the add_text_to_image() method")

if __name__ == "__main__":
    # Uncomment the line below to create a .env template file
    #create_env_template()
    
    main()


# Example CSV structure (save as employees.csv)
"""
first_name,last_name,email,birthday,anniversary
John,Doe,john.doe@company.com,1990-06-09,2018-05-20
Jane,Smith,jane.smith@company.com,1985-12-25,2015-08-15
Bob,Johnson,bob.johnson@company.com,1992-06-09,2020-10-12
Alice,Brown,alice.brown@company.com,1988-03-14,
Sarah,Wilson,sarah.wilson@company.com,1991-06-09,2019-09-14
"""