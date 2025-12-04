#!/usr/bin/env python3
"""
Simple Multi-modal Code Review AI
A simplified version that works with basic dependencies
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import re
from datetime import datetime

app = FastAPI(
    title="Simple Code Review AI",
    description="Simplified code review API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeReviewRequest(BaseModel):
    code: str
    language: str = "python"
    test_results: Optional[Dict[str, Any]] = None
    coverage_data: Optional[Dict[str, Any]] = None
    developer_comments: Optional[List[str]] = None
    file_path: Optional[str] = None

class CodeReviewResponse(BaseModel):
    overall_score: float
    issues: List[Dict[str, Any]]
    suggestions: List[str]
    summary: str
    timestamp: str

def analyze_code_simple(code: str, language: str = "python") -> Dict[str, Any]:
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
            # Check for print statements (should use logging)
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
    
    # Check for function complexity (simple heuristic)
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

def generate_suggestions(analysis: Dict[str, Any], test_results: Optional[Dict] = None, 
                        coverage_data: Optional[Dict] = None) -> List[str]:
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

@app.get("/")
async def root():
    return {"message": "Simple Code Review AI - Ready to analyze your code!"}

@app.post("/review", response_model=CodeReviewResponse)
async def review_code(request: CodeReviewRequest):
    """
    Perform code review
    """
    try:
        # Analyze the code
        analysis = analyze_code_simple(request.code, request.language)
        
        # Generate suggestions
        suggestions = generate_suggestions(
            analysis, 
            request.test_results, 
            request.coverage_data
        )
        
        # Calculate overall score
        base_score = analysis['score']
        
        # Adjust score based on test results
        if request.test_results:
            test_score = request.test_results.get('pass_rate', 1) * 100
            base_score = (base_score * 0.7) + (test_score * 0.3)
        
        # Adjust score based on coverage
        if request.coverage_data:
            coverage_score = request.coverage_data.get('line_coverage', 0) * 100
            base_score = (base_score * 0.8) + (coverage_score * 0.2)
        
        overall_score = round(base_score, 2)
        
        # Generate summary
        summary_parts = [
            f"Code analysis complete. Score: {overall_score}/100.",
            f"Found {len(analysis['issues'])} issues across {analysis['lines_analyzed']} lines."
        ]
        
        if overall_score >= 90:
            summary_parts.append("Excellent code quality!")
        elif overall_score >= 70:
            summary_parts.append("Good code quality with room for improvement.")
        elif overall_score >= 50:
            summary_parts.append("Code needs improvement in several areas.")
        else:
            summary_parts.append("Significant improvements needed.")
        
        return CodeReviewResponse(
            overall_score=overall_score,
            issues=analysis['issues'],
            suggestions=suggestions,
            summary=" ".join(summary_parts),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Review failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Simple Code Review AI...")
    print("📖 API docs will be available at: http://localhost:8001/docs")
    print("🏥 Health check at: http://localhost:8001/health")
    uvicorn.run(app, host="0.0.0.0", port=8001)
