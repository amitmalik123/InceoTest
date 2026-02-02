# Documentation Index

Welcome to the API Automation Framework documentation. This folder contains comprehensive guides and references for using and understanding the framework.

## 📚 Documentation Structure

### Getting Started
- **[Main README](../README.md)** - Quick start guide, installation, and basic usage

### Framework Documentation
- **[Framework Flow Guide](FRAMEWORK_FLOW.md)** - Complete execution flows with Mermaid diagrams
  - Test Case Generation Flow
  - Test Execution Flow (Pytest)
  - Locust Performance Test Flow
  - 8-Phase execution details
  - Component interactions

- **[Architecture Guide](ARCHITECTURE.md)** - Framework design and architecture principles

- **[Architecture Diagrams](ARCHITECTURE_DIAGRAM.md)** - Visual architecture diagrams

### Specialized Guides
- **[Performance Testing](PERFORMANCE.md)** - Locust performance testing guide
  - Setup and configuration
  - Running performance tests
  - InfluxDB integration
  - Interpreting results

- **[Security Guide](SECURITY.md)** - Security best practices and guidelines
  - Credential management
  - Azure AD authentication
  - Secure configuration

- **[Git Best Practices](GIT_BEST_PRACTICES.md)** - Version control guidelines
  - Branching strategy
  - Commit conventions
  - Pull request workflow

### Troubleshooting
- **[BOM Fix Guide](BOM_FIX_GUIDE.md)** - Byte Order Mark (BOM) troubleshooting
  - JSON BOM detection and removal
  - Automated fix utility (`framework/common/bom_utils.py`)
  - Prevention strategies

## 🗂️ Additional Resources

### Configuration
- **[Config Files](../config/)** - Environment-specific configurations
- **[Templates](../templates/)** - Test case templates and examples

### Test Data
- **[Test Cases](../testdata/)** - Service-specific test cases and data
- **[Test Examples](../templates/TestCase_Template_README.md)** - Detailed test case documentation

## 🔍 Quick Navigation

### For New Users
1. Start with [Main README](../README.md)
2. Review [Framework Flow Guide](FRAMEWORK_FLOW.md) for visual understanding
3. Check [Templates](../templates/TestCase_Template_README.md) for test case structure

### For Developers
1. [Architecture Guide](ARCHITECTURE.md) for design principles
2. [Architecture Diagrams](ARCHITECTURE_DIAGRAM.md) for visual architecture
3. [Framework Flow Guide](FRAMEWORK_FLOW.md) for execution details

### For Performance Testing
1. [Performance Testing Guide](PERFORMANCE.md)
2. [Locust Setup](PERFORMANCE.md#locust-setup)
3. [InfluxDB Configuration](PERFORMANCE.md#influxdb-integration)

### For Security
1. [Security Guide](SECURITY.md)
2. [Azure AD Setup](SECURITY.md#azure-ad-authentication)
3. [Credential Management](SECURITY.md#credential-management)

### For Troubleshooting
1. [BOM Fix Guide](BOM_FIX_GUIDE.md) for JSON parsing errors
2. [Auto-fix scripts](BOM_FIX_GUIDE.md#automated-fix) for bulk corrections

## 📝 Contributing

When adding new documentation:
- Place it in the `docs/` folder
- Update this README index
- Follow the existing markdown formatting
- Include code examples where applicable
- Add Mermaid diagrams for visual flows

## 🏗️ Documentation Organization

```
core-api-automation/
├── README.md                    # Main quick start guide
│   ├── ARCHITECTURE_DIAGRAM.md # Visual diagrams
│   ├── PERFORMANCE.md          # Performance testing guide
│   ├── SECURITY.md             # Security guidelines
│   ├── GIT_BEST_PRACTICES.md   # Version control guide
│   └── BOM_FIX_GUIDE.md        # BOM troubleshootingre
│   ├── ARCHITECTURE_DIAGRAM.md # Visual diagrams
│   ├── PERFORMANCE.md          # Performance testing guide
│   ├── SECURITY.md             # Security guidelines
│   └── GIT_BEST_PRACTICES.md   # Version control guide
├── templates/                   # Test case templates
│   └── TestCase_Template_README.md
├── config/                      # Configuration files
└── testdata/                    # Test cases and data
```

---

**Last Updated**: December 14, 2025
**Framework Version**: Latest
**Maintained By**: Automation Team
