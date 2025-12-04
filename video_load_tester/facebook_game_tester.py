#!/usr/bin/env python3
"""
Facebook Game Load Tester - Web Interface
Easy way to test Facebook games and websites
"""

from flask import Flask, request, jsonify, render_template_string
import requests
import json
import time
import threading
from datetime import datetime
from typing import Dict, Any, List
import os
import urllib.parse

app = Flask(__name__)

class FacebookGameLoadTester:
    def __init__(self):
        self.active_tests = {}
        self.scenarios = {}
    
    def analyze_website(self, url: str) -> Dict[str, Any]:
        """Analyze any website/game to create load test scenarios"""
        print(f"🔍 Analyzing website: {url}")
        
        try:
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            
            response = session.get(url, timeout=10)
            
            if response.status_code != 200:
                raise Exception(f"Cannot access URL: {response.status_code}")
            
            # Extract basic info
            parsed_url = urllib.parse.urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # Detect if it's a Facebook game
            is_facebook_game = 'facebook.com' in url or 'apps.facebook.com' in url
            
            # Create scenarios based on site type
            if is_facebook_game:
                scenarios = self._create_facebook_scenarios(base_url, response.text)
            else:
                scenarios = self._create_generic_scenarios(base_url, response.text)
            
            return {
                'url': url,
                'base_url': base_url,
                'is_facebook_game': is_facebook_game,
                'scenarios': scenarios,
                'analysis_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error analyzing website: {e}")
            return self._create_fallback_scenarios(url)
    
    def _create_facebook_scenarios(self, base_url: str, html_content: str) -> List[Dict[str, Any]]:
        """Create Facebook game specific scenarios"""
        scenarios = []
        
        # Facebook Game Scenario 1: Login and Play
        scenarios.append({
            'name': 'Facebook Game - Login and Play',
            'description': 'Simulate user logging in and playing the game',
            'actions': [
                {
                    'name': 'Load Game Page',
                    'method': 'GET',
                    'endpoint': '/',
                    'delay': 2.0,
                    'expected_status': 200
                },
                {
                    'name': 'Facebook Login',
                    'method': 'POST',
                    'endpoint': '/login',
                    'delay': 3.0,
                    'payload': {'fb_auth': True},
                    'expected_status': 200
                },
                {
                    'name': 'Load Game Data',
                    'method': 'GET',
                    'endpoint': '/api/gamedata',
                    'delay': 1.5,
                    'expected_status': 200
                },
                {
                    'name': 'Start Game Session',
                    'method': 'POST',
                    'endpoint': '/api/game/start',
                    'delay': 1.0,
                    'expected_status': 200
                },
                {
                    'name': 'Game Action 1',
                    'method': 'POST',
                    'endpoint': '/api/game/action',
                    'delay': 0.5,
                    'payload': {'action': 'move'},
                    'expected_status': 200
                },
                {
                    'name': 'Game Action 2',
                    'method': 'POST',
                    'endpoint': '/api/game/action',
                    'delay': 0.7,
                    'payload': {'action': 'click'},
                    'expected_status': 200
                },
                {
                    'name': 'Check Leaderboard',
                    'method': 'GET',
                    'endpoint': '/api/leaderboard',
                    'delay': 1.0,
                    'expected_status': 200
                }
            ]
        })
        
        # Facebook Game Scenario 2: Social Features
        scenarios.append({
            'name': 'Facebook Game - Social Features',
            'description': 'Test social features like friends, sharing, etc.',
            'actions': [
                {
                    'name': 'Load Game',
                    'method': 'GET',
                    'endpoint': '/',
                    'delay': 2.0,
                    'expected_status': 200
                },
                {
                    'name': 'Get Friends List',
                    'method': 'GET',
                    'endpoint': '/api/friends',
                    'delay': 1.5,
                    'expected_status': 200
                },
                {
                    'name': 'Send Gift',
                    'method': 'POST',
                    'endpoint': '/api/gift/send',
                    'delay': 1.0,
                    'payload': {'friend_id': 'test_friend'},
                    'expected_status': 200
                },
                {
                    'name': 'Share Achievement',
                    'method': 'POST',
                    'endpoint': '/api/share',
                    'delay': 1.2,
                    'payload': {'type': 'achievement'},
                    'expected_status': 200
                }
            ]
        })
        
        return scenarios
    
    def _create_generic_scenarios(self, base_url: str, html_content: str) -> List[Dict[str, Any]]:
        """Create generic website scenarios"""
        scenarios = []
        
        # Generic Scenario 1: Basic User Flow
        scenarios.append({
            'name': 'Website - Basic User Flow',
            'description': 'Simulate typical user browsing behavior',
            'actions': [
                {
                    'name': 'Load Homepage',
                    'method': 'GET',
                    'endpoint': '/',
                    'delay': 2.0,
                    'expected_status': 200
                },
                {
                    'name': 'Login/Register',
                    'method': 'POST',
                    'endpoint': '/login',
                    'delay': 2.5,
                    'payload': {'username': 'test_user', 'password': 'test_pass'},
                    'expected_status': [200, 302]
                },
                {
                    'name': 'Browse Content',
                    'method': 'GET',
                    'endpoint': '/browse',
                    'delay': 1.5,
                    'expected_status': 200
                },
                {
                    'name': 'User Action',
                    'method': 'POST',
                    'endpoint': '/api/action',
                    'delay': 1.0,
                    'payload': {'action': 'click'},
                    'expected_status': 200
                }
            ]
        })
        
        # Generic Scenario 2: API Heavy
        scenarios.append({
            'name': 'Website - API Heavy Usage',
            'description': 'Test API endpoints with frequent calls',
            'actions': [
                {
                    'name': 'API Call 1',
                    'method': 'GET',
                    'endpoint': '/api/data',
                    'delay': 0.5,
                    'expected_status': 200
                },
                {
                    'name': 'API Call 2',
                    'method': 'GET',
                    'endpoint': '/api/status',
                    'delay': 0.3,
                    'expected_status': 200
                },
                {
                    'name': 'API Call 3',
                    'method': 'POST',
                    'endpoint': '/api/update',
                    'delay': 0.8,
                    'payload': {'data': 'test'},
                    'expected_status': 200
                }
            ]
        })
        
        return scenarios
    
    def _create_fallback_scenarios(self, url: str) -> Dict[str, Any]:
        """Create fallback scenarios when analysis fails"""
        parsed_url = urllib.parse.urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        return {
            'url': url,
            'base_url': base_url,
            'is_facebook_game': False,
            'scenarios': [
                {
                    'name': 'Basic Load Test',
                    'description': 'Simple load test for the website',
                    'actions': [
                        {
                            'name': 'Load Page',
                            'method': 'GET',
                            'endpoint': '/',
                            'delay': 1.0,
                            'expected_status': 200
                        }
                    ]
                }
            ],
            'analysis_time': datetime.now().isoformat(),
            'error': 'Analysis failed, using fallback scenario'
        }
    
    def run_load_test(self, config: Dict[str, Any]) -> str:
        """Run load test with the specified configuration"""
        test_id = f"test_{int(time.time())}"
        
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
                'errors': []
            }
        }
        
        self.active_tests[test_id] = test_session
        
        # Start test in background
        thread = threading.Thread(target=self._execute_load_test, args=(test_id, config))
        thread.daemon = True
        thread.start()
        
        return test_id
    
    def _execute_load_test(self, test_id: str, config: Dict[str, Any]):
        """Execute the actual load test"""
        try:
            base_url = config['base_url']
            scenario = config['scenario']
            concurrent_users = config.get('concurrent_users', 10)
            duration = config.get('duration', 300)
            ramp_up_time = config.get('ramp_up_time', 60)
            
            # Create user threads
            user_threads = []
            
            for user_id in range(concurrent_users):
                start_delay = (ramp_up_time / concurrent_users) * user_id
                
                thread = threading.Thread(
                    target=self._simulate_user,
                    args=(test_id, user_id, base_url, scenario, start_delay, duration)
                )
                thread.daemon = True
                user_threads.append(thread)
                thread.start()
            
            # Monitor test
            start_time = time.time()
            while time.time() - start_time < duration:
                self._update_metrics(test_id)
                time.sleep(5)
            
            # Wait for completion
            for thread in user_threads:
                thread.join(timeout=30)
            
            # Finalize
            self.active_tests[test_id]['status'] = 'completed'
            self.active_tests[test_id]['end_time'] = datetime.now().isoformat()
            
        except Exception as e:
            self.active_tests[test_id]['status'] = 'failed'
            self.active_tests[test_id]['error'] = str(e)
    
    def _simulate_user(self, test_id: str, user_id: int, base_url: str, scenario: Dict, start_delay: float, duration: float):
        """Simulate a single user session"""
        time.sleep(start_delay)
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': f'LoadTester-User-{user_id}'
        })
        
        user_results = []
        session_start = time.time()
        
        # Run scenario actions repeatedly until duration expires
        while time.time() - session_start < duration:
            for action in scenario['actions']:
                if time.time() - session_start >= duration:
                    break
                
                result = self._execute_action(session, base_url, action, user_id)
                user_results.append(result)
                
                # Wait between actions
                time.sleep(action.get('delay', 1.0))
        
        # Store user results
        self.active_tests[test_id]['results'].extend(user_results)
    
    def _execute_action(self, session: requests.Session, base_url: str, action: Dict, user_id: int) -> Dict[str, Any]:
        """Execute a single action"""
        start_time = time.time()
        
        try:
            url = f"{base_url.rstrip('/')}{action['endpoint']}"
            method = action.get('method', 'GET').upper()
            payload = action.get('payload', {})
            
            # Add user-specific data to payload
            if payload and isinstance(payload, dict):
                payload['user_id'] = f'test_user_{user_id}'
            
            if method == 'POST':
                response = session.post(url, json=payload, timeout=10)
            else:
                response = session.get(url, timeout=10)
            
            response_time = time.time() - start_time
            expected_status = action.get('expected_status', 200)
            
            # Check if status is expected
            if isinstance(expected_status, list):
                success = response.status_code in expected_status
            else:
                success = response.status_code == expected_status
            
            return {
                'action': action['name'],
                'method': method,
                'url': url,
                'status_code': response.status_code,
                'response_time': response_time,
                'success': success,
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id
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
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id
            }
    
    def _update_metrics(self, test_id: str):
        """Update test metrics"""
        test_session = self.active_tests[test_id]
        results = test_session['results']
        
        if not results:
            return
        
        total_requests = len(results)
        successful_requests = sum(1 for r in results if r['success'])
        failed_requests = total_requests - successful_requests
        
        response_times = [r['response_time'] for r in results if r['response_time'] > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        errors = [r.get('error', 'Unknown error') for r in results if not r['success']]
        
        test_session['metrics'].update({
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'avg_response_time': avg_response_time,
            'errors': errors[-10:]  # Keep last 10 errors
        })

# Initialize the tester
facebook_tester = FacebookGameLoadTester()

@app.route('/')
def dashboard():
    """Facebook Game Testing Dashboard"""
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Game Load Tester</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f0f2f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .section { margin: 20px 0; padding: 25px; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .button { padding: 12px 24px; background: #1877f2; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 600; }
        .button:hover { background: #166fe5; }
        .button:disabled { background: #ccc; cursor: not-allowed; }
        .form-group { margin: 15px 0; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: 600; color: #333; }
        .form-group input, .form-group select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
        .metric-card { padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; text-align: center; }
        .metric-value { font-size: 32px; font-weight: bold; }
        .metric-label { margin-top: 8px; opacity: 0.9; }
        .scenario-card { padding: 15px; margin: 10px 0; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #1877f2; }
        .status-running { color: #28a745; font-weight: bold; }
        .status-completed { color: #6c757d; font-weight: bold; }
        .status-failed { color: #dc3545; font-weight: bold; }
        h1 { color: #1877f2; text-align: center; margin-bottom: 10px; }
        h2 { color: #333; border-bottom: 3px solid #1877f2; padding-bottom: 10px; }
        .facebook-header { text-align: center; color: #666; margin-bottom: 30px; }
        .loading { display: none; text-align: center; padding: 20px; }
        .loading.show { display: block; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 Facebook Game Load Tester</h1>
        <div class="facebook-header">
            <p>Test any Facebook game or website with realistic user behavior simulation</p>
        </div>
        
        <div class="section">
            <h2>🔗 Analyze Website/Game</h2>
            <div class="form-group">
                <label>Facebook Game URL or Any Website URL:</label>
                <input type="url" id="gameUrl" placeholder="https://www.facebook.com/games/your-game or any website URL" style="margin-bottom: 10px;">
                <small style="color: #666;">Examples: Facebook games, web games, any website you want to load test</small>
            </div>
            <button class="button" onclick="analyzeWebsite()">🔍 Analyze Website</button>
            
            <div id="loading" class="loading">
                <p>🔄 Analyzing website... This may take a few seconds.</p>
            </div>
        </div>
        
        <div class="section" id="scenarioSection" style="display: none;">
            <h2>📋 Available Scenarios</h2>
            <div id="scenarios"></div>
        </div>
        
        <div class="section" id="testSection" style="display: none;">
            <h2>🚀 Configure Load Test</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                <div class="form-group">
                    <label>Selected Scenario:</label>
                    <select id="selectedScenario"></select>
                </div>
                <div class="form-group">
                    <label>Concurrent Users:</label>
                    <input type="number" id="concurrentUsers" value="10" min="1" max="500">
                </div>
                <div class="form-group">
                    <label>Test Duration (seconds):</label>
                    <input type="number" id="testDuration" value="300" min="60" max="3600">
                </div>
                <div class="form-group">
                    <label>Ramp-up Time (seconds):</label>
                    <input type="number" id="rampUpTime" value="60" min="10" max="600">
                </div>
            </div>
            <button class="button" onclick="startLoadTest()">🚀 Start Load Test</button>
        </div>
        
        <div class="section">
            <h2>📊 Active Tests</h2>
            <div id="activeTests">No active tests</div>
        </div>
        
        <div class="section">
            <h2>📈 Real-time Metrics</h2>
            <div id="metricsContainer" class="metrics">
                <div class="metric-card">
                    <div class="metric-value">0</div>
                    <div class="metric-label">Total Requests</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">0</div>
                    <div class="metric-label">Successful</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">0</div>
                    <div class="metric-label">Failed</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">0.0s</div>
                    <div class="metric-label">Avg Response</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentAnalysis = null;
        
        function analyzeWebsite() {
            const url = document.getElementById('gameUrl').value.trim();
            if (!url) {
                alert('Please enter a website URL');
                return;
            }
            
            document.getElementById('loading').classList.add('show');
            document.getElementById('scenarioSection').style.display = 'none';
            document.getElementById('testSection').style.display = 'none';
            
            fetch('/analyze', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({url: url})
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('loading').classList.remove('show');
                
                if (data.success) {
                    currentAnalysis = data.analysis;
                    displayScenarios(data.analysis);
                } else {
                    alert('Error analyzing website: ' + data.error);
                }
            })
            .catch(error => {
                document.getElementById('loading').classList.remove('show');
                alert('Error: ' + error);
            });
        }
        
        function displayScenarios(analysis) {
            const container = document.getElementById('scenarios');
            const scenarioSelect = document.getElementById('selectedScenario');
            
            container.innerHTML = '';
            scenarioSelect.innerHTML = '';
            
            analysis.scenarios.forEach((scenario, index) => {
                // Display scenario card
                const card = document.createElement('div');
                card.className = 'scenario-card';
                card.innerHTML = `
                    <h4>${scenario.name}</h4>
                    <p>${scenario.description}</p>
                    <small>Actions: ${scenario.actions.length} | Base URL: ${analysis.base_url}</small>
                `;
                container.appendChild(card);
                
                // Add to select
                const option = document.createElement('option');
                option.value = index;
                option.textContent = scenario.name;
                scenarioSelect.appendChild(option);
            });
            
            document.getElementById('scenarioSection').style.display = 'block';
            document.getElementById('testSection').style.display = 'block';
        }
        
        function startLoadTest() {
            if (!currentAnalysis) {
                alert('Please analyze a website first');
                return;
            }
            
            const scenarioIndex = parseInt(document.getElementById('selectedScenario').value);
            const scenario = currentAnalysis.scenarios[scenarioIndex];
            
            const config = {
                base_url: currentAnalysis.base_url,
                scenario: scenario,
                concurrent_users: parseInt(document.getElementById('concurrentUsers').value),
                duration: parseInt(document.getElementById('testDuration').value),
                ramp_up_time: parseInt(document.getElementById('rampUpTime').value)
            };
            
            fetch('/start_test', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(config)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('🚀 Load test started! Test ID: ' + data.test_id);
                    loadActiveTests();
                } else {
                    alert('Error starting test: ' + data.error);
                }
            });
        }
        
        function loadActiveTests() {
            fetch('/active_tests')
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
                    testDiv.style.cssText = 'padding: 15px; margin: 10px 0; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #1877f2;';
                    testDiv.innerHTML = `
                        <strong>Test ${test.id}</strong> - 
                        <span class="status-${test.status}">${test.status.toUpperCase()}</span><br>
                        <small>Users: ${test.config.concurrent_users} | Started: ${new Date(test.start_time).toLocaleTimeString()}</small>
                    `;
                    container.appendChild(testDiv);
                });
            });
        }
        
        function updateMetrics() {
            fetch('/active_tests')
            .then(response => response.json())
            .then(data => {
                let totalRequests = 0, successful = 0, failed = 0, avgTime = 0;
                
                Object.values(data).forEach(test => {
                    if (test.metrics) {
                        totalRequests += test.metrics.total_requests || 0;
                        successful += test.metrics.successful_requests || 0;
                        failed += test.metrics.failed_requests || 0;
                        avgTime = Math.max(avgTime, test.metrics.avg_response_time || 0);
                    }
                });
                
                document.querySelector('.metrics .metric-card:nth-child(1) .metric-value').textContent = totalRequests;
                document.querySelector('.metrics .metric-card:nth-child(2) .metric-value').textContent = successful;
                document.querySelector('.metrics .metric-card:nth-child(3) .metric-value').textContent = failed;
                document.querySelector('.metrics .metric-card:nth-child(4) .metric-value').textContent = avgTime.toFixed(1) + 's';
            });
        }
        
        // Auto-refresh every 5 seconds
        setInterval(() => {
            loadActiveTests();
            updateMetrics();
        }, 5000);
        
        // Initial load
        loadActiveTests();
    </script>
</body>
</html>
    ''')

@app.route('/analyze', methods=['POST'])
def analyze_website():
    """Analyze website/game"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'success': False, 'error': 'URL is required'})
        
        analysis = facebook_tester.analyze_website(url)
        return jsonify({'success': True, 'analysis': analysis})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/start_test', methods=['POST'])
def start_test():
    """Start load test"""
    try:
        config = request.get_json()
        test_id = facebook_tester.run_load_test(config)
        
        return jsonify({'success': True, 'test_id': test_id})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/active_tests')
def get_active_tests():
    """Get active tests"""
    return jsonify(facebook_tester.active_tests)

if __name__ == '__main__':
    print("🎮 Starting Facebook Game Load Tester...")
    print("📖 Dashboard available at: http://localhost:5001")
    print("🎯 Test any Facebook game or website!")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
