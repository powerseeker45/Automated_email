import pandas as pd
import json
import base64
from PIL import Image, ImageDraw, ImageFont
import datetime
import os
import io
import logging
import traceback
from typing import Optional, List, Dict, Union
from dotenv import load_dotenv
import webbrowser
import http.server
import socketserver
import threading
import urllib.parse
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager

class OutlookWebEmailAutomation:
    def __init__(self, output_folder: str = "output"):
        """
        Initialize Outlook Web email automation system using browser automation
        
        Args:
            output_folder: Folder to save generated images and logs
        """
        load_dotenv()
        
        self.output_folder = output_folder
        self.driver: Optional[WebDriver] = None
        self.user_email = None
        
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
        log_filename = os.path.join(self.logs_folder, "outlook_web_automation.log")
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler = logging.FileHandler(log_filename, mode='a', encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        
        self.logger = logging.getLogger('OutlookWebAutomation')
        self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()
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
    
    def setup_browser(self) -> bool:
        """Setup Chrome browser with appropriate options"""
        try:
            self.logger.info("Setting up Chrome browser...")
            
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Use existing user profile to leverage existing login
            user_data_dir = os.getenv('CHROME_USER_DATA_DIR')
            if user_data_dir and os.path.exists(user_data_dir):
                chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
                self.logger.info(f"Using Chrome profile: {user_data_dir}")
            else:
                self.logger.info("Using temporary Chrome profile (you may need to log in)")
            
            # Install and setup ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self.logger.info("✅ Chrome browser setup successful")
            return True
            
        except Exception as e:
            self.log_error("Failed to setup browser", e)
            return False
    
    def login_to_outlook(self) -> bool:
        """Navigate to Outlook and ensure user is logged in"""
        try:
            # Navigate to Outlook Web
            if not self.driver:
                raise Exception("Browser driver not initialized")
                
            self.driver.get("https://outlook.live.com")
            
            # Wait for page to load
            time.sleep(5)
            
            # Check if already logged in by looking for compose button or user menu
            try:
                # Look for compose button (indicates logged in)
                WebDriverWait(self.driver, 10).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.XPATH, "//button[contains(@aria-label, 'New message') or contains(@aria-label, 'Compose')]")),
                        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'compose') or contains(@data-testid, 'compose')]")),
                        EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'New message')]"))
                    )
                )
                self.logger.info("✅ Already logged in to Outlook")
                return self._get_user_email()
                
            except:
                # Not logged in, check for sign-in elements
                self.logger.info("Not logged in, checking for sign-in options...")
                
                # Look for sign-in button
                try:
                    if not self.driver:
                        raise Exception("Browser driver not available")
                        
                    sign_in_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'login') or contains(text(), 'Sign in')]"))
                    )
                    sign_in_button.click()
                    time.sleep(3)
                except:
                    pass
                
                # Inform user to log in manually
                print("\n" + "="*60)
                print("🔐 OUTLOOK LOGIN REQUIRED")
                print("="*60)
                print("Please log in to your Outlook account in the browser window that opened.")
                print("After logging in successfully, you should see your inbox.")
                print("Then return here and press Enter to continue...")
                print("="*60)
                
                input("Press Enter after logging in to Outlook...")
                
                # Verify login by checking for compose button again
                try:
                    if not self.driver:
                        raise Exception("Browser driver not available")
                        
                    WebDriverWait(self.driver, 30).until(
                        EC.any_of(
                            EC.presence_of_element_located((By.XPATH, "//button[contains(@aria-label, 'New message') or contains(@aria-label, 'Compose')]")),
                            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'compose')]")),
                            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'New message')]"))
                        )
                    )
                    self.logger.info("✅ Login verification successful")
                    return self._get_user_email()
                    
                except Exception as e:
                    self.log_error("Login verification failed", e)
                    return False
                    
        except Exception as e:
            self.log_error("Error during Outlook login process", e)
            return False
    
    def _get_user_email(self) -> bool:
        """Extract user email from the page"""
        try:
            if not self.driver:
                self.log_error("Browser driver not available for email extraction")
                return False
                
            # Try to find user email in various places
            email_selectors = [
                "//div[contains(@class, 'profile')]//span[contains(@class, 'email')]",
                "//div[contains(@aria-label, '@')]",
                "//span[contains(text(), '@')]",
                "//div[contains(@class, 'user')]//span[contains(text(), '@')]"
            ]
            
            for selector in email_selectors:
                try:
                    email_element = self.driver.find_element(By.XPATH, selector)
                    email_text = email_element.text
                    if '@' in email_text:
                        self.user_email = email_text
                        self.logger.info(f"Found user email: {self.user_email}")
                        return True
                except:
                    continue
            
            # If we can't find the email, that's okay - we can still send emails
            self.user_email = "outlook_user"
            self.logger.info("Could not extract user email, but login appears successful")
            return True
            
        except Exception as e:
            self.log_error("Error extracting user email", e)
            return True  # Don't fail if we can't get email
    
    def compose_and_send_email(self, recipient_email: str, recipient_name: str, 
                              subject: str, image_bytes: Optional[bytes]) -> bool:
        """Compose and send email using Outlook Web interface"""
        try:
            if not self.driver:
                self.log_error("Browser driver not available for email composition")
                return False
                
            self.logger.info(f"Composing email to {recipient_email}")
            
            # Click compose/new message button
            compose_selectors = [
                "//button[contains(@aria-label, 'New message')]",
                "//button[contains(@aria-label, 'Compose')]",
                "//div[contains(@data-testid, 'compose')]//button",
                "//span[contains(text(), 'New message')]/..",
                "//button[contains(@class, 'compose')]"
            ]
            
            compose_clicked = False
            for selector in compose_selectors:
                try:
                    if not self.driver:
                        raise Exception("Browser driver not available")
                        
                    compose_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    compose_button.click()
                    compose_clicked = True
                    self.logger.info("Clicked compose button")
                    break
                except:
                    continue
            
            if not compose_clicked:
                raise Exception("Could not find compose button")
            
            # Wait for compose window to open
            time.sleep(3)
            
            # Fill in recipient
            to_selectors = [
                "//input[contains(@aria-label, 'To')]",
                "//input[contains(@placeholder, 'To')]",
                "//div[contains(@aria-label, 'To')]//input",
                "//input[contains(@class, 'to')]"
            ]
            
            for selector in to_selectors:
                try:
                    if not self.driver:
                        raise Exception("Browser driver not available")
                        
                    to_field = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    to_field.clear()
                    to_field.send_keys(recipient_email)
                    time.sleep(1)
                    self.logger.info(f"Filled recipient: {recipient_email}")
                    break
                except:
                    continue
            
            # Fill in subject
            subject_selectors = [
                "//input[contains(@aria-label, 'Subject')]",
                "//input[contains(@placeholder, 'Subject')]",
                "//input[contains(@class, 'subject')]"
            ]
            
            for selector in subject_selectors:
                try:
                    if not self.driver:
                        raise Exception("Browser driver not available")
                        
                    subject_field = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    subject_field.clear()
                    subject_field.send_keys(subject)
                    time.sleep(1)
                    self.logger.info(f"Filled subject: {subject}")
                    break
                except:
                    continue
            
            # Attach image if provided
            if image_bytes:
                # Save image temporarily
                temp_image_path = os.path.join(self.output_folder, f"temp_attachment_{int(time.time())}.jpg")
                with open(temp_image_path, 'wb') as f:
                    f.write(image_bytes)
                
                # Look for attachment button
                attach_selectors = [
                    "//button[contains(@aria-label, 'Attach')]",
                    "//button[contains(@title, 'Attach')]",
                    "//input[@type='file']",
                    "//button[contains(@class, 'attach')]"
                ]
                
                for selector in attach_selectors:
                    try:
                        if not self.driver:
                            raise Exception("Browser driver not available")
                            
                        if 'input' in selector:
                            # Direct file input
                            file_input = self.driver.find_element(By.XPATH, selector)
                            file_input.send_keys(temp_image_path)
                        else:
                            # Button that opens file dialog
                            attach_button = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                            attach_button.click()
                            time.sleep(2)
                            
                            # Look for file input after clicking
                            file_input = WebDriverWait(self.driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
                            )
                            file_input.send_keys(temp_image_path)
                        
                        time.sleep(3)  # Wait for upload
                        self.logger.info("Image attached successfully")
                        break
                    except:
                        continue
                
                # Clean up temp file
                try:
                    os.remove(temp_image_path)
                except:
                    pass
            
            # Send the email
            send_selectors = [
                "//button[contains(@aria-label, 'Send')]",
                "//button[contains(text(), 'Send')]",
                "//button[contains(@class, 'send')]",
                "//div[contains(@aria-label, 'Send')]//button"
            ]
            
            for selector in send_selectors:
                try:
                    if not self.driver:
                        raise Exception("Browser driver not available")
                        
                    send_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    send_button.click()
                    time.sleep(2)
                    self.logger.info(f"✅ Email sent to {recipient_email}")
                    return True
                except:
                    continue
            
            raise Exception("Could not find send button")
            
        except Exception as e:
            self.log_error(f"Error sending email to {recipient_email}", e)
            return False
    
    def hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple"""
        try:
            hex_color = hex_color.lstrip('#')
            if len(hex_color) == 3:
                hex_color = ''.join([c*2 for c in hex_color])
            elif len(hex_color) != 6:
                raise ValueError(f"Invalid hex color length: {hex_color}")
            
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return (r, g, b)
            
        except Exception as e:
            self.logger.warning(f"Invalid hex color '{hex_color}', using black as default: {e}")
            return (0, 0, 0)
        
    def load_employee_data(self, csv_file: str) -> pd.DataFrame:
        """Load employee data from CSV file with error handling"""
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
        """Add personalized text to greeting card image and save to output folder"""
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
                
            with Image.open(image_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                draw = ImageDraw.Draw(img)
                rgb_color = self.hex_to_rgb(font_color)
                
                # Font loading section
                font = None
                
                if custom_font_path:
                    try:
                        if os.path.exists(custom_font_path):
                            font = ImageFont.truetype(custom_font_path, font_size)
                            self.logger.info(f"Using custom font: {custom_font_path} with size {font_size}")
                        else:
                            self.logger.warning(f"Custom font not found: {custom_font_path}")
                    except Exception as e:
                        self.logger.warning(f"Failed to load custom font {custom_font_path}: {e}")
                
                if not font:
                    font_paths = [
                        "arial.ttf", "calibri.ttf", "times.ttf",
                        "C:/Windows/Fonts/arial.ttf",
                        "C:/Windows/Fonts/calibri.ttf",
                        "C:/Windows/Fonts/times.ttf",
                        "/System/Library/Fonts/Arial.ttf",
                        "/System/Library/Fonts/Times.ttc", 
                        "/System/Library/Fonts/Helvetica.ttc",
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
                
                if not font:
                    font = ImageFont.load_default()
                    self.logger.warning(f"Using default font with size {font_size}")
                
                # Get image dimensions
                img_width, img_height = img.size
                
                # Calculate text positioning
                if center_align:
                    if multiline:
                        lines = text.split('\n')
                        line_height = font_size + 10
                        total_text_height = len(lines) * line_height
                        start_y = position[1] if position[1] > 0 else (img_height - total_text_height) // 2
                        
                        for i, line in enumerate(lines):
                            line_width = draw.textlength(line, font=font)
                            line_x = (img_width - line_width) // 2
                            line_y = start_y + (i * line_height)
                            draw.text((line_x, line_y), line, font=font, fill=rgb_color)
                    else:
                        text_width = draw.textlength(text, font=font)
                        text_x = (img_width - text_width) // 2
                        text_y = position[1]
                        draw.text((text_x, text_y), text, font=font, fill=rgb_color)
                else:
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
    
    def check_and_send_birthday_emails(self, df: pd.DataFrame, 
                                     birthday_card_path: str,
                                     text_position: tuple = (50, 50),
                                     font_size: int = 40,
                                     font_color: str = "#000000",
                                     custom_font_path: Optional[str] = None,
                                     center_align: bool = False):
        """Check for today's birthdays and send emails"""
        try:
            today = datetime.date.today()
            self.logger.info("Checking for birthday emails...")
            
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
                    
                    greeting_text = f"Happy Birthday {first_name}"
                    output_filename = f"birthday_{first_name}_{last_name}_{today.strftime('%Y%m%d')}.jpg"
                    
                    personalized_image, saved_path = self.add_text_to_image(
                        birthday_card_path, 
                        greeting_text, 
                        text_position,
                        font_size,
                        font_color,
                        custom_font_path,
                        output_filename=output_filename,
                        center_align=center_align,
                        multiline=False
                    )
                    
                    if personalized_image:
                        subject = f"Happy Birthday, {first_name}! 🎉"
                        
                        if self.compose_and_send_email(email, f"{first_name} {last_name}", subject, personalized_image):
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
        """Check for today's marriage anniversaries and send emails"""
        try:
            today = datetime.date.today()
            self.logger.info("Checking for marriage anniversary emails...")
            
            if 'anniversary' not in df.columns:
                self.logger.warning("No anniversary column found in employee data")
                return
            
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
                    
                    years = today.year - employee['anniversary'].year
                    
                    self.stats['anniversaries_today'].append({
                        'name': f"{first_name} {last_name}",
                        'email': email,
                        'years': years
                    })
                    
                    greeting_text = f"Happy Anniversary\n{first_name}"
                    output_filename = f"anniversary_{first_name}_{last_name}_{today.strftime('%Y%m%d')}.jpg"
                    
                    personalized_image, saved_path = self.add_text_to_image(
                        anniversary_card_path, 
                        greeting_text, 
                        text_position,
                        font_size,
                        font_color,
                        custom_font_path,
                        output_filename=output_filename,
                        center_align=center_align,
                        multiline=True
                    )
                    
                    if personalized_image:
                        subject = f"Happy Anniversary, {first_name}! 💕"
                        
                        if self.compose_and_send_email(email, f"{first_name} {last_name}", subject, personalized_image):
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
Daily Outlook Web Email Automation Report - {datetime.date.today().strftime('%B %d, %Y')}
================================================================

EXECUTION SUMMARY:
- User: {self.user_email or 'Outlook User'}
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
        """Send daily report to authenticated user"""
        try:
            report = self.create_summary_report()
            
            # Save report to file
            report_filename = os.path.join(self.output_folder, f"daily_report_{datetime.date.today().strftime('%Y%m%d')}.txt")
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            # Send report via Outlook Web
            subject = f"📊 Daily Email Automation Report - {datetime.date.today().strftime('%Y-%m-%d')}"
            
            if self.user_email and '@' in str(self.user_email):
                recipient_email = self.user_email
            else:
                # If we can't determine user email, skip sending report
                self.logger.info("Cannot determine user email, saving report to file only")
                return
            
            # Create a simple text email for the report
            self.logger.info("Sending daily report...")
            
            # For the report, we'll send it as plain text without image
            if self.compose_and_send_email(recipient_email, "Admin", subject, None):
                self.logger.info("✅ Daily report sent successfully")
            else:
                self.logger.error("Failed to send daily report")
                
        except Exception as e:
            self.log_error("Error creating/sending daily report", e)
    
    def cleanup(self):
        """Cleanup browser resources"""
        try:
            if self.driver:
                self.driver.quit()
                self.logger.info("Browser cleanup completed")
        except Exception as e:
            self.log_error("Error during cleanup", e)
    
    def run_daily_check(self, csv_file: str, birthday_card_path: str, 
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
        """Run daily check for birthdays and marriage anniversaries"""
        try:
            self.logger.info(f"🚀 Starting Outlook Web email automation check for {datetime.date.today()}")
            self.logger.info(f"📁 Output folder: {self.output_folder}")
            self.logger.info(f"📝 Logs folder: {self.logs_folder}")
            
            # Setup browser
            if not self.setup_browser():
                self.log_error("Browser setup failed. Cannot proceed.")
                return
            
            # Login to Outlook
            if not self.login_to_outlook():
                self.log_error("Outlook login failed. Cannot proceed.")
                return
            
            # Load employee data
            df = self.load_employee_data(csv_file)
            
            if df.empty:
                self.log_error("No employee data found or failed to load CSV file")
                return
            
            # Check and send birthday emails
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
            
            # Check and send anniversary emails
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
            
            self.logger.info("✅ Outlook Web email automation check completed")
            
        except Exception as e:
            self.log_error("Critical error in daily check execution", e)
            # Still try to send a report even if there was a critical error
            try:
                self.send_daily_report()
            except:
                pass
        finally:
            # Always cleanup browser
            self.cleanup()


def main():
    """Main function to run the Outlook Web email automation"""
    try:
        # Load environment variables from .env file
        load_dotenv()
        
        # File and folder configuration from environment variables
        OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'output')
        CSV_FILE = os.getenv('CSV_FILE', 'employees_test_today.csv')
        BIRTHDAY_CARD = os.getenv('BIRTHDAY_CARD', 'assets/Slide2.PNG')
        ANNIVERSARY_CARD = os.getenv('ANNIVERSARY_CARD', 'assets/Slide1.PNG')
        
        # Text positioning for 1280x720 images
        BIRTHDAY_TEXT_X = int(os.getenv('BIRTHDAY_TEXT_X', '50'))
        BIRTHDAY_TEXT_Y = int(os.getenv('BIRTHDAY_TEXT_Y', '300'))
        ANNIVERSARY_TEXT_X = int(os.getenv('ANNIVERSARY_TEXT_X', '0'))
        ANNIVERSARY_TEXT_Y = int(os.getenv('ANNIVERSARY_TEXT_Y', '200'))
        
        BIRTHDAY_TEXT_POSITION = (BIRTHDAY_TEXT_X, BIRTHDAY_TEXT_Y)
        ANNIVERSARY_TEXT_POSITION = (ANNIVERSARY_TEXT_X, ANNIVERSARY_TEXT_Y)
        
        # Text alignment settings
        BIRTHDAY_CENTER_ALIGN = os.getenv('BIRTHDAY_CENTER_ALIGN', 'false').lower() == 'true'
        ANNIVERSARY_CENTER_ALIGN = os.getenv('ANNIVERSARY_CENTER_ALIGN', 'true').lower() == 'true'
        
        # Font customization
        BIRTHDAY_FONT_SIZE = int(os.getenv('BIRTHDAY_FONT_SIZE', '64'))
        ANNIVERSARY_FONT_SIZE = int(os.getenv('ANNIVERSARY_FONT_SIZE', '72'))
        
        BIRTHDAY_FONT_COLOR = os.getenv('BIRTHDAY_FONT_COLOR', '#4b446a')
        ANNIVERSARY_FONT_COLOR = os.getenv('ANNIVERSARY_FONT_COLOR', '#72719f')
        
        BIRTHDAY_FONT_PATH = os.getenv('BIRTHDAY_FONT_PATH', 'fonts/Inkfree.ttf')
        ANNIVERSARY_FONT_PATH = os.getenv('ANNIVERSARY_FONT_PATH', 'C:/Windows/Fonts/HTOWERT.TTF')
        
        # Optional: Chrome user data directory for persistent login
        CHROME_USER_DATA_DIR = os.getenv('CHROME_USER_DATA_DIR')
        
        print("🚀 Starting Outlook Web Email Automation System")
        print(f"📁 Output Folder: {OUTPUT_FOLDER}")
        print(f"📊 CSV File: {CSV_FILE}")
        print(f"🎂 Birthday Card: {BIRTHDAY_CARD}")
        print(f"💕 Anniversary Card: {ANNIVERSARY_CARD}")
        print(f"🎨 Birthday Font: {BIRTHDAY_FONT_PATH} ({BIRTHDAY_FONT_COLOR})")
        print(f"🎨 Anniversary Font: {ANNIVERSARY_FONT_PATH} ({ANNIVERSARY_FONT_COLOR})")
        
        if CHROME_USER_DATA_DIR:
            print(f"🔐 Chrome Profile: {CHROME_USER_DATA_DIR}")
        else:
            print("🔐 Chrome Profile: Temporary (you may need to log in)")
        
        print("\n📋 REQUIREMENTS CHECK:")
        print("="*40)
        
        # Check for Chrome
        try:
            import selenium
            print("✅ Selenium installed")
        except ImportError:
            print("❌ Selenium not installed. Run: pip install selenium")
            return
        
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            print("✅ WebDriver Manager installed")
        except ImportError:
            print("❌ WebDriver Manager not installed. Run: pip install webdriver-manager")
            return
        
        print("✅ All requirements satisfied")
        print("="*40)
        
        # Initialize email automation
        email_system = OutlookWebEmailAutomation(output_folder=OUTPUT_FOLDER)
        
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
        
        print("✅ Outlook Web email automation completed successfully!")
        
    except Exception as e:
        print(f"❌ Critical error in main execution: {e}")
        import traceback
        traceback.print_exc()


def create_web_env_template():
    """Create a template .env file for Outlook Web automation"""
    env_template = """# Outlook Web Email Automation Configuration
# No Azure registration required - uses browser automation

# File Paths (same as previous versions)
OUTPUT_FOLDER=output
CSV_FILE=employees_test_today.csv
BIRTHDAY_CARD=assets/Slide2.PNG
ANNIVERSARY_CARD=assets/Slide1.PNG

# BIRTHDAY CARD CUSTOMIZATION (1280x720)
BIRTHDAY_TEXT_X=50
BIRTHDAY_TEXT_Y=300
BIRTHDAY_FONT_SIZE=64
BIRTHDAY_FONT_COLOR=#4b446a
BIRTHDAY_FONT_PATH=fonts/Inkfree.ttf
BIRTHDAY_CENTER_ALIGN=false

# ANNIVERSARY CARD CUSTOMIZATION (1280x720) 
ANNIVERSARY_TEXT_X=0
ANNIVERSARY_TEXT_Y=200
ANNIVERSARY_FONT_SIZE=72
ANNIVERSARY_FONT_COLOR=#72719f
ANNIVERSARY_FONT_PATH=C:/Windows/Fonts/HTOWERT.TTF
ANNIVERSARY_CENTER_ALIGN=true

# OPTIONAL: Chrome User Data Directory
# If you want to use an existing Chrome profile to stay logged in:
# CHROME_USER_DATA_DIR=C:/Users/YourName/AppData/Local/Google/Chrome/User Data
# Leave blank to use temporary profile (you'll need to log in each time)
CHROME_USER_DATA_DIR=

# HOW IT WORKS:
# =============
# 1. Opens Chrome browser automatically
# 2. Navigates to https://outlook.live.com
# 3. Prompts you to log in if not already logged in
# 4. Automates composing and sending emails through web interface
# 5. Attaches personalized greeting card images
# 6. Sends daily report to your email

# ADVANTAGES:
# ===========
# ✅ No Azure registration required
# ✅ No API keys or client IDs needed
# ✅ Works with any Outlook/Hotmail account
# ✅ Uses your existing browser login
# ✅ Simple setup - just install packages and run

# REQUIRED PACKAGES:
# ==================
# pip install pandas pillow python-dotenv selenium webdriver-manager

# BROWSER REQUIREMENTS:
# =====================
# - Google Chrome installed
# - ChromeDriver (automatically downloaded by webdriver-manager)

# FIRST RUN INSTRUCTIONS:
# =======================
# 1. Install required packages
# 2. Create/update this .env file
# 3. Run: python outlook_web_automation.py
# 4. Log in to Outlook when browser opens
# 5. Let the script send emails automatically

# PERSISTENT LOGIN (OPTIONAL):
# =============================
# To avoid logging in every time, you can use your existing Chrome profile:
# 1. Find your Chrome profile folder:
#    Windows: C:/Users/[Username]/AppData/Local/Google/Chrome/User Data
#    Mac: ~/Library/Application Support/Google/Chrome
#    Linux: ~/.config/google-chrome
# 2. Set CHROME_USER_DATA_DIR to this path
# 3. Make sure Chrome is completely closed before running the script
# 4. The script will use your existing login sessions
"""
    
    with open('.env.web.template', 'w') as f:
        f.write(env_template)
    
    print("📋 Created .env.web.template file")
    print("📝 Copy this to .env and customize as needed")


def show_setup_instructions():
    """Show detailed setup instructions"""
    print("\n" + "="*60)
    print("🔧 OUTLOOK WEB AUTOMATION SETUP GUIDE")
    print("="*60)
    print("\n📦 1. INSTALL REQUIRED PACKAGES:")
    print("   pip install pandas pillow python-dotenv selenium webdriver-manager")
    print("\n📁 2. CREATE PROJECT STRUCTURE:")
    print("   email-automation/")
    print("   ├── outlook_web_automation.py")
    print("   ├── .env")
    print("   ├── employees_test_today.csv")
    print("   ├── assets/")
    print("   │   ├── Slide1.PNG (anniversary card)")
    print("   │   └── Slide2.PNG (birthday card)")
    print("   └── output/ (auto-created)")
    print("\n⚙️ 3. CONFIGURE .env FILE:")
    print("   - Copy .env.web.template to .env")
    print("   - Update file paths if needed")
    print("   - Optionally set Chrome profile for persistent login")
    print("\n🌐 4. BROWSER REQUIREMENTS:")
    print("   - Google Chrome installed")
    print("   - ChromeDriver (auto-downloaded)")
    print("   - Stable internet connection")
    print("\n🚀 5. FIRST RUN:")
    print("   python outlook_web_automation.py")
    print("\n🔐 6. LOGIN PROCESS:")
    print("   - Browser opens to outlook.live.com")
    print("   - Log in with your Microsoft account")
    print("   - Grant any necessary permissions")
    print("   - Script continues automatically")
    print("\n✨ 7. AUTOMATION FEATURES:")
    print("   - Sends personalized birthday cards")
    print("   - Sends anniversary greetings")
    print("   - Attaches custom images with names")
    print("   - Generates daily reports")
    print("   - Comprehensive logging")
    print("\n🔄 8. SCHEDULING (OPTIONAL):")
    print("   - Windows: Task Scheduler")
    print("   - Linux/Mac: Cron job")
    print("   - Run daily at desired time")
    print("\n⚠️ IMPORTANT NOTES:")
    print("   - Keep Chrome browser closed when running")
    print("   - Don't interrupt the automation process")
    print("   - Check logs for any issues")
    print("   - Test with small employee list first")
    print("="*60)


if __name__ == "__main__":
    # Uncomment one of these lines for setup help:
    
    # Create web automation configuration template
    #create_web_env_template()
    
    # Show detailed setup instructions
    #show_setup_instructions()
    
    # Run the main automation
    main()


# COMPARISON: Different Email Automation Approaches
# =================================================
# 
# 1. SMTP Version (Original):
#    ✅ Simple setup (email + password)
#    ✅ Works with any email provider
#    ❌ Requires app passwords
#    ❌ May have rate limits
#    ❌ Less secure authentication
# 
# 2. Graph API Version (Previous):
#    ✅ Official Microsoft API
#    ✅ Modern OAuth2 authentication
#    ❌ Requires Azure app registration
#    ❌ Complex setup process
#    ❌ Only works with Microsoft accounts
# 
# 3. Web Automation Version (This):
#    ✅ No Azure registration needed
#    ✅ No API keys required
#    ✅ Uses existing browser login
#    ✅ Simple setup process
#    ✅ Works with any Outlook account
#    ❌ Requires browser automation
#    ❌ Slightly slower than API calls
#    ❌ May be affected by web UI changes
# 
# RECOMMENDED FOR:
# - Personal use: Web Automation (this version)
# - Small businesses: Web Automation
# - Large enterprises: Graph API version
# - Mixed email providers: SMTP version