"""
Docker deployment configuration and utilities
"""

import os
import subprocess
import json
from typing import Dict, Any

def create_dockerfile():
    """Create Dockerfile for the code review AI service"""
    
    dockerfile_content = '''# Multi-modal Code Review AI Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \\
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8001/ || exit 1

# Run the application
CMD ["python", "main.py"]
'''
    
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile_content)
    
    print("✅ Created Dockerfile")

def create_docker_compose():
    """Create docker-compose.yml for full stack deployment"""
    
    compose_content = '''version: '3.8'

services:
  code-review-ai:
    build: .
    ports:
      - "8001:8001"
    environment:
      - PYTHONPATH=/app
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
      - ./reports:/app/reports
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - code-review-ai
    restart: unless-stopped

volumes:
  redis_data:
'''
    
    with open('docker-compose.yml', 'w') as f:
        f.write(compose_content)
    
    print("✅ Created docker-compose.yml")

def create_nginx_config():
    """Create nginx configuration for load balancing and SSL"""
    
    nginx_content = '''events {
    worker_connections 1024;
}

http {
    upstream code_review_api {
        server code-review-ai:8001;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    server {
        listen 80;
        server_name localhost;

        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name localhost;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";

        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://code_review_api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Health check
        location /health {
            proxy_pass http://code_review_api/;
            access_log off;
        }

        # Static files (if any)
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
'''
    
    with open('nginx.conf', 'w') as f:
        f.write(nginx_content)
    
    print("✅ Created nginx.conf")

def create_kubernetes_manifests():
    """Create Kubernetes deployment manifests"""
    
    # Deployment
    deployment_yaml = '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: code-review-ai
  labels:
    app: code-review-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: code-review-ai
  template:
    metadata:
      labels:
        app: code-review-ai
    spec:
      containers:
      - name: code-review-ai
        image: code-review-ai:latest
        ports:
        - containerPort: 8001
        env:
        - name: LOG_LEVEL
          value: "INFO"
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: code-review-ai-service
spec:
  selector:
    app: code-review-ai
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8001
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: code-review-ai-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  rules:
  - host: code-review-ai.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: code-review-ai-service
            port:
              number: 80
'''
    
    with open('k8s-deployment.yaml', 'w') as f:
        f.write(deployment_yaml)
    
    print("✅ Created k8s-deployment.yaml")

def create_helm_chart():
    """Create Helm chart for Kubernetes deployment"""
    
    os.makedirs('helm-chart/code-review-ai/templates', exist_ok=True)
    
    # Chart.yaml
    chart_yaml = '''apiVersion: v2
name: code-review-ai
description: Multi-modal Code Review AI Helm Chart
type: application
version: 0.1.0
appVersion: "1.0.0"
'''
    
    with open('helm-chart/code-review-ai/Chart.yaml', 'w') as f:
        f.write(chart_yaml)
    
    # values.yaml
    values_yaml = '''replicaCount: 3

image:
  repository: code-review-ai
  pullPolicy: IfNotPresent
  tag: "latest"

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: true
  className: "nginx"
  annotations:
    nginx.ingress.kubernetes.io/rate-limit: "100"
  hosts:
    - host: code-review-ai.example.com
      paths:
        - path: /
          pathType: Prefix

resources:
  limits:
    cpu: 500m
    memory: 1Gi
  requests:
    cpu: 250m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80

redis:
  enabled: true
  auth:
    enabled: false
'''
    
    with open('helm-chart/code-review-ai/values.yaml', 'w') as f:
        f.write(values_yaml)
    
    print("✅ Created Helm chart")

def create_deployment_scripts():
    """Create deployment and management scripts"""
    
    # Build script
    build_script = '''#!/bin/bash
set -e

echo "🏗️  Building Code Review AI Docker image..."

# Build the image
docker build -t code-review-ai:latest .

# Tag for registry (update with your registry)
docker tag code-review-ai:latest your-registry.com/code-review-ai:latest

echo "✅ Build complete!"
echo "To push to registry: docker push your-registry.com/code-review-ai:latest"
'''
    
    with open('build.sh', 'w') as f:
        f.write(build_script)
    os.chmod('build.sh', 0o755)
    
    # Deploy script
    deploy_script = '''#!/bin/bash
set -e

ENVIRONMENT=${1:-development}

echo "🚀 Deploying Code Review AI to $ENVIRONMENT..."

case $ENVIRONMENT in
  "development")
    echo "Starting development environment with docker-compose..."
    docker-compose up -d
    ;;
  "staging"|"production")
    echo "Deploying to Kubernetes..."
    kubectl apply -f k8s-deployment.yaml
    kubectl rollout status deployment/code-review-ai
    ;;
  *)
    echo "Unknown environment: $ENVIRONMENT"
    echo "Usage: ./deploy.sh [development|staging|production]"
    exit 1
    ;;
esac

echo "✅ Deployment complete!"
'''
    
    with open('deploy.sh', 'w') as f:
        f.write(deploy_script)
    os.chmod('deploy.sh', 0o755)
    
    # Health check script
    health_script = '''#!/bin/bash

API_URL=${1:-http://localhost:8001}

echo "🏥 Checking health of Code Review AI at $API_URL..."

# Basic health check
response=$(curl -s -o /dev/null -w "%{http_code}" $API_URL/)

if [ $response -eq 200 ]; then
    echo "✅ Service is healthy"
    
    # Test API endpoint
    echo "🧪 Testing review endpoint..."
    curl -s -X POST $API_URL/review \\
        -H "Content-Type: application/json" \\
        -d '{"code":"def hello(): return \"world\"","language":"python"}' \\
        | jq '.overall_score' > /dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ API is working correctly"
    else
        echo "❌ API test failed"
        exit 1
    fi
else
    echo "❌ Service is unhealthy (HTTP $response)"
    exit 1
fi
'''
    
    with open('health-check.sh', 'w') as f:
        f.write(health_script)
    os.chmod('health-check.sh', 0o755)
    
    print("✅ Created deployment scripts")

def create_monitoring_config():
    """Create monitoring and observability configuration"""
    
    # Prometheus configuration
    prometheus_config = '''global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'code-review-ai'
    static_configs:
      - targets: ['code-review-ai:8001']
    metrics_path: /metrics
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
'''
    
    with open('prometheus.yml', 'w') as f:
        f.write(prometheus_config)
    
    # Alert rules
    alert_rules = '''groups:
- name: code-review-ai
  rules:
  - alert: CodeReviewAPIDown
    expr: up{job="code-review-ai"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Code Review AI API is down"
      description: "The Code Review AI service has been down for more than 1 minute."

  - alert: HighResponseTime
    expr: http_request_duration_seconds{quantile="0.95"} > 5
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High response time detected"
      description: "95th percentile response time is above 5 seconds."

  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is above 10% for the last 5 minutes."
'''
    
    with open('alert_rules.yml', 'w') as f:
        f.write(alert_rules)
    
    print("✅ Created monitoring configuration")

def main():
    """Create all deployment files"""
    
    print("🚀 Creating deployment configuration for Code Review AI...")
    
    create_dockerfile()
    create_docker_compose()
    create_nginx_config()
    create_kubernetes_manifests()
    create_helm_chart()
    create_deployment_scripts()
    create_monitoring_config()
    
    print("\n✅ All deployment files created!")
    print("\n📋 Next steps:")
    print("1. Build the Docker image: ./build.sh")
    print("2. Deploy locally: ./deploy.sh development")
    print("3. Check health: ./health-check.sh")
    print("4. For production: ./deploy.sh production")
    
    print("\n📁 Files created:")
    files = [
        'Dockerfile',
        'docker-compose.yml', 
        'nginx.conf',
        'k8s-deployment.yaml',
        'helm-chart/',
        'build.sh',
        'deploy.sh', 
        'health-check.sh',
        'prometheus.yml',
        'alert_rules.yml'
    ]
    
    for file in files:
        print(f"  - {file}")

if __name__ == "__main__":
    main()
