"""
Comment and Documentation Analysis Module
Analyzes code comments, docstrings, and developer feedback
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime

class CommentAnalyzer:
    def __init__(self):
        self.min_comment_ratio = 0.1  # 10% of lines should have comments
        self.sentiment_keywords = {
            'positive': ['good', 'excellent', 'great', 'perfect', 'clean', 'elegant', 'efficient'],
            'negative': ['bad', 'terrible', 'awful', 'messy', 'slow', 'broken', 'buggy'],
            'concern': ['todo', 'fixme', 'hack', 'workaround', 'temporary', 'review', 'check']
        }
    
    def analyze(self, comments: List[str]) -> Dict[str, Any]:
        """
        Analyze developer comments and code documentation
        """
        if not comments:
            return self._empty_comment_analysis()
        
        results = {
            'total_comments': len(comments),
            'comment_types': {
                'documentation': 0,
                'explanation': 0,
                'todo': 0,
                'warning': 0,
                'review_feedback': 0
            },
            'sentiment_analysis': {
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'concerns': 0
            },
            'quality_score': 0,
            'coverage': 0,
            'issues': [],
            'insights': [],
            'action_items': []
        }
        
        # Analyze each comment
        for comment in comments:
            self._analyze_single_comment(comment, results)
        
        # Calculate metrics
        self._calculate_comment_metrics(results)
        
        # Generate insights
        self._generate_comment_insights(results)
        
        return results
    
    def _empty_comment_analysis(self) -> Dict[str, Any]:
        """Return analysis when no comments are provided"""
        return {
            'total_comments': 0,
            'comment_types': {
                'documentation': 0,
                'explanation': 0,
                'todo': 0,
                'warning': 0,
                'review_feedback': 0
            },
            'sentiment_analysis': {
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'concerns': 0
            },
            'quality_score': 0,
            'coverage': 0,
            'issues': [{
                'type': 'no_comments',
                'severity': 'medium',
                'message': 'No developer comments or documentation provided'
            }],
            'insights': ['Consider adding code documentation and comments'],
            'action_items': []
        }
    
    def _analyze_single_comment(self, comment: str, results: Dict[str, Any]):
        """Analyze a single comment"""
        comment_lower = comment.lower().strip()
        
        # Classify comment type
        if any(keyword in comment_lower for keyword in ['todo', 'fixme', 'hack']):
            results['comment_types']['todo'] += 1
            results['action_items'].append({
                'type': 'todo',
                'content': comment,
                'priority': 'medium' if 'fixme' in comment_lower else 'low'
            })
        
        elif any(keyword in comment_lower for keyword in ['warning', 'caution', 'danger', 'important']):
            results['comment_types']['warning'] += 1
        
        elif any(keyword in comment_lower for keyword in ['review', 'feedback', 'suggestion']):
            results['comment_types']['review_feedback'] += 1
        
        elif len(comment) > 50 and ('"""' in comment or "'''" in comment or comment.startswith('#')):
            results['comment_types']['documentation'] += 1
        
        else:
            results['comment_types']['explanation'] += 1
        
        # Sentiment analysis
        sentiment = self._analyze_sentiment(comment_lower)
        results['sentiment_analysis'][sentiment] += 1
    
    def _analyze_sentiment(self, comment: str) -> str:
        """Analyze sentiment of a comment"""
        positive_count = sum(1 for word in self.sentiment_keywords['positive'] if word in comment)
        negative_count = sum(1 for word in self.sentiment_keywords['negative'] if word in comment)
        concern_count = sum(1 for word in self.sentiment_keywords['concern'] if word in comment)
        
        if concern_count > 0:
            return 'concerns'
        elif positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _calculate_comment_metrics(self, results: Dict[str, Any]):
        """Calculate comment quality metrics"""
        total_comments = results['total_comments']
        
        if total_comments == 0:
            results['quality_score'] = 0
            results['coverage'] = 0
            return
        
        # Quality score based on comment distribution
        quality_score = 0
        
        # Documentation comments are valuable (30% of score)
        doc_ratio = results['comment_types']['documentation'] / total_comments
        quality_score += min(doc_ratio * 100, 30)
        
        # Explanation comments are good (25% of score)
        exp_ratio = results['comment_types']['explanation'] / total_comments
        quality_score += min(exp_ratio * 100, 25)
        
        # Review feedback is valuable (20% of score)
        review_ratio = results['comment_types']['review_feedback'] / total_comments
        quality_score += min(review_ratio * 100, 20)
        
        # Positive sentiment adds to quality (15% of score)
        positive_ratio = results['sentiment_analysis']['positive'] / total_comments
        quality_score += positive_ratio * 15
        
        # Deduct for too many TODOs (max 10% deduction)
        todo_ratio = results['comment_types']['todo'] / total_comments
        if todo_ratio > 0.3:  # More than 30% TODOs
            quality_score -= min(todo_ratio * 20, 10)
        
        # Deduct for negative sentiment (max 10% deduction)
        negative_ratio = results['sentiment_analysis']['negative'] / total_comments
        quality_score -= negative_ratio * 10
        
        results['quality_score'] = max(0, min(100, quality_score))
        
        # Coverage is based on having comments (simplified metric)
        results['coverage'] = min(1.0, total_comments / 10)  # Assume 10 comments = 100% coverage
    
    def _generate_comment_insights(self, results: Dict[str, Any]):
        """Generate insights from comment analysis"""
        insights = []
        issues = []
        
        total_comments = results['total_comments']
        
        # Comment quantity insights
        if total_comments == 0:
            insights.append("No comments found - consider adding documentation")
            issues.append({
                'type': 'no_documentation',
                'severity': 'medium',
                'message': 'Code lacks comments and documentation'
            })
        elif total_comments < 5:
            insights.append("Limited documentation - consider adding more explanatory comments")
            issues.append({
                'type': 'sparse_documentation',
                'severity': 'low',
                'message': f'Only {total_comments} comments found'
            })
        
        # Comment type insights
        if results['comment_types']['todo'] > total_comments * 0.5:
            insights.append("High number of TODO items - prioritize addressing them")
            issues.append({
                'type': 'many_todos',
                'severity': 'medium',
                'message': f"{results['comment_types']['todo']} TODO items need attention"
            })
        
        if results['comment_types']['warning'] > 0:
            insights.append(f"Found {results['comment_types']['warning']} warning comments - review for potential issues")
        
        # Sentiment insights
        sentiment = results['sentiment_analysis']
        if sentiment['negative'] > sentiment['positive']:
            insights.append("Comments indicate potential code quality concerns")
            issues.append({
                'type': 'negative_sentiment',
                'severity': 'medium',
                'message': 'Comments suggest code quality issues'
            })
        
        if sentiment['concerns'] > 0:
            insights.append(f"Found {sentiment['concerns']} comments expressing concerns - investigate these areas")
        
        if sentiment['positive'] > total_comments * 0.3:
            insights.append("Positive feedback in comments - code appears well-received")
        
        # Quality insights
        if results['quality_score'] < 30:
            insights.append("Comment quality is low - improve documentation and reduce negative feedback")
            issues.append({
                'type': 'low_comment_quality',
                'severity': 'medium',
                'message': f'Comment quality score: {results["quality_score"]:.1f}/100'
            })
        elif results['quality_score'] > 70:
            insights.append("High-quality comments and documentation!")
        
        results['insights'] = insights
        results['issues'] = issues
    
    def analyze_code_comments(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Extract and analyze comments directly from code
        """
        comments = self._extract_comments_from_code(code, language)
        
        results = {
            'extracted_comments': comments,
            'comment_density': 0,
            'docstring_coverage': 0,
            'inline_comments': 0,
            'block_comments': 0,
            'issues': []
        }
        
        if not comments:
            results['issues'].append({
                'type': 'no_code_comments',
                'severity': 'low',
                'message': 'No comments found in code'
            })
            return results
        
        # Calculate comment density
        code_lines = [line for line in code.split('\n') if line.strip()]
        comment_lines = len(comments)
        
        if code_lines:
            results['comment_density'] = comment_lines / len(code_lines)
        
        # Analyze comment types
        for comment in comments:
            if len(comment.strip()) > 100 or '"""' in comment or "'''" in comment:
                results['block_comments'] += 1
            else:
                results['inline_comments'] += 1
        
        # Check comment density
        if results['comment_density'] < self.min_comment_ratio:
            results['issues'].append({
                'type': 'low_comment_density',
                'severity': 'low',
                'message': f'Comment density is {results["comment_density"]:.1%} (recommended: {self.min_comment_ratio:.1%})'
            })
        
        return results
    
    def _extract_comments_from_code(self, code: str, language: str) -> List[str]:
        """Extract comments from code based on language"""
        comments = []
        lines = code.split('\n')
        
        if language.lower() == "python":
            # Python comments
            in_docstring = False
            docstring_delimiter = None
            
            for line in lines:
                stripped = line.strip()
                
                # Handle docstrings
                if '"""' in stripped or "'''" in stripped:
                    if not in_docstring:
                        in_docstring = True
                        docstring_delimiter = '"""' if '"""' in stripped else "'''"
                        comments.append(stripped)
                    elif docstring_delimiter in stripped:
                        in_docstring = False
                        comments.append(stripped)
                elif in_docstring:
                    comments.append(stripped)
                
                # Handle # comments
                elif stripped.startswith('#'):
                    comments.append(stripped)
        
        elif language.lower() in ["javascript", "typescript", "java", "cpp", "c", "csharp"]:
            # C-style comments
            in_block_comment = False
            
            for line in lines:
                stripped = line.strip()
                
                # Block comments
                if '/*' in stripped and not in_block_comment:
                    in_block_comment = True
                    comments.append(stripped)
                elif '*/' in stripped and in_block_comment:
                    in_block_comment = False
                    comments.append(stripped)
                elif in_block_comment:
                    comments.append(stripped)
                
                # Line comments
                elif stripped.startswith('//'):
                    comments.append(stripped)
        
        return comments
    
    def extract_action_items(self, comments: List[str]) -> List[Dict[str, Any]]:
        """Extract actionable items from comments"""
        action_items = []
        
        for i, comment in enumerate(comments):
            comment_lower = comment.lower()
            
            # TODO items
            if 'todo' in comment_lower:
                priority = 'high' if any(word in comment_lower for word in ['urgent', 'critical', 'asap']) else 'medium'
                action_items.append({
                    'type': 'todo',
                    'content': comment,
                    'priority': priority,
                    'index': i
                })
            
            # FIXME items
            elif 'fixme' in comment_lower:
                action_items.append({
                    'type': 'fixme',
                    'content': comment,
                    'priority': 'high',
                    'index': i
                })
            
            # Review requests
            elif any(word in comment_lower for word in ['review', 'check', 'verify']):
                action_items.append({
                    'type': 'review',
                    'content': comment,
                    'priority': 'medium',
                    'index': i
                })
        
        return action_items
