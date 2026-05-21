# Docker Guide for DM1 Test Automation 🐳

Complete guide for running tests in Docker containers for consistent, isolated test execution.

---

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Docker Commands](#docker-commands)
- [Docker Compose Services](#docker-compose-services)
- [Running Tests](#running-tests)
- [Environment-Specific Execution](#environment-specific-execution)
- [Parallel Execution](#parallel-execution)
- [Allure Reports](#allure-reports)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## Prerequisites

### Required Software
```bash
# Docker Desktop (Windows/Mac) or Docker Engine (Linux)
docker --version
# Docker version 20.10+

# Docker Compose
docker-compose --version
# Docker Compose version 1.29+
```

### Installation
- **Windows/Mac**: [Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Linux**: [Docker Engine](https://docs.docker.com/engine/install/)

---

## Quick Start

### 1. Build Docker Image
```bash
# Build the image
docker build -t dm1-playwright:latest .

# Or using docker-compose
docker-compose build playwright-test11
```

### 2. Run Tests
```bash
# Run all tests in test11 environment
docker-compose up playwright-test11

# Run in background
docker-compose up -d playwright-test11

# View logs
docker-compose logs -f playwright-test11
```

### 3. View Reports
```bash
# Reports are saved to ./reports/ directory
# Open reports/pytest_report.html in browser
```

---

## Docker Commands

### Build Commands
```bash
# Build image
docker build -t dm1-playwright:latest .

# Build with no cache (fresh build)
docker build --no-cache -t dm1-playwright:latest .

# Build specific service
docker-compose build playwright-test11
```

### Run Commands
```bash
# Run single container
docker run --rm \
  -e TEST_ENV=test11 \
  -v $(pwd)/reports:/app/reports \
  dm1-playwright:latest

# Run with custom command
docker run --rm \
  -e TEST_ENV=test11 \
  -v $(pwd)/reports:/app/reports \
  dm1-playwright:latest \
  pytest tests/ui/ -v --browser=chromium

# Interactive mode (for debugging)
docker run -it --rm \
  -e TEST_ENV=test11 \
  -v $(pwd)/reports:/app/reports \
  dm1-playwright:latest /bin/bash
```

### Management Commands
```bash
# List running containers
docker ps

# Stop all containers
docker-compose down

# Remove all stopped containers
docker container prune

# Remove images
docker rmi dm1-playwright:latest

# View logs
docker logs <container_id>
docker-compose logs -f playwright-test11
```

---

## Docker Compose Services

### Available Services

| Service | Environment | Purpose |
|---------|-------------|---------|
| `playwright-test11` | test11 | Run tests in test11 environment |
| `playwright-test12` | test12 | Run tests in test12 environment |
| `playwright-qa` | qa | Run tests in QA environment |
| `playwright-parallel` | test11 | Run tests in parallel (4 workers) |
| `playwright-ui-only` | test11 | Run only UI tests |
| `playwright-bdd-only` | test11 | Run only BDD tests |
| `playwright-api-only` | test11 | Run only API tests |
| `allure` | - | Allure report server |

### Service Details

#### Full Test Suite
```yaml
playwright-test11:
  - Runs all tests (UI, BDD, API)
  - Environment: test11
  - Browser: Chromium headless
  - Generates pytest HTML and Allure reports
```

#### Parallel Execution
```yaml
playwright-parallel:
  - 4 parallel workers (pytest-xdist)
  - Faster execution for large test suites
  - Same environment as test11
```

#### Test Type Specific
```yaml
playwright-ui-only:    # UI tests only
playwright-bdd-only:   # BDD features only
playwright-api-only:   # API tests only (no browser)
```

---

## Running Tests

### Run All Tests
```bash
# Test11 environment
docker-compose up playwright-test11

# Test12 environment
docker-compose up playwright-test12

# QA environment
docker-compose up playwright-qa
```

### Run Specific Test Types
```bash
# UI tests only
docker-compose up playwright-ui-only

# BDD tests only
docker-compose up playwright-bdd-only

# API tests only
docker-compose up playwright-api-only
```

### Run with Tags/Markers
```bash
# Run smoke tests
docker run --rm \
  -e TEST_ENV=test11 \
  -v $(pwd)/reports:/app/reports \
  dm1-playwright:latest \
  pytest tests/ -v -m smoke --browser=chromium

# Run regression tests
docker run --rm \
  -e TEST_ENV=test11 \
  -v $(pwd)/reports:/app/reports \
  dm1-playwright:latest \
  pytest tests/ -v -m regression --browser=chromium
```

### Run Specific Test File
```bash
# Single test file
docker run --rm \
  -e TEST_ENV=test11 \
  -v $(pwd)/reports:/app/reports \
  dm1-playwright:latest \
  pytest tests/ui/test_roth_conversion.py -v --browser=chromium
```

---

## Environment-Specific Execution

### Test11 Environment
```bash
docker-compose up playwright-test11

# Or with docker run
docker run --rm \
  -e TEST_ENV=test11 \
  -v $(pwd)/reports:/app/reports \
  -v $(pwd)/config:/app/config:ro \
  dm1-playwright:latest
```

### Test12 Environment
```bash
docker-compose up playwright-test12

# Or with custom database configs
docker run --rm \
  -e TEST_ENV=test12 \
  -v $(pwd)/reports:/app/reports \
  -v $(pwd)/config:/app/config:ro \
  dm1-playwright:latest
```

### QA Environment
```bash
docker-compose up playwright-qa
```

### Custom Environment
```bash
# Set any environment
docker run --rm \
  -e TEST_ENV=silo \
  -v $(pwd)/reports:/app/reports \
  dm1-playwright:latest
```

---

## Parallel Execution

### Using Docker Compose
```bash
# Run with 4 parallel workers
docker-compose up playwright-parallel
```

### Custom Parallel Workers
```bash
# 8 parallel workers
docker run --rm \
  -e TEST_ENV=test11 \
  -v $(pwd)/reports:/app/reports \
  dm1-playwright:latest \
  pytest tests/ -v -n 8 --browser=chromium
```

### Distributed Across Multiple Containers
```bash
# Run UI tests in one container
docker-compose up -d playwright-ui-only

# Run BDD tests in another container
docker-compose up -d playwright-bdd-only

# Run API tests in third container
docker-compose up -d playwright-api-only

# Monitor all
docker-compose logs -f
```

---

## Allure Reports

### Start Allure Server
```bash
# Start Allure service
docker-compose up -d allure

# Access at http://localhost:5050
```

### Generate Reports After Tests
```bash
# 1. Run tests with allure results
docker-compose up playwright-test11

# 2. Start Allure server
docker-compose up -d allure

# 3. Open browser to http://localhost:5050
# 4. Click "Generate Report" or it auto-generates

# 5. Stop Allure when done
docker-compose down allure
```

### Allure with Custom Port
```bash
# Edit docker-compose.yml ports section:
# - "8080:5050"  # Map to port 8080 instead

docker-compose up -d allure
# Access at http://localhost:8080
```

---

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs playwright-test11

# Check if port conflicts
docker ps | grep 5050

# Rebuild image
docker-compose build --no-cache playwright-test11
```

### Tests Failing in Docker (but work locally)
```bash
# 1. Check environment variables
docker exec -it dm1-playwright-test11 env

# 2. Check config files are mounted
docker exec -it dm1-playwright-test11 ls -la /app/config

# 3. Run interactively to debug
docker run -it --rm \
  -e TEST_ENV=test11 \
  -v $(pwd):/app \
  dm1-playwright:latest /bin/bash

# Inside container:
pytest tests/ui/test_login.py -v -s
```

### Database Connection Issues
```bash
# Ensure ODBC driver is installed (already in Dockerfile)
docker exec -it <container_id> odbcinst -q -d

# Test database connection
docker exec -it <container_id> python -c "
from utils.database import get_db_from_vault
db = get_db_from_vault('transfer')
db.connect()
print('Connection successful')
"
```

### Reports Not Generated
```bash
# Check volume mounts
docker-compose config

# Ensure reports directory exists locally
mkdir -p reports/allure-results testResults

# Check permissions
chmod -R 755 reports testResults

# Run with explicit volume mount
docker run --rm \
  -v "$(pwd)/reports:/app/reports" \
  dm1-playwright:latest
```

### Slow Build Times
```bash
# Use multi-stage build (already in Dockerfile)
# Use .dockerignore to exclude unnecessary files

# Check .dockerignore includes:
# .venv/, reports/, node_modules/, .git/

# Build with BuildKit (faster)
DOCKER_BUILDKIT=1 docker build -t dm1-playwright:latest .
```

---

## Best Practices

### 1. Volume Mounts
```bash
# Always mount reports directory
-v $(pwd)/reports:/app/reports

# Mount config as read-only
-v $(pwd)/config:/app/config:ro

# Don't mount entire project (slow)
# Instead, rebuild image when code changes
```

### 2. Environment Variables
```bash
# Use .env file for sensitive data (not committed)
# docker-compose.yml can reference it:
env_file:
  - .env

# .env file:
DB_PASSWORD=mysecretpassword
API_TOKEN=myapitoken
```

### 3. Multi-Browser Testing
```bash
# Chromium (default)
docker run --rm dm1-playwright:latest pytest tests/ --browser=chromium

# Firefox
docker run --rm dm1-playwright:latest pytest tests/ --browser=firefox

# WebKit
docker run --rm dm1-playwright:latest pytest tests/ --browser=webkit

# All browsers
docker run --rm dm1-playwright:latest pytest tests/ --browser=all
```

### 4. Resource Limits
```bash
# In docker-compose.yml, add resource limits:
services:
  playwright-test11:
    # ... other config ...
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          memory: 2G
```

### 5. CI/CD Integration
```bash
# In Azure Pipeline / GitHub Actions:

# Build once
docker build -t dm1-playwright:latest .

# Run multiple test suites in parallel
docker run --rm dm1-playwright:latest pytest tests/ui/ &
docker run --rm dm1-playwright:latest pytest tests/bdd/ &
docker run --rm dm1-playwright:latest pytest tests/api/ &
wait

# Collect reports
docker cp <container_id>:/app/reports ./reports
```

### 6. Cleanup
```bash
# Regular cleanup
docker system prune -f

# Remove all test containers
docker-compose down --volumes --remove-orphans

# Remove old images
docker image prune -a -f
```

---

## PowerShell Commands (Windows)

### Build and Run
```powershell
# Build
docker build -t dm1-playwright:latest .

# Run with volume mount (PowerShell syntax)
docker run --rm `
  -e TEST_ENV=test11 `
  -v ${PWD}/reports:/app/reports `
  dm1-playwright:latest

# Docker Compose
docker-compose up playwright-test11
```

### Interactive Debugging
```powershell
# Start interactive session
docker run -it --rm `
  -e TEST_ENV=test11 `
  -v ${PWD}:/app `
  dm1-playwright:latest /bin/bash
```

---

## Advanced Usage

### Custom Dockerfile for Specific Needs
```dockerfile
# Extend base Dockerfile
FROM dm1-playwright:latest

# Install additional tools
RUN apt-get update && apt-get install -y vim

# Add custom scripts
COPY scripts/ /app/scripts/
```

### Network Isolation
```bash
# Create custom network
docker network create test-network

# Run containers on same network
docker run --network=test-network dm1-playwright:latest
```

### Multi-Stage Deployment
```bash
# Dev environment
docker-compose -f docker-compose.yml up

# Production-like environment
docker-compose -f docker-compose.prod.yml up
```

---

## Summary

### Key Benefits of Docker
✅ **Consistent Environment** - Same setup on all machines
✅ **Isolated Execution** - No dependency conflicts
✅ **Easy CI/CD** - Simple integration with pipelines
✅ **Parallel Execution** - Run multiple environments simultaneously
✅ **Reproducible** - Same results every time
✅ **Clean State** - Fresh environment for each run

### Common Commands Quick Reference
```bash
# Build
docker build -t dm1-playwright:latest .

# Run all tests
docker-compose up playwright-test11

# Run in background
docker-compose up -d playwright-test11

# View logs
docker-compose logs -f playwright-test11

# Stop containers
docker-compose down

# Cleanup
docker system prune -f
```

---

For more help, see [FRAMEWORK_GUIDE.md](FRAMEWORK_GUIDE.md) or raise an issue.
