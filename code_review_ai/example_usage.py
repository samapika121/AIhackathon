#!/usr/bin/env python3
"""
Example usage of the Multi-modal Code Review AI
"""

import json
import asyncio
from main import app
from static_analyzer import StaticCodeAnalyzer
from test_analyzer import TestResultAnalyzer
from coverage_analyzer import CoverageAnalyzer
from comment_analyzer import CommentAnalyzer
from ai_reviewer import AIReviewer

# Sample code for testing
SAMPLE_CODE = '''
def calculate_fibonacci(n):
    """Calculate fibonacci number"""
    if n <= 1:
        return n
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

def process_data(data):
    # TODO: Add input validation
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result

class DataProcessor:
    def __init__(self):
        self.data = []
    
    def add_data(self, item):
        self.data.append(item)
    
    def get_average(self):
        return sum(self.data) / len(self.data)  # FIXME: Handle division by zero
'''

# Sample test results
SAMPLE_TEST_RESULTS = {
    "tests": [
        {
            "nodeid": "test_fibonacci.py::test_fibonacci_base_case",
            "outcome": "passed",
            "call": {"duration": 0.001}
        },
        {
            "nodeid": "test_fibonacci.py::test_fibonacci_recursive",
            "outcome": "passed", 
            "call": {"duration": 0.005}
        },
        {
            "nodeid": "test_data_processor.py::test_process_data",
            "outcome": "failed",
            "call": {
                "duration": 0.002,
                "longrepr": "AssertionError: Expected [2, 4] but got [2, 4, 6]"
            }
        }
    ],
    "summary": {"duration": 0.008}
}

# Sample coverage data
SAMPLE_COVERAGE = {
    "files": {
        "main.py": {
            "executed_lines": [1, 2, 3, 5, 6, 8, 9],
            "missing_lines": [4, 7, 10, 11, 12]
        }
    }
}

# Sample developer comments
SAMPLE_COMMENTS = [
    "This function needs optimization - it's too slow for large inputs",
    "TODO: Implement caching for fibonacci calculation",
    "Great implementation of the data processor class!",
    "FIXME: The get_average method will crash with empty data",
    "Consider adding input validation to prevent errors"
]

async def demo_individual_analyzers():
    """Demonstrate individual analyzer capabilities"""
    print("="*60)
    print("INDIVIDUAL ANALYZER DEMONSTRATIONS")
    print("="*60)
    
    # Static Analysis
    print("\n1. STATIC CODE ANALYSIS")
    print("-" * 30)
    static_analyzer = StaticCodeAnalyzer()
    static_results = static_analyzer.analyze(SAMPLE_CODE, "python")
    
    print(f"Complexity Score: {static_results['complexity_score']}")
    print(f"Error Count: {static_results['error_count']}")
    print(f"Warning Count: {static_results['warning_count']}")
    print(f"Issues Found: {len(static_results['issues'])}")
    
    for issue in static_results['issues'][:3]:  # Show first 3 issues
        print(f"  - {issue['severity'].upper()}: {issue['message']}")
    
    # Test Analysis
    print("\n2. TEST RESULT ANALYSIS")
    print("-" * 30)
    test_analyzer = TestResultAnalyzer()
    test_results = test_analyzer.analyze(SAMPLE_TEST_RESULTS)
    
    print(f"Test Count: {test_results['test_count']}")
    print(f"Pass Rate: {test_results['pass_rate']:.1%}")
    print(f"Quality Score: {test_results['test_quality_score']}")
    print(f"Failed Tests: {len(test_results['failed_tests'])}")
    
    # Coverage Analysis
    print("\n3. COVERAGE ANALYSIS")
    print("-" * 30)
    coverage_analyzer = CoverageAnalyzer()
    coverage_results = coverage_analyzer.analyze(SAMPLE_COVERAGE)
    
    print(f"Line Coverage: {coverage_results['line_coverage']:.1%}")
    print(f"Uncovered Lines: {len(coverage_results['uncovered_lines'])}")
    print(f"Issues: {len(coverage_results['issues'])}")
    
    # Comment Analysis
    print("\n4. COMMENT ANALYSIS")
    print("-" * 30)
    comment_analyzer = CommentAnalyzer()
    comment_results = comment_analyzer.analyze(SAMPLE_COMMENTS)
    
    print(f"Total Comments: {comment_results['total_comments']}")
    print(f"Quality Score: {comment_results['quality_score']:.1f}")
    print(f"TODO Items: {comment_results['comment_types']['todo']}")
    print(f"Positive Sentiment: {comment_results['sentiment_analysis']['positive']}")
    print(f"Action Items: {len(comment_results['action_items'])}")

async def demo_ai_reviewer():
    """Demonstrate AI reviewer capabilities"""
    print("\n" + "="*60)
    print("AI-POWERED COMPREHENSIVE REVIEW")
    print("="*60)
    
    # Run all analyzers
    static_analyzer = StaticCodeAnalyzer()
    test_analyzer = TestResultAnalyzer()
    coverage_analyzer = CoverageAnalyzer()
    comment_analyzer = CommentAnalyzer()
    ai_reviewer = AIReviewer()
    
    # Get results from all analyzers
    static_results = static_analyzer.analyze(SAMPLE_CODE, "python")
    test_results = test_analyzer.analyze(SAMPLE_TEST_RESULTS)
    coverage_results = coverage_analyzer.analyze(SAMPLE_COVERAGE)
    comment_results = comment_analyzer.analyze(SAMPLE_COMMENTS)
    
    # Combine data for AI analysis
    combined_data = {
        'code': SAMPLE_CODE,
        'language': 'python',
        'static_analysis': static_results,
        'test_analysis': test_results,
        'coverage_analysis': coverage_results,
        'comment_analysis': comment_results
    }
    
    # Generate AI insights
    ai_insights = ai_reviewer.generate_insights(combined_data)
    
    print(f"\nCODE HEALTH SCORE: {ai_insights['code_health_score']:.1f}/100")
    print(f"RISK LEVEL: {ai_insights['risk_assessment'].get('risk_level', 'unknown').upper()}")
    
    print(f"\nSUMMARY:")
    print(f"  {ai_insights['summary']}")
    
    print(f"\nKEY INSIGHTS:")
    for insight in ai_insights['insights'][:5]:
        print(f"  • {insight}")
    
    print(f"\nTOP RECOMMENDATIONS:")
    for i, suggestion in enumerate(ai_insights['suggestions'][:5], 1):
        print(f"  {i}. {suggestion}")
    
    print(f"\nPRIORITY ISSUES ({len(ai_insights['priority_issues'])}):")
    for issue_data in ai_insights['priority_issues'][:3]:
        issue = issue_data['issue']
        print(f"  • {issue['severity'].upper()}: {issue['message']}")
    
    if ai_insights['improvement_roadmap']:
        print(f"\nIMPROVEMENT ROADMAP:")
        for phase in ai_insights['improvement_roadmap']:
            print(f"  Phase {phase['phase']}: {phase['title']}")
            print(f"    {phase['description']}")
            print(f"    Effort: {phase['estimated_effort']}, Timeline: {phase['timeline']}")

async def demo_api_usage():
    """Demonstrate API usage"""
    print("\n" + "="*60)
    print("API USAGE DEMONSTRATION")
    print("="*60)
    
    # This would be used with the FastAPI server running
    sample_request = {
        "code": SAMPLE_CODE,
        "language": "python",
        "test_results": SAMPLE_TEST_RESULTS,
        "coverage_data": SAMPLE_COVERAGE,
        "developer_comments": SAMPLE_COMMENTS,
        "file_path": "example.py"
    }
    
    print("Sample API Request:")
    print(json.dumps(sample_request, indent=2)[:500] + "...")
    
    print("\nTo use the API:")
    print("1. Start the server: python main.py")
    print("2. Send POST request to http://localhost:8001/review")
    print("3. Include code, test results, coverage data, and comments")
    print("4. Receive comprehensive analysis and recommendations")

def demo_real_world_scenarios():
    """Demonstrate real-world usage scenarios"""
    print("\n" + "="*60)
    print("REAL-WORLD USAGE SCENARIOS")
    print("="*60)
    
    scenarios = [
        {
            "name": "Pre-commit Review",
            "description": "Analyze code before committing to catch issues early",
            "use_case": "Run static analysis and check test coverage"
        },
        {
            "name": "Pull Request Review", 
            "description": "Comprehensive review of proposed changes",
            "use_case": "Combine test results, coverage, and developer feedback"
        },
        {
            "name": "Code Quality Audit",
            "description": "Periodic assessment of codebase health",
            "use_case": "Full multi-modal analysis with improvement roadmap"
        },
        {
            "name": "Legacy Code Assessment",
            "description": "Evaluate and prioritize technical debt",
            "use_case": "Focus on complexity analysis and test coverage gaps"
        },
        {
            "name": "Team Code Review",
            "description": "Collaborative review with developer insights",
            "use_case": "Include team comments and feedback in analysis"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['name']}:")
        print(f"  Description: {scenario['description']}")
        print(f"  Use Case: {scenario['use_case']}")

async def main():
    """Main demonstration function"""
    print("Multi-modal Code Review AI - Demonstration")
    print("This system combines static analysis, test results, coverage data,")
    print("and developer comments to provide comprehensive code review.")
    
    await demo_individual_analyzers()
    await demo_ai_reviewer()
    await demo_api_usage()
    demo_real_world_scenarios()
    
    print("\n" + "="*60)
    print("GETTING STARTED")
    print("="*60)
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Start the API server: python main.py")
    print("3. Send code review requests to http://localhost:8001/review")
    print("4. Or use individual analyzers programmatically")
    print("\nFor more examples, check the API documentation at:")
    print("http://localhost:8001/docs (when server is running)")

if __name__ == "__main__":
    asyncio.run(main())
