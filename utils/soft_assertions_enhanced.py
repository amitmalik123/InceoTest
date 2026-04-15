"""
Enhanced Soft Assertions with Allure Integration and Screenshot Capture

Provides soft assertions that:
- Capture screenshots immediately when assertion fails
- Generate beautiful HTML summary report
- Track expected vs actual values with JSON diffs
- Integrate seamlessly with Allure reporting
- Support test warning status (yellow) vs failure (red)
"""

import json
from typing import Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

import allure
from playwright.sync_api import Locator, Page

from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@dataclass
class SoftAssertionFailure:
    """Data class representing a single soft assertion failure"""
    assertion_number: int
    message: str
    expected: Any
    actual: Any
    timestamp: str
    screenshot_path: Optional[str] = None
    step_name: Optional[str] = None
    
    def to_dict(self):
        """Convert to dictionary for HTML rendering"""
        return {
            'number': self.assertion_number,
            'message': self.message,
            'expected': str(self.expected),
            'actual': str(self.actual),
            'expected_json': self._try_json(self.expected),
            'actual_json': self._try_json(self.actual),
            'timestamp': self.timestamp,
            'step_name': self.step_name or 'N/A',
            'has_screenshot': self.screenshot_path is not None,
        }
    
    @staticmethod
    def _try_json(value):
        """Try to pretty-print as JSON"""
        try:
            if isinstance(value, (dict, list)):
                return json.dumps(value, indent=2)
            elif isinstance(value, str):
                return json.dumps(json.loads(value), indent=2)
        except:
            pass
        return None


class EnhancedSoftAssertions:
    """
    Enhanced soft assertions with screenshot capture and Allure integration.
    
    Features:
    - Immediate screenshot capture on assertion failure
    - HTML summary report with all failures
    - Expected vs Actual comparison with JSON diff
    - Integration with Allure reporting
    - Test warning status (yellow) not failure (red)
    
    Example:
        soft = EnhancedSoftAssertions(page)
        soft.assert_equal(actual, expected, "Value check", step_name="Verify Status")
        # Screenshot automatically captured and stored
        soft.generate_report()  # Creates Allure attachment
    """
    
    def __init__(self, page: Page = None):
        """
        Initialize Enhanced Soft Assertions.
        
        Args:
            page: Playwright Page object for screenshot capture (optional)
        """
        self.page = page
        self.failures: List[SoftAssertionFailure] = []
        self._assertion_count = 0
    
    def __enter__(self):
        """Enter context manager"""
        self.failures.clear()
        self._assertion_count = 0
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and generate report. Does NOT raise - test stays PASSED with warnings."""
        if exc_type is None:  # Only check assertions if no other exception
            self.generate_report()
            if self.failures:
                self._mark_test_with_warning()
        return False
    
    def _record_failure(self, message: str, expected: Any, actual: Any, step_name: Optional[str] = None):
        """
        Record a failed assertion with screenshot.
        
        Args:
            message: Assertion failure message
            expected: Expected value
            actual: Actual value
            step_name: Name of the step where failure occurred
        """
        self._assertion_count += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        screenshot_path = None
        
        # Capture screenshot immediately if page is available
        if self.page:
            try:
                screenshot_path = self._capture_screenshot(self._assertion_count, message)
                logger.info(f"Screenshot captured for assertion #{self._assertion_count}")
            except Exception as e:
                logger.warning(f"Failed to capture screenshot: {e}")
        
        # Create failure record
        failure = SoftAssertionFailure(
            assertion_number=self._assertion_count,
            message=message,
            expected=expected,
            actual=actual,
            timestamp=timestamp,
            screenshot_path=screenshot_path,
            step_name=step_name
        )
        
        self.failures.append(failure)
        
        # Log to console and Allure
        logger.warning(f"[SOFT ASSERTION #{self._assertion_count}] {message}")
        logger.info(f"  Expected: {expected}")
        logger.info(f"  Actual: {actual}")
        
        # Attach text to Allure
        allure.attach(
            f"Expected: {expected}\nActual: {actual}\n{message}",
            name=f"Soft Assertion Failure #{self._assertion_count}",
            attachment_type=allure.attachment_type.TEXT
        )
    
    def _capture_screenshot(self, assertion_number: int, message: str) -> str:
        """
        Capture screenshot for failed assertion.
        
        Args:
            assertion_number: The assertion number
            message: Failure message
            
        Returns:
            Name of the attachment
        """
        if not self.page:
            return None
        
        screenshot_name = f"[SA #{assertion_number}] {message[:50]}"
        screenshot = self.page.screenshot()
        allure.attach(
            screenshot,
            name=screenshot_name,
            attachment_type=allure.attachment_type.PNG
        )
        return screenshot_name
    
    def assert_equal(self, actual: Any, expected: Any, message: Optional[str] = None, step_name: Optional[str] = None):
        """
        Assert two values are equal.
        
        Args:
            actual: Actual value
            expected: Expected value
            message: Custom failure message
            step_name: Name of step where assertion occurs
        """
        if actual != expected:
            msg = message or f"Values do not match"
            self._record_failure(msg, expected, actual, step_name)
    
    def assert_not_equal(self, actual: Any, expected: Any, message: Optional[str] = None, step_name: Optional[str] = None):
        """Assert two values are not equal."""
        if actual == expected:
            msg = message or f"Values should not be equal"
            self._record_failure(msg, f"Not {expected}", actual, step_name)
    
    def assert_true(self, condition: bool, message: Optional[str] = None, step_name: Optional[str] = None):
        """Assert condition is True."""
        if not condition:
            msg = message or "Condition is not True"
            self._record_failure(msg, True, condition, step_name)
    
    def assert_false(self, condition: bool, message: Optional[str] = None, step_name: Optional[str] = None):
        """Assert condition is False."""
        if condition:
            msg = message or "Condition is not False"
            self._record_failure(msg, False, condition, step_name)
    
    def assert_in(self, item: Any, container: Any, message: Optional[str] = None, step_name: Optional[str] = None):
        """Assert item is in container."""
        if item not in container:
            msg = message or f"{item} not found in container"
            self._record_failure(msg, f"Any of {container}", item, step_name)
    
    def assert_not_in(self, item: Any, container: Any, message: Optional[str] = None, step_name: Optional[str] = None):
        """Assert item is not in container."""
        if item in container:
            msg = message or f"{item} should not be in container"
            self._record_failure(msg, f"Not in {container}", item, step_name)
    
    def assert_none(self, value: Any, message: Optional[str] = None, step_name: Optional[str] = None):
        """Assert value is None."""
        if value is not None:
            msg = message or "Value is not None"
            self._record_failure(msg, None, value, step_name)
    
    def assert_not_none(self, value: Any, message: Optional[str] = None, step_name: Optional[str] = None):
        """Assert value is not None."""
        if value is None:
            msg = message or "Value is None"
            self._record_failure(msg, "Not None", value, step_name)
    
    # Playwright-specific soft assertions
    def assert_visible(self, locator: Locator, message: Optional[str] = None, step_name: Optional[str] = None):
        """Assert element is visible."""
        try:
            if not locator.is_visible():
                msg = message or f"Expected element to be visible: {locator}"
                self._record_failure(msg, "visible=True", "visible=False", step_name)
        except Exception as e:
            self._record_failure(f"Error checking visibility: {str(e)}", "visible=True", f"Error: {e}", step_name)
    
    def assert_hidden(self, locator: Locator, message: Optional[str] = None, step_name: Optional[str] = None):
        """Assert element is hidden."""
        try:
            if locator.is_visible():
                msg = message or f"Expected element to be hidden: {locator}"
                self._record_failure(msg, "visible=False", "visible=True", step_name)
        except Exception as e:
            self._record_failure(f"Error checking visibility: {str(e)}", "visible=False", f"Error: {e}", step_name)
    
    def assert_text_contains(self, locator: Locator, text: str, message: Optional[str] = None, step_name: Optional[str] = None):
        """Assert element text contains substring."""
        try:
            actual_text = locator.inner_text()
            if text not in actual_text:
                msg = message or f"Expected text to contain '{text}', but got '{actual_text}'"
                self._record_failure(msg, f"contains '{text}'", actual_text, step_name)
        except Exception as e:
            self._record_failure(f"Error getting text: {str(e)}", f"contains '{text}'", f"Error: {e}", step_name)
    
    def assert_count(self, locator: Locator, expected_count: int, message: Optional[str] = None, step_name: Optional[str] = None):
        """Assert element count matches expected."""
        try:
            actual_count = locator.count()
            if actual_count != expected_count:
                msg = message or f"Expected {expected_count} elements, but found {actual_count}"
                self._record_failure(msg, expected_count, actual_count, step_name)
        except Exception as e:
            self._record_failure(f"Error getting count: {str(e)}", expected_count, f"Error: {e}", step_name)
    
    def assert_all(self):
        """
        Backward-compatible method: generate report and mark with warning if failures exist.
        Does NOT raise an exception - test stays PASSED with yellow warning indicator.
        """
        self.generate_report()
        if self.failures:
            self._mark_test_with_warning()
    
    def _mark_test_with_warning(self):
        """
        Mark test with warning indicators in Allure.
        Sets severity, tags, and description without raising an exception.
        """
        # Set severity to minor (shows as downward arrow indicator in Allure)
        allure.dynamic.severity(allure.severity_level.MINOR)
        
        # Add visible warning tag in the Tags section
        allure.dynamic.tag("⚠️ SOFT_ASSERTION_WARNING")
        
        # Build warning summary
        warning_msg = f"\n⚠️ WARNING: {len(self.failures)} soft assertion(s) failed:\n"
        for failure in self.failures:
            warning_msg += f"\n  #{failure.assertion_number}: {failure.message}\n"
            warning_msg += f"    Expected: {failure.expected}\n"
            warning_msg += f"    Actual: {failure.actual}\n"
        
        # Attach warning summary as text
        allure.attach(
            warning_msg,
            name="⚠️ Soft Assertion Warnings",
            attachment_type=allure.attachment_type.TEXT
        )
        
        # Add warning banner in test description
        warning_html = (
            '<div style="background:#fff3e0;border-left:4px solid #ff9800;padding:12px;margin:10px 0;border-radius:4px;">'
            f'<strong style="color:#e65100;">⚠️ {len(self.failures)} Soft Assertion(s) Failed</strong>'
            '<br><span style="color:#bf360c;">Test PASSED with warnings — review the Soft Assertions Summary Report attachment below.</span>'
            '</div>'
        )
        allure.dynamic.description_html(warning_html)
        
        logger.warning(warning_msg)
    
    def generate_report(self):
        """
        Generate HTML summary report of all soft assertion failures.
        Attaches to Allure report.
        """
        if not self.failures:
            logger.info("No soft assertion failures detected")
            return
        
        # Generate HTML report
        html_content = self._generate_html_report()
        
        # Attach to Allure
        allure.attach(
            html_content,
            name="⚠️ Soft Assertions Summary Report",
            attachment_type=allure.attachment_type.HTML
        )
        
        logger.warning(f"Generated summary report for {len(self.failures)} soft assertion(s)")
    
    def _generate_html_report(self) -> str:
        """Generate beautiful HTML report of all failures."""
        # Generate table rows first
        rows = []
        for failure in self.failures:
            data = failure.to_dict()
            
            # Comparison section
            comparison = (
                '<div class="comparison">'
                f'<div class="expected">✓ Expected: {data["expected"]}</div>'
                f'<div class="actual">✗ Actual: {data["actual"]}</div>'
                '</div>'
            )
            
            # JSON diff if available
            if data['expected_json'] or data['actual_json']:
                comparison += '<div class="json-diff"><strong>JSON Comparison:</strong><br>'
                if data['expected_json']:
                    comparison += f'Expected JSON:<br><pre>{data["expected_json"]}</pre>'
                if data['actual_json']:
                    comparison += f'Actual JSON:<br><pre>{data["actual_json"]}</pre>'
                comparison += '</div>'
            
            row = (
                '<tr>'
                f'<td class="assertion-number">{data["number"]}</td>'
                f'<td><span class="step-name">{data["step_name"]}</span></td>'
                f'<td>{data["message"]}</td>'
                f'<td>{comparison}</td>'
                f'<td><span class="timestamp">{data["timestamp"]}</span></td>'
                '</tr>'
            )
            rows.append(row)
        
        rows_html = "\n".join(rows)
        total = len(self.failures)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .header {{ background: #ff9800; color: white; padding: 15px; border-radius: 4px; margin-bottom: 20px; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .summary {{ background: #fff3e0; border-left: 4px solid #ff9800; padding: 10px; margin-bottom: 20px; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                th {{ background: #f44336; color: white; padding: 12px; text-align: left; }}
                td {{ padding: 12px; border-bottom: 1px solid #ddd; }}
                tr:hover {{ background: #f9f9f9; }}
                .assertion-number {{ background: #ffebee; font-weight: bold; }}
                .comparison {{ background: #f0f0f0; padding: 10px; margin: 10px 0; border-radius: 4px; font-family: monospace; }}
                .expected {{ background: #e8f5e9; padding: 5px; margin: 5px 0; }}
                .actual {{ background: #ffebee; padding: 5px; margin: 5px 0; }}
                .json-diff {{ background: #fffde7; padding: 10px; margin: 10px 0; border-radius: 4px; }}
                .step-name {{ color: #1976d2; font-weight: bold; }}
                .timestamp {{ color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚠️ Soft Assertions Summary Report</h1>
                    <p>Test contains soft assertion failures that require attention</p>
                </div>
                
                <div class="summary">
                    <strong>Total Failures:</strong> {total}<br>
                    <strong>Report Generated:</strong> {ts}<br>
                    <strong>Status:</strong> <span style="color: #ff9800; font-weight: bold;">⚠️ WARNING</span> (Test PASSED with warnings)
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Step Name</th>
                            <th>Message</th>
                            <th>Expected vs Actual</th>
                            <th>Timestamp</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        
        return html
        
        return html
    
    def raise_with_warning(self):
        """
        Raise exception but mark as warning (not failure) in logs.
        This allows test to stay PASSED but with warning indicator.
        """
        error_msg = f"\n⚠️ WARNING: {len(self.failures)} soft assertion(s) failed:\n"
        for failure in self.failures:
            error_msg += f"\n  #{failure.assertion_number}: {failure.message}\n"
            error_msg += f"    Expected: {failure.expected}\n"
            error_msg += f"    Actual: {failure.actual}\n"
        
        logger.warning(error_msg)
        allure.attach(
            error_msg,
            name="⚠️ Soft Assertions Warning Summary",
            attachment_type=allure.attachment_type.TEXT
        )
        
        # Raise but this will be caught and handled as warning
        raise SoftAssertionWarning(error_msg)
    
    def get_failure_count(self) -> int:
        """Get count of soft assertion failures."""
        return len(self.failures)
    
    def has_failures(self) -> bool:
        """Check if there are any failures."""
        return len(self.failures) > 0


class SoftAssertionWarning(Exception):
    """
    Exception for soft assertion failures.
    Marked as WARNING not FAILURE for test reporting.
    """
    pass
