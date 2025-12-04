# 🚀 Real-World Integration Guide

This guide shows you how to integrate the Multi-modal Code Review AI into real-world development workflows and production environments.

## 🎯 Integration Options

### 1. **GitHub Integration** (Recommended)
Automatically review pull requests and provide feedback.

### 2. **CI/CD Pipeline Integration**
Integrate with Jenkins, GitLab CI, GitHub Actions, etc.

### 3. **Docker Deployment**
Containerized deployment for scalability and consistency.

### 4. **Pre-commit Hooks**
Catch issues before they reach the repository.

---

## 🔧 Quick Setup (5 minutes)

### Option 1: Docker (Easiest)

```bash
# 1. Navigate to the project
cd code_review_ai

# 2. Create deployment files
python integrations/docker_deployment.py

# 3. Build and run
./build.sh
./deploy.sh development

# 4. Test the service
./health-check.sh
```

### Option 2: Local Development

```bash
# 1. Install dependencies (use python3 if python command not found)
python3 -m pip install -r requirements.txt

# 2. Start the service
python3 main.py

# 3. Test in another terminal
curl -X POST http://localhost:8001/review \
  -H "Content-Type: application/json" \
  -d '{"code":"def hello(): return \"world\"","language":"python"}'
```

---

## 🔗 Real-World Integration Examples

### 1. GitHub Pull Request Reviews

#### Setup GitHub Bot

```bash
# 1. Create GitHub App or use Personal Access Token
export GITHUB_TOKEN="your_github_token"

# 2. Install GitHub integration dependencies
pip install PyGithub

# 3. Run the GitHub integration
python integrations/github_integration.py
```

#### GitHub Actions Workflow

Copy `workflows/github_actions.yml` to `.github/workflows/` in your repository:

```yaml
# .github/workflows/code-review.yml
name: AI Code Review

on:
  pull_request:
    branches: [ main ]

jobs:
  ai-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: AI Code Review
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # Start review service
          python code_review_ai/main.py &
          sleep 10
          
          # Run review
          python code_review_ai/integrations/github_integration.py
```

### 2. Jenkins Pipeline Integration

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Code Review') {
            steps {
                script {
                    // Start review service
                    sh 'python code_review_ai/main.py &'
                    sh 'sleep 10'
                    
                    // Run CI/CD integration
                    sh 'python code_review_ai/integrations/ci_cd_integration.py --fail-threshold 70'
                }
            }
            post {
                always {
                    // Archive reports
                    archiveArtifacts artifacts: '*.xml,*.json,*.md', fingerprint: true
                    
                    // Publish test results
                    publishTestResults testResultsPattern: 'code_review_results.xml'
                }
            }
        }
    }
}
```

### 3. GitLab CI Integration

```yaml
# .gitlab-ci.yml
stages:
  - test
  - review
  - deploy

code_review:
  stage: review
  image: python:3.11
  script:
    - pip install -r code_review_ai/requirements.txt
    - cd code_review_ai
    - python main.py &
    - sleep 10
    - python integrations/ci_cd_integration.py --target-branch $CI_MERGE_REQUEST_TARGET_BRANCH_NAME
  artifacts:
    reports:
      junit: code_review_results.xml
    paths:
      - code_review_report.md
      - coverage.json
  only:
    - merge_requests
```

### 4. Pre-commit Hook

```bash
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ai-code-review
        name: AI Code Review
        entry: python code_review_ai/integrations/pre_commit_hook.py
        language: system
        pass_filenames: true
        files: \.(py|js|ts|java)$
```

Create the pre-commit hook:

```python
# integrations/pre_commit_hook.py
#!/usr/bin/env python3
import sys
import subprocess
import requests
import json

def main():
    changed_files = sys.argv[1:]
    
    if not changed_files:
        return 0
    
    # Start review service if not running
    try:
        requests.get('http://localhost:8001/')
    except:
        subprocess.Popen(['python', 'code_review_ai/main.py'])
        time.sleep(5)
    
    failed_files = []
    
    for file_path in changed_files:
        with open(file_path, 'r') as f:
            code = f.read()
        
        response = requests.post('http://localhost:8001/review', json={
            'code': code,
            'language': 'python',  # detect from extension
            'file_path': file_path
        })
        
        if response.status_code == 200:
            result = response.json()
            if result['overall_score'] < 70:  # Configurable threshold
                print(f"❌ {file_path}: Score {result['overall_score']}/100")
                failed_files.append(file_path)
            else:
                print(f"✅ {file_path}: Score {result['overall_score']}/100")
    
    if failed_files:
        print(f"\n{len(failed_files)} files failed code review. Fix issues or use --no-verify to skip.")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
```

---

## 🐳 Production Deployment

### Docker Compose (Recommended for small teams)

```bash
# 1. Generate deployment files
python integrations/docker_deployment.py

# 2. Configure environment
cp .env.example .env
# Edit .env with your settings

# 3. Deploy
docker-compose up -d

# 4. Check status
docker-compose ps
./health-check.sh
```

### Kubernetes (Enterprise)

```bash
# 1. Build and push image
./build.sh
docker push your-registry.com/code-review-ai:latest

# 2. Deploy to Kubernetes
kubectl apply -f k8s-deployment.yaml

# 3. Check deployment
kubectl get pods -l app=code-review-ai
kubectl logs -l app=code-review-ai
```

### Helm Chart

```bash
# 1. Install with Helm
helm install code-review-ai ./helm-chart/code-review-ai

# 2. Upgrade
helm upgrade code-review-ai ./helm-chart/code-review-ai

# 3. Monitor
kubectl get all -l app.kubernetes.io/name=code-review-ai
```

---

## 🔧 Configuration

### Environment Variables

```bash
# API Configuration
export API_HOST=0.0.0.0
export API_PORT=8001
export LOG_LEVEL=INFO

# Review Settings
export MIN_SCORE_THRESHOLD=70
export MAX_FILE_SIZE_MB=10
export REVIEW_TIMEOUT_SECONDS=60

# Integration Settings
export GITHUB_TOKEN=your_token
export SLACK_WEBHOOK_URL=your_webhook
export REDIS_URL=redis://localhost:6379
```

### Custom Configuration File

```yaml
# config.yaml
api:
  host: "0.0.0.0"
  port: 8001
  workers: 4

review:
  thresholds:
    min_score: 70
    complexity_limit: 15
    coverage_target: 0.8
  
  languages:
    python:
      enabled: true
      style_guide: "pep8"
    javascript:
      enabled: true
      style_guide: "eslint"

integrations:
  github:
    enabled: true
    auto_comment: true
  slack:
    enabled: false
    webhook_url: ""
```

---

## 📊 Monitoring & Observability

### Health Checks

```bash
# Basic health check
curl http://localhost:8001/

# Detailed health with metrics
curl http://localhost:8001/health

# Prometheus metrics
curl http://localhost:8001/metrics
```

### Logging

```python
# Custom logging configuration
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('code_review.log'),
        logging.StreamHandler()
    ]
)
```

### Metrics Collection

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'code-review-ai'
    static_configs:
      - targets: ['localhost:8001']
    metrics_path: /metrics
```

---

## 🔒 Security Considerations

### API Security

```python
# Add API key authentication
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.middleware("http")
async def authenticate(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        token = request.headers.get("Authorization")
        if not validate_token(token):
            raise HTTPException(401, "Invalid token")
    
    response = await call_next(request)
    return response
```

### Network Security

```yaml
# docker-compose.yml with network isolation
networks:
  code_review_network:
    driver: bridge

services:
  code-review-ai:
    networks:
      - code_review_network
    ports:
      - "127.0.0.1:8001:8001"  # Bind to localhost only
```

---

## 🚀 Scaling & Performance

### Horizontal Scaling

```yaml
# kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: code-review-ai-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: code-review-ai
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Load Balancing

```nginx
# nginx.conf
upstream code_review_backend {
    server code-review-ai-1:8001;
    server code-review-ai-2:8001;
    server code-review-ai-3:8001;
}

server {
    location / {
        proxy_pass http://code_review_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Caching

```python
# Redis caching for review results
import redis
import hashlib
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_review(code_hash):
    return redis_client.get(f"review:{code_hash}")

def cache_review(code_hash, result, ttl=3600):
    redis_client.setex(f"review:{code_hash}", ttl, json.dumps(result))
```

---

## 🛠 Troubleshooting

### Common Issues

1. **"python command not found"**
   ```bash
   # Use python3 instead
   python3 main.py
   
   # Or create alias
   alias python=python3
   ```

2. **Port already in use**
   ```bash
   # Find process using port 8001
   lsof -i :8001
   
   # Kill process or use different port
   export API_PORT=8002
   python main.py
   ```

3. **Module import errors**
   ```bash
   # Install missing dependencies
   pip install -r requirements.txt
   
   # Check Python path
   export PYTHONPATH=/path/to/code_review_ai:$PYTHONPATH
   ```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python main.py

# Run with profiling
python -m cProfile -o profile.stats main.py
```

### Performance Tuning

```python
# Optimize for your use case
app = FastAPI(
    title="Code Review AI",
    docs_url="/docs" if DEBUG else None,  # Disable docs in production
    redoc_url=None,  # Disable redoc
)

# Add request timeout
@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    try:
        return await asyncio.wait_for(call_next(request), timeout=60.0)
    except asyncio.TimeoutError:
        return JSONResponse({"error": "Request timeout"}, status_code=408)
```

---

## 📈 Success Metrics

Track these metrics to measure integration success:

- **Code Quality Score**: Average score improvement over time
- **Issue Detection Rate**: Critical issues caught before merge
- **Developer Adoption**: Usage statistics and feedback
- **Time to Review**: Reduction in manual review time
- **False Positive Rate**: Accuracy of AI recommendations

---

## 🎯 Next Steps

1. **Start Small**: Begin with one repository or team
2. **Gather Feedback**: Collect developer feedback and iterate
3. **Expand Gradually**: Roll out to more teams based on success
4. **Customize Rules**: Adapt analysis rules to your coding standards
5. **Monitor & Optimize**: Track metrics and optimize performance

---

## 📞 Support & Resources

- **Documentation**: Check `/docs` endpoint when service is running
- **Examples**: See `example_usage.py` for comprehensive examples
- **Issues**: Report problems via GitHub issues
- **Community**: Join discussions and share experiences

**Ready to revolutionize your code review process? Start with the quick setup above! 🚀**
