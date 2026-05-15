"""
Unified Allure Logger - Combines logging and Allure reporting seamlessly.

This module provides a wrapper that:
- Logs to console/file using Python logging
- Automatically attaches to Allure reports when in test context
- Works in both test and non-test contexts (pages, utilities)
- Reduces boilerplate code
- Auto-screenshot after steps (configurable)
"""

import logging
import os
from contextlib import contextmanager
from typing import Any

import allure


# Global step screenshot configuration
class StepScreenshotConfig:
    """Global configuration for automatic step screenshots"""

    def __init__(self):
        # Check environment variable: SCREENSHOT_EACH_STEP=true/false
        env_value = os.getenv("SCREENSHOT_EACH_STEP", "false").lower()
        self.enabled = env_value in ("true", "1", "yes", "on")
        self.step_counter = 0
        self.screenshot_on_failure_only = (
            not self.enabled
        )  # If not enabled for all, only on failure

    def reset_counter(self):
        """Reset step counter (called at test start)"""
        self.step_counter = 0

    def should_screenshot(self, step_failed: bool = False) -> bool:
        """Determine if screenshot should be taken"""
        if step_failed:
            return True  # Always screenshot on failure
        return self.enabled  # Otherwise, check if enabled for all steps


_screenshot_config = StepScreenshotConfig()


class AllureLogger:
    """
    Logger that automatically integrates with Allure reports.

    Usage:
        logger = AllureLogger(__name__)

        # Simple logging - goes to console and allure
        logger.info("User logged in")

        # With allure step
        with logger.step("Login to application"):
            logger.info("Entering credentials")
            # ... actions ...

        # Attach data to allure
        logger.attach_text("User ID: 12345", "User Info")
        logger.attach_screenshot(page, "Login Page")
    """

    def __init__(self, name: str, level: int = logging.INFO):
        """
        Initialize AllureLogger.

        Args:
            name: Logger name (typically __name__ from calling module)
            level: Logging level (default: INFO)
        """
        self.logger = logging.getLogger(name)

        # Only configure if not already configured
        if not self.logger.handlers:
            self.logger.setLevel(level)
            handler = logging.StreamHandler()
            handler.setLevel(level)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def debug(self, msg: str, attach_to_allure: bool = True) -> None:
        """
        Log debug message.

        Args:
            msg: Message to log
            attach_to_allure: If True, also attach to Allure report (default: True)

        Output:
            - Console/log file: Always
            - Allure report: Only if attach_to_allure=True
        """
        self.logger.debug(msg)
        if attach_to_allure:
            allure.attach(msg, name="Debug", attachment_type=allure.attachment_type.TEXT)

    def info(self, msg: str, attach_to_allure: bool = True) -> None:
        """
        Log info message.

        Args:
            msg: Message to log
            attach_to_allure: If True, also attach to Allure report (default: True)

        Output:
            - Console/log file: Always
            - Allure report: Only if attach_to_allure=True

        Example:
            logger.info("Searching for client: ABC123")  # Console + Allure
            logger.info("Debug info", attach_to_allure=False)  # Console only
        """
        self.logger.info(msg)
        if attach_to_allure:
            allure.attach(msg, name="Info", attachment_type=allure.attachment_type.TEXT)

    def warning(self, msg: str, attach_to_allure: bool = True) -> None:
        """
        Log warning message - automatically attaches to Allure by default.

        Args:
            msg: Warning message
            attach_to_allure: If True, also attach to Allure report (default: True)

        Output:
            - Console/log file: Always
            - Allure report: By default (can disable with attach_to_allure=False)
        """
        self.logger.warning(msg)
        if attach_to_allure:
            allure.attach(msg, name="Warning", attachment_type=allure.attachment_type.TEXT)

    def error(self, msg: str, attach_to_allure: bool = True) -> None:
        """
        Log error message - automatically attaches to Allure by default.

        Args:
            msg: Error message
            attach_to_allure: If True, also attach to Allure report (default: True)

        Output:
            - Console/log file: Always
            - Allure report: By default (can disable with attach_to_allure=False)
        """
        self.logger.error(msg)
        if attach_to_allure:
            allure.attach(msg, name="Error", attachment_type=allure.attachment_type.TEXT)

    def critical(self, msg: str, attach_to_allure: bool = True) -> None:
        """
        Log critical message - automatically attaches to Allure by default.

        Args:
            msg: Critical message
            attach_to_allure: If True, also attach to Allure report (default: True)

        Output:
            - Console/log file: Always
            - Allure report: By default (can disable with attach_to_allure=False)
        """
        self.logger.critical(msg)
        if attach_to_allure:
            allure.attach(msg, name="Critical", attachment_type=allure.attachment_type.TEXT)

    @contextmanager
    def step(self, title: str, page=None, log: bool = True, auto_screenshot: bool = True):
        """
        Context manager for Allure steps with optional auto-screenshot.

        Args:
            title: Step title for Allure report
            page: Playwright Page object (optional, for auto-screenshot)
            log: Whether to also log to console (default: True)
            auto_screenshot: Whether to auto-screenshot after step (default: True)

        Usage:
            # Without auto-screenshot
            with logger.step("Login to application"):
                # ... actions ...

            # With auto-screenshot
            with logger.step("Search for client", page=page):
                # ... actions ...
                # Screenshot automatically taken at end
        """
        global _screenshot_config

        if log:
            self.info(f"Step: {title}", attach_to_allure=False)

        step_failed = False
        try:
            with allure.step(title):
                yield
        except Exception:
            step_failed = True
            raise
        finally:
            # Auto-screenshot if page provided and config allows
            if page and auto_screenshot and _screenshot_config.should_screenshot(step_failed):
                try:
                    _screenshot_config.step_counter += 1
                    status = "FAILED" if step_failed else "PASSED"
                    screenshot_name = f"Step {_screenshot_config.step_counter} {status} {title}"
                    self.attach_screenshot(page, screenshot_name)
                except Exception as screenshot_error:
                    self.logger.warning(f"Failed to take step screenshot: {screenshot_error}")

    def attach_text(self, content: str, name: str = "Text") -> None:
        """Attach text to Allure report"""
        allure.attach(content, name=name, attachment_type=allure.attachment_type.TEXT)

    def attach_json(self, content: dict, name: str = "JSON") -> None:
        """Attach JSON data to Allure report"""
        import json

        allure.attach(
            json.dumps(content, indent=2), name=name, attachment_type=allure.attachment_type.JSON
        )

    def attach_screenshot(self, page, name: str = "Screenshot") -> None:
        """
        Take and attach screenshot to Allure report.

        Args:
            page: Playwright Page object
            name: Screenshot name in report
        """
        screenshot = page.screenshot()
        allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)

    def attach_html(self, content: str, name: str = "HTML") -> None:
        """Attach HTML content to Allure report"""
        allure.attach(content, name=name, attachment_type=allure.attachment_type.HTML)

    def attach_data(self, data: Any, name: str, attach_type: str = "TEXT") -> None:
        """
        Generic attach method for any data type.

        Args:
            data: Data to attach
            name: Attachment name
            attach_type: Allure attachment type
        """
        attachment_type = getattr(allure.attachment_type, attach_type, allure.attachment_type.TEXT)
        allure.attach(str(data), name=name, attachment_type=attachment_type)


def get_allure_logger(name: str = __name__, level: int = logging.INFO) -> AllureLogger:
    """
    Factory function to create AllureLogger instances.

    Args:
        name: Logger name (typically __name__ from calling module)
        level: Logging level (default: INFO)

    Returns:
        AllureLogger instance
    """
    return AllureLogger(name, level)


def enable_step_screenshots(enabled: bool = True) -> None:
    """
    Enable or disable automatic screenshots after each step.

    Args:
        enabled: True to enable screenshots after every step, False to only screenshot on failure

    Usage:
        from utils.allure_logger import enable_step_screenshots

        # In conftest.py or at test start
        enable_step_screenshots(True)

        # Or via environment variable:
        # export SCREENSHOT_EACH_STEP=true
    """
    global _screenshot_config
    _screenshot_config.enabled = enabled
    print(f"Step screenshots: {'ENABLED' if enabled else 'DISABLED (failure only)'}")


def reset_step_counter() -> None:
    """
    Reset the step counter (useful at test start).

    Usage:
        from utils.allure_logger import reset_step_counter

        @pytest.fixture(autouse=True)
        def reset_steps():
            reset_step_counter()
    """
    global _screenshot_config
    _screenshot_config.reset_counter()


def get_step_screenshot_config() -> StepScreenshotConfig:
    """Get the current step screenshot configuration"""
    global _screenshot_config
    return _screenshot_config
