"""
Static Code Analysis Module
Performs static analysis on code to identify issues, complexity, and quality metrics
"""

import ast
import re
from typing import Dict, List, Any
import subprocess
import tempfile
import os

class StaticCodeAnalyzer:
    def __init__(self):
        self.complexity_threshold = 10
        self.line_length_limit = 100
    
    def analyze(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Perform comprehensive static analysis
        """
        if language.lower() == "python":
            return self._analyze_python(code)
        elif language.lower() in ["javascript", "typescript"]:
            return self._analyze_javascript(code)
        else:
            return self._analyze_generic(code)
    
    def _analyze_python(self, code: str) -> Dict[str, Any]:
        """Analyze Python code"""
        results = {
            'language': 'python',
            'issues': [],
            'metrics': {},
            'error_count': 0,
            'warning_count': 0,
            'complexity_score': 0
        }
        
        try:
            # Parse AST
            tree = ast.parse(code)
            
            # Analyze AST
            self._analyze_ast(tree, results)
            
            # Check code style
            self._check_python_style(code, results)
            
            # Calculate complexity
            results['complexity_score'] = self._calculate_complexity(tree)
            
            # Run pylint if available
            self._run_pylint(code, results)
            
        except SyntaxError as e:
            results['issues'].append({
                'type': 'syntax_error',
                'severity': 'critical',
                'message': f"Syntax error: {str(e)}",
                'line': e.lineno
            })
            results['error_count'] += 1
        
        return results
    
    def _analyze_ast(self, tree: ast.AST, results: Dict[str, Any]):
        """Analyze AST for various issues"""
        class CodeAnalyzer(ast.NodeVisitor):
            def __init__(self, results):
                self.results = results
                self.function_complexity = {}
                self.current_function = None
            
            def visit_FunctionDef(self, node):
                self.current_function = node.name
                self.function_complexity[node.name] = 1
                
                # Check function length
                if len(node.body) > 20:
                    self.results['issues'].append({
                        'type': 'function_length',
                        'severity': 'medium',
                        'message': f"Function '{node.name}' is too long ({len(node.body)} statements)",
                        'line': node.lineno
                    })
                    self.results['warning_count'] += 1
                
                # Check for missing docstring
                if not ast.get_docstring(node):
                    self.results['issues'].append({
                        'type': 'missing_docstring',
                        'severity': 'low',
                        'message': f"Function '{node.name}' missing docstring",
                        'line': node.lineno
                    })
                    self.results['warning_count'] += 1
                
                self.generic_visit(node)
                self.current_function = None
            
            def visit_ClassDef(self, node):
                # Check for missing docstring
                if not ast.get_docstring(node):
                    self.results['issues'].append({
                        'type': 'missing_docstring',
                        'severity': 'low',
                        'message': f"Class '{node.name}' missing docstring",
                        'line': node.lineno
                    })
                    self.results['warning_count'] += 1
                
                self.generic_visit(node)
            
            def visit_If(self, node):
                if self.current_function:
                    self.function_complexity[self.current_function] += 1
                self.generic_visit(node)
            
            def visit_For(self, node):
                if self.current_function:
                    self.function_complexity[self.current_function] += 1
                self.generic_visit(node)
            
            def visit_While(self, node):
                if self.current_function:
                    self.function_complexity[self.current_function] += 1
                self.generic_visit(node)
            
            def visit_Try(self, node):
                if self.current_function:
                    self.function_complexity[self.current_function] += 1
                
                # Check for bare except
                for handler in node.handlers:
                    if handler.type is None:
                        self.results['issues'].append({
                            'type': 'bare_except',
                            'severity': 'medium',
                            'message': "Avoid bare except clauses",
                            'line': handler.lineno
                        })
                        self.results['warning_count'] += 1
                
                self.generic_visit(node)
        
        analyzer = CodeAnalyzer(results)
        analyzer.visit(tree)
        
        # Check for high complexity functions
        for func_name, complexity in analyzer.function_complexity.items():
            if complexity > self.complexity_threshold:
                results['issues'].append({
                    'type': 'high_complexity',
                    'severity': 'high',
                    'message': f"Function '{func_name}' has high complexity ({complexity})",
                    'complexity': complexity
                })
                results['error_count'] += 1
        
        results['metrics']['function_complexities'] = analyzer.function_complexity
    
    def _check_python_style(self, code: str, results: Dict[str, Any]):
        """Check Python style guidelines"""
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check line length
            if len(line) > self.line_length_limit:
                results['issues'].append({
                    'type': 'line_too_long',
                    'severity': 'low',
                    'message': f"Line too long ({len(line)} > {self.line_length_limit})",
                    'line': i
                })
                results['warning_count'] += 1
            
            # Check for trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                results['issues'].append({
                    'type': 'trailing_whitespace',
                    'severity': 'low',
                    'message': "Trailing whitespace",
                    'line': i
                })
                results['warning_count'] += 1
            
            # Check for TODO/FIXME comments
            if 'TODO' in line or 'FIXME' in line:
                results['issues'].append({
                    'type': 'todo_comment',
                    'severity': 'info',
                    'message': "TODO/FIXME comment found",
                    'line': i
                })
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _run_pylint(self, code: str, results: Dict[str, Any]):
        """Run pylint if available"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Run pylint
            result = subprocess.run(
                ['pylint', '--output-format=json', temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                import json
                pylint_results = json.loads(result.stdout)
                
                for issue in pylint_results:
                    severity_map = {
                        'error': 'high',
                        'warning': 'medium',
                        'refactor': 'low',
                        'convention': 'low'
                    }
                    
                    results['issues'].append({
                        'type': 'pylint',
                        'severity': severity_map.get(issue['type'], 'medium'),
                        'message': issue['message'],
                        'line': issue['line'],
                        'symbol': issue.get('symbol', '')
                    })
                    
                    if issue['type'] == 'error':
                        results['error_count'] += 1
                    else:
                        results['warning_count'] += 1
            
            os.unlink(temp_file)
            
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            # Pylint not available or failed
            pass
    
    def _analyze_javascript(self, code: str) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript code"""
        results = {
            'language': 'javascript',
            'issues': [],
            'metrics': {},
            'error_count': 0,
            'warning_count': 0,
            'complexity_score': 0
        }
        
        # Basic JavaScript analysis
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for console.log (should be removed in production)
            if 'console.log' in line:
                results['issues'].append({
                    'type': 'console_log',
                    'severity': 'low',
                    'message': "Remove console.log statements in production",
                    'line': i
                })
                results['warning_count'] += 1
            
            # Check for == instead of ===
            if re.search(r'[^=!]==[^=]', line):
                results['issues'].append({
                    'type': 'loose_equality',
                    'severity': 'medium',
                    'message': "Use strict equality (===) instead of loose equality (==)",
                    'line': i
                })
                results['warning_count'] += 1
            
            # Check for var usage (prefer let/const)
            if re.search(r'\bvar\s+', line):
                results['issues'].append({
                    'type': 'var_usage',
                    'severity': 'medium',
                    'message': "Use 'let' or 'const' instead of 'var'",
                    'line': i
                })
                results['warning_count'] += 1
        
        return results
    
    def _analyze_generic(self, code: str) -> Dict[str, Any]:
        """Generic analysis for unsupported languages"""
        results = {
            'language': 'generic',
            'issues': [],
            'metrics': {},
            'error_count': 0,
            'warning_count': 0,
            'complexity_score': 0
        }
        
        lines = code.split('\n')
        
        # Basic checks
        for i, line in enumerate(lines, 1):
            # Check line length
            if len(line) > self.line_length_limit:
                results['issues'].append({
                    'type': 'line_too_long',
                    'severity': 'low',
                    'message': f"Line too long ({len(line)} > {self.line_length_limit})",
                    'line': i
                })
                results['warning_count'] += 1
            
            # Check for TODO/FIXME
            if 'TODO' in line or 'FIXME' in line:
                results['issues'].append({
                    'type': 'todo_comment',
                    'severity': 'info',
                    'message': "TODO/FIXME comment found",
                    'line': i
                })
        
        results['metrics']['total_lines'] = len(lines)
        results['metrics']['non_empty_lines'] = len([l for l in lines if l.strip()])
        
        return results
