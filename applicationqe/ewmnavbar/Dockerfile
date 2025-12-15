# Multi-stage Dockerfile for EWM-NavBar Playwright Tests
# Stage 1: Builder - Install dependencies and Playwright browsers
FROM node:22-bookworm AS builder

WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    libgconf-2-4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libatspi2.0-0 \
    libxss1 \
    libappindicator1 \
    libindicator7 \
    libnss3 \
    libgbm-dev \
    libxshmfence1 \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy package files
COPY package.json package-lock.json ./

# Install npm dependencies
RUN npm ci

# Install Playwright browsers
RUN npm run postinstall

# Stage 2: Runtime - Minimal image with tests and dependencies
FROM node:22-bookworm

WORKDIR /app

# Install system dependencies for Playwright runtime
RUN apt-get update && apt-get install -y \
    libgconf-2-4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libatspi2.0-0 \
    libxss1 \
    libappindicator1 \
    libindicator7 \
    libnss3 \
    libgbm-dev \
    libxshmfence1 \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Copy installed dependencies from builder
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /root/.cache/ms-playwright ./root/.cache/ms-playwright

# Copy project files
COPY . .

# Install Python dependencies for reporter
RUN if [ -f framework/reporter/requirements.txt ]; then \
    pip install --no-cache-dir -r framework/reporter/requirements.txt; \
    fi

# Create directories for test results and reports
RUN mkdir -p allure-results playwright-report reports test-results

# Set environment variables
ENV NODE_ENV=production \
    PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 \
    DISPLAY=:99

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "console.log('OK')" || exit 1

# Default command - run all tests
CMD ["npm", "run", "test:e2e"]
