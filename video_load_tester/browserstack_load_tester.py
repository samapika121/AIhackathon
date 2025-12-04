#!/usr/bin/env python3
"""
BrowserStack Load Testing Integration
Run load tests on real devices via BrowserStack and capture load times
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import json
import threading
from datetime import datetime
from typing import Dict, List, Any
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

class BrowserStackLoadTester:
    def __init__(self, username: str, access_key: str):
        self.username = username
        self.access_key = access_key
        self.hub_url = f"https://{username}:{access_key}@hub-cloud.browserstack.com/wd/hub"
        self.active_tests = {}
        
    def get_device_capabilities(self, device_type: str = "mobile") -> List[Dict[str, Any]]:
        """Get BrowserStack device capabilities"""
        if device_type == "mobile":
            return [
                {
                    'browserName': 'chrome',
                    'device': 'iPhone 13',
                    'realMobile': 'true',
                    'os_version': '15',
                    'name': 'iPhone 13 Load Test'
                },
                {
                    'browserName': 'chrome', 
                    'device': 'Samsung Galaxy S21',
                    'realMobile': 'true',
                    'os_version': '11.0',
                    'name': 'Galaxy S21 Load Test'
                },
                {
                    'browserName': 'chrome',
                    'device': 'iPad Pro 12.9 2021',
                    'realMobile': 'true', 
                    'os_version': '15',
                    'name': 'iPad Pro Load Test'
                }
            ]
        else:  # desktop
            return [
                {
                    'browserName': 'chrome',
                    'browser_version': 'latest',
                    'os': 'Windows',
                    'os_version': '10',
                    'name': 'Windows Chrome Load Test'
                },
                {
                    'browserName': 'safari',
                    'browser_version': 'latest',
                    'os': 'OS X',
                    'os_version': 'Big Sur',
                    'name': 'Mac Safari Load Test'
                }
            ]
    
    def create_driver(self, capabilities: Dict[str, Any]) -> webdriver.Remote:
        """Create BrowserStack WebDriver instance"""
        return webdriver.Remote(
            command_executor=self.hub_url,
            desired_capabilities=capabilities
        )
    
    def run_browserstack_load_test(self, config: Dict[str, Any]) -> str:
        """Run load test on BrowserStack devices"""
        test_id = f"bs_test_{int(time.time())}"
        
        test_session = {
            'id': test_id,
            'config': config,
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'results': [],
            'metrics': {
                'total_devices': 0,
                'successful_tests': 0,
                'failed_tests': 0,
                'avg_load_time': 0,
                'device_results': []
            }
        }
        
        self.active_tests[test_id] = test_session
        
        # Start test in background
        thread = threading.Thread(target=self._execute_browserstack_test, args=(test_id, config))
        thread.daemon = True
        thread.start()
        
        return test_id
    
    def _execute_browserstack_test(self, test_id: str, config: Dict[str, Any]):
        """Execute BrowserStack load test"""
        try:
            target_url = config['target_url']
            device_type = config.get('device_type', 'mobile')
            concurrent_devices = config.get('concurrent_devices', 3)
            test_duration = config.get('test_duration', 300)
            
            # Get device capabilities
            capabilities_list = self.get_device_capabilities(device_type)
            
            # Limit concurrent devices to available capabilities
            if concurrent_devices > len(capabilities_list):
                concurrent_devices = len(capabilities_list)
            
            # Create device test threads
            device_threads = []
            
            for i in range(concurrent_devices):
                capabilities = capabilities_list[i % len(capabilities_list)]
                capabilities['name'] = f"{capabilities['name']} - Device {i+1}"
                
                thread = threading.Thread(
                    target=self._run_device_test,
                    args=(test_id, i, capabilities, target_url, test_duration)
                )
                thread.daemon = True
                device_threads.append(thread)
                thread.start()
            
            # Wait for all device tests to complete
            for thread in device_threads:
                thread.join()
            
            # Calculate final metrics
            self._calculate_final_metrics(test_id)
            self.active_tests[test_id]['status'] = 'completed'
            
        except Exception as e:
            self.active_tests[test_id]['status'] = 'failed'
            self.active_tests[test_id]['error'] = str(e)
    
    def _run_device_test(self, test_id: str, device_id: int, capabilities: Dict[str, Any], target_url: str, duration: int):
        """Run test on a single BrowserStack device"""
        driver = None
        device_results = []
        
        try:
            print(f"🚀 Starting test on {capabilities.get('device', capabilities.get('os', 'Unknown'))}")
            
            # Create driver
            driver = self.create_driver(capabilities)
            
            start_time = time.time()
            test_count = 0
            
            while time.time() - start_time < duration:
                test_count += 1
                
                # Measure page load time
                load_result = self._measure_page_load(driver, target_url, device_id, test_count)
                device_results.append(load_result)
                
                # Wait between tests
                time.sleep(5)
                
                # Break if we have enough data points
                if test_count >= 10:  # Limit to 10 tests per device to avoid long sessions
                    break
            
            # Store device results
            self.active_tests[test_id]['results'].extend(device_results)
            
            device_summary = {
                'device_id': device_id,
                'device_name': capabilities.get('device', capabilities.get('os', 'Unknown')),
                'total_tests': len(device_results),
                'successful_tests': sum(1 for r in device_results if r['success']),
                'avg_load_time': sum(r['load_time'] for r in device_results if r['success']) / max(1, sum(1 for r in device_results if r['success'])),
                'results': device_results
            }
            
            self.active_tests[test_id]['metrics']['device_results'].append(device_summary)
            
        except Exception as e:
            print(f"❌ Device test failed: {e}")
            error_result = {
                'device_id': device_id,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.active_tests[test_id]['results'].append(error_result)
            
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def _measure_page_load(self, driver: webdriver.Remote, url: str, device_id: int, test_number: int) -> Dict[str, Any]:
        """Measure page load time and capture performance metrics"""
        try:
            print(f"  📊 Test {test_number} on device {device_id}: Loading {url}")
            
            # Start timing
            start_time = time.time()
            
            # Navigate to URL
            driver.get(url)
            
            # Wait for page to be ready
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # Calculate load time
            load_time = time.time() - start_time
            
            # Get performance metrics from browser
            performance_data = self._get_browser_performance(driver)
            
            # Capture additional metrics
            page_title = driver.title
            current_url = driver.current_url
            
            # Take screenshot (optional)
            screenshot_data = None
            try:
                screenshot_data = driver.get_screenshot_as_base64()
            except:
                pass
            
            result = {
                'device_id': device_id,
                'test_number': test_number,
                'url': url,
                'load_time': load_time,
                'success': True,
                'page_title': page_title,
                'final_url': current_url,
                'performance_data': performance_data,
                'timestamp': datetime.now().isoformat(),
                'screenshot': screenshot_data[:100] if screenshot_data else None  # First 100 chars for storage
            }
            
            print(f"    ✅ Load time: {load_time:.2f}s")
            return result
            
        except Exception as e:
            print(f"    ❌ Load failed: {e}")
            return {
                'device_id': device_id,
                'test_number': test_number,
                'url': url,
                'load_time': 0,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_browser_performance(self, driver: webdriver.Remote) -> Dict[str, Any]:
        """Get browser performance metrics"""
        try:
            # Get navigation timing
            nav_timing = driver.execute_script("""
                var timing = window.performance.timing;
                return {
                    'dns_lookup': timing.domainLookupEnd - timing.domainLookupStart,
                    'tcp_connect': timing.connectEnd - timing.connectStart,
                    'request_response': timing.responseEnd - timing.requestStart,
                    'dom_processing': timing.domComplete - timing.domLoading,
                    'total_load': timing.loadEventEnd - timing.navigationStart
                };
            """)
            
            # Get resource timing
            resources = driver.execute_script("""
                var resources = window.performance.getEntriesByType('resource');
                return resources.slice(0, 10).map(function(r) {
                    return {
                        'name': r.name,
                        'duration': r.duration,
                        'size': r.transferSize || 0
                    };
                });
            """)
            
            return {
                'navigation_timing': nav_timing,
                'resources': resources,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_final_metrics(self, test_id: str):
        """Calculate final test metrics"""
        results = self.active_tests[test_id]['results']
        
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.get('success', False))
        failed_tests = total_tests - successful_tests
        
        successful_load_times = [r['load_time'] for r in results if r.get('success', False) and r['load_time'] > 0]
        avg_load_time = sum(successful_load_times) / len(successful_load_times) if successful_load_times else 0
        
        self.active_tests[test_id]['metrics'].update({
            'total_devices': len(self.active_tests[test_id]['metrics']['device_results']),
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'failed_tests': failed_tests,
            'avg_load_time': avg_load_time,
            'min_load_time': min(successful_load_times) if successful_load_times else 0,
            'max_load_time': max(successful_load_times) if successful_load_times else 0
        })

# Global BrowserStack tester instance
bs_tester = None

@app.route('/')
def browserstack_dashboard():
    """BrowserStack Load Testing Dashboard"""
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>BrowserStack Load Tester</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f0f2f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .section { margin: 20px 0; padding: 25px; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .button { padding: 12px 24px; background: #ff6900; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; }
        .button:hover { background: #e55a00; }
        .form-group { margin: 15px 0; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: 600; }
        .form-group input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .metric-card { padding: 20px; background: linear-gradient(135deg, #ff6900 0%, #fcb900 100%); color: white; border-radius: 10px; text-align: center; }
        .device-result { padding: 15px; margin: 10px 0; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #ff6900; }
        h1 { color: #ff6900; text-align: center; }
        .bs-logo { text-align: center; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="bs-logo">
            <h1>📱 BrowserStack Load Tester</h1>
            <p>Run load tests on real devices and capture performance metrics</p>
        </div>
        
        <div class="section">
            <h2>🔧 BrowserStack Configuration</h2>
            <div class="form-group">
                <label>BrowserStack Username:</label>
                <input type="text" id="bsUsername" placeholder="your_browserstack_username">
            </div>
            <div class="form-group">
                <label>BrowserStack Access Key:</label>
                <input type="password" id="bsAccessKey" placeholder="your_access_key">
            </div>
            <button class="button" onclick="configureBrowserStack()">🔑 Configure BrowserStack</button>
        </div>
        
        <div class="section">
            <h2>🚀 Load Test Configuration</h2>
            <div class="form-group">
                <label>Target URL:</label>
                <input type="url" id="targetUrl" placeholder="https://your-website.com" value="http://localhost:3000">
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">
                <div class="form-group">
                    <label>Device Type:</label>
                    <select id="deviceType">
                        <option value="mobile">Mobile Devices</option>
                        <option value="desktop">Desktop Browsers</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Concurrent Devices:</label>
                    <input type="number" id="concurrentDevices" value="3" min="1" max="5">
                </div>
                <div class="form-group">
                    <label>Test Duration (seconds):</label>
                    <input type="number" id="testDuration" value="180" min="60" max="600">
                </div>
            </div>
            <button class="button" onclick="startBrowserStackTest()">📱 Start BrowserStack Load Test</button>
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
                    <div>Total Tests</div>
                </div>
                <div class="metric-card">
                    <div style="font-size: 24px; font-weight: bold;">0</div>
                    <div>Devices Tested</div>
                </div>
                <div class="metric-card">
                    <div style="font-size: 24px; font-weight: bold;">0.0s</div>
                    <div>Avg Load Time</div>
                </div>
                <div class="metric-card">
                    <div style="font-size: 24px; font-weight: bold;">0%</div>
                    <div>Success Rate</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📖 BrowserStack Setup Guide</h2>
            <h3>🔑 Get BrowserStack Credentials:</h3>
            <ol>
                <li>Sign up at <a href="https://browserstack.com" target="_blank">BrowserStack.com</a></li>
                <li>Go to Account → Settings → Automate</li>
                <li>Copy your Username and Access Key</li>
                <li>Paste them in the configuration above</li>
            </ol>
            
            <h3>📱 Available Devices:</h3>
            <ul>
                <li><strong>Mobile:</strong> iPhone 13, Samsung Galaxy S21, iPad Pro</li>
                <li><strong>Desktop:</strong> Windows Chrome, Mac Safari</li>
            </ul>
            
            <h3>📊 Metrics Captured:</h3>
            <ul>
                <li><strong>Page Load Time:</strong> Total time to load your website</li>
                <li><strong>Navigation Timing:</strong> DNS, TCP, Request/Response times</li>
                <li><strong>Resource Loading:</strong> Individual resource load times</li>
                <li><strong>Device Performance:</strong> Per-device performance comparison</li>
            </ul>
        </div>
    </div>

    <script>
        let bsConfigured = false;
        
        function configureBrowserStack() {
            const username = document.getElementById('bsUsername').value.trim();
            const accessKey = document.getElementById('bsAccessKey').value.trim();
            
            if (!username || !accessKey) {
                alert('Please enter both username and access key');
                return;
            }
            
            fetch('/configure_browserstack', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: username, access_key: accessKey})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✅ BrowserStack configured successfully!');
                    bsConfigured = true;
                } else {
                    alert('❌ Configuration failed: ' + data.error);
                }
            });
        }
        
        function startBrowserStackTest() {
            if (!bsConfigured) {
                alert('Please configure BrowserStack credentials first');
                return;
            }
            
            const config = {
                target_url: document.getElementById('targetUrl').value,
                device_type: document.getElementById('deviceType').value,
                concurrent_devices: parseInt(document.getElementById('concurrentDevices').value),
                test_duration: parseInt(document.getElementById('testDuration').value)
            };
            
            fetch('/start_browserstack_test', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(config)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('🚀 BrowserStack load test started! Test ID: ' + data.test_id);
                    loadActiveTests();
                } else {
                    alert('❌ Error: ' + data.error);
                }
            });
        }
        
        function loadActiveTests() {
            fetch('/browserstack_tests')
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
                    testDiv.className = 'device-result';
                    testDiv.innerHTML = `
                        <strong>📱 ${test.id}</strong> - ${test.status.toUpperCase()}<br>
                        <small>URL: ${test.config.target_url} | Devices: ${test.config.concurrent_devices} | Started: ${new Date(test.start_time).toLocaleTimeString()}</small>
                    `;
                    container.appendChild(testDiv);
                });
                
                updateMetrics(data);
            });
        }
        
        function updateMetrics(tests) {
            let totalTests = 0, totalDevices = 0, totalLoadTime = 0, successfulTests = 0;
            
            Object.values(tests).forEach(test => {
                if (test.metrics) {
                    totalTests += test.metrics.total_tests || 0;
                    totalDevices += test.metrics.total_devices || 0;
                    if (test.metrics.avg_load_time) {
                        totalLoadTime += test.metrics.avg_load_time;
                    }
                    successfulTests += test.metrics.successful_tests || 0;
                }
            });
            
            const avgLoadTime = totalTests > 0 ? totalLoadTime / Object.keys(tests).length : 0;
            const successRate = totalTests > 0 ? (successfulTests / totalTests) * 100 : 0;
            
            document.querySelector('.metrics .metric-card:nth-child(1) div').textContent = totalTests;
            document.querySelector('.metrics .metric-card:nth-child(2) div').textContent = totalDevices;
            document.querySelector('.metrics .metric-card:nth-child(3) div').textContent = avgLoadTime.toFixed(1) + 's';
            document.querySelector('.metrics .metric-card:nth-child(4) div').textContent = successRate.toFixed(0) + '%';
        }
        
        setInterval(loadActiveTests, 10000);
        loadActiveTests();
    </script>
</body>
</html>
    ''')

@app.route('/configure_browserstack', methods=['POST'])
def configure_browserstack():
    """Configure BrowserStack credentials"""
    global bs_tester
    try:
        data = request.get_json()
        username = data.get('username')
        access_key = data.get('access_key')
        
        if not username or not access_key:
            return jsonify({'success': False, 'error': 'Username and access key required'})
        
        bs_tester = BrowserStackLoadTester(username, access_key)
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/start_browserstack_test', methods=['POST'])
def start_browserstack_test():
    """Start BrowserStack load test"""
    global bs_tester
    try:
        if not bs_tester:
            return jsonify({'success': False, 'error': 'BrowserStack not configured'})
        
        config = request.get_json()
        test_id = bs_tester.run_browserstack_load_test(config)
        
        return jsonify({'success': True, 'test_id': test_id})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/browserstack_tests')
def get_browserstack_tests():
    """Get active BrowserStack tests"""
    global bs_tester
    if bs_tester:
        return jsonify(bs_tester.active_tests)
    return jsonify({})

if __name__ == '__main__':
    print("📱 Starting BrowserStack Load Tester...")
    print("📖 Dashboard: http://localhost:5003")
    print("🎯 Test on real devices with BrowserStack!")
    print("\n🔑 You'll need BrowserStack credentials:")
    print("   1. Sign up at https://browserstack.com")
    print("   2. Get your username and access key")
    print("   3. Configure them in the dashboard")
    
    app.run(host='0.0.0.0', port=5003, debug=True)
