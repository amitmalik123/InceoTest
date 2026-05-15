# Dockerfile for Playwright Python Test Automation
FROM mcr.microsoft.com/playwright/python:v1.57.0-jammy

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    TEST_ENV=test11

# Create app directory
WORKDIR /app

# Install ODBC Driver for SQL Server (for database connections)
# Also install OpenJDK and wget for Allure reporting
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    apt-transport-https \
    openjdk-11-jdk \
    wget \
    unzip && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
    msodbcsql17 \
    unixodbc-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

# Download and install Allure CLI directly
RUN wget -q https://github.com/allure-framework/allure2/releases/download/2.24.1/allure-2.24.1.tgz && \
    tar -zxf allure-2.24.1.tgz -C /opt/ && \
    ln -s /opt/allure-2.24.1/bin/allure /usr/local/bin/allure && \
    rm allure-2.24.1.tgz && \
    allure --version

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for reports and results
RUN mkdir -p reports/allure-results reports/screenshots testResults

# Set proper permissions
RUN chmod -R 755 /app

# Default command - can be overridden in docker-compose or docker run
CMD ["pytest", "tests/test_runners/", "-v", "--browser=chromium"]
