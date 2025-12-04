#!/usr/bin/env python3
"""
Simple Video-Based Load Testing System
Simplified version without complex video processing dependencies
"""

from flask import Flask, request, jsonify, render_template_string
import threading
import time
import json
import requests
import os
from datetime import datetime
from typing import Dict, List, Any
import queue
import logging

app = Flask(__name__)

# Global state
test_sessions = {}
video_scenarios = {}
active_tests = {}

class SimpleLoadExecutor:
    def __init__(self):
        self.active_tests = {}
        self.results_queue = queue.Queue()
        
    def execute_load_test(self, test_config: Dict[str, Any]) -> str:
        """Execute load test based on scenario"""
        test_id = f"test_{int(time.time())}"
        
        test_session = {
            'id': test_id,
            'config': test_config,
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'results': [],
            'metrics': {
                'total_users': 0,
                'successful_sessions': 0,
                'failed_sessions': 0,
                'avg_response_time': 0,
                'errors': []
            }
        }
        
        self.active_tests[test_id] = test_session
        
        # Start test in background thread
        thread = threading.Thread(
            target=self._run_test_scenario,
            args=(test_id, test_config)
        )
        thread.daemon = True
        thread.start()
        
        return test_id
    
    def _run_test_scenario(self, test_id: str, config: Dict[str, Any]):
        """Run the actual load test scenario"""
        try:
            scenario_name = config['scenario']
            concurrent_users = config.get('concurrent_users', 10)
            duration = config.get('duration', 300)  # 5 minutes default
            ramp_up_time = config.get('ramp_up_time', 60)  # 1 minute ramp up
            
            # Get scenario details (simplified)
            scenario = self._get_default_scenario(scenario_name)
            
            # Create user simulation threads
            user_threads = []
            
            for user_id in range(concurrent_users):
                # Stagger user start times for realistic ramp-up
                start_delay = (ramp_up_time / concurrent_users) * user_id
                
                thread = threading.Thread(
                    target=self._simulate_user_session,
                    args=(test_id, user_id, scenario, config, start_delay)
                )
                thread.daemon = True
                user_threads.append(thread)
                thread.start()
            
            # Monitor test progress
            start_time = time.time()
            while time.time() - start_time < duration:
                self._update_test_metrics(test_id)
                time.sleep(5)  # Update every 5 seconds
            
            # Wait for all threads to complete
            for thread in user_threads:
                thread.join(timeout=30)
            
            # Finalize test results
            self._finalize_test(test_id)
            
        except Exception as e:
            self.active_tests[test_id]['status'] = 'failed'
            self.active_tests[test_id]['error'] = str(e)
            logging.error(f"Test {test_id} failed: {e}")
    
    def _get_default_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """Get default scenario if video analysis isn't available"""
        scenarios = {
            'login_lobby_game': {
                'name': 'Login → Lobby → Game',
                'actions': [
                    {'type': 'login', 'endpoint': '/api/login', 'delay': 2.0},
                    {'type': 'lobby', 'endpoint': '/api/lobby', 'delay': 1.5},
                    {'type': 'join_game', 'endpoint': '/api/join_game', 'delay': 3.0},
                    {'type': 'game_status', 'endpoint': '/api/game_status', 'delay': 0.5},
                    {'type': 'logout', 'endpoint': '/api/logout', 'delay': 1.0}
                ]
            },
            'quick_match': {
                'name': 'Quick Match Flow',
                'actions': [
                    {'type': 'login', 'endpoint': '/api/login', 'delay': 1.5},
                    {'type': 'join_game', 'endpoint': '/api/join_game', 'delay': 2.0},
                    {'type': 'game_status', 'endpoint': '/api/game_status', 'delay': 0.5}
                ]
            },
            'lobby_browse': {
                'name': 'Lobby Browsing',
                'actions': [
                    {'type': 'login', 'endpoint': '/api/login', 'delay': 2.0},
                    {'type': 'lobby', 'endpoint': '/api/lobby', 'delay': 1.0},
                    {'type': 'lobby', 'endpoint': '/api/lobby', 'delay': 1.0},
                    {'type': 'server_stats', 'endpoint': '/api/server_stats', 'delay': 0.5}
                ]
            }
        }
        
        return scenarios.get(scenario_name, scenarios['login_lobby_game'])
    
    def _simulate_user_session(self, test_id: str, user_id: int, scenario: Dict, config: Dict, start_delay: float):
        """Simulate a single user session"""
        time.sleep(start_delay)
        
        session_start = time.time()
        session_result = {
            'user_id': user_id,
            'start_time': datetime.now().isoformat(),
            'actions': [],
            'success': False,
            'total_time': 0,
            'errors': []
        }
        
        try:
            base_url = config.get('target_url', 'http://localhost:3000')
            
            # Execute actions from scenario
            for action in scenario['actions']:
                action_result = self._execute_action(action, base_url, user_id)
                session_result['actions'].append(action_result)
                
                if not action_result['success']:
                    session_result['errors'].append(action_result['error'])
                
                # Wait based on scenario timing
                time.sleep(action.get('delay', 1.0))
            
            session_result['success'] = len(session_result['errors']) == 0
            session_result['total_time'] = time.time() - session_start
            
        except Exception as e:
            session_result['errors'].append(str(e))
            session_result['success'] = False
            session_result['total_time'] = time.time() - session_start
        
        # Store results
        self.active_tests[test_id]['results'].append(session_result)
        self.results_queue.put((test_id, session_result))
    
    def _execute_action(self, action: Dict, base_url: str, user_id: int) -> Dict[str, Any]:
        """Execute a specific action"""
        action_start = time.time()
        
        try:
            endpoint = action['endpoint']
            
            if action['type'] == 'login':
                response = requests.post(f"{base_url}{endpoint}", json={
                    'username': f'test_user_{user_id}',
                    'password': 'test_password'
                }, timeout=10)
            else:
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            return {
                'type': action['type'],
                'success': response.status_code == 200,
                'response_time': time.time() - action_start,
                'status_code': response.status_code,
                'error': None if response.status_code == 200 else f"HTTP {response.status_code}"
            }
                
        except Exception as e:
            return {
                'type': action['type'],
                'success': False,
                'response_time': time.time() - action_start,
                'status_code': 0,
                'error': str(e)
            }
    
    def _update_test_metrics(self, test_id: str):
        """Update test metrics in real-time"""
        test_session = self.active_tests[test_id]
        results = test_session['results']
        
        if not results:
            return
        
        total_users = len(results)
        successful_sessions = sum(1 for r in results if r['success'])
        failed_sessions = total_users - successful_sessions
        
        response_times = [r['total_time'] for r in results if r['total_time'] > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        all_errors = []
        for r in results:
            all_errors.extend(r['errors'])
        
        test_session['metrics'].update({
            'total_users': total_users,
            'successful_sessions': successful_sessions,
            'failed_sessions': failed_sessions,
            'avg_response_time': avg_response_time,
            'errors': all_errors[-10:]  # Keep last 10 errors
        })
    
    def _finalize_test(self, test_id: str):
        """Finalize test and generate report"""
        test_session = self.active_tests[test_id]
        test_session['status'] = 'completed'
        test_session['end_time'] = datetime.now().isoformat()
        
        # Generate detailed report
        self._generate_test_report(test_id)
    
    def _generate_test_report(self, test_id: str):
        """Generate comprehensive test report"""
        test_session = self.active_tests[test_id]
        
        # Create detailed report
        report = {
            'test_id': test_id,
            'summary': test_session['metrics'],
            'configuration': test_session['config'],
            'timeline': test_session['results'],
            'generated_at': datetime.now().isoformat()
        }
        
        # Save report to file
        os.makedirs('reports', exist_ok=True)
        with open(f'reports/test_report_{test_id}.json', 'w') as f:
            json.dump(report, f, indent=2)

# Initialize components
load_executor = SimpleLoadExecutor()

@app.route('/')
def dashboard():
    """Main dashboard"""
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Video Load Tester</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .section { margin: 20px 0; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .button { padding: 12px 24px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; }
        .button:hover { background: #0056b3; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .metric-card { padding: 20px; background: #f8f9fa; border-radius: 8px; text-align: center; border-left: 4px solid #007bff; }
        .metric-value { font-size: 28px; font-weight: bold; color: #333; }
        .metric-label { color: #666; margin-top: 5px; }
        .status-running { color: #28a745; }
        .status-failed { color: #dc3545; }
        .status-completed { color: #6c757d; }
        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 15px 0; }
        .form-grid input, .form-grid select { padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        h1 { color: #333; text-align: center; }
        h2 { color: #555; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 Video-Based Load Testing System</h1>
        
        <div class="section">
            <h2>🚀 Start Load Test</h2>
            <div class="form-grid">
                <select id="scenarioSelect">
                    <option value="login_lobby_game">Login → Lobby → Game</option>
                    <option value="quick_match">Quick Match Flow</option>
                    <option value="lobby_browse">Lobby Browsing</option>
                </select>
                <input type="text" id="targetUrl" placeholder="Target URL" value="http://localhost:3000">
                <input type="number" id="concurrentUsers" placeholder="Concurrent Users" value="10" min="1" max="1000">
                <input type="number" id="testDuration" placeholder="Duration (seconds)" value="300" min="60" max="3600">
                <input type="number" id="rampUpTime" placeholder="Ramp-up (seconds)" value="60" min="10" max="600">
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
                    <div class="metric-label">Total Users</div>
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
        
        <div class="section">
            <h2>📋 Test History</h2>
            <div id="testHistory">No completed tests</div>
        </div>
    </div>

    <script>
        function startLoadTest() {
            const config = {
                scenario: document.getElementById('scenarioSelect').value,
                target_url: document.getElementById('targetUrl').value,
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
                    alert('❌ Error: ' + data.error);
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
                    testDiv.style.cssText = 'padding: 15px; margin: 10px 0; background: #f8f9fa; border-radius: 5px; border-left: 4px solid #007bff;';
                    testDiv.innerHTML = `
                        <strong>Test ${test.id}</strong> - 
                        <span class="status-${test.status}">${test.status.toUpperCase()}</span><br>
                        <small>Scenario: ${test.config.scenario} | Users: ${test.config.concurrent_users} | Started: ${new Date(test.start_time).toLocaleTimeString()}</small>
                    `;
                    container.appendChild(testDiv);
                });
            });
        }
        
        function updateMetrics() {
            fetch('/active_tests')
            .then(response => response.json())
            .then(data => {
                let totalUsers = 0, successful = 0, failed = 0, avgTime = 0;
                
                Object.values(data).forEach(test => {
                    if (test.metrics) {
                        totalUsers += test.metrics.total_users || 0;
                        successful += test.metrics.successful_sessions || 0;
                        failed += test.metrics.failed_sessions || 0;
                        avgTime = Math.max(avgTime, test.metrics.avg_response_time || 0);
                    }
                });
                
                document.querySelector('.metrics .metric-card:nth-child(1) .metric-value').textContent = totalUsers;
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

@app.route('/start_test', methods=['POST'])
def start_test():
    """Start load test"""
    try:
        config = request.get_json()
        test_id = load_executor.execute_load_test(config)
        
        return jsonify({'success': True, 'test_id': test_id})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/active_tests')
def get_active_tests():
    """Get active tests"""
    return jsonify(load_executor.active_tests)

@app.route('/test_results/<test_id>')
def get_test_results(test_id):
    """Get test results"""
    if test_id in load_executor.active_tests:
        return jsonify(load_executor.active_tests[test_id])
    else:
        return jsonify({'error': 'Test not found'}), 404

if __name__ == '__main__':
    print("🎮 Starting Simple Video-Based Load Testing System...")
    print("📖 Dashboard available at: http://localhost:5000")
    print("🎯 Ready to test your game APIs with realistic scenarios!")
    
    # Create required directories
    os.makedirs('reports', exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
