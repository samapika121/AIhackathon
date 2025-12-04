"""
Facebook Automation Framework - Browser Manager
Handles browser initialization and management
"""

import os
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from fake_useragent import UserAgent
try:
    import undetected_chromedriver as uc
    UC_AVAILABLE = True
except ImportError:
    UC_AVAILABLE = False
    uc = None
from config.settings import FacebookConfig
import logging

class BrowserManager:
    """Manages browser instances and configurations"""
    
    def __init__(self, config=None):
        self.config = config or FacebookConfig()
        self.driver = None
        self.logger = logging.getLogger(__name__)
        
    def create_browser(self, browser_type=None, headless=None):
        """Create and configure browser instance"""
        browser_type = browser_type or self.config.BROWSER_TYPE
        headless = headless if headless is not None else self.config.HEADLESS_MODE
        
        try:
            if browser_type.lower() == 'chrome':
                self.driver = self._create_chrome_browser(headless)
            elif browser_type.lower() == 'firefox':
                self.driver = self._create_firefox_browser(headless)
            elif browser_type.lower() == 'edge':
                self.driver = self._create_edge_browser(headless)
            else:
                raise ValueError(f"Unsupported browser type: {browser_type}")
            
            # Configure browser settings
            self._configure_browser()
            
            self.logger.info(f"Browser created successfully: {browser_type}")
            return self.driver
            
        except Exception as e:
            self.logger.error(f"Failed to create browser: {e}")
            raise
    
    def _create_chrome_browser(self, headless=False):
        """Create Chrome browser instance"""
        if self.config.USE_UNDETECTED_CHROME and UC_AVAILABLE:
            return self._create_undetected_chrome(headless)
        else:
            return self._create_regular_chrome(headless)
    
    def _create_undetected_chrome(self, headless=False):
        """Create undetected Chrome browser"""
        if not UC_AVAILABLE:
            return self._create_regular_chrome(headless)
        
        options = uc.ChromeOptions()
        
        # Basic options
        if headless:
            options.add_argument('--headless')
        
        # Anti-detection options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Performance options
        if not self.config.LOAD_IMAGES:
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)
        
        # User agent
        if self.config.RANDOM_USER_AGENT:
            ua = UserAgent()
            options.add_argument(f'--user-agent={ua.random}')
        
        # Proxy settings
        if self.config.USE_PROXY and self.config.PROXY_HOST:
            options.add_argument(f'--proxy-server={self.config.PROXY_HOST}:{self.config.PROXY_PORT}')
        
        # Window size
        width, height = self.config.WINDOW_SIZE.split(',')
        options.add_argument(f'--window-size={width},{height}')
        
        driver = uc.Chrome(options=options)
        
        # Execute script to hide automation
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def _create_regular_chrome(self, headless=False):
        """Create regular Chrome browser"""
        options = ChromeOptions()
        
        if headless:
            options.add_argument('--headless')
        
        # Basic options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        # Performance options
        if not self.config.LOAD_IMAGES:
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)
        
        # User agent
        if self.config.RANDOM_USER_AGENT:
            ua = UserAgent()
            options.add_argument(f'--user-agent={ua.random}')
        
        # Window size
        width, height = self.config.WINDOW_SIZE.split(',')
        options.add_argument(f'--window-size={width},{height}')
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    
    def _create_firefox_browser(self, headless=False):
        """Create Firefox browser instance"""
        options = FirefoxOptions()
        
        if headless:
            options.add_argument('--headless')
        
        # Performance options
        if not self.config.LOAD_IMAGES:
            options.set_preference('permissions.default.image', 2)
        
        # User agent
        if self.config.RANDOM_USER_AGENT:
            ua = UserAgent()
            options.set_preference("general.useragent.override", ua.random)
        
        service = Service(GeckoDriverManager().install())
        return webdriver.Firefox(service=service, options=options)
    
    def _create_edge_browser(self, headless=False):
        """Create Edge browser instance"""
        options = EdgeOptions()
        
        if headless:
            options.add_argument('--headless')
        
        # Basic options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        service = Service(EdgeChromiumDriverManager().install())
        return webdriver.Edge(service=service, options=options)
    
    def _configure_browser(self):
        """Configure browser timeouts and settings"""
        if self.driver:
            self.driver.implicitly_wait(self.config.IMPLICIT_WAIT)
            self.driver.set_page_load_timeout(self.config.PAGE_LOAD_TIMEOUT)
            self.driver.set_script_timeout(self.config.SCRIPT_TIMEOUT)
            
            # Maximize window if not headless
            if not self.config.HEADLESS_MODE:
                self.driver.maximize_window()
    
    def take_screenshot(self, filename=None):
        """Take screenshot of current page"""
        if not self.config.TAKE_SCREENSHOTS or not self.driver:
            return None
        
        try:
            if not filename:
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}.png"
            
            filepath = os.path.join(self.config.SCREENSHOT_DIR, filename)
            self.driver.save_screenshot(filepath)
            self.logger.info(f"Screenshot saved: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            return None
    
    def wait_for_element(self, by, value, timeout=None):
        """Wait for element to be present"""
        timeout = timeout or self.config.IMPLICIT_WAIT
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, value)))
            return element
        except Exception as e:
            self.logger.error(f"Element not found: {by}={value}, Error: {e}")
            return None
    
    def wait_for_clickable(self, by, value, timeout=None):
        """Wait for element to be clickable"""
        timeout = timeout or self.config.IMPLICIT_WAIT
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.element_to_be_clickable((by, value)))
            return element
        except Exception as e:
            self.logger.error(f"Element not clickable: {by}={value}, Error: {e}")
            return None
    
    def safe_click(self, element):
        """Safely click an element with retry logic"""
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                # Scroll to element
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(0.5)
                
                # Click element
                element.click()
                return True
                
            except Exception as e:
                self.logger.warning(f"Click attempt {attempt + 1} failed: {e}")
                if attempt < max_attempts - 1:
                    time.sleep(1)
                else:
                    self.logger.error(f"Failed to click element after {max_attempts} attempts")
                    return False
    
    def random_delay(self, min_delay=None, max_delay=None):
        """Add random delay to mimic human behavior"""
        min_delay = min_delay or 1.0
        max_delay = max_delay or 3.0
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
        return delay
    
    def scroll_page(self, direction='down', pixels=None):
        """Scroll page in specified direction"""
        if not pixels:
            pixels = random.randint(300, 800)
        
        if direction.lower() == 'down':
            self.driver.execute_script(f"window.scrollBy(0, {pixels});")
        elif direction.lower() == 'up':
            self.driver.execute_script(f"window.scrollBy(0, -{pixels});")
        
        time.sleep(random.uniform(0.5, 1.5))
    
    def close_browser(self):
        """Close browser and clean up"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Browser closed successfully")
            except Exception as e:
                self.logger.error(f"Error closing browser: {e}")
            finally:
                self.driver = None
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_browser()
