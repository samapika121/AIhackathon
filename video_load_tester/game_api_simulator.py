#!/usr/bin/env python3
"""
Game API Simulator
Simulates a real game backend for testing the load tester
"""

from flask import Flask, request, jsonify
import time
import random
import threading
from datetime import datetime

app = Flask(__name__)

# Simulate game state
game_state = {
    'active_users': 0,
    'lobby_users': 0,
    'in_game_users': 0,
    'server_load': 0.0
}

# User sessions
user_sessions = {}

@app.route('/')
def home():
    return jsonify({
        'message': 'Game API Simulator - Ready for Load Testing! 🎮',
        'endpoints': [
            'POST /api/login - User login',
            'GET /api/lobby - Get lobby info',
            'POST /api/join_game - Join game session',
            'GET /api/game_status - Get game status',
            'POST /api/logout - User logout',
            'GET /api/server_stats - Server statistics'
        ],
        'current_stats': game_state
    })

@app.route('/api/login', methods=['POST'])
def login():
    """Simulate user login"""
    try:
        data = request.get_json() or {}
        username = data.get('username', f'user_{random.randint(1000, 9999)}')
        password = data.get('password', 'password')
        
        # Simulate authentication delay
        time.sleep(random.uniform(0.1, 0.5))
        
        # Simulate occasional login failures
        if random.random() < 0.05:  # 5% failure rate
            return jsonify({
                'success': False,
                'error': 'Invalid credentials'
            }), 401
        
        # Create user session
        session_id = f'session_{int(time.time())}_{random.randint(1000, 9999)}'
        user_sessions[session_id] = {
            'username': username,
            'login_time': datetime.now().isoformat(),
            'status': 'logged_in'
        }
        
        # Update game state
        game_state['active_users'] += 1
        game_state['server_load'] = min(1.0, game_state['active_users'] / 1000)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'username': username,
            'server_time': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/lobby', methods=['GET'])
def lobby():
    """Simulate lobby/matchmaking"""
    try:
        # Simulate lobby loading time
        time.sleep(random.uniform(0.2, 0.8))
        
        # Simulate occasional server overload
        if game_state['server_load'] > 0.8 and random.random() < 0.1:
            return jsonify({
                'success': False,
                'error': 'Server overloaded, please try again'
            }), 503
        
        # Update lobby users
        game_state['lobby_users'] = min(game_state['active_users'], 
                                       game_state['lobby_users'] + random.randint(-5, 10))
        
        # Simulate available games
        available_games = []
        for i in range(random.randint(3, 8)):
            available_games.append({
                'game_id': f'game_{i+1}',
                'players': random.randint(1, 10),
                'max_players': 10,
                'map': f'Map_{random.choice(["Alpha", "Beta", "Gamma", "Delta"])}',
                'mode': random.choice(['Battle Royale', 'Team Deathmatch', 'Capture Flag'])
            })
        
        return jsonify({
            'success': True,
            'lobby_info': {
                'online_players': game_state['active_users'],
                'lobby_players': game_state['lobby_users'],
                'server_load': game_state['server_load'],
                'available_games': available_games
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/join_game', methods=['POST'])
def join_game():
    """Simulate joining a game"""
    try:
        data = request.get_json() or {}
        game_id = data.get('game_id', 'game_1')
        
        # Simulate matchmaking time
        time.sleep(random.uniform(1.0, 3.0))
        
        # Simulate game full or connection issues
        if random.random() < 0.15:  # 15% failure rate
            return jsonify({
                'success': False,
                'error': random.choice([
                    'Game is full',
                    'Connection timeout',
                    'Matchmaking failed'
                ])
            }), 400
        
        # Update game state
        game_state['in_game_users'] += 1
        game_state['lobby_users'] = max(0, game_state['lobby_users'] - 1)
        
        return jsonify({
            'success': True,
            'game_session': {
                'game_id': game_id,
                'session_id': f'game_session_{int(time.time())}',
                'server_ip': f'192.168.1.{random.randint(10, 100)}',
                'port': random.randint(7000, 8000),
                'players_in_game': random.randint(5, 10)
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/game_status', methods=['GET'])
def game_status():
    """Get current game status"""
    try:
        # Simulate status check delay
        time.sleep(random.uniform(0.1, 0.3))
        
        return jsonify({
            'success': True,
            'game_status': {
                'status': random.choice(['waiting', 'in_progress', 'ending']),
                'players_alive': random.randint(1, 10),
                'time_remaining': random.randint(60, 300),
                'your_stats': {
                    'kills': random.randint(0, 5),
                    'deaths': random.randint(0, 3),
                    'score': random.randint(100, 1000)
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """Simulate user logout"""
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id')
        
        if session_id in user_sessions:
            del user_sessions[session_id]
        
        # Update game state
        game_state['active_users'] = max(0, game_state['active_users'] - 1)
        game_state['server_load'] = max(0.0, game_state['active_users'] / 1000)
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/server_stats', methods=['GET'])
def server_stats():
    """Get server statistics"""
    return jsonify({
        'success': True,
        'server_stats': {
            'active_users': game_state['active_users'],
            'lobby_users': game_state['lobby_users'],
            'in_game_users': game_state['in_game_users'],
            'server_load': game_state['server_load'],
            'uptime': '2 days, 14 hours',
            'memory_usage': f"{random.randint(60, 85)}%",
            'cpu_usage': f"{random.randint(30, 70)}%"
        }
    })

def simulate_background_activity():
    """Simulate background server activity"""
    while True:
        time.sleep(10)  # Update every 10 seconds
        
        # Simulate natural user fluctuation
        change = random.randint(-2, 3)
        game_state['active_users'] = max(0, game_state['active_users'] + change)
        
        # Update server load
        game_state['server_load'] = min(1.0, game_state['active_users'] / 1000)
        
        # Clean up old sessions (simulate session timeout)
        current_time = time.time()
        expired_sessions = []
        for session_id, session_data in user_sessions.items():
            # Sessions expire after 1 hour of inactivity
            if current_time - int(session_id.split('_')[1]) > 3600:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del user_sessions[session_id]

if __name__ == '__main__':
    print("🎮 Starting Game API Simulator...")
    print("🌐 API available at: http://localhost:3000")
    print("📊 Use this as target URL in the load tester")
    
    # Start background activity simulation
    bg_thread = threading.Thread(target=simulate_background_activity)
    bg_thread.daemon = True
    bg_thread.start()
    
    app.run(host='0.0.0.0', port=3000, debug=True)
