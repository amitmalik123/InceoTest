# Pipeline Matrix Usage Guide

This guide explains how to use the new matrix-based pipeline (`azure-pipelines-matrix.yml`) and the `manage_matrix.py` script.

## Overview

The pipeline now uses the `manage_matrix.py` script to dynamically determine which services to run based on:
- Trigger type (PR, Push, Schedule, Manual)
- Service configuration in `services-matrix.yaml`
- Manual parameters

## Pipeline Features

### ✅ Supported Execution Modes

1. **Automatic (PR/Push/Schedule)**
   - Runs services based on their flags in `services-matrix.yaml`
   - PR: Only runs services with `runOnPR: true`
   - Push: Only runs services with `runOnPush: true`
   - Schedule: Only runs services with `runOnSchedule: true`

2. **Manual Execution**
   - Select specific services to run
   - Override environments
   - Choose test type
   - Run disabled services (with override)

### 📊 Pipeline Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `executionMode` | string | `auto` | `auto` or `manual` |
| `services` | string | `` | Comma-separated service names (e.g., `parties,movemoney`) |
| `environments` | string | `` | Comma-separated environments (e.g., `TSADEV,T12`) |
| `testType` | string | `functional` | `functional`, `non-functional`, or `both` |
| `overrideEnabled` | boolean | `false` | Run disabled services too |

## Usage Examples

### 1. Run on Pull Request (Automatic)
When a PR is created, the pipeline automatically runs services with `runOnPR: true`.

**Services that will run:**
- Only `parties` (the only service with `runOnPR: true` and `enabled: true`)

### 2. Run on Push (Automatic)
When code is pushed, the pipeline runs services with `runOnPush: true`.

**Services that will run:**
- `parties` (enabled, runOnPush: true)

### 3. Manual - Run Single Service
**Pipeline Parameters:**
```yaml
executionMode: manual
services: parties
testType: functional
```

**Result:** Runs `parties` service in all its configured environments (TSADEV, TSATEST, T12, T11, T10)

### 4. Manual - Run Multiple Services
**Pipeline Parameters:**
```yaml
executionMode: manual
services: parties,movemoney,securities
testType: both
```

**Result:** Runs all three services (functional + non-functional tests) in their configured environments

### 5. Manual - Specific Environments
**Pipeline Parameters:**
```yaml
executionMode: manual
services: parties
environments: TSADEV,T12
testType: functional
```

**Result:** Runs `parties` only in TSADEV and T12 environments

### 6. Manual - Run Disabled Services
**Pipeline Parameters:**
```yaml
executionMode: manual
services: work_item_notification
overrideEnabled: true
testType: functional
```

**Result:** Runs the disabled service

### 7. Manual - Run All Enabled Services
**Pipeline Parameters:**
```yaml
executionMode: manual
services: (leave empty)
testType: functional
```

**Result:** Runs all enabled services in their configured environments

## Using manage_matrix.py Script

### Local Testing and Simulation

#### Generate Pipeline Matrix (what pipeline would run)
```bash
# Simulate PR trigger
python scripts/manage_matrix.py generate-pipeline-matrix \
  --execution-mode auto \
  --trigger-reason PullRequest

# Simulate manual run with specific services
python scripts/manage_matrix.py generate-pipeline-matrix \
  --execution-mode manual \
  --services parties,movemoney \
  --environments TSADEV,T12 \
  --test-type both

# Simulate push trigger
python scripts/manage_matrix.py generate-pipeline-matrix \
  --execution-mode auto \
  --trigger-reason IndividualCI
```

#### Simulate What Would Run (without pipeline output)
```bash
# Simulate PR
python scripts/manage_matrix.py simulate-pr --env TSADEV

# Simulate Push
python scripts/manage_matrix.py simulate-push --env TSADEV

# Simulate Schedule
python scripts/manage_matrix.py simulate-schedule --env TSADEV
```

#### Manage Services
```bash
# List all services
python scripts/manage_matrix.py list

# List only enabled services
python scripts/manage_matrix.py list --enabled-only

# List only disabled services
python scripts/manage_matrix.py list --disabled-only

# Enable a service (legacy method)
python scripts/manage_matrix.py enable work_item_notification

# Disable a service (legacy method)
python scripts/manage_matrix.py disable models

# Set individual flag for a service
python scripts/manage_matrix.py set-flag parties runOnPR true
python scripts/manage_matrix.py set-flag movemoney runOnSchedule false
python scripts/manage_matrix.py set-flag securities enabled true

# Set all flags for a single service to true or false
python scripts/manage_matrix.py set-all-flags movemoney true
python scripts/manage_matrix.py set-all-flags securities false

# Set specific flags for a service
python scripts/manage_matrix.py set-all-flags parties \
  --enabled true \
  --run-on-pr true \
  --run-on-push false \
  --run-on-schedule true

# Set all flags for ALL services at once
python scripts/manage_matrix.py set-all-flags all true
python scripts/manage_matrix.py set-all-flags all false

# Validate configuration
python scripts/manage_matrix.py validate

# Generate summary report
python scripts/manage_matrix.py summary
```

#### Export Services List
```bash
# Export as JSON
python scripts/manage_matrix.py export-services --format json

# Export as comma-separated
python scripts/manage_matrix.py export-services --format comma

# Export as YAML
python scripts/manage_matrix.py export-services --format yaml
```

## Pipeline Architecture

### Stage 1: Initialize
- Parses `services-matrix.yaml`
- Runs `manage_matrix.py generate-pipeline-matrix`
- Determines which services to run
- Generates Azure DevOps matrix JSON
- Sets pipeline variables

### Stage 2: Execute Tests
- Uses dynamic matrix strategy
- Runs jobs in parallel (max 5 concurrent)
- Each job runs for a specific service-environment combination
- Executes functional and/or non-functional tests
- Publishes results and artifacts

### Stage 3: Summary
- Generates execution summary
- Displays overall results

## Service Matrix Configuration

Example service configuration in `config/services-matrix.yaml`:

```yaml
services:
  parties:
    displayName: Parties API
    enabled: true              # Service is active
    runOnPR: true              # Run on pull requests
    runOnPush: true            # Run on code push
    runOnSchedule: true        # Run on scheduled triggers
    testType: functional       # Default test type
    priority: 1                # Execution priority (lower = higher priority)
    environments:              # Environments to run in
      - TSADEV
      - TSATEST
      - T12
      - T11
      - T10
    functionalTestArgs: --service-name parties --env TSADEV
    nonFunctionalTestArgs: --file testdata/parties/testcases/TestCase_Party_POST.json --test_type Performance --env TSADEV --headless -u 10 -r 2 -t 30s
```

## Matrix Output Format

The pipeline creates a matrix with unique keys for each service-environment combination:

```json
{
  "parties_TSADEV": {
    "name": "parties",
    "displayName": "Parties API",
    "environment": "TSADEV",
    "priority": 1,
    "testType": "functional",
    "functionalTestArgs": "--service-name parties --env TSADEV",
    "nonFunctionalTestArgs": "...",
    "reason": "Manual selection"
  },
  "parties_T12": {
    "name": "parties",
    "displayName": "Parties API",
    "environment": "T12",
    ...
  }
}
```

## Best Practices

### 1. **PR Triggers**
- Only enable `runOnPR: true` for critical services
- Keeps PR validation fast
- Currently only `parties` is configured

### 2. **Push Triggers**
- Enable `runOnPush: true` for services that should run on every commit
- Good for regression testing

### 3. **Scheduled Runs**
- Enable `runOnSchedule: true` for comprehensive testing
- Configure cron schedules per service

### 4. **Priority Settings**
- Use priority to control execution order
- Priority 1 = highest (runs first)
- Priority 3 = lowest (runs last)

### 5. **Test Types**
- Set appropriate default `testType` per service
- Override at pipeline level when needed
- Use `both` for comprehensive testing

### 6. **Environment Management**
- Configure appropriate environments per service
- Use `environments` parameter to override for specific runs

## Troubleshooting

### No Services Running
**Issue:** Pipeline shows "No services to run"

**Solutions:**
1. Check if services are enabled in `services-matrix.yaml`
2. Verify trigger flags match execution type (PR/Push/Schedule)
3. Use `--override-enabled true` for manual runs of disabled services

### Service Not Running on PR
**Issue:** Expected service doesn't run on PR

**Solution:** Ensure `runOnPR: true` in service configuration

### Wrong Environment
**Issue:** Tests running in wrong environment

**Solution:** 
1. Check `environments` list in service configuration
2. Use `environments` parameter to override
3. Verify environment-specific variable groups are configured

### Script Not Found
**Issue:** `manage_matrix.py` not found in pipeline

**Solution:** Ensure `workingDirectory: $(buildPath)` is set correctly

## Advanced Usage

### Custom Trigger Reasons
The `--trigger-reason` parameter supports:
- `PullRequest` - PR trigger
- `IndividualCI` - Push trigger
- `BatchedCI` - Push trigger (batched)
- `Schedule` - Scheduled trigger
- `Manual` - Manual execution

### Testing Locally Before Pipeline Run
Always test your configuration locally first:

```bash
# Test what would run on PR
python scripts/manage_matrix.py simulate-pr

# Validate configuration
python scripts/manage_matrix.py validate

# Test specific scenario
python scripts/manage_matrix.py generate-pipeline-matrix \
  --execution-mode manual \
  --services YOUR_SERVICE \
  --environments TSADEV
```

## Service Configuration Management

### Quick Reference - manage_matrix.py Commands

#### View Services
```bash
python scripts/manage_matrix.py list                    # List all services with details
python scripts/manage_matrix.py list --enabled-only     # Show only enabled services
python scripts/manage_matrix.py list --disabled-only    # Show only disabled services
python scripts/manage_matrix.py summary                 # Configuration statistics
```

#### Enable/Disable Services
```bash
# Legacy simple commands
python scripts/manage_matrix.py enable <service>
python scripts/manage_matrix.py disable <service>

# Modern flag-based commands (recommended)
python scripts/manage_matrix.py set-flag <service> enabled true
python scripts/manage_matrix.py set-flag <service> enabled false
```

#### Set Individual Flags
```bash
# Set specific trigger flags
python scripts/manage_matrix.py set-flag parties runOnPR true
python scripts/manage_matrix.py set-flag movemoney runOnPush false
python scripts/manage_matrix.py set-flag securities runOnSchedule true

# Valid flags: enabled, runOnPR, runOnPush, runOnSchedule
```

#### Bulk Flag Operations
```bash
# Enable/disable all flags for a single service
python scripts/manage_matrix.py set-all-flags parties true      # All flags to true
python scripts/manage_matrix.py set-all-flags movemoney false   # All flags to false

# Set specific flags only
python scripts/manage_matrix.py set-all-flags parties \
  --enabled true \
  --run-on-pr true \
  --run-on-push false \
  --run-on-schedule true

# Enable/disable ALL services at once (use with caution!)
python scripts/manage_matrix.py set-all-flags all true     # Enable everything
python scripts/manage_matrix.py set-all-flags all false    # Disable everything
```

#### Validation and Testing
```bash
# Validate configuration file
python scripts/manage_matrix.py validate

# Test what would run in different scenarios
python scripts/manage_matrix.py simulate-pr --env TSADEV
python scripts/manage_matrix.py simulate-push --env TSADEV
python scripts/manage_matrix.py simulate-schedule --env TSADEV

# Test pipeline matrix generation
python scripts/manage_matrix.py generate-pipeline-matrix \
  --execution-mode manual \
  --services parties,movemoney \
  --environments TSADEV,T12 \
  --test-type functional
```

#### Export Services
```bash
python scripts/manage_matrix.py export-services --format json
python scripts/manage_matrix.py export-services --format comma
python scripts/manage_matrix.py export-services --format yaml
```

### Flag Combinations Guide

Common configuration patterns:

```yaml
# Fast PR validation only
set-all-flags <service> --enabled true --run-on-pr true --run-on-push false --run-on-schedule false

# Full CI/CD (PR + Push + Schedule)
set-all-flags <service> true

# Only scheduled comprehensive tests
set-all-flags <service> --enabled true --run-on-pr false --run-on-push false --run-on-schedule true

# Disabled completely
set-all-flags <service> false
```

## Support

For issues or questions:
1. Review this guide
2. Check `services-matrix.yaml` configuration with `python scripts/manage_matrix.py list`
3. Run local simulations with `manage_matrix.py simulate-pr/push/schedule`
4. Validate configuration with `python scripts/manage_matrix.py validate`
5. Check summary statistics with `python scripts/manage_matrix.py summary`
