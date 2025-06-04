#!/usr/bin/env python3
"""
Setup script for Birthday Email Automation System
This script helps with initial setup and configuration
"""

import os
import subprocess
import sys
from pathlib import Path

def install_requirements():
    """Install required Python packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False
    return True

def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    directories = ['output_img', 'assets', 'logs']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_file = Path('.env')
    template_file = Path('.env.template')
    
    if not env_file.exists():
        if template_file.exists():
            # Copy template to .env
            with open(template_file, 'r') as f:
                content = f.read()
            
            with open(env_file, 'w') as f:
                f.write(content)
            
            print("✅ Created .env file from template")
            print("📝 Please edit .env file with your configuration before running the application")
        else:
            print("❌ .env.template file not found")
            return False
    else:
        print("ℹ️  .env file already exists")
    
    return True

def create_gitignore():
    """Create .gitignore file to protect sensitive data"""
    gitignore_content = """# Birthday Automation - Sensitive Files
.env
*.log
output_img/
logs/

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

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
    
    gitignore_file = Path('.gitignore')
    if not gitignore_file.exists():
        with open(gitignore_file, 'w') as f:
            f.write(gitignore_content)
        print("✅ Created .gitignore file")
    else:
        print("ℹ️  .gitignore file already exists")

def check_python_version():
    """Check if Python version is compatible"""
    required_version = (3, 7)
    current_version = sys.version_info[:2]
    
    if current_version < required_version:
        print(f"❌ Python {required_version[0]}.{required_version[1]}+ required. Current version: {current_version[0]}.{current_version[1]}")
        return False
    
    print(f"✅ Python version {current_version[0]}.{current_version[1]} is compatible")
    return True

def show_next_steps():
    """Show next steps to user"""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("\n📋 NEXT STEPS:")
    print("\n1. Configure your settings:")
    print("   - Edit .env file with your email credentials")
    print("   - Update employees.csv with your employee data")
    print("\n2. Gmail App Password Setup:")
    print("   - Enable 2-Factor Authentication on Gmail")
    print("   - Generate App Password: Google Account → Security → App Passwords")
    print("   - Use the App Password in EMAIL_PASSWORD (not your regular password)")
    print("\n3. Optional: Add company assets:")
    print("   - Place logo.png in assets/ folder")
    print("   - Place cake.png in assets/ folder")
    print("\n4. Test the system:")
    print("   python birthday_automation.py --run-once")
    print("\n5. Start automated scheduling:")
    print("   python birthday_automation.py")
    print("\n📚 For detailed instructions, see README.md")
    print("="*60)

def main():
    """Main setup function"""
    print("🎂 Birthday Email Automation - Setup Script")
    print("="*50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Create .env file
    if not create_env_file():
        sys.exit(1)
    
    # Create .gitignore
    create_gitignore()
    
    # Show next steps
    show_next_steps()

if __name__ == "__main__":
    main()