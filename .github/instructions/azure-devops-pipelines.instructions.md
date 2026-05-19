---
description: 'Azure DevOps Pipelines conventions and security best practices for AssetMark CI/CD'
applyTo: '**/azure-pipelines*.yml,**/pipelines/**/*.yml,**/.azuredevops/**'
---

# Azure DevOps Pipelines — AssetMark CI/CD Conventions

This document defines conventions, security best practices, and patterns for Azure DevOps Pipelines at AssetMark. All CI/CD pipelines must follow these standards to ensure security, maintainability, and TSA compliance.

## Pipeline Structure

### Multi-Stage Pipelines

Use multi-stage pipelines for all production deployments:

```yaml
trigger:
  branches:
    include:
      - main
      - release/*

pool:
  vmImage: 'ubuntu-latest'

stages:
  - stage: Build
    displayName: 'Build and Test'
    jobs:
      - job: BuildJob
        steps:
          - task: DotNetCoreCLI@2
            inputs:
              command: 'build'
              projects: '**/*.csproj'

  - stage: Test
    displayName: 'Run Tests'
    dependsOn: Build
    jobs:
      - job: TestJob
        steps:
          - task: DotNetCoreCLI@2
            inputs:
              command: 'test'
              projects: '**/*Tests.csproj'

  - stage: Deploy
    displayName: 'Deploy to Production'
    dependsOn: Test
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    jobs:
      - deployment: DeployProduction
        environment: 'production'
        strategy:
          runOnce:
            deploy:
              steps:
                - task: AzureWebApp@1
                  inputs:
                    azureSubscription: 'AssetMark-Production'
                    appName: '$(AZURE_APP_NAME)'
                    package: '$(Pipeline.Workspace)/drop/*.zip'
```

**Key principles:**
- **Build → Test → Deploy** flow
- Explicit `dependsOn` for stage ordering
- Conditional deployment (only on `main` branch)
- Environment-based approvals for production

---

## YAML Syntax Conventions

### Trigger Configuration

**Single quotes everywhere:**
```yaml
trigger:
  branches:
    include:
      - 'main'
      - 'release/*'
    exclude:
      - 'feature/*'
  paths:
    include:
      - 'src/**'
    exclude:
      - 'docs/**'
      - '*.md'
```

**Scheduled triggers:**
```yaml
schedules:
  - cron: '0 2 * * *'  # Daily at 2 AM UTC
    displayName: 'Nightly build'
    branches:
      include:
        - 'main'
    always: false  # Only run if there are changes
```

### Pool Configuration

**Hosted agents (preferred):**
```yaml
pool:
  vmImage: 'ubuntu-latest'  # Linux
  # vmImage: 'windows-latest'  # Windows
  # vmImage: 'macOS-latest'  # macOS
```

**Self-hosted agents (when required):**
```yaml
pool:
  name: 'AssetMark-OnPrem'  # Self-hosted pool
  demands:
    - Agent.OS -equals Windows_NT
```

### Variables

**Pipeline variables:**
```yaml
variables:
  - name: 'buildConfiguration'
    value: 'Release'
  - name: 'dotnetVersion'
    value: '8.0.x'
```

**Variable groups (for secrets):**
```yaml
variables:
  - group: 'assetmark-production-secrets'  # Azure Key Vault-linked
  - name: 'buildConfiguration'
    value: 'Release'
```

**Runtime variables:**
```yaml
variables:
  - name: 'currentDate'
    value: $[format('{0:yyyyMMdd}', pipeline.startTime)]
```

---

## Templates

### Template References

Use templates for shared logic:

**Pipeline with template:**
```yaml
# azure-pipelines.yml
trigger:
  - 'main'

extends:
  template: 'templates/dotnet-app.yml'
  parameters:
    buildConfiguration: 'Release'
    azureSubscription: 'AssetMark-Production'
```

**Template file:**
```yaml
# templates/dotnet-app.yml
parameters:
  - name: 'buildConfiguration'
    type: string
    default: 'Release'
  - name: 'azureSubscription'
    type: string

stages:
  - stage: Build
    jobs:
      - job: BuildJob
        steps:
          - template: 'steps/build.yml'
            parameters:
              buildConfiguration: ${{ parameters.buildConfiguration }}

  - stage: Deploy
    jobs:
      - deployment: DeployProduction
        environment: 'production'
        strategy:
          runOnce:
            deploy:
              steps:
                - template: 'steps/deploy.yml'
                  parameters:
                    azureSubscription: ${{ parameters.azureSubscription }}
```

**Step template:**
```yaml
# templates/steps/build.yml
parameters:
  - name: 'buildConfiguration'
    type: string
    default: 'Release'

steps:
  - task: DotNetCoreCLI@2
    displayName: 'Restore dependencies'
    inputs:
      command: 'restore'
      projects: '**/*.csproj'

  - task: DotNetCoreCLI@2
    displayName: 'Build solution'
    inputs:
      command: 'build'
      projects: '**/*.csproj'
      arguments: '--configuration ${{ parameters.buildConfiguration }}'
```

**Why templates:**
- Reuse common logic across pipelines
- Centralized updates (change once, apply everywhere)
- Easier testing (validate template once)
- Enforced standards

---

## Variable Groups & Secrets Management

### Azure Key Vault-Linked Variable Groups

**Never inline secrets** — always use Azure Key Vault:

**Setup (Azure DevOps):**
1. Create Azure Key Vault in production subscription
2. Store secrets in Key Vault (connection strings, API keys, PATs)
3. Create Variable Group in Azure DevOps
4. Link Variable Group to Key Vault
5. Grant pipeline service principal `Get` permission on Key Vault secrets

**Usage in pipeline:**
```yaml
variables:
  - group: 'assetmark-production-secrets'  # Linked to Key Vault

steps:
  - task: AzureCLI@2
    inputs:
      azureSubscription: 'AssetMark-Production'
      scriptType: 'bash'
      scriptLocation: 'inlineScript'
      inlineScript: |
        echo "Deploying with API key..."
        # $(API_KEY) is populated from Key Vault
        curl -H "X-API-Key: $(API_KEY)" https://api.assetmark.com/deploy
    env:
      API_KEY: $(API_KEY)  # Secret from Key Vault variable group
```

**Secret handling:**
- Variables from Key Vault are **automatically marked as secret** (masked in logs)
- Use `issecret=true` for secrets defined directly in pipelines:
  ```yaml
  variables:
    - name: 'secretValue'
      value: 'placeholder'
      issecret: true
  ```
- **Never echo secrets**: `echo $(SECRET)` will be masked as `***`, but avoid logging altogether

---

## Service Connections

### Managed Identity (Preferred)

Use **managed identity-based service connections** for Azure resources:

**Setup:**
1. Enable managed identity on Azure DevOps agent pool
2. Grant managed identity permissions on Azure resources (Reader, Contributor, etc.)
3. Create service connection in Azure DevOps with managed identity authentication

**Advantages:**
- No credentials to manage or rotate
- Automatic authentication
- Fine-grained RBAC via Azure AD roles
- TSA-compliant (no PATs or service principals)

**Usage:**
```yaml
steps:
  - task: AzureWebApp@1
    inputs:
      azureSubscription: 'AssetMark-Production'  # Managed identity connection
      appName: '$(AZURE_APP_NAME)'
      package: '$(Pipeline.Workspace)/drop/*.zip'
```

### PAT-Based Connections (Avoid)

**Only use PATs when managed identity is not available** (e.g., GitHub, third-party APIs):
- Store PAT in Azure Key Vault
- Reference via variable group
- Set expiration (max 90 days)
- Rotate regularly

---

## Environments & Approval Gates

### Environment Definitions

Define environments for each deployment target:

**Dev:**
- Auto-deploy on merge to `main`
- No approvals required
- No retention policies

**Staging:**
- Auto-deploy on successful Dev deployment
- No approvals required
- Retain deployments for 30 days

**Production:**
- Manual approval required
- Minimum 2 reviewers (DevOps Lead + Product Owner)
- Wait timer: 30 minutes (allows time for pre-deployment checks)
- Retain deployments for 90 days

**Setup (Azure DevOps):**
1. Go to Pipelines → Environments
2. Create environment (e.g., `production`)
3. Add approvals: Settings → Approvals and checks → Add approval
4. Add required reviewers
5. Add wait timer (optional)

**Usage in pipeline:**
```yaml
stages:
  - stage: DeployProduction
    displayName: 'Deploy to Production'
    jobs:
      - deployment: DeployProd
        environment: 'production'  # Requires approval
        strategy:
          runOnce:
            deploy:
              steps:
                - task: AzureWebApp@1
                  inputs:
                    azureSubscription: 'AssetMark-Production'
                    appName: '$(AZURE_APP_NAME)'
                    package: '$(Pipeline.Workspace)/drop/*.zip'
```

---

## Deployment Jobs

### Strategy: runOnce

Use `runOnce` for simple deployments:

```yaml
jobs:
  - deployment: DeployProduction
    environment: 'production'
    strategy:
      runOnce:
        deploy:
          steps:
            - task: AzureWebApp@1
              inputs:
                azureSubscription: 'AssetMark-Production'
                appName: '$(AZURE_APP_NAME)'
                package: '$(Pipeline.Workspace)/drop/*.zip'
```

### Strategy: rolling

Use `rolling` for zero-downtime deployments (when deploying to multiple targets):

```yaml
jobs:
  - deployment: DeployProduction
    environment: 'production'
    strategy:
      rolling:
        maxParallel: 2  # Deploy to 2 targets at a time
        deploy:
          steps:
            - task: AzureWebApp@1
              inputs:
                azureSubscription: 'AssetMark-Production'
                appName: '$(AZURE_APP_NAME)'
                package: '$(Pipeline.Workspace)/drop/*.zip'
```

---

## Artifacts

### Publish Artifacts

Publish build artifacts for downstream stages:

```yaml
steps:
  - task: DotNetCoreCLI@2
    displayName: 'Publish application'
    inputs:
      command: 'publish'
      projects: '**/*.csproj'
      arguments: '--configuration Release --output $(Build.ArtifactStagingDirectory)'
      zipAfterPublish: true

  - task: PublishPipelineArtifact@1
    displayName: 'Publish artifact'
    inputs:
      targetPath: '$(Build.ArtifactStagingDirectory)'
      artifact: 'drop'
      publishLocation: 'pipeline'
```

### Download Artifacts

Download artifacts in deployment stages:

```yaml
steps:
  - task: DownloadPipelineArtifact@2
    displayName: 'Download build artifact'
    inputs:
      buildType: 'current'
      artifactName: 'drop'
      targetPath: '$(Pipeline.Workspace)/drop'
```

---

## Caching

### NuGet Cache

Cache NuGet packages to speed up builds:

```yaml
steps:
  - task: Cache@2
    displayName: 'Cache NuGet packages'
    inputs:
      key: 'nuget | "$(Agent.OS)" | **/packages.lock.json'
      restoreKeys: |
        nuget | "$(Agent.OS)"
      path: '$(Pipeline.Workspace)/.nuget/packages'

  - task: DotNetCoreCLI@2
    displayName: 'Restore dependencies'
    inputs:
      command: 'restore'
      projects: '**/*.csproj'
```

### npm Cache

Cache npm packages:

```yaml
steps:
  - task: Cache@2
    displayName: 'Cache npm packages'
    inputs:
      key: 'npm | "$(Agent.OS)" | **/package-lock.json'
      restoreKeys: |
        npm | "$(Agent.OS)"
      path: '$(Pipeline.Workspace)/.npm'

  - script: npm ci
    displayName: 'Install dependencies'
```

---

## Branch Policies

### Required PR Reviews

Configure branch policies on `main` and `develop`:

**Settings:**
- Require pull request for merges
- Minimum 2 reviewers
- At least 1 approval from code owners
- Comment resolution required before merge
- Build validation (pipeline must pass)
- Work item linking required

**Setup (Azure Repos):**
1. Go to Repos → Branches
2. Click `...` on `main` branch → Branch policies
3. Enable policies:
   - ✅ Require a minimum number of reviewers (2)
   - ✅ Check for comment resolution
   - ✅ Build validation (select pipeline)
   - ✅ Check for linked work items

---

## Security

### Pin Task Versions

Always pin task versions — **never use `@*`**:

❌ **Bad:**
```yaml
- task: DotNetCoreCLI@*  # Unpredictable behavior on updates
```

✅ **Good:**
```yaml
- task: DotNetCoreCLI@2  # Locked to major version 2
```

**Why:**
- Predictable builds (no surprise breaking changes)
- Security auditing (know exactly which task versions are used)
- Rollback capability (if a new task version has a bug)

### Limit Pipeline Permissions

Use **least privilege** for pipeline service principals:

**Resource permissions:**
- Build pipelines: `Reader` on source repos
- Deploy pipelines: `Contributor` on specific resource groups (not subscription-wide)

**Setup:**
1. Create separate service connections for each environment (Dev, Staging, Production)
2. Grant minimum permissions:
   - Dev: `Contributor` on `assetmark-dev-rg`
   - Staging: `Contributor` on `assetmark-staging-rg`
   - Production: `Contributor` on `assetmark-prod-rg`
3. Never grant `Owner` role to pipelines

### Checkout Security

Use `checkout: self` with `fetchDepth: 1` for speed and security:

```yaml
steps:
  - checkout: self
    fetchDepth: 1  # Shallow clone (faster, no history)
    clean: true    # Clean workspace before checkout
```

**Why:**
- Faster checkouts (no full Git history)
- Smaller attack surface (no historical vulnerabilities in code)

### Never Echo Secrets

**Secrets are automatically masked** in logs, but avoid logging them entirely:

❌ **Bad:**
```yaml
- script: |
    echo "API Key: $(API_KEY)"  # Will be masked, but still bad practice
```

✅ **Good:**
```yaml
- script: |
    echo "Deploying application..."
    # Use secret in command without logging
    curl -H "X-API-Key: $(API_KEY)" https://api.assetmark.com/deploy
```

### Audit Pipeline Modifications

**Enable pipeline audit logging:**
1. Go to Project Settings → Auditing
2. Enable audit log for pipeline changes
3. Review logs monthly for unauthorized modifications

**Track:**
- Pipeline YAML changes (who, when, what)
- Variable group updates
- Service connection changes

---

## Common Tasks

### .NET Core

```yaml
# Restore
- task: DotNetCoreCLI@2
  displayName: 'Restore dependencies'
  inputs:
    command: 'restore'
    projects: '**/*.csproj'

# Build
- task: DotNetCoreCLI@2
  displayName: 'Build solution'
  inputs:
    command: 'build'
    projects: '**/*.csproj'
    arguments: '--configuration Release'

# Test
- task: DotNetCoreCLI@2
  displayName: 'Run tests'
  inputs:
    command: 'test'
    projects: '**/*Tests.csproj'
    arguments: '--configuration Release --collect:"XPlat Code Coverage"'

# Publish
- task: DotNetCoreCLI@2
  displayName: 'Publish application'
  inputs:
    command: 'publish'
    projects: '**/*.csproj'
    arguments: '--configuration Release --output $(Build.ArtifactStagingDirectory)'
    zipAfterPublish: true
```

### npm

```yaml
# Install
- task: Npm@1
  displayName: 'Install dependencies'
  inputs:
    command: 'ci'
    workingDir: 'src/frontend'

# Build
- task: Npm@1
  displayName: 'Build frontend'
  inputs:
    command: 'custom'
    customCommand: 'run build'
    workingDir: 'src/frontend'

# Test
- task: Npm@1
  displayName: 'Run tests'
  inputs:
    command: 'custom'
    customCommand: 'run test:ci'
    workingDir: 'src/frontend'
```

### Azure Web App Deployment

```yaml
- task: AzureWebApp@1
  displayName: 'Deploy to Azure App Service'
  inputs:
    azureSubscription: 'AssetMark-Production'
    appType: 'webApp'
    appName: '$(AZURE_APP_NAME)'
    package: '$(Pipeline.Workspace)/drop/*.zip'
    deploymentMethod: 'zipDeploy'
```

### Docker

```yaml
# Build
- task: Docker@2
  displayName: 'Build Docker image'
  inputs:
    command: 'build'
    repository: '$(DOCKER_REGISTRY)/$(IMAGE_NAME)'
    dockerfile: 'Dockerfile'
    tags: |
      $(Build.BuildNumber)
      latest

# Push
- task: Docker@2
  displayName: 'Push Docker image'
  inputs:
    command: 'push'
    repository: '$(DOCKER_REGISTRY)/$(IMAGE_NAME)'
    tags: |
      $(Build.BuildNumber)
      latest
```

### Azure CLI

```yaml
- task: AzureCLI@2
  displayName: 'Run Azure CLI commands'
  inputs:
    azureSubscription: 'AssetMark-Production'
    scriptType: 'bash'
    scriptLocation: 'inlineScript'
    inlineScript: |
      az webapp config appsettings set \
        --resource-group $(AZURE_RG) \
        --name $(AZURE_APP_NAME) \
        --settings ENVIRONMENT=production
```

---

## Test Integration

### Publish Test Results

```yaml
- task: PublishTestResults@2
  displayName: 'Publish test results'
  inputs:
    testResultsFormat: 'VSTest'  # xUnit, NUnit, JUnit
    testResultsFiles: '**/*.trx'
    mergeTestResults: true
    failTaskOnFailedTests: true
```

### Publish Code Coverage

```yaml
- task: PublishCodeCoverageResults@2
  displayName: 'Publish code coverage'
  inputs:
    codeCoverageTool: 'Cobertura'  # JaCoCo, Cobertura
    summaryFileLocation: '$(Agent.TempDirectory)/**/coverage.cobertura.xml'
    failIfCoverageEmpty: true
```

### Enforce 85% Coverage Gate (AssetMark Mandate)

Builds **must fail** if unit test coverage drops below 85%. Use a PowerShell task after publishing coverage:

```yaml
- task: PowerShell@2
  displayName: 'Enforce 85% coverage threshold'
  inputs:
    targetType: 'inline'
    script: |
      $coverageFile = Get-ChildItem -Recurse -Filter 'coverage.cobertura.xml' | Select-Object -First 1
      if (-not $coverageFile) { Write-Error 'No coverage.cobertura.xml found'; exit 1 }
      [xml]$xml = Get-Content $coverageFile.FullName
      $lineRate = [double]$xml.coverage.'line-rate'
      $pct = [math]::Round($lineRate * 100, 2)
      Write-Host "##[section]Coverage: $pct%"
      if ($lineRate -lt 0.85) {
        Write-Error "Coverage $pct% is below the required 85% threshold. Build failed."
        exit 1
      }
      Write-Host "##vso[task.complete result=Succeeded;]Coverage gate passed: $pct%"
```

> **For Jest (TypeScript):** Set `coverageThreshold` in `jest.config.js` (branches/functions/lines/statements all ≥ 85). The Jest task will fail automatically if thresholds are not met.

#### Python / pytest variant

```yaml
- task: PowerShell@2
  displayName: 'Enforce 85% coverage gate (Python)'
  inputs:
    targetType: 'inline'
    script: |
      $threshold = 85
      $coverageFile = Get-ChildItem -Path "$(System.DefaultWorkingDirectory)" -Filter "coverage.xml" -Recurse | Select-Object -First 1
      if (-not $coverageFile) {
        Write-Error "coverage.xml not found. Ensure pytest runs with --cov-report=xml:coverage.xml"
        exit 1
      }
      [xml]$xml = Get-Content $coverageFile.FullName
      $lineRate = [double]$xml.coverage.'line-rate'
      $linePct  = [math]::Round($lineRate * 100, 2)
      Write-Host "Python line coverage: $linePct%"
      if ($linePct -lt $threshold) {
        Write-Error "FAIL: Python line coverage $linePct% is below the 85% AssetMark mandate."
        exit 1
      }
      Write-Host "✅ Python coverage gate passed."
```

### CI Coverage Threshold Linter

Add this step to validate that coverage config files don't secretly lower thresholds below 85%:

```yaml
- task: PowerShell@2
  displayName: 'Lint coverage config thresholds'
  inputs:
    targetType: 'inline'
    script: |
      $minThreshold = 85
      $failed = $false
      # Check .coveragerc
      $coverageRc = Get-ChildItem -Path "." -Filter ".coveragerc" -Recurse
      foreach ($f in $coverageRc) {
        $content = Get-Content $f.FullName -Raw
        if ($content -match 'fail_under\s*=\s*(\d+)') {
          $val = [int]$Matches[1]
          if ($val -lt $minThreshold) {
            Write-Warning "LINT FAIL: $($f.FullName) sets fail_under=$val (below 85)"
            $failed = $true
          }
        }
      }
      # Check jest.config.js / jest.config.ts
      $jestConfigs = Get-ChildItem -Path "." -Filter "jest.config.*" -Recurse
      foreach ($f in $jestConfigs) {
        $content = Get-Content $f.FullName -Raw
        $matches = [regex]::Matches($content, '(?:branches|functions|lines|statements)\s*:\s*(\d+)')
        foreach ($m in $matches) {
          $val = [int]$m.Groups[1].Value
          if ($val -lt $minThreshold) {
            Write-Warning "LINT FAIL: $($f.FullName) sets coverage threshold=$val (below 85)"
            $failed = $true
          }
        }
      }
      if ($failed) {
        Write-Error "Coverage config linting failed. All thresholds must be >= 85."
        exit 1
      }
      Write-Host "✅ Coverage config thresholds are compliant."
```

---

## Anti-Patterns

### ❌ Classic Pipelines

**Don't use Classic (UI-based) pipelines** — use YAML:

**Why:**
- YAML is version-controlled (Git history, PR reviews)
- YAML is reproducible (export/import across projects)
- YAML is testable (validate syntax, simulate runs)
- Classic pipelines are deprecated by Microsoft

### ❌ Hardcoded Secrets

**Never hardcode secrets in YAML:**

❌ **Bad:**
```yaml
variables:
  - name: 'API_KEY'
    value: 'sk-1234567890abcdef'  # NEVER DO THIS
```

✅ **Good:**
```yaml
variables:
  - group: 'assetmark-production-secrets'  # From Key Vault
```

### ❌ Missing Approval Gates

**Never deploy to production without approval:**

❌ **Bad:**
```yaml
- stage: DeployProduction
  jobs:
    - job: DeployJob  # No approval required
      steps:
        - task: AzureWebApp@1
```

✅ **Good:**
```yaml
- stage: DeployProduction
  jobs:
    - deployment: DeployProd
      environment: 'production'  # Approval required
      strategy:
        runOnce:
          deploy:
            steps:
              - task: AzureWebApp@1
```

### ❌ No Artifact Versioning

**Always tag artifacts with version numbers:**

❌ **Bad:**
```yaml
- task: Docker@2
  inputs:
    tags: 'latest'  # No version tracking
```

✅ **Good:**
```yaml
- task: Docker@2
  inputs:
    tags: |
      $(Build.BuildNumber)
      latest
```

---

## Summary

Azure DevOps Pipelines at AssetMark follow these principles:

1. **YAML over Classic** — All pipelines are version-controlled YAML
2. **Secrets in Key Vault** — Never inline secrets
3. **Managed Identity** — Prefer managed identity over PATs/service principals
4. **Approval Gates** — Production deployments require approval
5. **Pin Versions** — Task versions are pinned (`@2`, not `@*`)
6. **Least Privilege** — Pipelines have minimum required permissions
7. **Multi-Stage** — Build → Test → Deploy flow
8. **Templates** — Reuse common logic
9. **Caching** — Speed up builds with NuGet/npm caching
10. **Test Integration** — Publish test results and code coverage

**For questions or exceptions, contact:** DevOps Lead or submit RFC for approval.
