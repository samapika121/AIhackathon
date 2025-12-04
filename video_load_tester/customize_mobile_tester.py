#!/usr/bin/env python3
"""
Mobile Game Tester Customization Tool
Customize the load tester for your specific mobile game
"""

import json
import os
from typing import Dict, List, Any

class MobileGameCustomizer:
    def __init__(self):
        self.custom_scenarios = {}
        self.custom_headers = {}
        self.custom_auth = {}
    
    def create_custom_scenario(self, game_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create a custom scenario for a specific mobile game"""
        
        print(f"🎮 Creating custom scenario for: {game_info['game_name']}")
        
        scenario = {
            'name': f"{game_info['game_name']} - Custom Flow",
            'description': f"Custom load test scenario for {game_info['game_name']}",
            'game_info': game_info,
            'actions': []
        }
        
        # Build actions based on game type
        game_type = game_info.get('game_type', 'general')
        
        if game_type == 'battle_royale':
            scenario['actions'] = self._create_battle_royale_actions(game_info)
        elif game_type == 'puzzle':
            scenario['actions'] = self._create_puzzle_game_actions(game_info)
        elif game_type == 'social':
            scenario['actions'] = self._create_social_game_actions(game_info)
        elif game_type == 'rpg':
            scenario['actions'] = self._create_rpg_actions(game_info)
        else:
            scenario['actions'] = self._create_general_actions(game_info)
        
        return scenario
    
    def _create_battle_royale_actions(self, game_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Actions for battle royale games"""
        base_url = game_info['api_base_url']
        
        return [
            {
                'name': 'Player Authentication',
                'method': 'POST',
                'endpoint': '/api/v1/auth/login',
                'delay': 2.0,
                'payload': {
                    'username': 'player_{user_id}',
                    'password': 'test_password',
                    'device_id': '{device_id}',
                    'platform': game_info.get('platform', 'iOS')
                }
            },
            {
                'name': 'Load Player Loadout',
                'method': 'GET',
                'endpoint': '/api/v1/player/loadout',
                'delay': 1.5,
                'headers': {'Authorization': 'Bearer {auth_token}'}
            },
            {
                'name': 'Join Matchmaking Queue',
                'method': 'POST',
                'endpoint': '/api/v1/matchmaking/join',
                'delay': 3.0,
                'payload': {
                    'game_mode': 'solo',
                    'region': 'us-east'
                }
            },
            {
                'name': 'Game Session Start',
                'method': 'POST',
                'endpoint': '/api/v1/game/session/start',
                'delay': 2.0,
                'payload': {
                    'match_id': '{match_id}',
                    'spawn_location': {'x': 100, 'y': 200}
                }
            },
            {
                'name': 'Player Movement',
                'method': 'POST',
                'endpoint': '/api/v1/game/action/move',
                'delay': 0.5,
                'payload': {
                    'position': {'x': 150, 'y': 250},
                    'timestamp': '{timestamp}'
                }
            },
            {
                'name': 'Player Combat Action',
                'method': 'POST',
                'endpoint': '/api/v1/game/action/combat',
                'delay': 0.3,
                'payload': {
                    'action_type': 'shoot',
                    'target_position': {'x': 200, 'y': 300}
                }
            },
            {
                'name': 'Game Session End',
                'method': 'POST',
                'endpoint': '/api/v1/game/session/end',
                'delay': 1.0,
                'payload': {
                    'final_position': 5,
                    'kills': 2,
                    'damage_dealt': 450
                }
            }
        ]
    
    def _create_puzzle_game_actions(self, game_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Actions for puzzle games"""
        return [
            {
                'name': 'Player Login',
                'method': 'POST',
                'endpoint': '/api/v1/auth/login',
                'delay': 2.0,
                'payload': {
                    'user_id': 'puzzle_player_{user_id}',
                    'device_id': '{device_id}'
                }
            },
            {
                'name': 'Load Current Level',
                'method': 'GET',
                'endpoint': '/api/v1/levels/current',
                'delay': 1.0
            },
            {
                'name': 'Start Level',
                'method': 'POST',
                'endpoint': '/api/v1/game/level/start',
                'delay': 1.5,
                'payload': {
                    'level_id': '{current_level}',
                    'boosts_used': []
                }
            },
            {
                'name': 'Make Move',
                'method': 'POST',
                'endpoint': '/api/v1/game/move',
                'delay': 0.8,
                'payload': {
                    'move_type': 'swap',
                    'from_position': {'row': 2, 'col': 3},
                    'to_position': {'row': 2, 'col': 4}
                }
            },
            {
                'name': 'Complete Level',
                'method': 'POST',
                'endpoint': '/api/v1/game/level/complete',
                'delay': 2.0,
                'payload': {
                    'score': 15000,
                    'moves_used': 25,
                    'stars_earned': 3
                }
            }
        ]
    
    def _create_social_game_actions(self, game_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Actions for social games"""
        return [
            {
                'name': 'Social Login',
                'method': 'POST',
                'endpoint': '/api/v1/auth/facebook',
                'delay': 3.0,
                'payload': {
                    'facebook_token': 'mock_fb_token_{user_id}',
                    'device_id': '{device_id}'
                }
            },
            {
                'name': 'Load Friends List',
                'method': 'GET',
                'endpoint': '/api/v1/social/friends',
                'delay': 1.5
            },
            {
                'name': 'Send Daily Gift',
                'method': 'POST',
                'endpoint': '/api/v1/social/gifts/send',
                'delay': 1.0,
                'payload': {
                    'friend_ids': ['friend_1', 'friend_2'],
                    'gift_type': 'energy'
                }
            },
            {
                'name': 'Visit Friend Farm',
                'method': 'POST',
                'endpoint': '/api/v1/social/visit',
                'delay': 2.0,
                'payload': {
                    'friend_id': 'friend_1',
                    'action': 'help_crops'
                }
            },
            {
                'name': 'Share Achievement',
                'method': 'POST',
                'endpoint': '/api/v1/social/share',
                'delay': 1.5,
                'payload': {
                    'achievement_type': 'level_up',
                    'level': 25
                }
            }
        ]
    
    def _create_rpg_actions(self, game_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Actions for RPG games"""
        return [
            {
                'name': 'Character Login',
                'method': 'POST',
                'endpoint': '/api/v1/auth/character',
                'delay': 2.5,
                'payload': {
                    'character_id': 'char_{user_id}',
                    'device_id': '{device_id}'
                }
            },
            {
                'name': 'Load Character Stats',
                'method': 'GET',
                'endpoint': '/api/v1/character/stats',
                'delay': 1.0
            },
            {
                'name': 'Enter Dungeon',
                'method': 'POST',
                'endpoint': '/api/v1/dungeon/enter',
                'delay': 2.0,
                'payload': {
                    'dungeon_id': 'forest_temple',
                    'difficulty': 'normal'
                }
            },
            {
                'name': 'Combat Action',
                'method': 'POST',
                'endpoint': '/api/v1/combat/action',
                'delay': 1.0,
                'payload': {
                    'skill_id': 'fireball',
                    'target_id': 'monster_1'
                }
            },
            {
                'name': 'Loot Collection',
                'method': 'POST',
                'endpoint': '/api/v1/loot/collect',
                'delay': 0.5,
                'payload': {
                    'items': ['gold_coin', 'health_potion']
                }
            },
            {
                'name': 'Exit Dungeon',
                'method': 'POST',
                'endpoint': '/api/v1/dungeon/exit',
                'delay': 1.5,
                'payload': {
                    'experience_gained': 150,
                    'gold_earned': 75
                }
            }
        ]
    
    def _create_general_actions(self, game_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """General actions for any mobile game"""
        return [
            {
                'name': 'App Launch',
                'method': 'POST',
                'endpoint': '/api/v1/app/launch',
                'delay': 2.0,
                'payload': {
                    'device_id': '{device_id}',
                    'app_version': game_info.get('app_version', '1.0.0')
                }
            },
            {
                'name': 'User Authentication',
                'method': 'POST',
                'endpoint': '/api/v1/auth/login',
                'delay': 2.5,
                'payload': {
                    'username': 'user_{user_id}',
                    'password': 'test_password'
                }
            },
            {
                'name': 'Load Game Data',
                'method': 'GET',
                'endpoint': '/api/v1/game/data',
                'delay': 1.5
            },
            {
                'name': 'Game Action',
                'method': 'POST',
                'endpoint': '/api/v1/game/action',
                'delay': 1.0,
                'payload': {
                    'action_type': 'tap',
                    'coordinates': {'x': 100, 'y': 200}
                }
            }
        ]
    
    def create_custom_headers(self, game_info: Dict[str, Any]) -> Dict[str, str]:
        """Create custom headers for the specific game"""
        headers = {
            'User-Agent': f"{game_info['game_name']}/{game_info.get('app_version', '1.0.0')} (iPhone; iOS 15.0; Scale/3.00)",
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Platform': game_info.get('platform', 'iOS'),
            'X-App-Version': game_info.get('app_version', '1.0.0'),
            'X-Game-ID': game_info.get('game_id', 'unknown')
        }
        
        # Add custom headers if specified
        if 'custom_headers' in game_info:
            headers.update(game_info['custom_headers'])
        
        return headers
    
    def save_custom_configuration(self, game_info: Dict[str, Any], filename: str = None):
        """Save custom configuration to file"""
        if not filename:
            game_name = game_info['game_name'].replace(' ', '_').lower()
            filename = f"custom_{game_name}_config.json"
        
        scenario = self.create_custom_scenario(game_info)
        headers = self.create_custom_headers(game_info)
        
        config = {
            'game_info': game_info,
            'scenario': scenario,
            'headers': headers,
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Custom configuration saved to: {filename}")
        return filename

def interactive_customization():
    """Interactive tool to create custom mobile game configuration"""
    print("🎮 Mobile Game Customization Tool")
    print("=" * 50)
    
    customizer = MobileGameCustomizer()
    
    # Collect game information
    game_info = {}
    
    game_info['game_name'] = input("Enter your game name: ").strip()
    game_info['api_base_url'] = input("Enter API base URL (e.g., https://api.yourgame.com): ").strip()
    
    print("\nGame Types:")
    print("1. Battle Royale")
    print("2. Puzzle Game") 
    print("3. Social Game")
    print("4. RPG")
    print("5. General")
    
    game_type_choice = input("Select game type (1-5): ").strip()
    game_types = {
        '1': 'battle_royale',
        '2': 'puzzle', 
        '3': 'social',
        '4': 'rpg',
        '5': 'general'
    }
    game_info['game_type'] = game_types.get(game_type_choice, 'general')
    
    game_info['app_version'] = input("Enter app version (default: 1.0.0): ").strip() or "1.0.0"
    game_info['platform'] = input("Enter platform (iOS/Android/Mixed, default: iOS): ").strip() or "iOS"
    
    # Optional custom headers
    print("\nAdd custom headers? (y/n): ", end="")
    if input().lower() == 'y':
        game_info['custom_headers'] = {}
        while True:
            header_name = input("Header name (or press Enter to finish): ").strip()
            if not header_name:
                break
            header_value = input(f"Value for {header_name}: ").strip()
            game_info['custom_headers'][header_name] = header_value
    
    # Generate and save configuration
    filename = customizer.save_custom_configuration(game_info)
    
    print(f"\n🎯 Custom configuration created!")
    print(f"📁 File: {filename}")
    print(f"🎮 Game: {game_info['game_name']}")
    print(f"🔗 API: {game_info['api_base_url']}")
    print(f"📱 Type: {game_info['game_type']}")
    
    print(f"\n📖 How to use:")
    print(f"1. Copy {filename} to your load tester directory")
    print(f"2. Modify mobile_app_tester.py to use this configuration")
    print(f"3. Run load tests with your custom scenario")

if __name__ == "__main__":
    import time
    interactive_customization()
