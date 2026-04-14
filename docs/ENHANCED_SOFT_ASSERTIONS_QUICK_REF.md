"""
Enhanced Soft Assertions - Quick Reference

Use this as a quick lookup guide for the most common operations.
For detailed documentation, see ENHANCED_SOFT_ASSERTIONS_ARCHITECTURE.md
"""

# ============================================================================
# QUICK START
# ============================================================================

# IMPORT:
from utils.soft_assertions_enhanced import EnhancedSoftAssertions

# BASIC USAGE:
@then("verify something")
def verify_something(page, test_context):
    with EnhancedSoftAssertions(page) as soft:
        soft.assert_equal(actual, expected, "message", step_name="Step Name")
    # Test PASSED ✅ + ⚠️ WARNING (if failures) or ✅ PASSED (if all passed)


# ============================================================================
# ASSERTION METHODS CHEAT SHEET
# ============================================================================

"""
EQUALITY:
  soft.assert_equal(5, 5)
  soft.assert_not_equal(5, 10)

BOOLEAN:
  soft.assert_true(user.is_active)
  soft.assert_false(user.is_deleted)

NULL:
  soft.assert_none(value)
  soft.assert_not_none(user_id)

CONTAINER:
  soft.assert_in("admin", user.roles)
  soft.assert_not_in("banned", user.status)

ALL WITH OPTIONS:
  soft.assert_equal(
      actual=response_code,
      expected=200,
      message="HTTP response should be 200",
      step_name="Verify Response Code"
  )
"""

# ============================================================================
# COMMON PATTERNS
# ============================================================================

# PATTERN 1: Verify multiple fields
@then("verify user profile")
def verify_user(page, test_context):
    user = test_context["user"]
    with EnhancedSoftAssertions(page) as soft:
        soft.assert_not_none(user.get("id"), step_name="User ID")
        soft.assert_equal(user.get("status"), "ACTIVE", step_name="User Status")
        soft.assert_in("ADMIN", user.get("roles", []), step_name="User Roles")


# PATTERN 2: Verify API response
@then("verify API response")
def verify_api(page, test_context):
    response = test_context.get("api_response", {})
    with EnhancedSoftAssertions(page) as soft:
        soft.assert_equal(response.get("status"), "success", step_name="Status")
        soft.assert_not_none(response.get("data"), step_name="Data Present")
        # If comparing dicts, JSON diff auto-generated
        soft.assert_equal(
            response.get("meta"),
            {"version": "1.0", "timestamp": "2024-01-01"},
            step_name="Verify Metadata"
        )


# PATTERN 3: Verify page elements
@then("verify form elements")
def verify_form(page, test_context):
    with EnhancedSoftAssertions(page) as soft:
        soft.assert_true(
            page.get_by_label("Email").is_visible(),
            message="Email field visible",
            step_name="Email Field"
        )
        soft.assert_true(
            page.get_by_role("button", name="Submit").is_enabled(),
            message="Submit button enabled",
            step_name="Submit Button"
        )


# PATTERN 4: Conditional checking after assertions
@then("verify and log failures")
def verify_and_log(page, test_context):
    soft = EnhancedSoftAssertions(page)
    with soft:
        soft.assert_equal(value1, expected1, step_name="Check 1")
        soft.assert_equal(value2, expected2, step_name="Check 2")
    
    # Can check after context exits
    if soft.has_failures():
        logger.warning(f"Found {soft.get_failure_count()} failures")


# ============================================================================
# WHAT GETS CAPTURED
# ============================================================================

"""
WHEN ASSERTION FAILS:

1. SCREENSHOT CAPTURED
   - Shows page state at failure moment
   - Attached to Allure as "[SA #N] message"
   - Click to view full page screenshot
   
2. TEXT ATTACHMENT
   - Allure attachment: "Soft Assertion Failure #N"
   - Shows: Expected vs Actual values
   
3. FAILURE RECORD CREATED
   - Message: Custom description
   - Expected: What we wanted
   - Actual: What we got
   - Timestamp: When it failed
   - Screenshot path: Reference to image
   - Step name: What step failed
   
4. JSON DIFF (if applicable)
   - Automatically generates if comparing dicts/lists
   - Pretty-printed on separate lines
   - Easy to spot differences

5. HTML SUMMARY (when context exits)
   - Beautiful table with all failures
   - Expected vs Actual side-by-side
   - Screenshots embedded
   - JSON diffs shown
   - Timestamps included
"""

# ============================================================================
# ALLURE OUTPUT REFERENCE
# ============================================================================

"""
TEST RESULT:
  ✅ PASSED ⚠️ WARNING (or ✅ PASSED if no failures)

LABELS:
  • severity: warning
  • status_badge: ⚠️ WARNINGS

ATTACHMENTS:
  [SA #1] Error message 1 (screenshot.png)
  [SA #2] Error message 2 (screenshot.png)
  Soft Assertion Failure #1 (text)
  Soft Assertion Failure #2 (text)
  ⚠️ Soft Assertions Summary Report (HTML) ← Main summary
  ⚠️ Soft Assertions Warning Summary (text)

To read results:
  1. Click test in Allure
  2. Find "⚠️ Soft Assertions Summary Report" attachment
  3. Click to view beautiful HTML table
  4. See all failures with screenshots
"""

# ============================================================================
# PARAMETER QUICK REFERENCE
# ============================================================================

"""
Constructor:
  EnhancedSoftAssertions(page)
    page: Playwright Page object (required for screenshots)
    
  with EnhancedSoftAssertions(page) as soft:

Assertion Parameters:
  soft.assert_equal(
      actual,                    # Value being checked
      expected,                  # What we expect
      message=None,              # Custom failure message (optional)
      step_name=None             # Step name for context (optional)
  )
  
  # Same parameters for all these:
  soft.assert_not_equal(actual, expected, message, step_name)
  soft.assert_true(condition, message, step_name)
  soft.assert_false(condition, message, step_name)
  soft.assert_none(value, message, step_name)
  soft.assert_not_none(value, message, step_name)
  soft.assert_in(item, container, message, step_name)
  soft.assert_not_in(item, container, message, step_name)

Later Methods:
  soft.generate_report()        # Manually trigger report (auto in __exit__)
  soft.get_failure_count()      # Returns int of failure count
  soft.has_failures()           # Returns bool (True if failures exist)
  soft.failures                 # Access raw failure list
"""

# ============================================================================
# ERROR MESSAGES YOU MIGHT SEE
# ============================================================================

"""
MESSAGE: "Values do not match"
  WHEN: soft.assert_equal() fails
  FIX: Verify expected value is correct
  
MESSAGE: "Condition is not True"
  WHEN: soft.assert_true() fails
  FIX: Check that condition evaluates to True
  
MESSAGE: "Assertion does not match"
  WHEN: Your custom message appears
  FIX: Read the message to understand what failed
  
MESSAGE: "[SOFT ASSERTION #N] ..."
  WHEN: In logs - failure detected
  FIX: Check Allure report for details
  
MESSAGE: "Test PASSED ⚠️ WARNING"
  WHEN: In Allure - soft failures found
  EXPECTED: This is working as intended - soft assertions don't fail tests
"""

# ============================================================================
# MIGRATION FROM OLD SOFTASSERTIONS
# ============================================================================

"""
IF USING OLD:
  from utils.assertions import SoftAssertions
  with SoftAssertions() as soft:
      soft.assert_equal(actual, expected)

CHANGE TO:
  from utils.soft_assertions_enhanced import EnhancedSoftAssertions
  with EnhancedSoftAssertions(page) as soft:
      soft.assert_equal(actual, expected, step_name="Check Value")

THAT'S IT!
  - API is compatible
  - Just add page parameter
  - Add optional step_name for better reporting
  - Everything else stays the same
"""

# ============================================================================
# DEBUGGING TIPS
# ============================================================================

"""
NO SCREENSHOTS?
  1. Check page is passed: EnhancedSoftAssertions(page)
  2. Verify page is navigated: assert page.url != "about:blank"
  3. Look in allure-results/ for PNG files

NO HTML REPORT?
  1. Check failures exist: soft.has_failures() should be True
  2. Verify context exited normally (no exception raised before)
  3. Check Allure has attachment "⚠️ Soft Assertions Summary Report"

TEST STILL FAILING?
  1. Check it's SoftAssertionWarning not regular AssertionError
  2. Verify pytest_runtest_makereport hook exists
  3. Check conftest.py has the hook
  4. Try: pytest -v to see hook execution

SCREENSHOTS BLURRY?
  1. Normal - Playwright screenshots are exact copies of page
  2. Increase resolution if needed (less common issue)
  3. Check page zoom level is 100%
"""

# ============================================================================
# BEST PRACTICES SUMMARY
# ============================================================================

"""
✅ ALWAYS:
  - Pass page parameter (enables screenshots)
  - Use step_name for readability
  - Group related assertions in one with block
  - Let soft assertions handle test status
  
❌ NEVER:
  - Use hard assert with soft assertions
  - Forget to pass page
  - Use empty messages
  - Try to manually fail test
  
🎯 GOALS:
  - Capture all failures in one test run
  - Get visual context via screenshots
  - Generate beautiful HTML reports
  - Help developers debug quickly
  - Keep test PASSED (non-blocking)
"""

# ============================================================================
# EXAMPLES BY SCENARIO
# ============================================================================

"""
SCENARIO 1: Data validation
-----------
User lists, database records, API responses

with EnhancedSoftAssertions(page) as soft:
    soft.assert_equal(db_record["status"], "ACTIVE", step_name="DB Status")
    soft.assert_equal(db_record["count"], 42, step_name="Record Count")
    soft.assert_not_none(db_record["updated_at"], step_name="Updated Time")


SCENARIO 2: UI verification
-----------
Button visibility, text content, form fields

with EnhancedSoftAssertions(page) as soft:
    soft.assert_true(
        page.get_by_role("button").is_visible(),
        step_name="Button Visible"
    )
    soft.assert_equal(
        page.locator(".message").text_content(),
        "Success",
        step_name="Success Message"
    )


SCENARIO 3: Complex object comparison
-----------
JSON responses, nested dicts, lists

response = {"user": {"id": 1, "roles": ["admin"]}}
expected = {"user": {"id": 1, "roles": ["admin"]}}

with EnhancedSoftAssertions(page) as soft:
    soft.assert_equal(response, expected, step_name="Full Response")
    # JSON diff auto-generated in HTML


SCENARIO 4: Multiple validations
-----------
Several unrelated checks

with EnhancedSoftAssertions(page) as soft:
    soft.assert_equal(status_code, 200, step_name="Status Code")
    soft.assert_in("success", response_text, step_name="Response Text")
    soft.assert_not_none(response_id, step_name="Response ID")
    soft.assert_true(len(items) > 0, step_name="Items Exist")
"""

# ============================================================================
# KEY DIFFERENCES FROM REGULAR ASSERTIONS
# ============================================================================

"""
REGULAR assert:
  assert value == expected  ← STOPS on first failure ❌
  Rest of assertions skipped
  Test marked as FAILED ❌

SOFT ASSERTIONS:
  soft.assert_equal(value, expected)  ← CONTINUES ✅
  All assertions run
  Test marked as PASSED with ⚠️ WARNING ✅

USE SOFT ASSERTIONS FOR:
  - Multiple field validations
  - Non-critical checks
  - Data that can fail gracefully
  - Cases where you want all failures at once

USE REGULAR ASSERT FOR:
  - Critical path checks
  - Authentication/authorization
  - Cases that MUST stop immediately
"""

# ============================================================================
# END QUICK REFERENCE
# ============================================================================
