"""
Screenshot Helper Utility
Provides enhanced screenshot functionality for test documentation and debugging
"""
from playwright.sync_api import Page
from pathlib import Path
from typing import Optional, Dict, Any
import datetime
import os


def take_screenshot(page: Page, name: str, full_page: bool = True, 
                   path: Optional[str] = None) -> str:
    """
    Take a screenshot with automatic naming and organization
    
    Args:
        page: Playwright page object
        name: Base name for the screenshot
        full_page: Whether to capture full page or just viewport
        path: Optional custom path, otherwise uses default structure
        
    Returns:
        Path to the saved screenshot file
    """
    # Set up screenshot directory
    if path:
        screenshot_dir = Path(path)
    else:
        # Default to reports/oam/screenshots directory
        base_dir = Path(__file__).parent.parent
        screenshot_dir = base_dir / "reports" / "oam" / "screenshots"
    
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name}_{timestamp}.png"
    screenshot_path = screenshot_dir / filename
    
    # Take screenshot
    page.screenshot(path=str(screenshot_path), full_page=full_page)
    
    print(f"Screenshot saved: {screenshot_path}")
    return str(screenshot_path)


def take_element_screenshot(page: Page, selector: str, name: str, 
                           path: Optional[str] = None) -> str:
    """
    Take a screenshot of a specific element
    
    Args:
        page: Playwright page object
        selector: CSS selector or locator for the element
        name: Base name for the screenshot
        path: Optional custom path
        
    Returns:
        Path to the saved screenshot file
    """
    # Set up screenshot directory
    if path:
        screenshot_dir = Path(path)
    else:
        base_dir = Path(__file__).parent.parent
        screenshot_dir = base_dir / "reports" / "screenshots" / "elements"
    
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"element_{name}_{timestamp}.png"
    screenshot_path = screenshot_dir / filename
    
    # Take element screenshot
    element = page.locator(selector)
    element.screenshot(path=str(screenshot_path))
    
    print(f"Element screenshot saved: {screenshot_path}")
    return str(screenshot_path)


def take_comparison_screenshots(page: Page, name: str, 
                               before_action: callable = None,
                               after_action: callable = None) -> Dict[str, str]:
    """
    Take before and after screenshots for comparison
    
    Args:
        page: Playwright page object
        name: Base name for the screenshots
        before_action: Optional action to perform before the "before" screenshot
        after_action: Action to perform between before and after screenshots
        
    Returns:
        Dictionary with 'before' and 'after' screenshot paths
    """
    screenshots = {}
    
    # Take before screenshot
    if before_action:
        before_action()
    screenshots['before'] = take_screenshot(page, f"{name}_before")
    
    # Perform action if provided
    if after_action:
        after_action()
        page.wait_for_timeout(1000)  # Brief wait for UI changes
    
    # Take after screenshot
    screenshots['after'] = take_screenshot(page, f"{name}_after")
    
    return screenshots


def take_error_screenshot(page: Page, error_context: str, 
                         include_console_logs: bool = True) -> Dict[str, str]:
    """
    Take a screenshot when an error occurs, with additional debugging info
    
    Args:
        page: Playwright page object
        error_context: Description of the error context
        include_console_logs: Whether to capture console logs
        
    Returns:
        Dictionary with screenshot path and optional console log info
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create error screenshots directory
    base_dir = Path(__file__).parent.parent
    error_dir = base_dir / "reports" / "screenshots" / "errors"
    error_dir.mkdir(parents=True, exist_ok=True)
    
    # Take screenshot
    screenshot_name = f"error_{error_context}_{timestamp}.png"
    screenshot_path = error_dir / screenshot_name
    page.screenshot(path=str(screenshot_path), full_page=True)
    
    result = {"screenshot": str(screenshot_path)}
    
    # Capture additional debugging info
    debug_info = []
    debug_info.append(f"Error Context: {error_context}")
    debug_info.append(f"Current URL: {page.url}")
    debug_info.append(f"Page Title: {page.title()}")
    
    if include_console_logs:
        # This would need to be captured during page navigation
        # Since we can't retroactively get console logs, we'll note this limitation
        debug_info.append("Console logs: Enable console log capture in test setup for detailed logs")
    
    # Save debug info to text file
    debug_file = error_dir / f"error_{error_context}_{timestamp}_debug.txt"
    with open(debug_file, 'w') as f:
        f.write('\n'.join(debug_info))
    
    result["debug_info"] = str(debug_file)
    
    print(f"Error screenshot and debug info saved:")
    print(f"  Screenshot: {screenshot_path}")
    print(f"  Debug info: {debug_file}")
    
    return result


def take_workflow_screenshots(page: Page, workflow_name: str, 
                             steps: list) -> Dict[str, str]:
    """
    Take screenshots at each step of a workflow
    
    Args:
        page: Playwright page object
        workflow_name: Name of the workflow (e.g. "login_flow", "journal_transfer")
        steps: List of step names/descriptions
        
    Returns:
        Dictionary mapping step names to screenshot paths
    """
    base_dir = Path(__file__).parent.parent
    workflow_dir = base_dir / "reports" / "screenshots" / "workflows" / workflow_name
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    screenshots = {}
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for i, step in enumerate(steps, 1):
        step_name = step.lower().replace(' ', '_').replace('/', '_')
        filename = f"step_{i:02d}_{step_name}_{timestamp}.png"
        screenshot_path = workflow_dir / filename
        
        page.screenshot(path=str(screenshot_path), full_page=True)
        screenshots[step] = str(screenshot_path)
        
        print(f"Workflow screenshot {i}: {step} -> {screenshot_path}")
    
    return screenshots


def setup_screenshot_directory() -> str:
    """
    Set up the main screenshot directory structure
    
    Returns:
        Path to the main screenshots directory
    """
    base_dir = Path(__file__).parent.parent
    screenshot_base = base_dir / "reports" / "screenshots"
    
    # Create subdirectories
    subdirs = ["elements", "errors", "workflows", "comparisons"]
    for subdir in subdirs:
        (screenshot_base / subdir).mkdir(parents=True, exist_ok=True)
    
    return str(screenshot_base)


def cleanup_old_screenshots(days_to_keep: int = 7) -> int:
    """
    Clean up screenshot files older than specified days
    
    Args:
        days_to_keep: Number of days of screenshots to retain
        
    Returns:
        Number of files deleted
    """
    base_dir = Path(__file__).parent.parent
    screenshot_dir = base_dir / "reports" / "screenshots"
    
    if not screenshot_dir.exists():
        return 0
    
    cutoff_time = datetime.datetime.now() - datetime.timedelta(days=days_to_keep)
    deleted_count = 0
    
    for screenshot_file in screenshot_dir.rglob("*.png"):
        if screenshot_file.stat().st_mtime < cutoff_time.timestamp():
            try:
                screenshot_file.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"Could not delete {screenshot_file}: {e}")
    
    # Also clean up debug text files
    for debug_file in screenshot_dir.rglob("*_debug.txt"):
        if debug_file.stat().st_mtime < cutoff_time.timestamp():
            try:
                debug_file.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"Could not delete {debug_file}: {e}")
    
    print(f"Cleaned up {deleted_count} old screenshot files")
    return deleted_count


# Configuration class for screenshot settings
class ScreenshotConfig:
    """Configuration settings for screenshot functionality"""
    
    DEFAULT_FULL_PAGE = True
    DEFAULT_QUALITY = 90  # JPEG quality if format is changed
    DEFAULT_FORMAT = "png"
    AUTO_CLEANUP_DAYS = 7
    
    @classmethod
    def set_defaults(cls, full_page: bool = True, format: str = "png"):
        """Set default screenshot configuration"""
        cls.DEFAULT_FULL_PAGE = full_page
        cls.DEFAULT_FORMAT = format