# Multi-modal Code Review AI

A comprehensive AI-powered code review system that combines static analysis, test results, coverage data, and developer comments to provide holistic feedback and actionable insights.

## Features

### 🔍 **Multi-Modal Analysis**
- **Static Code Analysis**: Complexity, style, and quality metrics
- **Test Result Analysis**: Test quality, pass rates, and failure patterns
- **Coverage Analysis**: Line, branch, and function coverage insights
- **Comment Analysis**: Developer sentiment and documentation quality
- **AI-Powered Insights**: Intelligent pattern recognition and recommendations

### 🎯 **Key Capabilities**
- **Holistic Code Health Score**: Combined metric from all analysis types
- **Priority Issue Detection**: Automatically identifies critical problems
- **Improvement Roadmap**: Phased plan for code quality enhancement
- **Technical Debt Assessment**: Quantifies and categorizes technical debt
- **Pattern Recognition**: Detects complex quality patterns across metrics

## Quick Start

### Installation

```bash
# Clone or navigate to the code_review_ai directory
cd code_review_ai

# Install dependencies
pip install -r requirements.txt
```

### Start the API Server

```bash
python main.py
```

The API will be available at `http://localhost:8001`

### API Documentation

Visit `http://localhost:8001/docs` for interactive API documentation.

## Usage Examples

### 1. Basic Code Review via API

```python
import requests

# Prepare your code review request
review_request = {
    "code": """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
    """,
    "language": "python",
    "test_results": {
        "tests": [
            {"nodeid": "test_fib", "outcome": "passed"}
        ]
    },
    "coverage_data": {
        "line_coverage": 0.85,
        "branch_coverage": 0.70
    },
    "developer_comments": [
        "This function needs optimization",
        "TODO: Add memoization"
    ]
}

# Send review request
response = requests.post(
    "http://localhost:8001/review",
    json=review_request
)

result = response.json()
print(f"Code Health Score: {result['overall_score']}")
print(f"Summary: {result['summary']}")
```

### 2. File Upload Review

```python
import requests

# Upload files for review
files = {
    'code_file': open('my_code.py', 'rb'),
    'test_file': open('test_results.json', 'rb'),
    'coverage_file': open('coverage.json', 'rb')
}

response = requests.post(
    "http://localhost:8001/upload-file-review",
    files=files
)

result = response.json()
```

### 3. Programmatic Usage

```python
from static_analyzer import StaticCodeAnalyzer
from ai_reviewer import AIReviewer

# Analyze code directly
analyzer = StaticCodeAnalyzer()
results = analyzer.analyze(code, "python")

# Generate AI insights
ai_reviewer = AIReviewer()
insights = ai_reviewer.generate_insights({
    'static_analysis': results,
    'code': code
})

print(f"Health Score: {insights['code_health_score']}")
```

## API Endpoints

### `POST /review`
Comprehensive code review with all analysis types.

**Request Body:**
```json
{
    "code": "string",
    "language": "python",
    "test_results": {},
    "coverage_data": {},
    "developer_comments": [],
    "file_path": "optional"
}
```

**Response:**
```json
{
    "overall_score": 85.5,
    "issues": [...],
    "suggestions": [...],
    "test_analysis": {...},
    "coverage_analysis": {...},
    "comment_analysis": {...},
    "ai_insights": [...],
    "summary": "Code health score: 85.5/100...",
    "timestamp": "2024-01-01T12:00:00"
}
```

### `POST /upload-file-review`
Upload files for review (code, test results, coverage data).

## Analysis Components

### 🔧 Static Analysis
- **Complexity Metrics**: Cyclomatic complexity, function length
- **Code Quality**: Style violations, best practices
- **Error Detection**: Syntax errors, potential bugs
- **Language Support**: Python, JavaScript, TypeScript, Java, C++

### 🧪 Test Analysis
- **Test Quality**: Pass rates, execution time, test patterns
- **Failure Analysis**: Failed test categorization and impact
- **Coverage Integration**: Test effectiveness measurement
- **Framework Support**: pytest, Jest, JUnit

### 📊 Coverage Analysis
- **Multi-Level Coverage**: Line, branch, function coverage
- **Hotspot Identification**: Low-coverage areas needing attention
- **Critical Path Analysis**: Uncovered important code paths
- **Format Support**: coverage.py, LCOV, Istanbul/NYC

### 💬 Comment Analysis
- **Sentiment Analysis**: Developer feedback interpretation
- **Documentation Quality**: Comment coverage and usefulness
- **Action Item Extraction**: TODO, FIXME, review requests
- **Quality Scoring**: Comment effectiveness metrics

### 🤖 AI Insights
- **Pattern Recognition**: Cross-metric quality patterns
- **Risk Assessment**: Technical debt and maintenance risks
- **Improvement Roadmap**: Prioritized enhancement plan
- **Smart Recommendations**: Context-aware suggestions

## Configuration

### Analyzer Settings

```python
# Static Analyzer
static_analyzer = StaticCodeAnalyzer()
static_analyzer.complexity_threshold = 10
static_analyzer.line_length_limit = 100

# Coverage Analyzer  
coverage_analyzer = CoverageAnalyzer()
coverage_analyzer.min_line_coverage = 0.8
coverage_analyzer.min_branch_coverage = 0.7

# Comment Analyzer
comment_analyzer = CommentAnalyzer()
comment_analyzer.min_comment_ratio = 0.1
```

## Real-World Use Cases

### 1. **Pre-commit Hooks**
```bash
# Run before each commit
python -c "
from main import review_code
result = review_code('path/to/changed/files')
if result['overall_score'] < 70:
    exit(1)
"
```

### 2. **CI/CD Integration**
```yaml
# GitHub Actions example
- name: Code Review AI
  run: |
    python code_review_ai/main.py --ci-mode
    python -m pytest --cov=. --cov-report=json
    curl -X POST localhost:8001/review -d @review_data.json
```

### 3. **Pull Request Reviews**
- Automated PR analysis with comprehensive feedback
- Integration with GitHub/GitLab review systems
- Team collaboration insights

### 4. **Code Quality Audits**
- Periodic codebase health assessments
- Technical debt tracking and prioritization
- Quality trend analysis over time

## Advanced Features

### Custom Analysis Rules

```python
# Add custom static analysis rules
class CustomAnalyzer(StaticCodeAnalyzer):
    def analyze_custom_patterns(self, code):
        # Your custom analysis logic
        pass
```

### Integration Examples

```python
# Slack notifications
def send_review_to_slack(review_result):
    if review_result['overall_score'] < 60:
        send_slack_alert(review_result['summary'])

# Database logging
def log_review_metrics(review_result):
    db.insert_review_metrics({
        'timestamp': review_result['timestamp'],
        'score': review_result['overall_score'],
        'issues': len(review_result['issues'])
    })
```

## Performance Considerations

- **Parallel Analysis**: Multiple analyzers run concurrently
- **Caching**: Results cached for repeated analysis
- **Scalability**: Designed for large codebases
- **Resource Management**: Configurable timeouts and limits

## Troubleshooting

### Common Issues

1. **Pylint not found**: Install with `pip install pylint`
2. **Large file timeouts**: Increase timeout settings
3. **Memory usage**: Process files in chunks for large codebases

### Debug Mode

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- **Documentation**: Check `/docs` endpoint when server is running
- **Examples**: See `example_usage.py` for comprehensive examples
- **Issues**: Report bugs and feature requests via GitHub issues

---

**Multi-modal Code Review AI** - Elevating code quality through intelligent, comprehensive analysis.
