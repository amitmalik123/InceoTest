# Performance Monitoring Guide

## 📊 Overview

This framework includes comprehensive performance monitoring capabilities to ensure your web application meets performance standards. The performance monitoring system tracks Web Vitals, navigation timing, resource metrics, and integrates with Lighthouse for complete audits.

---

## 🎯 Features

### 1. **Web Vitals Tracking**
Monitor Core Web Vitals that Google uses for ranking:
- **LCP** (Largest Contentful Paint) - Loading performance
- **FID** (First Input Delay) - Interactivity
- **CLS** (Cumulative Layout Shift) - Visual stability
- **TTFB** (Time to First Byte) - Server response
- **FCP** (First Contentful Paint) - Perceived load speed

### 2. **Navigation Timing**
Track browser navigation performance:
- DNS lookup time
- TCP connection time
- Request/response times
- DOM processing time
- Page load time

### 3. **Resource Metrics**
Monitor resource loading:
- Total resources loaded
- Count by type (scripts, stylesheets, images, fonts)
- Size by type (in KB)
- Total page weight

### 4. **Performance Budgets**
Set thresholds and fail tests if exceeded:
- Configurable per metric
- Environment-specific budgets
- Automatic validation

### 5. **Lighthouse Integration**
Run complete Lighthouse audits:
- Performance score
- Accessibility score
- Best Practices score
- SEO score
- PWA validation

---

## 🚀 Quick Start

### Basic Usage

```python
import pytest
from playwright.sync_api import Page
from utils.performance_monitor import PerformanceMonitor

@pytest.mark.performance
def test_page_performance(page: Page, performance_monitor: PerformanceMonitor):
    """Performance is automatically monitored with the fixture"""
    page.goto("https://example.com")
    page.wait_for_load_state("networkidle")
    # Metrics collected automatically after test
```

### Manual Monitoring

```python
from utils.performance_monitor import PerformanceMonitor, PerformanceBudget

def test_manual_performance(page: Page):
    # Create monitor
    monitor = PerformanceMonitor(page)

    # Start monitoring
    monitor.start_monitoring()

    # Perform actions
    page.goto("https://example.com")
    page.wait_for_load_state("networkidle")

    # Collect metrics
    metrics = monitor.collect_metrics(test_name="homepage")

    # Save metrics
    monitor.save_metrics(metrics)

    # Print report
    print(monitor.generate_report(metrics))

    # Validate budget
    assert monitor.validate_budget(metrics)
```

---

## 🎨 Custom Performance Budgets

### Define Custom Budget

```python
from utils.performance_monitor import PerformanceBudget

budget = PerformanceBudget(
    lcp_max=2000,           # Max LCP in ms
    fid_max=100,            # Max FID in ms
    cls_max=0.1,            # Max CLS score
    ttfb_max=600,           # Max TTFB in ms
    fcp_max=1500,           # Max FCP in ms
    page_load_max=2500,     # Max page load in ms
    total_size_max_kb=1500  # Max total size in KB
)

monitor = PerformanceMonitor(page, budget=budget)
```

### Environment-Specific Budgets

```python
import os
from utils.performance_monitor import PerformanceBudget

env = os.getenv('TEST_ENV', 'test11')

budgets = {
    'prod': PerformanceBudget(lcp_max=2000, fcp_max=1500),
    'test11': PerformanceBudget(lcp_max=3000, fcp_max=2000),
    'qa': PerformanceBudget(lcp_max=3500, fcp_max=2500)
}

budget = budgets.get(env, PerformanceBudget())
```

---

## 🔦 Lighthouse Integration

### Prerequisites

Install Lighthouse CLI globally:

```bash
npm install -g lighthouse
```

### Run Lighthouse Audit

```python
from utils.lighthouse_runner import LighthouseRunner

@pytest.mark.lighthouse
def test_lighthouse_audit(page: Page):
    url = "https://example.com"

    runner = LighthouseRunner()

    # Run audit
    audit_result = runner.run_audit(
        url=url,
        form_factor="desktop",  # or "mobile"
        throttling=True
    )

    # Extract scores
    scores = runner.extract_scores(audit_result)

    # Validate
    assert scores.performance >= 90
    assert scores.accessibility >= 90

    # Print report
    print(runner.generate_report(scores, url=url))
```

### Custom Lighthouse Budget

```python
from utils.lighthouse_runner import LighthouseBudget

budget = LighthouseBudget(
    performance_min=90,
    accessibility_min=95,
    best_practices_min=90,
    seo_min=90,
    pwa_min=80
)

runner = LighthouseRunner(budget=budget)
```

---

## 📈 Performance Test Examples

### Test Multiple Pages

```python
@pytest.mark.performance
def test_multi_page_performance(page: Page):
    pages = ["https://example.com", "https://example.com/about"]

    for url in pages:
        monitor = PerformanceMonitor(page)
        monitor.start_monitoring()

        page.goto(url)
        page.wait_for_load_state("networkidle")

        metrics = monitor.collect_metrics(test_name=url.split("/")[-1])
        monitor.save_metrics(metrics)

        assert monitor.validate_budget(metrics)
```

### Test User Journey

```python
@pytest.mark.performance
def test_checkout_journey_performance(page: Page):
    monitor = PerformanceMonitor(page)

    # Step 1: Homepage
    monitor.start_monitoring()
    page.goto("https://shop.example.com")
    homepage_metrics = monitor.collect_metrics("homepage")
    monitor.save_metrics(homepage_metrics, "journey_01_home.json")

    # Step 2: Product page
    monitor.start_monitoring()
    page.click("text=Products")
    product_metrics = monitor.collect_metrics("product_page")
    monitor.save_metrics(product_metrics, "journey_02_product.json")

    # Validate entire journey
    assert monitor.validate_budget(homepage_metrics)
    assert monitor.validate_budget(product_metrics)
```

### Compare Desktop vs Mobile

```python
@pytest.mark.lighthouse
def test_desktop_vs_mobile_performance():
    runner = LighthouseRunner()
    url = "https://example.com"

    # Desktop audit
    desktop_result = runner.run_audit(url, form_factor="desktop")
    desktop_scores = runner.extract_scores(desktop_result)

    # Mobile audit
    mobile_result = runner.run_audit(url, form_factor="mobile")
    mobile_scores = runner.extract_scores(mobile_result)

    # Compare
    print(f"Desktop Performance: {desktop_scores.performance}")
    print(f"Mobile Performance: {mobile_scores.performance}")

    assert desktop_scores.performance >= 90
    assert mobile_scores.performance >= 70  # Mobile typically has lower scores
```

---

## 📊 Reports and Output

### JSON Report Structure

```json
{
  "url": "https://example.com",
  "timestamp": "2025-12-22T10:30:00",
  "test_name": "test_homepage",
  "environment": "test11",
  "web_vitals": {
    "lcp": 1850.5,
    "fid": 45.2,
    "cls": 0.05,
    "ttfb": 450.1,
    "fcp": 1200.3
  },
  "navigation_timing": {
    "dns_lookup": 15.5,
    "tcp_connection": 25.3,
    "request_time": 150.2,
    "response_time": 300.1,
    "dom_processing": 450.5,
    "dom_content_loaded": 100.2,
    "page_load": 2100.5
  },
  "resource_metrics": {
    "total_resources": 45,
    "scripts_count": 12,
    "stylesheets_count": 5,
    "images_count": 20,
    "fonts_count": 3,
    "total_size_kb": 1850.5,
    "scripts_size_kb": 850.2,
    "stylesheets_size_kb": 150.5,
    "images_size_kb": 750.3
  },
  "memory_usage_mb": 45.5
}
```

### Console Report

Performance reports are automatically printed with clear formatting:

```
╔══════════════════════════════════════════════════════════════════════════╗
║                    PERFORMANCE MONITORING REPORT                         ║
╚══════════════════════════════════════════════════════════════════════════╝

URL: https://example.com
Timestamp: 2025-12-22T10:30:00
Test: test_homepage
Environment: test11

───────────────────────────────────────────────────────────────────────────
WEB VITALS
───────────────────────────────────────────────────────────────────────────
LCP (Largest Contentful Paint):  1850.5 ms
FID (First Input Delay):          45.2 ms
CLS (Cumulative Layout Shift):    0.05
TTFB (Time to First Byte):        450.1 ms
FCP (First Contentful Paint):     1200.3 ms

Status: ✓ GOOD
```

---

## 🔧 CI/CD Integration

### Run Performance Tests in Pipeline

```yaml
# Azure Pipeline example
- task: Bash@3
  displayName: 'Run Performance Tests'
  inputs:
    targetType: 'inline'
    script: |
      pytest tests/performance/ -m performance -v
      pytest tests/performance/ -m lighthouse -v
```

### Save Performance Reports as Artifacts

```yaml
- task: PublishBuildArtifacts@1
  displayName: 'Publish Performance Reports'
  inputs:
    PathtoPublish: 'reports/performance'
    ArtifactName: 'performance-reports'
```

---

## 🎯 Best Practices

1. **Run performance tests separately** - Use `-m performance` marker
2. **Set realistic budgets** - Adjust for environment and network conditions
3. **Monitor trends** - Track performance over time
4. **Test on stable infrastructure** - Avoid shared CI runners for accurate results
5. **Include in smoke tests** - Critical pages should have performance checks
6. **Use Lighthouse for comprehensive audits** - Not just performance, but accessibility and SEO too

---

## 🐛 Troubleshooting

### Lighthouse Not Found

```bash
# Install Lighthouse globally
npm install -g lighthouse

# Verify installation
lighthouse --version
```

### Memory Metrics Not Available

Memory metrics require Chrome to be launched with specific flags:
```python
# In conftest.py or test
browser_context_args = {
    "args": ["--enable-precise-memory-info"]
}
```

### Web Vitals Not Collected

Some metrics (especially FID) require user interaction:
```python
page.goto(url)
page.click("button")  # Trigger FID measurement
page.wait_for_timeout(2000)  # Wait for metrics
```

---

## 📚 Additional Resources

- [Web Vitals Documentation](https://web.dev/vitals/)
- [Lighthouse Documentation](https://developers.google.com/web/tools/lighthouse)
- [Navigation Timing API](https://developer.mozilla.org/en-US/docs/Web/API/Navigation_timing_API)
- [Performance API](https://developer.mozilla.org/en-US/docs/Web/API/Performance)

---

## 📝 Markers Reference

```python
@pytest.mark.performance  # Enable automatic performance monitoring
@pytest.mark.lighthouse   # Run Lighthouse audit
@pytest.mark.slow         # Mark as slow test (useful for Lighthouse)
```

---

## 🎓 Examples Location

See `tests/performance/test_performance_example.py` for complete working examples.
