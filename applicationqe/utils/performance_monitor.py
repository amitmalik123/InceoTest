"""
Performance Monitoring Module for Playwright Tests

This module provides comprehensive performance monitoring capabilities:
- Web Vitals metrics (LCP, FID, CLS, TTFB, FCP)
- Page load timing
- Resource loading metrics
- Network timing
- Memory usage
- Performance budgets
- Lighthouse integration
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from playwright.sync_api import Page, Response

logger = logging.getLogger(__name__)


@dataclass
class WebVitals:
    """Web Vitals metrics"""

    lcp: Optional[float] = None  # Largest Contentful Paint (ms)
    fid: Optional[float] = None  # First Input Delay (ms)
    cls: Optional[float] = None  # Cumulative Layout Shift (score)
    ttfb: Optional[float] = None  # Time to First Byte (ms)
    fcp: Optional[float] = None  # First Contentful Paint (ms)

    def is_good(self) -> bool:
        """Check if all metrics are within 'good' thresholds"""
        checks = []
        if self.lcp is not None:
            checks.append(self.lcp <= 2500)  # Good: <= 2.5s
        if self.fid is not None:
            checks.append(self.fid <= 100)  # Good: <= 100ms
        if self.cls is not None:
            checks.append(self.cls <= 0.1)  # Good: <= 0.1
        if self.ttfb is not None:
            checks.append(self.ttfb <= 800)  # Good: <= 800ms
        if self.fcp is not None:
            checks.append(self.fcp <= 1800)  # Good: <= 1.8s

        return all(checks) if checks else False


@dataclass
class NavigationTiming:
    """Navigation timing metrics"""

    dns_lookup: Optional[float] = None
    tcp_connection: Optional[float] = None
    request_time: Optional[float] = None
    response_time: Optional[float] = None
    dom_processing: Optional[float] = None
    dom_content_loaded: Optional[float] = None
    page_load: Optional[float] = None


@dataclass
class ResourceMetrics:
    """Resource loading metrics"""

    total_resources: int = 0
    scripts_count: int = 0
    stylesheets_count: int = 0
    images_count: int = 0
    fonts_count: int = 0
    total_size_kb: float = 0.0
    scripts_size_kb: float = 0.0
    stylesheets_size_kb: float = 0.0
    images_size_kb: float = 0.0


@dataclass
class PerformanceMetrics:
    """Complete performance metrics for a page"""

    url: str
    timestamp: str
    web_vitals: WebVitals
    navigation_timing: NavigationTiming
    resource_metrics: ResourceMetrics
    memory_usage_mb: Optional[float] = None
    test_name: Optional[str] = None
    environment: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "url": self.url,
            "timestamp": self.timestamp,
            "web_vitals": asdict(self.web_vitals),
            "navigation_timing": asdict(self.navigation_timing),
            "resource_metrics": asdict(self.resource_metrics),
            "memory_usage_mb": self.memory_usage_mb,
            "test_name": self.test_name,
            "environment": self.environment,
        }


@dataclass
class PerformanceBudget:
    """Performance budget thresholds"""

    lcp_max: float = 2500  # ms
    fid_max: float = 100  # ms
    cls_max: float = 0.1  # score
    ttfb_max: float = 800  # ms
    fcp_max: float = 1800  # ms
    page_load_max: float = 3000  # ms
    total_size_max_kb: float = 2000  # KB

    def validate(self, metrics: PerformanceMetrics) -> Dict[str, bool]:
        """Validate metrics against budget"""
        violations = {}

        if metrics.web_vitals.lcp and metrics.web_vitals.lcp > self.lcp_max:
            violations["lcp"] = f"LCP {metrics.web_vitals.lcp}ms exceeds budget {self.lcp_max}ms"

        if metrics.web_vitals.fid and metrics.web_vitals.fid > self.fid_max:
            violations["fid"] = f"FID {metrics.web_vitals.fid}ms exceeds budget {self.fid_max}ms"

        if metrics.web_vitals.cls and metrics.web_vitals.cls > self.cls_max:
            violations["cls"] = f"CLS {metrics.web_vitals.cls} exceeds budget {self.cls_max}"

        if metrics.web_vitals.ttfb and metrics.web_vitals.ttfb > self.ttfb_max:
            violations["ttfb"] = (
                f"TTFB {metrics.web_vitals.ttfb}ms exceeds budget {self.ttfb_max}ms"
            )

        if metrics.web_vitals.fcp and metrics.web_vitals.fcp > self.fcp_max:
            violations["fcp"] = f"FCP {metrics.web_vitals.fcp}ms exceeds budget {self.fcp_max}ms"

        if (
            metrics.navigation_timing.page_load
            and metrics.navigation_timing.page_load > self.page_load_max
        ):
            violations["page_load"] = (
                f"Page Load {metrics.navigation_timing.page_load}ms exceeds budget {self.page_load_max}ms"
            )

        if metrics.resource_metrics.total_size_kb > self.total_size_max_kb:
            violations["total_size"] = (
                f"Total Size {metrics.resource_metrics.total_size_kb}KB exceeds budget {self.total_size_max_kb}KB"
            )

        return violations


class PerformanceMonitor:
    """
    Performance monitoring for Playwright tests.

    Usage:
        monitor = PerformanceMonitor(page)
        await monitor.start_monitoring()
        # ... perform actions ...
        metrics = await monitor.collect_metrics()
        monitor.save_metrics(metrics, 'test_name')
    """

    def __init__(
        self,
        page: Page,
        budget: Optional[PerformanceBudget] = None,
        report_dir: str = "reports/performance",
    ):
        """
        Initialize performance monitor.

        Args:
            page: Playwright page object
            budget: Performance budget thresholds
            report_dir: Directory to save performance reports
        """
        self.page = page
        self.budget = budget or PerformanceBudget()
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)

        self.resources: List[Dict] = []
        self._setup_listeners()

    def _setup_listeners(self):
        """Setup event listeners for resource tracking"""

        def on_response(response: Response):
            try:
                headers = response.headers
                content_length = int(headers.get("content-length", 0))

                resource_type = response.request.resource_type
                self.resources.append(
                    {
                        "url": response.url,
                        "type": resource_type,
                        "size": content_length,
                        "status": response.status,
                    }
                )
            except Exception as e:
                logger.debug(f"Error tracking resource: {e}")

        self.page.on("response", on_response)

    def start_monitoring(self):
        """Start monitoring (call before navigation)"""
        self.resources = []
        logger.info("Performance monitoring started")

    def collect_metrics(
        self, test_name: Optional[str] = None, environment: Optional[str] = None
    ) -> PerformanceMetrics:
        """
        Collect all performance metrics.

        Args:
            test_name: Name of the test
            environment: Test environment

        Returns:
            PerformanceMetrics object with all collected metrics
        """
        logger.info("Collecting performance metrics...")

        # Collect Web Vitals
        web_vitals = self._collect_web_vitals()

        # Collect Navigation Timing
        navigation_timing = self._collect_navigation_timing()

        # Collect Resource Metrics
        resource_metrics = self._collect_resource_metrics()

        # Collect Memory Usage
        memory_usage = self._collect_memory_usage()

        metrics = PerformanceMetrics(
            url=self.page.url,
            timestamp=datetime.now().isoformat(),
            web_vitals=web_vitals,
            navigation_timing=navigation_timing,
            resource_metrics=resource_metrics,
            memory_usage_mb=memory_usage,
            test_name=test_name,
            environment=environment,
        )

        logger.info(f"Metrics collected for: {self.page.url}")
        return metrics

    def _collect_web_vitals(self) -> WebVitals:
        """Collect Web Vitals metrics using JavaScript"""
        script = """
        () => {
            return new Promise((resolve) => {
                const vitals = {};

                // Get Performance Observer entries
                const observer = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        if (entry.entryType === 'largest-contentful-paint') {
                            vitals.lcp = entry.renderTime || entry.loadTime;
                        }
                        if (entry.entryType === 'first-input') {
                            vitals.fid = entry.processingStart - entry.startTime;
                        }
                        if (entry.entryType === 'layout-shift' && !entry.hadRecentInput) {
                            vitals.cls = (vitals.cls || 0) + entry.value;
                        }
                    }
                });

                try {
                    observer.observe({ entryTypes: ['largest-contentful-paint', 'first-input', 'layout-shift'] });
                } catch (e) {
                    // Browser doesn't support some metrics
                }

                // Get Navigation Timing metrics
                const navTiming = performance.getEntriesByType('navigation')[0];
                if (navTiming) {
                    vitals.ttfb = navTiming.responseStart - navTiming.requestStart;
                }

                // Get Paint Timing
                const paintEntries = performance.getEntriesByType('paint');
                const fcpEntry = paintEntries.find(e => e.name === 'first-contentful-paint');
                if (fcpEntry) {
                    vitals.fcp = fcpEntry.startTime;
                }

                // Wait a bit for metrics to be collected
                setTimeout(() => {
                    observer.disconnect();
                    resolve(vitals);
                }, 1000);
            });
        }
        """

        try:
            vitals_data = self.page.evaluate(script)
            return WebVitals(
                lcp=vitals_data.get("lcp"),
                fid=vitals_data.get("fid"),
                cls=vitals_data.get("cls"),
                ttfb=vitals_data.get("ttfb"),
                fcp=vitals_data.get("fcp"),
            )
        except Exception as e:
            logger.warning(f"Failed to collect Web Vitals: {str(e).splitlines()[0]}")
            return WebVitals()

    def _collect_navigation_timing(self) -> NavigationTiming:
        """Collect navigation timing metrics"""
        script = """
        () => {
            const nav = performance.getEntriesByType('navigation')[0];
            if (!nav) return {};

            return {
                dnsLookup: nav.domainLookupEnd - nav.domainLookupStart,
                tcpConnection: nav.connectEnd - nav.connectStart,
                requestTime: nav.responseStart - nav.requestStart,
                responseTime: nav.responseEnd - nav.responseStart,
                domProcessing: nav.domComplete - nav.domInteractive,
                domContentLoaded: nav.domContentLoadedEventEnd - nav.domContentLoadedEventStart,
                pageLoad: nav.loadEventEnd - nav.loadEventStart
            };
        }
        """

        try:
            timing_data = self.page.evaluate(script)
            return NavigationTiming(
                dns_lookup=timing_data.get("dnsLookup"),
                tcp_connection=timing_data.get("tcpConnection"),
                request_time=timing_data.get("requestTime"),
                response_time=timing_data.get("responseTime"),
                dom_processing=timing_data.get("domProcessing"),
                dom_content_loaded=timing_data.get("domContentLoaded"),
                page_load=timing_data.get("pageLoad"),
            )
        except Exception as e:
            logger.warning(f"Failed to collect navigation timing: {str(e).splitlines()[0]}")
            return NavigationTiming()

    def _collect_resource_metrics(self) -> ResourceMetrics:
        """Collect resource loading metrics"""
        metrics = ResourceMetrics()

        for resource in self.resources:
            size_kb = resource["size"] / 1024 if resource["size"] else 0
            resource_type = resource["type"]

            metrics.total_resources += 1
            metrics.total_size_kb += size_kb

            if resource_type == "script":
                metrics.scripts_count += 1
                metrics.scripts_size_kb += size_kb
            elif resource_type == "stylesheet":
                metrics.stylesheets_count += 1
                metrics.stylesheets_size_kb += size_kb
            elif resource_type == "image":
                metrics.images_count += 1
                metrics.images_size_kb += size_kb
            elif resource_type == "font":
                metrics.fonts_count += 1

        return metrics

    def _collect_memory_usage(self) -> Optional[float]:
        """Collect memory usage (if available)"""
        script = """
        () => {
            if (performance.memory) {
                return performance.memory.usedJSHeapSize / (1024 * 1024);
            }
            return null;
        }
        """

        try:
            return self.page.evaluate(script)
        except Exception as e:
            logger.debug(f"Memory metrics not available: {e}")
            return None

    def save_metrics(self, metrics: PerformanceMetrics, filename: Optional[str] = None) -> Path:
        """
        Save metrics to JSON file.

        Args:
            metrics: Performance metrics to save
            filename: Optional filename (defaults to timestamp)

        Returns:
            Path to saved file
        """
        if filename is None:
            filename = f"perf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        if not filename.endswith(".json"):
            filename += ".json"

        filepath = self.report_dir / filename

        with open(filepath, "w") as f:
            json.dump(metrics.to_dict(), f, indent=2)

        logger.info(f"Performance metrics saved to: {filepath}")
        return filepath

    def validate_budget(self, metrics: PerformanceMetrics) -> bool:
        """
        Validate metrics against performance budget.

        Args:
            metrics: Performance metrics to validate

        Returns:
            True if all metrics meet budget, False otherwise
        """
        violations = self.budget.validate(metrics)

        if violations:
            logger.warning("Performance budget violations detected:")
            for key, message in violations.items():
                logger.warning(f"  - {message}")
            return False

        logger.info("✓ All performance metrics meet budget requirements")
        return True

    def generate_report(self, metrics: PerformanceMetrics) -> str:
        """
        Generate human-readable performance report.

        Args:
            metrics: Performance metrics

        Returns:
            Formatted report string
        """
        report = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                    PERFORMANCE MONITORING REPORT                         ║
╚══════════════════════════════════════════════════════════════════════════╝

URL: {metrics.url}
Timestamp: {metrics.timestamp}
Test: {metrics.test_name or 'N/A'}
Environment: {metrics.environment or 'N/A'}

───────────────────────────────────────────────────────────────────────────
WEB VITALS
───────────────────────────────────────────────────────────────────────────
LCP (Largest Contentful Paint):  {metrics.web_vitals.lcp or 'N/A'} ms
FID (First Input Delay):          {metrics.web_vitals.fid or 'N/A'} ms
CLS (Cumulative Layout Shift):    {metrics.web_vitals.cls or 'N/A'}
TTFB (Time to First Byte):        {metrics.web_vitals.ttfb or 'N/A'} ms
FCP (First Contentful Paint):     {metrics.web_vitals.fcp or 'N/A'} ms

Status: {'✓ GOOD' if metrics.web_vitals.is_good() else '✗ NEEDS IMPROVEMENT'}

───────────────────────────────────────────────────────────────────────────
NAVIGATION TIMING
───────────────────────────────────────────────────────────────────────────
DNS Lookup:                       {metrics.navigation_timing.dns_lookup or 'N/A'} ms
TCP Connection:                   {metrics.navigation_timing.tcp_connection or 'N/A'} ms
Request Time:                     {metrics.navigation_timing.request_time or 'N/A'} ms
Response Time:                    {metrics.navigation_timing.response_time or 'N/A'} ms
DOM Processing:                   {metrics.navigation_timing.dom_processing or 'N/A'} ms
DOM Content Loaded:               {metrics.navigation_timing.dom_content_loaded or 'N/A'} ms
Page Load:                        {metrics.navigation_timing.page_load or 'N/A'} ms

───────────────────────────────────────────────────────────────────────────
RESOURCE METRICS
───────────────────────────────────────────────────────────────────────────
Total Resources:                  {metrics.resource_metrics.total_resources}
  - Scripts:                      {metrics.resource_metrics.scripts_count}
  - Stylesheets:                  {metrics.resource_metrics.stylesheets_count}
  - Images:                       {metrics.resource_metrics.images_count}
  - Fonts:                        {metrics.resource_metrics.fonts_count}

Total Size:                       {metrics.resource_metrics.total_size_kb:.2f} KB
  - Scripts:                      {metrics.resource_metrics.scripts_size_kb:.2f} KB
  - Stylesheets:                  {metrics.resource_metrics.stylesheets_size_kb:.2f} KB
  - Images:                       {metrics.resource_metrics.images_size_kb:.2f} KB

───────────────────────────────────────────────────────────────────────────
MEMORY USAGE
───────────────────────────────────────────────────────────────────────────
JS Heap Size:                     {metrics.memory_usage_mb or 'N/A'} MB

───────────────────────────────────────────────────────────────────────────
BUDGET VALIDATION
───────────────────────────────────────────────────────────────────────────
"""

        violations = self.budget.validate(metrics)
        if violations:
            report += "Status: ✗ BUDGET VIOLATIONS DETECTED\n\n"
            for violation in violations.values():
                report += f"  - {violation}\n"
        else:
            report += "Status: ✓ ALL METRICS MEET BUDGET\n"

        report += "\n╚══════════════════════════════════════════════════════════════════════════╝\n"

        return report
