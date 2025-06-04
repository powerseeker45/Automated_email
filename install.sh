#!/bin/bash

# Birthday Email Automation - Installation Script
# This script sets up the complete birthday automation system

set -e  # Exit on any error

echo "🎂 Birthday Email Automation - Installation Script"
echo "================================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.7+ and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
echo "✅ Python $PYTHON_VERSION detected"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    echo "Please install pip3 and try again."
    exit 1
fi

echo "✅ pip3 is available"

# Create virtual environment (optional but recommended)
read -p "🤔 Create virtual environment? (recommended) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv birthday_env
    echo "📦 Activating virtual environment..."
    source birthday_env/bin/activate
    echo "✅ Virtual environment created and activated"
    echo "💡 To activate in future: source birthday_env/bin/activate"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install pandas pillow schedule python-dotenv

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p output_img
mkdir -p assets
mkdir -p logs
echo "✅ Directories created"

# Create .env file from template if it doesn't exist
if [ ! -f .env ]; then
    if [ -f .env.template ]; then
        echo "⚙️ Creating .env file from template..."
        cp .env.template .env
        echo "✅ .env file created"
    else
        echo "⚙️ Creating .env file..."
        cat > .env << 'EOF'
# Birthday Email Automation Configuration

# Required: Email Configuration
EMAIL_USER=your-email@company.com
EMAIL_PASSWORD=your-app-password-here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Optional: File Paths
EMPLOYEE_CSV_FILE=employees.csv
CUSTOM_BASE_IMAGE=
OUTPUT_DIR=output_img

# Optional: Company Information
COMPANY_NAME=Your Company Name
SENDER_TITLE=CEO

# Optional: Logging
LOG_LEVEL=INFO
EOF
        echo "✅ .env file created"
    fi
else
    echo "ℹ️ .env file already exists"
fi

# Create sample employees.csv if it doesn't exist
if [ ! -f employees.csv ]; then
    echo "📋 Creating sample employees.csv..."
    cat > employees.csv << 'EOF'
empid,first_name,second_name,email,dob,department
EMP001,Alice,Johnson,alice.johnson@company.com,1990-06-04,Engineering
EMP002,Bob,Smith,bob.smith@company.com,1985-06-05,Marketing
EMP003,Carol,Davis,carol.davis@company.com,1992-06-04,HR
EMP004,David,Wilson,david.wilson@company.com,1988-06-05,Engineering
EMP005,Emma,Brown,emma.brown@company.com,1995-12-25,Finance
EOF
    echo "✅ Sample employees.csv created"
else
    echo "ℹ️ employees.csv already exists"
fi

# Create .gitignore
if [ ! -f .gitignore ]; then
    echo "🔒 Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Birthday Automation - Sensitive Files
.env
*.log
output_img/
logs/
visual_test_outputs/

# Employee Data (keep private)
employees.csv
employee_data/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environments
.env
.venv
env/
venv/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF
    echo "✅ .gitignore created"
else
    echo "ℹ️ .gitignore already exists"
fi

# Create sample assets if they don't exist
if [ -f create_sample_assets.py ]; then
    echo "🎨 Creating sample assets..."
    python3 create_sample_assets.py
else
    echo "ℹ️ Sample assets script not found, skipping asset creation"
fi

# Make scripts executable
chmod +x run.py 2>/dev/null || true
chmod +x birthday_automation.py 2>/dev/null || true

# Run tests if available
if [ -f test_birthday_system.py ]; then
    echo "🧪 Running system tests..."
    python3 test_birthday_system.py
else
    echo "ℹ️ Test script not found, skipping tests"
fi

echo ""
echo "🎉 Installation completed successfully!"
echo "================================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. 📧 Configure Email Settings:"
echo "   - Edit .env file with your email credentials"
echo "   - Use Gmail App Password (not regular password)"
echo ""
echo "2. 👥 Update Employee Data:"
echo "   - Edit employees.csv with your employee information"
echo "   - Ensure date format is YYYY-MM-DD"
echo ""
echo "3. 🧪 Test the System:"
echo "   python3 birthday_automation.py --run-once"
echo ""
echo "4. 🚀 Start Automated Scheduler:"
echo "   python3 birthday_automation.py"
echo ""
echo "5. 📚 For detailed help:"
echo "   python3 run.py help"
echo ""
echo "📁 Important Files:"
echo "   - .env: Your configuration (keep private!)"
echo "   - employees.csv: Employee data"
echo "   - birthday_automation.log: Application logs"
echo "   - output_img/: Generated birthday images"
echo ""
echo "🔐 Security Reminder:"
echo "   - Never commit .env file to version control"
echo "   - Use Gmail App Passwords, not regular passwords"
echo "   - Keep employee data secure"
echo ""
echo "Happy Birthday Automation! 🎂"