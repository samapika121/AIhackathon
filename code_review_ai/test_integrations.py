#!/usr/bin/env python3
"""
Test script for Code Review AI integrations
"""

import os
import requests
import json

def test_api_integration():
    """Test the basic API functionality"""
    print("🧪 Testing API Integration...")
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:8001/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print("❌ Health check failed")
            return False
    except:
        print("❌ API server not running. Start with: python flask_main.py")
        return False
    
    # Test review endpoint
    test_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print("Hello World")  # This should trigger a warning
"""
    
    try:
        response = requests.post("http://localhost:8001/review", json={
            "code": test_code,
            "language": "python",
            "test_results": {"pass_rate": 0.8, "test_count": 3},
            "coverage_data": {"line_coverage": 0.75}
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Code review completed")
            print(f"   Score: {result['overall_score']}/100")
            print(f"   Issues: {len(result['issues'])}")
            print(f"   Suggestions: {len(result['suggestions'])}")
            return True
        else:
            print("❌ Code review failed")
            return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_github_integration():
    """Test GitHub integration setup"""
    print("\n🧪 Testing GitHub Integration...")
    
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token or github_token == "your_token":
        print("⚠️  GitHub token not set")
        print("   To test GitHub integration:")
        print("   1. Get token from: https://github.com/settings/tokens")
        print("   2. export GITHUB_TOKEN='your_actual_token'")
        print("   3. Run this test again")
        return False
    
    try:
        from integrations.github_integration import GitHubCodeReviewBot
        bot = GitHubCodeReviewBot(github_token)
        print("✅ GitHub bot initialized successfully")
        print("   Ready to review pull requests!")
        return True
    except Exception as e:
        print(f"❌ GitHub integration failed: {e}")
        return False

def test_ci_cd_integration():
    """Test CI/CD integration"""
    print("\n🧪 Testing CI/CD Integration...")
    
    try:
        from integrations.ci_cd_integration import CICDIntegration
        ci_integration = CICDIntegration()
        print(f"✅ CI/CD integration loaded")
        print(f"   Detected CI system: {ci_integration.ci_system}")
        return True
    except Exception as e:
        print(f"❌ CI/CD integration failed: {e}")
        return False

def show_usage_examples():
    """Show practical usage examples"""
    print("\n📚 Usage Examples:")
    print("="*50)
    
    print("\n1. 🚀 Start the API server:")
    print("   python flask_main.py")
    
    print("\n2. 🧪 Test code review:")
    print("   curl -X POST http://localhost:8001/review \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"code\":\"def hello(): return \\\"world\\\"\",\"language\":\"python\"}'")
    
    print("\n3. 🔗 GitHub PR review:")
    print("   export GITHUB_TOKEN='your_token'")
    print("   python integrations/github_integration.py")
    
    print("\n4. 🏗️ CI/CD pipeline:")
    print("   python integrations/ci_cd_integration.py --fail-threshold 70")
    
    print("\n5. 🐳 Docker deployment:")
    print("   python integrations/docker_deployment.py")
    print("   ./build.sh && ./deploy.sh development")

def main():
    """Run all integration tests"""
    print("🚀 Code Review AI - Integration Tests")
    print("="*50)
    
    results = []
    
    # Test API
    results.append(test_api_integration())
    
    # Test GitHub integration
    results.append(test_github_integration())
    
    # Test CI/CD integration  
    results.append(test_ci_cd_integration())
    
    # Show results
    print("\n📊 Test Results:")
    print("="*30)
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    if passed == total:
        print("🎉 All integrations working!")
    else:
        print("⚠️  Some integrations need setup")
    
    # Show usage examples
    show_usage_examples()

if __name__ == "__main__":
    main()
