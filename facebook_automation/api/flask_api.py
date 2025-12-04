"""
Facebook Automation Framework - Flask API
Web interface for controlling Facebook automation
"""

from flask import Flask, request, jsonify, render_template_string
import threading
import time
from datetime import datetime
from core.facebook_automation import FacebookAutomation
from config.settings import FacebookConfig, APIConfig
from utils.logger import setup_logger
import json

app = Flask(__name__)
logger = setup_logger(__name__)

# Global automation instances
automation_sessions = {}
session_counter = 0

class AutomationSession:
    """Manages a single automation session"""
    
    def __init__(self, session_id):
        self.session_id = session_id
        self.automation = FacebookAutomation()
        self.status = 'created'
        self.created_at = datetime.now()
        self.logs = []
        self.current_action = None
        
    def add_log(self, level, message):
        """Add log entry"""
        self.logs.append({
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message
        })
        
        # Keep only last 100 logs
        if len(self.logs) > 100:
            self.logs = self.logs[-100:]

@app.route('/')
def dashboard():
    """Facebook Automation Dashboard"""
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Automation Framework</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f0f2f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .section { margin: 20px 0; padding: 25px; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .button { padding: 12px 24px; background: #1877f2; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; margin: 5px; }
        .button:hover { background: #166fe5; }
        .button.danger { background: #dc3545; }
        .button.danger:hover { background: #c82333; }
        .form-group { margin: 15px 0; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: 600; }
        .form-group input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; }
        .session-card { padding: 15px; margin: 10px 0; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #1877f2; }
        .status-active { color: #28a745; font-weight: bold; }
        .status-inactive { color: #6c757d; font-weight: bold; }
        .status-error { color: #dc3545; font-weight: bold; }
        .logs { background: #000; color: #00ff00; padding: 15px; border-radius: 5px; max-height: 300px; overflow-y: auto; font-family: monospace; }
        h1 { color: #1877f2; text-align: center; }
        .tabs { display: flex; margin-bottom: 20px; }
        .tab { padding: 10px 20px; background: #e9ecef; border: none; cursor: pointer; }
        .tab.active { background: #1877f2; color: white; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Facebook Automation Framework</h1>
        <p style="text-align: center; color: #666;">Automate Facebook login, navigation, and game interactions</p>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('control')">🎮 Control Panel</button>
            <button class="tab" onclick="showTab('sessions')">📊 Sessions</button>
            <button class="tab" onclick="showTab('logs')">📝 Logs</button>
            <button class="tab" onclick="showTab('settings')">⚙️ Settings</button>
        </div>
        
        <div id="control-tab" class="tab-content active">
            <div class="section">
                <h2>🚀 Quick Actions</h2>
                <button class="button" onclick="createSession()">🆕 Create New Session</button>
                <button class="button" onclick="loginToFacebook()">🔐 Login to Facebook</button>
                <button class="button" onclick="navigateToGames()">🎮 Go to Games</button>
                <button class="button" onclick="launchGame()">🎯 Launch Game</button>
                <button class="button danger" onclick="stopAllSessions()">🛑 Stop All Sessions</button>
            </div>
            
            <div class="section">
                <h2>🎮 Game Automation</h2>
                <div class="form-group">
                    <label>Select Game:</label>
                    <select id="gameSelect">
                        <option value="farmville">FarmVille</option>
                        <option value="candy_crush">Candy Crush</option>
                        <option value="words_with_friends">Words with Friends</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Actions to Perform:</label>
                    <select id="actionSelect" multiple style="height: 120px;">
                        <option value="click_play_button">Click Play Button</option>
                        <option value="wait_for_game_load">Wait for Game Load</option>
                        <option value="perform_game_action">Perform Game Action</option>
                        <option value="collect_rewards">Collect Rewards</option>
                        <option value="check_notifications">Check Notifications</option>
                    </select>
                </div>
                <button class="button" onclick="performGameActions()">⚡ Perform Actions</button>
            </div>
        </div>
        
        <div id="sessions-tab" class="tab-content">
            <div class="section">
                <h2>📊 Active Sessions</h2>
                <div id="sessionsList">Loading sessions...</div>
                <button class="button" onclick="refreshSessions()">🔄 Refresh</button>
            </div>
        </div>
        
        <div id="logs-tab" class="tab-content">
            <div class="section">
                <h2>📝 Session Logs</h2>
                <div class="form-group">
                    <label>Select Session:</label>
                    <select id="logSessionSelect">
                        <option value="">Select a session...</option>
                    </select>
                </div>
                <div id="logsContainer" class="logs">
                    Select a session to view logs...
                </div>
                <button class="button" onclick="refreshLogs()">🔄 Refresh Logs</button>
            </div>
        </div>
        
        <div id="settings-tab" class="tab-content">
            <div class="section">
                <h2>⚙️ Browser Settings</h2>
                <div class="form-group">
                    <label>Browser Type:</label>
                    <select id="browserType">
                        <option value="chrome">Chrome</option>
                        <option value="firefox">Firefox</option>
                        <option value="edge">Edge</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Headless Mode:</label>
                    <select id="headlessMode">
                        <option value="false">No (Show Browser)</option>
                        <option value="true">Yes (Hidden)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Facebook Email:</label>
                    <input type="email" id="facebookEmail" placeholder="your@email.com">
                </div>
                <div class="form-group">
                    <label>Facebook Password:</label>
                    <input type="password" id="facebookPassword" placeholder="Your password">
                </div>
                <button class="button" onclick="saveSettings()">💾 Save Settings</button>
            </div>
            
            <div class="section">
                <h2>📖 Usage Guide</h2>
                <h3>🚀 Getting Started:</h3>
                <ol>
                    <li>Configure your Facebook credentials in Settings</li>
                    <li>Create a new automation session</li>
                    <li>Login to Facebook</li>
                    <li>Navigate to games and start automation</li>
                </ol>
                
                <h3>🎮 Game Automation:</h3>
                <ul>
                    <li><strong>FarmVille:</strong> Automated farming and resource collection</li>
                    <li><strong>Candy Crush:</strong> Level progression and reward collection</li>
                    <li><strong>Words with Friends:</strong> Game interaction and notifications</li>
                </ul>
                
                <h3>⚠️ Important Notes:</h3>
                <ul>
                    <li>Use responsibly and follow Facebook's Terms of Service</li>
                    <li>Start with headless mode disabled to monitor actions</li>
                    <li>Keep sessions short to avoid detection</li>
                    <li>Use random delays between actions</li>
                </ul>
            </div>
        </div>
    </div>

    <script>
        let currentSessionId = null;
        
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            document.getElementById(tabName + '-tab').classList.add('active');
            event.target.classList.add('active');
        }
        
        function createSession() {
            const browserType = document.getElementById('browserType').value;
            const headless = document.getElementById('headlessMode').value === 'true';
            
            fetch('/api/create_session', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    browser_type: browserType,
                    headless: headless
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    currentSessionId = data.session_id;
                    alert('✅ Session created: ' + data.session_id);
                    refreshSessions();
                } else {
                    alert('❌ Error: ' + data.error);
                }
            });
        }
        
        function loginToFacebook() {
            if (!currentSessionId) {
                alert('Please create a session first');
                return;
            }
            
            const email = document.getElementById('facebookEmail').value;
            const password = document.getElementById('facebookPassword').value;
            
            if (!email || !password) {
                alert('Please enter Facebook credentials in Settings');
                return;
            }
            
            fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    session_id: currentSessionId,
                    email: email,
                    password: password
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✅ Successfully logged in to Facebook');
                } else {
                    alert('❌ Login failed: ' + data.error);
                }
            });
        }
        
        function navigateToGames() {
            if (!currentSessionId) {
                alert('Please create a session and login first');
                return;
            }
            
            fetch('/api/navigate_games', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({session_id: currentSessionId})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✅ Navigated to Facebook Games');
                } else {
                    alert('❌ Navigation failed: ' + data.error);
                }
            });
        }
        
        function launchGame() {
            if (!currentSessionId) {
                alert('Please create a session and login first');
                return;
            }
            
            const gameName = document.getElementById('gameSelect').value;
            
            fetch('/api/launch_game', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    session_id: currentSessionId,
                    game_name: gameName
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✅ Game launched: ' + gameName);
                } else {
                    alert('❌ Game launch failed: ' + data.error);
                }
            });
        }
        
        function performGameActions() {
            if (!currentSessionId) {
                alert('Please create a session and launch a game first');
                return;
            }
            
            const gameName = document.getElementById('gameSelect').value;
            const actionSelect = document.getElementById('actionSelect');
            const actions = Array.from(actionSelect.selectedOptions).map(option => option.value);
            
            if (actions.length === 0) {
                alert('Please select at least one action');
                return;
            }
            
            fetch('/api/perform_actions', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    session_id: currentSessionId,
                    game_name: gameName,
                    actions: actions
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✅ Game actions completed');
                } else {
                    alert('❌ Actions failed: ' + data.error);
                }
            });
        }
        
        function refreshSessions() {
            fetch('/api/sessions')
            .then(response => response.json())
            .then(data => {
                const container = document.getElementById('sessionsList');
                const logSelect = document.getElementById('logSessionSelect');
                
                container.innerHTML = '';
                logSelect.innerHTML = '<option value="">Select a session...</option>';
                
                if (Object.keys(data).length === 0) {
                    container.innerHTML = '<p>No active sessions</p>';
                    return;
                }
                
                Object.values(data).forEach(session => {
                    const sessionDiv = document.createElement('div');
                    sessionDiv.className = 'session-card';
                    
                    const statusClass = session.status === 'active' ? 'status-active' : 
                                      session.status === 'error' ? 'status-error' : 'status-inactive';
                    
                    sessionDiv.innerHTML = `
                        <strong>Session ${session.session_id}</strong> - 
                        <span class="${statusClass}">${session.status.toUpperCase()}</span><br>
                        <small>Created: ${new Date(session.created_at).toLocaleString()}</small><br>
                        <small>Current Action: ${session.current_action || 'None'}</small>
                        <button class="button danger" onclick="stopSession('${session.session_id}')" style="float: right;">Stop</button>
                    `;
                    container.appendChild(sessionDiv);
                    
                    // Add to log select
                    const option = document.createElement('option');
                    option.value = session.session_id;
                    option.textContent = `Session ${session.session_id}`;
                    logSelect.appendChild(option);
                });
            });
        }
        
        function stopSession(sessionId) {
            fetch('/api/stop_session', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({session_id: sessionId})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✅ Session stopped');
                    refreshSessions();
                } else {
                    alert('❌ Error stopping session: ' + data.error);
                }
            });
        }
        
        function stopAllSessions() {
            if (confirm('Are you sure you want to stop all sessions?')) {
                fetch('/api/stop_all_sessions', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert('✅ All sessions stopped');
                    refreshSessions();
                });
            }
        }
        
        function refreshLogs() {
            const sessionId = document.getElementById('logSessionSelect').value;
            if (!sessionId) return;
            
            fetch(`/api/logs/${sessionId}`)
            .then(response => response.json())
            .then(data => {
                const container = document.getElementById('logsContainer');
                container.innerHTML = '';
                
                data.logs.forEach(log => {
                    const logLine = document.createElement('div');
                    logLine.textContent = `[${log.timestamp}] ${log.level}: ${log.message}`;
                    container.appendChild(logLine);
                });
                
                container.scrollTop = container.scrollHeight;
            });
        }
        
        function saveSettings() {
            alert('✅ Settings saved (stored in browser session)');
        }
        
        // Auto-refresh sessions every 10 seconds
        setInterval(refreshSessions, 10000);
        
        // Initial load
        refreshSessions();
    </script>
</body>
</html>
    ''')

@app.route('/api/create_session', methods=['POST'])
def create_session():
    """Create new automation session"""
    global session_counter
    try:
        data = request.get_json() or {}
        
        session_counter += 1
        session_id = f"session_{session_counter}"
        
        session = AutomationSession(session_id)
        
        # Start browser session
        browser_type = data.get('browser_type', 'chrome')
        headless = data.get('headless', False)
        
        success = session.automation.start_session(browser_type, headless)
        
        if success:
            session.status = 'active'
            session.add_log('INFO', f'Session created with {browser_type} browser')
            automation_sessions[session_id] = session
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'message': 'Session created successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create browser session'
            })
            
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/login', methods=['POST'])
def login():
    """Login to Facebook"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        email = data.get('email')
        password = data.get('password')
        
        if session_id not in automation_sessions:
            return jsonify({'success': False, 'error': 'Session not found'})
        
        session = automation_sessions[session_id]
        session.current_action = 'Logging in to Facebook'
        session.add_log('INFO', 'Starting Facebook login')
        
        success = session.automation.login_to_facebook(email, password)
        
        if success:
            session.add_log('INFO', 'Successfully logged in to Facebook')
            return jsonify({'success': True, 'message': 'Login successful'})
        else:
            session.add_log('ERROR', 'Facebook login failed')
            return jsonify({'success': False, 'error': 'Login failed'})
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/navigate_games', methods=['POST'])
def navigate_games():
    """Navigate to Facebook Games"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if session_id not in automation_sessions:
            return jsonify({'success': False, 'error': 'Session not found'})
        
        session = automation_sessions[session_id]
        session.current_action = 'Navigating to Games'
        session.add_log('INFO', 'Navigating to Facebook Games')
        
        success = session.automation.navigate_to_games()
        
        if success:
            session.add_log('INFO', 'Successfully navigated to Games')
            return jsonify({'success': True, 'message': 'Navigation successful'})
        else:
            session.add_log('ERROR', 'Failed to navigate to Games')
            return jsonify({'success': False, 'error': 'Navigation failed'})
            
    except Exception as e:
        logger.error(f"Navigation error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/launch_game', methods=['POST'])
def launch_game():
    """Launch specific game"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        game_name = data.get('game_name')
        
        if session_id not in automation_sessions:
            return jsonify({'success': False, 'error': 'Session not found'})
        
        session = automation_sessions[session_id]
        session.current_action = f'Launching {game_name}'
        session.add_log('INFO', f'Launching game: {game_name}')
        
        success = session.automation.launch_game(game_name)
        
        if success:
            session.add_log('INFO', f'Successfully launched {game_name}')
            return jsonify({'success': True, 'message': f'Game {game_name} launched'})
        else:
            session.add_log('ERROR', f'Failed to launch {game_name}')
            return jsonify({'success': False, 'error': f'Failed to launch {game_name}'})
            
    except Exception as e:
        logger.error(f"Game launch error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/perform_actions', methods=['POST'])
def perform_actions():
    """Perform game actions"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        game_name = data.get('game_name')
        actions = data.get('actions', [])
        
        if session_id not in automation_sessions:
            return jsonify({'success': False, 'error': 'Session not found'})
        
        session = automation_sessions[session_id]
        session.current_action = f'Performing actions in {game_name}'
        session.add_log('INFO', f'Performing {len(actions)} actions in {game_name}')
        
        success = session.automation.perform_game_actions(game_name, actions)
        
        if success:
            session.add_log('INFO', 'Game actions completed successfully')
            return jsonify({'success': True, 'message': 'Actions completed'})
        else:
            session.add_log('ERROR', 'Game actions failed')
            return jsonify({'success': False, 'error': 'Actions failed'})
            
    except Exception as e:
        logger.error(f"Actions error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/sessions')
def get_sessions():
    """Get all active sessions"""
    sessions_data = {}
    for session_id, session in automation_sessions.items():
        sessions_data[session_id] = {
            'session_id': session.session_id,
            'status': session.status,
            'created_at': session.created_at.isoformat(),
            'current_action': session.current_action,
            'log_count': len(session.logs)
        }
    return jsonify(sessions_data)

@app.route('/api/logs/<session_id>')
def get_logs(session_id):
    """Get logs for specific session"""
    if session_id not in automation_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = automation_sessions[session_id]
    return jsonify({'logs': session.logs})

@app.route('/api/stop_session', methods=['POST'])
def stop_session():
    """Stop specific session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if session_id not in automation_sessions:
            return jsonify({'success': False, 'error': 'Session not found'})
        
        session = automation_sessions[session_id]
        session.automation.end_session()
        session.status = 'stopped'
        session.add_log('INFO', 'Session stopped by user')
        
        del automation_sessions[session_id]
        
        return jsonify({'success': True, 'message': 'Session stopped'})
        
    except Exception as e:
        logger.error(f"Stop session error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stop_all_sessions', methods=['POST'])
def stop_all_sessions():
    """Stop all active sessions"""
    try:
        for session_id, session in list(automation_sessions.items()):
            session.automation.end_session()
            session.status = 'stopped'
        
        automation_sessions.clear()
        
        return jsonify({'success': True, 'message': 'All sessions stopped'})
        
    except Exception as e:
        logger.error(f"Stop all sessions error: {e}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    logger.info("Starting Facebook Automation API...")
    logger.info(f"Dashboard available at: http://localhost:{APIConfig.API_PORT}")
    
    app.run(
        host=APIConfig.API_HOST,
        port=APIConfig.API_PORT,
        debug=APIConfig.API_DEBUG
    )
