"""
CI/CD Integration for Multi-modal Code Review AI
Integrates with Jenkins, GitLab CI, GitHub Actions, and other CI systems
"""

import os
import json
import subprocess
import tempfile
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path

class CICDIntegration:
    def __init__(self, review_api_url: str = "http://localhost:8001"):
        self.review_api_url = review_api_url
        self.ci_system = self._detect_ci_system()
        
    def _detect_ci_system(self) -> str:
        """Detect which CI system we're running in"""
        if os.getenv('GITHUB_ACTIONS'):
            return 'github_actions'
        elif os.getenv('GITLAB_CI'):
            return 'gitlab_ci'
        elif os.getenv('JENKINS_URL'):
            return 'jenkins'
        elif os.getenv('CIRCLECI'):
            return 'circleci'
        elif os.getenv('TRAVIS'):
            return 'travis'
        else:
            return 'unknown'
    
    def run_code_review_pipeline(self, 
                                target_branch: str = 'main',
                                fail_threshold: float = 60.0) -> Dict[str, Any]:
        """
        Run complete code review pipeline in CI/CD
        """
        results = {
            'ci_system': self.ci_system,
            'status': 'running',
            'steps': {},
            'overall_score': 0,
            'should_fail': False
        }
        
        try:
            # Step 1: Get changed files
            print("🔍 Getting changed files...")
            changed_files = self._get_changed_files(target_branch)
            results['steps']['changed_files'] = {
                'status': 'success',
                'count': len(changed_files),
                'files': changed_files
            }
            
            # Step 2: Run tests and collect results
            print("🧪 Running tests...")
            test_results = self._run_tests()
            results['steps']['tests'] = test_results
            
            # Step 3: Generate coverage report
            print("📊 Generating coverage report...")
            coverage_results = self._generate_coverage()
            results['steps']['coverage'] = coverage_results
            
            # Step 4: Review changed files
            print("🤖 Running AI code review...")
            review_results = []
            
            for file_path in changed_files:
                if self._should_review_file(file_path):
                    file_review = self._review_single_file(
                        file_path, 
                        test_results, 
                        coverage_results
                    )
                    review_results.append(file_review)
            
            results['steps']['review'] = {
                'status': 'success',
                'files_reviewed': len(review_results),
                'results': review_results
            }
            
            # Step 5: Calculate overall score
            overall_score = self._calculate_pipeline_score(review_results, test_results, coverage_results)
            results['overall_score'] = overall_score
            results['should_fail'] = overall_score < fail_threshold
            
            # Step 6: Generate reports
            print("📝 Generating reports...")
            self._generate_ci_reports(results)
            
            # Step 7: Set CI outputs
            self._set_ci_outputs(results)
            
            results['status'] = 'success'
            
        except Exception as e:
            results['status'] = 'error'
            results['error'] = str(e)
            print(f"❌ Pipeline failed: {e}")
        
        return results
    
    def _get_changed_files(self, target_branch: str) -> List[str]:
        """Get list of changed files"""
        try:
            # Get changed files using git
            cmd = f"git diff --name-only origin/{target_branch}...HEAD"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
                return files
            else:
                # Fallback: get all Python files (for demo)
                return [str(p) for p in Path('.').rglob('*.py')]
                
        except Exception as e:
            print(f"Warning: Could not get changed files: {e}")
            return []
    
    def _run_tests(self) -> Dict[str, Any]:
        """Run test suite and collect results"""
        test_results = {
            'status': 'success',
            'framework': 'pytest',
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'execution_time': 0,
            'details': {}
        }
        
        try:
            # Try to run pytest with JSON output
            cmd = "python3 -m pytest --tb=short --json-report --json-report-file=test_results.json"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
            
            # Try to read JSON results
            try:
                with open('test_results.json', 'r') as f:
                    pytest_data = json.load(f)
                
                test_results.update({
                    'total_tests': pytest_data.get('summary', {}).get('total', 0),
                    'passed': pytest_data.get('summary', {}).get('passed', 0),
                    'failed': pytest_data.get('summary', {}).get('failed', 0),
                    'execution_time': pytest_data.get('duration', 0),
                    'details': pytest_data
                })
                
            except (FileNotFoundError, json.JSONDecodeError):
                # Parse from stdout if JSON not available
                if "passed" in result.stdout:
                    test_results['status'] = 'success'
                elif "failed" in result.stdout:
                    test_results['status'] = 'partial'
                
        except subprocess.TimeoutExpired:
            test_results['status'] = 'timeout'
        except Exception as e:
            test_results['status'] = 'error'
            test_results['error'] = str(e)
        
        return test_results
    
    def _generate_coverage(self) -> Dict[str, Any]:
        """Generate code coverage report"""
        coverage_results = {
            'status': 'success',
            'line_coverage': 0,
            'branch_coverage': 0,
            'details': {}
        }
        
        try:
            # Run coverage
            subprocess.run("python3 -m coverage run -m pytest", shell=True, timeout=300)
            
            # Generate JSON report
            result = subprocess.run(
                "python3 -m coverage json -o coverage.json", 
                shell=True, 
                capture_output=True, 
                text=True
            )
            
            # Read coverage data
            try:
                with open('coverage.json', 'r') as f:
                    coverage_data = json.load(f)
                
                totals = coverage_data.get('totals', {})
                coverage_results.update({
                    'line_coverage': totals.get('percent_covered', 0) / 100,
                    'branch_coverage': totals.get('percent_covered_display', 0) / 100,
                    'details': coverage_data
                })
                
            except (FileNotFoundError, json.JSONDecodeError):
                # Try to parse from coverage report
                result = subprocess.run(
                    "python3 -m coverage report", 
                    shell=True, 
                    capture_output=True, 
                    text=True
                )
                
                # Simple parsing of coverage percentage
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'TOTAL' in line:
                        parts = line.split()
                        if len(parts) > 3 and '%' in parts[-1]:
                            coverage_results['line_coverage'] = float(parts[-1].replace('%', '')) / 100
                
        except Exception as e:
            coverage_results['status'] = 'error'
            coverage_results['error'] = str(e)
        
        return coverage_results
    
    def _should_review_file(self, file_path: str) -> bool:
        """Check if file should be reviewed"""
        reviewable_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.go', '.rs']
        return any(file_path.endswith(ext) for ext in reviewable_extensions)
    
    def _review_single_file(self, file_path: str, test_results: Dict, coverage_results: Dict) -> Dict[str, Any]:
        """Review a single file"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Prepare review request
            review_request = {
                'code': content,
                'language': self._detect_language(file_path),
                'test_results': test_results.get('details', {}),
                'coverage_data': coverage_results.get('details', {}),
                'developer_comments': [],
                'file_path': file_path
            }
            
            # Call review API
            response = requests.post(
                f"{self.review_api_url}/review",
                json=review_request,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                result['file_path'] = file_path
                return result
            else:
                return {
                    'file_path': file_path,
                    'error': f'API error: {response.status_code}',
                    'overall_score': 0
                }
                
        except Exception as e:
            return {
                'file_path': file_path,
                'error': str(e),
                'overall_score': 0
            }
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language"""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust'
        }
        
        for ext, lang in extension_map.items():
            if file_path.endswith(ext):
                return lang
        
        return 'python'
    
    def _calculate_pipeline_score(self, review_results: List[Dict], 
                                 test_results: Dict, coverage_results: Dict) -> float:
        """Calculate overall pipeline score"""
        scores = []
        
        # Review scores (60% weight)
        if review_results:
            review_scores = [r.get('overall_score', 0) for r in review_results]
            avg_review_score = sum(review_scores) / len(review_scores)
            scores.append(avg_review_score * 0.6)
        
        # Test score (25% weight)
        if test_results.get('total_tests', 0) > 0:
            test_pass_rate = test_results.get('passed', 0) / test_results.get('total_tests', 1)
            scores.append(test_pass_rate * 100 * 0.25)
        
        # Coverage score (15% weight)
        coverage_score = coverage_results.get('line_coverage', 0) * 100
        scores.append(coverage_score * 0.15)
        
        return sum(scores) if scores else 0
    
    def _generate_ci_reports(self, results: Dict[str, Any]):
        """Generate CI-specific reports"""
        
        # Generate JUnit XML for test results
        self._generate_junit_xml(results)
        
        # Generate coverage reports
        self._generate_coverage_reports(results)
        
        # Generate code review report
        self._generate_review_report(results)
    
    def _generate_junit_xml(self, results: Dict[str, Any]):
        """Generate JUnit XML report"""
        try:
            review_results = results.get('steps', {}).get('review', {}).get('results', [])
            
            junit_xml = ['<?xml version="1.0" encoding="UTF-8"?>']
            junit_xml.append('<testsuites>')
            junit_xml.append('<testsuite name="CodeReview" tests="{}" failures="{}" errors="0">'.format(
                len(review_results),
                len([r for r in review_results if r.get('overall_score', 0) < 60])
            ))
            
            for result in review_results:
                file_path = result.get('file_path', 'unknown')
                score = result.get('overall_score', 0)
                
                if score >= 60:
                    junit_xml.append(f'<testcase name="{file_path}" classname="CodeReview"/>')
                else:
                    junit_xml.append(f'<testcase name="{file_path}" classname="CodeReview">')
                    junit_xml.append(f'<failure message="Code quality score too low: {score}"/>')
                    junit_xml.append('</testcase>')
            
            junit_xml.append('</testsuite>')
            junit_xml.append('</testsuites>')
            
            with open('code_review_results.xml', 'w') as f:
                f.write('\n'.join(junit_xml))
                
        except Exception as e:
            print(f"Failed to generate JUnit XML: {e}")
    
    def _generate_coverage_reports(self, results: Dict[str, Any]):
        """Generate coverage reports"""
        try:
            # HTML coverage report
            subprocess.run("python -m coverage html -d htmlcov", shell=True)
            
            # Coverage badge
            coverage_results = results.get('steps', {}).get('coverage', {})
            coverage_pct = coverage_results.get('line_coverage', 0) * 100
            
            badge_color = 'brightgreen' if coverage_pct >= 80 else 'yellow' if coverage_pct >= 60 else 'red'
            
            with open('coverage_badge.json', 'w') as f:
                json.dump({
                    'schemaVersion': 1,
                    'label': 'coverage',
                    'message': f'{coverage_pct:.1f}%',
                    'color': badge_color
                }, f)
                
        except Exception as e:
            print(f"Failed to generate coverage reports: {e}")
    
    def _generate_review_report(self, results: Dict[str, Any]):
        """Generate markdown review report"""
        try:
            review_results = results.get('steps', {}).get('review', {}).get('results', [])
            overall_score = results.get('overall_score', 0)
            
            report_lines = [
                '# 🤖 AI Code Review Report',
                '',
                f'**Overall Score**: {overall_score:.1f}/100',
                f'**Files Reviewed**: {len(review_results)}',
                f'**CI System**: {self.ci_system}',
                '',
                '## 📊 Summary',
                ''
            ]
            
            # Score distribution
            excellent = len([r for r in review_results if r.get('overall_score', 0) >= 90])
            good = len([r for r in review_results if 70 <= r.get('overall_score', 0) < 90])
            fair = len([r for r in review_results if 50 <= r.get('overall_score', 0) < 70])
            poor = len([r for r in review_results if r.get('overall_score', 0) < 50])
            
            report_lines.extend([
                f'- 🟢 Excellent (90+): {excellent} files',
                f'- 🟡 Good (70-89): {good} files', 
                f'- 🟠 Fair (50-69): {fair} files',
                f'- 🔴 Poor (<50): {poor} files',
                '',
                '## 📁 File Details',
                ''
            ])
            
            # File-by-file results
            for result in review_results:
                file_path = result.get('file_path', 'unknown')
                score = result.get('overall_score', 0)
                issues = len(result.get('issues', []))
                
                status_emoji = '🟢' if score >= 90 else '🟡' if score >= 70 else '🟠' if score >= 50 else '🔴'
                
                report_lines.extend([
                    f'### {status_emoji} {file_path}',
                    f'**Score**: {score:.1f}/100 | **Issues**: {issues}',
                    ''
                ])
                
                # Top suggestions
                suggestions = result.get('suggestions', [])[:3]
                if suggestions:
                    report_lines.append('**Top Suggestions**:')
                    for suggestion in suggestions:
                        report_lines.append(f'- {suggestion}')
                    report_lines.append('')
            
            with open('code_review_report.md', 'w') as f:
                f.write('\n'.join(report_lines))
                
        except Exception as e:
            print(f"Failed to generate review report: {e}")
    
    def _set_ci_outputs(self, results: Dict[str, Any]):
        """Set CI system specific outputs"""
        
        if self.ci_system == 'github_actions':
            # GitHub Actions outputs
            print(f"::set-output name=overall_score::{results['overall_score']}")
            print(f"::set-output name=should_fail::{results['should_fail']}")
            print(f"::set-output name=files_reviewed::{len(results.get('steps', {}).get('review', {}).get('results', []))}")
            
            # Set step summary
            with open(os.environ.get('GITHUB_STEP_SUMMARY', '/dev/null'), 'a') as f:
                f.write(f"## Code Review Results\n")
                f.write(f"Overall Score: {results['overall_score']:.1f}/100\n")
                f.write(f"Status: {'❌ Failed' if results['should_fail'] else '✅ Passed'}\n")
        
        elif self.ci_system == 'gitlab_ci':
            # GitLab CI artifacts and variables
            os.makedirs('artifacts', exist_ok=True)
            
            with open('artifacts/review_results.json', 'w') as f:
                json.dump(results, f, indent=2)
        
        elif self.ci_system == 'jenkins':
            # Jenkins properties
            with open('review.properties', 'w') as f:
                f.write(f"OVERALL_SCORE={results['overall_score']}\n")
                f.write(f"SHOULD_FAIL={results['should_fail']}\n")

def main():
    """Main CI/CD integration entry point"""
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='CI/CD Code Review Integration')
    parser.add_argument('--target-branch', default='main', help='Target branch for comparison')
    parser.add_argument('--fail-threshold', type=float, default=60.0, help='Minimum score to pass')
    parser.add_argument('--api-url', default='http://localhost:8001', help='Review API URL')
    
    args = parser.parse_args()
    
    # Run integration
    integration = CICDIntegration(args.api_url)
    results = integration.run_code_review_pipeline(args.target_branch, args.fail_threshold)
    
    # Print results
    print(f"\n{'='*60}")
    print("CI/CD CODE REVIEW RESULTS")
    print(f"{'='*60}")
    print(f"Overall Score: {results['overall_score']:.1f}/100")
    print(f"Status: {'FAILED' if results['should_fail'] else 'PASSED'}")
    
    # Exit with appropriate code
    if results['should_fail'] or results['status'] == 'error':
        exit(1)
    else:
        exit(0)

if __name__ == "__main__":
    main()
