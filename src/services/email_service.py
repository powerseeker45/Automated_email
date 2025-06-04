"""
Email service for sending birthday notifications.
"""

import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class EmailTemplate:
    """Email template configuration."""
    subject: str = "🎉 Happy Birthday {first_name}! 🎉"
    sender_name: str = "Birthday Automation System"
    sender_signature: str = "CEO, Bharti Airtel"
    company_name: str = "Bharti Airtel Family"


class EmailService:
    """Service for sending birthday emails."""
    
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        email_user: str,
        email_password: str,
        template: Optional[EmailTemplate] = None
    ):
        """
        Initialize email service.
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP server port
            email_user: Sender email address
            email_password: Sender email password/app password
            template: Email template configuration
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_user = email_user
        self.email_password = email_password
        self.template = template or EmailTemplate()
        self.logger = logging.getLogger(__name__)
    
    def send_birthday_email(
        self,
        employee_email: str,
        first_name: str,
        full_name: str,
        department: str,
        image_data: bytes,
        custom_message: Optional[str] = None
    ) -> bool:
        """
        Send birthday email to employee.
        
        Args:
            employee_email: Recipient email address
            first_name: Employee's first name
            full_name: Employee's full name
            department: Employee's department
            image_data: Birthday image as bytes
            custom_message: Optional custom message
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Validate inputs
            if not self._validate_email_inputs(employee_email, first_name, full_name, image_data):
                return False
            
            # Create email message
            msg = self._create_email_message(
                employee_email, first_name, full_name, 
                department, image_data, custom_message
            )
            
            # Send email
            success = self._send_email(msg, employee_email)
            
            if success:
                self.logger.info(f"Birthday email sent successfully to {full_name} ({employee_email})")
            else:
                self.logger.error(f"Failed to send birthday email to {full_name} ({employee_email})")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending birthday email to {full_name}: {e}")
            return False
    
    def _validate_email_inputs(
        self,
        employee_email: str,
        first_name: str,
        full_name: str,
        image_data: bytes
    ) -> bool:
        """Validate email input parameters."""
        if not employee_email or '@' not in employee_email:
            self.logger.error(f"Invalid email address: {employee_email}")
            return False
        
        if not first_name or not full_name:
            self.logger.error("Missing employee name information")
            return False
        
        if not image_data or len(image_data) == 0:
            self.logger.error("Missing or empty image data")
            return False
        
        return True
    
    def _create_email_message(
        self,
        employee_email: str,
        first_name: str,
        full_name: str,
        department: str,
        image_data: bytes,
        custom_message: Optional[str] = None
    ) -> MIMEMultipart:
        """Create the email message with all components."""
        # Create message container
        msg = MIMEMultipart('related')
        msg['From'] = f"{self.template.sender_name} <{self.email_user}>"
        msg['To'] = employee_email
        msg['Subject'] = self.template.subject.format(first_name=first_name)
        
        # Create HTML body
        html_body = self._create_html_body(
            first_name, full_name, department, custom_message
        )
        msg.attach(MIMEText(html_body, 'html'))
        
        # Attach birthday image
        self._attach_birthday_image(msg, image_data)
        
        return msg
    
    def _create_html_body(
        self,
        first_name: str,
        full_name: str,
        department: str,
        custom_message: Optional[str] = None
    ) -> str:
        """Create HTML email body."""
        # Default birthday message
        default_message = (
            f"We hope your special day is filled with happiness, laughter, and joy! "
            f"Thank you for being such a valuable part of our {department} team."
        )
        
        birthday_message = custom_message or default_message
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Happy Birthday {first_name}!</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f9f9f9;
                }}
                .container {{
                    background-color: white;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    color: #e40000;
                    font-size: 2.5em;
                    margin: 0;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
                }}
                .greeting {{
                    font-size: 1.2em;
                    margin-bottom: 20px;
                    color: #555;
                }}
                .birthday-image {{
                    text-align: center;
                    margin: 30px 0;
                }}
                .birthday-image img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                }}
                .message {{
                    font-size: 1.1em;
                    margin: 20px 0;
                    padding: 20px;
                    background-color: #f8f8f8;
                    border-left: 4px solid #e40000;
                    border-radius: 5px;
                }}
                .wishes {{
                    text-align: center;
                    font-style: italic;
                    color: #666;
                    margin: 30px 0;
                    font-size: 1.1em;
                }}
                .signature {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 2px solid #e40000;
                    text-align: center;
                }}
                .signature .company {{
                    font-weight: bold;
                    color: #e40000;
                    font-size: 1.1em;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #888;
                    font-size: 0.9em;
                }}
                .emoji {{
                    font-size: 1.2em;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1><span class="emoji">🎉</span> Happy Birthday! <span class="emoji">🎉</span></h1>
                </div>
                
                <div class="greeting">
                    <p>Dear <strong>{full_name}</strong>,</p>
                </div>
                
                <div class="message">
                    <p>{birthday_message}</p>
                </div>
                
                <div class="birthday-image">
                    <img src="cid:birthday_image" alt="Happy Birthday {first_name}!" />
                </div>
                
                <div class="wishes">
                    <p><span class="emoji">🎂</span> Wishing you a wonderful year ahead filled with success and happiness! <span class="emoji">🎈</span></p>
                </div>
                
                <div class="signature">
                    <p>With warm birthday wishes,</p>
                    <p><strong>{self.template.sender_signature}</strong></p>
                    <p class="company">{self.template.company_name}</p>
                </div>
                
                <div class="footer">
                    <p><em>This is an automated birthday greeting from our HR system.</em></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def _attach_birthday_image(self, msg: MIMEMultipart, image_data: bytes) -> None:
        """Attach birthday image to email."""
        try:
            img_attachment = MIMEImage(image_data)
            img_attachment.add_header('Content-ID', '<birthday_image>')
            img_attachment.add_header('Content-Disposition', 'inline', filename='birthday_card.png')
            msg.attach(img_attachment)
        except Exception as e:
            self.logger.error(f"Error attaching birthday image: {e}")
            raise
    
    def _send_email(self, msg: MIMEMultipart, recipient_email: str) -> bool:
        """Send the email using SMTP."""
        server = None
        try:
            # Create SMTP server connection
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable encryption
            server.login(self.email_user, self.email_password)
            
            # Send email
            server.sendmail(self.email_user, recipient_email, msg.as_string())
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            self.logger.error(f"SMTP Authentication failed: {e}")
            return False
        except smtplib.SMTPRecipientsRefused as e:
            self.logger.error(f"Recipient refused: {e}")
            return False
        except smtplib.SMTPServerDisconnected as e:
            self.logger.error(f"SMTP server disconnected: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error sending email: {e}")
            return False
        finally:
            if server:
                try:
                    server.quit()
                except:
                    pass  # Ignore errors when closing connection
    
    def send_test_email(self, test_recipient: str) -> bool:
        """
        Send a test email to verify email configuration.
        
        Args:
            test_recipient: Email address to send test to
            
        Returns:
            True if test email sent successfully
        """
        try:
            self.logger.info(f"Sending test email to {test_recipient}")
            
            # Create simple test message
            msg = MIMEMultipart()
            msg['From'] = f"{self.template.sender_name} <{self.email_user}>"
            msg['To'] = test_recipient
            msg['Subject'] = "Birthday System Test Email"
            
            test_body = """
            <html>
                <body>
                    <h2>Birthday Email System Test</h2>
                    <p>This is a test email from the birthday automation system.</p>
                    <p>If you receive this email, the system is configured correctly!</p>
                    <p>Best regards,<br>Birthday Automation System</p>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(test_body, 'html'))
            
            success = self._send_email(msg, test_recipient)
            
            if success:
                self.logger.info("Test email sent successfully")
            else:
                self.logger.error("Test email failed")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending test email: {e}")
            return False
    
    def send_bulk_birthday_emails(
        self,
        birthday_employees: list,
        image_data_dict: Dict[str, bytes],
        custom_messages: Optional[Dict[str, str]] = None
    ) -> Dict[str, bool]:
        """
        Send birthday emails to multiple employees.
        
        Args:
            birthday_employees: List of employee dictionaries
            image_data_dict: Dictionary mapping employee ID to image data
            custom_messages: Optional custom messages per employee
            
        Returns:
            Dictionary mapping employee ID to success status
        """
        results = {}
        custom_messages = custom_messages or {}
        
        self.logger.info(f"Sending bulk birthday emails to {len(birthday_employees)} employees")
        
        for employee in birthday_employees:
            empid = employee['empid']
            first_name = employee['first_name']
            full_name = employee['full_name']
            email = employee['email']
            department = employee['department']
            
            # Get image data for this employee
            image_data = image_data_dict.get(empid)
            if not image_data:
                self.logger.warning(f"No image data found for employee {empid}")
                results[empid] = False
                continue
            
            # Get custom message if available
            custom_message = custom_messages.get(empid)
            
            # Send email
            success = self.send_birthday_email(
                employee_email=email,
                first_name=first_name,
                full_name=full_name,
                department=department,
                image_data=image_data,
                custom_message=custom_message
            )
            
            results[empid] = success
        
        # Log summary
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        self.logger.info(f"Bulk email results: {successful}/{total} emails sent successfully")
        
        return results
    
    def validate_smtp_connection(self) -> bool:
        """
        Validate SMTP connection settings.
        
        Returns:
            True if connection can be established
        """
        try:
            self.logger.info("Validating SMTP connection...")
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.quit()
            
            self.logger.info("SMTP connection validation successful")
            return True
            
        except Exception as e:
            self.logger.error(f"SMTP connection validation failed: {e}")
            return False
    
    def get_email_stats(self) -> Dict[str, Any]:
        """Get email service statistics and configuration."""
        return {
            'smtp_server': self.smtp_server,
            'smtp_port': self.smtp_port,
            'email_user': self.email_user,
            'template_subject': self.template.subject,
            'template_sender': self.template.sender_name,
            'template_signature': self.template.sender_signature,
            'template_company': self.template.company_name,
        }


# Example usage and testing
if __name__ == "__main__":
    import os
    import logging
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Example configuration (use environment variables in production)
    email_service = EmailService(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        email_user=os.getenv("EMAIL_USER", "test@gmail.com"),
        email_password=os.getenv("EMAIL_PASSWORD", "test_password")
    )
    
    # Validate SMTP connection
    if email_service.validate_smtp_connection():
        print("✓ SMTP connection is valid")
    else:
        print("✗ SMTP connection failed")
    
    # Send test email
    test_email = os.getenv("TEST_EMAIL")
    if test_email:
        print(f"Sending test email to {test_email}...")
        if email_service.send_test_email(test_email):
            print("✓ Test email sent successfully")
        else:
            print("✗ Test email failed")
    
    # Display service stats
    stats = email_service.get_email_stats()
    print("Email service configuration:")
    for key, value in stats.items():
        print(f"  {key}: {value}")