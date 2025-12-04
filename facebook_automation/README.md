# 🤖 Facebook Automation Framework

A comprehensive Python framework for automating Facebook interactions, including login, navigation, and game automation with anti-detection features.

## 🚀 Features

### 🔐 **Authentication & Security**
- **Secure Facebook Login** with credential management
- **Anti-Detection Technology** using undetected-chromedriver
- **Random User Agents** and human-like behavior simulation
- **Proxy Support** for IP rotation
- **Screenshot Capture** for monitoring and debugging

### 🎮 **Game Automation**
- **Multi-Game Support**: FarmVille, Candy Crush, Words with Friends
- **Intelligent Game Detection** and loading
- **Automated Actions**: Click, collect, navigate
- **Reward Collection** and notification handling
- **Customizable Action Sequences**

### 🌐 **Web Interface**
- **Beautiful Dashboard** for easy control
- **Real-time Session Management**
- **Live Logs and Monitoring**
- **Multiple Browser Support** (Chrome, Firefox, Edge)
- **Headless and Visible Modes**

### 🛠️ **Framework Features**
- **Modular Architecture** for easy extension
- **Comprehensive Logging** with file and console output
- **Configuration Management** via environment variables
- **Error Handling** and recovery mechanisms
- **Performance Monitoring** and optimization

## 📦 Installation

### **1. Clone the Repository**
```bash
git clone <repository-url>
cd facebook_automation
```

### **2. Create Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Setup Configuration**
```bash
cp .env.example .env
# Edit .env with your Facebook credentials and preferences
```

## 🎯 Quick Start

### **Method 1: Web Interface (Recommended)**
```bash
python main.py --mode api
```
Then open: **http://localhost:5005**

### **Method 2: Command Line**
```bash
# Basic login and navigation
python main.py --mode cli --email your@email.com --password yourpassword

# Launch specific game
python main.py --mode cli --email your@email.com --password yourpassword --game farmville

# Headless mode
python main.py --mode cli --headless --email your@email.com --password yourpassword
```

## 🎮 Supported Games

### **🚜 FarmVille**
- Automated farming actions
- Resource collection
- Crop management
- Friend interactions

### **🍭 Candy Crush**
- Level progression
- Move optimization
- Reward collection
- Booster management

### **📝 Words with Friends**
- Game interaction
- Notification handling
- Turn management
- Score tracking

## ⚙️ Configuration

### **Environment Variables (.env)**
```bash
# Facebook Credentials
FACEBOOK_EMAIL=your_email@example.com
FACEBOOK_PASSWORD=your_password

# Browser Settings
BROWSER_TYPE=chrome
HEADLESS_MODE=False
WINDOW_SIZE=1920,1080

# Anti-Detection
USE_UNDETECTED_CHROME=True
RANDOM_USER_AGENT=True

# Performance
LOAD_IMAGES=False
LOAD_CSS=True
LOAD_JAVASCRIPT=True
```

### **Advanced Settings**
```bash
# Proxy Configuration
USE_PROXY=True
PROXY_HOST=your.proxy.com
PROXY_PORT=8080

# Timing Settings
ACTION_DELAY_MIN=1.0
ACTION_DELAY_MAX=3.0
GAME_LOAD_TIMEOUT=60

# Logging
LOG_LEVEL=INFO
TAKE_SCREENSHOTS=True
```

## 🖥️ Web Dashboard

### **🎮 Control Panel**
- Create and manage automation sessions
- Quick actions for login and navigation
- Real-time session monitoring
- Game selection and action configuration

### **📊 Session Management**
- View all active sessions
- Monitor session status and progress
- Stop individual or all sessions
- Session performance metrics

### **📝 Logging System**
- Real-time log viewing
- Session-specific logs
- Error tracking and debugging
- Performance monitoring

### **⚙️ Settings Panel**
- Browser configuration
- Credential management
- Performance tuning
- Anti-detection settings

## 🔧 API Endpoints

### **Session Management**
```bash
POST /api/create_session    # Create new automation session
POST /api/stop_session      # Stop specific session
POST /api/stop_all_sessions # Stop all sessions
GET  /api/sessions          # Get all sessions
```

### **Facebook Actions**
```bash
POST /api/login            # Login to Facebook
POST /api/navigate_games   # Navigate to Games
POST /api/launch_game      # Launch specific game
POST /api/perform_actions  # Perform game actions
```

### **Monitoring**
```bash
GET /api/logs/{session_id} # Get session logs
GET /api/status           # Get system status
```

## 🛡️ Security & Best Practices

### **🔐 Credential Security**
- Store credentials in environment variables
- Never commit credentials to version control
- Use strong, unique passwords
- Enable two-factor authentication on Facebook

### **🤖 Anti-Detection**
- Random delays between actions
- Human-like typing patterns
- Realistic mouse movements
- User agent rotation
- Proxy support for IP rotation

### **⚠️ Usage Guidelines**
- Respect Facebook's Terms of Service
- Use reasonable delays between actions
- Monitor for unusual account activity
- Keep automation sessions short
- Test in headless=False mode first

## 📊 Monitoring & Debugging

### **📸 Screenshot Capture**
- Automatic screenshots at key points
- Error state capture
- Progress monitoring
- Debugging assistance

### **📝 Comprehensive Logging**
- Action-level logging
- Error tracking
- Performance metrics
- Session history

### **🔍 Debug Mode**
- Detailed error messages
- Step-by-step execution
- Browser developer tools access
- Network request monitoring

## 🚀 Advanced Usage

### **Custom Game Actions**
```python
from core.facebook_automation import FacebookAutomation

# Create custom automation
automation = FacebookAutomation()
automation.start_session('chrome', headless=False)
automation.login_to_facebook()

# Custom game actions
custom_actions = [
    'click_play_button',
    'wait_for_game_load',
    'custom_action_1',
    'custom_action_2'
]

automation.perform_game_actions('farmville', custom_actions)
```

### **Extending Game Support**
```python
# Add new game in config/settings.py
GAME_URLS = {
    'your_game': 'https://www.facebook.com/games/yourgame'
}

# Implement game-specific actions
def _perform_your_game_action(self):
    # Custom game logic here
    pass
```

### **Custom Browser Configuration**
```python
from core.browser_manager import BrowserManager

browser_manager = BrowserManager()
driver = browser_manager.create_browser(
    browser_type='chrome',
    headless=True
)
```

## 🔧 Troubleshooting

### **Common Issues**

#### **Browser Not Starting**
```bash
# Install browser drivers
pip install webdriver-manager

# Check browser installation
which google-chrome
which firefox
```

#### **Login Issues**
- Verify credentials in .env file
- Check for CAPTCHA requirements
- Enable two-factor authentication
- Use fresh browser session

#### **Game Loading Problems**
- Increase GAME_LOAD_TIMEOUT
- Check internet connection
- Verify game URL accessibility
- Try different browser

#### **Detection Issues**
- Enable USE_UNDETECTED_CHROME
- Increase action delays
- Use proxy rotation
- Reduce session frequency

### **Debug Commands**
```bash
# Verbose logging
LOG_LEVEL=DEBUG python main.py

# Screenshot mode
TAKE_SCREENSHOTS=True python main.py

# Visible browser
HEADLESS_MODE=False python main.py
```

## 📈 Performance Optimization

### **Speed Optimization**
```bash
# Disable images for faster loading
LOAD_IMAGES=False

# Use headless mode
HEADLESS_MODE=True

# Optimize timeouts
PAGE_LOAD_TIMEOUT=15
SCRIPT_TIMEOUT=15
```

### **Resource Management**
- Close unused sessions
- Monitor memory usage
- Limit concurrent sessions
- Use appropriate delays

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request
5. Follow coding standards

## 📄 License

This project is for educational purposes only. Use responsibly and in accordance with Facebook's Terms of Service.

## ⚠️ Disclaimer

This framework is provided as-is for educational and research purposes. Users are responsible for complying with Facebook's Terms of Service and applicable laws. The authors are not responsible for any misuse or consequences of using this software.

## 🆘 Support

- 📧 **Email**: support@example.com
- 💬 **Discord**: [Join our community]
- 📖 **Documentation**: [Full docs]
- 🐛 **Issues**: [Report bugs]

---

**🚀 Start automating your Facebook interactions today with this powerful, secure, and user-friendly framework!**
