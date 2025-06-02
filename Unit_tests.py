import unittest
import pandas as pd
import datetime
import os
import tempfile
import shutil
from io import BytesIO
from PIL import Image
import sys

# Import the main class (assuming the main code is in birthday_generator.py)
# If you saved it with a different name, update the import below
try:
    from birthday_generator import BirthdayImageGenerator
except ImportError:
    print("Please save the main code as 'birthday_generator.py' in the same directory")
    sys.exit(1)

class TestBirthdayImageGenerator(unittest.TestCase):
    """Test suite for Birthday Image Generator"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.test_dir = tempfile.mkdtemp()
        self.csv_file = os.path.join(self.test_dir, 'test_employees.csv')
        
        # Create test instance
        self.birthday_gen = BirthdayImageGenerator(
            csv_file=self.csv_file,
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            email_user="test@gmail.com",
            email_password="test_password"
        )
        
        # Create test CSV data
        self.create_test_csv()
    
    def tearDown(self):
        """Clean up after each test"""
        shutil.rmtree(self.test_dir)
    
    def create_test_csv(self):
        """Create a test CSV file with various scenarios"""
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        yesterday = today - datetime.timedelta(days=1)
        next_month = today.replace(month=today.month + 1 if today.month < 12 else 1)
        
        test_data = {
            'empid': ['EMP001', 'EMP002', 'EMP003', 'EMP004', 'EMP005'],
            'first_name': ['Alice', 'Bob', 'Carol', 'David', 'Emma'],
            'second_name': ['Johnson', 'Smith', 'Davis', 'Wilson', 'Brown'],
            'email': [
                'shashwat.airtel@gmail.com',
                'shashwat.airtel@gmail.com', 
                'shashwat.airtel@gmail.com',
                'shashwat.airtel@gmail.com',
                'shashwat.airtel@gmail.com'
            ],
            'dob': [
                f'{today.day:02d}-{today.month:02d}-1990',  # Today's birthday (DD-MM-YYYY format)
                f'{tomorrow.day:02d}-{tomorrow.month:02d}-1985',  # Tomorrow's birthday
                f'{yesterday.day:02d}-{yesterday.month:02d}-1992',  # Yesterday's birthday
                f'{today.day:02d}-{today.month:02d}-1988',  # Another today's birthday
                f'{next_month.day:02d}-{next_month.month:02d}-1995'  # Next month birthday
            ],
            'department': ['Engineering', 'Marketing', 'HR', 'Engineering', 'Finance']
        }
        
        df = pd.DataFrame(test_data)
        df.to_csv(self.csv_file, index=False)
        return df

class TestCSVLoading(TestBirthdayImageGenerator):
    """Test CSV loading functionality"""
    
    def test_load_valid_csv(self):
        """Test loading a valid CSV file"""
        df = self.birthday_gen.load_employee_data()
        self.assertIsNotNone(df, "Should successfully load valid CSV")
        self.assertEqual(len(df), 5, "Should load all 5 employees")
        self.assertIn('full_name', df.columns, "Should create full_name column")
        self.assertIn('birthday', df.columns, "Should create birthday column")
    
    def test_missing_csv_file(self):
        """Test handling of missing CSV file"""
        self.birthday_gen.csv_file = "nonexistent.csv"
        df = self.birthday_gen.load_employee_data()
        self.assertIsNone(df, "Should return None for missing file")
    
    def test_invalid_csv_structure(self):
        """Test handling of CSV with missing columns"""
        # Create CSV with missing columns
        invalid_data = {'name': ['Alice'], 'email': ['alice@test.com']}
        invalid_df = pd.DataFrame(invalid_data)
        invalid_csv = os.path.join(self.test_dir, 'invalid.csv')
        invalid_df.to_csv(invalid_csv, index=False)
        
        self.birthday_gen.csv_file = invalid_csv
        df = self.birthday_gen.load_employee_data()
        self.assertIsNone(df, "Should return None for invalid CSV structure")
    
    def test_full_name_creation(self):
        """Test full name creation from first and second names"""
        df = self.birthday_gen.load_employee_data()
        expected_names = ['Alice Johnson', 'Bob Smith', 'Carol Davis', 'David Wilson', 'Emma Brown']
        actual_names = df['full_name'].tolist()
        self.assertEqual(actual_names, expected_names, "Should correctly combine first and second names")

class TestBirthdayDetection(TestBirthdayImageGenerator):
    """Test birthday detection functionality"""
    
    def test_todays_birthdays(self):
        """Test detection of today's birthdays"""
        df = self.birthday_gen.load_employee_data()
        birthday_employees = self.birthday_gen.get_todays_birthdays(df)
        
        # Should find Alice (EMP001) and David (EMP004) who have today's birthday
        self.assertEqual(len(birthday_employees), 2, "Should find 2 employees with today's birthday")
        
        names = [emp['first_name'] for emp in birthday_employees]
        self.assertIn('Alice', names, "Should find Alice's birthday")
        self.assertIn('David', names, "Should find David's birthday")
    
    def test_no_birthdays_today(self):
        """Test when no one has birthday today"""
        # Create CSV with no today's birthdays
        future_date = datetime.date.today() + datetime.timedelta(days=30)
        test_data = {
            'empid': ['EMP001'],
            'first_name': ['Alice'],
            'second_name': ['Johnson'],
            'email': ['shashwat.airtel@gmail.com'],
            'dob': [f'{future_date.day:02d}-{future_date.month:02d}-1990'],
            'department': ['Engineering']
        }
        
        df = pd.DataFrame(test_data)
        no_birthday_csv = os.path.join(self.test_dir, 'no_birthdays.csv')
        df.to_csv(no_birthday_csv, index=False)
        
        self.birthday_gen.csv_file = no_birthday_csv
        df = self.birthday_gen.load_employee_data()
        birthday_employees = self.birthday_gen.get_todays_birthdays(df)
        
        self.assertEqual(len(birthday_employees), 0, "Should find no birthdays today")

class TestImageGeneration(TestBirthdayImageGenerator):
    """Test image generation functionality"""
    
    def test_create_birthday_image(self):
        """Test birthday image creation"""
        test_name = "Alice"
        image = self.birthday_gen.create_birthday_image(test_name)
        
        # Test image properties
        self.assertIsInstance(image, Image.Image, "Should return PIL Image object")
        self.assertEqual(image.size, (800, 600), "Should have correct dimensions")
        self.assertEqual(image.mode, 'RGB', "Should be RGB mode")
    
    def test_save_birthday_image(self):
        """Test saving birthday image to file"""
        test_name = "TestUser"
        image = self.birthday_gen.create_birthday_image(test_name)
        
        # Save image
        test_image_path = os.path.join(self.test_dir, f'test_birthday_{test_name}.png')
        image.save(test_image_path)
        
        # Verify file was created
        self.assertTrue(os.path.exists(test_image_path), "Image file should be created")
        
        # Verify file is not empty
        self.assertGreater(os.path.getsize(test_image_path), 0, "Image file should not be empty")
        
        # Verify we can load the saved image
        loaded_image = Image.open(test_image_path)
        self.assertEqual(loaded_image.size, (800, 600), "Saved image should maintain correct size")
    
    def test_image_content_varies_by_name(self):
        """Test that different names create different images"""
        image1 = self.birthday_gen.create_birthday_image("Alice")
        image2 = self.birthday_gen.create_birthday_image("Bob")
        
        # Convert images to bytes for comparison
        img1_bytes = BytesIO()
        img2_bytes = BytesIO()
        image1.save(img1_bytes, format='PNG')
        image2.save(img2_bytes, format='PNG')
        
        # Images should be different (they contain different names)
        self.assertNotEqual(img1_bytes.getvalue(), img2_bytes.getvalue(), 
                           "Images with different names should be different")
    
    def test_special_characters_in_name(self):
        """Test image generation with special characters in name"""
        special_names = ["José", "Müller", "O'Connor", "Jean-Pierre"]
        
        for name in special_names:
            with self.subTest(name=name):
                image = self.birthday_gen.create_birthday_image(name)
                self.assertIsInstance(image, Image.Image, f"Should handle special characters in {name}")

class TestEmailFunctionality(TestBirthdayImageGenerator):
    """Test email-related functionality (without actually sending emails)"""
    
    def test_email_content_generation(self):
        """Test email HTML content generation"""
        # This tests the email content creation without actually sending
        test_image = self.birthday_gen.create_birthday_image("Alice")
        img_byte_arr = BytesIO()
        test_image.save(img_byte_arr, format='PNG')
        img_data = img_byte_arr.getvalue()
        
        # We can't easily test the actual email sending without mocking SMTP,
        # but we can verify the image data is properly formatted
        self.assertIsInstance(img_data, bytes, "Image data should be bytes")
        self.assertGreater(len(img_data), 0, "Image data should not be empty")

class TestIntegration(TestBirthdayImageGenerator):
    """Integration tests for the complete workflow"""
    
    def test_complete_birthday_processing_workflow(self):
        """Test the complete workflow without sending emails"""
        # Load data
        df = self.birthday_gen.load_employee_data()
        self.assertIsNotNone(df, "Should load employee data")
        
        # Find today's birthdays
        birthday_employees = self.birthday_gen.get_todays_birthdays(df)
        self.assertGreater(len(birthday_employees), 0, "Should find birthday employees")
        
        # Process each birthday employee
        for employee in birthday_employees:
            first_name = employee['first_name']
            empid = employee['empid']
            
            # Generate image
            image = self.birthday_gen.create_birthday_image(first_name)
            self.assertIsInstance(image, Image.Image, f"Should generate image for {first_name}")
            
            # Save image
            img_filename = os.path.join(self.test_dir, f"birthday_{empid}_{first_name}_test.png")
            image.save(img_filename)
            self.assertTrue(os.path.exists(img_filename), f"Should save image for {first_name}")

class TestEdgeCases(TestBirthdayImageGenerator):
    """Test edge cases and error conditions"""
    
    def test_empty_csv(self):
        """Test handling of empty CSV file"""
        empty_csv = os.path.join(self.test_dir, 'empty.csv')
        pd.DataFrame().to_csv(empty_csv, index=False)
        
        self.birthday_gen.csv_file = empty_csv
        df = self.birthday_gen.load_employee_data()
        self.assertIsNone(df, "Should handle empty CSV gracefully")
    
    def test_leap_year_birthday(self):
        """Test handling of leap year birthdays"""
        # Create employee with Feb 29 birthday
        leap_data = {
            'empid': ['EMP001'],
            'first_name': ['Alice'],
            'second_name': ['Johnson'],
            'email': ['shashwat.airtel@gmail.com'],
            'dob': ['29-02-1992'],  # Leap year birthday (DD-MM-YYYY format)
            'department': ['Engineering']
        }
        
        df = pd.DataFrame(leap_data)
        leap_csv = os.path.join(self.test_dir, 'leap.csv')
        df.to_csv(leap_csv, index=False)
        
        self.birthday_gen.csv_file = leap_csv
        loaded_df = self.birthday_gen.load_employee_data()
        self.assertIsNotNone(loaded_df, "Should handle leap year birthdays")
    
    def test_very_long_name(self):
        """Test image generation with very long names"""
        long_name = "Bartholomew Christopher Alexander Montgomery Winchester III"
        image = self.birthday_gen.create_birthday_image(long_name)
        self.assertIsInstance(image, Image.Image, "Should handle very long names")

def run_visual_tests():
    """Run visual tests that save images for manual inspection"""
    print("\n" + "="*50)
    print("RUNNING VISUAL TESTS")
    print("="*50)
    
    # Create test directory for visual outputs
    visual_test_dir = "visual_test_outputs"
    os.makedirs(visual_test_dir, exist_ok=True)
    
    # Initialize birthday generator
    birthday_gen = BirthdayImageGenerator(
        csv_file="dummy.csv",
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        email_user="test@gmail.com",
        email_password="test_password"
    )
    
    # Test different names
    test_names = ["Alice", "Bob", "Carol", "José", "Jean-Pierre", "A Very Long Name That Tests Wrapping"]
    
    print(f"Generating test images in '{visual_test_dir}' directory...")
    
    for i, name in enumerate(test_names, 1):
        print(f"  {i}. Generating image for '{name}'...")
        try:
            image = birthday_gen.create_birthday_image(name)
            filename = os.path.join(visual_test_dir, f"test_birthday_{name.replace(' ', '_').replace("'", '')}.png")
            image.save(filename)
            print(f"     ✓ Saved: {filename}")
        except Exception as e:
            print(f"     ✗ Error generating image for {name}: {e}")
    
    print(f"\nVisual test images saved in '{visual_test_dir}' directory.")
    print("Please check these images manually to verify they look correct!")

if __name__ == '__main__':
    print("Birthday Image Generator - Test Suite")
    print("="*50)
    
    # Run unit tests
    print("Running unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run visual tests
    run_visual_tests()
    
    print("\n" + "="*50)
    print("ALL TESTS COMPLETED!")
    print("="*50)