"""
Test Result Analysis Module
Analyzes test results, test quality, and test coverage patterns
"""

from typing import Dict, List, Any, Optional
import json
import re
from datetime import datetime

class TestResultAnalyzer:
    def __init__(self):
        self.min_test_count = 5
        self.acceptable_pass_rate = 0.9
    
    def analyze(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze test results and provide insights
        """
        if not test_data:
            return self._empty_test_analysis()
        
        results = {
            'test_count': 0,
            'passed_tests': 0,
            'failed_tests': [],
            'skipped_tests': [],
            'pass_rate': 0.0,
            'execution_time': 0.0,
            'test_quality_score': 0,
            'issues': [],
            'recommendations': []
        }
        
        # Parse different test result formats
        if 'pytest' in test_data or 'tests' in test_data:
            self._analyze_pytest_results(test_data, results)
        elif 'jest' in test_data or 'suites' in test_data:
            self._analyze_jest_results(test_data, results)
        elif 'junit' in test_data:
            self._analyze_junit_results(test_data, results)
        else:
            self._analyze_generic_results(test_data, results)
        
        # Calculate metrics
        self._calculate_test_metrics(results)
        
        # Generate recommendations
        self._generate_test_recommendations(results)
        
        return results
    
    def _empty_test_analysis(self) -> Dict[str, Any]:
        """Return analysis for when no test data is provided"""
        return {
            'test_count': 0,
            'passed_tests': 0,
            'failed_tests': [],
            'skipped_tests': [],
            'pass_rate': 0.0,
            'execution_time': 0.0,
            'test_quality_score': 0,
            'issues': [{
                'type': 'no_tests',
                'severity': 'high',
                'message': 'No test results provided - consider adding comprehensive tests'
            }],
            'recommendations': [
                'Add unit tests for core functionality',
                'Implement integration tests',
                'Set up automated testing pipeline'
            ]
        }
    
    def _analyze_pytest_results(self, test_data: Dict[str, Any], results: Dict[str, Any]):
        """Analyze pytest format results"""
        if 'tests' in test_data:
            tests = test_data['tests']
            results['test_count'] = len(tests)
            
            for test in tests:
                if test.get('outcome') == 'passed':
                    results['passed_tests'] += 1
                elif test.get('outcome') == 'failed':
                    results['failed_tests'].append({
                        'name': test.get('nodeid', 'unknown'),
                        'error': test.get('call', {}).get('longrepr', 'No error details'),
                        'duration': test.get('call', {}).get('duration', 0)
                    })
                elif test.get('outcome') == 'skipped':
                    results['skipped_tests'].append({
                        'name': test.get('nodeid', 'unknown'),
                        'reason': test.get('call', {}).get('longrepr', 'No reason provided')
                    })
        
        # Extract execution time
        if 'summary' in test_data:
            results['execution_time'] = test_data['summary'].get('duration', 0)
    
    def _analyze_jest_results(self, test_data: Dict[str, Any], results: Dict[str, Any]):
        """Analyze Jest format results"""
        if 'testResults' in test_data:
            for test_suite in test_data['testResults']:
                for test in test_suite.get('assertionResults', []):
                    results['test_count'] += 1
                    
                    if test.get('status') == 'passed':
                        results['passed_tests'] += 1
                    elif test.get('status') == 'failed':
                        results['failed_tests'].append({
                            'name': test.get('fullName', 'unknown'),
                            'error': '\n'.join([msg.get('message', '') for msg in test.get('failureMessages', [])]),
                            'duration': test.get('duration', 0)
                        })
        
        # Extract execution time
        if 'perfStats' in test_data:
            results['execution_time'] = test_data['perfStats'].get('runtime', 0) / 1000  # Convert to seconds
    
    def _analyze_junit_results(self, test_data: Dict[str, Any], results: Dict[str, Any]):
        """Analyze JUnit XML format results"""
        # This would parse JUnit XML format
        # For now, implement basic structure
        results['test_count'] = test_data.get('tests', 0)
        results['passed_tests'] = test_data.get('tests', 0) - test_data.get('failures', 0) - test_data.get('errors', 0)
        results['execution_time'] = test_data.get('time', 0)
        
        # Add failed tests
        for failure in test_data.get('failures', []):
            results['failed_tests'].append({
                'name': failure.get('name', 'unknown'),
                'error': failure.get('message', 'No error details'),
                'duration': 0
            })
    
    def _analyze_generic_results(self, test_data: Dict[str, Any], results: Dict[str, Any]):
        """Analyze generic test result format"""
        results['test_count'] = test_data.get('total', test_data.get('count', 0))
        results['passed_tests'] = test_data.get('passed', test_data.get('success', 0))
        results['execution_time'] = test_data.get('duration', test_data.get('time', 0))
        
        # Handle failed tests
        failed = test_data.get('failed', [])
        if isinstance(failed, list):
            results['failed_tests'] = failed
        else:
            # If failed is just a count
            for i in range(failed):
                results['failed_tests'].append({
                    'name': f'failed_test_{i+1}',
                    'error': 'No details available',
                    'duration': 0
                })
    
    def _calculate_test_metrics(self, results: Dict[str, Any]):
        """Calculate test quality metrics"""
        total_tests = results['test_count']
        
        if total_tests > 0:
            results['pass_rate'] = results['passed_tests'] / total_tests
        else:
            results['pass_rate'] = 0.0
        
        # Calculate test quality score (0-100)
        quality_score = 0
        
        # Pass rate component (50% of score)
        quality_score += results['pass_rate'] * 50
        
        # Test count component (30% of score)
        if total_tests >= self.min_test_count:
            quality_score += 30
        else:
            quality_score += (total_tests / self.min_test_count) * 30
        
        # Execution time component (20% of score)
        # Faster tests get higher scores (reasonable execution time < 60 seconds)
        if results['execution_time'] <= 60:
            quality_score += 20
        elif results['execution_time'] <= 300:  # 5 minutes
            quality_score += 10
        # else: 0 points for very slow tests
        
        results['test_quality_score'] = round(quality_score, 2)
    
    def _generate_test_recommendations(self, results: Dict[str, Any]):
        """Generate actionable recommendations"""
        recommendations = []
        
        # Test count recommendations
        if results['test_count'] == 0:
            recommendations.append("Add comprehensive test suite - no tests found")
            results['issues'].append({
                'type': 'no_tests',
                'severity': 'critical',
                'message': 'No tests found'
            })
        elif results['test_count'] < self.min_test_count:
            recommendations.append(f"Increase test coverage - only {results['test_count']} tests found (minimum: {self.min_test_count})")
            results['issues'].append({
                'type': 'insufficient_tests',
                'severity': 'medium',
                'message': f'Only {results["test_count"]} tests found'
            })
        
        # Pass rate recommendations
        if results['pass_rate'] < self.acceptable_pass_rate:
            recommendations.append(f"Fix failing tests - pass rate is {results['pass_rate']:.1%} (target: {self.acceptable_pass_rate:.1%})")
            results['issues'].append({
                'type': 'low_pass_rate',
                'severity': 'high',
                'message': f'Low test pass rate: {results["pass_rate"]:.1%}'
            })
        
        # Performance recommendations
        if results['execution_time'] > 300:  # 5 minutes
            recommendations.append("Optimize test execution time - tests are running too slowly")
            results['issues'].append({
                'type': 'slow_tests',
                'severity': 'medium',
                'message': f'Tests take {results["execution_time"]:.1f} seconds to run'
            })
        
        # Failed test recommendations
        if results['failed_tests']:
            recommendations.append(f"Address {len(results['failed_tests'])} failing test(s)")
            for failed_test in results['failed_tests'][:3]:  # Show first 3
                results['issues'].append({
                    'type': 'test_failure',
                    'severity': 'high',
                    'message': f"Test '{failed_test['name']}' is failing",
                    'details': failed_test['error']
                })
        
        # Skipped test recommendations
        if results['skipped_tests']:
            recommendations.append(f"Review {len(results['skipped_tests'])} skipped test(s)")
            results['issues'].append({
                'type': 'skipped_tests',
                'severity': 'low',
                'message': f'{len(results["skipped_tests"])} tests are being skipped'
            })
        
        # General recommendations
        if results['test_quality_score'] < 70:
            recommendations.append("Improve overall test quality - consider adding more comprehensive test cases")
        
        if results['test_count'] > 0 and not results['failed_tests']:
            recommendations.append("Great job! All tests are passing. Consider adding edge case tests.")
        
        results['recommendations'] = recommendations
    
    def analyze_test_patterns(self, test_code: str) -> Dict[str, Any]:
        """
        Analyze test code patterns and quality
        """
        patterns = {
            'has_setup_teardown': False,
            'uses_mocking': False,
            'has_assertions': False,
            'test_naming_convention': True,
            'has_edge_cases': False,
            'issues': []
        }
        
        lines = test_code.split('\n')
        
        for line in lines:
            line = line.strip().lower()
            
            # Check for setup/teardown
            if any(keyword in line for keyword in ['setup', 'teardown', 'beforeeach', 'aftereach']):
                patterns['has_setup_teardown'] = True
            
            # Check for mocking
            if any(keyword in line for keyword in ['mock', 'stub', 'spy', 'patch']):
                patterns['uses_mocking'] = True
            
            # Check for assertions
            if any(keyword in line for keyword in ['assert', 'expect', 'should']):
                patterns['has_assertions'] = True
            
            # Check for edge case keywords
            if any(keyword in line for keyword in ['edge', 'boundary', 'null', 'empty', 'invalid']):
                patterns['has_edge_cases'] = True
        
        # Check test naming convention
        test_functions = re.findall(r'def (test_\w+|it\s*\(|describe\s*\()', test_code)
        if not test_functions:
            patterns['test_naming_convention'] = False
            patterns['issues'].append({
                'type': 'naming_convention',
                'severity': 'medium',
                'message': 'Test functions should follow naming conventions (test_* or describe/it)'
            })
        
        return patterns
