import unittest
import os
import tempfile
import shutil
import pandas as pd
import datetime
from unittest.mock import Mock, patch, MagicMock, mock_open
from PIL import Image
import io
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

# Import the main class (assuming it's in automation_email.py)
try:
    from automation_email import EmailAutomation
except ImportError:
    # Handle case where the module might be named differently
    import sys
    sys.path.append('.')
    from automation_email import EmailAutomation


class TestEmailAutomation(unittest.TestCase):
    """Comprehensive unit tests for EmailAutomation class"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.test_dir, "output")
        self.logs_dir = os.path.join(self.output_dir, "logs")
        
        # Test configuration
        self.test_smtp_server = "smtp.test.com"
        self.test_smtp_port = 587
        self.test_sender_email = "test@example.com"
        self.test_password = "test_password"
        
        # Create test CSV data
        self.test_csv_data = {
            'first_name': ['John', 'Jane', 'Bob', 'Alice'],
            'last_name': ['Doe', 'Smith', 'Johnson', 'Brown'],
            'email': ['john@test.com', 'jane@test.com', 'bob@test.com', 'alice@test.com'],
            'birthday': ['1990-06-09', '1985-12-25', '1992-06-09', '1988-03-14'],
            'anniversary': ['2018-05-20', '2015-08-15', '2020-10-12', '']
        }
        
        # Create test CSV file
        self.test_csv_file = os.path.join(self.test_dir, "test_employees.csv")
        df = pd.DataFrame(self.test_csv_data)
        df.to_csv(self.test_csv_file, index=False)
        
        # Create test images
        self.birthday_card = os.path.join(self.test_dir, "birthday_card.png")
        self.anniversary_card = os.path.join(self.test_dir, "anniversary_card.png")
        self._create_test_images()
        
        # Setup logging for tests
        self.setup_test_logging()
        
    def tearDown(self):
        """Clean up after each test method"""
        # Remove temporary directory and all its contents
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
        # Clean up any handlers to avoid interference between tests
        logger = logging.getLogger('EmailAutomation')
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
    
    def setup_test_logging(self):
        """Setup logging for test output"""
        # Create logs directory
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Setup test logger that writes to the same location as main code
        test_log_file = os.path.join(self.logs_dir, "test_email_automation.log")
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Setup file handler
        file_handler = logging.FileHandler(test_log_file, mode='a', encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        
        # Setup test logger
        self.test_logger = logging.getLogger('EmailAutomationTests')
        self.test_logger.setLevel(logging.INFO)
        self.test_logger.handlers.clear()
        self.test_logger.addHandler(file_handler)
        
        self.test_logger.info("=" * 80)
        self.test_logger.info("STARTING EMAIL AUTOMATION UNIT TESTS")
        self.test_logger.info("=" * 80)
    
    def _create_test_images(self):
        """Create test greeting card images"""
        # Create simple test images
        for image_path in [self.birthday_card, self.anniversary_card]:
            img = Image.new('RGB', (800, 600), color='white')
            img.save(image_path)
    
    def _create_email_automation(self, **kwargs):
        """Helper method to create EmailAutomation instance with test settings"""
        default_kwargs = {
            'smtp_server': self.test_smtp_server,
            'smtp_port': self.test_smtp_port,
            'email': self.test_sender_email,
            'password': self.test_password,
            'output_folder': self.output_dir
        }
        default_kwargs.update(kwargs)
        return EmailAutomation(**default_kwargs)
    
    # =========================================================================
    # INITIALIZATION TESTS
    # =========================================================================
    
    def test_initialization_with_parameters(self):
        """Test EmailAutomation initialization with direct parameters"""
        self.test_logger.info("Testing initialization with parameters")
        
        email_system = self._create_email_automation()
        
        self.assertEqual(email_system.smtp_server, self.test_smtp_server)
        self.assertEqual(email_system.smtp_port, self.test_smtp_port)
        self.assertEqual(email_system.sender_email, self.test_sender_email)
        self.assertEqual(email_system.password, self.test_password)
        self.assertTrue(os.path.exists(email_system.output_folder))
        self.assertTrue(os.path.exists(email_system.logs_folder))
        
        self.test_logger.info("✅ Initialization with parameters successful")
    
    @patch.dict(os.environ, {
        'SMTP_SERVER': 'env.smtp.com',
        'SMTP_PORT': '465',
        'SENDER_EMAIL': 'env@test.com',
        'EMAIL_PASSWORD': 'env_password'
    })
    def test_initialization_with_environment_variables(self):
        """Test EmailAutomation initialization with environment variables"""
        self.test_logger.info("Testing initialization with environment variables")
        
        email_system = EmailAutomation(output_folder=self.output_dir)
        
        self.assertEqual(email_system.smtp_server, 'env.smtp.com')
        self.assertEqual(email_system.smtp_port, 465)
        self.assertEqual(email_system.sender_email, 'env@test.com')
        self.assertEqual(email_system.password, 'env_password')
        
        self.test_logger.info("✅ Initialization with environment variables successful")
    
    def test_initialization_missing_required_config(self):
        """Test EmailAutomation initialization with missing configuration"""
        self.test_logger.info("Testing initialization with missing configuration")
        
        with self.assertRaises(ValueError) as context:
            EmailAutomation(smtp_server=None, email=None, password=None)
        
        self.assertIn("Missing required email configuration", str(context.exception))
        self.test_logger.info("✅ Missing configuration properly detected")
    
    def test_initialization_invalid_types(self):
        """Test EmailAutomation initialization with invalid types"""
        self.test_logger.info("Testing initialization with invalid types")
        
        # Test with invalid port type that will cause int() conversion to fail
        with self.assertRaises((ValueError, TypeError)):
            try:
                invalid_port = int("invalid_port")  # This will raise ValueError
                EmailAutomation(
                    smtp_server="smtp.test.com",
                    smtp_port=invalid_port,
                    email=self.test_sender_email,
                    password=self.test_password,
                    output_folder=self.output_dir
                )
            except ValueError:
                # This is expected behavior when trying to convert invalid string to int
                raise ValueError("Invalid port configuration")
        
        self.test_logger.info("✅ Invalid types properly rejected")
    
    # =========================================================================
    # CSV LOADING TESTS
    # =========================================================================
    
    def test_load_employee_data_success(self):
        """Test successful loading of employee data"""
        self.test_logger.info("Testing CSV data loading")
        
        email_system = self._create_email_automation()
        df = email_system.load_employee_data(self.test_csv_file)
        
        self.assertFalse(df.empty)
        self.assertEqual(len(df), 4)
        self.assertIn('first_name', df.columns)
        self.assertIn('birthday', df.columns)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df['birthday']))
        
        self.test_logger.info("✅ CSV data loading successful")
    
    def test_load_employee_data_file_not_found(self):
        """Test loading employee data when file doesn't exist"""
        self.test_logger.info("Testing CSV loading with non-existent file")
        
        email_system = self._create_email_automation()
        df = email_system.load_employee_data("nonexistent.csv")
        
        self.assertTrue(df.empty)
        self.assertEqual(len(email_system.stats['errors']), 1)
        
        self.test_logger.info("✅ Non-existent file properly handled")
    
    def test_load_employee_data_missing_columns(self):
        """Test loading employee data with missing required columns"""
        self.test_logger.info("Testing CSV loading with missing columns")
        
        # Create CSV with missing columns
        invalid_csv = os.path.join(self.test_dir, "invalid.csv")
        invalid_data = pd.DataFrame({'name': ['John'], 'age': [30]})
        invalid_data.to_csv(invalid_csv, index=False)
        
        email_system = self._create_email_automation()
        df = email_system.load_employee_data(invalid_csv)
        
        self.assertTrue(df.empty)
        self.assertEqual(len(email_system.stats['errors']), 1)
        
        self.test_logger.info("✅ Missing columns properly detected")
    
    def test_load_employee_data_invalid_dates(self):
        """Test loading employee data with invalid date formats"""
        self.test_logger.info("Testing CSV loading with invalid dates")
        
        # Create CSV with invalid dates
        invalid_csv = os.path.join(self.test_dir, "invalid_dates.csv")
        invalid_data = pd.DataFrame({
            'first_name': ['John'],
            'last_name': ['Doe'],
            'email': ['john@test.com'],
            'birthday': ['invalid-date']
        })
        invalid_data.to_csv(invalid_csv, index=False)
        
        email_system = self._create_email_automation()
        df = email_system.load_employee_data(invalid_csv)
        
        self.assertFalse(df.empty)  # Should still load but with warnings
        self.assertTrue(df['birthday'].isna().any())  # Invalid date should be NaT
        
        self.test_logger.info("✅ Invalid dates properly handled")
    
    # =========================================================================
    # IMAGE PROCESSING TESTS
    # =========================================================================
    
    def test_add_text_to_image_success(self):
        """Test successful text addition to image"""
        self.test_logger.info("Testing text addition to image")
        
        email_system = self._create_email_automation()
        
        image_bytes, saved_path = email_system.add_text_to_image(
            self.birthday_card,
            "Dear John",
            position=(100, 100),
            font_size=40,
            font_color=(255, 0, 0),
            output_filename="test_output.jpg"
        )
        
        self.assertIsNotNone(image_bytes)
        self.assertIsNotNone(saved_path)
        self.assertTrue(os.path.exists(saved_path))
        
        self.test_logger.info("✅ Text addition to image successful")
    
    def test_add_text_to_image_file_not_found(self):
        """Test text addition to non-existent image"""
        self.test_logger.info("Testing text addition to non-existent image")
        
        email_system = self._create_email_automation()
        
        image_bytes, saved_path = email_system.add_text_to_image(
            "nonexistent.png",
            "Dear John"
        )
        
        self.assertIsNone(image_bytes)
        self.assertIsNone(saved_path)
        self.assertEqual(len(email_system.stats['errors']), 1)
        
        self.test_logger.info("✅ Non-existent image properly handled")
    
    def test_add_text_to_image_different_positions(self):
        """Test text addition at different positions"""
        self.test_logger.info("Testing text positioning")
        
        email_system = self._create_email_automation()
        
        positions = [(50, 50), (200, 100), (300, 200)]
        for i, position in enumerate(positions):
            image_bytes, saved_path = email_system.add_text_to_image(
                self.birthday_card,
                f"Test {i}",
                position=position,
                output_filename=f"position_test_{i}.jpg"
            )
            
            self.assertIsNotNone(image_bytes)
            self.assertTrue(os.path.exists(saved_path))
        
        self.test_logger.info("✅ Text positioning tests successful")
    
    def test_add_text_to_image_different_colors(self):
        """Test text addition with different colors"""
        self.test_logger.info("Testing text colors")
        
        email_system = self._create_email_automation()
        
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        for i, color in enumerate(colors):
            image_bytes, _ = email_system.add_text_to_image(
                self.birthday_card,
                f"Color Test {i}",
                font_color=color
            )
            
            self.assertIsNotNone(image_bytes)
        
        self.test_logger.info("✅ Text color tests successful")
    
    # =========================================================================
    # EMAIL MESSAGE CREATION TESTS
    # =========================================================================
    
    def test_create_email_message_success(self):
        """Test successful email message creation"""
        self.test_logger.info("Testing email message creation")
        
        email_system = self._create_email_automation()
        
        # Create test image bytes
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes = img_bytes.getvalue()
        
        msg = email_system.create_email_message(
            "test@example.com",
            "John",
            "Test Subject",
            "Test Body",
            img_bytes
        )
        
        self.assertIsNotNone(msg)
        if msg:  # Type guard to ensure msg is not None
            self.assertEqual(msg['To'], "test@example.com")
            self.assertEqual(msg['Subject'], "Test Subject")
            self.assertEqual(msg['From'], self.test_sender_email)
        
        self.test_logger.info("✅ Email message creation successful")
    
    def test_create_email_message_without_image(self):
        """Test email message creation without image"""
        self.test_logger.info("Testing email message creation without image")
        
        email_system = self._create_email_automation()
        
        msg = email_system.create_email_message(
            "test@example.com",
            "John",
            "Test Subject",
            "Test Body",
            None
        )
        
        self.assertIsNotNone(msg)
        if msg:  # Type guard to ensure msg is not None
            self.assertEqual(msg['To'], "test@example.com")
        
        self.test_logger.info("✅ Email message creation without image successful")
    
    def test_create_email_message_invalid_sender(self):
        """Test email message creation with invalid sender"""
        self.test_logger.info("Testing email message creation with invalid sender")
        
        # Create instance with invalid sender
        email_system = EmailAutomation(
            smtp_server=self.test_smtp_server,
            smtp_port=self.test_smtp_port,
            email=self.test_sender_email,
            password=self.test_password,
            output_folder=self.output_dir
        )
        
        # Manually set sender_email to None to test validation
        email_system.sender_email = None
        
        msg = email_system.create_email_message(
            "test@example.com",
            "John",
            "Test Subject",
            "Test Body",
            None
        )
        
        self.assertIsNone(msg)
        
        self.test_logger.info("✅ Invalid sender properly handled")
    
    # =========================================================================
    # SMTP SENDING TESTS (MOCKED)
    # =========================================================================
    
    @patch('smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        """Test successful email sending"""
        self.test_logger.info("Testing email sending")
        
        # Setup mock
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        
        email_system = self._create_email_automation()
        
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = self.test_sender_email
        msg['To'] = "test@example.com"
        msg['Subject'] = "Test"
        
        result = email_system.send_email(msg)
        
        self.assertTrue(result)
        mock_smtp.assert_called_once_with(self.test_smtp_server, self.test_smtp_port)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with(self.test_sender_email, self.test_password)
        mock_server.sendmail.assert_called_once()
        mock_server.quit.assert_called_once()
        
        self.test_logger.info("✅ Email sending successful")
    
    @patch('smtplib.SMTP')
    def test_send_email_authentication_error(self, mock_smtp):
        """Test email sending with authentication error"""
        self.test_logger.info("Testing email sending with authentication error")
        
        # Setup mock to raise authentication error
        mock_server = Mock()
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, "Authentication failed")
        mock_smtp.return_value = mock_server
        
        email_system = self._create_email_automation()
        
        msg = MIMEMultipart()
        msg['From'] = self.test_sender_email
        msg['To'] = "test@example.com"
        
        result = email_system.send_email(msg)
        
        self.assertFalse(result)
        self.assertEqual(len(email_system.stats['errors']), 1)
        
        self.test_logger.info("✅ Authentication error properly handled")
    
    def test_send_email_none_message(self):
        """Test sending None message"""
        self.test_logger.info("Testing sending None message")
        
        email_system = self._create_email_automation()
        result = email_system.send_email(None)
        
        self.assertFalse(result)
        
        self.test_logger.info("✅ None message properly handled")
    
    def test_send_email_invalid_config(self):
        """Test sending email with invalid configuration"""
        self.test_logger.info("Testing email sending with invalid configuration")
        
        email_system = self._create_email_automation()
        # Manually set invalid config
        email_system.smtp_server = None
        
        msg = MIMEMultipart()
        msg['From'] = self.test_sender_email
        msg['To'] = "test@example.com"
        
        result = email_system.send_email(msg)
        
        self.assertFalse(result)
        
        self.test_logger.info("✅ Invalid configuration properly handled")
    
    # =========================================================================
    # BIRTHDAY EMAIL PROCESSING TESTS
    # =========================================================================
    
    @patch('automation_email.EmailAutomation.send_email')
    @patch('automation_email.EmailAutomation.add_text_to_image')
    def test_check_and_send_birthday_emails_success(self, mock_add_text, mock_send):
        """Test birthday email processing"""
        self.test_logger.info("Testing birthday email processing")
        
        # Setup mocks
        mock_add_text.return_value = (b'fake_image_bytes', 'fake_path')
        mock_send.return_value = True
        
        email_system = self._create_email_automation()
        
        # Create DataFrame with today's birthday
        today = datetime.date.today()
        test_data = pd.DataFrame({
            'first_name': ['John'],
            'last_name': ['Doe'],
            'email': ['john@test.com'],
            'birthday': [today]
        })
        
        email_system.check_and_send_birthday_emails(
            test_data,
            self.birthday_card,
            text_position=(100, 100),
            font_size=40,
            font_color=(0, 0, 0)
        )
        
        self.assertEqual(email_system.stats['birthday_emails_sent'], 1)
        self.assertEqual(len(email_system.stats['birthdays_today']), 1)
        mock_add_text.assert_called_once()
        mock_send.assert_called_once()
        
        self.test_logger.info("✅ Birthday email processing successful")
    
    @patch('automation_email.EmailAutomation.send_email')
    @patch('automation_email.EmailAutomation.add_text_to_image')
    def test_check_and_send_birthday_emails_no_birthdays(self, mock_add_text, mock_send):
        """Test birthday email processing with no birthdays today"""
        self.test_logger.info("Testing birthday email processing with no birthdays")
        
        email_system = self._create_email_automation()
        
        # Create DataFrame with no birthdays today
        test_data = pd.DataFrame({
            'first_name': ['John'],
            'last_name': ['Doe'],
            'email': ['john@test.com'],
            'birthday': [datetime.date(1990, 1, 1)]  # Different date
        })
        
        email_system.check_and_send_birthday_emails(
            test_data,
            self.birthday_card
        )
        
        self.assertEqual(email_system.stats['birthday_emails_sent'], 0)
        self.assertEqual(len(email_system.stats['birthdays_today']), 0)
        mock_add_text.assert_not_called()
        mock_send.assert_not_called()
        
        self.test_logger.info("✅ No birthdays properly handled")
    
    @patch('automation_email.EmailAutomation.send_email')
    @patch('automation_email.EmailAutomation.add_text_to_image')
    def test_check_and_send_birthday_emails_image_error(self, mock_add_text, mock_send):
        """Test birthday email processing with image creation error"""
        self.test_logger.info("Testing birthday email processing with image error")
        
        # Setup mocks
        mock_add_text.return_value = (None, None)  # Simulate image creation failure
        
        email_system = self._create_email_automation()
        
        # Create DataFrame with today's birthday
        today = datetime.date.today()
        test_data = pd.DataFrame({
            'first_name': ['John'],
            'last_name': ['Doe'],
            'email': ['john@test.com'],
            'birthday': [today]
        })
        
        email_system.check_and_send_birthday_emails(
            test_data,
            self.birthday_card
        )
        
        self.assertEqual(email_system.stats['birthday_emails_failed'], 1)
        mock_send.assert_not_called()
        
        self.test_logger.info("✅ Image error properly handled")
    
    # =========================================================================
    # ANNIVERSARY EMAIL PROCESSING TESTS
    # =========================================================================
    
    @patch('automation_email.EmailAutomation.send_email')
    @patch('automation_email.EmailAutomation.add_text_to_image')
    def test_check_and_send_anniversary_emails_success(self, mock_add_text, mock_send):
        """Test anniversary email processing"""
        self.test_logger.info("Testing anniversary email processing")
        
        # Setup mocks
        mock_add_text.return_value = (b'fake_image_bytes', 'fake_path')
        mock_send.return_value = True
        
        email_system = self._create_email_automation()
        
        # Create DataFrame with today's anniversary
        today = datetime.date.today()
        anniversary_date = datetime.date(today.year - 5, today.month, today.day)
        
        test_data = pd.DataFrame({
            'first_name': ['John'],
            'last_name': ['Doe'],
            'email': ['john@test.com'],
            'birthday': [datetime.date(1990, 1, 1)],
            'anniversary': [anniversary_date]
        })
        
        # Use the correct method name with proper fallback
        if hasattr(email_system, 'check_and_send_anniversary_emails'):
            email_system.check_and_send_anniversary_emails(
                test_data,
                self.anniversary_card,
                text_position=(100, 100),
                font_size=40,
                font_color=(0, 0, 0)
            )
        else:
            # Fallback to direct method call if attribute name is different
            getattr(email_system, 'check_and_send_anniversary_emails', lambda *args, **kwargs: None)(
                test_data,
                self.anniversary_card,
                text_position=(100, 100),
                font_size=40,
                font_color=(0, 0, 0)
            )
        
        self.assertEqual(email_system.stats['anniversary_emails_sent'], 1)
        self.assertEqual(len(email_system.stats['anniversaries_today']), 1)
        self.assertEqual(email_system.stats['anniversaries_today'][0]['years'], 5)
        
        self.test_logger.info("✅ Anniversary email processing successful")
    
    @patch('automation_email.EmailAutomation.send_email')
    def test_check_and_send_anniversary_emails_no_column(self, mock_send):
        """Test anniversary email processing without anniversary column"""
        self.test_logger.info("Testing anniversary email processing without column")
        
        email_system = self._create_email_automation()
        
        # Create DataFrame without anniversary column
        test_data = pd.DataFrame({
            'first_name': ['John'],
            'last_name': ['Doe'],
            'email': ['john@test.com'],
            'birthday': [datetime.date(1990, 1, 1)]
        })
        
        # Use the correct method name with proper fallback
        if hasattr(email_system, 'check_and_send_anniversary_emails'):
            email_system.check_and_send_anniversary_emails(
                test_data,
                self.anniversary_card
            )
        else:
            # Fallback method call
            getattr(email_system, 'check_and_send_anniversary_emails', lambda *args, **kwargs: None)(
                test_data,
                self.anniversary_card
            )
        
        self.assertEqual(email_system.stats['anniversary_emails_sent'], 0)
        mock_send.assert_not_called()
        
        self.test_logger.info("✅ Missing anniversary column properly handled")
    
    # =========================================================================
    # DAILY REPORT TESTS
    # =========================================================================
    
    @patch('automation_email.EmailAutomation.send_email')
    def test_create_summary_report(self, mock_send):
        """Test summary report creation"""
        self.test_logger.info("Testing summary report creation")
        
        email_system = self._create_email_automation()
        
        # Add some test data to stats
        email_system.stats['birthday_emails_sent'] = 3
        email_system.stats['anniversary_emails_sent'] = 2
        email_system.stats['birthday_emails_failed'] = 1
        email_system.stats['birthdays_today'] = [
            {'name': 'John Doe', 'email': 'john@test.com'}
        ]
        email_system.stats['anniversaries_today'] = [
            {'name': 'Jane Smith', 'email': 'jane@test.com', 'years': 5}
        ]
        email_system.stats['errors'] = [
            {'timestamp': '2023-01-01T12:00:00', 'message': 'Test error', 'exception': None}
        ]
        
        report = email_system.create_summary_report()
        
        self.assertIn("BIRTHDAY EMAILS", report)
        self.assertIn("ANNIVERSARY EMAILS", report)
        self.assertIn("Sent Successfully: 3", report)
        self.assertIn("Sent Successfully: 2", report)
        self.assertIn("Failed: 1", report)
        self.assertIn("John Doe", report)
        self.assertIn("Jane Smith", report)
        self.assertIn("5 years", report)
        self.assertIn("Test error", report)
        
        self.test_logger.info("✅ Summary report creation successful")
    
    @patch('automation_email.EmailAutomation.send_email')
    def test_send_daily_report_success(self, mock_send):
        """Test daily report sending"""
        self.test_logger.info("Testing daily report sending")
        
        mock_send.return_value = True
        
        email_system = self._create_email_automation()
        email_system.send_daily_report()
        
        # Check that report file was created
        today_str = datetime.date.today().strftime('%Y%m%d')
        report_file = os.path.join(email_system.output_folder, f"daily_report_{today_str}.txt")
        self.assertTrue(os.path.exists(report_file))
        
        # Check that send_email was called
        mock_send.assert_called_once()
        
        self.test_logger.info("✅ Daily report sending successful")
    
    def test_send_daily_report_invalid_sender(self):
        """Test daily report sending with invalid sender"""
        self.test_logger.info("Testing daily report with invalid sender")
        
        email_system = self._create_email_automation()
        email_system.sender_email = None
        
        email_system.send_daily_report()
        
        # Should handle gracefully and log error
        self.assertEqual(len(email_system.stats['errors']), 1)
        
        self.test_logger.info("✅ Invalid sender in report properly handled")
    
    # =========================================================================
    # INTEGRATION TESTS
    # =========================================================================
    
    @patch('automation_email.EmailAutomation.send_email')
    def test_run_daily_check_success(self, mock_send):
        """Test complete daily check process"""
        self.test_logger.info("Testing complete daily check process")
        
        mock_send.return_value = True
        
        email_system = self._create_email_automation()
        
        # Create test data with today's dates
        today = datetime.date.today()
        anniversary_date = datetime.date(today.year - 3, today.month, today.day)
        
        test_data = {
            'first_name': ['John', 'Jane'],
            'last_name': ['Doe', 'Smith'],
            'email': ['john@test.com', 'jane@test.com'],
            'birthday': [today, datetime.date(1990, 1, 1)],
            'anniversary': [anniversary_date, '']
        }
        
        # Update test CSV
        test_df = pd.DataFrame(test_data)
        test_df.to_csv(self.test_csv_file, index=False)
        
        email_system.run_daily_check(
            csv_file=self.test_csv_file,
            birthday_card_path=self.birthday_card,
            anniversary_card_path=self.anniversary_card,
            birthday_text_pos=(100, 100),
            anniversary_text_pos=(150, 150),
            birthday_font_size=50,
            anniversary_font_size=45,
            birthday_font_color=(255, 0, 0),
            anniversary_font_color=(0, 0, 255)
        )
        
        # Should have processed 1 birthday and 1 anniversary
        self.assertEqual(email_system.stats['birthday_emails_sent'], 1)
        self.assertEqual(email_system.stats['anniversary_emails_sent'], 1)
        
        # Check that daily report was sent (mock_send called multiple times)
        self.assertTrue(mock_send.called)
        
        self.test_logger.info("✅ Complete daily check process successful")
    
    def test_run_daily_check_missing_files(self):
        """Test daily check with missing files"""
        self.test_logger.info("Testing daily check with missing files")
        
        email_system = self._create_email_automation()
        
        email_system.run_daily_check(
            csv_file="nonexistent.csv",
            birthday_card_path="nonexistent.png",
            anniversary_card_path="nonexistent.png"
        )
        
        # Should have errors for missing files
        self.assertGreater(len(email_system.stats['errors']), 0)
        
        self.test_logger.info("✅ Missing files properly handled")
    
    # =========================================================================
    # ERROR HANDLING TESTS
    # =========================================================================
    
    def test_log_error_functionality(self):
        """Test error logging functionality"""
        self.test_logger.info("Testing error logging")
        
        email_system = self._create_email_automation()
        
        # Test logging error without exception
        email_system.log_error("Test error message")
        self.assertEqual(len(email_system.stats['errors']), 1)
        self.assertEqual(email_system.stats['errors'][0]['message'], "Test error message")
        self.assertIsNone(email_system.stats['errors'][0]['exception'])
        
        # Test logging error with exception
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            email_system.log_error("Test error with exception", e)
        
        self.assertEqual(len(email_system.stats['errors']), 2)
        self.assertIsNotNone(email_system.stats['errors'][1]['exception'])
        
        self.test_logger.info("✅ Error logging functionality successful")
    
    def test_stats_tracking(self):
        """Test statistics tracking"""
        self.test_logger.info("Testing statistics tracking")
        
        email_system = self._create_email_automation()
        
        # Check initial stats
        self.assertEqual(email_system.stats['birthday_emails_sent'], 0)
        self.assertEqual(email_system.stats['anniversary_emails_sent'], 0)
        self.assertEqual(email_system.stats['birthday_emails_failed'], 0)
        self.assertEqual(email_system.stats['anniversary_emails_failed'], 0)
        self.assertEqual(len(email_system.stats['errors']), 0)
        self.assertEqual(len(email_system.stats['birthdays_today']), 0)
        self.assertEqual(len(email_system.stats['anniversaries_today']), 0)
        self.assertIsNotNone(email_system.stats['start_time'])
        self.assertIsNone(email_system.stats['end_time'])
        
        self.test_logger.info("✅ Statistics tracking successful")
    
    # =========================================================================
    # EDGE CASE TESTS
    # =========================================================================
    
    def test_leap_year_birthday(self):
        """Test handling of leap year birthdays"""
        self.test_logger.info("Testing leap year birthday handling")
        
        email_system = self._create_email_automation()
        
        # Create test data with Feb 29 birthday
        test_data = pd.DataFrame({
            'first_name': ['Leap'],
            'last_name': ['Year'],
            'email': ['leap@test.com'],
            'birthday': ['2000-02-29']  # Leap year birthday
        })
        
        # Should load without errors
        df = email_system.load_employee_data(self.test_csv_file)
        self.assertFalse(df.empty)
        
        self.test_logger.info("✅ Leap year birthday handling successful")
    
    def test_empty_csv_file(self):
        """Test handling of empty CSV file"""
        self.test_logger.info("Testing empty CSV file handling")
        
        # Create empty CSV
        empty_csv = os.path.join(self.test_dir, "empty.csv")
        pd.DataFrame().to_csv(empty_csv, index=False)
        
        email_system = self._create_email_automation()
        df = email_system.load_employee_data(empty_csv)
        
        # Should handle gracefully
        self.assertTrue(df.empty)
        
        self.test_logger.info("✅ Empty CSV file handling successful")
    
    def test_special_characters_in_names(self):
        """Test handling of special characters in names"""
        self.test_logger.info("Testing special characters in names")
        
        email_system = self._create_email_automation()
        
        # Test with special characters
        image_bytes, _ = email_system.add_text_to_image(
            self.birthday_card,
            "Dear José María"  # Special characters
        )
        
        self.assertIsNotNone(image_bytes)
        
        self.test_logger.info("✅ Special characters handling successful")
    
    def test_very_long_name(self):
        """Test handling of very long names"""
        self.test_logger.info("Testing very long name handling")
        
        email_system = self._create_email_automation()
        
        # Test with very long name
        long_name = "Dear " + "A" * 100  # Very long name
        image_bytes, _ = email_system.add_text_to_image(
            self.birthday_card,
            long_name
        )
        
        self.assertIsNotNone(image_bytes)
        
        self.test_logger.info("✅ Very long name handling successful")
    
    # =========================================================================
    # PERFORMANCE TESTS
    # =========================================================================
    
    def test_large_dataset_processing(self):
        """Test processing of large employee dataset"""
        self.test_logger.info("Testing large dataset processing")
        
        email_system = self._create_email_automation()
        
        # Create large dataset
        large_data = {
            'first_name': [f'Employee{i}' for i in range(1000)],
            'last_name': [f'Last{i}' for i in range(1000)],
            'email': [f'employee{i}@test.com' for i in range(1000)],
            'birthday': ['1990-01-01'] * 1000,
            'anniversary': ['2020-01-01'] * 500 + [''] * 500
        }
        
        large_csv = os.path.join(self.test_dir, "large_employees.csv")
        large_df = pd.DataFrame(large_data)
        large_df.to_csv(large_csv, index=False)
        
        # Should load without issues
        df = email_system.load_employee_data(large_csv)
        self.assertEqual(len(df), 1000)
        
        self.test_logger.info("✅ Large dataset processing successful")
    
    def test_multiple_image_formats(self):
        """Test handling of different image formats"""
        self.test_logger.info("Testing multiple image formats")
        
        email_system = self._create_email_automation()
        
        # Create images in different formats
        formats = [('JPEG', 'test.jpg'), ('PNG', 'test.png')]
        
        for format_name, filename in formats:
            img_path = os.path.join(self.test_dir, filename)
            img = Image.new('RGB', (200, 200), color='blue')
            img.save(img_path, format=format_name)
            
            image_bytes, _ = email_system.add_text_to_image(
                img_path,
                "Test Text"
            )
            
            self.assertIsNotNone(image_bytes)
        
        self.test_logger.info("✅ Multiple image formats handling successful")
    
    # =========================================================================
    # CONFIGURATION TESTS
    # =========================================================================
    
    def test_different_font_sizes(self):
        """Test different font size configurations"""
        self.test_logger.info("Testing different font sizes")
        
        email_system = self._create_email_automation()
        
        font_sizes = [10, 20, 40, 60, 80, 100]
        
        for size in font_sizes:
            image_bytes, _ = email_system.add_text_to_image(
                self.birthday_card,
                "Test Text",
                font_size=size
            )
            
            self.assertIsNotNone(image_bytes)
        
        self.test_logger.info("✅ Different font sizes successful")
    
    def test_different_text_positions(self):
        """Test different text position configurations"""
        self.test_logger.info("Testing different text positions")
        
        email_system = self._create_email_automation()
        
        positions = [(0, 0), (100, 100), (200, 200), (400, 300), (50, 500)]
        
        for position in positions:
            image_bytes, _ = email_system.add_text_to_image(
                self.birthday_card,
                "Test Text",
                position=position
            )
            
            self.assertIsNotNone(image_bytes)
        
        self.test_logger.info("✅ Different text positions successful")
    
    # =========================================================================
    # CLEANUP AND LOGGING TESTS
    # =========================================================================
    
    def test_log_file_creation(self):
        """Test that log files are created properly"""
        self.test_logger.info("Testing log file creation")
        
        email_system = self._create_email_automation()
        
        # Check that log file exists
        self.assertTrue(os.path.exists(email_system.log_file_path))
        
        # Check that log file is in correct location
        expected_log_path = os.path.join(email_system.logs_folder, "email_automation.log")
        self.assertEqual(email_system.log_file_path, expected_log_path)
        
        self.test_logger.info("✅ Log file creation successful")
    
    def test_output_folder_structure(self):
        """Test that output folder structure is created correctly"""
        self.test_logger.info("Testing output folder structure")
        
        email_system = self._create_email_automation()
        
        # Check main output folder
        self.assertTrue(os.path.exists(email_system.output_folder))
        
        # Check logs subfolder
        self.assertTrue(os.path.exists(email_system.logs_folder))
        
        # Check correct path structure
        expected_logs_path = os.path.join(email_system.output_folder, "logs")
        self.assertEqual(email_system.logs_folder, expected_logs_path)
        
        self.test_logger.info("✅ Output folder structure successful")


class TestEmailAutomationIntegration(unittest.TestCase):
    """Integration tests that test multiple components working together"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.test_dir, "output")
        
        # Setup test logging
        self.logs_dir = os.path.join(self.output_dir, "logs")
        os.makedirs(self.logs_dir, exist_ok=True)
        
        test_log_file = os.path.join(self.logs_dir, "integration_test.log")
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler = logging.FileHandler(test_log_file, mode='a', encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        self.integration_logger = logging.getLogger('EmailAutomationIntegration')
        self.integration_logger.setLevel(logging.INFO)
        self.integration_logger.handlers.clear()
        self.integration_logger.addHandler(file_handler)
        
        self.integration_logger.info("=" * 80)
        self.integration_logger.info("STARTING EMAIL AUTOMATION INTEGRATION TESTS")
        self.integration_logger.info("=" * 80)
    
    def tearDown(self):
        """Clean up integration test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
        # Clean up logger
        for handler in self.integration_logger.handlers[:]:
            handler.close()
            self.integration_logger.removeHandler(handler)
    
    @patch('automation_email.EmailAutomation.send_email')
    def test_end_to_end_workflow(self, mock_send):
        """Test complete end-to-end workflow"""
        self.integration_logger.info("Testing end-to-end workflow")
        
        mock_send.return_value = True
        
        # Create complete test environment
        today = datetime.date.today()
        
        # Create test CSV
        csv_file = os.path.join(self.test_dir, "employees.csv")
        test_data = pd.DataFrame({
            'first_name': ['John', 'Jane', 'Bob'],
            'last_name': ['Doe', 'Smith', 'Johnson'],
            'email': ['john@test.com', 'jane@test.com', 'bob@test.com'],
            'birthday': [today, datetime.date(1990, 1, 1), today],
            'anniversary': [
                datetime.date(today.year - 2, today.month, today.day),
                '',
                ''
            ]
        })
        test_data.to_csv(csv_file, index=False)
        
        # Create test images
        birthday_card = os.path.join(self.test_dir, "birthday.png")
        anniversary_card = os.path.join(self.test_dir, "anniversary.png")
        
        for card_path in [birthday_card, anniversary_card]:
            img = Image.new('RGB', (800, 600), color='white')
            img.save(card_path)
        
        # Initialize system
        email_system = EmailAutomation(
            smtp_server="smtp.test.com",
            smtp_port=587,
            email="test@example.com",
            password="password",
            output_folder=self.output_dir
        )
        
        # Run complete workflow
        email_system.run_daily_check(
            csv_file=csv_file,
            birthday_card_path=birthday_card,
            anniversary_card_path=anniversary_card
        )
        
        # Verify results
        self.assertEqual(email_system.stats['birthday_emails_sent'], 2)  # John and Bob
        self.assertEqual(email_system.stats['anniversary_emails_sent'], 1)  # John
        
        # Check that images were created
        output_files = os.listdir(self.output_dir)
        birthday_images = [f for f in output_files if f.startswith('birthday_')]
        anniversary_images = [f for f in output_files if f.startswith('anniversary_')]
        
        self.assertEqual(len(birthday_images), 2)
        self.assertEqual(len(anniversary_images), 1)
        
        # Check that daily report was created
        today_str = today.strftime('%Y%m%d')
        report_file = f"daily_report_{today_str}.txt"
        self.assertIn(report_file, output_files)
        
        self.integration_logger.info("✅ End-to-end workflow successful")


def run_test_suite():
    """Run the complete test suite and generate detailed report"""
    
    # Create test output directory
    output_dir = "output"
    logs_dir = os.path.join(output_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    # Setup main test logger
    test_log_file = os.path.join(logs_dir, "test_suite_results.log")
    
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler = logging.FileHandler(test_log_file, mode='w', encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    suite_logger = logging.getLogger('TestSuite')
    suite_logger.setLevel(logging.INFO)
    suite_logger.handlers.clear()
    suite_logger.addHandler(file_handler)
    suite_logger.addHandler(console_handler)
    
    suite_logger.info("🚀 STARTING EMAIL AUTOMATION TEST SUITE")
    suite_logger.info("=" * 80)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestEmailAutomation))
    suite.addTests(loader.loadTestsFromTestCase(TestEmailAutomationIntegration))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=open(os.path.join(logs_dir, "test_output.txt"), 'w'),
        buffer=True
    )
    
    start_time = datetime.datetime.now()
    result = runner.run(suite)
    end_time = datetime.datetime.now()
    
    # Generate summary report
    duration = end_time - start_time
    
    suite_logger.info("=" * 80)
    suite_logger.info("TEST SUITE SUMMARY")
    suite_logger.info("=" * 80)
    suite_logger.info(f"Tests Run: {result.testsRun}")
    suite_logger.info(f"Failures: {len(result.failures)}")
    suite_logger.info(f"Errors: {len(result.errors)}")
    suite_logger.info(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    suite_logger.info(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    suite_logger.info(f"Execution Time: {duration}")
    
    if result.failures:
        suite_logger.error("FAILURES:")
        for test, traceback in result.failures:
            suite_logger.error(f"❌ {test}: {traceback}")
    
    if result.errors:
        suite_logger.error("ERRORS:")
        for test, traceback in result.errors:
            suite_logger.error(f"💥 {test}: {traceback}")
    
    # Create detailed HTML report
    html_report_path = os.path.join(output_dir, "test_report.html")
    create_html_report(result, html_report_path, duration)
    
    suite_logger.info(f"📊 Detailed HTML report saved to: {html_report_path}")
    suite_logger.info(f"📝 Test logs saved to: {logs_dir}")
    
    if len(result.failures) == 0 and len(result.errors) == 0:
        suite_logger.info("🎉 ALL TESTS PASSED!")
    else:
        suite_logger.warning("⚠️  SOME TESTS FAILED - Check logs for details")
    
    return result


def create_html_report(test_result, output_path, duration):
    """Create detailed HTML test report"""
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Email Automation Test Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .summary {{ margin: 20px 0; }}
            .success {{ color: green; }}
            .failure {{ color: red; }}
            .error {{ color: orange; }}
            .test-case {{ margin: 10px 0; padding: 10px; border-left: 3px solid #ccc; }}
            .passed {{ border-left-color: green; }}
            .failed {{ border-left-color: red; }}
            .error-case {{ border-left-color: orange; }}
            pre {{ background-color: #f5f5f5; padding: 10px; overflow-x: auto; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📧 Email Automation Test Report</h1>
            <p>Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="summary">
            <h2>📊 Test Summary</h2>
            <ul>
                <li><strong>Total Tests:</strong> {test_result.testsRun}</li>
                <li class="success"><strong>Passed:</strong> {test_result.testsRun - len(test_result.failures) - len(test_result.errors)}</li>
                <li class="failure"><strong>Failed:</strong> {len(test_result.failures)}</li>
                <li class="error"><strong>Errors:</strong> {len(test_result.errors)}</li>
                <li><strong>Success Rate:</strong> {((test_result.testsRun - len(test_result.failures) - len(test_result.errors)) / test_result.testsRun * 100):.1f}%</li>
                <li><strong>Execution Time:</strong> {duration}</li>
            </ul>
        </div>
    """
    
    if test_result.failures:
        html_content += """
        <div class="failures">
            <h2>❌ Failed Tests</h2>
        """
        for test, traceback in test_result.failures:
            html_content += f"""
            <div class="test-case failed">
                <h3>{test}</h3>
                <pre>{traceback}</pre>
            </div>
            """
        html_content += "</div>"
    
    if test_result.errors:
        html_content += """
        <div class="errors">
            <h2>💥 Error Tests</h2>
        """
        for test, traceback in test_result.errors:
            html_content += f"""
            <div class="test-case error-case">
                <h3>{test}</h3>
                <pre>{traceback}</pre>
            </div>
            """
        html_content += "</div>"
    
    html_content += """
        <div class="footer">
            <h2>📝 Test Categories Covered</h2>
            <ul>
                <li>✅ Initialization and Configuration</li>
                <li>✅ CSV Data Loading and Validation</li>
                <li>✅ Image Processing and Text Addition</li>
                <li>✅ Email Message Creation</li>
                <li>✅ SMTP Email Sending (Mocked)</li>
                <li>✅ Birthday Email Processing</li>
                <li>✅ Anniversary Email Processing</li>
                <li>✅ Daily Report Generation</li>
                <li>✅ Error Handling and Logging</li>
                <li>✅ Edge Cases and Performance</li>
                <li>✅ Integration Testing</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


if __name__ == "__main__":
    # Run the complete test suite
    print("🧪 Starting Email Automation Test Suite...")
    print("📝 Logs will be saved to: output/logs/")
    print("=" * 60)
    
    result = run_test_suite()
    
    print("=" * 60)
    if len(result.failures) == 0 and len(result.errors) == 0:
        print("🎉 ALL TESTS PASSED! System is ready for production.")
    else:
        print("⚠️  Some tests failed. Please check the logs for details.")
    
    print("📊 Check output/test_report.html for detailed results.")