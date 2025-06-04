"""
Birthday Image Generator - Refactored Version
A modular, well-structured birthday automation system.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional
import logging

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.config.settings import Config
from src.services.employee_service import EmployeeService
from src.services.image_service import ImageService
from src.services.email_service import EmailService
from src.utils.logger import setup_logger


class BirthdayAutomationSystem:
    """Main orchestrator for the birthday automation system."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the birthday automation system."""
        self.config = Config(config_path)
        self.logger = setup_logger(self.config.log_level)
        
        # Initialize services
        self.employee_service = EmployeeService(self.config.csv_file)
        self.image_service = ImageService(
            base_image_path=self.config.custom_base_image,
            output_dir=self.config.output_dir
        )
        self.email_service = EmailService(
            smtp_server=self.config.smtp_server,
            smtp_port=self.config.smtp_port,
            email_user=self.config.email_user,
            email_password=self.config.email_password
        )
    
    def run_daily_check(self, save_images: bool = True) -> None:
        """Run the daily birthday check and send emails."""
        try:
            self.logger.info("Starting daily birthday check...")
            
            # Load employee data
            employees_df = self.employee_service.load_employees()
            if employees_df is None:
                self.logger.error("Failed to load employee data")
                return
            
            # Find today's birthdays
            birthday_employees = self.employee_service.get_todays_birthdays(employees_df)
            
            if not birthday_employees:
                self.logger.info("No birthdays today!")
                return
            
            self.logger.info(f"Found {len(birthday_employees)} birthday(s) today!")
            
            # Process each birthday
            success_count = 0
            for employee in birthday_employees:
                try:
                    if self._process_single_birthday(employee, save_images):
                        success_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to process birthday for {employee.get('full_name', 'Unknown')}: {e}")
            
            self.logger.info(f"Successfully processed {success_count}/{len(birthday_employees)} birthdays")
            
        except Exception as e:
            self.logger.error(f"Error in daily birthday check: {e}")
    
    def _process_single_birthday(self, employee: dict, save_images: bool) -> bool:
        """Process a single employee's birthday."""
        empid = employee['empid']
        first_name = employee['first_name']
        full_name = employee['full_name']
        email = employee['email']
        department = employee['department']
        
        self.logger.info(f"Processing birthday for {full_name} (ID: {empid}, Dept: {department})")
        
        # Generate personalized image
        image_data = self.image_service.create_birthday_image(first_name)
        if image_data is None:
            self.logger.error(f"Failed to generate image for {full_name}")
            return False
        
        # Save image if requested
        if save_images:
            image_path = self.image_service.save_birthday_image(
                image_data, empid, full_name
            )
            if image_path:
                self.logger.info(f"Image saved: {image_path}")
        
        # Send email
        success = self.email_service.send_birthday_email(
            employee_email=email,
            first_name=first_name,
            full_name=full_name,
            department=department,
            image_data=image_data
        )
        
        if success:
            self.logger.info(f"Birthday email sent successfully to {full_name}")
        else:
            self.logger.error(f"Failed to send birthday email to {full_name}")
        
        return success


def main():
    """Main entry point."""
    try:
        # Initialize system with default config
        birthday_system = BirthdayAutomationSystem()
        
        # Run daily check
        birthday_system.run_daily_check(save_images=True)
        
    except Exception as e:
        logging.error(f"Fatal error in main: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()