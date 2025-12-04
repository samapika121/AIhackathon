#!/usr/bin/env python3
"""
Facebook Automation Framework - Standalone Version
Can be run directly from the core directory
"""

import time
import random
import logging
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager

# Simple logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleFacebookAutomation:
    """Standalone Facebook automation class"""
    
    def __init__(self):
        self.driver = None
        self.is_logged_in = False
        
        # Configuration
        self.FACEBOOK_BASE_URL = "https://www.facebook.com"
        self.FACEBOOK_LOGIN_URL = "https://www.facebook.com/login"
        self.FACEBOOK_GAMES_URL = "https://www.facebook.com/games"
        
        # Game URLs
        self.GAME_URLS = {
            'farmville': 'https://www.facebook.com/games/farmville',
            'candy_crush': 'https://apps.facebook.com/candycrushsaga/',
            'words_with_friends': 'https://www.facebook.com/games/wordswithfriends'
        }
        
    def start_browser(self, headless=False):
        """Start Chrome browser"""
        try:
            logger.info("Starting Chrome browser...")
            
            options = ChromeOptions()
            
            if headless:
                options.add_argument('--headless')
            
            # Basic options for stability
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            # Create driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Set timeouts
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)
            
            logger.info("Browser started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            return False
    
    def login_to_facebook(self, email, password):
        """Login to Facebook"""
        if not email or not password:
            logger.error("Email and password are required")
            return False
        
        try:
            logger.info("Logging in to Facebook...")
            
            # Navigate to login page
            self.driver.get(self.FACEBOOK_LOGIN_URL)
            time.sleep(3)
            
            # Find and fill email field
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            email_field.clear()
            self._human_type(email_field, email)
            time.sleep(1)
            
            # Find and fill password field
            password_field = self.driver.find_element(By.ID, "pass")
            password_field.clear()
            self._human_type(password_field, password)
            time.sleep(1)
            
            # Find and click login button
            login_button = self.driver.find_element(By.NAME, "login")
            login_button.click()
            
            logger.info("Login button clicked, waiting for response...")
            time.sleep(5)
            
            # Check if login was successful
            current_url = self.driver.current_url
            if "facebook.com" in current_url and "login" not in current_url:
                self.is_logged_in = True
                logger.info("Successfully logged in to Facebook!")
                return True
            else:
                logger.error("Login failed - still on login page")
                return False
                
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    def _human_type(self, element, text):
        """Type text with human-like delays"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
    
    def navigate_to_games(self):
        """Navigate to Facebook Games"""
        if not self.is_logged_in:
            logger.error("Must be logged in first")
            return False
        
        try:
            logger.info("Navigating to Facebook Games...")
            self.driver.get(self.FACEBOOK_GAMES_URL)
            time.sleep(5)
            
            logger.info("Successfully navigated to Games page")
            return True
            
        except Exception as e:
            logger.error(f"Failed to navigate to games: {e}")
            return False
    
    def launch_game(self, game_name):
        """Launch a specific game"""
        if not self.is_logged_in:
            logger.error("Must be logged in first")
            return False
        
        game_url = self.GAME_URLS.get(game_name.lower())
        if not game_url:
            logger.error(f"Unknown game: {game_name}")
            logger.info(f"Available games: {list(self.GAME_URLS.keys())}")
            return False
        
        try:
            logger.info(f"Launching {game_name}...")
            self.driver.get(game_url)
            time.sleep(10)  # Wait for game to load
            
            logger.info(f"Game {game_name} launched successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to launch game: {e}")
            return False
    
    def perform_basic_actions(self):
        """Perform some basic actions on the current page"""
        try:
            logger.info("Performing basic actions...")
            
            # Scroll down
            self.driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(2)
            
            # Scroll up
            self.driver.execute_script("window.scrollBy(0, -300);")
            time.sleep(2)
            
            # Look for clickable elements
            clickable_elements = self.driver.find_elements(By.XPATH, "//button | //a | //div[@role='button']")
            
            if clickable_elements:
                # Click a random element (safely)
                element = random.choice(clickable_elements[:5])  # Only first 5 to be safe
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(1)
                    element.click()
                    logger.info("Clicked on an element")
                    time.sleep(3)
                except:
                    logger.info("Could not click element, continuing...")
            
            logger.info("Basic actions completed")
            return True
            
        except Exception as e:
            logger.error(f"Error performing actions: {e}")
            return False
    
    def take_screenshot(self, filename=None):
        """Take a screenshot"""
        try:
            if not filename:
                filename = f"screenshot_{int(time.time())}.png"
            
            filepath = os.path.join("..", "screenshots", filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            self.driver.save_screenshot(filepath)
            logger.info(f"Screenshot saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return None
    
    def close_browser(self):
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")

def main():
    """Main function for standalone execution"""
    print("🤖 Facebook Automation - Standalone Version")
    print("=" * 50)
    
    # Get user input
    email = input("Enter Facebook email: ").strip()
    password = input("Enter Facebook password: ").strip()
    
    if not email or not password:
        print("❌ Email and password are required")
        return
    
    headless = input("Run in headless mode? (y/n): ").strip().lower() == 'y'
    
    # Create automation instance
    automation = SimpleFacebookAutomation()
    
    try:
        # Start browser
        if not automation.start_browser(headless):
            print("❌ Failed to start browser")
            return
        
        print("✅ Browser started")
        
        # Login
        if not automation.login_to_facebook(email, password):
            print("❌ Login failed")
            automation.take_screenshot("login_failed.png")
            return
        
        print("✅ Login successful")
        automation.take_screenshot("login_success.png")
        
        # Navigate to games
        if automation.navigate_to_games():
            print("✅ Navigated to games")
            automation.take_screenshot("games_page.png")
            
            # Ask user which game to launch
            print("\nAvailable games:")
            for i, game in enumerate(automation.GAME_URLS.keys(), 1):
                print(f"{i}. {game}")
            
            try:
                choice = input("\nEnter game number (or press Enter to skip): ").strip()
                if choice:
                    game_index = int(choice) - 1
                    game_names = list(automation.GAME_URLS.keys())
                    if 0 <= game_index < len(game_names):
                        game_name = game_names[game_index]
                        
                        if automation.launch_game(game_name):
                            print(f"✅ Launched {game_name}")
                            automation.take_screenshot(f"{game_name}_launched.png")
                            
                            # Perform some actions
                            automation.perform_basic_actions()
                            automation.take_screenshot(f"{game_name}_actions.png")
                        else:
                            print(f"❌ Failed to launch {game_name}")
                    else:
                        print("❌ Invalid game selection")
            except ValueError:
                print("❌ Invalid input")
        
        # Wait for user input before closing
        input("\nPress Enter to close browser...")
        
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        automation.close_browser()
        print("🏁 Automation completed")

if __name__ == "__main__":
    main()
