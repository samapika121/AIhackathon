"""
AI-Powered Code Review Module
Combines all analysis results to generate intelligent insights and recommendations
"""

from typing import Dict, List, Any, Optional
import json
from datetime import datetime

class AIReviewer:
    def __init__(self):
        self.severity_weights = {
            'critical': 10,
            'high': 7,
            'medium': 4,
            'low': 2,
            'info': 1
        }
        
        self.quality_thresholds = {
            'excellent': 90,
            'good': 75,
            'fair': 60,
            'poor': 40
        }
    
    def generate_insights(self, combined_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI-powered insights from combined analysis data
        """
        insights = {
            'insights': [],
            'suggestions': [],
            'summary': '',
            'priority_issues': [],
            'code_health_score': 0,
            'improvement_roadmap': [],
            'risk_assessment': {}
        }
        
        # Extract data from different analyzers
        static_analysis = combined_data.get('static_analysis', {})
        test_analysis = combined_data.get('test_analysis', {})
        coverage_analysis = combined_data.get('coverage_analysis', {})
        comment_analysis = combined_data.get('comment_analysis', {})
        
        # Generate comprehensive insights
        self._analyze_code_quality_patterns(combined_data, insights)
        self._identify_critical_issues(combined_data, insights)
        self._generate_improvement_suggestions(combined_data, insights)
        self._assess_technical_debt(combined_data, insights)
        self._create_improvement_roadmap(combined_data, insights)
        self._calculate_health_score(combined_data, insights)
        self._generate_summary(combined_data, insights)
        
        return insights
    
    def _analyze_code_quality_patterns(self, data: Dict[str, Any], insights: Dict[str, Any]):
        """Analyze patterns across different quality metrics"""
        static = data.get('static_analysis', {})
        test = data.get('test_analysis', {})
        coverage = data.get('coverage_analysis', {})
        comments = data.get('comment_analysis', {})
        
        patterns = []
        
        # Pattern: High complexity with low test coverage
        if (static.get('complexity_score', 0) > 15 and 
            coverage.get('line_coverage', 0) < 0.6):
            patterns.append({
                'pattern': 'high_complexity_low_coverage',
                'description': 'Complex code with insufficient test coverage',
                'risk': 'high',
                'recommendation': 'Prioritize testing complex functions and consider refactoring'
            })
        
        # Pattern: Many failed tests with low coverage
        if (len(test.get('failed_tests', [])) > 3 and 
            coverage.get('line_coverage', 0) < 0.7):
            patterns.append({
                'pattern': 'failing_tests_low_coverage',
                'description': 'Multiple test failures combined with low coverage',
                'risk': 'critical',
                'recommendation': 'Fix failing tests and expand test suite'
            })
        
        # Pattern: High TODO count with negative sentiment
        if (comments.get('comment_types', {}).get('todo', 0) > 5 and
            comments.get('sentiment_analysis', {}).get('negative', 0) > 2):
            patterns.append({
                'pattern': 'technical_debt_accumulation',
                'description': 'Accumulating technical debt with negative developer sentiment',
                'risk': 'medium',
                'recommendation': 'Address TODO items and investigate developer concerns'
            })
        
        # Pattern: Good test coverage but many static analysis issues
        if (coverage.get('line_coverage', 0) > 0.8 and 
            static.get('error_count', 0) + static.get('warning_count', 0) > 10):
            patterns.append({
                'pattern': 'good_coverage_poor_quality',
                'description': 'Good test coverage but code quality issues',
                'risk': 'medium',
                'recommendation': 'Focus on code quality improvements and refactoring'
            })
        
        for pattern in patterns:
            insights['insights'].append(f"Pattern detected: {pattern['description']}")
            insights['suggestions'].append(pattern['recommendation'])
    
    def _identify_critical_issues(self, data: Dict[str, Any], insights: Dict[str, Any]):
        """Identify and prioritize critical issues"""
        all_issues = []
        
        # Collect issues from all analyzers
        for analyzer_name, analyzer_data in data.items():
            if isinstance(analyzer_data, dict) and 'issues' in analyzer_data:
                for issue in analyzer_data['issues']:
                    issue['source'] = analyzer_name
                    all_issues.append(issue)
        
        # Sort by severity
        critical_issues = []
        for issue in all_issues:
            severity = issue.get('severity', 'low')
            weight = self.severity_weights.get(severity, 1)
            
            if weight >= 7:  # High and critical issues
                critical_issues.append({
                    'issue': issue,
                    'weight': weight,
                    'impact': self._assess_issue_impact(issue, data)
                })
        
        # Sort by weight and impact
        critical_issues.sort(key=lambda x: (x['weight'], x['impact']), reverse=True)
        
        insights['priority_issues'] = critical_issues[:10]  # Top 10 critical issues
        
        if critical_issues:
            insights['insights'].append(f"Found {len(critical_issues)} critical issues requiring immediate attention")
    
    def _assess_issue_impact(self, issue: Dict[str, Any], data: Dict[str, Any]) -> int:
        """Assess the potential impact of an issue"""
        impact_score = 0
        issue_type = issue.get('type', '')
        
        # High impact issue types
        high_impact_types = [
            'syntax_error', 'security_vulnerability', 'test_failure',
            'high_complexity', 'no_tests', 'critical_path_uncovered'
        ]
        
        if issue_type in high_impact_types:
            impact_score += 5
        
        # Consider context
        if 'line' in issue:
            # Issues in frequently changed code have higher impact
            impact_score += 2
        
        if issue.get('source') == 'static_analysis' and 'error' in issue_type:
            impact_score += 3
        
        return impact_score
    
    def _generate_improvement_suggestions(self, data: Dict[str, Any], insights: Dict[str, Any]):
        """Generate intelligent improvement suggestions"""
        suggestions = []
        
        static = data.get('static_analysis', {})
        test = data.get('test_analysis', {})
        coverage = data.get('coverage_analysis', {})
        comments = data.get('comment_analysis', {})
        
        # Code quality suggestions
        if static.get('error_count', 0) > 0:
            suggestions.append("Fix critical errors identified in static analysis before proceeding")
        
        if static.get('complexity_score', 0) > 20:
            suggestions.append("Consider breaking down complex functions into smaller, more manageable pieces")
        
        # Testing suggestions
        if test.get('test_count', 0) == 0:
            suggestions.append("Implement a comprehensive test suite starting with unit tests for core functionality")
        elif test.get('pass_rate', 1) < 0.9:
            suggestions.append("Stabilize the test suite by fixing failing tests before adding new features")
        
        # Coverage suggestions
        if coverage.get('line_coverage', 0) < 0.5:
            suggestions.append("Significantly increase test coverage - current coverage is critically low")
        elif coverage.get('branch_coverage', 0) < coverage.get('line_coverage', 0) - 0.2:
            suggestions.append("Focus on branch coverage by testing edge cases and error conditions")
        
        # Documentation suggestions
        if comments.get('total_comments', 0) < 3:
            suggestions.append("Add comprehensive documentation and inline comments for better maintainability")
        
        # Performance suggestions
        if test.get('execution_time', 0) > 300:  # 5 minutes
            suggestions.append("Optimize test execution time - consider parallel testing or test optimization")
        
        # Prioritized suggestions based on impact
        priority_suggestions = self._prioritize_suggestions(suggestions, data)
        insights['suggestions'].extend(priority_suggestions)
    
    def _prioritize_suggestions(self, suggestions: List[str], data: Dict[str, Any]) -> List[str]:
        """Prioritize suggestions based on current state"""
        # Simple prioritization logic
        prioritized = []
        
        # Critical issues first
        critical_suggestions = [s for s in suggestions if any(word in s.lower() 
                              for word in ['critical', 'fix', 'error', 'failing'])]
        
        # Quality improvements second
        quality_suggestions = [s for s in suggestions if any(word in s.lower() 
                             for word in ['coverage', 'test', 'quality'])]
        
        # Documentation and optimization last
        other_suggestions = [s for s in suggestions if s not in critical_suggestions + quality_suggestions]
        
        return critical_suggestions + quality_suggestions + other_suggestions
    
    def _assess_technical_debt(self, data: Dict[str, Any], insights: Dict[str, Any]):
        """Assess technical debt levels"""
        debt_indicators = {
            'code_complexity': 0,
            'test_debt': 0,
            'documentation_debt': 0,
            'maintenance_debt': 0
        }
        
        static = data.get('static_analysis', {})
        test = data.get('test_analysis', {})
        coverage = data.get('coverage_analysis', {})
        comments = data.get('comment_analysis', {})
        
        # Code complexity debt
        complexity = static.get('complexity_score', 0)
        if complexity > 20:
            debt_indicators['code_complexity'] = min(100, complexity * 2)
        
        # Test debt
        test_quality = test.get('test_quality_score', 0)
        debt_indicators['test_debt'] = max(0, 100 - test_quality)
        
        # Documentation debt
        doc_quality = comments.get('quality_score', 0)
        debt_indicators['documentation_debt'] = max(0, 100 - doc_quality)
        
        # Maintenance debt (based on TODO count and failed tests)
        todo_count = comments.get('comment_types', {}).get('todo', 0)
        failed_tests = len(test.get('failed_tests', []))
        maintenance_debt = (todo_count * 5) + (failed_tests * 10)
        debt_indicators['maintenance_debt'] = min(100, maintenance_debt)
        
        # Overall debt score
        total_debt = sum(debt_indicators.values()) / len(debt_indicators)
        
        insights['risk_assessment'] = {
            'technical_debt_score': round(total_debt, 2),
            'debt_breakdown': debt_indicators,
            'risk_level': self._categorize_risk_level(total_debt)
        }
        
        if total_debt > 60:
            insights['insights'].append(f"High technical debt detected (score: {total_debt:.1f}/100)")
        elif total_debt > 30:
            insights['insights'].append(f"Moderate technical debt (score: {total_debt:.1f}/100)")
    
    def _categorize_risk_level(self, debt_score: float) -> str:
        """Categorize risk level based on debt score"""
        if debt_score > 80:
            return 'critical'
        elif debt_score > 60:
            return 'high'
        elif debt_score > 40:
            return 'medium'
        else:
            return 'low'
    
    def _create_improvement_roadmap(self, data: Dict[str, Any], insights: Dict[str, Any]):
        """Create a prioritized improvement roadmap"""
        roadmap = []
        
        static = data.get('static_analysis', {})
        test = data.get('test_analysis', {})
        coverage = data.get('coverage_analysis', {})
        
        # Phase 1: Critical fixes
        if static.get('error_count', 0) > 0 or len(test.get('failed_tests', [])) > 0:
            roadmap.append({
                'phase': 1,
                'title': 'Critical Fixes',
                'description': 'Address critical errors and failing tests',
                'estimated_effort': 'High',
                'timeline': '1-2 weeks'
            })
        
        # Phase 2: Test improvements
        if test.get('test_count', 0) < 10 or coverage.get('line_coverage', 0) < 0.7:
            roadmap.append({
                'phase': 2,
                'title': 'Test Coverage Enhancement',
                'description': 'Expand test suite and improve coverage',
                'estimated_effort': 'Medium',
                'timeline': '2-3 weeks'
            })
        
        # Phase 3: Code quality
        if static.get('warning_count', 0) > 5 or static.get('complexity_score', 0) > 15:
            roadmap.append({
                'phase': 3,
                'title': 'Code Quality Improvements',
                'description': 'Refactor complex code and address warnings',
                'estimated_effort': 'Medium',
                'timeline': '1-2 weeks'
            })
        
        # Phase 4: Documentation
        if data.get('comment_analysis', {}).get('total_comments', 0) < 5:
            roadmap.append({
                'phase': 4,
                'title': 'Documentation Enhancement',
                'description': 'Add comprehensive documentation and comments',
                'estimated_effort': 'Low',
                'timeline': '1 week'
            })
        
        insights['improvement_roadmap'] = roadmap
    
    def _calculate_health_score(self, data: Dict[str, Any], insights: Dict[str, Any]):
        """Calculate overall code health score"""
        scores = {
            'static_quality': 0,
            'test_quality': 0,
            'coverage_quality': 0,
            'documentation_quality': 0
        }
        
        static = data.get('static_analysis', {})
        test = data.get('test_analysis', {})
        coverage = data.get('coverage_analysis', {})
        comments = data.get('comment_analysis', {})
        
        # Static analysis score (30% weight)
        error_penalty = static.get('error_count', 0) * 15
        warning_penalty = static.get('warning_count', 0) * 5
        complexity_penalty = max(0, static.get('complexity_score', 0) - 10) * 2
        scores['static_quality'] = max(0, 100 - error_penalty - warning_penalty - complexity_penalty)
        
        # Test quality score (30% weight)
        scores['test_quality'] = test.get('test_quality_score', 0)
        
        # Coverage score (25% weight)
        line_cov = coverage.get('line_coverage', 0) * 100
        branch_cov = coverage.get('branch_coverage', 0) * 100
        scores['coverage_quality'] = (line_cov * 0.7 + branch_cov * 0.3)
        
        # Documentation score (15% weight)
        scores['documentation_quality'] = comments.get('quality_score', 0)
        
        # Weighted average
        health_score = (
            scores['static_quality'] * 0.30 +
            scores['test_quality'] * 0.30 +
            scores['coverage_quality'] * 0.25 +
            scores['documentation_quality'] * 0.15
        )
        
        insights['code_health_score'] = round(health_score, 2)
        insights['score_breakdown'] = scores
    
    def _generate_summary(self, data: Dict[str, Any], insights: Dict[str, Any]):
        """Generate a comprehensive summary"""
        health_score = insights.get('code_health_score', 0)
        priority_issues = len(insights.get('priority_issues', []))
        
        # Determine overall assessment
        if health_score >= self.quality_thresholds['excellent']:
            assessment = "excellent"
        elif health_score >= self.quality_thresholds['good']:
            assessment = "good"
        elif health_score >= self.quality_thresholds['fair']:
            assessment = "fair"
        else:
            assessment = "poor"
        
        summary_parts = [
            f"Code health score: {health_score:.1f}/100 ({assessment})",
        ]
        
        if priority_issues > 0:
            summary_parts.append(f"{priority_issues} critical issues require immediate attention")
        
        # Add key recommendations
        roadmap = insights.get('improvement_roadmap', [])
        if roadmap:
            next_phase = roadmap[0]
            summary_parts.append(f"Next priority: {next_phase['title']}")
        
        # Add positive notes
        static = data.get('static_analysis', {})
        test = data.get('test_analysis', {})
        coverage = data.get('coverage_analysis', {})
        
        if static.get('error_count', 0) == 0:
            summary_parts.append("No critical errors found")
        
        if test.get('pass_rate', 0) == 1.0 and test.get('test_count', 0) > 0:
            summary_parts.append("All tests passing")
        
        if coverage.get('line_coverage', 0) > 0.8:
            summary_parts.append("Good test coverage")
        
        insights['summary'] = ". ".join(summary_parts) + "."
