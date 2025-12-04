#!/usr/bin/env python3
"""
Mobile App Load Tester
Test mobile game APIs and backends
"""

from flask import Flask, request, jsonify, render_template_string
import requests
import json
import time
import threading
from datetime import datetime
from typing import Dict, Any, List
import base64
import uuid

app = Flask(__name__)

class MobileAppLoadTester:
    def __init__(self):
        self.active_tests = {}
        
    def create_mobile_scenarios(self, app_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create mobile app specific scenarios"""
        base_url = app_info.get('api_base_url', 'https://api.yourgame.com')
        
        scenarios = []
        
        # Mobile Game Scenario 1: Complete User Journey
        scenarios.append({
            'name': 'Mobile Game - Complete Journey',
            'description': 'Full mobile game user flow',
            'actions': [
                {
                    'name': 'App Launch',
                    'method': 'POST',
                    'endpoint': '/api/v1/app/launch',
                    'delay': 2.0,
                    'headers': self._get_mobile_headers(),
                    'payload': {
                        'device_id': '{device_id}',
                        'app_version': '1.0.0',
                        'platform': 'iOS'
                    }
                },
                {
                    'name': 'User Login',
                    'method': 'POST', 
                    'endpoint': '/api/v1/auth/login',
                    'delay': 3.0,
                    'payload': {
                        'username': 'test_user_{user_id}',
                        'password': 'test_password',
                        'device_id': '{device_id}'
                    }
                },
                {
                    'name': 'Load Player Data',
                    'method': 'GET',
                    'endpoint': '/api/v1/player/profile',
                    'delay': 1.5,
                    'headers': {'Authorization': 'Bearer {auth_token}'}
                },
                {
                    'name': 'Start Game Session',
                    'method': 'POST',
                    'endpoint': '/api/v1/game/start',
                    'delay': 1.0,
                    'payload': {'game_mode': 'normal'}
                },
                {
                    'name': 'Game Action',
                    'method': 'POST',
                    'endpoint': '/api/v1/game/action',
                    'delay': 0.5,
                    'payload': {'action': 'move', 'x': 100, 'y': 200}
                },
                {
                    'name': 'End Game Session',
                    'method': 'POST',
                    'endpoint': '/api/v1/game/end',
                    'delay': 2.0,
                    'payload': {'score': 1500, 'duration': 120}
                }
            ]
        })
        
        # Mobile Scenario 2: Social Features
        scenarios.append({
            'name': 'Mobile Game - Social Features',
            'description': 'Test social and multiplayer features',
            'actions': [
                {
                    'name': 'Get Friends List',
                    'method': 'GET',
                    'endpoint': '/api/v1/social/friends',
                    'delay': 1.0
                },
                {
                    'name': 'Send Gift',
                    'method': 'POST',
                    'endpoint': '/api/v1/social/gift',
                    'delay': 1.5,
                    'payload': {'friend_id': 'friend_123', 'gift_type': 'coins'}
                },
                {
                    'name': 'Join Multiplayer',
                    'method': 'POST',
                    'endpoint': '/api/v1/multiplayer/join',
                    'delay': 2.0,
                    'payload': {'room_type': 'quick_match'}
                }
            ]
        })
        
        return scenarios
    
    def _get_mobile_headers(self) -> Dict[str, str]:
        """Generate realistic mobile app headers"""
        return {
            'User-Agent': 'YourGame/1.0.0 (iPhone; iOS 15.0; Scale/3.00)',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Platform': 'iOS',
            'X-App-Version': '1.0.0',
            'X-Device-Type': 'iPhone13,2'
        }
    
    def run_mobile_load_test(self, config: Dict[str, Any]) -> str:
        """Run mobile app load test"""
        test_id = f"mobile_test_{int(time.time())}"
        
        test_session = {
            'id': test_id,
            'config': config,
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'results': [],
            'metrics': {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'avg_response_time': 0,
                'auth_failures': 0,
                'device_simulations': 0
            }
        }
        
        self.active_tests[test_id] = test_session
        
        # Start test
        thread = threading.Thread(target=self._execute_mobile_test, args=(test_id, config))
        thread.daemon = True
        thread.start()
        
        return test_id
    
    def _execute_mobile_test(self, test_id: str, config: Dict[str, Any]):
        """Execute mobile load test"""
        try:
            base_url = config['api_base_url']
            scenario = config['scenario']
            concurrent_devices = config.get('concurrent_devices', 10)
            duration = config.get('duration', 300)
            
            # Create device simulation threads
            device_threads = []
            
            for device_id in range(concurrent_devices):
                thread = threading.Thread(
                    target=self._simulate_mobile_device,
                    args=(test_id, device_id, base_url, scenario, duration)
                )
                thread.daemon = True
                device_threads.append(thread)
                thread.start()
            
            # Monitor test
            start_time = time.time()
            while time.time() - start_time < duration:
                self._update_mobile_metrics(test_id)
                time.sleep(5)
            
            # Wait for completion
            for thread in device_threads:
                thread.join(timeout=30)
            
            self.active_tests[test_id]['status'] = 'completed'
            
        except Exception as e:
            self.active_tests[test_id]['status'] = 'failed'
            self.active_tests[test_id]['error'] = str(e)
    
    def _simulate_mobile_device(self, test_id: str, device_id: int, base_url: str, scenario: Dict, duration: float):
        """Simulate a single mobile device"""
        session = requests.Session()
        
        # Generate unique device info
        device_uuid = str(uuid.uuid4())
        auth_token = None
        
        session_start = time.time()
        device_results = []
        
        while time.time() - session_start < duration:
            for action in scenario['actions']:
                if time.time() - session_start >= duration:
                    break
                
                # Prepare action with device-specific data
                prepared_action = self._prepare_mobile_action(action, device_id, device_uuid, auth_token)
                
                result = self._execute_mobile_action(session, base_url, prepared_action, device_id)
                device_results.append(result)
                
                # Extract auth token if login was successful
                if action['name'] == 'User Login' and result['success']:
                    try:
                        response_data = json.loads(result.get('response_body', '{}'))
                        auth_token = response_data.get('access_token') or response_data.get('token')
                    except:
                        pass
                
                time.sleep(action.get('delay', 1.0))
        
        self.active_tests[test_id]['results'].extend(device_results)
    
    def _prepare_mobile_action(self, action: Dict, device_id: int, device_uuid: str, auth_token: str) -> Dict:
        """Prepare action with mobile-specific data"""
        prepared = action.copy()
        
        # Replace placeholders in payload
        if 'payload' in prepared:
            payload = json.dumps(prepared['payload'])
            payload = payload.replace('{device_id}', device_uuid)
            payload = payload.replace('{user_id}', str(device_id))
            prepared['payload'] = json.loads(payload)
        
        # Add auth token to headers if available
        if auth_token and 'headers' in prepared:
            if 'Authorization' in prepared['headers']:
                prepared['headers']['Authorization'] = prepared['headers']['Authorization'].replace('{auth_token}', auth_token)
        
        return prepared
    
    def _execute_mobile_action(self, session: requests.Session, base_url: str, action: Dict, device_id: int) -> Dict:
        """Execute mobile action"""
        start_time = time.time()
        
        try:
            url = f"{base_url.rstrip('/')}{action['endpoint']}"
            method = action.get('method', 'GET').upper()
            headers = action.get('headers', {})
            payload = action.get('payload', {})
            
            # Add mobile headers
            mobile_headers = self._get_mobile_headers()
            headers.update(mobile_headers)
            
            if method == 'POST':
                response = session.post(url, json=payload, headers=headers, timeout=10)
            else:
                response = session.get(url, headers=headers, timeout=10)
            
            return {
                'action': action['name'],
                'method': method,
                'url': url,
                'status_code': response.status_code,
                'response_time': time.time() - start_time,
                'success': 200 <= response.status_code < 400,
                'device_id': device_id,
                'timestamp': datetime.now().isoformat(),
                'response_body': response.text[:500]  # First 500 chars
            }
            
        except Exception as e:
            return {
                'action': action['name'],
                'method': method,
                'url': f"{base_url}{action['endpoint']}",
                'status_code': 0,
                'response_time': time.time() - start_time,
                'success': False,
                'error': str(e),
                'device_id': device_id,
                'timestamp': datetime.now().isoformat()
            }
    
    def _update_mobile_metrics(self, test_id: str):
        """Update mobile test metrics"""
        test_session = self.active_tests[test_id]
        results = test_session['results']
        
        if not results:
            return
        
        total_requests = len(results)
        successful_requests = sum(1 for r in results if r['success'])
        failed_requests = total_requests - successful_requests
        
        response_times = [r['response_time'] for r in results if r['response_time'] > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        auth_failures = sum(1 for r in results if 'login' in r['action'].lower() and not r['success'])
        device_simulations = len(set(r['device_id'] for r in results))
        
        test_session['metrics'].update({
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'avg_response_time': avg_response_time,
            'auth_failures': auth_failures,
            'device_simulations': device_simulations
        })

mobile_tester = MobileAppLoadTester()

@app.route('/')
def mobile_dashboard():
    """Mobile App Testing Dashboard"""
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Mobile App Load Tester</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f0f2f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .section { margin: 20px 0; padding: 25px; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .button { padding: 12px 24px; background: #007bff; color: white; border: none; border-radius: 6px; cursor: pointer; }
        .form-group { margin: 15px 0; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: 600; }
        .form-group input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; }
        .metric-card { padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; text-align: center; }
        h1 { color: #007bff; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📱 Mobile App Load Tester</h1>
        
        <div class="section">
            <h2>🔧 Configure Mobile App Test</h2>
            <div class="form-group">
                <label>API Base URL:</label>
                <input type="url" id="apiBaseUrl" placeholder="https://api.yourgame.com" value="http://localhost:3000">
            </div>
            <div class="form-group">
                <label>Test Scenario:</label>
                <select id="scenario">
                    <option value="complete_journey">Complete User Journey</option>
                    <option value="social_features">Social Features</option>
                </select>
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">
                <div class="form-group">
                    <label>Concurrent Devices:</label>
                    <input type="number" id="concurrentDevices" value="10" min="1" max="100">
                </div>
                <div class="form-group">
                    <label>Duration (seconds):</label>
                    <input type="number" id="duration" value="300" min="60" max="1800">
                </div>
                <div class="form-group">
                    <label>Platform:</label>
                    <select id="platform">
                        <option value="iOS">iOS</option>
                        <option value="Android">Android</option>
                        <option value="Mixed">Mixed</option>
                    </select>
                </div>
            </div>
            <button class="button" onclick="startMobileTest()">📱 Start Mobile Load Test</button>
        </div>
        
        <div class="section">
            <h2>📊 Active Mobile Tests</h2>
            <div id="activeTests">No active tests</div>
        </div>
        
        <div class="section">
            <h2>📈 Mobile Metrics</h2>
            <div id="metricsContainer" class="metrics">
                <div class="metric-card">
                    <div style="font-size: 24px; font-weight: bold;">0</div>
                    <div>Total Requests</div>
                </div>
                <div class="metric-card">
                    <div style="font-size: 24px; font-weight: bold;">0</div>
                    <div>Devices Simulated</div>
                </div>
                <div class="metric-card">
                    <div style="font-size: 24px; font-weight: bold;">0</div>
                    <div>Auth Failures</div>
                </div>
                <div class="metric-card">
                    <div style="font-size: 24px; font-weight: bold;">0.0s</div>
                    <div>Avg Response</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📖 Mobile Testing Guide</h2>
            <h3>🎮 For Mobile Games:</h3>
            <ul>
                <li><strong>API Base URL:</strong> Your game's backend API (e.g., https://api.yourgame.com)</li>
                <li><strong>Authentication:</strong> Tests login flows with device IDs</li>
                <li><strong>Device Simulation:</strong> Each concurrent device has unique ID</li>
                <li><strong>Realistic Headers:</strong> Includes mobile-specific headers</li>
            </ul>
            
            <h3>📱 Common Mobile API Endpoints:</h3>
            <ul>
                <li><code>/api/v1/app/launch</code> - App startup</li>
                <li><code>/api/v1/auth/login</code> - User authentication</li>
                <li><code>/api/v1/player/profile</code> - Player data</li>
                <li><code>/api/v1/game/start</code> - Start game session</li>
                <li><code>/api/v1/game/action</code> - Game actions</li>
                <li><code>/api/v1/social/friends</code> - Social features</li>
            </ul>
        </div>
    </div>

    <script>
        function startMobileTest() {
            const config = {
                api_base_url: document.getElementById('apiBaseUrl').value,
                scenario_type: document.getElementById('scenario').value,
                concurrent_devices: parseInt(document.getElementById('concurrentDevices').value),
                duration: parseInt(document.getElementById('duration').value),
                platform: document.getElementById('platform').value
            };
            
            fetch('/start_mobile_test', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(config)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('📱 Mobile load test started! Test ID: ' + data.test_id);
                    loadActiveTests();
                } else {
                    alert('❌ Error: ' + data.error);
                }
            });
        }
        
        function loadActiveTests() {
            fetch('/mobile_tests')
            .then(response => response.json())
            .then(data => {
                const container = document.getElementById('activeTests');
                container.innerHTML = '';
                
                if (Object.keys(data).length === 0) {
                    container.innerHTML = 'No active tests';
                    return;
                }
                
                Object.values(data).forEach(test => {
                    const testDiv = document.createElement('div');
                    testDiv.style.cssText = 'padding: 15px; margin: 10px 0; background: #f8f9fa; border-radius: 8px;';
                    testDiv.innerHTML = `
                        <strong>📱 ${test.id}</strong> - ${test.status.toUpperCase()}<br>
                        <small>Devices: ${test.config.concurrent_devices} | Started: ${new Date(test.start_time).toLocaleTimeString()}</small>
                    `;
                    container.appendChild(testDiv);
                });
            });
        }
        
        setInterval(loadActiveTests, 5000);
        loadActiveTests();
    </script>
</body>
</html>
    ''')

@app.route('/start_mobile_test', methods=['POST'])
def start_mobile_test():
    """Start mobile app load test"""
    try:
        config = request.get_json()
        
        # Create scenario based on type
        app_info = {'api_base_url': config['api_base_url']}
        scenarios = mobile_tester.create_mobile_scenarios(app_info)
        
        scenario_map = {
            'complete_journey': scenarios[0],
            'social_features': scenarios[1] if len(scenarios) > 1 else scenarios[0]
        }
        
        config['scenario'] = scenario_map.get(config['scenario_type'], scenarios[0])
        
        test_id = mobile_tester.run_mobile_load_test(config)
        return jsonify({'success': True, 'test_id': test_id})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/mobile_tests')
def get_mobile_tests():
    """Get active mobile tests"""
    return jsonify(mobile_tester.active_tests)

if __name__ == '__main__':
    print("📱 Starting Mobile App Load Tester...")
    print("📖 Dashboard: http://localhost:5002")
    print("🎯 Test mobile game APIs and backends!")
    
    app.run(host='0.0.0.0', port=5002, debug=True)
