"""
Lighthouse Integration for Playwright Tests

Provides automated Lighthouse audits for performance, accessibility,
best practices, SEO, and PWA validation.
"""

import json
import logging
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class LighthouseScore:
    """Lighthouse audit scores"""

    performance: float
    accessibility: float
    best_practices: float
    seo: float
    pwa: Optional[float] = None


@dataclass
class LighthouseMetrics:
    """Lighthouse performance metrics"""

    first_contentful_paint: float
    largest_contentful_paint: float
    total_blocking_time: float
    cumulative_layout_shift: float
    speed_index: float
    time_to_interactive: float


@dataclass
class LighthouseBudget:
    """Lighthouse score budgets"""

    performance_min: float = 90
    accessibility_min: float = 90
    best_practices_min: float = 90
    seo_min: float = 90
    pwa_min: Optional[float] = None

    def validate(self, scores: LighthouseScore) -> Dict[str, str]:
        """Validate scores against budget"""
        violations = {}

        if scores.performance < self.performance_min:
            violations["performance"] = (
                f"Performance score {scores.performance} below minimum {self.performance_min}"
            )

        if scores.accessibility < self.accessibility_min:
            violations["accessibility"] = (
                f"Accessibility score {scores.accessibility} below minimum {self.accessibility_min}"
            )

        if scores.best_practices < self.best_practices_min:
            violations["best_practices"] = (
                f"Best Practices score {scores.best_practices} below minimum {self.best_practices_min}"
            )

        if scores.seo < self.seo_min:
            violations["seo"] = f"SEO score {scores.seo} below minimum {self.seo_min}"

        if self.pwa_min and scores.pwa and scores.pwa < self.pwa_min:
            violations["pwa"] = f"PWA score {scores.pwa} below minimum {self.pwa_min}"

        return violations


class LighthouseRunner:
    """
    Run Lighthouse audits on web pages.

    Prerequisites:
        npm install -g lighthouse

    Usage:
        runner = LighthouseRunner()
        result = runner.run_audit('https://example.com')
        if runner.validate_budget(result.scores):
            print("All scores meet budget!")
    """

    def __init__(
        self, budget: Optional[LighthouseBudget] = None, report_dir: str = "reports/lighthouse"
    ):
        """
        Initialize Lighthouse runner.

        Args:
            budget: Score budget thresholds
            report_dir: Directory to save reports
        """
        self.budget = budget or LighthouseBudget()
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)

        # Check if Lighthouse is installed
        self._check_lighthouse_installation()

    def _check_lighthouse_installation(self):
        """Check if Lighthouse CLI is installed"""
        try:
            result = subprocess.run(
                ["lighthouse", "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                logger.info(f"Lighthouse {version} detected")
            else:
                logger.warning("Lighthouse CLI not found. Install with: npm install -g lighthouse")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("Lighthouse CLI not found. Install with: npm install -g lighthouse")

    def run_audit(
        self,
        url: str,
        form_factor: str = "desktop",
        throttling: bool = True,
        categories: Optional[List[str]] = None,
        save_report: bool = True,
    ) -> Dict:
        """
        Run Lighthouse audit on URL.

        Args:
            url: URL to audit
            form_factor: 'desktop' or 'mobile'
            throttling: Apply network/CPU throttling
            categories: List of categories to audit (default: all)
            save_report: Save HTML and JSON reports

        Returns:
            Lighthouse audit results
        """
        logger.info(f"Running Lighthouse audit on: {url}")

        if categories is None:
            categories = ["performance", "accessibility", "best-practices", "seo", "pwa"]

        # Prepare output files
        timestamp = Path(tempfile.mktemp()).name
        output_path = self.report_dir / f"lighthouse_{timestamp}"

        # Build Lighthouse command
        cmd = [
            "lighthouse",
            url,
            "--output=json,html",
            f"--output-path={output_path}",
            f"--form-factor={form_factor}",
            "--quiet",
            '--chrome-flags="--headless"',
        ]

        # Add categories
        for category in categories:
            cmd.append(f"--only-categories={category}")

        # Throttling settings
        if not throttling:
            cmd.append("--throttling-method=provided")

        try:
            # Run Lighthouse
            logger.info(f"Executing Lighthouse with form factor: {form_factor}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode != 0:
                logger.error(f"Lighthouse audit failed: {result.stderr}")
                return {}

            # Read JSON report
            json_path = Path(f"{output_path}.report.json")
            if json_path.exists():
                with open(json_path, "r") as f:
                    audit_result = json.load(f)

                logger.info(f"Lighthouse audit completed. Reports saved to: {output_path}")
                return audit_result
            else:
                logger.error("Lighthouse report file not found")
                return {}

        except subprocess.TimeoutExpired:
            logger.error("Lighthouse audit timed out")
            return {}
        except Exception as e:
            logger.error(f"Error running Lighthouse: {e}")
            return {}

    def extract_scores(self, audit_result: Dict) -> Optional[LighthouseScore]:
        """
        Extract scores from Lighthouse audit result.

        Args:
            audit_result: Raw Lighthouse audit result

        Returns:
            LighthouseScore object
        """
        try:
            categories = audit_result.get("categories", {})

            return LighthouseScore(
                performance=categories.get("performance", {}).get("score", 0) * 100,
                accessibility=categories.get("accessibility", {}).get("score", 0) * 100,
                best_practices=categories.get("best-practices", {}).get("score", 0) * 100,
                seo=categories.get("seo", {}).get("score", 0) * 100,
                pwa=(
                    categories.get("pwa", {}).get("score", 0) * 100 if "pwa" in categories else None
                ),
            )
        except Exception as e:
            logger.error(f"Failed to extract scores: {e}")
            return None

    def extract_metrics(self, audit_result: Dict) -> Optional[LighthouseMetrics]:
        """
        Extract performance metrics from Lighthouse audit result.

        Args:
            audit_result: Raw Lighthouse audit result

        Returns:
            LighthouseMetrics object
        """
        try:
            audits = audit_result.get("audits", {})

            return LighthouseMetrics(
                first_contentful_paint=audits.get("first-contentful-paint", {}).get(
                    "numericValue", 0
                ),
                largest_contentful_paint=audits.get("largest-contentful-paint", {}).get(
                    "numericValue", 0
                ),
                total_blocking_time=audits.get("total-blocking-time", {}).get("numericValue", 0),
                cumulative_layout_shift=audits.get("cumulative-layout-shift", {}).get(
                    "numericValue", 0
                ),
                speed_index=audits.get("speed-index", {}).get("numericValue", 0),
                time_to_interactive=audits.get("interactive", {}).get("numericValue", 0),
            )
        except Exception as e:
            logger.error(f"Failed to extract metrics: {e}")
            return None

    def validate_budget(self, scores: LighthouseScore) -> bool:
        """
        Validate scores against budget.

        Args:
            scores: Lighthouse scores

        Returns:
            True if all scores meet budget
        """
        violations = self.budget.validate(scores)

        if violations:
            logger.warning("Lighthouse budget violations detected:")
            for key, message in violations.items():
                logger.warning(f"  - {message}")
            return False

        logger.info("✓ All Lighthouse scores meet budget requirements")
        return True

    def generate_report(
        self, scores: LighthouseScore, metrics: Optional[LighthouseMetrics] = None, url: str = ""
    ) -> str:
        """
        Generate human-readable Lighthouse report.

        Args:
            scores: Lighthouse scores
            metrics: Lighthouse metrics (optional)
            url: Audited URL

        Returns:
            Formatted report string
        """
        report = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                        LIGHTHOUSE AUDIT REPORT                           ║
╚══════════════════════════════════════════════════════════════════════════╝

URL: {url}

───────────────────────────────────────────────────────────────────────────
SCORES
───────────────────────────────────────────────────────────────────────────
Performance:                      {scores.performance:.1f}/100
Accessibility:                    {scores.accessibility:.1f}/100
Best Practices:                   {scores.best_practices:.1f}/100
SEO:                              {scores.seo:.1f}/100
"""

        if scores.pwa is not None:
            report += f"PWA:                              {scores.pwa:.1f}/100\n"

        if metrics:
            report += f"""
───────────────────────────────────────────────────────────────────────────
PERFORMANCE METRICS
───────────────────────────────────────────────────────────────────────────
First Contentful Paint:           {metrics.first_contentful_paint:.0f} ms
Largest Contentful Paint:         {metrics.largest_contentful_paint:.0f} ms
Total Blocking Time:              {metrics.total_blocking_time:.0f} ms
Cumulative Layout Shift:          {metrics.cumulative_layout_shift:.3f}
Speed Index:                      {metrics.speed_index:.0f} ms
Time to Interactive:              {metrics.time_to_interactive:.0f} ms
"""

        violations = self.budget.validate(scores)
        report += """
───────────────────────────────────────────────────────────────────────────
BUDGET VALIDATION
───────────────────────────────────────────────────────────────────────────
"""

        if violations:
            report += "Status: ✗ BUDGET VIOLATIONS DETECTED\n\n"
            for violation in violations.values():
                report += f"  - {violation}\n"
        else:
            report += "Status: ✓ ALL SCORES MEET BUDGET\n"

        report += "\n╚══════════════════════════════════════════════════════════════════════════╝\n"

        return report
