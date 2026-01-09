# Docker Setup for EWM-NavBar Tests

This guide explains how to run EWM-NavBar Playwright tests in Docker containers.

## Files

- **Dockerfile**: Multi-stage Docker image for building and running tests
- **docker-compose.yml**: Orchestration file for test container + optional InfluxDB
- **.dockerignore**: Excludes unnecessary files from Docker context

## Quick Start

### 1. Build the Docker Image

```bash
docker build -t ewm-navbar-tests:latest .
```

### 2. Run Tests in Docker

#### Option A: Using Docker Run (Simple)

```bash
# Run all tests (authenticated + unauthenticated)
docker run --rm \
  -v $(pwd)/test-results:/app/test-results \
  -v $(pwd)/allure-results:/app/allure-results \
  ewm-navbar-tests:latest \
  npm run test:e2e

# Run only authenticated tests
docker run --rm \
  -v $(pwd)/test-results:/app/test-results \
  -v $(pwd)/allure-results:/app/allure-results \
  ewm-navbar-tests:latest \
  npm run test:auth

# Run only unauthenticated tests
docker run --rm \
  -v $(pwd)/test-results:/app/test-results \
  -v $(pwd)/allure-results:/app/allure-results \
  ewm-navbar-tests:latest \
  npm run test:unauth
```

#### Option B: Using Docker Compose (With InfluxDB)

```bash
# Start containers (tests + InfluxDB)
docker-compose up

# Run only tests (InfluxDB must be running)
docker-compose up ewm-navbar-tests

# Run with specific test project
docker-compose run ewm-navbar-tests npm run test:auth

# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Environment Variables

### Test Configuration
- `BROWSER`: Browser to use (chromium, firefox, webkit) - Default: chromium
- `HEADLESS`: Run in headless mode (true/false) - Default: true
- `DEBUG`: Enable debug logging (true/false) - Default: false

### InfluxDB Configuration (Optional)
- `INFLUX_URL`: InfluxDB server URL - Default: http://influxdb:8086
- `INFLUX_ORG`: InfluxDB organization - Default: assetmark
- `INFLUX_BUCKET`: InfluxDB bucket name - Default: qatest
- `INFLUX_TOKEN`: InfluxDB authentication token

### Azure Pipelines Configuration (Optional)
- `SYSTEM_TEAMFOUNDATIONCOLLECTIONURI`: Azure DevOps collection URI
- `SYSTEM_TEAMPROJECT`: Azure DevOps project name
- `BUILD_BUILDID`: Build ID - Default: local
- `BUILD_REASON`: Build reason (Manual, IndividualCI, etc.)

## Custom Commands

Run any npm script inside the container:

```bash
# Run unit tests
docker run --rm ewm-navbar-tests:latest npm run test:unit

# Interactive shell
docker run -it --rm ewm-navbar-tests:latest /bin/bash

# Run specific test file
docker run --rm ewm-navbar-tests:latest npx playwright test auth.setup.ts
```

## Accessing Test Reports

After running tests, reports are available in:

- **Playwright Report**: `./playwright-report/` - Interactive HTML report
- **Allure Results**: `./allure-results/` - Raw Allure test data
- **Test Results**: `./test-results/` - Standard test output

To view Playwright report locally:

```bash
npx playwright show-report ./playwright-report
```

## Docker Compose Services

### ewm-navbar-tests
- **Image**: Local build from Dockerfile
- **Purpose**: Run Playwright tests
- **Default Command**: `npm run test:e2e`
- **Ports**: None exposed (tests run internally)

### influxdb (Optional)
- **Image**: influxdb:2.7-alpine
- **Purpose**: Store test metrics and results
- **Port**: 8086 (InfluxDB API)
- **Data**: Persisted in `influxdb_data` volume
- **Auto-start**: Only if explicitly configured

## Performance Tips

1. **Pre-build image**: Build the Docker image once, reuse multiple times
2. **Parallel execution**: Run multiple container instances for different test projects
3. **Volume mounting**: Mount result directories to host for inspection
4. **Caching**: Docker layers cache npm dependencies - faster rebuilds

## Troubleshooting

### Container exits immediately
```bash
# Check logs
docker-compose logs ewm-navbar-tests

# Check specific error
docker run --rm ewm-navbar-tests:latest npm run test:e2e 2>&1 | tail -50
```

### Browser crashes in container
```bash
# Run with debug output
docker run -e DEBUG=true --rm ewm-navbar-tests:latest npm run test:auth

# Check system dependencies - usually a missing library
docker run -it --rm ewm-navbar-tests:latest apt-get update && apt-get install -y <package>
```

### InfluxDB connection fails
```bash
# Verify InfluxDB is running
docker-compose ps

# Check InfluxDB logs
docker-compose logs influxdb

# Test connection from container
docker-compose run ewm-navbar-tests curl -v http://influxdb:8086/health
```

### Volume permission denied
```bash
# On Linux, ensure proper permissions
sudo chown -R $USER:$USER ./allure-results ./test-results ./playwright-report

# Or run with --user flag
docker run --user $(id -u):$(id -g) --rm ewm-navbar-tests:latest npm run test:e2e
```

## CI/CD Integration

### Azure Pipelines Example

```yaml
- task: Docker@2
  displayName: Build Test Image
  inputs:
    command: build
    Dockerfile: applicationqe/ewmnavbar/Dockerfile
    tags: ewm-navbar-tests:$(Build.BuildId)

- task: Docker@2
  displayName: Run Tests in Docker
  inputs:
    command: run
    arguments: |
      --rm \
      -v $(System.DefaultWorkingDirectory)/test-results:/app/test-results \
      -v $(System.DefaultWorkingDirectory)/allure-results:/app/allure-results \
      -e BUILD_BUILDID=$(Build.BuildId) \
      -e BUILD_REASON=$(Build.Reason) \
      ewm-navbar-tests:$(Build.BuildId) \
      npm run test:e2e
```

## Clean Up

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove volumes
docker volume prune

# Full cleanup
docker system prune -a --volumes
```

## Best Practices

1. ✅ Use multi-stage builds (smaller final image)
2. ✅ Exclude unnecessary files with .dockerignore
3. ✅ Pin base image versions (node:22-bookworm, not latest)
4. ✅ Use volume mounts for persistent test results
5. ✅ Set environment variables for configuration
6. ✅ Add health checks for services
7. ✅ Document all available commands
8. ✅ Use docker-compose for local development

## Additional Resources

- [Playwright Docker Documentation](https://playwright.dev/docs/docker)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [docker-compose Reference](https://docs.docker.com/compose/compose-file/)

---

For more information about the test framework, see [FRAMEWORK_DOCUMENTATION_COMPLETE.md](../../../FRAMEWORK_DOCUMENTATION_COMPLETE.md)
