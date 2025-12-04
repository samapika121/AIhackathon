"""
Facebook Automation Framework - Configuration Settings
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FacebookConfig:
    """Facebook automation configuration"""
    
    # Facebook URLs
    FACEBOOK_BASE_URL = "https://www.facebook.com"
    FACEBOOK_LOGIN_URL = "https://www.facebook.com/login"
    FACEBOOK_GAMES_URL = "https://www.facebook.com/games"
    
    # Browser Settings
    BROWSER_TYPE = os.getenv('BROWSER_TYPE', 'chrome')  # chrome, firefox, edge
    HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'False').lower() == 'true'
    WINDOW_SIZE = os.getenv('WINDOW_SIZE', '1920,1080')
    
    # Automation Settings
    IMPLICIT_WAIT = int(os.getenv('IMPLICIT_WAIT', '10'))
    PAGE_LOAD_TIMEOUT = int(os.getenv('PAGE_LOAD_TIMEOUT', '30'))
    SCRIPT_TIMEOUT = int(os.getenv('SCRIPT_TIMEOUT', '30'))
    
    # User Credentials (use environment variables for security)
    FACEBOOK_EMAIL = os.getenv('FACEBOOK_EMAIL', '')
    FACEBOOK_PASSWORD = os.getenv('FACEBOOK_PASSWORD', '')
    
    # Proxy Settings
    USE_PROXY = os.getenv('USE_PROXY', 'False').lower() == 'true'
    PROXY_HOST = os.getenv('PROXY_HOST', '')
    PROXY_PORT = os.getenv('PROXY_PORT', '')
    
    # Anti-Detection Settings
    USE_UNDETECTED_CHROME = os.getenv('USE_UNDETECTED_CHROME', 'True').lower() == 'true'
    RANDOM_USER_AGENT = os.getenv('RANDOM_USER_AGENT', 'True').lower() == 'true'
    
    # Logging Settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/facebook_automation.log')
    
    # Screenshot Settings
    TAKE_SCREENSHOTS = os.getenv('TAKE_SCREENSHOTS', 'True').lower() == 'true'
    SCREENSHOT_DIR = os.getenv('SCREENSHOT_DIR', 'screenshots')
    
    # Performance Settings
    LOAD_IMAGES = os.getenv('LOAD_IMAGES', 'False').lower() == 'true'
    LOAD_CSS = os.getenv('LOAD_CSS', 'True').lower() == 'true'
    LOAD_JAVASCRIPT = os.getenv('LOAD_JAVASCRIPT', 'True').lower() == 'true'

class GameConfig:
    """Game-specific configuration"""
    
    # Game URLs and IDs
    GAME_URLS = {
        'farmville': 'https://www.facebook.com/games/farmville',
        'candy_crush': 'https://apps.facebook.com/candycrushsaga/',
        'words_with_friends': 'https://www.facebook.com/games/wordswithfriends'
    }
    
    # Game Actions
    DEFAULT_GAME_ACTIONS = [
        'click_play_button',
        'wait_for_game_load',
        'perform_game_action',
        'collect_rewards',
        'check_notifications'
    ]
    
    # Timing Settings
    GAME_LOAD_TIMEOUT = int(os.getenv('GAME_LOAD_TIMEOUT', '60'))
    ACTION_DELAY_MIN = float(os.getenv('ACTION_DELAY_MIN', '1.0'))
    ACTION_DELAY_MAX = float(os.getenv('ACTION_DELAY_MAX', '3.0'))

class APIConfig:
    """API and web service configuration"""
    
    # Flask API Settings
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', '5005'))
    API_DEBUG = os.getenv('API_DEBUG', 'True').lower() == 'true'
    
    # Database Settings (if needed)
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///facebook_automation.db')
    
    # External APIs
    WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
    NOTIFICATION_API = os.getenv('NOTIFICATION_API', '')

# Create directories if they don't exist
import os
os.makedirs(os.path.dirname(FacebookConfig.LOG_FILE), exist_ok=True)
os.makedirs(FacebookConfig.SCREENSHOT_DIR, exist_ok=True)
