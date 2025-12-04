#!/usr/bin/env python3
"""
Video-Based Load Testing System
Automates load testing using video scenarios for realistic user behavior simulation
"""

from flask import Flask, request, jsonify, render_template_string
from flask_socketio import SocketIO, emit
import cv2
import numpy as np
import threading
import time
import json
import requests
import subprocess
import os
from datetime import datetime
from typing import Dict, List, Any
import queue
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'video_load_tester_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
test_sessions = {}
video_scenarios = {}
active_tests = {}

class VideoScenarioProcessor:
    def __init__(self):
        self.scenarios = {}
        
    def analyze_video_scenario(self, video_path: str, scenario_name: str) -> Dict[str, Any]:
        """Analyze video to extract user actions and timing"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise Exception(f"Cannot open video: {video_path}")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps
            
            # Extract key frames and actions
            actions = []
            frame_number = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                timestamp = frame_number / fps
                
                # Detect UI elements and actions (simplified)
                action = self._detect_action_in_frame(frame, timestamp)
                if action:
                    actions.append(action)
                
                frame_number += 1
                
                # Process every 30th frame for performance
                if frame_number % 30 != 0:
                    continue
            
            cap.release()
            
            scenario = {
                'name': scenario_name,
                'video_path': video_path,
                'duration': duration,
                'fps': fps,
                'frame_count': frame_count,
                'actions': actions,
                'created_at': datetime.now().isoformat()
            }
            
            self.scenarios[scenario_name] = scenario
            return scenario
            
        except Exception as e:
            raise Exception(f"Video analysis failed: {str(e)}")
    
    def _detect_action_in_frame(self, frame, timestamp) -> Dict[str, Any]:
        """Detect user actions in video frame"""
        # This is a simplified version - in production you'd use:
        # - OCR to detect text/buttons
        # - Template matching for UI elements
        # - Color detection for state changes
        # - Machine learning for action recognition
        
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect significant changes (clicks, navigation, etc.)
        # This is a placeholder - implement actual detection logic
        
        # Example: detect if frame has login elements
        if self._has_login_elements(gray):
            return {
                'type': 'login_screen',
                'timestamp': timestamp,
                'confidence': 0.8,
                'description': 'Login screen detected'
            }
        
        # Example: detect lobby/menu
        if self._has_lobby_elements(gray):
            return {
                'type': 'lobby_screen',
                'timestamp': timestamp,
                'confidence': 0.9,
                'description': 'Game lobby detected'
            }
        
        return None
    
    def _has_login_elements(self, gray_frame) -> bool:
        """Detect login screen elements"""
        # Placeholder - implement actual detection
        # Look for login buttons, input fields, etc.
        return False
    
    def _has_lobby_elements(self, gray_frame) -> bool:
        """Detect lobby/menu elements"""
        # Placeholder - implement actual detection
        # Look for game lobby UI elements
        return False

class LoadTestExecutor:
    def __init__(self):
        self.active_tests = {}
        self.results_queue = queue.Queue()
        
    def execute_load_test(self, test_config: Dict[str, Any]) -> str:
        """Execute load test based on video scenario"""
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
            
            # Get scenario details
            scenario = video_scenarios.get(scenario_name)
            if not scenario:
                raise Exception(f"Scenario '{scenario_name}' not found")
            
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
                socketio.emit('test_progress', {
                    'test_id': test_id,
                    'metrics': self.active_tests[test_id]['metrics']
                })
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
    
    def _simulate_user_session(self, test_id: str, user_id: int, scenario: Dict, config: Dict, start_delay: float):
        """Simulate a single user session based on video scenario"""
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
            
            # Execute actions from video scenario
            for action in scenario['actions']:
                action_result = self._execute_action(action, base_url, user_id)
                session_result['actions'].append(action_result)
                
                if not action_result['success']:
                    session_result['errors'].append(action_result['error'])
                
                # Wait based on video timing
                if len(session_result['actions']) > 1:
                    prev_action = scenario['actions'][len(session_result['actions']) - 2]
                    wait_time = action['timestamp'] - prev_action['timestamp']
                    time.sleep(max(0, wait_time))
            
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
        """Execute a specific action from the video scenario"""
        action_start = time.time()
        
        try:
            if action['type'] == 'login_screen':
                # Simulate login API call
                response = requests.post(f"{base_url}/api/login", json={
                    'username': f'test_user_{user_id}',
                    'password': 'test_password'
                }, timeout=10)
                
                return {
                    'type': action['type'],
                    'success': response.status_code == 200,
                    'response_time': time.time() - action_start,
                    'status_code': response.status_code,
                    'error': None if response.status_code == 200 else f"HTTP {response.status_code}"
                }
            
            elif action['type'] == 'lobby_screen':
                # Simulate lobby/matchmaking API call
                response = requests.get(f"{base_url}/api/lobby", timeout=10)
                
                return {
                    'type': action['type'],
                    'success': response.status_code == 200,
                    'response_time': time.time() - action_start,
                    'status_code': response.status_code,
                    'error': None if response.status_code == 200 else f"HTTP {response.status_code}"
                }
            
            else:
                # Generic action
                return {
                    'type': action['type'],
                    'success': True,
                    'response_time': time.time() - action_start,
                    'status_code': 200,
                    'error': None
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
        
        socketio.emit('test_completed', {
            'test_id': test_id,
            'metrics': test_session['metrics']
        })
    
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
video_processor = VideoScenarioProcessor()
load_executor = LoadTestExecutor()

@app.route('/')
def dashboard():
    """Main dashboard"""
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Video Load Tester</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        .button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer; }
        .button:hover { background: #0056b3; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .metric-card { padding: 15px; background: #f8f9fa; border-radius: 5px; text-align: center; }
        .status-running { color: #28a745; }
        .status-failed { color: #dc3545; }
        .status-completed { color: #6c757d; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 Video-Based Load Testing System</h1>
        
        <div class="section">
            <h2>📹 Upload Video Scenario</h2>
            <input type="file" id="videoFile" accept="video/*">
            <input type="text" id="scenarioName" placeholder="Scenario name (e.g., login-lobby-game)">
            <button class="button" onclick="uploadScenario()">Analyze Video</button>
        </div>
        
        <div class="section">
            <h2>🚀 Start Load Test</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                <select id="scenarioSelect">
                    <option value="">Select Scenario</option>
                </select>
                <input type="text" id="targetUrl" placeholder="Target URL (e.g., https://your-game.com)" value="http://localhost:3000">
                <input type="number" id="concurrentUsers" placeholder="Concurrent Users" value="10" min="1" max="1000">
                <input type="number" id="testDuration" placeholder="Duration (seconds)" value="300" min="60" max="3600">
                <input type="number" id="rampUpTime" placeholder="Ramp-up (seconds)" value="60" min="10" max="600">
            </div>
            <button class="button" onclick="startLoadTest()" style="margin-top: 10px;">Start Load Test</button>
        </div>
        
        <div class="section">
            <h2>📊 Active Tests</h2>
            <div id="activeTests"></div>
        </div>
        
        <div class="section">
            <h2>📈 Real-time Metrics</h2>
            <div id="metricsContainer" class="metrics"></div>
        </div>
        
        <div class="section">
            <h2>📋 Test History</h2>
            <div id="testHistory"></div>
        </div>
    </div>

    <script>
        const socket = io();
        
        // Socket event listeners
        socket.on('test_progress', function(data) {
            updateMetrics(data.test_id, data.metrics);
        });
        
        socket.on('test_completed', function(data) {
            updateTestStatus(data.test_id, 'completed');
            alert('Test completed! Check the reports folder for detailed results.');
        });
        
        function uploadScenario() {
            const fileInput = document.getElementById('videoFile');
            const scenarioName = document.getElementById('scenarioName').value;
            
            if (!fileInput.files[0] || !scenarioName) {
                alert('Please select a video file and enter a scenario name');
                return;
            }
            
            const formData = new FormData();
            formData.append('video', fileInput.files[0]);
            formData.append('scenario_name', scenarioName);
            
            fetch('/upload_scenario', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Video scenario analyzed successfully!');
                    loadScenarios();
                } else {
                    alert('Error: ' + data.error);
                }
            });
        }
        
        function startLoadTest() {
            const config = {
                scenario: document.getElementById('scenarioSelect').value,
                target_url: document.getElementById('targetUrl').value,
                concurrent_users: parseInt(document.getElementById('concurrentUsers').value),
                duration: parseInt(document.getElementById('testDuration').value),
                ramp_up_time: parseInt(document.getElementById('rampUpTime').value)
            };
            
            if (!config.scenario) {
                alert('Please select a scenario');
                return;
            }
            
            fetch('/start_test', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(config)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Load test started! Test ID: ' + data.test_id);
                    loadActiveTests();
                } else {
                    alert('Error: ' + data.error);
                }
            });
        }
        
        function loadScenarios() {
            fetch('/scenarios')
            .then(response => response.json())
            .then(data => {
                const select = document.getElementById('scenarioSelect');
                select.innerHTML = '<option value="">Select Scenario</option>';
                
                Object.keys(data).forEach(name => {
                    const option = document.createElement('option');
                    option.value = name;
                    option.textContent = name;
                    select.appendChild(option);
                });
            });
        }
        
        function loadActiveTests() {
            fetch('/active_tests')
            .then(response => response.json())
            .then(data => {
                const container = document.getElementById('activeTests');
                container.innerHTML = '';
                
                Object.values(data).forEach(test => {
                    const testDiv = document.createElement('div');
                    testDiv.innerHTML = `
                        <strong>Test ${test.id}</strong> - 
                        <span class="status-${test.status}">${test.status}</span> - 
                        Scenario: ${test.config.scenario} - 
                        Users: ${test.config.concurrent_users}
                    `;
                    container.appendChild(testDiv);
                });
            });
        }
        
        function updateMetrics(testId, metrics) {
            const container = document.getElementById('metricsContainer');
            container.innerHTML = `
                <div class="metric-card">
                    <h3>Total Users</h3>
                    <div style="font-size: 24px; font-weight: bold;">${metrics.total_users}</div>
                </div>
                <div class="metric-card">
                    <h3>Successful Sessions</h3>
                    <div style="font-size: 24px; font-weight: bold; color: #28a745;">${metrics.successful_sessions}</div>
                </div>
                <div class="metric-card">
                    <h3>Failed Sessions</h3>
                    <div style="font-size: 24px; font-weight: bold; color: #dc3545;">${metrics.failed_sessions}</div>
                </div>
                <div class="metric-card">
                    <h3>Avg Response Time</h3>
                    <div style="font-size: 24px; font-weight: bold;">${metrics.avg_response_time.toFixed(2)}s</div>
                </div>
            `;
        }
        
        // Load initial data
        loadScenarios();
        loadActiveTests();
        
        // Refresh active tests every 10 seconds
        setInterval(loadActiveTests, 10000);
    </script>
</body>
</html>
    ''')

@app.route('/upload_scenario', methods=['POST'])
def upload_scenario():
    """Upload and analyze video scenario"""
    try:
        if 'video' not in request.files:
            return jsonify({'success': False, 'error': 'No video file provided'})
        
        video_file = request.files['video']
        scenario_name = request.form.get('scenario_name')
        
        if not scenario_name:
            return jsonify({'success': False, 'error': 'Scenario name required'})
        
        # Save uploaded video
        os.makedirs('videos', exist_ok=True)
        video_path = f'videos/{scenario_name}_{int(time.time())}.mp4'
        video_file.save(video_path)
        
        # Analyze video scenario
        scenario = video_processor.analyze_video_scenario(video_path, scenario_name)
        video_scenarios[scenario_name] = scenario
        
        return jsonify({'success': True, 'scenario': scenario})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/start_test', methods=['POST'])
def start_test():
    """Start load test"""
    try:
        config = request.get_json()
        test_id = load_executor.execute_load_test(config)
        
        return jsonify({'success': True, 'test_id': test_id})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/scenarios')
def get_scenarios():
    """Get available scenarios"""
    return jsonify(video_scenarios)

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
    print("🎮 Starting Video-Based Load Testing System...")
    print("📖 Dashboard available at: http://localhost:5000")
    print("🎯 Upload game videos to create realistic load test scenarios")
    
    # Create required directories
    os.makedirs('videos', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
