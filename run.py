#!/usr/bin/env python3
"""
Simple runner script for Birthday Email Automation
This provides an easy way to run the automation with common options
"""

import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print application banner"""
    print("🎂 Birthday Email Automation System")
    print("=" * 50)

def check_setup():
    """Check if the system is properly set up"""
    issues = []
    
    # Check if main script exists
    if not Path("birthday_automation.py").exists():
        issues.append("birthday_automation.py not found")
    
    # Check if .env exists
    if not Path(".env").exists():
        if Path(".env.template").exists():
            issues.append(".env file not found. Copy .env.template to .env and configure it")
        else:
            issues.append(".env file not found")
    
    # Check if employees.csv exists
    if not Path("employees.csv").exists():
        issues.append("employees.csv not found")
    
    if issues:
        print("⚠️  Setup Issues Found:")
        for issue in issues:
            print(f"   - {issue}")
        print("\nPlease run 'python setup.py' first to set up the system.")
        return False
    
    return True

def run_setup():
    """Run the setup script"""
    print("🔧 Running setup...")
    try:
        subprocess.run([sys.executable, "setup.py"], check=True)
        print("✅ Setup completed!")
    except subprocess.CalledProcessError:
        print("❌ Setup failed. Please check the error messages above.")
        return False
    except FileNotFoundError:
        print("❌ setup.py not found.")
        return False
    return True

def run_tests():
    """Run the test suite"""
    print("🧪 Running tests...")
    try:
        subprocess.run([sys.executable, "test_birthday_system.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Some tests failed. Check the output above.")
        return False
    except FileNotFoundError:
        print("❌ test_birthday_system.py not found.")
        return False
    return True

def run_once():
    """Run the automation once"""
    print("🎯 Running birthday automation once...")
    try:
        subprocess.run([sys.executable, "birthday_automation.py", "--run-once"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Automation failed. Check the logs for details.")
        return False
    except FileNotFoundError:
        print("❌ birthday_automation.py not found.")
        return False
    return True

def start_scheduler():
    """Start the automatic scheduler"""
    print("⏰ Starting automatic scheduler...")
    print("Press Ctrl+C to stop the scheduler")
    try:
        subprocess.run([sys.executable, "birthday_automation.py"])
    except KeyboardInterrupt:
        print("\n🛑 Scheduler stopped by user")
    except subprocess.CalledProcessError:
        print("❌ Scheduler failed. Check the logs for details.")
        return False
    except FileNotFoundError:
        print("❌ birthday_automation.py not found.")
        return False
    return True

def show_menu():
    """Show interactive menu"""
    while True:
        print("\n📋 What would you like to do?")
        print("1. 🔧 Run setup")
        print("2. 🧪 Run tests")
        print("3. 🎯 Run once (check today's birthdays)")
        print("4. ⏰ Start scheduler (run daily automatically)")
        print("5. 📖 Show help")
        print("6. 🚪 Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            run_setup()
        elif choice == "2":
            if not check_setup():
                continue
            run_tests()
        elif choice == "3":
            if not check_setup():
                continue
            run_once()
        elif choice == "4":
            if not check_setup():
                continue
            start_scheduler()
        elif choice == "5":
            show_help()
        elif choice == "6":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-6.")

def show_help():
    """Show help information"""
    print("\n📖 Birthday Email Automation Help")
    print("=" * 40)
    print("\n🚀 Quick Start:")
    print("1. Run setup: python run.py (choose option 1)")
    print("2. Configure .env file with your email settings")
    print("3. Update employees.csv with your employee data")
    print("4. Test: python run.py (choose option 2)")
    print("5. Run: python run.py (choose option 3 or 4)")
    
    print("\n📧 Gmail Setup:")
    print("- Enable 2-Factor Authentication")
    print("- Generate App Password (not regular password)")
    print("- Use App Password in .env file")
    
    print("\n📁 File Structure:")
    print("- .env: Your configuration (email, company info)")
    print("- employees.csv: Employee data with birthdays")
    print("- output_img/: Generated birthday images")
    print("- birthday_automation.log: Application logs")
    
    print("\n🔧 Command Line Options:")
    print("python birthday_automation.py --run-once")
    print("python birthday_automation.py --schedule-time 08:30")
    print("python birthday_automation.py --create-env")
    
    print("\n📋 For detailed documentation, see README.md")

def main():
    """Main function"""
    print_banner()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ["setup", "--setup", "-s"]:
            run_setup()
        elif arg in ["test", "--test", "-t"]:
            if check_setup():
                run_tests()
        elif arg in ["run", "--run", "-r"]:
            if check_setup():
                run_once()
        elif arg in ["schedule", "--schedule", "-a"]:
            if check_setup():
                start_scheduler()
        elif arg in ["help", "--help", "-h"]:
            show_help()
        else:
            print(f"❌ Unknown argument: {arg}")
            print("Use 'python run.py help' for available options")
            return 1
    else:
        # Interactive mode
        show_menu()
    
    return 0

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        exit(0)