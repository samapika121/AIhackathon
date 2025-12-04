# 🎮 Video-Based Load Testing System

An innovative load testing platform that uses **real gameplay videos** to create realistic user behavior patterns for testing game applications and APIs.

## 🌟 Key Features

### **📹 Video-Based Scenario Creation**
- Upload gameplay videos (login → lobby → game launch)
- AI-powered analysis extracts user actions and timing
- Generates realistic API call patterns
- Supports multiple game types and UI patterns

### **🚀 Realistic Load Testing**
- Simulates real user behavior from video analysis
- Concurrent user simulation with realistic timing
- Gradual ramp-up to simulate organic traffic
- Real-time metrics and monitoring

### **📊 Comprehensive Analytics**
- Live dashboard with real-time metrics
- Success/failure rates and response times
- Detailed test reports and visualizations
- Performance bottleneck identification

### **🔧 Easy Integration**
- Web-based dashboard for non-technical users
- REST API for programmatic access
- Supports any game/application with HTTP APIs
- Export results for further analysis

## 🚀 Quick Start

### **1. Installation**

```bash
# Clone or navigate to the project
cd video_load_tester

# Install dependencies
pip install -r requirements.txt
```

### **2. Start the System**

```bash
# Terminal 1: Start the load testing dashboard
python main.py

# Terminal 2: Start the game API simulator (for testing)
python game_api_simulator.py
```

### **3. Access the Dashboard**

Open your browser and go to:
- **Load Tester Dashboard**: http://localhost:5000
- **Game API Simulator**: http://localhost:3000

## 📖 How It Works

### **Step 1: Record Gameplay Video**
1. Record a video of typical user flow in your game:
   - Login process
   - Navigate to lobby/menu
   - Join a game/match
   - Basic gameplay interactions

### **Step 2: Upload and Analyze**
1. Upload video to the dashboard
2. AI analyzes the video to extract:
   - User action timing
   - UI state transitions
   - API call patterns
   - Realistic user behavior

### **Step 3: Configure Load Test**
1. Select your analyzed scenario
2. Set test parameters:
   - Number of concurrent users
   - Test duration
   - Ramp-up time
   - Target API URL

### **Step 4: Run and Monitor**
1. Start the load test
2. Monitor real-time metrics
3. View detailed results and reports

## 🎯 Use Cases

### **Game Development**
- Test login servers during launch events
- Validate matchmaking system performance
- Stress test game lobbies and menus
- Simulate realistic player behavior patterns

### **API Testing**
- Test authentication endpoints
- Validate session management
- Check database performance under load
- Test CDN and asset delivery

### **Performance Optimization**
- Identify bottlenecks in user flows
- Optimize server response times
- Test auto-scaling configurations
- Validate caching strategies

## 📊 Dashboard Features

### **📹 Video Scenario Management**
- Upload and manage gameplay videos
- View extracted user action patterns
- Edit and customize scenarios
- Share scenarios with team members

### **🚀 Load Test Configuration**
- Visual test setup wizard
- Pre-configured templates for common scenarios
- Advanced timing and behavior customization
- Integration with CI/CD pipelines

### **📈 Real-Time Monitoring**
- Live metrics dashboard
- Success/failure rate tracking
- Response time distributions
- Error analysis and categorization

### **📋 Detailed Reporting**
- Comprehensive test reports
- Performance trend analysis
- Comparison between test runs
- Export to various formats (JSON, CSV, PDF)

## 🔧 Configuration Options

### **Video Analysis Settings**
```python
{
    "frame_analysis_interval": 5,  # Analyze every 5th frame
    "ui_detection_sensitivity": 0.7,  # UI element detection threshold
    "action_confidence_threshold": 0.6,  # Minimum confidence for actions
    "game_type": "battle_royale"  # Optimize for specific game types
}
```

### **Load Test Parameters**
```python
{
    "concurrent_users": 100,  # Number of simultaneous users
    "duration": 600,  # Test duration in seconds
    "ramp_up_time": 120,  # Time to reach full load
    "think_time": {"min": 1, "max": 5},  # User pause between actions
    "failure_threshold": 0.05  # Acceptable failure rate (5%)
}
```

## 🌐 API Integration

### **Start Load Test**
```bash
curl -X POST http://localhost:5000/start_test \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "login_lobby_game",
    "target_url": "https://your-game-api.com",
    "concurrent_users": 50,
    "duration": 300
  }'
```

### **Get Test Results**
```bash
curl http://localhost:5000/test_results/test_12345
```

### **Upload Video Scenario**
```bash
curl -X POST http://localhost:5000/upload_scenario \
  -F "video=@gameplay_recording.mp4" \
  -F "scenario_name=login_flow"
```

## 🎮 Game API Simulator

For testing and demonstration, we include a realistic game API simulator:

### **Available Endpoints**
- `POST /api/login` - User authentication
- `GET /api/lobby` - Lobby/matchmaking info
- `POST /api/join_game` - Join game session
- `GET /api/game_status` - Current game state
- `POST /api/logout` - User logout
- `GET /api/server_stats` - Server statistics

### **Realistic Behavior**
- Variable response times
- Occasional failures (5-15% rate)
- Server load simulation
- Session management
- Background user activity

## 📈 Advanced Features

### **AI-Powered Analysis**
- Computer vision for UI element detection
- Machine learning for action recognition
- Behavioral pattern extraction
- Timing optimization for realistic simulation

### **Scalability**
- Distributed load generation
- Cloud deployment support
- Auto-scaling based on demand
- Multi-region testing capabilities

### **Integration Options**
- CI/CD pipeline integration
- Slack/Discord notifications
- Custom webhook support
- Third-party monitoring tools

## 🛠 Development and Customization

### **Adding New Game Types**
1. Extend `GameVideoAnalyzer` class
2. Add game-specific UI detection patterns
3. Define custom API call mappings
4. Test with sample gameplay videos

### **Custom UI Detection**
```python
def detect_custom_ui_element(self, frame):
    # Add your custom UI detection logic
    # Use template matching, color detection, or ML models
    pass
```

### **API Call Customization**
```python
def generate_custom_api_calls(self, actions):
    # Map video actions to your specific API endpoints
    # Customize request payloads and timing
    pass
```

## 🚀 Production Deployment

### **Docker Deployment**
```bash
# Build container
docker build -t video-load-tester .

# Run with docker-compose
docker-compose up -d
```

### **Cloud Deployment**
- AWS ECS/Fargate support
- Google Cloud Run compatibility
- Kubernetes manifests included
- Auto-scaling configurations

### **Monitoring and Alerting**
- Prometheus metrics export
- Grafana dashboard templates
- Custom alerting rules
- Performance threshold monitoring

## 📞 Support and Community

### **Getting Help**
- Check the troubleshooting guide
- Review example scenarios
- Join our Discord community
- Submit GitHub issues

### **Contributing**
- Fork the repository
- Add new features or game types
- Submit pull requests
- Share your gameplay scenarios

## 🎯 Roadmap

### **Upcoming Features**
- Mobile game support (touch gestures)
- VR/AR game compatibility
- Machine learning model improvements
- Real-time collaboration features
- Advanced analytics and insights

---

**Transform your load testing with realistic user behavior patterns! 🚀**

Start by recording a simple gameplay video and see how our AI creates comprehensive load test scenarios that mirror real user interactions.
