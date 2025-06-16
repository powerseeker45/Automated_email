#!/usr/bin/env python3
"""
Simple test script to debug Outlook login issues
This script will help identify the correct element selectors for your Outlook version
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def setup_browser():
    """Setup Chrome browser"""
    try:
        print("🔧 Setting up Chrome browser...")
        
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Don't use headless mode for this test
        # chrome_options.add_argument("--headless")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ Chrome browser setup successful")
        return driver
        
    except Exception as e:
        print(f"❌ Failed to setup browser: {e}")
        return None

def analyze_page_elements(driver):
    """Analyze page elements to find the right selectors"""
    print("\n🔍 ANALYZING PAGE ELEMENTS...")
    print("=" * 50)
    
    # Basic page info
    print(f"📄 URL: {driver.current_url}")
    print(f"📝 Title: {driver.title}")
    
    # Check for various element types
    element_checks = [
        # Buttons
        ("Buttons with 'message'", "//button[contains(text(), 'message') or contains(@aria-label, 'message')]"),
        ("Buttons with 'compose'", "//button[contains(text(), 'compose') or contains(@aria-label, 'compose') or contains(@aria-label, 'Compose')]"),
        ("Buttons with 'new'", "//button[contains(text(), 'New') or contains(@aria-label, 'New')]"),
        
        # Common Outlook elements
        ("Inbox elements", "//div[contains(text(), 'Inbox') or contains(@aria-label, 'Inbox')]"),
        ("Mail elements", "//div[contains(@class, 'mail') or contains(@aria-label, 'mail')]"),
        ("Profile elements", "//button[contains(@aria-label, 'Account') or contains(@aria-label, 'Profile')]"),
        
        # Sign-in elements
        ("Sign-in links", "//a[contains(text(), 'Sign in') or contains(@href, 'login')]"),
        ("Login elements", "//div[contains(@class, 'login') or contains(@class, 'signin')]"),
        
        # Generic interactive elements
        ("All buttons", "//button"),
        ("All links", "//a"),
        ("All inputs", "//input"),
        
        # Role-based elements
        ("Main content", "//main[@role='main'] | //div[@role='main']"),
        ("Lists", "//div[@role='list'] | //ul[@role='list']"),
        ("Navigation", "//nav | //div[@role='navigation']")
    ]
    
    for check_name, selector in element_checks:
        try:
            elements = driver.find_elements(By.XPATH, selector)
            print(f"\n🔸 {check_name}: Found {len(elements)} elements")
            
            # Show details for first few elements
            for i, element in enumerate(elements[:3]):  # Show max 3 elements
                try:
                    tag = element.tag_name
                    text = element.text[:100] if element.text else "(no text)"
                    aria_label = element.get_attribute("aria-label") or "(no aria-label)"
                    class_attr = element.get_attribute("class") or "(no class)"
                    visible = element.is_displayed()
                    enabled = element.is_enabled()
                    
                    print(f"   [{i+1}] {tag}: visible={visible}, enabled={enabled}")
                    print(f"       Text: {text}")
                    print(f"       Aria-label: {aria_label}")
                    print(f"       Class: {class_attr}")
                    
                except Exception as e:
                    print(f"   [{i+1}] Error getting element details: {e}")
                    
        except Exception as e:
            print(f"❌ Error checking {check_name}: {e}")

def test_outlook_login():
    """Test Outlook login and analyze page structure"""
    driver = None
    
    try:
        # Setup browser
        driver = setup_browser()
        if not driver:
            return False
        
        print("\n🌐 Navigating to Outlook...")
        driver.get("https://outlook.live.com")
        
        # Wait for initial page load
        time.sleep(5)
        
        print("\n📊 INITIAL PAGE ANALYSIS:")
        analyze_page_elements(driver)
        
        # Take screenshot
        try:
            screenshot_path = f"outlook_debug_initial_{int(time.time())}.png"
            driver.save_screenshot(screenshot_path)
            print(f"\n📸 Screenshot saved: {screenshot_path}")
        except Exception as e:
            print(f"⚠️ Could not save screenshot: {e}")
        
        # Check if we need to login
        print("\n🔍 CHECKING LOGIN STATUS...")
        
        # Look for compose button (indicates logged in)
        compose_selectors = [
            "//button[contains(@aria-label, 'New message')]",
            "//button[contains(@aria-label, 'Compose')]",
            "//button[contains(text(), 'New message')]",
            "//span[contains(text(), 'New message')]",
            "//button[contains(@title, 'New message')]"
        ]
        
        already_logged_in = False
        for selector in compose_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements and any(elem.is_displayed() for elem in elements):
                    print(f"✅ Found compose button with selector: {selector}")
                    already_logged_in = True
                    break
            except:
                continue
        
        if already_logged_in:
            print("🎉 Already logged in to Outlook!")
        else:
            print("🔐 Not logged in, manual login required...")
            
            # Prompt for manual login
            print("\n" + "="*60)
            print("🔐 MANUAL LOGIN REQUIRED")
            print("="*60)
            print("Please log in to your Outlook account in the browser window.")
            print("After logging in successfully, return here and press Enter.")
            print("="*60)
            
            input("Press Enter after logging in...")
            
            # Wait for page to update
            time.sleep(3)
            
            print("\n📊 POST-LOGIN PAGE ANALYSIS:")
            analyze_page_elements(driver)
            
            # Take another screenshot
            try:
                screenshot_path = f"outlook_debug_loggedin_{int(time.time())}.png"
                driver.save_screenshot(screenshot_path)
                print(f"\n📸 Post-login screenshot saved: {screenshot_path}")
            except Exception as e:
                print(f"⚠️ Could not save screenshot: {e}")
        
        # Test compose functionality
        print("\n🧪 TESTING COMPOSE FUNCTIONALITY...")
        
        compose_found = False
        for i, selector in enumerate(compose_selectors):
            try:
                print(f"Trying compose selector {i+1}: {selector}")
                element = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                if element:
                    print(f"✅ Found clickable compose button!")
                    
                    # Ask user if they want to test clicking
                    test_click = input("Test clicking compose button? (y/n): ").strip().lower()
                    if test_click in ['y', 'yes']:
                        element.click()
                        print("✅ Compose button clicked successfully!")
                        time.sleep(3)
                        
                        # Analyze compose window
                        print("\n📊 COMPOSE WINDOW ANALYSIS:")
                        analyze_page_elements(driver)
                    
                    compose_found = True
                    break
                    
            except Exception as e:
                print(f"❌ Selector {i+1} failed: {e}")
        
        if not compose_found:
            print("❌ Could not find working compose button")
            print("\n💡 SUGGESTED FIXES:")
            print("1. Make sure you're fully logged into Outlook")
            print("2. Try refreshing the page")
            print("3. Check if you're on the correct Outlook URL")
            print("4. Look at the screenshots to see the current page state")
        
        return compose_found
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
        
    finally:
        if driver:
            print("\n🧹 Cleaning up...")
            try:
                driver.quit()
                print("✅ Browser closed")
            except:
                pass

def main():
    """Main test function"""
    print("🧪 OUTLOOK LOGIN TEST SCRIPT")
    print("=" * 50)
    print("This script will help debug Outlook login issues")
    print("by analyzing page elements and testing interactions.")
    print("=" * 50)
    
    success = test_outlook_login()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ TEST COMPLETED SUCCESSFULLY!")
        print("The compose button was found and is working.")
        print("You can now run the full email automation script.")
    else:
        print("❌ TEST FAILED")
        print("Check the analysis above and screenshots for debugging.")
        print("Common issues:")
        print("- Not fully logged into Outlook")
        print("- Page still loading")
        print("- Different Outlook interface version")
        print("- Browser compatibility issues")
    
    print("=" * 50)

if __name__ == "__main__":
    main()