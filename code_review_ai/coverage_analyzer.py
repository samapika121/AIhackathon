"""
Coverage Analysis Module
Analyzes test coverage data and identifies uncovered code paths
"""

from typing import Dict, List, Any, Optional
import json

class CoverageAnalyzer:
    def __init__(self):
        self.min_line_coverage = 0.8
        self.min_branch_coverage = 0.7
        self.min_function_coverage = 0.9
    
    def analyze(self, coverage_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze coverage data and provide insights
        """
        if not coverage_data:
            return self._empty_coverage_analysis()
        
        results = {
            'line_coverage': 0.0,
            'branch_coverage': 0.0,
            'function_coverage': 0.0,
            'uncovered_lines': [],
            'uncovered_branches': [],
            'uncovered_functions': [],
            'coverage_by_file': {},
            'issues': [],
            'recommendations': [],
            'hotspots': []  # Areas needing attention
        }
        
        # Parse different coverage formats
        if 'coverage' in coverage_data or 'lines' in coverage_data:
            self._analyze_python_coverage(coverage_data, results)
        elif 'lcov' in coverage_data or 'info' in coverage_data:
            self._analyze_lcov_coverage(coverage_data, results)
        elif 'istanbul' in coverage_data or 'nyc' in coverage_data:
            self._analyze_istanbul_coverage(coverage_data, results)
        else:
            self._analyze_generic_coverage(coverage_data, results)
        
        # Generate insights
        self._generate_coverage_insights(results)
        
        return results
    
    def _empty_coverage_analysis(self) -> Dict[str, Any]:
        """Return analysis when no coverage data is provided"""
        return {
            'line_coverage': 0.0,
            'branch_coverage': 0.0,
            'function_coverage': 0.0,
            'uncovered_lines': [],
            'uncovered_branches': [],
            'uncovered_functions': [],
            'coverage_by_file': {},
            'issues': [{
                'type': 'no_coverage',
                'severity': 'high',
                'message': 'No coverage data provided - run tests with coverage reporting'
            }],
            'recommendations': [
                'Set up code coverage reporting',
                'Run tests with coverage analysis',
                'Aim for at least 80% line coverage'
            ],
            'hotspots': []
        }
    
    def _analyze_python_coverage(self, coverage_data: Dict[str, Any], results: Dict[str, Any]):
        """Analyze Python coverage.py format"""
        # Handle coverage.py JSON format
        if 'files' in coverage_data:
            total_lines = 0
            covered_lines = 0
            
            for filename, file_data in coverage_data['files'].items():
                executed_lines = file_data.get('executed_lines', [])
                missing_lines = file_data.get('missing_lines', [])
                
                file_total = len(executed_lines) + len(missing_lines)
                file_covered = len(executed_lines)
                
                total_lines += file_total
                covered_lines += file_covered
                
                # Store per-file coverage
                if file_total > 0:
                    file_coverage = file_covered / file_total
                    results['coverage_by_file'][filename] = {
                        'line_coverage': file_coverage,
                        'covered_lines': file_covered,
                        'total_lines': file_total,
                        'missing_lines': missing_lines
                    }
                    
                    # Add uncovered lines
                    results['uncovered_lines'].extend([
                        {'file': filename, 'line': line} for line in missing_lines
                    ])
            
            # Calculate overall coverage
            if total_lines > 0:
                results['line_coverage'] = covered_lines / total_lines
        
        # Handle summary format
        elif 'totals' in coverage_data:
            totals = coverage_data['totals']
            results['line_coverage'] = totals.get('percent_covered', 0) / 100
            results['branch_coverage'] = totals.get('percent_covered_display', 0) / 100
    
    def _analyze_lcov_coverage(self, coverage_data: Dict[str, Any], results: Dict[str, Any]):
        """Analyze LCOV format coverage"""
        if 'records' in coverage_data:
            total_lines = 0
            covered_lines = 0
            total_functions = 0
            covered_functions = 0
            total_branches = 0
            covered_branches = 0
            
            for record in coverage_data['records']:
                # Line coverage
                lines = record.get('lines', {})
                if 'found' in lines and 'hit' in lines:
                    total_lines += lines['found']
                    covered_lines += lines['hit']
                
                # Function coverage
                functions = record.get('functions', {})
                if 'found' in functions and 'hit' in functions:
                    total_functions += functions['found']
                    covered_functions += functions['hit']
                
                # Branch coverage
                branches = record.get('branches', {})
                if 'found' in branches and 'hit' in branches:
                    total_branches += branches['found']
                    covered_branches += branches['hit']
            
            # Calculate coverages
            if total_lines > 0:
                results['line_coverage'] = covered_lines / total_lines
            if total_functions > 0:
                results['function_coverage'] = covered_functions / total_functions
            if total_branches > 0:
                results['branch_coverage'] = covered_branches / total_branches
    
    def _analyze_istanbul_coverage(self, coverage_data: Dict[str, Any], results: Dict[str, Any]):
        """Analyze Istanbul/NYC format coverage"""
        if isinstance(coverage_data, dict):
            total_statements = 0
            covered_statements = 0
            total_branches = 0
            covered_branches = 0
            total_functions = 0
            covered_functions = 0
            
            for filename, file_data in coverage_data.items():
                if isinstance(file_data, dict):
                    # Statements (lines)
                    statements = file_data.get('s', {})
                    total_statements += len(statements)
                    covered_statements += sum(1 for count in statements.values() if count > 0)
                    
                    # Branches
                    branches = file_data.get('b', {})
                    for branch_data in branches.values():
                        if isinstance(branch_data, list):
                            total_branches += len(branch_data)
                            covered_branches += sum(1 for count in branch_data if count > 0)
                    
                    # Functions
                    functions = file_data.get('f', {})
                    total_functions += len(functions)
                    covered_functions += sum(1 for count in functions.values() if count > 0)
                    
                    # Store uncovered lines
                    uncovered = [line for line, count in statements.items() if count == 0]
                    results['uncovered_lines'].extend([
                        {'file': filename, 'line': int(line)} for line in uncovered
                    ])
            
            # Calculate coverages
            if total_statements > 0:
                results['line_coverage'] = covered_statements / total_statements
            if total_branches > 0:
                results['branch_coverage'] = covered_branches / total_branches
            if total_functions > 0:
                results['function_coverage'] = covered_functions / total_functions
    
    def _analyze_generic_coverage(self, coverage_data: Dict[str, Any], results: Dict[str, Any]):
        """Analyze generic coverage format"""
        # Try to extract common fields
        results['line_coverage'] = coverage_data.get('line_coverage', 
                                                   coverage_data.get('lines', 
                                                   coverage_data.get('coverage', 0)))
        results['branch_coverage'] = coverage_data.get('branch_coverage', 
                                                     coverage_data.get('branches', 0))
        results['function_coverage'] = coverage_data.get('function_coverage', 
                                                       coverage_data.get('functions', 0))
        
        # Convert percentages to decimals if needed
        if results['line_coverage'] > 1:
            results['line_coverage'] /= 100
        if results['branch_coverage'] > 1:
            results['branch_coverage'] /= 100
        if results['function_coverage'] > 1:
            results['function_coverage'] /= 100
    
    def _generate_coverage_insights(self, results: Dict[str, Any]):
        """Generate coverage insights and recommendations"""
        recommendations = []
        issues = []
        
        # Line coverage analysis
        if results['line_coverage'] < self.min_line_coverage:
            severity = 'high' if results['line_coverage'] < 0.5 else 'medium'
            issues.append({
                'type': 'low_line_coverage',
                'severity': severity,
                'message': f"Line coverage is {results['line_coverage']:.1%} (target: {self.min_line_coverage:.1%})"
            })
            recommendations.append(f"Increase line coverage from {results['line_coverage']:.1%} to at least {self.min_line_coverage:.1%}")
        
        # Branch coverage analysis
        if results['branch_coverage'] < self.min_branch_coverage:
            issues.append({
                'type': 'low_branch_coverage',
                'severity': 'medium',
                'message': f"Branch coverage is {results['branch_coverage']:.1%} (target: {self.min_branch_coverage:.1%})"
            })
            recommendations.append(f"Improve branch coverage by testing edge cases and error conditions")
        
        # Function coverage analysis
        if results['function_coverage'] < self.min_function_coverage:
            issues.append({
                'type': 'low_function_coverage',
                'severity': 'medium',
                'message': f"Function coverage is {results['function_coverage']:.1%} (target: {self.min_function_coverage:.1%})"
            })
            recommendations.append("Add tests for uncovered functions")
        
        # Identify hotspots (files with low coverage)
        hotspots = []
        for filename, file_data in results['coverage_by_file'].items():
            if file_data['line_coverage'] < 0.6:  # Less than 60% coverage
                hotspots.append({
                    'file': filename,
                    'coverage': file_data['line_coverage'],
                    'missing_lines': len(file_data.get('missing_lines', [])),
                    'priority': 'high' if file_data['line_coverage'] < 0.3 else 'medium'
                })
        
        # Sort hotspots by coverage (lowest first)
        hotspots.sort(key=lambda x: x['coverage'])
        results['hotspots'] = hotspots[:10]  # Top 10 files needing attention
        
        if hotspots:
            recommendations.append(f"Focus on {len(hotspots)} files with low coverage")
            issues.append({
                'type': 'coverage_hotspots',
                'severity': 'medium',
                'message': f"{len(hotspots)} files have coverage below 60%"
            })
        
        # Uncovered lines analysis
        if results['uncovered_lines']:
            total_uncovered = len(results['uncovered_lines'])
            if total_uncovered > 50:
                issues.append({
                    'type': 'many_uncovered_lines',
                    'severity': 'high',
                    'message': f"{total_uncovered} lines are not covered by tests"
                })
                recommendations.append("Prioritize testing the most critical uncovered code paths")
            elif total_uncovered > 10:
                recommendations.append(f"Add tests to cover {total_uncovered} uncovered lines")
        
        # Positive feedback
        if results['line_coverage'] >= self.min_line_coverage:
            recommendations.append("Excellent line coverage! Consider improving branch coverage for edge cases.")
        
        if (results['line_coverage'] >= 0.9 and 
            results['branch_coverage'] >= 0.8 and 
            results['function_coverage'] >= 0.9):
            recommendations.append("Outstanding test coverage across all metrics!")
        
        results['issues'] = issues
        results['recommendations'] = recommendations
    
    def identify_critical_paths(self, coverage_data: Dict[str, Any], code: str) -> List[Dict[str, Any]]:
        """
        Identify critical code paths that lack coverage
        """
        critical_paths = []
        
        # Look for important patterns in uncovered code
        uncovered_lines = coverage_data.get('uncovered_lines', [])
        code_lines = code.split('\n')
        
        for uncovered in uncovered_lines:
            line_num = uncovered.get('line', 0) - 1  # Convert to 0-based index
            
            if 0 <= line_num < len(code_lines):
                line_content = code_lines[line_num].strip()
                
                # Identify critical patterns
                if any(keyword in line_content.lower() for keyword in 
                      ['error', 'exception', 'raise', 'throw', 'critical', 'security']):
                    critical_paths.append({
                        'line': line_num + 1,
                        'content': line_content,
                        'type': 'error_handling',
                        'priority': 'high',
                        'reason': 'Error handling code should be tested'
                    })
                
                elif any(keyword in line_content.lower() for keyword in 
                        ['if', 'else', 'elif', 'switch', 'case']):
                    critical_paths.append({
                        'line': line_num + 1,
                        'content': line_content,
                        'type': 'conditional',
                        'priority': 'medium',
                        'reason': 'Conditional logic should be tested'
                    })
        
        return critical_paths
