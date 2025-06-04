#!/usr/bin/env python3
"""
Test script for Birthday Email Automation System
This script runs comprehensive tests without sending actual emails
"""

import unittest
import pandas as pd
import tempfile
import shutil
import os
from datetime import date, timedelta
from pathlib import Path
from io import BytesIO
from PIL import Image
from unittest.mock import patch, MagicMock

# Import the main automation class
try:
    from birthday_automation import BirthdayEmailAutomation, Employee
except ImportError:
    print("❌ Could not import birthday_automation. Make sure the file exists in the same directory.")
    exit(1)

class TestBirthdayAutomation(unittest.TestCase):
    """Test suite for Birthday Email Automation"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.csv_file = os.path.join(self.test_dir, 'test_employees.csv')
        
        # Set environment variables for testing
        os.environ['EMAIL_USER'] = 'test@example.com'
        os.environ['EMAIL_PASSWORD'] = 'test_password'
        os.environ['EMPLOYEE_CSV_FILE'] = self.csv_file
        os.environ['OUTPUT_DIR'] = os.path.join(self.test_dir, 'output')
        
        # Create test CSV
        self.create_test_csv()
        
        # Initialize automation system
        self.automation = BirthdayEmailAutomation()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
        # Clean up environment variables
        test_vars = ['EMAIL_USER', 'EMAIL_PASSWORD', 'EMPLOYEE_CSV_FILE', 'OUTPUT_DIR']
        for var in test_vars:
            if var in os.environ:
                del os.environ[var]
    
    def create_test_csv(self):
        """Create test CSV with various birthday scenarios"""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        yesterday = today - timedelta(days=1)
        
        test_data = {
            'empid': ['EMP001', 'EMP002', 'EMP003', 'EMP004', 'EMP005'],
            'first_name': ['Alice', 'Bob', 'Carol', 'David', 'Emma'],
            'second_name': ['Johnson', 'Smith', 'Davis', 'Wilson', 'Brown'],
            'email': [
                'alice@test.com',
                'bob@test.com',
                'carol@test.com',
                'david@test.com',
                'emma@test.com'
            ],
            'dob': [
                today.strftime('%Y-%m-%d'),      # Today's birthday
                tomorrow.strftime('%Y-%m-%d'),   # Tomorrow's birthday
                yesterday.strftime('%Y-%m-%d'),  # Yesterday's birthday
                today.strftime('%Y-%m-%d'),      # Another today's birthday
                '1995-12-25'                     # Christmas birthday (not today)
            ],
            'department': ['Engineering', 'Marketing', 'HR', 'Engineering', 'Finance']
        }
        
        df = pd.DataFrame(test_data)
        df.to_csv(self.csv_file, index=False)
        return df

class TestEmployeeDataLoading(TestBirthdayAutomation):
    """Test employee data loading functionality"""
    
    def test_load_valid_csv(self):
        """Test loading valid CSV file"""
        employees = self.automation.load_employee_data()
        self.assertEqual(len(employees), 5, "Should load all 5 employees")
        self.assertIsInstance(employees[0], Employee, "Should return Employee objects")
    
    def test_missing_csv_file(self):
        """Test handling of missing CSV file"""
        os.environ['EMPLOYEE_CSV_FILE'] = 'nonexistent.csv'
        automation = BirthdayEmailAutomation()
        employees = automation.load_employee_data()
        self.assertEqual(len(employees), 0, "Should return empty list for missing file")
    
    def test_invalid_csv_structure(self):
        """Test handling of CSV with missing columns"""
        invalid_data = {'name': ['Alice'], 'email': ['alice@test.com']}
        invalid_df = pd.DataFrame(invalid_data)
        invalid_csv = os.path.join(self.test_dir, 'invalid.csv')
        invalid_df.to_csv(invalid_csv, index=False)
        
        os.environ['EMPLOYEE_CSV_FILE'] = invalid_csv
        automation = BirthdayEmailAutomation()
        employees = automation.load_employee_data()
        self.assertEqual(len(employees), 0, "Should return empty list for invalid CSV")

class TestBirthdayDetection(TestBirthdayAutomation):
    """Test birthday detection functionality"""
    
    def test_todays_birthdays(self):
        """Test detection of today's birthdays"""
        employees = self.automation.load_employee_data()
        birthday_employees = self.automation.get_birthday_employees(employees)
        
        # Should find Alice and David who have today's birthday
        self.assertEqual(len(birthday_employees), 2, "Should find 2 employees with today's birthday")
        names = [emp.first_name for emp in birthday_employees]
        self.assertIn('Alice', names, "Should find Alice's birthday")
        self.assertIn('David', names, "Should find David's birthday")
    
    def test_specific_date_birthdays(self):
        """Test detection of birthdays for specific date"""
        employees = self.automation.load_employee_data()
        tomorrow = date.today() + timedelta(days=1)
        birthday_employees = self.automation.get_birthday_employees(employees, tomorrow)
        
        self.assertEqual(len(birthday_employees), 1, "Should find 1 employee with tomorrow's birthday")
        self.assertEqual(birthday_employees[0].first_name, 'Bob', "Should find Bob's birthday tomorrow")

class TestImageGeneration(TestBirthdayAutomation):
    """Test image generation functionality"""
    
    def test_font_loading(self):
        """Test font loading functionality"""
        self.automation.load_fonts()
        self.assertTrue(self.automation.fonts_loaded, "Fonts should be marked as loaded")
        self.assertIn('header', self.automation.fonts, "Should have header font")
        self.assertIn('main', self.automation.fonts, "Should have main font")
    
    def test_create_base_image(self):
        """Test base image creation"""
        base_image = self.automation.create_base_image()
        
        self.assertIsInstance(base_image, Image.Image, "Should return PIL Image object")
        self.assertEqual(base_image.size, (800, 624), "Should have correct dimensions")
        self.assertEqual(base_image.mode, 'RGB', "Should be RGB mode")
        
        # Test caching
        base_image2 = self.automation.create_base_image()
        self.assertIs(base_image, base_image2, "Should return cached base image")
    
    def test_create_personalized_image(self):
        """Test creating personalized images"""
        employee = Employee(
            empid="TEST001",
            first_name="Alice",
            second_name="Test",
            email="alice@test.com",
            dob=date.today(),
            department="Testing"
        )
        
        image = self.automation.create_personalized_image(employee)
        self.assertIsInstance(image, Image.Image, "Should return PIL Image object")
        self.assertEqual(image.size, (800, 624), "Should maintain base image dimensions")

class TestEmailFunctionality(TestBirthdayAutomation):
    """Test email functionality (without sending actual emails)"""
    
    def test_create_email_content(self):
        """Test email content generation"""
        employee = Employee(
            empid="TEST001",
            first_name="Alice",
            second_name="Test",
            email="alice@test.com",
            dob=date.today(),
            department="Testing"
        )
        
        content = self.automation.create_email_content(employee)
        self.assertIn("Alice", content, "Should include employee first name")
        self.assertIn("Alice Test", content, "Should include full name")
        self.assertIn("Testing", content, "Should include department")
        self.assertIn("html", content.lower(), "Should be HTML content")
    
    @patch('smtplib.SMTP')
    def test_send_birthday_email_success(self, mock_smtp):
        """Test successful email sending"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        employee = Employee(
            empid="TEST001",
            first_name="Alice",
            second_name="Test",
            email="alice@test.com",
            dob=date.today(),
            department="Testing"
        )
        
        # Create test image data
        test_image = self.automation.create_personalized_image(employee)
        img_byte_arr = BytesIO()
        test_image.save(img_byte_arr, format='PNG')
        img_data = img_byte_arr.getvalue()
        
        result = self.automation.send_birthday_email(employee, img_data)
        
        self.assertTrue(result, "Should return True for successful email")
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.sendmail.assert_called_once()

class TestImageSaving(TestBirthdayAutomation):
    """Test image saving functionality"""
    
    def test_save_image(self):
        """Test saving images to disk"""
        employee = Employee(
            empid="TEST001",
            first_name="Alice",
            second_name="Test",
            email="alice@test.com",
            dob=date.today(),
            department="Testing"
        )
        
        image = self.automation.create_personalized_image(employee)
        filepath = self.automation.save_image(employee, image)
        
        self.assertIsNotNone(filepath, "Should return filepath")
        self.assertTrue(Path(filepath).exists(), "Image file should exist")
        self.assertGreater(Path(filepath).stat().st_size, 0, "Image file should not be empty")

class TestIntegration(TestBirthdayAutomation):
    """Integration tests for complete workflow"""
    
    @patch('birthday_automation.BirthdayEmailAutomation.send_birthday_email')
    def test_complete_workflow(self, mock_send_email):
        """Test complete birthday processing workflow"""
        mock_send_email.return_value = True
        
        results = self.automation.process_birthdays(save_images=True)
        
        self.assertGreater(results['processed'], 0, "Should process some birthdays")
        self.assertEqual(results['successful'], results['processed'], "All should be successful")
        self.assertEqual(results['failed'], 0, "No failures expected")
    
    def test_no_birthdays_scenario(self):
        """Test scenario when no one has birthday"""
        # Create CSV with no today's birthdays
        future_date = date.today() + timedelta(days=30)
        test_data = {
            'empid': ['EMP001'],
            'first_name': ['Alice'],
            'second_name': ['Johnson'],
            'email': ['alice@test.com'],
            'dob': [future_date.strftime('%Y-%m-%d')],
            'department': ['Engineering']
        }
        
        df = pd.DataFrame(test_data)
        no_birthday_csv = os.path.join(self.test_dir, 'no_birthdays.csv')
        df.to_csv(no_birthday_csv, index=False)
        
        os.environ['EMPLOYEE_CSV_FILE'] = no_birthday_csv
        automation = BirthdayEmailAutomation()
        
        results = automation.process_birthdays()
        
        self.assertEqual(results['processed'], 0, "Should process no birthdays")
        self.assertEqual(results['successful'], 0, "No successful emails")
        self.assertEqual(results['failed'], 0, "No failed emails")

def run_visual_tests():
    """Run visual tests that generate sample images"""
    print("\n" + "="*60)
    print("RUNNING VISUAL TESTS")
    print("="*60)
    
    # Set up environment for visual tests
    os.environ['EMAIL_USER'] = 'test@example.com'
    os.environ['EMAIL_PASSWORD'] = 'test_password'
    
    try:
        automation = BirthdayEmailAutomation()
        
        # Create test directory
        visual_dir = Path("visual_test_outputs")
        visual_dir.mkdir(exist_ok=True)
        
        print(f"Generating test images in '{visual_dir}' directory...")
        
        # Test employees with different name types
        test_employees = [
            Employee("001", "Alice", "Johnson", "alice@test.com", date.today(), "Engineering"),
            Employee("002", "José", "García", "jose@test.com", date.today(), "Marketing"),
            Employee("003", "李", "明", "li.ming@test.com", date.today(), "HR"),
            Employee("004", "Müller", "Schmidt", "muller@test.com", date.today(), "Finance"),
            Employee("005", "O'Connor", "MacDonald", "oconnor@test.com", date.today(), "Sales"),
        ]
        
        for i, employee in enumerate(test_employees, 1):
            print(f"  {i}. Generating image for '{employee.full_name}'...")
            try:
                image = automation.create_personalized_image(employee)
                filename = visual_dir / f"test_birthday_{employee.first_name}_{employee.second_name}.png"
                image.save(filename)
                print(f"     ✅ Saved: {filename}")
            except Exception as e:
                print(f"     ❌ Error generating image for {employee.full_name}: {e}")
        
        # Generate base template
        print("  Generating base template image...")
        try:
            base_image = automation.create_base_image()
            base_filename = visual_dir / "base_template.png"
            base_image.save(base_filename)
            print(f"     ✅ Saved: {base_filename}")
        except Exception as e:
            print(f"     ❌ Error generating base image: {e}")
        
        print(f"\n✅ Visual test images saved in '{visual_dir}' directory.")
        print("📋 Please check these images manually to verify they look correct!")
        
    except Exception as e:
        print(f"❌ Error running visual tests: {e}")
    
    finally:
        # Clean up environment variables
        if 'EMAIL_USER' in os.environ:
            del os.environ['EMAIL_USER']
        if 'EMAIL_PASSWORD' in os.environ:
            del os.environ['EMAIL_PASSWORD']

def run_system_check():
    """Run system compatibility check"""
    print("\n" + "="*60)
    print("SYSTEM COMPATIBILITY CHECK")
    print("="*60)
    
    checks_passed = 0
    total_checks = 0
    
    # Check Python version
    total_checks += 1
    import sys
    if sys.version_info >= (3, 7):
        print("✅ Python version compatible")
        checks_passed += 1
    else:
        print("❌ Python 3.7+ required")
    
    # Check required modules
    required_modules = ['pandas', 'PIL', 'schedule', 'dotenv']
    for module in required_modules:
        total_checks += 1
        try:
            __import__(module)
            print(f"✅ {module} module available")
            checks_passed += 1
        except ImportError:
            print(f"❌ {module} module missing")
    
    # Check file permissions
    total_checks += 1
    try:
        test_file = Path("test_permissions.tmp")
        test_file.write_text("test")
        test_file.unlink()
        print("✅ File write permissions OK")
        checks_passed += 1
    except Exception:
        print("❌ File write permissions failed")
    
    print(f"\n📊 System Check: {checks_passed}/{total_checks} checks passed")
    
    if checks_passed == total_checks:
        print("🎉 System is ready for birthday automation!")
        return True
    else:
        print("⚠️  Please fix the issues above before running the automation")
        return False

def main():
    """Main test function"""
    print("🎂 Birthday Email Automation - Test Suite")
    print("="*60)
    
    # Run system check first
    if not run_system_check():
        print("\n❌ System check failed. Please fix issues before running tests.")
        return 1
    
    # Run unit tests
    print("\n" + "="*60)
    print("RUNNING UNIT TESTS")
    print("="*60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestEmployeeDataLoading,
        TestBirthdayDetection,
        TestImageGeneration,
        TestEmailFunctionality,
        TestImageSaving,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Run visual tests
    run_visual_tests()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    if result.wasSuccessful():
        print("🎉 All tests passed successfully!")
        print("✅ The birthday automation system is ready to use")
        print("\n📋 Next steps:")
        print("   1. Configure .env file with your email settings")
        print("   2. Update employees.csv with your employee data")
        print("   3. Run: python birthday_automation.py --run-once")
        return 0
    else:
        print(f"❌ {len(result.failures + result.errors)} test(s) failed")
        print("🔧 Please fix the issues before using the system")
        return 1

if __name__ == "__main__":
    exit(main())