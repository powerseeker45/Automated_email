# 🎉 Email Automation System - Setup Guide

An automated system that sends personalized birthday and marriage anniversary greeting cards to employees via email.

## 📋 Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [File Setup](#file-setup)
- [Customization](#customization)
- [Running the System](#running-the-system)
- [Troubleshooting](#troubleshooting)
- [Company Email Setup](#company-email-setup)
- [Scheduling](#scheduling)

## ✨ Features

- 🎂 **Automatic Birthday Emails** - Sends personalized birthday cards
- 💕 **Marriage Anniversary Emails** - Sends anniversary greetings
- 🎨 **Customizable Cards** - Add employee names to greeting card images
- 📊 **Comprehensive Logging** - Detailed logs and daily reports
- 🔐 **Secure Configuration** - Environment variables for sensitive data
- 📧 **Daily Reports** - Email summaries sent to administrator
- 🏢 **Company Email Support** - Works with Office 365, Gmail, Exchange
- 🎯 **Font Customization** - Custom fonts, sizes, colors, and positioning

## 🛠️ Prerequisites

- Python 3.7 or higher
- Email account with SMTP access
- App password (for Gmail/Office 365)
- Greeting card image templates (PNG/JPG)

## 📦 Installation

### 1. Clone/Download the Project
```bash
git clone <repository-url>
cd email-automation
```

### 2. Install Required Packages
```bash
pip install pandas pillow python-dotenv
```

### 3. Create Project Structure
```
email-automation/
├── automation_email.py          # Main script
├── generate_csv.py              # CSV generator (optional)
├── .env                         # Your configuration (create this)
├── employees.csv                # Employee data
├── assets
|   |── birthday_card.png            # Birthday card template
|   └── anniversary_card.png         # Anniversary card template
└── output/                      # Auto-created for logs and images
    └── logs/
        └── email_automation.log
```

## ⚙️ Configuration

### 1. Create Environment File

**Option A: Generate Template (Recommended)**
```python
# Uncomment this line in automation_email.py and run once
create_env_template()
```

**Option B: Create .env File Manually**
```env
# Email Automation Configuration

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

# Text Positioning
BIRTHDAY_TEXT_X=100
BIRTHDAY_TEXT_Y=80
ANNIVERSARY_TEXT_X=100
ANNIVERSARY_TEXT_Y=80

# Font Customization
BIRTHDAY_FONT_SIZE=40
ANNIVERSARY_FONT_SIZE=40
BIRTHDAY_FONT_COLOR_R=0
BIRTHDAY_FONT_COLOR_G=0
BIRTHDAY_FONT_COLOR_B=0
```

### 2. Get Email App Password

**For Gmail:**
1. Enable 2-Factor Authentication
2. Go to Google Account Settings → Security
3. Generate App Password for "Mail"
4. Use this password in .env file

**For Office 365:**
1. Go to Microsoft Account Security
2. Enable 2FA and generate App Password
3. Use generated password in .env file

## 📁 File Setup

### 1. Create Employee CSV File
```csv
first_name,last_name,email,birthday,marriage_anniversary,department
John,Doe,john.doe@company.com,1990-06-09,2018-05-20,HR
Jane,Smith,jane.smith@company.com,1985-12-25,NA,Finance
Michael,Brown,michael.brown@company.com,1992-06-09,2020-10-12,Engineering
```

**CSV Generator (Optional):**
```python
python generate_csv.py
```

### 2. Prepare Greeting Card Images

- **Birthday Card**: `assets/birthday_card.png` (recommended size: 800x600px)
- **Anniversary Card**: `assets/anniversary_card.png` (recommended size: 800x600px)
- **Format**: PNG or JPG
- **Text Area**: Leave space where names will be added

## 🎨 Customization

### Text Position
```env
# Position from top-left corner (pixels)
BIRTHDAY_TEXT_X=150      # 150px from left
BIRTHDAY_TEXT_Y=100      # 100px from top
```

### Font Size
```env
BIRTHDAY_FONT_SIZE=50    # Larger text
ANNIVERSARY_FONT_SIZE=30 # Smaller text
```

### Font Color (RGB Values 0-255)
```env
# Red text
BIRTHDAY_FONT_COLOR_R=255
BIRTHDAY_FONT_COLOR_G=0
BIRTHDAY_FONT_COLOR_B=0

# Blue text  
ANNIVERSARY_FONT_COLOR_R=0
ANNIVERSARY_FONT_COLOR_G=0
ANNIVERSARY_FONT_COLOR_B=255
```

### Common Colors
- **Black**: R=0, G=0, B=0
- **White**: R=255, G=255, B=255
- **Red**: R=255, G=0, B=0
- **Gold**: R=255, G=215, B=0
- **Blue**: R=0, G=0, B=255

### Custom Fonts
Edit the `add_text_to_image()` method in `automation_email.py`:
```python
# Add your custom font
font = ImageFont.truetype("fonts/your_font.ttf", font_size)
```

## 🚀 Running the System

### 1. Test Run
```bash
python automation_email.py
```

### 2. Check Output
- View logs: `output/logs/email_automation.log`
- Check images: `output/birthday_*.jpg`, `output/anniversary_*.jpg`
- Daily report: `output/daily_report_YYYYMMDD.txt`

### 3. Verify Emails
- Check your email for daily report
- Verify employee emails were sent successfully

## 🏢 Company Email Setup

### Microsoft 365/Office 365
```env
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SENDER_EMAIL=hr@yourcompany.com
EMAIL_PASSWORD=your_app_password
```

### Google Workspace
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=hr@yourcompany.com
EMAIL_PASSWORD=your_app_password
```

### On-Premise Exchange
```env
SMTP_SERVER=mail.yourcompany.com
SMTP_PORT=587
SENDER_EMAIL=hr@yourcompany.com
EMAIL_PASSWORD=your_domain_password
```

## ⏰ Scheduling

### Windows Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Set Daily trigger at 9:00 AM
4. Action: Start Program
5. Program: `python`
6. Arguments: `C:\path\to\automation_email.py`
7. Start in: `C:\path\to\project\folder`

### Linux/Mac Cron Job
```bash
# Edit crontab
crontab -e

# Add line for daily 9 AM execution
0 9 * * * cd /path/to/project && python3 automation_email.py
```

### Docker (Advanced)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "automation_email.py"]
```

## 🔧 Troubleshooting

### Common Issues

**1. "Missing required email configuration"**
- Check `.env` file exists
- Verify `SENDER_EMAIL` and `EMAIL_PASSWORD` are set
- Remove extra spaces in .env file

**2. "SMTP Authentication failed"**
- Verify app password is correct
- Check 2FA is enabled
- Confirm SMTP server settings

**3. "Module not found" errors**
```bash
pip install pandas pillow python-dotenv
```

**4. "Image file not found"**
- Check image files exist in project folder
- Verify file names match .env configuration
- Ensure correct file extensions (png/jpg)

**5. Text not showing on cards**
- Adjust text position in .env file
- Try different font colors
- Check image format (use RGB images)

### Debug Mode
Add this to see detailed information:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Monitoring

### Daily Reports
- Emailed to sender address automatically
- Contains success/failure statistics
- Lists all birthdays and anniversaries
- Includes error details

### Log Files
- Location: `output/logs/email_automation.log`
- Contains detailed execution information
- Useful for troubleshooting

### Generated Images
- Saved in: `output/` folder
- Named: `birthday_FirstName_LastName_YYYYMMDD.jpg`
- Check these to verify text positioning

## 🔐 Security Best Practices

1. **Never commit .env files** to version control
2. **Use app passwords** instead of account passwords
3. **Restrict file permissions** on .env file
4. **Regular password rotation** for service accounts
5. **Monitor logs** for unauthorized access attempts

## 📞 Support

### Quick Setup Checklist
- [ ] Python 3.7+ installed
- [ ] Required packages installed
- [ ] .env file created with credentials
- [ ] Employee CSV file prepared
- [ ] Greeting card images ready
- [ ] Test run completed successfully
- [ ] Daily scheduling configured

### Getting Help
1. Check logs in `output/logs/email_automation.log`
2. Verify all file paths in .env are correct
3. Test email settings with a simple SMTP test
4. Check firewall/network restrictions

---

## 🎯 Quick Start Summary

1. **Install**: `pip install pandas pillow python-dotenv`
2. **Configure**: Create `.env` with email settings
3. **Prepare**: Add employee CSV and greeting card images
4. **Test**: Run `python automation_email.py`
5. **Schedule**: Set up daily automation
6. **Monitor**: Check logs and daily reports

Happy automating! 🚀