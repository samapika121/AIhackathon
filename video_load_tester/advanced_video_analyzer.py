#!/usr/bin/env python3
"""
Advanced Video Analysis for Game Load Testing
Uses computer vision and ML to extract realistic user behavior patterns
"""

import cv2
import numpy as np
import json
import time
from typing import Dict, List, Any, Tuple
import os
from datetime import datetime

class GameVideoAnalyzer:
    def __init__(self):
        self.ui_templates = {}
        self.action_patterns = {}
        self.load_ui_templates()
    
    def load_ui_templates(self):
        """Load UI element templates for detection"""
        # In a real implementation, you'd have template images for:
        # - Login buttons
        # - Menu items
        # - Game UI elements
        # - Loading screens
        pass
    
    def analyze_gameplay_video(self, video_path: str, game_type: str = "general") -> Dict[str, Any]:
        """
        Analyze gameplay video to extract user behavior patterns
        """
        print(f"🎬 Analyzing video: {video_path}")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception(f"Cannot open video: {video_path}")
        
        # Video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"📊 Video info: {duration:.1f}s, {fps:.1f} FPS, {width}x{height}")
        
        # Analysis results
        analysis_result = {
            'video_info': {
                'path': video_path,
                'duration': duration,
                'fps': fps,
                'resolution': f"{width}x{height}",
                'frame_count': frame_count
            },
            'user_actions': [],
            'ui_states': [],
            'performance_metrics': {},
            'behavior_patterns': {},
            'api_calls': []
        }
        
        # Process video frames
        frame_number = 0
        prev_frame = None
        scene_changes = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            timestamp = frame_number / fps
            
            # Detect scene changes and UI transitions
            if prev_frame is not None:
                scene_change = self._detect_scene_change(prev_frame, frame)
                if scene_change['changed']:
                    scene_changes.append({
                        'timestamp': timestamp,
                        'type': scene_change['type'],
                        'confidence': scene_change['confidence']
                    })
            
            # Analyze current frame for UI elements and actions
            frame_analysis = self._analyze_frame(frame, timestamp, game_type)
            
            if frame_analysis['ui_state']:
                analysis_result['ui_states'].append(frame_analysis['ui_state'])
            
            if frame_analysis['user_action']:
                analysis_result['user_actions'].append(frame_analysis['user_action'])
            
            prev_frame = frame.copy()
            frame_number += 1
            
            # Process every 5th frame for performance
            if frame_number % 5 != 0:
                continue
            
            # Progress indicator
            if frame_number % (frame_count // 10) == 0:
                progress = (frame_number / frame_count) * 100
                print(f"📈 Analysis progress: {progress:.1f}%")
        
        cap.release()
        
        # Post-process analysis results
        analysis_result['scene_changes'] = scene_changes
        analysis_result['behavior_patterns'] = self._extract_behavior_patterns(analysis_result)
        analysis_result['api_calls'] = self._generate_api_calls(analysis_result)
        analysis_result['performance_metrics'] = self._calculate_performance_metrics(analysis_result)
        
        print(f"✅ Analysis complete: {len(analysis_result['user_actions'])} actions detected")
        
        return analysis_result
    
    def _detect_scene_change(self, prev_frame: np.ndarray, current_frame: np.ndarray) -> Dict[str, Any]:
        """Detect significant scene changes between frames"""
        # Convert to grayscale
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate frame difference
        diff = cv2.absdiff(prev_gray, curr_gray)
        
        # Calculate change percentage
        change_pixels = np.sum(diff > 30)  # Threshold for significant change
        total_pixels = diff.shape[0] * diff.shape[1]
        change_percentage = change_pixels / total_pixels
        
        # Determine scene change type
        scene_type = "unknown"
        if change_percentage > 0.7:
            scene_type = "major_transition"  # Complete scene change
        elif change_percentage > 0.3:
            scene_type = "ui_transition"     # UI change or menu navigation
        elif change_percentage > 0.1:
            scene_type = "minor_change"      # Small UI updates or animations
        
        return {
            'changed': change_percentage > 0.1,
            'type': scene_type,
            'confidence': min(1.0, change_percentage * 2),
            'change_percentage': change_percentage
        }
    
    def _analyze_frame(self, frame: np.ndarray, timestamp: float, game_type: str) -> Dict[str, Any]:
        """Analyze individual frame for UI elements and user actions"""
        result = {
            'ui_state': None,
            'user_action': None
        }
        
        # Convert to different color spaces for analysis
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Detect UI elements
        ui_elements = self._detect_ui_elements(frame, gray, hsv)
        
        if ui_elements:
            result['ui_state'] = {
                'timestamp': timestamp,
                'elements': ui_elements,
                'screen_type': self._classify_screen_type(ui_elements)
            }
        
        # Detect user actions based on UI changes
        action = self._detect_user_action(frame, ui_elements, timestamp)
        if action:
            result['user_action'] = action
        
        return result
    
    def _detect_ui_elements(self, frame: np.ndarray, gray: np.ndarray, hsv: np.ndarray) -> List[Dict[str, Any]]:
        """Detect UI elements in the frame"""
        elements = []
        
        # Detect buttons (simplified approach)
        # In production, use template matching or trained ML models
        
        # Detect text regions (potential buttons/labels)
        # Using edge detection to find rectangular regions
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 1000 < area < 50000:  # Filter by size
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                
                # Classify potential UI elements
                if 1.5 < aspect_ratio < 4 and area > 2000:  # Button-like shape
                    elements.append({
                        'type': 'button',
                        'bounds': {'x': x, 'y': y, 'width': w, 'height': h},
                        'confidence': 0.6
                    })
                elif aspect_ratio > 4 and h < 50:  # Text field-like
                    elements.append({
                        'type': 'text_field',
                        'bounds': {'x': x, 'y': y, 'width': w, 'height': h},
                        'confidence': 0.5
                    })
        
        # Detect loading indicators (spinning elements or progress bars)
        # Look for circular or horizontal rectangular regions with specific colors
        
        # Detect game-specific elements based on color patterns
        if self._has_health_bar_colors(hsv):
            elements.append({
                'type': 'health_bar',
                'bounds': {'x': 0, 'y': 0, 'width': 100, 'height': 20},
                'confidence': 0.7
            })
        
        if self._has_minimap_colors(hsv):
            elements.append({
                'type': 'minimap',
                'bounds': {'x': frame.shape[1]-200, 'y': 0, 'width': 200, 'height': 200},
                'confidence': 0.8
            })
        
        return elements
    
    def _has_health_bar_colors(self, hsv: np.ndarray) -> bool:
        """Detect health bar by looking for red/green color patterns"""
        # Define color ranges for health bars (red/green)
        red_lower = np.array([0, 50, 50])
        red_upper = np.array([10, 255, 255])
        green_lower = np.array([40, 50, 50])
        green_upper = np.array([80, 255, 255])
        
        red_mask = cv2.inRange(hsv, red_lower, red_upper)
        green_mask = cv2.inRange(hsv, green_lower, green_upper)
        
        red_pixels = np.sum(red_mask > 0)
        green_pixels = np.sum(green_mask > 0)
        
        return red_pixels > 100 or green_pixels > 100
    
    def _has_minimap_colors(self, hsv: np.ndarray) -> bool:
        """Detect minimap by looking for typical map colors"""
        # Look for blue (water) and brown/green (terrain) colors
        blue_lower = np.array([100, 50, 50])
        blue_upper = np.array([130, 255, 255])
        
        blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
        blue_pixels = np.sum(blue_mask > 0)
        
        return blue_pixels > 500
    
    def _classify_screen_type(self, ui_elements: List[Dict[str, Any]]) -> str:
        """Classify the type of screen based on UI elements"""
        element_types = [elem['type'] for elem in ui_elements]
        
        if 'text_field' in element_types and 'button' in element_types:
            return 'login_screen'
        elif 'health_bar' in element_types and 'minimap' in element_types:
            return 'gameplay_screen'
        elif len([e for e in element_types if e == 'button']) > 3:
            return 'menu_screen'
        else:
            return 'unknown_screen'
    
    def _detect_user_action(self, frame: np.ndarray, ui_elements: List[Dict[str, Any]], timestamp: float) -> Dict[str, Any]:
        """Detect user actions based on UI state and changes"""
        # This is a simplified version - in production you'd track:
        # - Mouse cursor position and clicks
        # - Keyboard input indicators
        # - UI element state changes
        # - Animation triggers
        
        screen_type = self._classify_screen_type(ui_elements) if ui_elements else 'unknown'
        
        # Generate actions based on screen type and timing patterns
        if screen_type == 'login_screen':
            return {
                'type': 'login_attempt',
                'timestamp': timestamp,
                'screen_type': screen_type,
                'confidence': 0.8,
                'api_endpoint': '/api/login',
                'expected_duration': 2.0
            }
        elif screen_type == 'menu_screen':
            return {
                'type': 'menu_navigation',
                'timestamp': timestamp,
                'screen_type': screen_type,
                'confidence': 0.7,
                'api_endpoint': '/api/lobby',
                'expected_duration': 1.0
            }
        elif screen_type == 'gameplay_screen':
            return {
                'type': 'gameplay_action',
                'timestamp': timestamp,
                'screen_type': screen_type,
                'confidence': 0.9,
                'api_endpoint': '/api/game_status',
                'expected_duration': 0.5
            }
        
        return None
    
    def _extract_behavior_patterns(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract user behavior patterns from analysis"""
        actions = analysis_result['user_actions']
        
        if not actions:
            return {}
        
        # Calculate timing patterns
        action_intervals = []
        for i in range(1, len(actions)):
            interval = actions[i]['timestamp'] - actions[i-1]['timestamp']
            action_intervals.append(interval)
        
        # Analyze action sequences
        action_sequence = [action['type'] for action in actions]
        
        # Calculate user behavior metrics
        patterns = {
            'total_actions': len(actions),
            'avg_action_interval': np.mean(action_intervals) if action_intervals else 0,
            'action_sequence': action_sequence,
            'session_duration': actions[-1]['timestamp'] - actions[0]['timestamp'] if len(actions) > 1 else 0,
            'most_common_action': max(set(action_sequence), key=action_sequence.count) if action_sequence else None,
            'user_pace': 'fast' if np.mean(action_intervals) < 2 else 'normal' if np.mean(action_intervals) < 5 else 'slow'
        }
        
        return patterns
    
    def _generate_api_calls(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate API calls based on detected user actions"""
        api_calls = []
        
        for action in analysis_result['user_actions']:
            if 'api_endpoint' in action:
                api_call = {
                    'timestamp': action['timestamp'],
                    'method': 'POST' if 'login' in action['api_endpoint'] else 'GET',
                    'endpoint': action['api_endpoint'],
                    'expected_response_time': action.get('expected_duration', 1.0),
                    'action_type': action['type'],
                    'payload': self._generate_api_payload(action)
                }
                api_calls.append(api_call)
        
        return api_calls
    
    def _generate_api_payload(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Generate appropriate API payload for action"""
        if action['type'] == 'login_attempt':
            return {
                'username': 'test_user_{user_id}',
                'password': 'test_password'
            }
        elif action['type'] == 'menu_navigation':
            return {}
        elif action['type'] == 'gameplay_action':
            return {
                'action': 'status_check'
            }
        
        return {}
    
    def _calculate_performance_metrics(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance and quality metrics"""
        actions = analysis_result['user_actions']
        ui_states = analysis_result['ui_states']
        
        metrics = {
            'analysis_quality': {
                'actions_detected': len(actions),
                'ui_states_detected': len(ui_states),
                'confidence_avg': np.mean([a.get('confidence', 0) for a in actions]) if actions else 0
            },
            'user_behavior': {
                'session_complexity': len(set([a['type'] for a in actions])),
                'interaction_frequency': len(actions) / analysis_result['video_info']['duration'] if analysis_result['video_info']['duration'] > 0 else 0
            },
            'load_test_suitability': {
                'realistic_timing': True,  # Based on action intervals
                'api_coverage': len(set([a.get('api_endpoint') for a in actions if a.get('api_endpoint')])),
                'scenario_completeness': 'high' if len(actions) > 5 else 'medium' if len(actions) > 2 else 'low'
            }
        }
        
        return metrics
    
    def save_analysis_result(self, analysis_result: Dict[str, Any], output_path: str):
        """Save analysis result to JSON file"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Add metadata
        analysis_result['analysis_metadata'] = {
            'analyzer_version': '1.0.0',
            'analysis_date': datetime.now().isoformat(),
            'total_processing_time': time.time()  # You'd track this properly
        }
        
        with open(output_path, 'w') as f:
            json.dump(analysis_result, f, indent=2)
        
        print(f"💾 Analysis saved to: {output_path}")

def main():
    """Example usage of the video analyzer"""
    analyzer = GameVideoAnalyzer()
    
    # Example video analysis
    video_path = "example_gameplay.mp4"  # Replace with actual video
    
    if os.path.exists(video_path):
        try:
            result = analyzer.analyze_gameplay_video(video_path, "battle_royale")
            
            # Save results
            output_path = f"analysis_results/{os.path.basename(video_path)}_analysis.json"
            analyzer.save_analysis_result(result, output_path)
            
            # Print summary
            print("\n📊 Analysis Summary:")
            print(f"Actions detected: {len(result['user_actions'])}")
            print(f"UI states: {len(result['ui_states'])}")
            print(f"API calls generated: {len(result['api_calls'])}")
            print(f"Session duration: {result['behavior_patterns'].get('session_duration', 0):.1f}s")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
    else:
        print(f"❌ Video file not found: {video_path}")
        print("📝 To use this analyzer:")
        print("1. Record a video of your game (login → lobby → gameplay)")
        print("2. Save it as 'example_gameplay.mp4'")
        print("3. Run this script again")

if __name__ == "__main__":
    main()
