# Email Automation with Personalized Greeting Cards

🎉 **Automated Birthday & Anniversary Email System with Custom Greeting Cards**

An advanced Python-based email automation system that generates personalized greeting cards and sends them via SMTP or Outlook automation for employee birthdays and anniversaries. The system includes comprehensive logging, daily reports, and customizable card templates.

## 🌟 Features

- **Dual Email Methods**: SMTP automation OR Outlook GUI automation
- **Automated Daily Processing**: Runs daily to check for birthdays and anniversaries
- **Personalized Greeting Cards**: Generates custom cards with employee names
- **Multi-Template Support**: Separate templates for birthdays and anniversaries
- **Email Integration**: SMTP (Gmail, Outlook, Yahoo) OR Outlook GUI automation
- **Comprehensive Logging**: Detailed logs for monitoring and debugging
- **Daily Reports**: Automated summary reports with statistics
- **Font Customization**: Custom fonts, colors, and positioning
- **Error Handling**: Robust error handling with retry mechanisms
- **Statistics Tracking**: Tracks sent/failed emails and generation metrics
- **Safety Features**: PyAutoGUI failsafe for GUI automation

## 📋 Prerequisites

### Required Python Packages
```bash
pip install pandas smtplib email datetime logging python-dotenv pillow pyautogui
```

### Required Files
- `card_generation.py` - Card generation module (dependency)
- Employee CSV file with birthday/anniversary data
- Birthday card template image (PNG/JPG)
- Anniversary card template image (PNG/JPG)
- Custom fonts (optional)

## 🚀 Quick Start Guide

### Step 1: Clone and Setup
```bash
# Clone the repository
git clone <repository-url>
cd email-automation

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Choose Your Email Method

The system supports two email sending methods:

**Option A: SMTP Automation** (Recommended)
- Uses SMTP servers directly
- Works with Gmail, Outlook, Yahoo, etc.
- More reliable and faster
- No GUI interaction required

**Option B: Outlook GUI Automation**
- Controls Outlook desktop application
- Uses PyAutoGUI for mouse/keyboard control
- Works with any Outlook configuration
- Requires screen coordinate calibration

## 📧 Method A: SMTP Email Automation

### Step 3A: Create SMTP Environment Configuration
```bash
# Generate SMTP environment template
python SMTP_email_automation.py
# Uncomment create_env_template() in main()

# This creates .env.template - copy it to .env
cp .env.template .env
```

### Step 4A: Configure SMTP Settings
Edit `.env` file with your email configuration:

```env
# SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Email Credentials (REQUIRED)
SENDER_EMAIL=your.email@gmail.com
EMAIL_PASSWORD=your_app_password_here
```

#### 📧 Email Provider Setup Guides

**Gmail Setup:**
1. Enable 2-Factor Authentication
2. Generate App Password: Google Account → Security → App Passwords
3. Use App Password (not regular password) in `EMAIL_PASSWORD`
4. Settings: `SMTP_SERVER=smtp.gmail.com`, `SMTP_PORT=587`

**Outlook/Hotmail Setup:**
- `SMTP_SERVER=smtp-mail.outlook.com`
- `SMTP_PORT=587`
- Use regular password or App Password

**Yahoo Setup:**
- `SMTP_SERVER=smtp.mail.yahoo.com`
- `SMTP_PORT=587`
- Enable "Less secure app access" or use App Password

### Step 5A: Run SMTP Automation
```bash
python SMTP_email_automation.py
```

## 🖥️ Method B: Outlook GUI Automation

### Step 3B: Create Outlook Environment Configuration
```bash
# Generate Outlook environment template
python outlook_email_sender.py
# Uncomment create_env_template() in main()

# This creates .env.outlook_template - copy it to .env
cp .env.outlook_template .env
```

### Step 4B: Configure Outlook GUI Settings
Edit `.env` file with your Outlook configuration:

```env
# Outlook GUI Automation Coordinates
# These may need adjustment for your screen resolution

# Insert Tab Coordinates (where to click "Insert" in Outlook ribbon)
OUTLOOK_INSERT_TAB_X=178
OUTLOOK_INSERT_TAB_Y=89

# Picture Button Coordinates (where to click "Picture" in Insert tab)
OUTLOOK_PICTURE_BUTTON_X=554
OUTLOOK_PICTURE_BUTTON_Y=156

# Deselect Coordinates (where to click to deselect image after insertion)
OUTLOOK_DESELECT_X=400
OUTLOOK_DESELECT_Y=300
```

#### 🎯 Screen Resolution Coordinate Guide

**Common screen resolutions and coordinate adjustments:**
- **1920x1080**: Use default values above
- **1366x768**: Reduce all coordinates by ~25%
- **2560x1440**: Increase all coordinates by ~30%
- **4K (3840x2160)**: Double all coordinates

#### 📐 Finding Coordinates
1. Take a screenshot of Outlook with email composition window open
2. Use image editing software (Paint, GIMP) to find pixel coordinates
3. Update the coordinates in .env file
4. Test with one email before bulk processing

**Coordinate Reference Points:**
- **Insert Tab**: Usually in the top ribbon, second or third tab
- **Picture Button**: In Insert tab, usually in "Illustrations" group
- **Deselect Area**: Click in email body area, away from image

### Step 5B: Outlook Prerequisites
Before running Outlook automation:

1. **Install Microsoft Outlook desktop application**
2. **Configure Outlook with your email account**
3. **Set Outlook as default email client**
4. **Close other applications for best results**
5. **Ensure stable screen resolution**

### Step 6B: Run Outlook Automation
```bash
python outlook_email_sender.py
```

**⚠️ Safety Features:**
- PyAutoGUI failsafe is enabled
- Move mouse to top-left corner to stop automation
- 5-second countdown before starting
- Detailed logging of each step

## 📊 Common Configuration (Both Methods)

### Step 7: Prepare Employee Data
Create CSV file with employee information:

```csv
first_name,last_name,email,birthday,anniversary
John,Doe,john.doe@company.com,1990-06-25,2018-05-20
Jane,Smith,jane.smith@company.com,1985-12-25,2015-08-15
Bob,Johnson,bob.johnson@company.com,1992-06-25,2020-10-12
Alice,Brown,alice.brown@company.com,1988-03-14,
Sarah,Wilson,sarah.wilson@company.com,1991-06-25,2019-09-14
```

**CSV Format Requirements:**
- `first_name`: Employee's first name
- `last_name`: Employee's last name  
- `email`: Valid email address
- `birthday`: Format YYYY-MM-DD
- `anniversary`: Format YYYY-MM-DD (leave empty if none)

### Step 8: Prepare Card Templates
- Create birthday card template (recommended: 1280x720 pixels)
- Create anniversary card template (recommended: 1280x720 pixels)
- Save as PNG or JPG in `assets/` folder

## ⚙️ Advanced Configuration

### Card Customization Options

#### Birthday Card Settings
```env
# Text positioning (pixels from top-left)
BIRTHDAY_TEXT_X=50
BIRTHDAY_TEXT_Y=300

# Font customization
BIRTHDAY_FONT_SIZE=64
BIRTHDAY_FONT_COLOR=#4b446a
BIRTHDAY_FONT_PATH=fonts/Inkfree.ttf

# Text alignment
BIRTHDAY_CENTER_ALIGN=false
```

#### Anniversary Card Settings
```env
# Text positioning (X ignored if center-aligned)
ANNIVERSARY_TEXT_X=0
ANNIVERSARY_TEXT_Y=200

# Font customization
ANNIVERSARY_FONT_SIZE=72
ANNIVERSARY_FONT_COLOR=#72719f
ANNIVERSARY_FONT_PATH=C:/Windows/Fonts/HTOWERT.TTF

# Text alignment (recommended: true)
ANNIVERSARY_CENTER_ALIGN=true
```

### Color Codes Reference
```
Popular Birthday Colors:
- Bright Gold: #FFD700
- Party Pink: #FF69B4
- Vibrant Blue: #1E90FF
- Purple: #4b446a

Popular Anniversary Colors:
- Romantic Purple: #800080
- Deep Red: #8B0000
- Rose Gold: #E8B4B8
- Light Purple: #72719f
```

### File Structure
```
project/
├── SMTP_email_automation.py      # SMTP automation script
├── outlook_email_sender.py       # Outlook GUI automation script
├── card_generation.py            # Card generation module
├── .env                          # Environment configuration
├── employees.csv                 # Employee data
├── assets/
│   ├── Slide1.PNG               # Anniversary card template
│   └── Slide2.PNG               # Birthday card template
├── fonts/
│   ├── Inkfree.ttf              # Custom fonts
│   └── Arial-Bold.ttf
└── output/
    ├── logs/
    │   └── email_log.log        # System logs
    ├── daily_report_YYYYMMDD.txt # Daily reports (SMTP)
    ├── outlook_daily_report_YYYYMMDD.txt # Daily reports (Outlook)
    └── generated_cards/         # Generated greeting cards
```

## 🔧 System Architecture

### SMTP Automation Architecture

1. **SMTPEmailAutomation Class**
   - Main orchestrator for SMTP automation
   - Handles SMTP configuration and email sending
   - Manages logging and statistics tracking

2. **Email Processing**
   - Creates HTML email messages with embedded images
   - Handles SMTP authentication and sending
   - Implements retry logic and error handling

### Outlook GUI Automation Architecture

1. **OutlookEmailSender Class**
   - Handles GUI automation using PyAutoGUI
   - Manages mouse clicks and keyboard inputs
   - Coordinates screen interactions with Outlook

2. **IntegratedEmailAutomation Class**
   - Orchestrates card generation and email sending
   - Manages the complete automation workflow
   - Handles statistics and reporting

3. **GUI Automation Workflow**
   ```
   Open Outlook → Maximize Window → Click Insert Tab → Click Picture Button
        ↓               ↓               ↓                    ↓
   Insert Image → Deselect Image → Send Email (Ctrl+Enter) → Next Email
   ```

### Common Components (Both Methods)

1. **Card Generation Integration**
   - Interfaces with `card_generation.py` module
   - Generates personalized greeting cards
   - Handles image processing and text overlay

2. **Reporting System**
   - Generates daily summary reports
   - Tracks success/failure statistics
   - Comprehensive logging system

## 📊 Monitoring and Logging

### Log Files Location
- **Email Logs**: `output/logs/email_log.log` (both methods)
- **Daily Reports (SMTP)**: `output/daily_report_YYYYMMDD.txt`
- **Daily Reports (Outlook)**: `output/outlook_daily_report_YYYYMMDD.txt`
- **Generated Cards**: `output/`

### Daily Report Contents
- Execution summary with timestamps
- Birthday/Anniversary processing statistics
- Success/failure counts
- List of people contacted
- Error details and troubleshooting info
- Automation duration and performance metrics

### Statistics Tracked
- Cards generated (birthday/anniversary)
- Emails sent successfully
- Failed email attempts
- Processing duration
- Error occurrences with stack traces
- GUI automation step timings (Outlook method)

## 🛠️ Troubleshooting Guide

### SMTP Method Issues

**1. SMTP Authentication Failed**
```
Solution: 
- Verify email credentials in .env
- For Gmail: Use App Password, not regular password
- Check 2FA is enabled for Gmail
- Verify SMTP server and port settings
```

**2. Email Sending Failed**
```
Solution:
- Check internet connectivity
- Verify recipient email addresses
- Check SMTP server rate limits
- Review firewall/antivirus settings
```

### Outlook GUI Method Issues

**1. Coordinate Issues**
```
Solution:
- Take screenshot of Outlook interface
- Use image editing software to find exact coordinates
- Update coordinates in .env file
- Test with different screen resolutions
```

**2. Outlook Not Opening**
```
Solution:
- Ensure Outlook is set as default email client
- Check if Outlook is already running
- Verify mailto protocol is properly configured
- Restart Outlook if necessary
```

**3. Image Insertion Fails**
```
Solution:
- Check if image files exist at specified paths
- Ensure file permissions allow reading
- Verify image file formats are supported (PNG, JPG)
- Check file path length limitations
```

**4. Automation Stops Unexpectedly**
```
Solution:
- Check PyAutoGUI failsafe (mouse in top-left corner)
- Review logs for specific error messages
- Ensure no dialog boxes are blocking automation
- Close unnecessary applications
```

**5. Wrong Clicks/GUI Issues**
```
Solution:
- Verify screen resolution matches coordinate settings
- Update coordinates for your specific setup
- Ensure Outlook window is maximized
- Check for Windows scaling settings (should be 100%)
```

### Common Issues (Both Methods)

**1. Card Generation Failed**
```
Solution:
- Verify card_generation.py is present
- Check template image paths exist
- Ensure fonts are installed/accessible
- Verify image permissions
```

**2. CSV Processing Errors**
```
Solution:
- Check CSV format matches required columns
- Verify date formats (YYYY-MM-DD)
- Ensure no special characters in names
- Check file encoding (UTF-8 recommended)
```

### Debug Mode
Enable detailed logging by modifying the logger level:
```python
self.logger.setLevel(logging.DEBUG)
```

## 🔒 Security Considerations

### Email Security (Both Methods)
- Use App Passwords instead of regular passwords
- Enable 2-Factor Authentication
- Store credentials in environment variables (.env)
- Never commit passwords to version control

### SMTP Security
- Use TLS/SSL encryption (port 587)
- Verify SMTP server certificates
- Monitor for suspicious sending patterns
- Implement rate limiting if needed

### Outlook GUI Security
- Ensure Outlook account is properly secured
- Monitor for unauthorized access
- Keep Outlook application updated
- Use screen lock when automation is running

### File Security
- Restrict access to .env file (chmod 600)
- Keep employee data CSV secure
- Regularly rotate email passwords
- Monitor log files for unauthorized access

## 📅 Automation and Scheduling

### Windows Task Scheduler

**For SMTP Method:**
```batch
# Create batch file (run_smtp_automation.bat)
@echo off
cd /d "C:\path\to\project"
python SMTP_email_automation.py
```

**For Outlook Method:**
```batch
# Create batch file (run_outlook_automation.bat)
@echo off
cd /d "C:\path\to\project"
python outlook_email_sender.py
```

**Schedule Settings:**
- Trigger: Daily at 9:00 AM
- Action: Start program → run_automation.bat
- Conditions: Start only if network available
- For Outlook: Ensure user is logged in (GUI required)

### Linux Cron Job (SMTP Only)
```bash
# Edit crontab
crontab -e

# Add daily execution at 9:00 AM
0 9 * * * /usr/bin/python3 /path/to/SMTP_email_automation.py
```

**Note**: Outlook GUI automation requires Windows with active desktop session

### macOS Launchd (SMTP Only)
Create `com.company.emailautomation.plist` in `~/Library/LaunchAgents/`

## 🎨 Customization Examples

### Template Design Guidelines
- **Resolution**: 1280x720 pixels recommended
- **Format**: PNG for transparency, JPG for photos
- **Text Areas**: Leave space for dynamic text overlay
- **Colors**: Consider brand colors and readability
- **Fonts**: Ensure fonts are installed on system

### Custom Font Installation
```bash
# Windows
Copy fonts to C:\Windows\Fonts\

# Linux
Copy fonts to ~/.fonts/ or /usr/share/fonts/

# macOS  
Copy fonts to ~/Library/Fonts/
```

### Outlook Coordinate Calibration

**Step-by-step coordinate finding:**
1. Open Outlook and create new email
2. Take screenshot (Windows: Win+Shift+S)
3. Open screenshot in Paint or image editor
4. Hover over UI elements to see coordinates
5. Update .env file with exact coordinates
6. Test with single email first

**Pro Tips for Coordinate Setup:**
- Use consistent screen resolution
- Disable Windows display scaling (set to 100%)
- Always maximize Outlook window before taking coordinates
- Test coordinates after any Outlook updates

## 🆚 SMTP vs Outlook Method Comparison

| Feature | SMTP Method | Outlook GUI Method |
|---------|-------------|-------------------|
| **Reliability** | ⭐⭐⭐⭐⭐ High | ⭐⭐⭐ Medium |
| **Speed** | ⭐⭐⭐⭐⭐ Fast | ⭐⭐ Slower |
| **Setup Complexity** | ⭐⭐ Easy | ⭐⭐⭐⭐ Complex |
| **Cross-platform** | ⭐⭐⭐⭐⭐ All platforms | ⭐ Windows only |
| **GUI Dependency** | ✅ None | ❌ Requires active desktop |
| **Email Providers** | ✅ Most SMTP servers | ❌ Outlook only |
| **Automation Stability** | ⭐⭐⭐⭐⭐ Very stable | ⭐⭐⭐ Coordinate dependent |
| **Server Scheduling** | ✅ Works on servers | ❌ Desktop required |

**Recommendation**: Use SMTP method unless you specifically need Outlook desktop features or have SMTP restrictions.

## 🤝 Contributing

### Development Setup
```bash
# Fork the repository
git clone https://github.com/yourusername/email-automation
cd email-automation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements-dev.txt
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints where applicable
- Include docstrings for all functions
- Add comprehensive error handling
- Write unit tests for new features

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

### Getting Help
- Check the troubleshooting guide above
- Review log files for error details
- Verify configuration settings
- Test with a small employee dataset first

### Bug Reports
When reporting issues, include:
- Which method you're using (SMTP or Outlook)
- Error messages from logs
- Configuration settings (without passwords)
- Python version and OS
- Steps to reproduce the issue
- For Outlook method: Screen resolution and Outlook version

### Feature Requests
- Describe the use case
- Explain expected behavior
- Consider implementation complexity
- Check existing issues first
- Specify if for SMTP, Outlook, or both methods

---

## 📚 Additional Resources

- [Python SMTP Documentation](https://docs.python.org/3/library/smtplib.html)
- [PyAutoGUI Documentation](https://pyautogui.readthedocs.io/)
- [Pillow Image Processing](https://pillow.readthedocs.io/)
- [Email MIME Documentation](https://docs.python.org/3/library/email.mime.html)
- [Environment Variables Best Practices](https://12factor.net/config)
- [Microsoft Outlook Automation](https://docs.microsoft.com/en-us/office/vba/api/outlook.application)

---

**🎯 Quick Method Selection Guide:**

- **Choose SMTP** if you want: Reliability, speed, cross-platform support, server automation
- **Choose Outlook GUI** if you need: Specific Outlook features, existing Outlook setup, corporate email restrictions
