#!/usr/bin/env python3
"""
Flask-based Code Review AI
A simple working version using Flask
"""

from flask import Flask, request, jsonify
import json
import re
from datetime import datetime

app = Flask(__name__)

def analyze_code_simple(code: str, language: str = "python") -> dict:
    """Simple code analysis"""
    issues = []
    score = 100
    
    lines = code.split('\n')
    
    # Basic checks
    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()
        
        # Check line length
        if len(line) > 100:
            issues.append({
                'type': 'line_too_long',
                'severity': 'low',
                'message': f'Line {i} is too long ({len(line)} characters)',
                'line': i
            })
            score -= 2
        
        # Check for TODO/FIXME
        if 'TODO' in line or 'FIXME' in line:
            issues.append({
                'type': 'todo_comment',
                'severity': 'info',
                'message': f'TODO/FIXME found on line {i}',
                'line': i
            })
            score -= 1
        
        # Python specific checks
        if language.lower() == 'python':
            # Check for print statements
            if re.search(r'\bprint\s*\(', line_stripped):
                issues.append({
                    'type': 'print_statement',
                    'severity': 'low',
                    'message': f'Consider using logging instead of print on line {i}',
                    'line': i
                })
                score -= 3
            
            # Check for bare except
            if 'except:' in line_stripped:
                issues.append({
                    'type': 'bare_except',
                    'severity': 'medium',
                    'message': f'Avoid bare except clauses on line {i}',
                    'line': i
                })
                score -= 5
    
    # Check for function complexity
    function_lines = [line for line in lines if line.strip().startswith('def ')]
    if len(function_lines) == 0 and len(lines) > 10:
        issues.append({
            'type': 'no_functions',
            'severity': 'medium',
            'message': 'Consider breaking code into functions',
            'line': 1
        })
        score -= 10
    
    # Check for docstrings
    has_docstring = any('"""' in line or "'''" in line for line in lines)
    if not has_docstring and len(lines) > 5:
        issues.append({
            'type': 'missing_docstring',
            'severity': 'low',
            'message': 'Consider adding docstrings for documentation',
            'line': 1
        })
        score -= 5
    
    return {
        'issues': issues,
        'score': max(0, score),
        'lines_analyzed': len(lines),
        'functions_found': len(function_lines)
    }

def generate_suggestions(analysis: dict, test_results: dict = None, coverage_data: dict = None) -> list:
    """Generate improvement suggestions"""
    suggestions = []
    
    # Code quality suggestions
    if analysis['score'] < 70:
        suggestions.append("Focus on addressing code quality issues to improve maintainability")
    
    # Issue-specific suggestions
    issue_types = [issue['type'] for issue in analysis['issues']]
    
    if 'line_too_long' in issue_types:
        suggestions.append("Break long lines into multiple lines for better readability")
    
    if 'print_statement' in issue_types:
        suggestions.append("Replace print statements with proper logging")
    
    if 'bare_except' in issue_types:
        suggestions.append("Use specific exception types instead of bare except clauses")
    
    if 'missing_docstring' in issue_types:
        suggestions.append("Add docstrings to functions and classes for better documentation")
    
    # Test-related suggestions
    if test_results:
        if test_results.get('test_count', 0) == 0:
            suggestions.append("Add unit tests to ensure code reliability")
        elif test_results.get('pass_rate', 1) < 0.9:
            suggestions.append("Fix failing tests before proceeding")
    
    # Coverage suggestions
    if coverage_data:
        coverage = coverage_data.get('line_coverage', 0)
        if coverage < 0.8:
            suggestions.append(f"Increase test coverage from {coverage:.1%} to at least 80%")
    
    # Default suggestions if none found
    if not suggestions:
        suggestions.append("Code looks good! Consider adding more comprehensive tests.")
    
    return suggestions

@app.route('/')
def root():
    return jsonify({"message": "Code Review AI - Ready to analyze your code! 🚀"})

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

@app.route('/review', methods=['POST'])
def review_code():
    """
    Perform code review
    """
    try:
        data = request.get_json()
        
        if not data or 'code' not in data:
            return jsonify({"error": "Missing 'code' field"}), 400
        
        code = data['code']
        language = data.get('language', 'python')
        test_results = data.get('test_results')
        coverage_data = data.get('coverage_data')
        
        # Analyze the code
        analysis = analyze_code_simple(code, language)
        
        # Generate suggestions
        suggestions = generate_suggestions(analysis, test_results, coverage_data)
        
        # Calculate overall score
        base_score = analysis['score']
        
        # Adjust score based on test results
        if test_results:
            test_score = test_results.get('pass_rate', 1) * 100
            base_score = (base_score * 0.7) + (test_score * 0.3)
        
        # Adjust score based on coverage
        if coverage_data:
            coverage_score = coverage_data.get('line_coverage', 0) * 100
            base_score = (base_score * 0.8) + (coverage_score * 0.2)
        
        overall_score = round(base_score, 2)
        
        # Generate summary
        summary_parts = [
            f"Code analysis complete. Score: {overall_score}/100.",
            f"Found {len(analysis['issues'])} issues across {analysis['lines_analyzed']} lines."
        ]
        
        if overall_score >= 90:
            summary_parts.append("Excellent code quality! 🌟")
        elif overall_score >= 70:
            summary_parts.append("Good code quality with room for improvement. 👍")
        elif overall_score >= 50:
            summary_parts.append("Code needs improvement in several areas. 🔧")
        else:
            summary_parts.append("Significant improvements needed. 🚨")
        
        return jsonify({
            "overall_score": overall_score,
            "issues": analysis['issues'],
            "suggestions": suggestions,
            "summary": " ".join(summary_parts),
            "timestamp": datetime.now().isoformat(),
            "test_analysis": test_results or {},
            "coverage_analysis": coverage_data or {},
            "ai_insights": [
                f"Analyzed {analysis['lines_analyzed']} lines of {language} code",
                f"Found {analysis['functions_found']} functions",
                f"Code quality score: {analysis['score']}/100"
            ]
        })
        
    except Exception as e:
        return jsonify({"error": f"Review failed: {str(e)}"}), 500

if __name__ == "__main__":
    print("🚀 Starting Code Review AI...")
    print("📖 Available endpoints:")
    print("  GET  /          - Welcome message")
    print("  GET  /health    - Health check")
    print("  POST /review    - Code review")
    print("🌐 Server running at: http://localhost:8001")
    
    app.run(host="0.0.0.0", port=8001, debug=True)
