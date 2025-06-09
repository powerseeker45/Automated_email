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
from birthday_card_generator import create_birthday_card
from anniversary_card_generator import create_anniversary_card

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
    
    def hex_to_rgb(self, hex_color: str) -> tuple:
        """
        Convert hex color to RGB tuple
        
        Args:
            hex_color: Hex color string (e.g., '#FF0000' or 'FF0000')
            
        Returns:
            tuple: (R, G, B) values
        """
        try:
            # Remove # if present
            hex_color = hex_color.lstrip('#')
            
            # Ensure we have a 6-character hex code
            if len(hex_color) == 3:
                # Convert short form (e.g., 'F0A') to long form ('FF00AA')
                hex_color = ''.join([c*2 for c in hex_color])
            elif len(hex_color) != 6:
                raise ValueError(f"Invalid hex color length: {hex_color}")
            
            # Convert to RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            return (r, g, b)
            
        except Exception as e:
            self.logger.warning(f"Invalid hex color '{hex_color}', using black as default: {e}")
            return (0, 0, 0)  # Default to black
        
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
                         font_color: str = "#000000",
                         custom_font_path: Optional[str] = None,
                         output_filename: Optional[str] = None,
                         center_align: bool = False,
                         multiline: bool = False) -> tuple:
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
           - For center text: set center_align=True
        
        3. FONT COLOR (HEX):
           - Change font_color parameter: font_color="#FF0000" (red)
           - "#000000" = Black (default)
           - "#FFFFFF" = White
           - "#FF0000" = Red
           - "#00FF00" = Green
           - "#0000FF" = Blue
           - "#FFD700" = Gold
           - "#800080" = Purple
        
        4. CUSTOM FONTS:
           - Set custom_font_path parameter to your font file
           - Example: custom_font_path="fonts/Arial.ttf"
        
        5. CENTER ALIGNMENT:
           - Set center_align=True to center text horizontally
           - position parameter becomes the Y-coordinate for vertical placement
        
        6. MULTILINE TEXT:
           - Set multiline=True for text with line breaks
           - Useful for "Happy Anniversary\nJohn" format
        
        Args:
            image_path: Path to the greeting card image
            text: Text to add (e.g., "Happy Birthday John" or "Happy Anniversary\nJohn")
            position: (x, y) position for text placement, or (ignored, y) if center_align=True
            font_size: Size of the font
            font_color: Hex color string for text (e.g., "#FF0000")
            custom_font_path: Path to custom font file
            output_filename: Optional filename to save the image
            center_align: If True, center text horizontally (position[0] ignored)
            multiline: If True, handle text with line breaks properly
            
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
                
                # Convert hex color to RGB
                rgb_color = self.hex_to_rgb(font_color)
                
                # ================================================================
                # FONT LOADING SECTION
                # ================================================================
                font = None
                
                # Option 1: Try custom font if provided
                if custom_font_path:
                    try:
                        if os.path.exists(custom_font_path):
                            font = ImageFont.truetype(custom_font_path, font_size)
                            self.logger.info(f"Using custom font: {custom_font_path} with size {font_size}")
                        else:
                            self.logger.warning(f"Custom font not found: {custom_font_path}")
                    except Exception as e:
                        self.logger.warning(f"Failed to load custom font {custom_font_path}: {e}")
                
                # Option 2: Try system fonts if custom font failed
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
                            self.logger.info(f"Using system font: {font_path} with size {font_size}")
                            break
                        except:
                            continue
                
                # Option 3: Fallback to default font
                if not font:
                    font = ImageFont.load_default()
                    self.logger.warning(f"Using default font with size {font_size} - text may not display optimally")
                
                # Get image dimensions (1280x720 for your cards)
                img_width, img_height = img.size
                
                # Calculate text positioning
                if center_align:
                    if multiline:
                        # Handle multiline text (for anniversary cards)
                        lines = text.split('\n')
                        line_height = font_size + 10  # Add some spacing between lines
                        total_text_height = len(lines) * line_height
                        
                        # Start Y position (use position[1] or center vertically)
                        start_y = position[1] if position[1] > 0 else (img_height - total_text_height) // 2
                        
                        # Draw each line centered
                        for i, line in enumerate(lines):
                            line_width = draw.textlength(line, font=font)
                            line_x = (img_width - line_width) // 2
                            line_y = start_y + (i * line_height)
                            draw.text((line_x, line_y), line, font=font, fill=rgb_color)
                    else:
                        # Single line text (for birthday cards)
                        text_width = draw.textlength(text, font=font)
                        text_x = (img_width - text_width) // 2
                        text_y = position[1]  # Use provided Y position
                        draw.text((text_x, text_y), text, font=font, fill=rgb_color)
                else:
                    # Use exact position provided (legacy behavior)
                    draw.text(position, text, font=font, fill=rgb_color)
                
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
                                     font_color: str = "#000000",
                                     custom_font_path: Optional[str] = None,
                                     center_align: bool = False):
        """
        Check for today's birthdays and send emails
        
        CUSTOMIZATION PARAMETERS:
        ========================
        text_position: (x, y) tuple for text placement (or (ignored, y) if center_align=True)
        font_size: Size of the font (default: 40)
        font_color: Hex color string for text (e.g., "#FF0000")
        custom_font_path: Path to custom font file
        center_align: If True, center text horizontally
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
                    greeting_text = f"Happy Birthday {first_name}"
                    
                    # Generate unique filename for this image
                    output_filename = f"birthday_{first_name}_{last_name}_{today.strftime('%Y%m%d')}.jpg"
                    
                    # Add text to birthday card with custom styling
                    personalized_image, saved_path = self.add_text_to_image(
                        birthday_card_path, 
                        greeting_text, 
                        text_position,
                        font_size,
                        font_color,
                        custom_font_path,
                        output_filename=output_filename,
                        center_align=center_align,
                        multiline=False  # Birthday cards are single line
                    )
                    
                    if personalized_image:
                        # Create email
                        subject = f"Happy Birthday, {first_name}! 🎉"
                        body = ""  # No body text
                        
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
                                         font_color: str = "#000000",
                                         custom_font_path: Optional[str] = None,
                                         center_align: bool = True):
        """
        Check for today's marriage anniversaries and send emails
        
        CUSTOMIZATION PARAMETERS:
        ========================
        text_position: (x, y) tuple for text placement (or (ignored, y) if center_align=True)
        font_size: Size of the font (default: 40)
        font_color: Hex color string for text (e.g., "#FF0000")
        custom_font_path: Path to custom font file
        center_align: If True, center text horizontally (default: True for anniversaries)
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
                    
                    # Create personalized greeting with name on next line
                    greeting_text = f"Happy Anniversary\n{first_name}"
                    
                    # Generate unique filename for this image
                    output_filename = f"anniversary_{first_name}_{last_name}_{today.strftime('%Y%m%d')}.jpg"
                    
                    # Add text to anniversary card with custom styling
                    personalized_image, saved_path = self.add_text_to_image(
                        anniversary_card_path, 
                        greeting_text, 
                        text_position,
                        font_size,
                        font_color,
                        custom_font_path,
                        output_filename=output_filename,
                        center_align=center_align,
                        multiline=True  # Anniversary cards have name on next line
                    )
                    
                    if personalized_image:
                        # Create email with appropriate marriage anniversary message
                        subject = f"Happy Anniversary, {first_name}! 💕"
                        body = ""  # No body text
                        
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
                       anniversary_text_pos: tuple = (0, 300),  # Y=300 for 1280x720 center
                       birthday_font_size: int = 40,
                       anniversary_font_size: int = 40,
                       birthday_font_color: str = "#000000",
                       anniversary_font_color: str = "#000000",
                       birthday_font_path: Optional[str] = None,
                       anniversary_font_path: Optional[str] = None,
                       birthday_center_align: bool = False,
                       anniversary_center_align: bool = True):
        """
        Run daily check for birthdays and marriage anniversaries
        
        CUSTOMIZATION PARAMETERS:
        ========================
        birthday_text_pos: (x, y) position for birthday text
        anniversary_text_pos: (ignored, y) position for anniversary text (x ignored due to center alignment)
        birthday_font_size: Font size for birthday cards
        anniversary_font_size: Font size for anniversary cards
        birthday_font_color: Hex color for birthday text (e.g., "#FF0000")
        anniversary_font_color: Hex color for anniversary text (e.g., "#0000FF")
        birthday_font_path: Path to custom font for birthday cards
        anniversary_font_path: Path to custom font for anniversary cards
        birthday_center_align: Center align birthday text (default: False)
        anniversary_center_align: Center align anniversary text (default: True)
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
                    birthday_font_color,
                    birthday_font_path,
                    birthday_center_align
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
                    anniversary_font_color,
                    anniversary_font_path,
                    anniversary_center_align
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
        
        # Text positioning for 1280x720 images
        # For center positioning on anniversary cards
        BIRTHDAY_TEXT_X = int(os.getenv('BIRTHDAY_TEXT_X', '100'))
        BIRTHDAY_TEXT_Y = int(os.getenv('BIRTHDAY_TEXT_Y', '80'))
        ANNIVERSARY_TEXT_X = int(os.getenv('ANNIVERSARY_TEXT_X', '0'))    # Ignored due to center alignment
        ANNIVERSARY_TEXT_Y = int(os.getenv('ANNIVERSARY_TEXT_Y', '300'))  # Center vertically for 1280x720
        
        BIRTHDAY_TEXT_POSITION = (BIRTHDAY_TEXT_X, BIRTHDAY_TEXT_Y)
        ANNIVERSARY_TEXT_POSITION = (ANNIVERSARY_TEXT_X, ANNIVERSARY_TEXT_Y)
        
        # Text alignment settings
        BIRTHDAY_CENTER_ALIGN = os.getenv('BIRTHDAY_CENTER_ALIGN', 'False').lower() == 'true'
        ANNIVERSARY_CENTER_ALIGN = os.getenv('ANNIVERSARY_CENTER_ALIGN', 'True').lower() == 'true'
        
        # FONT SIZE CUSTOMIZATION:
        # ========================
        # Add these to your .env file to customize font sizes:
        # BIRTHDAY_FONT_SIZE=50    # Larger font for birthdays
        # ANNIVERSARY_FONT_SIZE=45 # Slightly smaller for anniversaries
        #
        # Default font size is 40 if not specified
        BIRTHDAY_FONT_SIZE = int(os.getenv('BIRTHDAY_FONT_SIZE', '40'))
        ANNIVERSARY_FONT_SIZE = int(os.getenv('ANNIVERSARY_FONT_SIZE', '40'))
        
        # FONT COLOR CUSTOMIZATION (HEX):
        # ===============================
        # Add these to your .env file for custom colors:
        # BIRTHDAY_FONT_COLOR=#FF0000     # Red text for birthdays
        # ANNIVERSARY_FONT_COLOR=#0000FF  # Blue text for anniversaries
        #
        # Common hex colors:
        # Black: #000000
        # White: #FFFFFF
        # Red: #FF0000
        # Blue: #0000FF
        # Green: #00FF00
        # Purple: #800080
        # Orange: #FFA500
        # Gold: #FFD700
        # Pink: #FF69B4
        # Navy: #000080
        #
        BIRTHDAY_FONT_COLOR = os.getenv('BIRTHDAY_FONT_COLOR', '#000000')    # Default: Black
        ANNIVERSARY_FONT_COLOR = os.getenv('ANNIVERSARY_FONT_COLOR', '#000000')  # Default: Black
        
        # CUSTOM FONT PATHS:
        # ==================
        # Add these to your .env file for custom fonts:
        # BIRTHDAY_FONT_PATH=fonts/birthday_font.ttf
        # ANNIVERSARY_FONT_PATH=fonts/anniversary_font.ttf
        #
        # You can use different fonts for birthday and anniversary cards
        # Popular font examples:
        # - fonts/Arial-Bold.ttf
        # - fonts/Times-New-Roman.ttf
        # - fonts/Comic-Sans-MS.ttf
        # - fonts/Edwardian-Script.ttf (elegant script)
        # - fonts/Brush-Script.ttf (casual handwriting)
        #
        BIRTHDAY_FONT_PATH = os.getenv('BIRTHDAY_FONT_PATH')  # None if not set
        ANNIVERSARY_FONT_PATH = os.getenv('ANNIVERSARY_FONT_PATH')  # None if not set
        
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
        print(f"🎂 Birthday Font: {BIRTHDAY_FONT_PATH or 'System Default'}")
        print(f"💕 Anniversary Font: {ANNIVERSARY_FONT_PATH or 'System Default'}")
        print(f"🎨 Birthday Color: {BIRTHDAY_FONT_COLOR} {'(Center Aligned)' if BIRTHDAY_CENTER_ALIGN else ''}")
        print(f"🎨 Anniversary Color: {ANNIVERSARY_FONT_COLOR} {'(Center Aligned)' if ANNIVERSARY_CENTER_ALIGN else ''}")
        print(f"📏 Anniversary Layout: Multiline with name on next line")
        
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
            anniversary_font_color=ANNIVERSARY_FONT_COLOR,
            birthday_font_path=BIRTHDAY_FONT_PATH,
            anniversary_font_path=ANNIVERSARY_FONT_PATH,
            birthday_center_align=BIRTHDAY_CENTER_ALIGN,
            anniversary_center_align=ANNIVERSARY_CENTER_ALIGN
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

# IMAGE SPECIFICATIONS
# ===================
# This configuration is optimized for 1280x720 greeting card images
# Birthday cards: Display "Happy Birthday {Name}" 
# Anniversary cards: Display "Happy Anniversary" with name on next line, center-aligned

# BIRTHDAY CARD CUSTOMIZATION (1280x720)
# =======================================
# Text Position (pixels from top-left corner)
BIRTHDAY_TEXT_X=100
BIRTHDAY_TEXT_Y=300

# Font Size (larger number = bigger text)
BIRTHDAY_FONT_SIZE=48

# Font Color (hex format)
# Popular choices for birthdays:
# Bright Gold: #FFD700
# Party Pink: #FF69B4  
# Vibrant Blue: #1E90FF
# Classic Black: #000000
BIRTHDAY_FONT_COLOR=#FFD700

# Custom Font Path (optional)
# High Tower Text example:
# BIRTHDAY_FONT_PATH=C:/Windows/Fonts/HTOWERT.TTF
# Other examples:
# BIRTHDAY_FONT_PATH=fonts/Arial-Bold.ttf
# BIRTHDAY_FONT_PATH=fonts/Comic-Sans-MS.ttf
# BIRTHDAY_FONT_PATH=fonts/Edwardian-Script.ttf
BIRTHDAY_FONT_PATH=C:/Windows/Fonts/HTOWERT.TTF

# Text Alignment (center birthday text horizontally if desired)
BIRTHDAY_CENTER_ALIGN=false

# ANNIVERSARY CARD CUSTOMIZATION (1280x720)
# ==========================================
# Text Position - X is ignored due to center alignment, Y controls vertical position
ANNIVERSARY_TEXT_X=0
ANNIVERSARY_TEXT_Y=300

# Font Size (larger number = bigger text)
ANNIVERSARY_FONT_SIZE=45

# Font Color (hex format)
# Popular choices for anniversaries:
# Romantic Purple: #800080
# Deep Red: #8B0000
# Elegant Navy: #000080
# Classic Black: #000000
# Rose Gold: #E8B4B8
ANNIVERSARY_FONT_COLOR=#800080

# Custom Font Path (optional) - Can be different from birthday font
# High Tower Text example:
# ANNIVERSARY_FONT_PATH=C:/Windows/Fonts/HTOWERT.TTF
# Other elegant options:
# ANNIVERSARY_FONT_PATH=fonts/Times-New-Roman.ttf
# ANNIVERSARY_FONT_PATH=fonts/Brush-Script.ttf
# ANNIVERSARY_FONT_PATH=fonts/Calligraphy.ttf
ANNIVERSARY_FONT_PATH=C:/Windows/Fonts/HTOWERT.TTF

# Text Alignment (anniversary cards are center-aligned by default)
ANNIVERSARY_CENTER_ALIGN=true

# LAYOUT EXPLANATION:
# ==================
# Birthday Layout:    "Happy Birthday John"     (single line)
# Anniversary Layout: "Happy Anniversary"       (first line, centered)
#                     "      John      "        (second line, centered)

# WINDOWS FONT PATHS REFERENCE:
# =============================
# High Tower Text: C:/Windows/Fonts/HTOWERT.TTF
# Arial Bold: C:/Windows/Fonts/ARIALBD.TTF
# Times New Roman: C:/Windows/Fonts/times.ttf
# Georgia: C:/Windows/Fonts/georgia.ttf
# Calibri: C:/Windows/Fonts/calibri.ttf
# Book Antiqua: C:/Windows/Fonts/BKANT.TTF
# Garamond: C:/Windows/Fonts/GARA.TTF
# Palatino Linotype: C:/Windows/Fonts/pala.ttf

# HEX COLOR REFERENCE:
# ===================
# Classic Colors:
# Black: #000000        White: #FFFFFF
# Red: #FF0000          Green: #00FF00
# Blue: #0000FF         Yellow: #FFFF00

# Professional Colors:
# Navy: #000080         Maroon: #800000
# Dark Green: #006400   Dark Blue: #000080
# Charcoal: #36454F     Steel Blue: #4682B4

# Elegant Colors:
# Gold: #FFD700         Rose Gold: #E8B4B8
# Purple: #800080       Indigo: #4B0082
# Burgundy: #800020     Forest Green: #355E3B

# Fun & Vibrant Colors:
# Hot Pink: #FF69B4     Orange: #FFA500
# Lime: #00FF00         Cyan: #00FFFF
# Magenta: #FF00FF      Coral: #FF7F50

# PRESET COMBINATIONS FOR 1280x720 CARDS:
# =======================================

# ELEGANT PROFESSIONAL SETUP:
# BIRTHDAY_FONT_PATH=C:/Windows/Fonts/HTOWERT.TTF
# BIRTHDAY_FONT_COLOR=#FFD700
# BIRTHDAY_FONT_SIZE=48
# BIRTHDAY_TEXT_Y=320
# 
# ANNIVERSARY_FONT_PATH=C:/Windows/Fonts/HTOWERT.TTF
# ANNIVERSARY_FONT_COLOR=#800080
# ANNIVERSARY_FONT_SIZE=45
# ANNIVERSARY_TEXT_Y=300

# MODERN CASUAL SETUP:
# BIRTHDAY_FONT_PATH=C:/Windows/Fonts/ARIALBD.TTF
# BIRTHDAY_FONT_COLOR=#FF69B4
# BIRTHDAY_FONT_SIZE=52
# BIRTHDAY_CENTER_ALIGN=true
# BIRTHDAY_TEXT_Y=340
#
# ANNIVERSARY_FONT_PATH=C:/Windows/Fonts/ARIALBD.TTF  
# ANNIVERSARY_FONT_COLOR=#4B0082
# ANNIVERSARY_FONT_SIZE=48
# ANNIVERSARY_TEXT_Y=320

# CLASSIC FORMAL SETUP:
# BIRTHDAY_FONT_PATH=C:/Windows/Fonts/times.ttf
# BIRTHDAY_FONT_COLOR=#000080
# BIRTHDAY_FONT_SIZE=46
# BIRTHDAY_TEXT_Y=330
#
# ANNIVERSARY_FONT_PATH=C:/Windows/Fonts/times.ttf
# ANNIVERSARY_FONT_COLOR=#8B0000
# ANNIVERSARY_FONT_SIZE=44
# ANNIVERSARY_TEXT_Y=310

# Optional: Company-specific settings
# COMPANY_NAME=Your Company Name
# HR_SIGNATURE=HR Team

# POSITIONING TIPS FOR 1280x720 IMAGES:
# =====================================
# Y=200-250: Upper third (good for backgrounds with lower design elements)
# Y=300-350: Center area (most balanced, recommended)
# Y=400-450: Lower third (good for backgrounds with upper design elements)
# Y=500+: Bottom area (use carefully, may look too low)

# For birthday cards: Experiment with Y positions between 280-360
# For anniversary cards: Y=300 typically works well for center positioning
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_template)
    
    print("📋 Created .env.template file")
    print("📝 Copy this to .env and update with your settings")
    print("\n🎨 OPTIMIZED FOR 1280x720 GREETING CARDS:")
    print("==========================================")
    print("📐 Image Dimensions: 1280 x 720 pixels")
    print("🎂 Birthday Layout: 'Happy Birthday {Name}' (single line)")
    print("💕 Anniversary Layout: 'Happy Anniversary' + '{Name}' (two lines, center-aligned)")
    print("\n📍 POSITIONING GUIDE:")
    print("===================")
    print("Y=300: Center position (recommended for most designs)")
    print("Y=250: Upper-center (good for cards with bottom graphics)")
    print("Y=350: Lower-center (good for cards with top graphics)")
    print("\n🎨 FONT & COLOR GUIDE:")
    print("=====================")
    print("1. HIGH TOWER TEXT: C:/Windows/Fonts/HTOWERT.TTF (elegant serif)")
    print("2. FONT COLORS: Use hex format (#FFD700 for gold, #800080 for purple)")
    print("3. FONT SIZES: 45-50 recommended for 1280x720 images")
    print("4. CENTER ALIGNMENT: Anniversary cards auto-center, birthday optional")
    print("\n🔧 QUICK SETUP:")
    print("==============")
    print("1. Copy .env.template to .env")
    print("2. Set your email credentials")
    print("3. Adjust Y positions (try Y=300 first)")
    print("4. Choose colors and fonts from the extensive reference")
    print("5. Test with sample employee data")

if __name__ == "__main__":
    # Uncomment the line below to create a .env template file
    #copy the .env.template to .env and fill necessary details
    #create_env_template()

    #Uncomment the line below to create an assets/birthday_card.png 
    #create_birthday_card()

    #Uncomment the line below to create an assets/anniversary_card.png 
    #create_anniversary_card()

    
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