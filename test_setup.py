#!/usr/bin/env python3
"""
Test script for Outlook Web Email Automation setup
This script verifies all requirements are met before running the main automation
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.7+")
        return False

def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name} - Installed")
        return True
    except ImportError:
        print(f"❌ {package_name} - Not installed")
        return False

def check_packages():
    """Check all required packages"""
    print("\n📦 Checking required packages...")
    
    packages = [
        ("pandas", "pandas"),
        ("pillow", "PIL"),
        ("python-dotenv", "dotenv"),
        ("selenium", "selenium"),
        ("webdriver-manager", "webdriver_manager"),
        ("requests", "requests")
    ]
    
    all_installed = True
    missing_packages = []
    
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            all_installed = False
            missing_packages.append(package_name)
    
    if not all_installed:
        print(f"\n💡 Install missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
    
    return all_installed

def check_chrome():
    """Check if Chrome is installed"""
    print("\n🌐 Checking Google Chrome...")
    
    chrome_paths = [
        # Windows
        "C:/Program Files/Google/Chrome/Application/chrome.exe",
        "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
        # macOS
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        # Linux
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium-browser"
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✅ Google Chrome found at: {path}")
            return True
    
    # Try command line
    try:
        result = subprocess.run(["chrome", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Google Chrome found: {result.stdout.strip()}")
            return True
    except:
        pass
    
    try:
        result = subprocess.run(["google-chrome", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Google Chrome found: {result.stdout.strip()}")
            return True
    except:
        pass
    
    print("❌ Google Chrome not found")
    print("💡 Please install Google Chrome from: https://www.google.com/chrome/")
    return False

def check_files():
    """Check if required files exist"""
    print("\n📁 Checking required files...")
    
    files_to_check = [
        (".env", "Environment configuration file"),
        ("employees_test_today.csv", "Employee data CSV"),
        ("assets/Slide1.PNG", "Anniversary card image"),
        ("assets/Slide2.PNG", "Birthday card image")
    ]
    
    all_exist = True
    
    for file_path, description in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - {description}")
        else:
            print(f"❌ {file_path} - {description} (Missing)")
            all_exist = False
    
    if not all_exist:
        print("\n💡 Missing files guidance:")
        print("   - Copy .env.web.template to .env and configure")
        print("   - Create employee CSV with columns: first_name, last_name, email, birthday, anniversary")
        print("   - Add greeting card images to assets/ folder")
    
    return all_exist

def check_env_file():
    """Check .env file configuration"""
    print("\n⚙️ Checking .env configuration...")
    
    if not os.path.exists(".env"):
        print("❌ .env file not found")
        return False
    
    required_vars = [
        "CSV_FILE",
        "BIRTHDAY_CARD", 
        "ANNIVERSARY_CARD",
        "OUTPUT_FOLDER"
    ]
    
    missing_vars = []
    
    try:
        with open(".env", "r") as f:
            env_content = f.read()
        
        for var in required_vars:
            if f"{var}=" not in env_content:
                missing_vars.append(var)
            else:
                print(f"✅ {var} - Configured")
        
        if missing_vars:
            print(f"❌ Missing variables: {', '.join(missing_vars)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False

def create_sample_csv():
    """Create a sample CSV file for testing"""
    print("\n📝 Creating sample employee CSV...")
    
    sample_data = """first_name,last_name,email,birthday,anniversary
John,Doe,john.doe@example.com,1990-06-16,2018-05-20
Jane,Smith,jane.smith@example.com,1985-06-16,2015-08-15
Test,User,test@example.com,1992-06-16,2020-10-12"""
    
    try:
        with open("employees_test_sample.csv", "w") as f:
            f.write(sample_data)
        print("✅ Created employees_test_sample.csv with sample data")
        print("💡 Update the email addresses to real ones for testing")
        return True
    except Exception as e:
        print(f"❌ Failed to create sample CSV: {e}")
        return False

def create_sample_env():
    """Create a sample .env file"""
    print("\n📝 Creating sample .env file...")
    
    env_content = """# Outlook Web Email Automation Configuration
OUTPUT_FOLDER=output
CSV_FILE=employees_test_sample.csv
BIRTHDAY_CARD=assets/Slide2.PNG
ANNIVERSARY_CARD=assets/Slide1.PNG

# Font customization
BIRTHDAY_TEXT_X=50
BIRTHDAY_TEXT_Y=300
BIRTHDAY_FONT_SIZE=64
BIRTHDAY_FONT_COLOR=#4b446a
BIRTHDAY_FONT_PATH=fonts/Inkfree.ttf
BIRTHDAY_CENTER_ALIGN=false

ANNIVERSARY_TEXT_X=0
ANNIVERSARY_TEXT_Y=200
ANNIVERSARY_FONT_SIZE=72
ANNIVERSARY_FONT_COLOR=#72719f
ANNIVERSARY_FONT_PATH=C:/Windows/Fonts/HTOWERT.TTF
ANNIVERSARY_CENTER_ALIGN=true

# Optional Chrome profile
CHROME_USER_DATA_DIR=
"""
    
    try:
        if not os.path.exists(".env"):
            with open(".env", "w") as f:
                f.write(env_content)
            print("✅ Created .env file with default configuration")
        else:
            print("ℹ️ .env file already exists")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def run_browser_test():
    """Test browser automation"""
    print("\n🧪 Testing browser automation...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless")  # Run in background for test
        
        # Setup driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Test navigation
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        if "Google" in title:
            print("✅ Browser automation test successful")
            return True
        else:
            print("❌ Browser automation test failed")
            return False
            
    except Exception as e:
        print(f"❌ Browser automation test failed: {e}")
        return False

def main():
    """Run all setup checks"""
    print("🔧 OUTLOOK WEB EMAIL AUTOMATION - SETUP CHECK")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_packages),
        ("Google Chrome", check_chrome),
        ("Browser Automation", run_browser_test)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} check failed: {e}")
            all_passed = False
    
    # File checks (optional)
    print("\n📁 OPTIONAL FILE CHECKS:")
    print("-" * 30)
    
    files_exist = check_files()
    env_configured = check_env_file()
    
    if not files_exist or not env_configured:
        print("\n🛠️ SETUP ASSISTANCE:")
        print("-" * 20)
        
        if not os.path.exists("employees_test_sample.csv"):
            create_sample_csv()
        
        if not os.path.exists(".env"):
            create_sample_env()
    
    # Final summary
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL CORE REQUIREMENTS MET!")
        print("✅ Ready to run Outlook Web email automation")
        
        if files_exist and env_configured:
            print("✅ All files configured - Ready for production")
        else:
            print("⚠️ Some files missing - Use sample files for testing")
            
        print("\n🚀 NEXT STEPS:")
        print("1. Update .env file with your settings")
        print("2. Add real email addresses to CSV file")
        print("3. Add greeting card images to assets/ folder")
        print("4. Run: python outlook_web_automation.py")
        
    else:
        print("❌ SETUP INCOMPLETE")
        print("Please resolve the issues above before running the automation")
    
    print("=" * 50)

if __name__ == "__main__":
    main()