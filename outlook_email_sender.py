import os
import time
import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv
import logging
import pyautogui
import webbrowser
from urllib.parse import quote
import traceback

# Import the card generator
from card_generation import BirthdayAnniversaryGenerator

class OutlookEmailSender:
    """
    Handles automated email sending through Outlook using PyAutoGUI
    """
    
    def __init__(self, config=None, output_folder: str = "output"):
        """
        Initialize Outlook email sender with configuration
        
        Args:
            config: Configuration object with coordinates and timing
            output_folder: Folder to save logs
        """
        self.output_folder = output_folder
        self.config = config or self.get_default_config()
        
        # Create logs folder if it doesn't exist
        self.logs_folder = os.path.join(output_folder, "logs")
        os.makedirs(self.logs_folder, exist_ok=True)
        
        # Setup logging first
        self.setup_logging()
        
        # Setup safety features
        self.setup_safety_features()
        
        self.logger.info("OutlookEmailSender initialized")
        self.logger.info(f"Output folder: {self.output_folder}")
        self.logger.info(f"Logs folder: {self.logs_folder}")
        self.logger.info(f"Configuration: {self.config}")
        
    def setup_logging(self):
        """Setup logging for OutlookEmailSender to same file as SMTP automation"""
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
        self.logger = logging.getLogger('OutlookEmailSender')
        self.logger.setLevel(logging.INFO)
        
        # Clear existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.log_file_path = log_filename
        
    def get_default_config(self):
        """Get default configuration from environment variables"""
        config = {
            'insert_tab_coords': (178, 89),
            'picture_button_coords': (554, 156),
            'deselect_coords': (400, 300),
            'wait_time_short': 1,
            'wait_time_medium': 2,
            'wait_time_long': 3
        }
        
        # Load coordinates from environment variables if available
        insert_x = os.getenv('OUTLOOK_INSERT_TAB_X')
        insert_y = os.getenv('OUTLOOK_INSERT_TAB_Y')
        if insert_x and insert_y:
            config['insert_tab_coords'] = (int(insert_x), int(insert_y))
            
        picture_x = os.getenv('OUTLOOK_PICTURE_BUTTON_X')
        picture_y = os.getenv('OUTLOOK_PICTURE_BUTTON_Y')
        if picture_x and picture_y:
            config['picture_button_coords'] = (int(picture_x), int(picture_y))
            
        deselect_x = os.getenv('OUTLOOK_DESELECT_X')
        deselect_y = os.getenv('OUTLOOK_DESELECT_Y')
        if deselect_x and deselect_y:
            config['deselect_coords'] = (int(deselect_x), int(deselect_y))
        
        return config
    
    def setup_safety_features(self):
        """Enable PyAutoGUI safety features"""
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        self.logger.info("PyAutoGUI safety features enabled - FAILSAFE: True, PAUSE: 0.5s")
        self.logger.info("Safety tip: Move mouse to top-left corner to stop automation")
    
    def log_error(self, error_msg: str, exception: Optional[Exception] = None):
        """Log error with detailed information"""
        if exception:
            full_error = f"{error_msg}: {str(exception)}\n{traceback.format_exc()}"
        else:
            full_error = error_msg
            
        self.logger.error(full_error)
    
    def open_outlook_mailto(self, recipient: str, subject: str, body: str = ""):
        """
        Opens Outlook using mailto protocol
        
        Args:
            recipient: Email address of the recipient
            subject: Subject line of the email
            body: Body content of the email (optional)
        """
        try:
            self.logger.info(f"Opening Outlook mailto for recipient: {recipient}")
            self.logger.info(f"Subject: {subject}")
            
            # URL encode the parameters
            encoded_subject = quote(subject)
            encoded_body = quote(body) if body else ""
            
            # Construct the mailto URL
            if body:
                mailto_url = f"mailto:{recipient}?subject={encoded_subject}&body={encoded_body}"
                self.logger.info("Mailto URL constructed with body content")
            else:
                mailto_url = f"mailto:{recipient}?subject={encoded_subject}"
                self.logger.info("Mailto URL constructed without body content")
            
            # Open the mailto URL
            webbrowser.open(mailto_url)
            self.logger.info(f"Mailto URL opened successfully for {recipient}")
            
            # Wait for Outlook to open
            wait_time = self.config['wait_time_long']
            self.logger.info(f"Waiting {wait_time} seconds for Outlook to open...")
            time.sleep(wait_time)
            self.logger.info("Outlook should now be open and ready")
            
        except Exception as e:
            self.log_error(f"Error opening Outlook for {recipient}", e)
            raise
    
    def maximize_window(self):
        """Maximizes the current window"""
        try:
            self.logger.info("Attempting to maximize Outlook window")
            pyautogui.hotkey('win', 'up')
            
            wait_time = self.config['wait_time_short']
            time.sleep(wait_time)
            self.logger.info(f"Window maximized successfully (waited {wait_time}s)")
            
        except Exception as e:
            self.log_error("Error maximizing window", e)
            raise
    
    def click_insert_tab(self):
        """Clicks on the Insert tab"""
        try:
            x, y = self.config['insert_tab_coords']
            self.logger.info(f"Clicking Insert tab at coordinates ({x}, {y})")
            
            pyautogui.click(x, y)
            
            wait_time = self.config['wait_time_short']
            time.sleep(wait_time)
            self.logger.info(f"Insert tab clicked successfully (waited {wait_time}s)")
            
        except Exception as e:
            self.log_error(f"Error clicking Insert tab at {self.config['insert_tab_coords']}", e)
            raise
    
    def click_picture_button(self):
        """Clicks on the Picture button"""
        try:
            x, y = self.config['picture_button_coords']
            self.logger.info(f"Clicking Picture button at coordinates ({x}, {y})")
            
            pyautogui.click(x, y)
            
            wait_time = self.config['wait_time_medium']
            time.sleep(wait_time)
            self.logger.info(f"Picture button clicked successfully (waited {wait_time}s)")
            
        except Exception as e:
            self.log_error(f"Error clicking Picture button at {self.config['picture_button_coords']}", e)
            raise
    
    def insert_image_from_dialog(self, image_path: str):
        """
        Inserts an image from the file dialog
        
        Args:
            image_path: Full path to the image file
        """
        try:
            # Convert relative path to absolute path
            abs_image_path = os.path.abspath(image_path)
            self.logger.info(f"Inserting image from path: {abs_image_path}")
            
            # Verify file exists
            if not os.path.exists(abs_image_path):
                raise FileNotFoundError(f"Image file not found: {abs_image_path}")
            
            # Type the file path
            self.logger.info("Typing file path in dialog")
            pyautogui.typewrite(abs_image_path)
            
            wait_time = self.config['wait_time_short']
            time.sleep(wait_time)
            self.logger.info(f"File path typed (waited {wait_time}s)")
            
            # Press Enter to select the file
            self.logger.info("Pressing Enter to select file")
            pyautogui.press('enter')
            
            wait_time = self.config['wait_time_medium']
            time.sleep(wait_time)
            self.logger.info(f"Image inserted successfully: {abs_image_path} (waited {wait_time}s)")
            
        except Exception as e:
            self.log_error(f"Error inserting image: {image_path}", e)
            raise
    
    def deselect_image(self):
        """Deselects the currently selected image"""
        try:
            x, y = self.config['deselect_coords']
            self.logger.info(f"Deselecting image by clicking at coordinates ({x}, {y})")
            
            pyautogui.click(x, y)
            
            wait_time = self.config['wait_time_short']
            time.sleep(wait_time)
            self.logger.info(f"Image deselected successfully (waited {wait_time}s)")
            
        except Exception as e:
            self.log_error(f"Error deselecting image at {self.config['deselect_coords']}", e)
            raise
    
    def send_email(self):
        """Sends the email using Ctrl+Enter shortcut"""
        try:
            self.logger.info("Sending email using Ctrl+Enter shortcut")
            pyautogui.hotkey('ctrl', 'enter')
            
            wait_time = self.config['wait_time_short']
            time.sleep(wait_time)
            self.logger.info(f"Email sent successfully using keyboard shortcut (waited {wait_time}s)")
            
        except Exception as e:
            self.log_error("Error sending email with keyboard shortcut", e)
            raise
    
    def send_email_with_image(self, recipient: str, subject: str, image_path: str, body: str = ""):
        """
        Complete automation to send an email with an image
        
        Args:
            recipient: Email address of the recipient
            subject: Subject line of the email
            image_path: Full path to the image file
            body: Body content of the email (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        automation_start_time = datetime.datetime.now()
        
        try:
            self.logger.info("=" * 60)
            self.logger.info(f"Starting email automation for {recipient}")
            self.logger.info(f"Subject: {subject}")
            self.logger.info(f"Image path: {image_path}")
            self.logger.info(f"Body: {body[:50]}..." if body else "Body: (empty)")
            self.logger.info("=" * 60)
            
            # Step 1: Open Outlook with mailto
            self.logger.info("STEP 1: Opening Outlook with mailto")
            self.open_outlook_mailto(recipient, subject, body)
            
            # Step 2: Maximize window
            self.logger.info("STEP 2: Maximizing Outlook window")
            self.maximize_window()
            
            # Step 3: Click Insert tab
            self.logger.info("STEP 3: Clicking Insert tab")
            self.click_insert_tab()
            
            # Step 4: Click Picture button
            self.logger.info("STEP 4: Clicking Picture button")
            self.click_picture_button()
            
            # Step 5: Insert image
            self.logger.info("STEP 5: Inserting image from dialog")
            self.insert_image_from_dialog(image_path)
            
            # Step 6: Deselect image
            self.logger.info("STEP 6: Deselecting image")
            self.deselect_image()
            
            # Step 7: Send email
            self.logger.info("STEP 7: Sending email")
            self.send_email()
            
            automation_end_time = datetime.datetime.now()
            duration = automation_end_time - automation_start_time
            
            self.logger.info("=" * 60)
            self.logger.info(f"Email automation COMPLETED SUCCESSFULLY for {recipient}")
            self.logger.info(f"Total automation duration: {duration}")
            self.logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            automation_end_time = datetime.datetime.now()
            duration = automation_end_time - automation_start_time
            
            self.log_error(f"Email automation FAILED for {recipient} after {duration}", e)
            self.logger.error("=" * 60)
            self.logger.error(f"AUTOMATION FAILED for {recipient}")
            self.logger.error(f"Duration before failure: {duration}")
            self.logger.error("=" * 60)
            
            return False


class IntegratedEmailAutomation:
    """
    Integrated system that combines card generation with email sending
    """
    
    def __init__(self, output_folder: str = "output"):
        """
        Initialize the integrated email automation system
        
        Args:
            output_folder: Folder to save generated cards and logs
        """
        # Load environment variables
        load_dotenv()
        
        self.output_folder = output_folder
        
        # Create logs folder
        self.logs_folder = os.path.join(output_folder, "logs")
        os.makedirs(self.logs_folder, exist_ok=True)
        
        # Setup logging first
        self.setup_logging()
        
        # Initialize components
        self.card_generator = BirthdayAnniversaryGenerator(output_folder)
        self.email_sender = OutlookEmailSender(output_folder=output_folder)
        
        # Track statistics
        self.stats = {
            'birthday_emails_sent': 0,
            'anniversary_emails_sent': 0,
            'birthday_emails_failed': 0,
            'anniversary_emails_failed': 0,
            'birthday_cards_generated': 0,
            'anniversary_cards_generated': 0,
            'total_cards_generated': 0,
            'errors': [],
            'birthdays_today': [],
            'anniversaries_today': [],
            'start_time': datetime.datetime.now(),
            'end_time': None
        }
        
        self.logger.info("IntegratedEmailAutomation system initialized")
        self.logger.info(f"Output folder: {self.output_folder}")
        self.logger.info(f"Logs folder: {self.logs_folder}")
    
    def setup_logging(self):
        """Setup logging for the integrated system to same file"""
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
        self.logger = logging.getLogger('IntegratedAutomation')
        self.logger.setLevel(logging.INFO)
        
        # Clear existing handlers
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
    
    def process_and_send_birthday_emails(self, birthdays: List[Dict], birthday_cards: List[str]):
        """
        Send birthday emails with generated cards
        
        Args:
            birthdays: List of birthday information
            birthday_cards: List of paths to generated birthday cards
        """
        self.logger.info(f"Processing {len(birthdays)} birthday emails")
        
        for i, (birthday_info, card_path) in enumerate(zip(birthdays, birthday_cards)):
            try:
                recipient = birthday_info['email']
                first_name = birthday_info['first_name']
                last_name = birthday_info['last_name']
                age = birthday_info['age']
                subject = f"Happy Birthday, {first_name}! 🎉"
                
                self.logger.info(f"Processing birthday email {i+1}/{len(birthdays)} for {first_name} {last_name} (age {age})")
                
                # Verify card file exists
                if not os.path.exists(card_path):
                    self.log_error(f"Birthday card file not found: {card_path}")
                    self.stats['birthday_emails_failed'] += 1
                    continue
                
                # Send email with card
                self.logger.info(f"Sending birthday email to {first_name} {last_name} ({recipient})")
                success = self.email_sender.send_email_with_image(
                    recipient=recipient,
                    subject=subject,
                    image_path=card_path,
                    body=""
                )
                
                if success:
                    self.stats['birthday_emails_sent'] += 1
                    self.logger.info(f"Birthday email sent successfully to {first_name} {last_name}")
                    
                    # Add to stats
                    self.stats['birthdays_today'].append({
                        'name': f"{first_name} {last_name}",
                        'email': recipient,
                        'age': age
                    })
                else:
                    self.stats['birthday_emails_failed'] += 1
                    self.log_error(f"Failed to send birthday email to {first_name} {last_name}")
                
                # Wait between emails to avoid overwhelming the system
                if i < len(birthdays) - 1:  # Don't wait after the last email
                    wait_time = 5
                    self.logger.info(f"Waiting {wait_time} seconds before next email...")
                    time.sleep(wait_time)
                    
            except Exception as e:
                self.stats['birthday_emails_failed'] += 1
                self.log_error(f"Error sending birthday email to {birthday_info.get('first_name', 'Unknown')}", e)
    
    def process_and_send_anniversary_emails(self, anniversaries: List[Dict], anniversary_cards: List[str]):
        """
        Send anniversary emails with generated cards
        
        Args:
            anniversaries: List of anniversary information
            anniversary_cards: List of paths to generated anniversary cards
        """
        self.logger.info(f"Processing {len(anniversaries)} anniversary emails")
        
        for i, (anniversary_info, card_path) in enumerate(zip(anniversaries, anniversary_cards)):
            try:
                recipient = anniversary_info['email']
                first_name = anniversary_info['first_name']
                last_name = anniversary_info['last_name']
                years = anniversary_info['years']
                subject = f"Happy Anniversary, {first_name}! 💕"
                
                self.logger.info(f"Processing anniversary email {i+1}/{len(anniversaries)} for {first_name} {last_name} ({years} years)")
                
                # Verify card file exists
                if not os.path.exists(card_path):
                    self.log_error(f"Anniversary card file not found: {card_path}")
                    self.stats['anniversary_emails_failed'] += 1
                    continue
                
                # Send email with card
                self.logger.info(f"Sending anniversary email to {first_name} {last_name} ({recipient})")
                success = self.email_sender.send_email_with_image(
                    recipient=recipient,
                    subject=subject,
                    image_path=card_path,
                    body=""
                )
                
                if success:
                    self.stats['anniversary_emails_sent'] += 1
                    self.logger.info(f"Anniversary email sent successfully to {first_name} {last_name} ({years} years)")
                    
                    # Add to stats
                    self.stats['anniversaries_today'].append({
                        'name': f"{first_name} {last_name}",
                        'email': recipient,
                        'years': years
                    })
                else:
                    self.stats['anniversary_emails_failed'] += 1
                    self.log_error(f"Failed to send anniversary email to {first_name} {last_name}")
                
                # Wait between emails
                if i < len(anniversaries) - 1:  # Don't wait after the last email
                    wait_time = 5
                    self.logger.info(f"Waiting {wait_time} seconds before next email...")
                    time.sleep(wait_time)
                    
            except Exception as e:
                self.stats['anniversary_emails_failed'] += 1
                self.log_error(f"Error sending anniversary email to {anniversary_info.get('first_name', 'Unknown')}", e)
    
    def create_summary_report(self) -> str:
        """Create a summary report of the day's activities"""
        self.stats['end_time'] = datetime.datetime.now()
        duration = self.stats['end_time'] - self.stats['start_time']
        
        report = f"""
Daily Outlook Email Automation Report - {datetime.date.today().strftime('%B %d, %Y')}
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
- Total Cards Generated: {self.stats['total_cards_generated']}
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
        
        return report
    
    def save_daily_report(self):
        """Save daily report to file"""
        try:
            self.logger.info("Generating daily report")
            report = self.create_summary_report()
            
            # Save report to file
            report_filename = os.path.join(self.output_folder, f"outlook_daily_report_{datetime.date.today().strftime('%Y%m%d')}.txt")
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            self.logger.info(f"Daily report saved to: {report_filename}")
            
            # Log the summary to the log file as well
            self.logger.info("=== DAILY SUMMARY ===")
            for line in report.strip().split('\n'):
                if line.strip():
                    self.logger.info(line)
            self.logger.info("=== END DAILY SUMMARY ===")
                
        except Exception as e:
            self.log_error("Error creating daily report", e)
    
    def run_complete_automation(self):
        """
        Run the complete automation process:
        1. Generate cards for today's birthdays and anniversaries
        2. Send emails with the generated cards
        """
        try:
            self.logger.info("=" * 80)
            self.logger.info("STARTING COMPLETE OUTLOOK EMAIL AUTOMATION PROCESS")
            self.logger.info("=" * 80)
            
            # Load configuration from environment variables
            csv_file = os.getenv('CSV_FILE', 'employees_test_today.csv')
            birthday_card_path = os.getenv('BIRTHDAY_CARD', 'assets\\Slide2.PNG')
            anniversary_card_path = os.getenv('ANNIVERSARY_CARD', 'assets\\Slide1.PNG')
            
            self.logger.info(f"CSV file: {csv_file}")
            self.logger.info(f"Birthday card template: {birthday_card_path}")
            self.logger.info(f"Anniversary card template: {anniversary_card_path}")
            
            # Birthday configuration
            birthday_text_x = int(os.getenv('BIRTHDAY_TEXT_X', '50'))
            birthday_text_y = int(os.getenv('BIRTHDAY_TEXT_Y', '300'))
            birthday_font_size = int(os.getenv('BIRTHDAY_FONT_SIZE', '64'))
            birthday_font_color = os.getenv('BIRTHDAY_FONT_COLOR', '#4b446a')
            birthday_font_path = os.getenv('BIRTHDAY_FONT_PATH', 'fonts/Inkfree.ttf')
            birthday_center_align = os.getenv('BIRTHDAY_CENTER_ALIGN', 'false').lower() == 'true'
            
            # Anniversary configuration
            anniversary_text_x = int(os.getenv('ANNIVERSARY_TEXT_X', '0'))
            anniversary_text_y = int(os.getenv('ANNIVERSARY_TEXT_Y', '200'))
            anniversary_font_size = int(os.getenv('ANNIVERSARY_FONT_SIZE', '72'))
            anniversary_font_color = os.getenv('ANNIVERSARY_FONT_COLOR', '#72719f')
            anniversary_font_path = os.getenv('ANNIVERSARY_FONT_PATH', 'C:/Windows/Fonts/HTOWERT.TTF')
            anniversary_center_align = os.getenv('ANNIVERSARY_CENTER_ALIGN', 'true').lower() == 'true'
            
            self.logger.info(f"Birthday config: pos=({birthday_text_x},{birthday_text_y}), size={birthday_font_size}, color={birthday_font_color}, center={birthday_center_align}")
            self.logger.info(f"Anniversary config: pos=({anniversary_text_x},{anniversary_text_y}), size={anniversary_font_size}, color={anniversary_font_color}, center={anniversary_center_align}")
            
            # Step 1: Generate cards
            self.logger.info("STEP 1: Generating birthday and anniversary cards")
            result = self.card_generator.process_daily_cards(
                csv_file=csv_file,
                birthday_card_path=birthday_card_path,
                anniversary_card_path=anniversary_card_path,
                birthday_text_pos=(birthday_text_x, birthday_text_y),
                anniversary_text_pos=(anniversary_text_x, anniversary_text_y),
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
            self.stats['total_cards_generated'] = self.stats['birthday_cards_generated'] + self.stats['anniversary_cards_generated']
            
            self.logger.info(f"Cards generated successfully:")
            self.logger.info(f"  - Birthday cards: {self.stats['birthday_cards_generated']}")
            self.logger.info(f"  - Anniversary cards: {self.stats['anniversary_cards_generated']}")
            self.logger.info(f"  - Total cards: {self.stats['total_cards_generated']}")
            
            # Step 2: Send birthday emails
            if result['birthday_cards_created']:
                self.logger.info("STEP 2: Sending birthday emails")
                self.process_and_send_birthday_emails(
                    result['birthdays_today'], 
                    result['birthday_cards_created']
                )
            else:
                self.logger.info("STEP 2: No birthday emails to send today")
            
            # Step 3: Send anniversary emails
            if result['anniversary_cards_created']:
                self.logger.info("STEP 3: Sending anniversary emails")
                self.process_and_send_anniversary_emails(
                    result['anniversaries_today'], 
                    result['anniversary_cards_created']
                )
            else:
                self.logger.info("STEP 3: No anniversary emails to send today")
            
            # Step 4: Generate daily report
            self.logger.info("STEP 4: Generating daily report")
            self.save_daily_report()
            
            # Final statistics
            self.stats['end_time'] = datetime.datetime.now()
            duration = self.stats['end_time'] - self.stats['start_time']
            
            self.logger.info("=" * 80)
            self.logger.info("OUTLOOK EMAIL AUTOMATION COMPLETE")
            self.logger.info("=" * 80)
            self.logger.info(f"Duration: {duration}")
            self.logger.info(f"Total cards generated: {self.stats['total_cards_generated']}")
            self.logger.info(f"Birthday emails sent: {self.stats['birthday_emails_sent']}")
            self.logger.info(f"Anniversary emails sent: {self.stats['anniversary_emails_sent']}")
            self.logger.info(f"Total emails sent: {self.stats['birthday_emails_sent'] + self.stats['anniversary_emails_sent']}")
            self.logger.info(f"Failed emails: {self.stats['birthday_emails_failed'] + self.stats['anniversary_emails_failed']}")
            self.logger.info(f"Total errors: {len(self.stats['errors'])}")
            self.logger.info("=" * 80)
            
            return True
            
        except Exception as e:
            self.log_error("Critical error in complete automation", e)
            # Still try to save a report even if there was a critical error
            try:
                self.save_daily_report()
            except:
                pass
            return False


def create_env_template():
    """Create a template .env file for Outlook automation configuration"""
    env_template = """# Outlook Email Automation Configuration
# Copy this file to .env and update with your settings

# File Paths
OUTPUT_FOLDER=output
CSV_FILE=employees_test_today.csv
BIRTHDAY_CARD=assets\\Slide2.PNG
ANNIVERSARY_CARD=assets\\Slide1.PNG

# OUTLOOK AUTOMATION COORDINATES
# ==============================
# These coordinates may need adjustment based on your screen resolution
# and Outlook version. Default values are for 1920x1080 resolution.

# Insert Tab Coordinates (where to click "Insert" in Outlook ribbon)
OUTLOOK_INSERT_TAB_X=178
OUTLOOK_INSERT_TAB_Y=89

# Picture Button Coordinates (where to click "Picture" in Insert tab)
OUTLOOK_PICTURE_BUTTON_X=554
OUTLOOK_PICTURE_BUTTON_Y=156

# Deselect Coordinates (where to click to deselect image after insertion)
OUTLOOK_DESELECT_X=400
OUTLOOK_DESELECT_Y=300

# BIRTHDAY CARD CUSTOMIZATION (1280x720)
# =======================================
BIRTHDAY_TEXT_X=50
BIRTHDAY_TEXT_Y=300
BIRTHDAY_FONT_SIZE=64
BIRTHDAY_FONT_COLOR=#4b446a
BIRTHDAY_FONT_PATH=fonts/Inkfree.ttf
BIRTHDAY_CENTER_ALIGN=false

# ANNIVERSARY CARD CUSTOMIZATION (1280x720)
# ==========================================
ANNIVERSARY_TEXT_X=0
ANNIVERSARY_TEXT_Y=200
ANNIVERSARY_FONT_SIZE=72
ANNIVERSARY_FONT_COLOR=#72719f
ANNIVERSARY_FONT_PATH=C:/Windows/Fonts/HTOWERT.TTF
ANNIVERSARY_CENTER_ALIGN=true

# COORDINATE CALIBRATION GUIDE:
# =============================
# If automation fails, you may need to adjust coordinates:
# 
# 1. Take a screenshot of Outlook with email composition window open
# 2. Use image editing software to find pixel coordinates
# 3. Update the coordinates above
# 
# Common screen resolutions and typical adjustments:
# - 1920x1080: Use default values above
# - 1366x768: Reduce all coordinates by ~25%
# - 2560x1440: Increase all coordinates by ~30%
# - 4K (3840x2160): Double all coordinates
#
# Tips for finding coordinates:
# - Insert Tab: Usually in the top ribbon, second or third tab
# - Picture Button: In Insert tab, usually in "Illustrations" group
# - Deselect Area: Click in email body area, away from image

# LOGGING:
# ========
# All logs will be saved to: {OUTPUT_FOLDER}/logs/email_log.log
# Daily reports will be saved to: {OUTPUT_FOLDER}/outlook_daily_report_YYYYMMDD.txt
# Generated cards will be saved to: {OUTPUT_FOLDER}/
"""
    
    with open('.env.outlook_template', 'w') as f:
        f.write(env_template)
    
    print("📋 Created .env.outlook_template file for Outlook Email Automation")
    print("📝 Copy this to .env and update with your settings")


def main():
    """
    Main function to run the integrated Outlook email automation
    """
    print("🚀 Starting Integrated Outlook Birthday & Anniversary Email Automation")
    print("=" * 70)
    
    # Load environment variables
    load_dotenv()
    
    # Configuration summary
    print("📋 Configuration Summary:")
    print(f"   📊 CSV File: {os.getenv('CSV_FILE', 'employees_test_today.csv')}")
    print(f"   🎂 Birthday Template: {os.getenv('BIRTHDAY_CARD', 'assets\\Slide2.PNG')}")
    print(f"   💕 Anniversary Template: {os.getenv('ANNIVERSARY_CARD', 'assets\\Slide1.PNG')}")
    print(f"   📁 Output Folder: {os.getenv('OUTPUT_FOLDER', 'output')}")
    print(f"   🖱️ Insert Tab: ({os.getenv('OUTLOOK_INSERT_TAB_X', '178')}, {os.getenv('OUTLOOK_INSERT_TAB_Y', '89')})")
    print(f"   🖱️ Picture Button: ({os.getenv('OUTLOOK_PICTURE_BUTTON_X', '554')}, {os.getenv('OUTLOOK_PICTURE_BUTTON_Y', '156')})")
    print(f"   📁 Logs: output/logs/email_log.log")
    print()
    
    # Safety warning
    print("⚠️  SAFETY NOTICE:")
    print("   • PyAutoGUI failsafe is enabled")
    print("   • Move mouse to top-left corner to stop automation")
    print("   • Make sure Outlook is installed and configured")
    print("   • Close other applications for best results")
    print("   • Ensure screen resolution matches coordinate settings")
    print()
    
    # Coordinate verification
    print("🎯 COORDINATE VERIFICATION:")
    print("   • If automation clicks wrong places, adjust coordinates in .env")
    print("   • Use .env.outlook_template as reference")
    print("   • Test with one email first before bulk processing")
    print()
    
    # Countdown
    print("🕒 Starting automation in:")
    for i in range(5, 0, -1):
        print(f"   {i}...")
        time.sleep(1)
    print("   🚀 GO!")
    print()
    
    # Initialize and run automation
    try:
        automation = IntegratedEmailAutomation(
            output_folder=os.getenv('OUTPUT_FOLDER', 'output')
        )
        
        success = automation.run_complete_automation()
        
        if success:
            print("✅ Outlook automation completed successfully!")
            print(f"📊 Check logs at: output/logs/email_log.log")
            print(f"📋 Check report at: output/outlook_daily_report_{datetime.date.today().strftime('%Y%m%d')}.txt")
        else:
            print("❌ Outlook automation completed with errors. Check logs for details.")
            
    except KeyboardInterrupt:
        print("\n⚠️  Automation stopped by user")
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()


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

# TROUBLESHOOTING GUIDE:
"""
1. COORDINATE ISSUES:
   - If clicks are in wrong places, adjust coordinates in .env file
   - Use screenshot tools to find exact pixel coordinates
   - Test with different screen resolutions
   
2. OUTLOOK NOT OPENING:
   - Ensure Outlook is set as default email client
   - Check if Outlook is already running
   - Verify mailto protocol is properly configured
   
3. IMAGE INSERTION FAILS:
   - Check if image files exist at specified paths
   - Ensure file permissions allow reading
   - Verify image file formats are supported
   
4. EMAIL NOT SENDING:
   - Check if Ctrl+Enter shortcut is enabled in Outlook
   - Ensure Outlook account is properly configured
   - Verify network connectivity
   
5. AUTOMATION STOPS UNEXPECTEDLY:
   - Check PyAutoGUI failsafe (mouse in top-left corner)
   - Review logs for specific error messages
   - Ensure no dialog boxes are blocking automation
"""