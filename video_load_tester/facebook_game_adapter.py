#!/usr/bin/env python3
"""
Facebook Game Load Testing Adapter
Handles Facebook game authentication and API calls
"""

import requests
import json
import time
from typing import Dict, Any, List
import urllib.parse
from datetime import datetime

class FacebookGameTester:
    def __init__(self, game_url: str, app_id: str = None):
        self.game_url = game_url
        self.app_id = app_id
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def analyze_game_endpoints(self) -> Dict[str, Any]:
        """
        Analyze the Facebook game to identify API endpoints
        """
        print(f"🔍 Analyzing Facebook game: {self.game_url}")
        
        try:
            # Load the game page
            response = self.session.get(self.game_url)
            
            if response.status_code != 200:
                raise Exception(f"Cannot access game URL: {response.status_code}")
            
            # Extract game information
            game_info = self._extract_game_info(response.text)
            
            # Identify common Facebook game API patterns
            api_endpoints = self._identify_api_endpoints(response.text)
            
            return {
                'game_info': game_info,
                'api_endpoints': api_endpoints,
                'base_url': self._extract_base_url(response.text),
                'csrf_token': self._extract_csrf_token(response.text),
                'session_info': self._extract_session_info(response.text)
            }
            
        except Exception as e:
            print(f"❌ Error analyzing game: {e}")
            return self._get_default_facebook_endpoints()
    
    def _extract_game_info(self, html_content: str) -> Dict[str, Any]:
        """Extract basic game information"""
        game_info = {
            'title': 'Unknown Game',
            'app_id': self.app_id,
            'game_type': 'facebook_game'
        }
        
        # Try to extract game title
        if '<title>' in html_content:
            start = html_content.find('<title>') + 7
            end = html_content.find('</title>', start)
            if end > start:
                game_info['title'] = html_content[start:end].strip()
        
        # Try to extract app ID from Facebook SDK
        if 'FB.init' in html_content:
            start = html_content.find('appId')
            if start > 0:
                start = html_content.find(':', start) + 1
                end = html_content.find(',', start)
                if end > start:
                    app_id = html_content[start:end].strip().strip('"\'')
                    game_info['app_id'] = app_id
        
        return game_info
    
    def _identify_api_endpoints(self, html_content: str) -> List[Dict[str, Any]]:
        """Identify common API endpoints used by Facebook games"""
        endpoints = []
        
        # Common Facebook game API patterns
        common_patterns = [
            {'pattern': '/api/login', 'type': 'authentication', 'method': 'POST'},
            {'pattern': '/api/user', 'type': 'user_info', 'method': 'GET'},
            {'pattern': '/api/game/start', 'type': 'game_start', 'method': 'POST'},
            {'pattern': '/api/game/action', 'type': 'game_action', 'method': 'POST'},
            {'pattern': '/api/leaderboard', 'type': 'leaderboard', 'method': 'GET'},
            {'pattern': '/api/friends', 'type': 'social', 'method': 'GET'},
            {'pattern': '/api/achievements', 'type': 'achievements', 'method': 'GET'},
            {'pattern': '/api/store', 'type': 'monetization', 'method': 'GET'},
            {'pattern': '/api/purchase', 'type': 'monetization', 'method': 'POST'},
        ]
        
        # Look for actual API calls in the HTML/JavaScript
        for pattern_info in common_patterns:
            if pattern_info['pattern'] in html_content:
                endpoints.append({
                    'endpoint': pattern_info['pattern'],
                    'type': pattern_info['type'],
                    'method': pattern_info['method'],
                    'detected': True
                })
            else:
                # Add as potential endpoint even if not detected
                endpoints.append({
                    'endpoint': pattern_info['pattern'],
                    'type': pattern_info['type'],
                    'method': pattern_info['method'],
                    'detected': False
                })
        
        return endpoints
    
    def _extract_base_url(self, html_content: str) -> str:
        """Extract the base API URL"""
        # Try to find API base URL in the content
        if 'api_url' in html_content.lower():
            # Look for common patterns
            patterns = [
                r'api_url["\s]*:["\s]*([^"]+)',
                r'baseURL["\s]*:["\s]*([^"]+)',
                r'apiEndpoint["\s]*:["\s]*([^"]+)'
            ]
            
            import re
            for pattern in patterns:
                match = re.search(pattern, html_content, re.IGNORECASE)
                if match:
                    return match.group(1)
        
        # Default to same domain
        from urllib.parse import urlparse
        parsed = urlparse(self.game_url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def _extract_csrf_token(self, html_content: str) -> str:
        """Extract CSRF token if present"""
        import re
        
        # Common CSRF token patterns
        patterns = [
            r'csrf_token["\s]*:["\s]*([^"]+)',
            r'_token["\s]*:["\s]*([^"]+)',
            r'authenticity_token["\s]*:["\s]*([^"]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_session_info(self, html_content: str) -> Dict[str, Any]:
        """Extract session information"""
        session_info = {}
        
        # Look for Facebook user ID
        if 'userID' in html_content:
            import re
            match = re.search(r'userID["\s]*:["\s]*([^"]+)', html_content)
            if match:
                session_info['user_id'] = match.group(1)
        
        # Look for access token
        if 'accessToken' in html_content:
            import re
            match = re.search(r'accessToken["\s]*:["\s]*([^"]+)', html_content)
            if match:
                session_info['access_token'] = match.group(1)
        
        return session_info
    
    def _get_default_facebook_endpoints(self) -> Dict[str, Any]:
        """Return default Facebook game endpoints if analysis fails"""
        return {
            'game_info': {
                'title': 'Facebook Game',
                'app_id': self.app_id or 'unknown',
                'game_type': 'facebook_game'
            },
            'api_endpoints': [
                {'endpoint': '/api/login', 'type': 'authentication', 'method': 'POST', 'detected': False},
                {'endpoint': '/api/user', 'type': 'user_info', 'method': 'GET', 'detected': False},
                {'endpoint': '/api/game/start', 'type': 'game_start', 'method': 'POST', 'detected': False},
                {'endpoint': '/api/game/action', 'type': 'game_action', 'method': 'POST', 'detected': False},
            ],
            'base_url': self._extract_base_url_from_game_url(),
            'csrf_token': None,
            'session_info': {}
        }
    
    def _extract_base_url_from_game_url(self) -> str:
        """Extract base URL from game URL"""
        from urllib.parse import urlparse
        parsed = urlparse(self.game_url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def create_load_test_scenario(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Create a load test scenario based on the analysis"""
        
        base_url = analysis_result['base_url']
        endpoints = analysis_result['api_endpoints']
        
        # Create realistic user flow
        scenario_actions = []
        
        # 1. Authentication (if available)
        auth_endpoint = next((ep for ep in endpoints if ep['type'] == 'authentication'), None)
        if auth_endpoint:
            scenario_actions.append({
                'type': 'facebook_login',
                'endpoint': auth_endpoint['endpoint'],
                'method': auth_endpoint['method'],
                'delay': 2.0,
                'payload': self._get_auth_payload(analysis_result)
            })
        
        # 2. Get user info
        user_endpoint = next((ep for ep in endpoints if ep['type'] == 'user_info'), None)
        if user_endpoint:
            scenario_actions.append({
                'type': 'get_user_info',
                'endpoint': user_endpoint['endpoint'],
                'method': user_endpoint['method'],
                'delay': 1.0
            })
        
        # 3. Start game
        game_start_endpoint = next((ep for ep in endpoints if ep['type'] == 'game_start'), None)
        if game_start_endpoint:
            scenario_actions.append({
                'type': 'start_game',
                'endpoint': game_start_endpoint['endpoint'],
                'method': game_start_endpoint['method'],
                'delay': 1.5
            })
        
        # 4. Game actions
        game_action_endpoint = next((ep for ep in endpoints if ep['type'] == 'game_action'), None)
        if game_action_endpoint:
            # Add multiple game actions
            for i in range(3):
                scenario_actions.append({
                    'type': f'game_action_{i+1}',
                    'endpoint': game_action_endpoint['endpoint'],
                    'method': game_action_endpoint['method'],
                    'delay': 0.5 + (i * 0.2)
                })
        
        # 5. Social features
        social_endpoints = [ep for ep in endpoints if ep['type'] in ['social', 'leaderboard', 'achievements']]
        for social_ep in social_endpoints[:2]:  # Limit to 2 social calls
            scenario_actions.append({
                'type': f'social_{social_ep["type"]}',
                'endpoint': social_ep['endpoint'],
                'method': social_ep['method'],
                'delay': 1.0
            })
        
        return {
            'name': f'{analysis_result["game_info"]["title"]} - Full Flow',
            'base_url': base_url,
            'actions': scenario_actions,
            'csrf_token': analysis_result.get('csrf_token'),
            'session_info': analysis_result.get('session_info', {})
        }
    
    def _get_auth_payload(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate authentication payload"""
        payload = {}
        
        # Facebook-specific auth
        if analysis_result['game_info'].get('app_id'):
            payload['app_id'] = analysis_result['game_info']['app_id']
        
        # Add CSRF token if available
        if analysis_result.get('csrf_token'):
            payload['csrf_token'] = analysis_result['csrf_token']
        
        # Add session info if available
        if analysis_result.get('session_info'):
            payload.update(analysis_result['session_info'])
        
        return payload
    
    def test_endpoint_accessibility(self, endpoint: str, method: str = 'GET') -> Dict[str, Any]:
        """Test if an endpoint is accessible"""
        try:
            url = f"{self.game_url.rstrip('/')}{endpoint}"
            
            if method.upper() == 'POST':
                response = self.session.post(url, timeout=10)
            else:
                response = self.session.get(url, timeout=10)
            
            return {
                'endpoint': endpoint,
                'accessible': response.status_code < 500,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'requires_auth': response.status_code == 401 or response.status_code == 403
            }
            
        except Exception as e:
            return {
                'endpoint': endpoint,
                'accessible': False,
                'error': str(e),
                'requires_auth': False
            }

def create_facebook_game_scenario(game_url: str, app_id: str = None) -> Dict[str, Any]:
    """
    Main function to create a load test scenario for a Facebook game
    """
    print(f"🎮 Creating load test scenario for Facebook game...")
    print(f"🔗 Game URL: {game_url}")
    
    # Initialize the tester
    tester = FacebookGameTester(game_url, app_id)
    
    # Analyze the game
    analysis = tester.analyze_game_endpoints()
    
    # Create load test scenario
    scenario = tester.create_load_test_scenario(analysis)
    
    # Test endpoint accessibility
    print(f"🧪 Testing endpoint accessibility...")
    endpoint_tests = []
    for action in scenario['actions']:
        test_result = tester.test_endpoint_accessibility(action['endpoint'], action.get('method', 'GET'))
        endpoint_tests.append(test_result)
        
        status = "✅" if test_result['accessible'] else "❌"
        auth_note = " (requires auth)" if test_result.get('requires_auth') else ""
        print(f"  {status} {action['endpoint']}{auth_note}")
    
    # Add test results to scenario
    scenario['endpoint_tests'] = endpoint_tests
    scenario['analysis_timestamp'] = datetime.now().isoformat()
    
    return scenario

def main():
    """Example usage"""
    # Example Facebook game URLs (replace with actual game)
    example_games = [
        "https://www.facebook.com/games/farmville",
        "https://apps.facebook.com/candycrushsaga/",
        "https://www.facebook.com/games/wordswithfriends"
    ]
    
    print("🎮 Facebook Game Load Testing Tool")
    print("=" * 50)
    
    # Get game URL from user
    game_url = input("Enter Facebook game URL: ").strip()
    
    if not game_url:
        print("Using example URL for demonstration...")
        game_url = example_games[0]
    
    # Optional: Get app ID
    app_id = input("Enter Facebook App ID (optional): ").strip() or None
    
    try:
        # Create scenario
        scenario = create_facebook_game_scenario(game_url, app_id)
        
        # Save scenario
        import os
        os.makedirs('facebook_scenarios', exist_ok=True)
        
        scenario_file = f"facebook_scenarios/scenario_{int(time.time())}.json"
        with open(scenario_file, 'w') as f:
            json.dump(scenario, f, indent=2)
        
        print(f"\n✅ Scenario created successfully!")
        print(f"📁 Saved to: {scenario_file}")
        print(f"🎯 Game: {scenario['name']}")
        print(f"🔗 Base URL: {scenario['base_url']}")
        print(f"⚡ Actions: {len(scenario['actions'])}")
        
        # Show usage instructions
        print(f"\n📖 How to use this scenario:")
        print(f"1. Copy the scenario file to your load tester")
        print(f"2. Update the target URL in your load test configuration")
        print(f"3. Run the load test with realistic user counts")
        print(f"4. Monitor for authentication and rate limiting issues")
        
    except Exception as e:
        print(f"❌ Error creating scenario: {e}")

if __name__ == "__main__":
    main()
