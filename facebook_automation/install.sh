#!/bin/bash

# Facebook Automation Framework - Installation Script
# This script sets up the complete environment for Facebook automation

set -e  # Exit on any error

echo "🤖 Facebook Automation Framework - Installation"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3 is installed
print_status "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_success "Python ${PYTHON_VERSION} found"

# Check Python version (minimum 3.8)
if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
    print_success "Python version is compatible"
else
    print_error "Python 3.8 or higher is required. Current version: ${PYTHON_VERSION}"
    exit 1
fi

# Check if pip is installed
print_status "Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed. Please install pip3."
    exit 1
fi
print_success "pip3 found"

# Create virtual environment
print_status "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install requirements
print_status "Installing Python packages..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Python packages installed"
else
    print_error "requirements.txt not found"
    exit 1
fi

# Create necessary directories
print_status "Creating directories..."
mkdir -p logs
mkdir -p screenshots
mkdir -p config
print_success "Directories created"

# Copy environment file
print_status "Setting up configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success "Environment file created from template"
        print_warning "Please edit .env file with your Facebook credentials"
    else
        print_error ".env.example not found"
    fi
else
    print_warning ".env file already exists"
fi

# Check browser installations
print_status "Checking browser installations..."

# Check Chrome
if command -v google-chrome &> /dev/null || command -v chromium-browser &> /dev/null || command -v chromium &> /dev/null; then
    print_success "Chrome/Chromium found"
    CHROME_AVAILABLE=true
else
    print_warning "Chrome/Chromium not found"
    CHROME_AVAILABLE=false
fi

# Check Firefox
if command -v firefox &> /dev/null; then
    print_success "Firefox found"
    FIREFOX_AVAILABLE=true
else
    print_warning "Firefox not found"
    FIREFOX_AVAILABLE=false
fi

# Install browser drivers
print_status "Installing browser drivers..."
python3 -c "
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
try:
    ChromeDriverManager().install()
    print('Chrome driver installed')
except:
    print('Chrome driver installation failed')
try:
    GeckoDriverManager().install()
    print('Firefox driver installed')
except:
    print('Firefox driver installation failed')
"

# Test basic imports
print_status "Testing package imports..."
python3 -c "
import selenium
import flask
import requests
import fake_useragent
print('All packages imported successfully')
" && print_success "Package imports successful" || print_error "Package import failed"

# Create startup script
print_status "Creating startup script..."
cat > start.sh << 'EOF'
#!/bin/bash
# Facebook Automation Framework - Startup Script

echo "🤖 Starting Facebook Automation Framework..."

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Start the application
python3 main.py --mode api

EOF

chmod +x start.sh
print_success "Startup script created"

# Create CLI helper script
print_status "Creating CLI helper script..."
cat > run_cli.sh << 'EOF'
#!/bin/bash
# Facebook Automation Framework - CLI Runner

# Activate virtual environment
source venv/bin/activate

# Run CLI mode with parameters
python3 main.py --mode cli "$@"

EOF

chmod +x run_cli.sh
print_success "CLI helper script created"

# Installation summary
echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo ""
print_success "Facebook Automation Framework has been installed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Edit the .env file with your Facebook credentials:"
echo "   nano .env"
echo ""
echo "2. Start the web interface:"
echo "   ./start.sh"
echo "   Then open: http://localhost:5005"
echo ""
echo "3. Or use CLI mode:"
echo "   ./run_cli.sh --email your@email.com --password yourpassword"
echo ""
echo "📖 Documentation:"
echo "   - README.md for detailed usage instructions"
echo "   - Web dashboard has built-in help and examples"
echo ""
echo "🔧 Configuration:"
echo "   - Browser settings in .env file"
echo "   - Logging configuration in config/settings.py"
echo "   - Game URLs and actions in config/settings.py"
echo ""

# Browser recommendations
echo "🌐 Browser Recommendations:"
if [ "$CHROME_AVAILABLE" = true ]; then
    echo "   ✅ Chrome/Chromium is available (recommended)"
else
    echo "   ⚠️  Chrome/Chromium not found - install for best compatibility"
fi

if [ "$FIREFOX_AVAILABLE" = true ]; then
    echo "   ✅ Firefox is available"
else
    echo "   ⚠️  Firefox not found - install as alternative browser"
fi

echo ""
echo "⚠️  Important Security Notes:"
echo "   - Keep your Facebook credentials secure"
echo "   - Use responsibly and follow Facebook's Terms of Service"
echo "   - Start with headless=False to monitor automation"
echo "   - Use reasonable delays between actions"
echo ""
echo "🆘 Support:"
echo "   - Check README.md for troubleshooting"
echo "   - View logs in logs/ directory"
echo "   - Screenshots saved in screenshots/ directory"
echo ""
print_success "Ready to start automating Facebook! 🚀"
