# 🎂 Birthday Email Automation System

An automated system that generates personalized birthday images and sends them via email to employees on their special day. Features environment-based configuration, automatic scheduling, and comprehensive error handling.

## ✨ Features

- 🎂 **Automated Birthday Detection**: Identifies employees with birthdays today
- 🖼️ **Personalized Images**: Creates custom birthday images with employee names
- 📧 **Professional Email Templates**: Sends beautiful HTML emails with embedded images
- 🔒 **Secure Configuration**: Uses environment variables for sensitive data
- ⏰ **Automated Scheduling**: Runs daily automatically with built-in scheduler
- 🎨 **Custom Templates**: Support for custom PNG templates
- 📊 **Comprehensive Logging**: Detailed logs for monitoring and debugging
- 🛡️ **Error Handling**: Graceful error recovery and detailed error reporting
- 🧪 **Testing Suite**: Comprehensive tests with visual validation

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
git clone <your-repo-url>
cd birthday-automation

# Run setup script (recommended)
python setup.py

# Or install manually
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Create environment file
cp .env.template .env

# Edit with your settings
nano .env
```

Required configuration in `.env`:
```bash
EMAIL_USER=your-email@company.com
EMAIL_PASSWORD=your-gmail-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### 3. Prepare Employee Data

Update `employees.csv` with your employee information:
```csv
empid,first_name,second_name,email,dob,department
EMP001,John,Doe,john.doe@company.com,1990-06-15,Engineering
EMP002,Jane,Smith,jane.smith@company.com,1985-06-04,Marketing
```

### 4. Test the System

```bash
# Run tests
python test_birthday_system.py

# Test with today's birthdays
python birthday_automation.py --run-once
```

### 5. Start Automation

```bash
# Start automated daily scheduler (runs at 9:00 AM daily)
python birthday_automation.py

# Or specify custom time
python birthday_automation.py --schedule-time 08:30
```

## 📧 Gmail Setup

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Google Account Settings → Security → 2-Step Verification
   - Click "App passwords" → Generate password for "Mail"
   - Use this password in your `.env` file (not your regular password)

## 📁 Project Structure

```
birthday-automation/
├── birthday_automation.py      # Main automation script
├── setup.py                   # Setup and installation script
├── test_birthday_system.py    # Comprehensive test suite
├── requirements.txt           # Python dependencies
├── .env.template             # Configuration template
├── .env                      # Your configuration (create from template)
├── employees.csv             # Employee data
├── README.md                 # This file
├── output_img/              # Generated birthday images
├── assets/                  # Optional company assets
│   ├── logo.png
│   └── cake.png
└── logs/                   # Application logs
```

## 🛠️ Usage Options

### Manual Execution
```bash
# Run for today's birthdays
python birthday_automation.py --run-once

# Run for specific date
python birthday_automation.py --run-once --date 2024-12-25

# Run without saving images to disk
python birthday_automation.py --run-once --no-save-images
```

### Automated Scheduling
```bash
# Start scheduler (default: 9:00 AM daily)
python birthday_automation.py

# Custom schedule time
python birthday_automation.py --schedule-time 07:30
```

### System-Level Automation

**Linux/Mac (Cron):**
```bash
# Edit crontab
crontab -e

# Add this line for daily 9:00 AM execution
0 9 * * * cd /path/to/birthday-automation && python birthday_automation.py --run-once
```

**Windows (Task Scheduler):**
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 9:00 AM
4. Action: Start program `python` with arguments `birthday_automation.py --run-once`

## ⚙️ Configuration Options

### Environment Variables (.env file)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EMAIL_USER` | ✅ | - | Sender email address |
| `EMAIL_PASSWORD` | ✅ | - | Email app password |
| `SMTP_SERVER` | ❌ | smtp.gmail.com | SMTP server |
| `SMTP_PORT` | ❌ | 587 | SMTP port |
| `EMPLOYEE_CSV_FILE` | ❌ | employees.csv | Employee data file |
| `CUSTOM_BASE_IMAGE` | ❌ | - | Custom template PNG |
| `OUTPUT_DIR` | ❌ | output_img | Image save directory |
| `COMPANY_NAME` | ❌ | Your Company | Company name in emails |
| `SENDER_TITLE` | ❌ | CEO | Sender title in emails |

### CSV Format

Required columns in your employee CSV:
- `empid`: Unique employee identifier
- `first_name`: Employee's first name
- `second_name`: Employee's last name
- `email`: Email address
- `dob`: Date of birth (YYYY-MM-DD, DD/MM/YYYY, etc.)
- `department`: Department name

## 🎨 Customization

### Custom Birthday Templates

1. Create your birthday template as a PNG file
2. Set the path in `.env`:
   ```bash
   CUSTOM_BASE_IMAGE=path/to/your/template.png
   ```
3. Employee names will be added at the top center

### Company Branding

Place these files in your project directory or `assets/` folder:
- `logo.png` or `airtel_logo.png`: Company logo
- `cake.png`: Birthday cake image

### Email Templates

Modify the `create_email_content()` method in `birthday_automation.py` to customize:
- Email styling and layout
- Message content and tone
- Company branding elements

## 🔍 Monitoring & Logging

### Log Files

The system creates detailed logs in `birthday_automation.log`:
- Employee data loading status
- Birthday detection results
- Image generation progress
- Email sending status
- Error details and stack traces

### Monitoring Commands

```bash
# Watch logs in real-time
tail -f birthday_automation.log

# Check for errors
grep ERROR birthday_automation.log

# View recent activity
tail -n 50 birthday_automation.log
```

### Log Levels

Set log level in `.env`:
```bash
LOG_LEVEL=DEBUG    # Verbose logging
LOG_LEVEL=INFO     # Standard logging (default)
LOG_LEVEL=WARNING  # Warnings and errors only
LOG_LEVEL=ERROR    # Errors only
```

## 🧪 Testing

### Run Test Suite
```bash
# Complete test suite with system check
python test_birthday_system.py

# Unit tests only
python -m unittest test_birthday_system -v
```

### Test Categories

1. **System Compatibility**: Python version, modules, permissions
2. **Employee Data Loading**: CSV parsing, validation, error handling
3. **Birthday Detection**: Date matching, edge cases
4. **Image Generation**: Template creation, personalization
5. **Email Functionality**: Content generation, SMTP handling
6. **Integration Tests**: Complete workflow validation
7. **Visual Tests**: Generate sample images for manual inspection

### Test Outputs

- Unit test results in terminal
- Visual test images in `visual_test_outputs/`
- Test logs and debugging information

## 🔧 Troubleshooting

### Common Issues

**Environment Setup:**
```bash
# "No module named 'dotenv'"
pip install python-dotenv

# "EMAIL_USER and EMAIL_PASSWORD required"
# Edit .env file with your credentials
```

**Email Issues:**
```bash
# "Authentication failed"
# - Use Gmail App Password, not regular password
# - Ensure 2FA is enabled
# - Check EMAIL_USER and EMAIL_PASSWORD in .env
```

**CSV Issues:**
```bash
# "No birthdays found"
# - Check date formats in CSV (use YYYY-MM-DD)
# - Verify employee data loads correctly
# - Check system date and timezone
```

**Image Issues:**
```bash
# "Font loading failed"
# - System fonts not found (uses defaults automatically)
# - Check file permissions

# "Custom image not loading"
# - Verify CUSTOM_BASE_IMAGE path is correct
# - Ensure file is PNG format
```

### Debug Mode

Enable verbose logging in `.env`:
```bash
LOG_LEVEL=DEBUG
```

This provides detailed information about:
- Configuration loading
- Font discovery
- Image processing steps
- Email construction
- SMTP communication

### Performance Issues

For large employee databases:
- Consider batch processing
- Implement email rate limiting
- Use database instead of CSV
- Add progress indicators

## 📊 Advanced Features

### Multiple Email Providers

Update SMTP settings for different providers:

```bash
# Outlook
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587

# Yahoo
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587

# Custom SMTP
SMTP_SERVER=your-smtp-server.com
SMTP_PORT=587
```

### Database Integration

Replace CSV with database by modifying `load_employee_data()`:

```python
def load_employee_data(self) -> List[Employee]:
    # Connect to your database
    # Query employee data
    # Return list of Employee objects
```

### Webhook Notifications

Add webhook support in `process_birthdays()`:

```python
# Send summary to Slack, Teams, etc.
webhook_url = os.getenv('WEBHOOK_URL')
if webhook_url:
    send_webhook_notification(results)
```

### Rich Email Templates

Use HTML email frameworks:
- MJML for responsive designs
- Custom CSS for advanced styling
- Dynamic content based on employee data

## 🔒 Security Best Practices

1. **Environment Variables**: Never commit `.env` to version control
   ```bash
   echo ".env" >> .gitignore
   ```

2. **App Passwords**: Use Gmail App Passwords, not account passwords

3. **File Permissions**: Restrict access to configuration and log files
   ```bash
   chmod 600 .env
   chmod 755 birthday_automation.py
   ```

4. **Data Protection**: Encrypt employee data at rest

5. **Access Control**: Limit who can modify the automation system

6. **Regular Updates**: Keep dependencies updated
   ```bash
   pip list --outdated
   pip install --upgrade package-name
   ```

## 🔄 Maintenance

### Regular Tasks

1. **Update Employee Data**: Keep `employees.csv` current
2. **Monitor Logs**: Check for errors and performance issues
3. **Test Email Delivery**: Verify emails are being sent
4. **Update Templates**: Refresh birthday images seasonally
5. **Backup Configuration**: Store `.env` and employee data securely

### Performance Monitoring

Monitor these metrics:
- Email delivery success rate
- Image generation time
- Memory usage during processing
- Log file size growth

### Scaling Considerations

For organizations with 1000+ employees:
- Implement database storage
- Add email queuing system
- Use distributed scheduling
- Add load balancing
- Implement caching strategies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Update documentation
6. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run code formatting
black birthday_automation.py

# Run linting
flake8 birthday_automation.py

# Run tests
python test_birthday_system.py
```

## 📜 License

This project is provided as-is for educational and internal company use. Modify and distribute according to your organization's policies.

## 🆘 Support

### Getting Help

1. **Check Logs**: Review `birthday_automation.log` for errors
2. **Run Tests**: Execute `python test_birthday_system.py`
3. **Verify Configuration**: Ensure `.env` is properly configured
4. **Test Manually**: Try `python birthday_automation.py --run-once`

### Common Solutions

- **No emails sent**: Check email credentials and SMTP settings
- **Images not generated**: Verify font availability and file permissions
- **Birthday not detected**: Check date formats and CSV structure
- **Scheduler not working**: Ensure process stays running in background

### Reporting Issues

When reporting issues, include:
- Error messages from logs
- Your configuration (without passwords)
- Python version and OS
- Sample employee data (anonymized)

---

**Happy Birthday Automation! 🎉**

*Making every birthday special with automated, personalized greetings.*