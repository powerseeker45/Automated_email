# Birthday Image Generator

An automated system that generates personalized birthday images and sends them via email to employees on their special day. The system is optimized for performance and supports both auto-generated and custom birthday templates.

## To Do:-
1. change the sender login password from app password to environment variable.
2. this code currently needs to be run everyday manually, automate so dont have to do this


## Features

- 🎂 **Automated Birthday Detection**: Automatically identifies employees with birthdays today
- 🖼️ **Personalized Images**: Creates custom birthday images with employee names
- 📧 **Email Integration**: Sends beautiful HTML emails with embedded birthday images
- 🎨 **Custom Templates**: Support for using your own PNG templates
- ⚡ **Performance Optimized**: Creates base template once and reuses it for multiple employees
- 💾 **Image Saving**: Optionally saves generated images to disk
- 🛡️ **Error Handling**: Robust error handling with graceful fallbacks

## Prerequisites

### Required Python Packages

```bash
pip install pandas pillow smtplib datetime
```

### Required Files

1. **Employee CSV file** (`employees.csv`) with columns:
   - `empid`: Employee ID
   - `first_name`: Employee's first name
   - `second_name`: Employee's last name
   - `email`: Employee's email address
   - `dob`: Date of birth (various formats supported)
   - `department`: Employee's department

2. **Optional Image Assets**:
   - `airtel_logo.png`: Company logo (150x150px recommended)
   - `cake.png`: Birthday cake image (200x200px recommended)
   - `arialbd.ttf`: Arial Bold font file (falls back to system default if not found)

3. **Optional Custom Template**:
   - Any PNG file to use as birthday template background

## Installation

1. Clone or download the script
2. Install required Python packages
3. Prepare your CSV file with employee data
4. Configure email settings in the script
5. Add optional image assets to the same directory

## Configuration

### Email Settings

Update these variables in the `main()` function:

```python
CSV_FILE = "employees.csv"                    # Path to your employee CSV
SMTP_SERVER = "smtp.gmail.com"               # Your SMTP server
SMTP_PORT = 587                              # SMTP port
EMAIL_USER = "your-email@company.com"        # Sender email
EMAIL_PASSWORD = "your-app-password"         # Email password/app password
CUSTOM_BASE_IMAGE = None                     # Path to custom PNG template (optional)
```

### CSV Format Example

```csv
empid,first_name,second_name,email,dob,department
001,John,Doe,john.doe@company.com,15/06/1990,Engineering
002,Jane,Smith,jane.smith@company.com,04/06/1985,Marketing
003,Bob,Johnson,bob.johnson@company.com,04/06/1992,Sales
```

### Supported Date Formats

The system automatically handles various date formats:
- `DD/MM/YYYY`
- `MM/DD/YYYY` 
- `YYYY-MM-DD`
- And other common formats

## Usage

### Basic Usage

```python
python birthday_generator.py
```

The script will:
1. Check for today's birthdays
2. Generate personalized images
3. Send birthday emails
4. Save images to `output_img/` directory

### Using Custom Templates

1. Create your birthday template as a PNG file
2. Update the configuration:

```python
CUSTOM_BASE_IMAGE = "my_birthday_template.png"
```

3. Run the script normally

The system will use your custom image and add employee names to it.

### Programmatic Usage

```python
from birthday_generator import BirthdayImageGenerator

# Initialize
birthday_gen = BirthdayImageGenerator(
    csv_file="employees.csv",
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    email_user="sender@company.com",
    email_password="app-password",
    base_image_path="custom_template.png"  # Optional
)

# Process birthdays
birthday_gen.process_birthdays(save_images=True)
```

## Generated Image Details

### Auto-Generated Template Features

- **Dimensions**: 800x624 pixels
- **Background**: Company red (#e40000)
- **Elements**: 
  - Company logo (top-right)
  - Personalized greeting
  - "Happy Birthday!" message
  - Cake illustration
  - Birthday wishes text
  - Confetti animation effect

### Custom Template Usage

- Use any PNG image as your base template
- Employee names are added at the top center
- Original image dimensions are preserved
- White text color for name (ensure good contrast)

## Output

### Generated Files

Images are saved in `output_img/` directory with format:
```
birthday_{empid}_{full_name}_{date}.png
```

Example: `birthday_001_John_Doe_20240604.png`

### Email Content

- **Subject**: 🎉 Happy Birthday [FirstName]! 🎉
- **Content**: Personalized HTML email with embedded image
- **Sender**: Configured email address
- **Signature**: CEO, Bharti Airtel (customizable)

## Email Setup

### Gmail Configuration

1. Enable 2-Factor Authentication
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. Use the app password in `EMAIL_PASSWORD`

### Other Email Providers

Update `SMTP_SERVER` and `SMTP_PORT`:
- **Outlook**: smtp-mail.outlook.com:587
- **Yahoo**: smtp.mail.yahoo.com:587
- **Custom**: Contact your IT department

## Performance Optimization

The system includes several optimizations:

- **Single Base Image**: Template created once, reused for all employees
- **Font Caching**: Fonts loaded once and cached
- **Memory Efficient**: Uses image copies instead of recreation
- **Error Resilience**: Continues processing even if individual emails fail

## Troubleshooting

### Common Issues

1. **"No birthdays today!"**
   - Check date formats in CSV
   - Verify system date
   - Ensure CSV has valid birth dates

2. **Email sending fails**
   - Check SMTP settings
   - Verify email credentials
   - Ensure app password is used (not account password)

3. **Images not generating**
   - Check file permissions
   - Verify image assets exist
   - Check font file availability

4. **Custom image not loading**
   - Verify file path is correct
   - Ensure PNG format
   - Check file permissions

### Debug Mode

Add print statements to see processing details:

```python
birthday_gen.process_birthdays(save_images=True)
```

The system automatically prints status messages for debugging.

## Customization

### Modify Email Content

Edit the `html_body` in `send_birthday_email()` method:

```python
html_body = f"""
<html>
    <body>
        <h2>Happy Birthday, {first_name}!</h2>
        <!-- Customize your email content here -->
    </body>
</html>
"""
```

### Change Image Dimensions

Modify `width, height = 800, 624` in `create_base_image()`:

```python
width, height = 1200, 800  # Your preferred size
```

### Adjust Text Positioning

Update coordinates in `add_name_to_image()`:

```python
name_y_position = 100  # Adjust vertical position
```

## Scheduling

### Daily Automation

Set up daily execution using:

**Windows (Task Scheduler)**:
1. Open Task Scheduler
2. Create Basic Task
3. Set daily trigger
4. Set action to run Python script

**Linux/Mac (Cron)**:
```bash
# Run daily at 9:00 AM
0 9 * * * /usr/bin/python3 /path/to/birthday_generator.py
```

## Security Notes

- Store email passwords securely (consider environment variables)
- Keep employee data CSV secure
- Use app passwords instead of account passwords
- Regularly update email credentials

## Contributing

Feel free to submit issues and pull requests to improve the system:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is provided as-is for educational and internal company use.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review error messages in console output
3. Verify all configuration settings
4. Test with a small subset of data first

---

*Happy Birthday automation! 🎉*



