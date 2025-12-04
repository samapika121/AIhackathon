#!/usr/bin/env python3
"""
Test Script for Video Load Tester System
Automated tests to verify everything is working
"""

import requests
import json
import time
import sys

def test_service(url, name):
    """Test if a service is running"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {name} is running at {url}")
            return True
        else:
            print(f"❌ {name} returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name} is not accessible: {e}")
        return False

def test_facebook_analyzer():
    """Test the Facebook game analyzer"""
    print("\n🧪 Testing Facebook Game Analyzer...")
    
    test_urls = [
        "http://localhost:3000",  # Our simulator
        "https://httpbin.org",    # Public API testing site
        "https://www.facebook.com/games"  # Facebook games
    ]
    
    for url in test_urls:
        try:
            print(f"  🔍 Analyzing: {url}")
            
            response = requests.post(
                "http://localhost:5001/analyze",
                json={"url": url},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    analysis = data['analysis']
                    scenarios = analysis.get('scenarios', [])
                    print(f"    ✅ Analysis successful - {len(scenarios)} scenarios created")
                    
                    # Show first scenario
                    if scenarios:
                        first_scenario = scenarios[0]
                        print(f"    📋 First scenario: {first_scenario['name']}")
                        print(f"    ⚡ Actions: {len(first_scenario['actions'])}")
                else:
                    print(f"    ❌ Analysis failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"    ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
        
        time.sleep(1)  # Be nice to servers

def test_load_test_execution():
    """Test running a small load test"""
    print("\n🚀 Testing Load Test Execution...")
    
    # First analyze our local simulator
    try:
        print("  📊 Analyzing local simulator...")
        response = requests.post(
            "http://localhost:5001/analyze",
            json={"url": "http://localhost:3000"},
            timeout=10
        )
        
        if response.status_code != 200 or not response.json().get('success'):
            print("  ❌ Cannot analyze local simulator")
            return False
        
        analysis = response.json()['analysis']
        scenario = analysis['scenarios'][0]  # Use first scenario
        
        # Start a small load test
        print("  🎯 Starting small load test (3 users, 30 seconds)...")
        
        test_config = {
            'base_url': analysis['base_url'],
            'scenario': scenario,
            'concurrent_users': 3,
            'duration': 30,
            'ramp_up_time': 10
        }
        
        response = requests.post(
            "http://localhost:5001/start_test",
            json=test_config,
            timeout=10
        )
        
        if response.status_code == 200 and response.json().get('success'):
            test_id = response.json()['test_id']
            print(f"  ✅ Load test started - ID: {test_id}")
            
            # Monitor for a few seconds
            print("  📈 Monitoring test progress...")
            for i in range(6):  # Monitor for 30 seconds
                time.sleep(5)
                
                # Get test status
                status_response = requests.get("http://localhost:5001/active_tests")
                if status_response.status_code == 200:
                    tests = status_response.json()
                    if test_id in tests:
                        test_data = tests[test_id]
                        metrics = test_data.get('metrics', {})
                        
                        total = metrics.get('total_requests', 0)
                        successful = metrics.get('successful_requests', 0)
                        failed = metrics.get('failed_requests', 0)
                        avg_time = metrics.get('avg_response_time', 0)
                        
                        print(f"    📊 Requests: {total} | Success: {successful} | Failed: {failed} | Avg Time: {avg_time:.2f}s")
                        
                        if total > 0:
                            success_rate = (successful / total) * 100
                            if success_rate > 80:
                                print(f"    ✅ Good performance: {success_rate:.1f}% success rate")
                            else:
                                print(f"    ⚠️  Performance issue: {success_rate:.1f}% success rate")
            
            return True
        else:
            print("  ❌ Failed to start load test")
            return False
            
    except Exception as e:
        print(f"  ❌ Load test error: {e}")
        return False

def test_game_simulator():
    """Test the game API simulator"""
    print("\n🎮 Testing Game API Simulator...")
    
    endpoints = [
        ("/", "GET", "Homepage"),
        ("/api/login", "POST", "Login"),
        ("/api/lobby", "GET", "Lobby"),
        ("/api/server_stats", "GET", "Server Stats")
    ]
    
    for endpoint, method, name in endpoints:
        try:
            url = f"http://localhost:3000{endpoint}"
            
            if method == "POST":
                response = requests.post(url, json={"username": "test_user", "password": "test_pass"}, timeout=5)
            else:
                response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"  ✅ {name}: {response.status_code}")
            else:
                print(f"  ⚠️  {name}: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ {name}: {e}")

def main():
    """Run all tests"""
    print("🧪 Video Load Tester System Tests")
    print("=" * 50)
    
    # Test if all services are running
    services = [
        ("http://localhost:3000", "Game API Simulator"),
        ("http://localhost:5000", "General Load Tester"),
        ("http://localhost:5001", "Facebook Game Tester")
    ]
    
    print("\n📡 Checking Services...")
    all_running = True
    for url, name in services:
        if not test_service(url, name):
            all_running = False
    
    if not all_running:
        print("\n❌ Some services are not running. Please start them first:")
        print("  Terminal 1: python3 game_api_simulator.py")
        print("  Terminal 2: python3 simple_main.py")
        print("  Terminal 3: python3 facebook_game_tester.py")
        return False
    
    # Test game simulator
    test_game_simulator()
    
    # Test Facebook analyzer
    test_facebook_analyzer()
    
    # Test load test execution
    test_load_test_execution()
    
    print("\n🎉 System Test Complete!")
    print("\n📖 How to use:")
    print("1. Open http://localhost:5001 in your browser")
    print("2. Enter a website URL (try: http://localhost:3000)")
    print("3. Click 'Analyze Website'")
    print("4. Configure and start a load test")
    print("5. Monitor real-time metrics")
    
    return True

if __name__ == "__main__":
    main()
