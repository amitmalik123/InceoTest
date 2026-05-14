# SonarQube Integration Guide

## 📋 Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Local Setup](#local-setup)
- [CI/CD Integration](#cicd-integration)
- [Configuration](#configuration)
- [Running Analysis](#running-analysis)
- [Quality Gates](#quality-gates)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This framework includes comprehensive SonarQube integration for:
- **Code Quality Analysis**: Detect bugs, code smells, and vulnerabilities
- **Code Coverage**: Track test coverage metrics
- **Security Analysis**: Identify security hotspots and vulnerabilities
- **Technical Debt**: Monitor and manage technical debt
- **CI/CD Integration**: Automated analysis in pipelines

## 📦 Prerequisites

### Required Tools
1. **Python 3.8+** with pip
2. **SonarQube Server** (local or cloud)
3. **SonarScanner CLI** for local analysis
4. **Git** for version control

### Python Dependencies
All required dependencies are in `requirements.txt`:
```bash
pytest-cov    # Code coverage
bandit        # Security analysis
flake8        # Linting
mypy          # Type checking
```

## 🔧 Local Setup

### Step 1: Install SonarQube Server (Local Development)

#### Option A: Using Docker (Recommended)
```bash
# Pull and run SonarQube
docker run -d --name sonarqube -p 9000:9000 sonarqube:latest

# Access at http://localhost:9000
# Default credentials: admin/admin
```

#### Option B: Manual Installation
1. Download from [SonarQube Downloads](https://www.sonarqube.org/downloads/)
2. Extract and run:
   ```bash
   # Windows
   bin\windows-x86-64\StartSonar.bat

   # Linux/Mac
   bin/linux-x86-64/sonar.sh start
   ```

### Step 2: Install SonarScanner CLI

#### Windows
1. Download from [SonarScanner Downloads](https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/)
2. Extract to `C:\sonar-scanner`
3. Add to PATH: `C:\sonar-scanner\bin`

#### Linux/Mac
```bash
# Download and extract
wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-linux.zip
unzip sonar-scanner-cli-5.0.1.3006-linux.zip
sudo mv sonar-scanner-5.0.1.3006-linux /opt/sonar-scanner

# Add to PATH
echo 'export PATH=$PATH:/opt/sonar-scanner/bin' >> ~/.bashrc
source ~/.bashrc
```

### Step 3: Configure SonarQube

1. **Access SonarQube**: Navigate to http://localhost:9000
2. **Login**: Use default credentials (admin/admin)
3. **Create Project**:
   - Click "Create new project"
   - Project key: `python-playwright-automation`
   - Display name: `Python Playwright Automation Framework`
4. **Generate Token**:
   - Go to My Account > Security > Generate Token
   - Name: `local-analysis`
   - Copy the token (you'll need it later)

### Step 4: Set Environment Variables

#### Windows (PowerShell)
```powershell
$env:SONAR_HOST_URL = "http://localhost:9000"
$env:SONAR_TOKEN = "your-generated-token"
```

#### Linux/Mac
```bash
export SONAR_HOST_URL="http://localhost:9000"
export SONAR_TOKEN="your-generated-token"
```

## 🚀 Running Analysis

### Method 1: PowerShell Script (Recommended for Windows)

```powershell
# Basic usage with environment variables
.\run_sonar_analysis.ps1

# Specify parameters directly
.\run_sonar_analysis.ps1 -SonarHost "http://localhost:9000" -SonarToken "your-token"

# Local development mode
.\run_sonar_analysis.ps1 -Local -SonarToken "your-token"

# Skip tests (faster, uses existing reports)
.\run_sonar_analysis.ps1 -SkipTests

# Custom project key
.\run_sonar_analysis.ps1 -ProjectKey "my-custom-project"
```

### Method 2: Manual Steps

```bash
# 1. Install dependencies
pip install -r requirements.txt
pip install pytest-cov bandit

# 2. Run code quality tools
flake8 --output-file=reports/flake8-report.txt pages utils config fixtures
mypy pages utils config fixtures > reports/mypy-report.txt
bandit -r pages utils config fixtures -f json -o reports/bandit-report.json

# 3. Run tests with coverage
pytest tests/ \
  --cov=pages \
  --cov=utils \
  --cov=config \
  --cov=fixtures \
  --cov-report=xml:reports/coverage.xml \
  --junitxml=reports/junit.xml

# 4. Run SonarScanner
sonar-scanner \
  -Dsonar.projectKey=python-playwright-automation \
  -Dsonar.host.url=$SONAR_HOST_URL \
  -Dsonar.login=$SONAR_TOKEN
```

### Method 3: Using Makefile

```bash
# Run complete SonarQube analysis
make sonar

# Run only quality checks
make quality

# Run tests with coverage
make test-coverage
```

## 🔄 CI/CD Integration

### GitHub Actions

The framework includes `.github/workflows/sonarqube-analysis.yml` for GitHub Actions.

**Setup:**
1. Add repository secrets:
   - `SONAR_TOKEN`: Your SonarQube token
   - `SONAR_HOST_URL`: Your SonarQube server URL

2. Push to trigger:
   ```bash
   git push origin main
   ```

### GitLab CI/CD

The framework includes `.gitlab-ci.yml` for GitLab.

**Setup:**
1. Add CI/CD variables in GitLab:
   - `SONAR_TOKEN`: Your SonarQube token
   - `SONAR_HOST_URL`: Your SonarQube server URL

2. Pipeline runs automatically on push/merge requests

### Azure DevOps

The framework includes `azure-pipelines.yml` for Azure DevOps.

**Setup:**
1. Create SonarQube service connection:
   - Project Settings > Service connections
   - New service connection > SonarQube
   - Name: `SonarQube-Connection`

2. Add pipeline variables:
   - `SONAR_TOKEN`: Your SonarQube token

3. Run pipeline

### Jenkins

```groovy
pipeline {
    agent any

    environment {
        SONAR_TOKEN = credentials('sonarqube-token')
        SONAR_HOST_URL = 'http://sonarqube.company.com'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'pip install pytest-cov bandit'
            }
        }

        stage('Code Quality') {
            steps {
                sh '''
                    mkdir -p reports
                    flake8 --output-file=reports/flake8-report.txt pages utils config fixtures || true
                    mypy pages utils config fixtures > reports/mypy-report.txt 2>&1 || true
                    bandit -r pages utils config fixtures -f json -o reports/bandit-report.json || true
                '''
            }
        }

        stage('Test & Coverage') {
            steps {
                sh '''
                    pytest tests/ \
                        --cov=pages --cov=utils --cov=config --cov=fixtures \
                        --cov-report=xml:reports/coverage.xml \
                        --junitxml=reports/junit.xml
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'
                    withSonarQubeEnv('SonarQube') {
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
    }
}
```

## ⚙️ Configuration

### sonar-project.properties

Key configurations in `sonar-project.properties`:

```properties
# Project identification
sonar.projectKey=python-playwright-automation
sonar.projectName=Python Playwright Automation Framework
sonar.projectVersion=1.0.0

# Source paths
sonar.sources=pages,utils,config,fixtures,features/steps
sonar.tests=tests,features

# Exclusions
sonar.exclusions=**/__pycache__/**,**/venv/**,**/*.pyc

# Coverage
sonar.python.coverage.reportPaths=reports/coverage.xml

# Test results
sonar.python.xunit.reportPath=reports/junit.xml
```

### Quality Profiles

Create custom quality profiles in SonarQube:
1. Go to Quality Profiles
2. Create > Python
3. Activate rules based on your standards

### Quality Gates

Configure quality gates:
1. Go to Quality Gates
2. Create or modify gate
3. Set conditions:
   - Coverage > 80%
   - Duplications < 3%
   - Maintainability Rating = A
   - Security Rating = A
   - Reliability Rating = A

## 📊 Metrics and Reports

### Generated Reports

After analysis, the following reports are available:

1. **SonarQube Dashboard**: `http://your-sonarqube-url/dashboard?id=python-playwright-automation`
2. **Coverage Report**: `reports/htmlcov/index.html`
3. **Flake8 Report**: `reports/flake8-report.txt`
4. **MyPy Report**: `reports/mypy-report.txt`
5. **Bandit Report**: `reports/bandit-report.json`

### Key Metrics

Monitor these key metrics in SonarQube:
- **Bugs**: Critical code issues
- **Vulnerabilities**: Security issues
- **Code Smells**: Maintainability issues
- **Coverage**: Test coverage percentage
- **Duplications**: Code duplication percentage
- **Technical Debt**: Estimated time to fix issues

## 🔍 Quality Gates

### Default Quality Gate Conditions

```yaml
Coverage:                    >= 80%
Duplicated Lines:           < 3%
Maintainability Rating:     A
Reliability Rating:         A
Security Rating:            A
Security Hotspots Reviewed: 100%
```

### Custom Conditions

Add custom conditions based on your needs:
- New Code Coverage
- New Duplications
- New Bugs
- New Vulnerabilities
- New Code Smells

## 🐛 Troubleshooting

### Common Issues

#### 1. SonarScanner Not Found
```bash
# Windows - Add to PATH
$env:Path += ";C:\sonar-scanner\bin"

# Linux/Mac
export PATH=$PATH:/opt/sonar-scanner/bin
```

#### 2. Coverage Report Not Found
```bash
# Ensure pytest-cov is installed
pip install pytest-cov

# Run tests to generate coverage
pytest --cov=pages --cov-report=xml:reports/coverage.xml
```

#### 3. Authentication Failed
- Verify `SONAR_TOKEN` is correct
- Check token hasn't expired
- Regenerate token if needed

#### 4. Quality Gate Fails
- Review SonarQube dashboard for issues
- Check coverage metrics
- Fix reported bugs/vulnerabilities
- Reduce code smells

#### 5. Port 9000 Already in Use
```bash
# Windows
netstat -ano | findstr :9000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:9000 | xargs kill -9
```

### Debug Mode

Enable debug logging:
```bash
sonar-scanner -X -Dsonar.verbose=true
```

### Logs Location

Check SonarQube logs:
- Server: `$SONARQUBE_HOME/logs/sonar.log`
- Scanner: `.scannerwork/report-task.txt`

## 📚 Best Practices

1. **Run Locally First**: Test SonarQube analysis locally before CI/CD
2. **Fix Issues Early**: Address bugs and vulnerabilities immediately
3. **Monitor Coverage**: Maintain >= 80% code coverage
4. **Review Security**: Regular security hotspot reviews
5. **Update Rules**: Keep quality profiles current
6. **Clean Code**: Follow SonarQube recommendations
7. **Document Exceptions**: Document why issues are marked as false positives

## 🔗 Resources

- [SonarQube Documentation](https://docs.sonarqube.org/)
- [SonarScanner CLI](https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/)
- [Python Analysis](https://docs.sonarqube.org/latest/analysis/languages/python/)
- [Quality Gates](https://docs.sonarqube.org/latest/user-guide/quality-gates/)
- [Security Rules](https://rules.sonarsource.com/python/type/Security%20Hotspot)

## 📞 Support

For issues or questions:
1. Check SonarQube dashboard for detailed error messages
2. Review logs in `.scannerwork/` directory
3. Consult [SonarQube Community](https://community.sonarsource.com/)
4. Contact your DevOps team for pipeline issues

---

**Happy Testing with Quality Code!** 🚀
