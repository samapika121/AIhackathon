#!/usr/bin/env python3
"""
Mobile Game API Discovery Tool
Help find and analyze mobile game API endpoints
"""

import requests
import json
import re
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Any
import time

class MobileAPIDiscovery:
    def __init__(self):
        self.common_patterns = [
            # Common mobile game API patterns
            "api.{domain}",
            "{domain}-api.com", 
            "backend.{domain}",
            "server.{domain}",
            "game-api.{domain}",
            "{domain}.herokuapp.com",
            "{domain}-backend.herokuapp.com"
        ]
        
        self.common_endpoints = [
            "/api/v1/auth/login",
            "/api/v1/user/profile", 
            "/api/v1/game/start",
            "/api/v1/game/action",
            "/api/v1/leaderboard",
            "/api/auth/login",
            "/api/user/profile",
            "/api/game/start",
            "/login",
            "/auth",
            "/api/player",
            "/api/session"
        ]
    
    def discover_api_from_game_name(self, game_name: str) -> List[str]:
        """Generate possible API URLs from game name"""
        game_name = game_name.lower().replace(" ", "").replace("-", "")
        
        possible_urls = []
        
        for pattern in self.common_patterns:
            url = pattern.format(domain=game_name)
            if not url.startswith("http"):
                url = f"https://{url}"
            possible_urls.append(url)
        
        return possible_urls
    
    def test_api_endpoints(self, base_url: str) -> Dict[str, Any]:
        """Test common endpoints on a base URL"""
        results = {
            'base_url': base_url,
            'accessible_endpoints': [],
            'requires_auth': [],
            'not_found': [],
            'errors': []
        }
        
        print(f"🔍 Testing API endpoints for: {base_url}")
        
        for endpoint in self.common_endpoints:
            try:
                url = urljoin(base_url, endpoint)
                
                # Test GET request
                response = requests.get(url, timeout=5, headers={
                    'User-Agent': 'MobileGameTester/1.0',
                    'Accept': 'application/json'
                })
                
                if response.status_code == 200:
                    results['accessible_endpoints'].append({
                        'endpoint': endpoint,
                        'method': 'GET',
                        'status': response.status_code,
                        'content_type': response.headers.get('content-type', ''),
                        'response_size': len(response.content)
                    })
                    print(f"  ✅ {endpoint} - {response.status_code}")
                    
                elif response.status_code in [401, 403]:
                    results['requires_auth'].append({
                        'endpoint': endpoint,
                        'status': response.status_code,
                        'auth_required': True
                    })
                    print(f"  🔐 {endpoint} - {response.status_code} (Auth Required)")
                    
                elif response.status_code == 404:
                    results['not_found'].append(endpoint)
                    print(f"  ❌ {endpoint} - 404")
                    
                else:
                    print(f"  ⚠️  {endpoint} - {response.status_code}")
                
                # Small delay to be respectful
                time.sleep(0.1)
                
            except Exception as e:
                results['errors'].append({
                    'endpoint': endpoint,
                    'error': str(e)
                })
                print(f"  💥 {endpoint} - Error: {e}")
        
        return results
    
    def analyze_mobile_game(self, game_name: str) -> Dict[str, Any]:
        """Complete analysis of a mobile game's API"""
        print(f"🎮 Analyzing mobile game: {game_name}")
        
        # Generate possible API URLs
        possible_urls = self.discover_api_from_game_name(game_name)
        
        analysis_results = {
            'game_name': game_name,
            'possible_urls': possible_urls,
            'working_apis': [],
            'recommendations': []
        }
        
        # Test each possible URL
        for url in possible_urls:
            try:
                print(f"\n🔗 Testing: {url}")
                
                # First, check if the base URL is accessible
                response = requests.get(url, timeout=5)
                
                if response.status_code < 500:  # Server exists
                    endpoint_results = self.test_api_endpoints(url)
                    
                    if (endpoint_results['accessible_endpoints'] or 
                        endpoint_results['requires_auth']):
                        analysis_results['working_apis'].append(endpoint_results)
                        print(f"  🎯 Found working API at: {url}")
                
            except Exception as e:
                print(f"  ❌ {url} not accessible: {e}")
        
        # Generate recommendations
        analysis_results['recommendations'] = self._generate_recommendations(analysis_results)
        
        return analysis_results
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if not analysis['working_apis']:
            recommendations.extend([
                "No APIs found automatically. Try these methods:",
                "1. Use network monitoring tools (Charles Proxy, Wireshark)",
                "2. Check the game's developer documentation", 
                "3. Look for API references in the game's mobile app",
                "4. Contact the game developers for API documentation"
            ])
        else:
            recommendations.extend([
                f"Found {len(analysis['working_apis'])} potential API endpoints",
                "Start load testing with the discovered endpoints",
                "Monitor authentication requirements carefully",
                "Begin with low concurrent users (5-10) to test limits"
            ])
        
        return recommendations

def main():
    """Interactive API discovery"""
    print("🎮 Mobile Game API Discovery Tool")
    print("=" * 50)
    
    discovery = MobileAPIDiscovery()
    
    while True:
        print("\nOptions:")
        print("1. Discover APIs by game name")
        print("2. Test specific API URL")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            game_name = input("Enter mobile game name: ").strip()
            if game_name:
                results = discovery.analyze_mobile_game(game_name)
                
                print(f"\n📊 Analysis Results for '{game_name}':")
                print("=" * 40)
                
                if results['working_apis']:
                    print("✅ Working APIs found:")
                    for api in results['working_apis']:
                        print(f"  🔗 {api['base_url']}")
                        print(f"     Accessible: {len(api['accessible_endpoints'])}")
                        print(f"     Auth Required: {len(api['requires_auth'])}")
                else:
                    print("❌ No working APIs found automatically")
                
                print("\n💡 Recommendations:")
                for rec in results['recommendations']:
                    print(f"  • {rec}")
                
                # Save results
                filename = f"api_discovery_{game_name.replace(' ', '_').lower()}.json"
                with open(filename, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"\n💾 Results saved to: {filename}")
        
        elif choice == "2":
            api_url = input("Enter API base URL: ").strip()
            if api_url:
                if not api_url.startswith("http"):
                    api_url = f"https://{api_url}"
                
                results = discovery.test_api_endpoints(api_url)
                
                print(f"\n📊 Endpoint Test Results:")
                print("=" * 30)
                print(f"Base URL: {results['base_url']}")
                print(f"Accessible: {len(results['accessible_endpoints'])}")
                print(f"Auth Required: {len(results['requires_auth'])}")
                print(f"Not Found: {len(results['not_found'])}")
                print(f"Errors: {len(results['errors'])}")
                
                if results['accessible_endpoints']:
                    print("\n✅ Accessible Endpoints:")
                    for ep in results['accessible_endpoints']:
                        print(f"  {ep['endpoint']} - {ep['status']}")
                
                if results['requires_auth']:
                    print("\n🔐 Authentication Required:")
                    for ep in results['requires_auth']:
                        print(f"  {ep['endpoint']} - {ep['status']}")
        
        elif choice == "3":
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
