# 🎮 Mobile Game Customization Guide

## 🎯 **How to Customize for YOUR Mobile Game**

### **Step 1: Find Your Game's API Endpoints**

#### **Method A: Use the API Discovery Tool**
```bash
# Run the discovery tool
python3 find_mobile_apis.py

# Enter your game name (e.g., "Clash of Clans", "PUBG Mobile")
# It will automatically test common API patterns
```

#### **Method B: Network Monitoring (Most Accurate)**
```bash
# Use these tools to monitor your game's network traffic:
1. Charles Proxy (Mac/Windows) - https://www.charlesproxy.com/
2. Wireshark (Free) - https://www.wireshark.org/
3. Fiddler (Windows) - https://www.telerik.com/fiddler

# Steps:
1. Start monitoring network traffic
2. Open your mobile game
3. Play through typical user actions
4. Record all API calls made by the game
```

#### **Method C: Developer Documentation**
```bash
# Check if your game has public API documentation:
- Game's official website
- Developer portal
- GitHub repositories
- API documentation sites
```

### **Step 2: Create Custom Configuration**

#### **Run the Customization Tool**
```bash
python3 customize_mobile_tester.py
```

#### **Example Configuration for Different Game Types:**

##### **🔫 Battle Royale Games (PUBG, Fortnite, etc.)**
```json
{
  "game_name": "Your Battle Royale Game",
  "api_base_url": "https://api.yourgame.com",
  "game_type": "battle_royale",
  "custom_endpoints": [
    "/api/v1/matchmaking/join",
    "/api/v1/game/session/start", 
    "/api/v1/game/action/move",
    "/api/v1/game/action/combat"
  ]
}
```

##### **🧩 Puzzle Games (Candy Crush, etc.)**
```json
{
  "game_name": "Your Puzzle Game",
  "api_base_url": "https://api.yourgame.com",
  "game_type": "puzzle",
  "custom_endpoints": [
    "/api/v1/levels/current",
    "/api/v1/game/move",
    "/api/v1/game/level/complete"
  ]
}
```

##### **👥 Social Games (FarmVille, etc.)**
```json
{
  "game_name": "Your Social Game", 
  "api_base_url": "https://api.yourgame.com",
  "game_type": "social",
  "custom_endpoints": [
    "/api/v1/social/friends",
    "/api/v1/social/gifts/send",
    "/api/v1/social/visit"
  ]
}
```

### **Step 3: Real Examples**

#### **Example 1: Popular Mobile Game APIs**

##### **Clash of Clans Style Game**
```python
# Typical API flow:
1. POST /api/v1/auth/login          → Player authentication
2. GET  /api/v1/village/status      → Village state
3. POST /api/v1/buildings/upgrade   → Building upgrades  
4. GET  /api/v1/clan/info          → Clan information
5. POST /api/v1/attacks/start       → Start attack
```

##### **Match-3 Puzzle Game**
```python
# Typical API flow:
1. POST /api/v1/auth/login          → Player login
2. GET  /api/v1/levels/current      → Current level
3. POST /api/v1/game/start          → Start level
4. POST /api/v1/game/move           → Make moves
5. POST /api/v1/game/complete       → Complete level
```

### **Step 4: Customize Headers for Your Game**

#### **Common Mobile Game Headers**
```python
headers = {
    'User-Agent': 'YourGame/2.1.0 (iPhone; iOS 15.0; Scale/3.00)',
    'X-Platform': 'iOS',
    'X-App-Version': '2.1.0', 
    'X-Device-Model': 'iPhone13,2',
    'X-Game-Session-ID': '{session_id}',
    'Authorization': 'Bearer {auth_token}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
```

#### **Game-Specific Headers Examples**
```python
# Supercell Games (Clash of Clans, etc.)
'X-Supercell-Token': '{game_token}'

# King Games (Candy Crush, etc.)  
'X-King-Client-Version': '1.234.0'

# Niantic Games (Pokemon GO, etc.)
'X-Unity-Version': '2019.4.18f1'
```

### **Step 5: Authentication Patterns**

#### **Device-Based Authentication**
```python
{
    "device_id": "unique_device_uuid",
    "platform": "iOS",
    "app_version": "2.1.0"
}
```

#### **Social Login (Facebook/Google)**
```python
{
    "provider": "facebook",
    "access_token": "facebook_access_token",
    "device_id": "unique_device_uuid"
}
```

#### **Username/Password**
```python
{
    "username": "player_username",
    "password": "player_password", 
    "device_id": "unique_device_uuid"
}
```

### **Step 6: Test Your Customization**

#### **Start with Small Load**
```bash
# Test with 5 concurrent devices first
Concurrent Devices: 5
Duration: 60 seconds
Platform: iOS
```

#### **Monitor Key Metrics**
- **Success Rate**: Should be >90%
- **Auth Success**: Should be >95%
- **Response Times**: <2 seconds
- **Rate Limiting**: Watch for 429 errors

#### **Gradually Increase Load**
```bash
# If 5 devices work well, try:
Test 1: 5 devices  → Success? → Try 10
Test 2: 10 devices → Success? → Try 25  
Test 3: 25 devices → Success? → Try 50
Test 4: 50 devices → Success? → Try 100
```

### **Step 7: Advanced Customization**

#### **Custom Payload Generation**
```python
def generate_custom_payload(action_type, user_id, device_id):
    if action_type == "battle_action":
        return {
            "action": "attack",
            "target_id": f"enemy_{user_id % 100}",
            "weapon": "sword",
            "position": {"x": random.randint(0, 1000), "y": random.randint(0, 1000)}
        }
    elif action_type == "puzzle_move":
        return {
            "from": {"row": random.randint(0, 7), "col": random.randint(0, 7)},
            "to": {"row": random.randint(0, 7), "col": random.randint(0, 7)},
            "move_type": "swap"
        }
```

#### **Dynamic Authentication**
```python
def handle_authentication(session, base_url, user_id, device_id):
    # Step 1: Get session token
    auth_response = session.post(f"{base_url}/api/v1/auth/device", json={
        "device_id": device_id,
        "platform": "iOS"
    })
    
    # Step 2: Login with credentials
    if auth_response.status_code == 200:
        session_token = auth_response.json()["session_token"]
        
        login_response = session.post(f"{base_url}/api/v1/auth/login", json={
            "username": f"test_user_{user_id}",
            "session_token": session_token
        })
        
        return login_response.json().get("access_token")
```

### **Step 8: Production Testing Checklist**

#### **Before Testing Production**
- [ ] **Permission**: Ensure you have permission to test
- [ ] **Rate Limits**: Understand API rate limits
- [ ] **Start Small**: Begin with 1-5 concurrent users
- [ ] **Monitor**: Have monitoring in place
- [ ] **Rollback**: Plan for stopping tests quickly

#### **During Testing**
- [ ] **Watch Metrics**: Monitor success rates continuously
- [ ] **Check Logs**: Look for error patterns
- [ ] **Server Health**: Monitor your game servers
- [ ] **User Impact**: Ensure real users aren't affected

#### **After Testing**
- [ ] **Analyze Results**: Identify bottlenecks
- [ ] **Document Findings**: Record performance limits
- [ ] **Plan Improvements**: Schedule optimizations
- [ ] **Regular Testing**: Set up automated tests

## 🎯 **Quick Start Examples**

### **Test Popular Game Types**

#### **Battle Royale Game**
```bash
# 1. Open Mobile App Tester: http://localhost:5002
# 2. Configure:
API Base URL: https://api.yourbattleroyalegame.com
Scenario: Complete User Journey  
Concurrent Devices: 10
Duration: 300 seconds
Platform: Mixed

# 3. Watch for:
- Matchmaking delays
- Real-time action latency
- Session management
```

#### **Puzzle Game**
```bash
# 1. Configure:
API Base URL: https://api.yourpuzzlegame.com
Scenario: Complete User Journey
Concurrent Devices: 25
Duration: 180 seconds
Platform: iOS

# 2. Watch for:
- Level loading times
- Move validation speed
- Progress saving
```

#### **Social Game**
```bash
# 1. Configure:
API Base URL: https://api.yoursocialgame.com
Scenario: Social Features
Concurrent Devices: 15
Duration: 240 seconds
Platform: Android

# 2. Watch for:
- Friend list loading
- Gift sending/receiving
- Social notifications
```

## 🚀 **Ready to Test Your Game!**

Your mobile app load testing system is now fully customizable for any mobile game. Use the tools provided to discover APIs, create custom scenarios, and run realistic load tests that match your actual user behavior patterns.

**Start testing and optimize your mobile game for success! 🎮📱**
