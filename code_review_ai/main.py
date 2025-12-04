#!/usr/bin/env python3
"""
Multi-modal Code Review AI
Combines static analysis, test results, coverage data, and developer comments
for comprehensive code review feedback.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Union
from typing import List, Optional, Dict, Any
import json
import asyncio
from datetime import datetime

from static_analyzer import StaticCodeAnalyzer
from test_analyzer import TestResultAnalyzer
from coverage_analyzer import CoverageAnalyzer
from comment_analyzer import CommentAnalyzer
from ai_reviewer import AIReviewer

app = FastAPI(
    title="Multi-modal Code Review AI",
    description="Comprehensive code review using multiple data sources",
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
    test_analysis: Dict[str, Any]
    coverage_analysis: Dict[str, Any]
    comment_analysis: Dict[str, Any]
    ai_insights: List[str]
    summary: str
    timestamp: str

@app.get("/")
async def root():
    return {"message": "Multi-modal Code Review AI - Ready to analyze your code!"}

@app.post("/review", response_model=CodeReviewResponse)
async def review_code(request: CodeReviewRequest):
    """
    Perform comprehensive code review using multiple analysis methods
    """
    try:
        # Initialize analyzers
        static_analyzer = StaticCodeAnalyzer()
        test_analyzer = TestResultAnalyzer()
        coverage_analyzer = CoverageAnalyzer()
        comment_analyzer = CommentAnalyzer()
        ai_reviewer = AIReviewer()
        
        # Run analyses in parallel
        static_results = await asyncio.to_thread(
            static_analyzer.analyze, request.code, request.language
        )
        
        test_results = await asyncio.to_thread(
            test_analyzer.analyze, request.test_results or {}
        )
        
        coverage_results = await asyncio.to_thread(
            coverage_analyzer.analyze, request.coverage_data or {}
        )
        
        comment_results = await asyncio.to_thread(
            comment_analyzer.analyze, request.developer_comments or []
        )
        
        # Combine all results for AI analysis
        combined_data = {
            'code': request.code,
            'language': request.language,
            'static_analysis': static_results,
            'test_analysis': test_results,
            'coverage_analysis': coverage_results,
            'comment_analysis': comment_results,
            'file_path': request.file_path
        }
        
        ai_insights = await asyncio.to_thread(
            ai_reviewer.generate_insights, combined_data
        )
        
        # Calculate overall score
        overall_score = calculate_overall_score(
            static_results, test_results, coverage_results, comment_results
        )
        
        # Generate comprehensive suggestions
        suggestions = generate_suggestions(
            static_results, test_results, coverage_results, comment_results, ai_insights
        )
        
        # Compile all issues
        all_issues = compile_issues(static_results, test_results, coverage_results)
        
        return CodeReviewResponse(
            overall_score=overall_score,
            issues=all_issues,
            suggestions=suggestions,
            test_analysis=test_results,
            coverage_analysis=coverage_results,
            comment_analysis=comment_results,
            ai_insights=ai_insights['insights'],
            summary=ai_insights['summary'],
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code review failed: {str(e)}")

@app.post("/upload-file-review")
async def upload_file_review(
    code_file: UploadFile = File(...),
    test_file: Optional[UploadFile] = File(None),
    coverage_file: Optional[UploadFile] = File(None)
):
    """
    Upload files for code review
    """
    try:
        # Read code file
        code_content = await code_file.read()
        code = code_content.decode('utf-8')
        
        # Determine language from file extension
        language = determine_language(code_file.filename)
        
        # Read test results if provided
        test_results = None
        if test_file:
            test_content = await test_file.read()
            test_results = json.loads(test_content.decode('utf-8'))
        
        # Read coverage data if provided
        coverage_data = None
        if coverage_file:
            coverage_content = await coverage_file.read()
            coverage_data = json.loads(coverage_content.decode('utf-8'))
        
        # Create request object
        request = CodeReviewRequest(
            code=code,
            language=language,
            test_results=test_results,
            coverage_data=coverage_data,
            file_path=code_file.filename
        )
        
        return await review_code(request)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload review failed: {str(e)}")

def calculate_overall_score(static_results, test_results, coverage_results, comment_results):
    """Calculate overall code quality score (0-100)"""
    scores = []
    
    # Static analysis score (40% weight)
    static_score = max(0, 100 - (static_results['error_count'] * 10 + static_results['warning_count'] * 5))
    scores.append(static_score * 0.4)
    
    # Test score (30% weight)
    test_score = test_results.get('pass_rate', 0) * 100
    scores.append(test_score * 0.3)
    
    # Coverage score (20% weight)
    coverage_score = coverage_results.get('line_coverage', 0) * 100
    scores.append(coverage_score * 0.2)
    
    # Comment quality score (10% weight)
    comment_score = comment_results.get('quality_score', 50)
    scores.append(comment_score * 0.1)
    
    return round(sum(scores), 2)

def generate_suggestions(static_results, test_results, coverage_results, comment_results, ai_insights):
    """Generate actionable suggestions"""
    suggestions = []
    
    # Static analysis suggestions
    if static_results['error_count'] > 0:
        suggestions.append("Fix critical errors identified in static analysis")
    
    if static_results['warning_count'] > 5:
        suggestions.append("Address code quality warnings to improve maintainability")
    
    # Test suggestions
    if test_results.get('pass_rate', 1) < 0.9:
        suggestions.append("Improve test pass rate - some tests are failing")
    
    if test_results.get('test_count', 0) < 5:
        suggestions.append("Add more comprehensive test cases")
    
    # Coverage suggestions
    if coverage_results.get('line_coverage', 0) < 0.8:
        suggestions.append("Increase test coverage - aim for at least 80%")
    
    if coverage_results.get('branch_coverage', 0) < 0.7:
        suggestions.append("Improve branch coverage by testing edge cases")
    
    # Comment suggestions
    if comment_results.get('coverage', 0) < 0.3:
        suggestions.append("Add more documentation and comments")
    
    # AI-generated suggestions
    suggestions.extend(ai_insights.get('suggestions', []))
    
    return suggestions

def compile_issues(static_results, test_results, coverage_results):
    """Compile all issues from different analyzers"""
    issues = []
    
    # Add static analysis issues
    issues.extend(static_results.get('issues', []))
    
    # Add test issues
    for failed_test in test_results.get('failed_tests', []):
        issues.append({
            'type': 'test_failure',
            'severity': 'high',
            'message': f"Test failed: {failed_test['name']}",
            'details': failed_test.get('error', '')
        })
    
    # Add coverage issues
    for uncovered_line in coverage_results.get('uncovered_lines', []):
        issues.append({
            'type': 'coverage',
            'severity': 'medium',
            'message': f"Line {uncovered_line} not covered by tests",
            'line': uncovered_line
        })
    
    return issues

def determine_language(filename):
    """Determine programming language from file extension"""
    if not filename:
        return "python"
    
    extension_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.cs': 'csharp',
        '.go': 'go',
        '.rs': 'rust',
        '.php': 'php',
        '.rb': 'ruby'
    }
    
    for ext, lang in extension_map.items():
        if filename.endswith(ext):
            return lang
    
    return "python"  # default

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
