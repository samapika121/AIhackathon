"""
Facebook Automation Framework - Main Automation Class
Handles Facebook login, navigation, and game automation
"""

import time
import random
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from core.browser_manager import BrowserManager
from config.settings import FacebookConfig, GameConfig
from utils.logger import setup_logger

class FacebookAutomation:
    """Main Facebook automation class"""
    
    def __init__(self, config=None):
        self.config = config or FacebookConfig()
        self.game_config = GameConfig()
        self.browser_manager = BrowserManager(self.config)
        self.driver = None
        self.logger = setup_logger(__name__)
        self.is_logged_in = False
        
    def start_session(self, browser_type=None, headless=None):
        """Start automation session"""
        try:
            self.logger.info("Starting Facebook automation session...")
            self.driver = self.browser_manager.create_browser(browser_type, headless)
            self.logger.info("Browser session started successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start session: {e}")
            return False
    
    def login_to_facebook(self, email=None, password=None):
        """Login to Facebook"""
        email = email or self.config.FACEBOOK_EMAIL
        password = password or self.config.FACEBOOK_PASSWORD
        
        if not email or not password:
            self.logger.error("Facebook credentials not provided")
            return False
        
        try:
            self.logger.info("Attempting to login to Facebook...")
            
            # Navigate to Facebook login page
            self.driver.get(self.config.FACEBOOK_LOGIN_URL)
            self.browser_manager.random_delay(2, 4)
            
            # Take screenshot
            self.browser_manager.take_screenshot("login_page.png")
            
            # Find and fill email field
            email_field = self.browser_manager.wait_for_element(By.ID, "email")
            if not email_field:
                email_field = self.browser_manager.wait_for_element(By.NAME, "email")
            
            if email_field:
                email_field.clear()
                self._human_type(email_field, email)
                self.browser_manager.random_delay(1, 2)
            else:
                self.logger.error("Email field not found")
                return False
            
            # Find and fill password field
            password_field = self.browser_manager.wait_for_element(By.ID, "pass")
            if not password_field:
                password_field = self.browser_manager.wait_for_element(By.NAME, "pass")
            
            if password_field:
                password_field.clear()
                self._human_type(password_field, password)
                self.browser_manager.random_delay(1, 2)
            else:
                self.logger.error("Password field not found")
                return False
            
            # Find and click login button
            login_button = self.browser_manager.wait_for_clickable(By.NAME, "login")
            if not login_button:
                login_button = self.browser_manager.wait_for_clickable(By.XPATH, "//button[@type='submit']")
            
            if login_button:
                self.browser_manager.safe_click(login_button)
                self.logger.info("Login button clicked")
            else:
                self.logger.error("Login button not found")
                return False
            
            # Wait for login to complete
            self.browser_manager.random_delay(3, 6)
            
            # Check if login was successful
            if self._check_login_success():
                self.is_logged_in = True
                self.logger.info("Successfully logged in to Facebook")
                self.browser_manager.take_screenshot("login_success.png")
                return True
            else:
                self.logger.error("Login failed - checking for errors")
                self.browser_manager.take_screenshot("login_failed.png")
                self._handle_login_errors()
                return False
                
        except Exception as e:
            self.logger.error(f"Login process failed: {e}")
            self.browser_manager.take_screenshot("login_error.png")
            return False
    
    def _human_type(self, element, text, delay_range=(0.05, 0.15)):
        """Type text with human-like delays"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(*delay_range))
    
    def _check_login_success(self):
        """Check if login was successful"""
        try:
            # Check for common indicators of successful login
            success_indicators = [
                (By.XPATH, "//div[@role='banner']"),  # Facebook header
                (By.XPATH, "//div[@data-pagelet='LeftRail']"),  # Left sidebar
                (By.XPATH, "//a[@aria-label='Facebook']"),  # Facebook logo
                (By.XPATH, "//div[contains(@class, 'feed')]"),  # News feed
            ]
            
            for by, value in success_indicators:
                try:
                    element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((by, value))
                    )
                    if element:
                        return True
                except TimeoutException:
                    continue
            
            # Check current URL
            current_url = self.driver.current_url
            if "facebook.com" in current_url and "login" not in current_url:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking login success: {e}")
            return False
    
    def _handle_login_errors(self):
        """Handle login errors and provide feedback"""
        try:
            # Check for common error messages
            error_selectors = [
                "//div[contains(@class, 'error')]",
                "//div[contains(text(), 'incorrect')]",
                "//div[contains(text(), 'wrong')]",
                "//div[contains(text(), 'invalid')]",
                "//div[@role='alert']"
            ]
            
            for selector in error_selectors:
                try:
                    error_element = self.driver.find_element(By.XPATH, selector)
                    if error_element and error_element.is_displayed():
                        error_text = error_element.text
                        self.logger.error(f"Login error detected: {error_text}")
                        return
                except NoSuchElementException:
                    continue
            
            # Check for CAPTCHA
            captcha_selectors = [
                "//div[contains(@class, 'captcha')]",
                "//iframe[contains(@src, 'captcha')]"
            ]
            
            for selector in captcha_selectors:
                try:
                    captcha_element = self.driver.find_element(By.XPATH, selector)
                    if captcha_element:
                        self.logger.warning("CAPTCHA detected - manual intervention required")
                        return
                except NoSuchElementException:
                    continue
            
            self.logger.error("Unknown login error occurred")
            
        except Exception as e:
            self.logger.error(f"Error handling login errors: {e}")
    
    # def navigate_to_games(self):
    #     """Navigate to Facebook Games"""
    #     if not self.is_logged_in:
    #         self.logger.error("Must be logged in to navigate to games")
    #         return False
        
    #     try:
    #         self.logger.info("Navigating to Facebook Games...")
    #         self.driver.get(self.config.FACEBOOK_GAMES_URL)
    #         self.browser_manager.random_delay(3, 5)
            
    #         # Wait for games page to load
    #         games_indicator = self.browser_manager.wait_for_element(
    #             By.XPATH, "//div[contains(@class, 'game') or contains(text(), 'Games')]"
    #         )
            
    #         if games_indicator:
    #             self.logger.info("Successfully navigated to Games page")
    #             self.browser_manager.take_screenshot("games_page.png")
    #             return True
    #         else:
    #             self.logger.error("Failed to load Games page")
    #             return False
                
    #     except Exception as e:
    #         self.logger.error(f"Failed to navigate to games: {e}")
    #         return False
    
    # def launch_game(self, game_name):
    #     """Launch a specific game"""
    #     if not self.is_logged_in:
    #         self.logger.error("Must be logged in to launch games")
    #         return False
        
    #     try:
    #         game_url = self.game_config.GAME_URLS.get(game_name.lower())
    #         if not game_url:
    #             self.logger.error(f"Unknown game: {game_name}")
    #             return False
            
    #         self.logger.info(f"Launching game: {game_name}")
    #         self.driver.get(game_url)
            
    #         # Wait for game to load
    #         self.browser_manager.random_delay(5, 10)
            
    #         # Look for game-specific indicators
    #         game_loaded = self._wait_for_game_load(game_name)
            
    #         if game_loaded:
    #             self.logger.info(f"Game {game_name} loaded successfully")
    #             self.browser_manager.take_screenshot(f"{game_name}_loaded.png")
    #             return True
    #         else:
    #             self.logger.error(f"Failed to load game: {game_name}")
    #             return False
                
    #     except Exception as e:
    #         self.logger.error(f"Failed to launch game {game_name}: {e}")
    #         return False
    
    # def _wait_for_game_load(self, game_name, timeout=None):
    #     """Wait for specific game to load"""
    #     timeout = timeout or self.game_config.GAME_LOAD_TIMEOUT
        
    #     try:
    #         # Common game loading indicators
    #         game_indicators = [
    #             "//canvas",  # Game canvas
    #             "//iframe[contains(@src, 'game')]",  # Game iframe
    #             "//div[contains(@class, 'game-container')]",  # Game container
    #             "//button[contains(text(), 'Play')]",  # Play button
    #             "//div[contains(@class, 'loading')]",  # Loading indicator
    #         ]
            
    #         wait = WebDriverWait(self.driver, timeout)
            
    #         for indicator in game_indicators:
    #             try:
    #                 element = wait.until(EC.presence_of_element_located((By.XPATH, indicator)))
    #                 if element:
    #                     self.logger.info(f"Game loading indicator found: {indicator}")
    #                     return True
    #             except TimeoutException:
    #                 continue
            
    #         return False
            
    #     except Exception as e:
    #         self.logger.error(f"Error waiting for game load: {e}")
    #         return False
    
    # def perform_game_actions(self, game_name, actions=None):
    #     """Perform automated actions in the game"""
    #     actions = actions or self.game_config.DEFAULT_GAME_ACTIONS
        
    #     try:
    #         self.logger.info(f"Performing actions for game: {game_name}")
            
    #         for action in actions:
    #             self.logger.info(f"Executing action: {action}")
                
    #             if action == 'click_play_button':
    #                 self._click_play_button()
    #             elif action == 'wait_for_game_load':
    #                 self._wait_for_game_load(game_name)
    #             elif action == 'perform_game_action':
    #                 self._perform_generic_game_action()
    #             elif action == 'collect_rewards':
    #                 self._collect_rewards()
    #             elif action == 'check_notifications':
    #                 self._check_notifications()
                
    #             # Random delay between actions
    #             delay = random.uniform(
    #                 self.game_config.ACTION_DELAY_MIN,
    #                 self.game_config.ACTION_DELAY_MAX
    #             )
    #             time.sleep(delay)
            
    #         self.logger.info("Game actions completed")
    #         return True
            
    #     except Exception as e:
    #         self.logger.error(f"Error performing game actions: {e}")
    #         return False
    
    # def _click_play_button(self):
    #     """Click play button if available"""
    #     play_selectors = [
    #         "//button[contains(text(), 'Play')]",
    #         "//button[contains(text(), 'Start')]",
    #         "//a[contains(text(), 'Play')]",
    #         "//div[contains(@class, 'play-button')]"
    #     ]
        
    #     for selector in play_selectors:
    #         try:
    #             play_button = self.browser_manager.wait_for_clickable(By.XPATH, selector, timeout=5)
    #             if play_button:
    #                 self.browser_manager.safe_click(play_button)
    #                 self.logger.info("Play button clicked")
    #                 return True
    #         except TimeoutException:
    #             continue
        
    #     self.logger.info("No play button found")
    #     return False
    
    # def _perform_generic_game_action(self):
    #     """Perform generic game action (clicking, scrolling)"""
    #     try:
    #         # Random scroll
    #         if random.choice([True, False]):
    #             self.browser_manager.scroll_page(random.choice(['up', 'down']))
            
    #         # Random click on game area
    #         clickable_elements = self.driver.find_elements(By.XPATH, "//canvas | //div[@role='button'] | //button")
    #         if clickable_elements:
    #             element = random.choice(clickable_elements)
    #             try:
    #                 self.browser_manager.safe_click(element)
    #                 self.logger.info("Performed random game action")
    #             except:
    #                 pass
            
    #     except Exception as e:
    #         self.logger.debug(f"Generic game action error: {e}")
    
    # def _collect_rewards(self):
    #     """Collect rewards if available"""
    #     reward_selectors = [
    #         "//button[contains(text(), 'Collect')]",
    #         "//button[contains(text(), 'Claim')]",
    #         "//div[contains(@class, 'reward')]//button",
    #         "//div[contains(@class, 'gift')]//button"
    #     ]
        
    #     for selector in reward_selectors:
    #         try:
    #             reward_button = self.browser_manager.wait_for_clickable(By.XPATH, selector, timeout=3)
    #             if reward_button:
    #                 self.browser_manager.safe_click(reward_button)
    #                 self.logger.info("Reward collected")
    #                 return True
    #         except TimeoutException:
    #             continue
        
    #     return False
    
    # def _check_notifications(self):
    #     """Check and handle notifications"""
    #     try:
    #         notification_selectors = [
    #             "//div[contains(@class, 'notification')]",
    #             "//div[@role='alert']",
    #             "//div[contains(@class, 'popup')]"
    #         ]
            
    #         for selector in notification_selectors:
    #             try:
    #                 notification = self.driver.find_element(By.XPATH, selector)
    #                 if notification and notification.is_displayed():
    #                     self.logger.info("Notification detected")
                        
    #                     # Try to close notification
    #                     close_button = notification.find_element(By.XPATH, ".//button[contains(@aria-label, 'Close')] | .//button[contains(text(), 'X')]")
    #                     if close_button:
    #                         self.browser_manager.safe_click(close_button)
    #                         self.logger.info("Notification closed")
                        
    #                     return True
    #             except NoSuchElementException:
    #                 continue
            
    #         return False
            
    #     except Exception as e:
    #         self.logger.debug(f"Notification check error: {e}")
    #         return False
    
    # def logout_from_facebook(self):
    #     """Logout from Facebook"""
    #     if not self.is_logged_in:
    #         return True
        
    #     try:
    #         self.logger.info("Logging out from Facebook...")
            
    #         # Click on account menu
    #         account_menu = self.browser_manager.wait_for_clickable(
    #             By.XPATH, "//div[@role='button'][@aria-label='Account'] | //div[contains(@class, 'account-menu')]"
    #         )
            
    #         if account_menu:
    #             self.browser_manager.safe_click(account_menu)
    #             self.browser_manager.random_delay(1, 2)
                
    #             # Click logout
    #             logout_button = self.browser_manager.wait_for_clickable(
    #                 By.XPATH, "//a[contains(text(), 'Log Out')] | //button[contains(text(), 'Log Out')]"
    #             )
                
    #             if logout_button:
    #                 self.browser_manager.safe_click(logout_button)
    #                 self.browser_manager.random_delay(2, 4)
                    
    #                 self.is_logged_in = False
    #                 self.logger.info("Successfully logged out")
    #                 return True
            
    #         self.logger.error("Failed to find logout option")
    #         return False
            
    #     except Exception as e:
    #         self.logger.error(f"Logout failed: {e}")
    #         return False
    
    # def end_session(self):
    #     """End automation session"""
    #     try:
    #         if self.is_logged_in:
    #             self.logout_from_facebook()
            
    #         self.browser_manager.close_browser()
    #         self.logger.info("Automation session ended")
            
    #     except Exception as e:
    #         self.logger.error(f"Error ending session: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.end_session()
