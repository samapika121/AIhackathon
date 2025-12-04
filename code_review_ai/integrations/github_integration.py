"""
GitHub Integration for Multi-modal Code Review AI
Automatically reviews pull requests and posts feedback
"""

import os
import json
import requests
from typing import Dict, Any, List
from github import Github
import subprocess
import tempfile

class GitHubCodeReviewBot:
    def __init__(self, github_token: str, review_api_url: str = "http://localhost:8001"):
        self.github = Github(github_token)
        self.review_api_url = review_api_url
        
    def review_pull_request(self, repo_name: str, pr_number: int) -> Dict[str, Any]:
        """
        Review a pull request and post feedback
        """
        try:
            # Get repository and PR
            repo = self.github.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            
            # Get changed files
            changed_files = list(pr.get_files())
            
            review_results = []
            
            for file in changed_files:
                if self._is_reviewable_file(file.filename):
                    # Get file content
                    file_content = self._get_file_content(repo, file.filename, pr.head.sha)
                    
                    # Get test results and coverage for this file
                    test_results = self._get_test_results_for_file(repo, file.filename)
                    coverage_data = self._get_coverage_for_file(repo, file.filename)
                    
                    # Get PR comments related to this file
                    pr_comments = self._get_pr_comments_for_file(pr, file.filename)
                    
                    # Review the file
                    file_review = self._review_file(
                        file_content, 
                        file.filename,
                        test_results,
                        coverage_data,
                        pr_comments
                    )
                    
                    review_results.append({
                        'filename': file.filename,
                        'review': file_review
                    })
            
            # Post review comments
            self._post_review_comments(pr, review_results)
            
            # Post overall PR review
            self._post_pr_review(pr, review_results)
            
            return {
                'status': 'success',
                'files_reviewed': len(review_results),
                'overall_score': self._calculate_overall_pr_score(review_results)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _is_reviewable_file(self, filename: str) -> bool:
        """Check if file should be reviewed"""
        reviewable_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.go', '.rs']
        return any(filename.endswith(ext) for ext in reviewable_extensions)
    
    def _get_file_content(self, repo, filename: str, sha: str) -> str:
        """Get file content from GitHub"""
        try:
            file_content = repo.get_contents(filename, ref=sha)
            return file_content.decoded_content.decode('utf-8')
        except:
            return ""
    
    def _get_test_results_for_file(self, repo, filename: str) -> Dict[str, Any]:
        """Get test results related to the file"""
        # This would integrate with your CI system
        # For now, return mock data or check for test files
        test_filename = filename.replace('.py', '_test.py').replace('src/', 'tests/')
        
        try:
            # Check if test file exists
            repo.get_contents(test_filename)
            return {
                'has_tests': True,
                'test_file': test_filename
            }
        except:
            return {
                'has_tests': False,
                'recommendation': f'Add tests in {test_filename}'
            }
    
    def _get_coverage_for_file(self, repo, filename: str) -> Dict[str, Any]:
        """Get coverage data for the file"""
        # This would integrate with your coverage reporting system
        # Mock implementation
        return {
            'line_coverage': 0.75,  # Would come from actual coverage report
            'branch_coverage': 0.60
        }
    
    def _get_pr_comments_for_file(self, pr, filename: str) -> List[str]:
        """Get PR comments related to specific file"""
        comments = []
        
        # Get review comments
        for comment in pr.get_review_comments():
            if comment.path == filename:
                comments.append(comment.body)
        
        # Get issue comments mentioning the file
        for comment in pr.get_issue_comments():
            if filename in comment.body:
                comments.append(comment.body)
        
        return comments
    
    def _review_file(self, content: str, filename: str, test_results: Dict, 
                    coverage_data: Dict, comments: List[str]) -> Dict[str, Any]:
        """Review a single file using the AI system"""
        
        # Determine language
        language = self._detect_language(filename)
        
        # Prepare review request
        review_request = {
            'code': content,
            'language': language,
            'test_results': test_results,
            'coverage_data': coverage_data,
            'developer_comments': comments,
            'file_path': filename
        }
        
        # Call the review API
        try:
            response = requests.post(
                f"{self.review_api_url}/review",
                json=review_request,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'error': f'Review API error: {response.status_code}',
                    'overall_score': 0
                }
                
        except requests.RequestException as e:
            return {
                'error': f'Failed to connect to review API: {str(e)}',
                'overall_score': 0
            }
    
    def _detect_language(self, filename: str) -> str:
        """Detect programming language from filename"""
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
            if filename.endswith(ext):
                return lang
        
        return 'python'  # default
    
    def _post_review_comments(self, pr, review_results: List[Dict]):
        """Post inline review comments"""
        
        for file_result in review_results:
            filename = file_result['filename']
            review = file_result['review']
            
            if 'issues' in review:
                for issue in review['issues'][:5]:  # Limit to 5 issues per file
                    if 'line' in issue:
                        comment_body = f"**{issue['severity'].upper()}**: {issue['message']}"
                        
                        try:
                            pr.create_review_comment(
                                body=comment_body,
                                commit=pr.head,
                                path=filename,
                                line=issue['line']
                            )
                        except Exception as e:
                            print(f"Failed to post comment: {e}")
    
    def _post_pr_review(self, pr, review_results: List[Dict]):
        """Post overall PR review"""
        
        overall_score = self._calculate_overall_pr_score(review_results)
        total_issues = sum(len(r['review'].get('issues', [])) for r in review_results)
        
        # Create review summary
        summary_parts = [
            f"## 🤖 AI Code Review Summary",
            f"",
            f"**Overall Score**: {overall_score:.1f}/100",
            f"**Files Reviewed**: {len(review_results)}",
            f"**Issues Found**: {total_issues}",
            f""
        ]
        
        # Add top recommendations
        all_suggestions = []
        for result in review_results:
            all_suggestions.extend(result['review'].get('suggestions', []))
        
        if all_suggestions:
            summary_parts.extend([
                "### 🎯 Top Recommendations:",
                ""
            ])
            
            for i, suggestion in enumerate(all_suggestions[:5], 1):
                summary_parts.append(f"{i}. {suggestion}")
            
            summary_parts.append("")
        
        # Add file-by-file breakdown
        summary_parts.extend([
            "### 📁 File Analysis:",
            ""
        ])
        
        for result in review_results:
            filename = result['filename']
            review = result['review']
            file_score = review.get('overall_score', 0)
            
            status_emoji = "✅" if file_score >= 80 else "⚠️" if file_score >= 60 else "❌"
            summary_parts.append(f"- {status_emoji} **{filename}**: {file_score:.1f}/100")
        
        review_body = "\n".join(summary_parts)
        
        # Determine review event
        if overall_score >= 80:
            event = "APPROVE"
        elif overall_score >= 60:
            event = "COMMENT"
        else:
            event = "REQUEST_CHANGES"
        
        try:
            pr.create_review(
                body=review_body,
                event=event
            )
        except Exception as e:
            print(f"Failed to post PR review: {e}")
    
    def _calculate_overall_pr_score(self, review_results: List[Dict]) -> float:
        """Calculate overall PR score"""
        if not review_results:
            return 0
        
        scores = [r['review'].get('overall_score', 0) for r in review_results]
        return sum(scores) / len(scores)

# GitHub Actions Integration
def github_action_handler():
    """Handler for GitHub Actions workflow"""
    
    # Get environment variables
    github_token = os.getenv('GITHUB_TOKEN')
    repo_name = os.getenv('GITHUB_REPOSITORY')
    pr_number = int(os.getenv('PR_NUMBER', 0))
    
    if not all([github_token, repo_name, pr_number]):
        print("Missing required environment variables")
        return
    
    # Initialize bot
    bot = GitHubCodeReviewBot(github_token)
    
    # Review PR
    result = bot.review_pull_request(repo_name, pr_number)
    
    print(f"Review result: {json.dumps(result, indent=2)}")
    
    # Set GitHub Actions output
    if result['status'] == 'success':
        print(f"::set-output name=score::{result['overall_score']}")
        print(f"::set-output name=files_reviewed::{result['files_reviewed']}")
    else:
        print(f"::error::Review failed: {result.get('error', 'Unknown error')}")
        exit(1)

if __name__ == "__main__":
    github_action_handler()
