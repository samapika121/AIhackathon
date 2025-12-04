#!/usr/bin/env python3
"""
Simple CI/CD Integration for Code Review AI
Works with the current Flask-based setup
"""

import os
import requests
import json
import glob
from pathlib import Path

def get_python_files():
    """Get all Python files in the current directory"""
    return glob.glob("**/*.py", recursive=True)

def review_file(file_path, api_url="http://localhost:8001"):
    """Review a single Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        response = requests.post(f"{api_url}/review", json={
            "code": code,
            "language": "python",
            "file_path": file_path
        }, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"API error: {response.status_code}",
                "overall_score": 0,
                "file_path": file_path
            }
    
    except Exception as e:
        return {
            "error": str(e),
            "overall_score": 0,
            "file_path": file_path
        }

def run_simple_ci_pipeline(fail_threshold=70, api_url="http://localhost:8001"):
    """Run a simple CI pipeline"""
    
    print("🚀 Simple CI/CD Code Review Pipeline")
    print("=" * 50)
    
    # Check if API is running
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Code Review API is not running")
            print(f"   Start it with: python3 flask_main.py")
            return False
    except:
        print("❌ Code Review API is not accessible")
        print(f"   Make sure it's running at: {api_url}")
        return False
    
    print("✅ Code Review API is running")
    
    # Get Python files to review
    python_files = get_python_files()
    
    if not python_files:
        print("⚠️  No Python files found to review")
        return True
    
    print(f"📁 Found {len(python_files)} Python files to review")
    
    # Review each file
    results = []
    total_score = 0
    
    for file_path in python_files:
        print(f"🔍 Reviewing: {file_path}")
        
        result = review_file(file_path, api_url)
        results.append(result)
        
        score = result.get('overall_score', 0)
        total_score += score
        
        # Show file result
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            issues = len(result.get('issues', []))
            if score >= 90:
                print(f"   ✅ Score: {score}/100 ({issues} issues)")
            elif score >= fail_threshold:
                print(f"   ⚠️  Score: {score}/100 ({issues} issues)")
            else:
                print(f"   ❌ Score: {score}/100 ({issues} issues)")
    
    # Calculate overall results
    if results:
        avg_score = total_score / len(results)
    else:
        avg_score = 0
    
    print("\n" + "=" * 50)
    print("📊 PIPELINE RESULTS")
    print("=" * 50)
    print(f"Files Reviewed: {len(results)}")
    print(f"Average Score: {avg_score:.1f}/100")
    print(f"Threshold: {fail_threshold}/100")
    
    # Determine pass/fail
    passed = avg_score >= fail_threshold
    
    if passed:
        print("✅ PIPELINE PASSED")
        print("🎉 Code quality meets requirements!")
    else:
        print("❌ PIPELINE FAILED")
        print(f"💡 Improve code quality to reach {fail_threshold}/100 threshold")
    
    # Show detailed results
    print("\n📋 Detailed Results:")
    for result in results:
        file_path = result.get('file_path', 'unknown')
        score = result.get('overall_score', 0)
        issues = len(result.get('issues', []))
        
        status = "✅" if score >= 90 else "⚠️" if score >= fail_threshold else "❌"
        print(f"  {status} {file_path}: {score}/100 ({issues} issues)")
    
    # Show top suggestions
    all_suggestions = []
    for result in results:
        all_suggestions.extend(result.get('suggestions', []))
    
    if all_suggestions:
        print("\n💡 Top Suggestions:")
        unique_suggestions = list(set(all_suggestions))[:5]
        for i, suggestion in enumerate(unique_suggestions, 1):
            print(f"  {i}. {suggestion}")
    
    return passed

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple CI/CD Code Review')
    parser.add_argument('--fail-threshold', type=float, default=70.0, 
                       help='Minimum score to pass (default: 70)')
    parser.add_argument('--api-url', default='http://localhost:8001',
                       help='Code Review API URL')
    
    args = parser.parse_args()
    
    # Run the pipeline
    success = run_simple_ci_pipeline(args.fail_threshold, args.api_url)
    
    # Exit with appropriate code
    exit(0 if success else 1)

if __name__ == "__main__":
    main()
