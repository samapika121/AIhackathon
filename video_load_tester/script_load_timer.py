#!/usr/bin/env python3
"""
Script Load Timer - Run your scripts and capture load times
Simple alternative to BrowserStack for immediate testing
"""

import time
import subprocess
import threading
import json
import requests
from datetime import datetime
from typing import Dict, List, Any
from flask import Flask, request, jsonify, render_template_string
import psutil
import os

app = Flask(__name__)

class ScriptLoadTimer:
    def __init__(self):
        self.active_tests = {}
        self.script_results = {}
    
    def run_script_load_test(self, config: Dict[str, Any]) -> str:
        """Run load test with custom scripts"""
        test_id = f"script_test_{int(time.time())}"
        
        test_session = {
            'id': test_id,
            'config': config,
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'results': [],
            'metrics': {
                'total_runs': 0,
                'successful_runs': 0,
                'failed_runs': 0,
                'avg_execution_time': 0,
                'min_execution_time': float('inf'),
                'max_execution_time': 0,
                'script_outputs': []
            }
        }
        
        self.active_tests[test_id] = test_session
        
        # Start test in background
        thread = threading.Thread(target=self._execute_script_test, args=(test_id, config))
        thread.daemon = True
        thread.start()
        
        return test_id
    
    def _execute_script_test(self, test_id: str, config: Dict[str, Any]):
        """Execute script load test"""
        try:
            script_path = config['script_path']
            concurrent_instances = config.get('concurrent_instances', 5)
            test_duration = config.get('test_duration', 300)
            script_args = config.get('script_args', [])
            
            # Create concurrent script execution threads
            script_threads = []
            
            for i in range(concurrent_instances):
                thread = threading.Thread(
                    target=self._run_script_instance,
                    args=(test_id, i, script_path, script_args, test_duration)
                )
                thread.daemon = True
                script_threads.append(thread)
                thread.start()
            
            # Wait for all scripts to complete
            for thread in script_threads:
                thread.join()
            
            # Calculate final metrics
            self._calculate_script_metrics(test_id)
            self.active_tests[test_id]['status'] = 'completed'
            
        except Exception as e:
            self.active_tests[test_id]['status'] = 'failed'
            self.active_tests[test_id]['error'] = str(e)
    
    def _run_script_instance(self, test_id: str, instance_id: int, script_path: str, script_args: List[str], duration: int):
        """Run a single script instance"""
        start_time = time.time()
        run_count = 0
        
        while time.time() - start_time < duration:
            run_count += 1
            
            # Execute script and measure time
            result = self._execute_single_script(script_path, script_args, instance_id, run_count)
            
            # Store result
            self.active_tests[test_id]['results'].append(result)
            
            # Wait between runs
            time.sleep(1)
            
            # Limit runs to prevent overwhelming
            if run_count >= 20:
                break
    
    def _execute_single_script(self, script_path: str, script_args: List[str], instance_id: int, run_number: int) -> Dict[str, Any]:
        """Execute a single script run and capture metrics"""
        try:
            print(f"🚀 Instance {instance_id}, Run {run_number}: Executing {script_path}")
            
            # Prepare command
            cmd = ['python3', script_path] + script_args
            
            # Start timing
            start_time = time.time()
            
            # Get initial system metrics
            initial_cpu = psutil.cpu_percent()
            initial_memory = psutil.virtual_memory().percent
            
            # Execute script
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Get final system metrics
            final_cpu = psutil.cpu_percent()
            final_memory = psutil.virtual_memory().percent
            
            # Determine success
            success = process.returncode == 0
            
            result = {
                'instance_id': instance_id,
                'run_number': run_number,
                'script_path': script_path,
                'execution_time': execution_time,
                'success': success,
                'return_code': process.returncode,
                'stdout': process.stdout[:500] if process.stdout else '',  # First 500 chars
                'stderr': process.stderr[:500] if process.stderr else '',  # First 500 chars
                'system_metrics': {
                    'cpu_before': initial_cpu,
                    'cpu_after': final_cpu,
                    'memory_before': initial_memory,
                    'memory_after': final_memory
                },
                'timestamp': datetime.now().isoformat()
            }
            
            status = "✅" if success else "❌"
            print(f"  {status} Execution time: {execution_time:.2f}s, Return code: {process.returncode}")
            
            return result
            
        except subprocess.TimeoutExpired:
            return {
                'instance_id': instance_id,
                'run_number': run_number,
                'script_path': script_path,
                'execution_time': 30.0,
                'success': False,
                'error': 'Script timeout (30s)',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'instance_id': instance_id,
                'run_number': run_number,
                'script_path': script_path,
                'execution_time': 0,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _calculate_script_metrics(self, test_id: str):
        """Calculate final script test metrics"""
        results = self.active_tests[test_id]['results']
        
        total_runs = len(results)
        successful_runs = sum(1 for r in results if r.get('success', False))
        failed_runs = total_runs - successful_runs
        
        execution_times = [r['execution_time'] for r in results if r.get('success', False) and r['execution_time'] > 0]
        
        if execution_times:
            avg_execution_time = sum(execution_times) / len(execution_times)
            min_execution_time = min(execution_times)
            max_execution_time = max(execution_times)
        else:
            avg_execution_time = 0
            min_execution_time = 0
            max_execution_time = 0
        
        # Get sample outputs
        sample_outputs = [r.get('stdout', '') for r in results if r.get('stdout')][:5]
        
        self.active_tests[test_id]['metrics'].update({
            'total_runs': total_runs,
            'successful_runs': successful_runs,
            'failed_runs': failed_runs,
            'avg_execution_time': avg_execution_time,
            'min_execution_time': min_execution_time,
            'max_execution_time': max_execution_time,
            'script_outputs': sample_outputs
        })
    
    def run_url_load_test(self, config: Dict[str, Any]) -> str:
        """Run simple URL load test without BrowserStack"""
        test_id = f"url_test_{int(time.time())}"
        
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
                'min_response_time': float('inf'),
                'max_response_time': 0
            }
        }
        
        self.active_tests[test_id] = test_session
        
        # Start test in background
        thread = threading.Thread(target=self._execute_url_test, args=(test_id, config))
        thread.daemon = True
        thread.start()
        
        return test_id
    
    def _execute_url_test(self, test_id: str, config: Dict[str, Any]):
        """Execute URL load test"""
        try:
            target_url = config['target_url']
            concurrent_users = config.get('concurrent_users', 10)
            test_duration = config.get('test_duration', 300)
            
            # Create concurrent request threads
            user_threads = []
            
            for i in range(concurrent_users):
                thread = threading.Thread(
                    target=self._run_url_requests,
                    args=(test_id, i, target_url, test_duration)
                )
                thread.daemon = True
                user_threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in user_threads:
                thread.join()
            
            # Calculate final metrics
            self._calculate_url_metrics(test_id)
            self.active_tests[test_id]['status'] = 'completed'
            
        except Exception as e:
            self.active_tests[test_id]['status'] = 'failed'
            self.active_tests[test_id]['error'] = str(e)
    
    def _run_url_requests(self, test_id: str, user_id: int, url: str, duration: int):
        """Run URL requests for a single user"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': f'LoadTester-User-{user_id}'
        })
        
        start_time = time.time()
        request_count = 0
        
        while time.time() - start_time < duration:
            request_count += 1
            
            # Make request and measure time
            result = self._make_single_request(session, url, user_id, request_count)
            
            # Store result
            self.active_tests[test_id]['results'].append(result)
            
            # Wait between requests
            time.sleep(2)
            
            # Limit requests to prevent overwhelming
            if request_count >= 30:
                break
    
    def _make_single_request(self, session: requests.Session, url: str, user_id: int, request_number: int) -> Dict[str, Any]:
        """Make a single HTTP request and capture metrics"""
        try:
            print(f"🌐 User {user_id}, Request {request_number}: Loading {url}")
            
            start_time = time.time()
            response = session.get(url, timeout=10)
            response_time = time.time() - start_time
            
            success = 200 <= response.status_code < 400
            
            result = {
                'user_id': user_id,
                'request_number': request_number,
                'url': url,
                'response_time': response_time,
                'status_code': response.status_code,
                'success': success,
                'response_size': len(response.content),
                'timestamp': datetime.now().isoformat()
            }
            
            status = "✅" if success else "❌"
            print(f"  {status} Response time: {response_time:.2f}s, Status: {response.status_code}")
            
            return result
            
        except Exception as e:
            return {
                'user_id': user_id,
                'request_number': request_number,
                'url': url,
                'response_time': 0,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _calculate_url_metrics(self, test_id: str):
        """Calculate URL test metrics"""
        results = self.active_tests[test_id]['results']
        
        total_requests = len(results)
        successful_requests = sum(1 for r in results if r.get('success', False))
        failed_requests = total_requests - successful_requests
        
        response_times = [r['response_time'] for r in results if r.get('success', False) and r['response_time'] > 0]
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
        else:
            avg_response_time = 0
            min_response_time = 0
            max_response_time = 0
        
        self.active_tests[test_id]['metrics'].update({
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'avg_response_time': avg_response_time,
            'min_response_time': min_response_time,
            'max_response_time': max_response_time
        })

# Global script timer instance
script_timer = ScriptLoadTimer()

@app.route('/')
def script_dashboard():
    """Script Load Timer Dashboard"""
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Script Load Timer</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f0f2f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .section { margin: 20px 0; padding: 25px; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .button { padding: 12px 24px; background: #28a745; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; }
        .button:hover { background: #218838; }
        .form-group { margin: 15px 0; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: 600; }
        .form-group input, select, textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; }
        .metric-card { padding: 20px; background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; border-radius: 10px; text-align: center; }
        .test-result { padding: 15px; margin: 10px 0; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #28a745; }
        h1 { color: #28a745; text-align: center; }
        .tabs { display: flex; margin-bottom: 20px; }
        .tab { padding: 10px 20px; background: #e9ecef; border: none; cursor: pointer; }
        .tab.active { background: #28a745; color: white; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ Script Load Timer</h1>
        <p style="text-align: center; color: #666;">Run your scripts and capture load times - No BrowserStack needed!</p>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('script')">📜 Script Testing</button>
            <button class="tab" onclick="showTab('url')">🌐 URL Testing</button>
        </div>
        
        <div id="script-tab" class="tab-content active">
            <div class="section">
                <h2>📜 Script Load Testing</h2>
                <div class="form-group">
                    <label>Script Path:</label>
                    <input type="text" id="scriptPath" placeholder="/path/to/your/script.py" value="test_system.py">
                </div>
                <div class="form-group">
                    <label>Script Arguments (one per line):</label>
                    <textarea id="scriptArgs" rows="3" placeholder="--arg1 value1
--arg2 value2"></textarea>
                </div>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">
                    <div class="form-group">
                        <label>Concurrent Instances:</label>
                        <input type="number" id="concurrentInstances" value="5" min="1" max="20">
                    </div>
                    <div class="form-group">
                        <label>Test Duration (seconds):</label>
                        <input type="number" id="scriptDuration" value="180" min="60" max="600">
                    </div>
                    <div class="form-group">
                        <label>Python Version:</label>
                        <select id="pythonVersion">
                            <option value="python3">Python 3</option>
                            <option value="python">Python</option>
                        </select>
                    </div>
                </div>
                <button class="button" onclick="startScriptTest()">⚡ Start Script Load Test</button>
            </div>
        </div>
        
        <div id="url-tab" class="tab-content">
            <div class="section">
                <h2>🌐 URL Load Testing</h2>
                <div class="form-group">
                    <label>Target URL:</label>
                    <input type="url" id="targetUrl" placeholder="https://your-website.com" value="http://localhost:3000">
                </div>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;">
                    <div class="form-group">
                        <label>Concurrent Users:</label>
                        <input type="number" id="concurrentUsers" value="10" min="1" max="50">
                    </div>
                    <div class="form-group">
                        <label>Test Duration (seconds):</label>
                        <input type="number" id="urlDuration" value="180" min="60" max="600">
                    </div>
                </div>
                <button class="button" onclick="startUrlTest()">🌐 Start URL Load Test</button>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Active Tests</h2>
            <div id="activeTests">No active tests</div>
        </div>
        
        <div class="section">
            <h2>📈 Performance Metrics</h2>
            <div id="metricsContainer" class="metrics">
                <div class="metric-card">
                    <div style="font-size: 24px; font-weight: bold;">0</div>
                    <div>Total Runs</div>
                </div>
                <div class="metric-card">
                    <div style="font-size: 24px; font-weight: bold;">0</div>
                    <div>Successful</div>
                </div>
                <div class="metric-card">
                    <div style="font-size: 24px; font-weight: bold;">0.0s</div>
                    <div>Avg Time</div>
                </div>
                <div class="metric-card">
                    <div style="font-size: 24px; font-weight: bold;">0%</div>
                    <div>Success Rate</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📖 Usage Examples</h2>
            <h3>🐍 Script Testing Examples:</h3>
            <ul>
                <li><strong>Python Script:</strong> <code>my_script.py</code></li>
                <li><strong>With Arguments:</strong> <code>--url http://localhost:3000 --users 10</code></li>
                <li><strong>Test Script:</strong> <code>test_system.py</code> (already available)</li>
            </ul>
            
            <h3>🌐 URL Testing Examples:</h3>
            <ul>
                <li><strong>Local Server:</strong> <code>http://localhost:3000</code></li>
                <li><strong>Your Website:</strong> <code>https://your-website.com</code></li>
                <li><strong>API Endpoint:</strong> <code>https://api.your-service.com/health</code></li>
            </ul>
            
            <h3>📊 Metrics Captured:</h3>
            <ul>
                <li><strong>Execution Time:</strong> How long your script takes to run</li>
                <li><strong>Success Rate:</strong> Percentage of successful executions</li>
                <li><strong>System Metrics:</strong> CPU and memory usage</li>
                <li><strong>Output Capture:</strong> Script stdout/stderr</li>
            </ul>
        </div>
    </div>

    <script>
        function showTab(tabName) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Remove active class from all tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab content
            document.getElementById(tabName + '-tab').classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
        }
        
        function startScriptTest() {
            const scriptArgs = document.getElementById('scriptArgs').value
                .split('\\n')
                .map(arg => arg.trim())
                .filter(arg => arg.length > 0);
            
            const config = {
                script_path: document.getElementById('scriptPath').value,
                script_args: scriptArgs,
                concurrent_instances: parseInt(document.getElementById('concurrentInstances').value),
                test_duration: parseInt(document.getElementById('scriptDuration').value)
            };
            
            fetch('/start_script_test', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(config)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('⚡ Script load test started! Test ID: ' + data.test_id);
                    loadActiveTests();
                } else {
                    alert('❌ Error: ' + data.error);
                }
            });
        }
        
        function startUrlTest() {
            const config = {
                target_url: document.getElementById('targetUrl').value,
                concurrent_users: parseInt(document.getElementById('concurrentUsers').value),
                test_duration: parseInt(document.getElementById('urlDuration').value)
            };
            
            fetch('/start_url_test', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(config)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('🌐 URL load test started! Test ID: ' + data.test_id);
                    loadActiveTests();
                } else {
                    alert('❌ Error: ' + data.error);
                }
            });
        }
        
        function loadActiveTests() {
            fetch('/script_tests')
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
                    testDiv.className = 'test-result';
                    
                    const testType = test.id.includes('script') ? '📜 Script' : '🌐 URL';
                    const target = test.config.script_path || test.config.target_url || 'Unknown';
                    
                    testDiv.innerHTML = `
                        <strong>${testType} Test - ${test.id}</strong> - ${test.status.toUpperCase()}<br>
                        <small>Target: ${target} | Started: ${new Date(test.start_time).toLocaleTimeString()}</small>
                    `;
                    container.appendChild(testDiv);
                });
                
                updateMetrics(data);
            });
        }
        
        function updateMetrics(tests) {
            let totalRuns = 0, successful = 0, totalTime = 0, testCount = 0;
            
            Object.values(tests).forEach(test => {
                if (test.metrics) {
                    totalRuns += test.metrics.total_runs || test.metrics.total_requests || 0;
                    successful += test.metrics.successful_runs || test.metrics.successful_requests || 0;
                    if (test.metrics.avg_execution_time || test.metrics.avg_response_time) {
                        totalTime += test.metrics.avg_execution_time || test.metrics.avg_response_time;
                        testCount++;
                    }
                }
            });
            
            const avgTime = testCount > 0 ? totalTime / testCount : 0;
            const successRate = totalRuns > 0 ? (successful / totalRuns) * 100 : 0;
            
            document.querySelector('.metrics .metric-card:nth-child(1) div').textContent = totalRuns;
            document.querySelector('.metrics .metric-card:nth-child(2) div').textContent = successful;
            document.querySelector('.metrics .metric-card:nth-child(3) div').textContent = avgTime.toFixed(1) + 's';
            document.querySelector('.metrics .metric-card:nth-child(4) div').textContent = successRate.toFixed(0) + '%';
        }
        
        setInterval(loadActiveTests, 5000);
        loadActiveTests();
    </script>
</body>
</html>
    ''')

@app.route('/start_script_test', methods=['POST'])
def start_script_test():
    """Start script load test"""
    try:
        config = request.get_json()
        test_id = script_timer.run_script_load_test(config)
        return jsonify({'success': True, 'test_id': test_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/start_url_test', methods=['POST'])
def start_url_test():
    """Start URL load test"""
    try:
        config = request.get_json()
        test_id = script_timer.run_url_load_test(config)
        return jsonify({'success': True, 'test_id': test_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/script_tests')
def get_script_tests():
    """Get active script tests"""
    return jsonify(script_timer.active_tests)

if __name__ == '__main__':
    print("⚡ Starting Script Load Timer...")
    print("📖 Dashboard: http://localhost:5004")
    print("🎯 Run your scripts and capture load times!")
    print("\n📜 Perfect for:")
    print("   • Testing your Python scripts")
    print("   • Measuring execution times")
    print("   • Load testing without BrowserStack")
    print("   • Simple URL performance testing")
    
    app.run(host='0.0.0.0', port=5004, debug=True)
