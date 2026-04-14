"""
Example usage of Enhanced Soft Assertions in BDD step definitions

This file demonstrates best practices for using EnhancedSoftAssertions
to perform multiple assertions while capturing screenshots and generating
beautiful HTML reports in Allure.

Key Features Demonstrated:
1. Creating context manager with page reference
2. Performing multiple assertions without stopping on first failure
3. Automatic screenshot capture on failure
4. Expected vs Actual comparison with JSON diff
5. Step name context for better reporting
6. HTML summary report generation
"""

from pytest_bdd import given, when, then
import allure

from utils.soft_assertions_enhanced import EnhancedSoftAssertions
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


# ============================================================================
# EXAMPLE 1: Basic Soft Assertions with Screenshots
# ============================================================================

@then("verify all user details with screenshots")
def verify_user_details(page, test_context):
    """
    Example: Verify multiple user details and capture screenshots on failure.
    
    Benefits:
    - All assertions run even if one fails
    - Screenshot captured for each failure
    - Beautiful HTML summary in Allure report
    - Test stays PASSED with warning indicator
    """
    user_data = test_context.get("user_data", {})
    
    with EnhancedSoftAssertions(page) as soft:
        # Each assertion that fails will automatically capture a screenshot
        soft.assert_equal(
            actual=user_data.get("name"),
            expected="John Doe",
            message="Username should be John Doe",
            step_name="Verify User Name"
        )
        
        soft.assert_equal(
            actual=user_data.get("email"),
            expected="john@example.com",
            message="Email should match expected",
            step_name="Verify Email Address"
        )
        
        soft.assert_true(
            condition=user_data.get("is_active", False),
            message="User should be active",
            step_name="Verify Active Status"
        )
        
        soft.assert_not_none(
            value=user_data.get("user_id"),
            message="User ID should not be null",
            step_name="Verify User ID"
        )
    
    # Report automatically generated and attached to Allure
    # Test will PASS with yellow warning if failures exist


# ============================================================================
# EXAMPLE 2: Complex Object Comparison with JSON Diff
# ============================================================================

@then("verify API response structure")
def verify_api_response(page, test_context):
    """
    Example: Verify complex API response with automatic JSON diff.
    
    When comparing dict/JSON objects, the soft assertions will:
    - Detect that values are dicts/lists
    - Pretty-print both sides as JSON
    - Show side-by-side comparison in HTML report
    """
    api_response = test_context.get("api_response", {})
    
    expected_response = {
        "status": "success",
        "data": {
            "id": 123,
            "name": "Test User",
            "roles": ["admin", "editor"]
        },
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    with EnhancedSoftAssertions(page) as soft:
        # Full object comparison - will show JSON diff
        soft.assert_equal(
            actual=api_response.get("data"),
            expected=expected_response.get("data"),
            message="Response data structure matches",
            step_name="Verify Response Data"
        )
        
        # Individual field assertions
        soft.assert_equal(
            actual=api_response.get("status"),
            expected="success",
            message="Response status is success",
            step_name="Verify Status"
        )
        
        # Assertion on nested values
        soft.assert_in(
            item="admin",
            container=api_response.get("data", {}).get("roles", []),
            message="Admin role should be present",
            step_name="Verify Admin Role"
        )
    
    # HTML report shows:
    # - Expected JSON structure
    # - Actual JSON structure
    # - Differences highlighted
    # - Screenshot if page rendered incorrectly


# ============================================================================
# EXAMPLE 3: List and Container Assertions
# ============================================================================

@then("verify page contains all required elements")
def verify_page_elements(page, test_context):
    """
    Example: Verify that container (list, set, string) contains expected items.
    """
    page_text = page.text_content()
    visible_buttons = []
    
    with EnhancedSoftAssertions(page) as soft:
        # Check that required text is on page
        soft.assert_in(
            item="Submit",
            container=page_text,
            message="Submit button text should be visible",
            step_name="Verify Submit Button"
        )
        
        soft.assert_in(
            item="Cancel",
            container=page_text,
            message="Cancel button text should be visible",
            step_name="Verify Cancel Button"
        )
        
        # Check that unwanted content is NOT on page
        soft.assert_not_in(
            item="Error",
            container=page_text,
            message="Error message should not appear",
            step_name="Verify No Errors"
        )


# ============================================================================
# EXAMPLE 4: Checking Failure Count (Conditional Actions)
# ============================================================================

@then("verify data and log if there are failures")
def verify_with_conditional_logging(page, test_context):
    """
    Example: Perform assertions and conditionally log based on failure count.
    """
    data = test_context.get("data", {})
    
    soft = EnhancedSoftAssertions(page)
    
    with soft:
        soft.assert_equal(data.get("field1"), "expected1", step_name="Check Field 1")
        soft.assert_equal(data.get("field2"), "expected2", step_name="Check Field 2")
        soft.assert_equal(data.get("field3"), "expected3", step_name="Check Field 3")
    
    # Can check results after context exits
    if soft.has_failures():
        logger.warning(f"Data verification found {soft.get_failure_count()} issues")
        logger.warning("These are NON-BLOCKING - test will pass with warning")
    else:
        logger.info("All data verifications passed!")


# ============================================================================
# EXAMPLE 5: Nested Assertions Within Step
# ============================================================================

@then("verify complex business logic")
def verify_complex_logic(page, test_context):
    """
    Example: Multiple soft assertion blocks in single step.
    Each block represents a different concern.
    """
    account = test_context.get("account", {})
    
    # First set of checks - Account Info
    logger.info("Verifying account information...")
    with EnhancedSoftAssertions(page) as soft:
        soft.assert_not_none(account.get("id"), step_name="Account ID Exists")
        soft.assert_not_none(account.get("name"), step_name="Account Name Exists")
        soft.assert_true(
            condition=len(account.get("name", "")) > 0,
            message="Account name should not be empty",
            step_name="Account Name Not Empty"
        )
    
    # Second set of checks - Account Status
    logger.info("Verifying account status...")
    with EnhancedSoftAssertions(page) as soft:
        soft.assert_equal(
            actual=account.get("status"),
            expected="ACTIVE",
            step_name="Account Status is Active"
        )
        soft.assert_not_in(
            item="SUSPENDED",
            container=account.get("status", ""),
            message="Account should not be suspended",
            step_name="Account Not Suspended"
        )
    
    # Each context generates its own HTML report
    # If both have failures, you'll see 2 separate reports


# ============================================================================
# EXAMPLE 6: Using with Custom Page State Capture
# ============================================================================

@then("verify user can perform actions")
def verify_user_actions(page, test_context):
    """
    Example: Take screenshots at different points in user journey.
    """
    with EnhancedSoftAssertions(page) as soft:
        # Screenshot captured if next assertion fails
        soft.assert_true(
            page.get_by_role("button", name="Edit").is_visible(),
            message="Edit button should be visible",
            step_name="Edit Button Visible"
        )
        
        # Screenshot at this point if fails
        soft.assert_true(
            page.get_by_role("button", name="Delete").is_enabled(),
            message="Delete button should be enabled",
            step_name="Delete Button Enabled"
        )
        
        # Screenshot shows actual page state when assertion failed
        soft.assert_true(
            page.get_by_role("button", name="Export").is_visible(),
            message="Export button should be visible",
            step_name="Export Button Visible"
        )


# ============================================================================
# USAGE GUIDELINES
# ============================================================================
"""
✅ DO:
- Pass `page` parameter to enable screenshot capture
- Include `step_name` parameter for better context
- Use descriptive `message` for clarity
- Keep assertions focused per context manager
- Place related assertions in same context
- Use helper assertions like assert_in, assert_not_none

❌ DON'T:
- Forget to pass `page` parameter (screenshots won't work)
- Leave messages empty (make them descriptive)
- Mix unrelated assertions in same context
- Use regular assert - use soft assertion methods
- Forget to define test_context with required values

📊 REPORTING:
- Each failure gets a screenshot (if page provided)
- HTML summary shows all failures side-by-side
- JSON diffs automatically generated for dict/list comparisons
- Expected vs Actual clearly labeled
- Test stays PASSED with yellow warning indicator
- All attachments visible in Allure report

🔍 ALLURE OUTPUT:
- Test marked as PASSED (not FAILED)
- Severity label: "warning"
- Status badge: "⚠️ WARNINGS"
- Attachments:
  - Individual failure screenshots
  - Soft Assertions Summary Report (HTML)
  - Soft Assertions Warning Summary (text)
"""
