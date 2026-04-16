"""
Enhanced Soft Assertions - Implementation and Architecture Guide

This guide explains the architecture, features, and integration of the
Enhanced Soft Assertions system for highlighting test failures prominently
in Allure reports while keeping tests PASSED with warning indicators.
"""

# ============================================================================
# 1. ARCHITECTURE OVERVIEW
# ============================================================================

"""
┌─────────────────────────────────────────────────────────────────────────┐
│                     ENHANCED SOFT ASSERTIONS FLOW                        │
└─────────────────────────────────────────────────────────────────────────┘

USER RUNS TEST
    ↓
STEP DEFINITION STARTS
    ↓
CREATE EnhancedSoftAssertions(page) ← Pass page for screenshots
    ↓
PERFORM ASSERTIONS:
    ├─ soft.assert_equal(actual, expected, ...)
    │   ↓
    │   [FAILURE DETECTED]
    │   ├─ Screenshot captured immediately (if page provided)
    │   ├─ HTML comparison generated (Expected vs Actual)
    │   ├─ JSON diff created (if dict/list)
    │   ├─ Entry added to self.failures list
    │   ├─ Text attachment added to Allure
    │   └─ Warning logged
    │
    └─ [Continue to next assertion - NO EARLY STOP]
    ↓
EXIT CONTEXT MANAGER (__exit__)
    ├─ Call generate_report()
    ├─ Create HTML summary table
    ├─ Attach HTML to Allure as "⚠️ Soft Assertions Summary Report"
    ├─ Raise SoftAssertionWarning if failures exist
    └─ Test execution completes
    ↓
PYTEST HOOK: pytest_runtest_makereport()
    ├─ Catches SoftAssertionWarning exception
    ├─ Adds Allure label: severity = "warning"
    ├─ Adds Allure label: status_badge = "⚠️ WARNINGS"
    ├─ Suppresses exception (prevents FAIL status)
    └─ Test stays PASSED with yellow/orange indicator
    ↓
ALLURE REPORT SHOWS:
    ├─ Test: ✅ PASSED (with ⚠️ indicator)
    ├─ Attachments:
    │   ├─ Individual failure #1 (screenshot)
    │   ├─ Individual failure #2 (screenshot)
    │   ├─ Soft Assertions Summary Report (HTML table)
    │   └─ Soft Assertions Warning Summary (text)
    └─ Easy to spot failures without reading logs


┌─────────────────────────────────────────────────────────────────────────┐
│                        SCREENSHOT CAPTURE FLOW                           │
└─────────────────────────────────────────────────────────────────────────┘

ASSERTION FAILS:
    ↓
_record_failure() called:
    ├─ Check: if page is available
    ├─ YES → _capture_screenshot()
    │   ├─ page.screenshot() taken
    │   ├─ Attached to Allure with name: "[SA #N] message"
    │   ├─ Return attachment name
    │   └─ SoftAssertionFailure.screenshot_path = name
    │
    └─ NO → screenshot_path = None (graceful degradation)
    ↓
Failure recorded with screenshot metadata
"""

# ============================================================================
# 2. CLASS HIERARCHY
# ============================================================================

"""
┌────────────────────────────────────────────┐
│        SoftAssertionFailure                │
│        (dataclass)                         │
├────────────────────────────────────────────┤
│ - assertion_number: int                    │
│ - message: str                             │
│ - expected: Any                            │
│ - actual: Any                              │
│ - timestamp: str                           │
│ - screenshot_path: Optional[str]           │
│ - step_name: Optional[str]                 │
├────────────────────────────────────────────┤
│ + to_dict()                                │
│ + _try_json()                              │
└────────────────────────────────────────────┘
           △
           │ stored in
           │
┌────────────────────────────────────────────┐
│    EnhancedSoftAssertions                  │
│    (context manager)                       │
├────────────────────────────────────────────┤
│ - page: Page (optional)                    │
│ - failures: List[SoftAssertionFailure]    │
│ - _assertion_count: int                    │
├────────────────────────────────────────────┤
│ + assert_equal()                           │
│ + assert_not_equal()                       │
│ + assert_true()                            │
│ + assert_false()                           │
│ + assert_in()                              │
│ + assert_not_in()                          │
│ + assert_none()                            │
│ + assert_not_none()                        │
│ + generate_report()                        │
│ + raise_with_warning()                     │
│ + get_failure_count()                      │
│ + has_failures()                           │
├────────────────────────────────────────────┤
│ - _record_failure()                        │
│ - _capture_screenshot()                    │
│ - _generate_html_report()                  │
└────────────────────────────────────────────┘
           △
           │ raises
           │
┌────────────────────────────────────────────┐
│      SoftAssertionWarning                  │
│      (Exception)                           │
├────────────────────────────────────────────┤
│ - Inherits from Exception                 │
│ - Used to mark test with warning          │
│ - Caught by pytest hook                   │
│ - Does NOT fail test (PASSED + warning)  │
└────────────────────────────────────────────┘
"""

# ============================================================================
# 3. ASSERTION METHODS REFERENCE
# ============================================================================

"""
BASIC EQUALITY:
- assert_equal(actual, expected, message, step_name)
  └─ Fails if actual != expected
  
- assert_not_equal(actual, expected, message, step_name)
  └─ Fails if actual == expected

BOOLEAN CHECKS:
- assert_true(condition, message, step_name)
  └─ Fails if condition is False
  
- assert_false(condition, message, step_name)
  └─ Fails if condition is True

NULL CHECKS:
- assert_none(value, message, step_name)
  └─ Fails if value is not None
  
- assert_not_none(value, message, step_name)
  └─ Fails if value is None

CONTAINER CHECKS:
- assert_in(item, container, message, step_name)
  └─ Fails if item not in container (works with lists, dicts, strings, etc.)
  
- assert_not_in(item, container, message, step_name)
  └─ Fails if item in container


ALL METHODS SUPPORT:
- actual/condition/value/item - The value being checked
- expected/container - What we expect/check against (some methods)
- message - Custom failure message (optional, default provided)
- step_name - Name of the step for context (optional, useful for reports)

RETURNS: None (failures collected in list, not raised immediately)

WHEN RAISED: Only after exiting context manager's __exit__
"""

# ============================================================================
# 4. FILE STRUCTURE
# ============================================================================

"""
PROJECT_ROOT/
├── utils/
│   ├── soft_assertions_enhanced.py         [NEW] Enhanced soft assertions
│   │   ├── SoftAssertionFailure (dataclass)
│   │   ├── EnhancedSoftAssertions (context manager)
│   │   └── SoftAssertionWarning (exception)
│   │
│   └── allure_logger.py                    [EXISTING] Logger integration
│       └── Used for logging failures to Allure
│
├── tests/
│   └── bdd/
│       ├── conftest.py                     [MODIFIED] Added pytest hook
│       │   ├── pytest_runtest_makereport()
│       │   │   └─ Catches SoftAssertionWarning
│       │   │   └─ Adds warning label to Allure
│       │   │   └─ Suppresses exception
│       │   └─ pytest_sessionfinish()       [EXISTING]
│       │
│       └── steps/
│           ├── item_detail_steps.py        [CAN BE MODIFIED] Use enhanced soft asserts
│           │   └─ Replace SoftAssertions with EnhancedSoftAssertions(page)
│           │
│           └── other_steps.py              [CAN BE MODIFIED] Use enhanced soft asserts
│               └─ Replace SoftAssertions with EnhancedSoftAssertions(page)
│
└── docs/
    ├── ENHANCED_SOFT_ASSERTIONS_GUIDE.md   [NEW] Usage examples
    └── ENHANCED_SOFT_ASSERTIONS_ARCHITECTURE.md [THIS FILE]
"""

# ============================================================================
# 5. INTEGRATION WITH EXISTING CODE
# ============================================================================

"""
CURRENT STATE (OLD):
    from utils.assertions import SoftAssertions
    
    with SoftAssertions() as soft:
        soft.assert_equal(actual, expected)
        soft.assert_true(condition)
    # Failures only in logs, no screenshots

ENHANCED STATE (NEW):
    from utils.soft_assertions_enhanced import EnhancedSoftAssertions
    
    with EnhancedSoftAssertions(page) as soft:
        soft.assert_equal(actual, expected, message, step_name="Check Value")
        soft.assert_true(condition, step_name="Check Status")
    # Screenshots captured, HTML summary generated, yellow warning shown


MIGRATION PATH:
1. Import EnhancedSoftAssertions instead of SoftAssertions
2. Pass `page` parameter to constructor
3. Add optional `step_name` to assertion calls (improves readability)
4. Keep everything else the same - API is compatible

Step definitions can use both:
    from utils.soft_assertions_enhanced import EnhancedSoftAssertions
    
    @then("verify details")
    def verify_details(page, test_context):
        with EnhancedSoftAssertions(page) as soft:
            soft.assert_equal(...)  # Will capture screenshots on failure


PYTEST HOOK INTEGRATION (AUTOMATIC):
    conftest.py already has pytest_runtest_makereport()

    When SoftAssertionWarning is raised:
    ├─ Hook catches it
    ├─ Adds severity="warning" label
    ├─ Adds status_badge="⚠️ WARNINGS" label
    ├─ Suppresses exception
    └─ Test stays PASSED

    No additional setup needed - works automatically!
"""

# ============================================================================
# 6. ALLURE REPORT OUTPUT
# ============================================================================

"""
VISUAL HIERARCHY IN ALLURE REPORT:

┌─────────────────────────────────────────────────────────────────┐
│  TEST RESULT BADGE                          ✅ PASSED ⚠️        │
├─────────────────────────────────────────────────────────────────┤
│  STATUS LABELS                                                   │
│  • severity: warning                                             │
│  • status_badge: ⚠️ WARNINGS                                    │
├─────────────────────────────────────────────────────────────────┤
│  ATTACHMENTS                                                     │
│  ├─ [SA #1] Check User Name (screenshot)         [🖼️ PNG]      │
│  ├─ [SA #2] Verify Email (screenshot)            [🖼️ PNG]      │
│  ├─ Soft Assertion Failure #1 (text)             [📝 TEXT]     │
│  ├─ Soft Assertion Failure #2 (text)             [📝 TEXT]     │
│  ├─ ⚠️ Soft Assertions Summary Report (HTML)    [🌐 HTML]     │
│  └─ ⚠️ Soft Assertions Warning Summary (text)   [📝 TEXT]     │
└─────────────────────────────────────────────────────────────────┘


HTML SUMMARY TABLE STRUCTURE:

┌──────────────────────────────────────────────────────────────────┐
│            ⚠️ Soft Assertions Summary Report                     │
├──────────────────────────────────────────────────────────────────┤
│  Total Failures: 3                                               │
│  Report Generated: 2024-01-15 14:30:45                          │
│  Status: ⚠️ WARNING (Test PASSED with warnings)                │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  #  | Step Name        | Message           | Expected vs Actual│
│  ---|------------------|-------------------|-------------------|
│  1  | Verify Name      | Name mismatch     | John vs Jane      │
│  2  | Verify Email     | Email invalid     | john@... vs null  │
│  3  | Check Status     | Status not active | active vs pending │
│                                                                  │
│  For each failure, shows:                                       │
│  ✓ Expected: [value]                                           │
│  ✗ Actual: [value]                                             │
│                                                                  │
│  If JSON objects compared:                                      │
│  Expected JSON:                                                 │
│  {                                                               │
│    "id": 1,                                                      │
│    "name": "John"                                                │
│  }                                                               │
│                                                                  │
│  Actual JSON:                                                    │
│  {                                                               │
│    "id": 2,                                                      │
│    "name": "Jane"                                                │
│  }                                                               │
└──────────────────────────────────────────────────────────────────┘


SCREENSHOT NAMING:
- "[SA #1] Check User Name" - Shows assertion number and what was checked
- Appears as individual attachment in Allure
- Click to view full page screenshot taken at failure moment
- Shows ACTUAL page state (what user saw when assertion failed)
"""

# ============================================================================
# 7. FEATURE COMPARISON
# ============================================================================

"""
                          OLD              NEW              BENEFIT
FEATURE                   SoftAssertions   Enhanced         
─────────────────────────────────────────────────────────────────────
Screenshots               ❌ None           ✅ Yes            See page state
                                                           at failure

HTML Summary              ❌ No             ✅ Yes            Visual summary
                                                           in Allure

Expected vs Actual        ❌ Logs only      ✅ HTML table     Easy comparison
                                                           
JSON Diff                 ❌ No             ✅ Yes            Understand
                                                           object diffs

Step Name Context         ❌ No             ✅ Yes            Know which step
                                                           failed

Immediate Capture         ❌ No             ✅ Yes            Works currently

Test Status               ❌ FAILED         ✅ PASSED         Doesn't block
                                           + ⚠️ badge       CI/CD

Allure Integration        ⚠️ Text only     ✅ Rich content   Professional
                                                           looking reports

Per-Assertion Visibility  ❌ In logs        ✅ Screenshots    Quick diagnosis


REAL-WORLD EXAMPLE:

Test: "Verify user profile update"

OLD (SoftAssertions):
    ⚠️ Test FAILED
    Had to: 
    1) Open Allure report
    2) Find test in results
    3) Search logs for assertion messages
    4) Manually compare expected vs actual
    5) Guess what page looked like at failure

NEW (EnhancedSoftAssertions):
    ✅ Test PASSED with ⚠️ WARNINGS
    1) Click test in results
    2) See yellow warning indicator
    3) Look at "⚠️ Soft Assertions Summary Report" tab
    4) See all failures in beautiful HTML table
    5) Click screenshot to see page state
    6) Check JSON diffs side-by-side
    7) Understand issue immediately
"""

# ============================================================================
# 8. PARALLEL EXECUTION SAFETY
# ============================================================================

"""
THREAD SAFETY:

✅ SAFE COMPONENTS:
- EnhancedSoftAssertions: Each test creates own instance
- SoftAssertionFailure: Immutable dataclass, no shared state
- HTML generation: Uses local failures list (not global)
- Page reference: Each test has own page (Playwright feature)

✅ PYTEST HOOKS (if using parallel pytest-xdist):
- pytest_runtest_makereport(): Uses report.nodeid (unique per test)
- No global state manipulation
- Each test's warning handled independently

✅ ALLURE ATTACHMENTS:
- Each attachment has unique name per test
- Allure handles parallel writes internally
- Safe for multiple workers


PARALLEL EXECUTION EXAMPLE:

Worker 1 (test_A):
    EnhancedSoftAssertions(page_A)
        ├─ Failures for test_A
        └─ HTML report for test_A
        
Worker 2 (test_B):
    EnhancedSoftAssertions(page_B)
        ├─ Failures for test_B
        └─ HTML report for test_B

Worker 3 (test_C):
    EnhancedSoftAssertions(page_C)
        ├─ Failures for test_C
        └─ HTML report for test_C

Each test isolated, no interference, all reports generated correctly
"""

# ============================================================================
# 9. PERFORMANCE CONSIDERATIONS
# ============================================================================

"""
SCREENSHOT CAPTURE PERFORMANCE:

Memory:
    - Per screenshot: 50-200 KB (typical PNG)
    - Per test with 3 failures: ~300-600 KB
    - In RAM: Not stored, immediately attached to Allure
    - No memory accumulation over test run

Time:
    - page.screenshot(): 50-100ms typical
    - Per assertion failure: +50-100ms
    - 3 failures per test: +150-300ms overhead
    - Negligible compared to test execution time

Storage:
    - Allure stores in ./allure-results/ folder
    - ~5-10 MB for 100 tests with 3 failures each
    - Clean up: rm -rf allure-results/ or use CI cleanup

OPTIMIZATION TIPS:
- Pass page=None to disable screenshots if not needed (edge cases)
- Only screenshot when failures expected (most scenarios do this)
- Allure caches images - no duplication even if similar screenshots
"""

# ============================================================================
# 10. MIGRATION CHECKLIST
# ============================================================================

"""
TO MIGRATE EXISTING TESTS:

☐ 1. Import new module:
      FROM: from utils.assertions import SoftAssertions
      TO:   from utils.soft_assertions_enhanced import EnhancedSoftAssertions

☐ 2. Create with page:
      FROM: with SoftAssertions() as soft:
      TO:   with EnhancedSoftAssertions(page) as soft:

☐ 3. Add step names (optional but recommended):
      FROM: soft.assert_equal(actual, expected, "message")
      TO:   soft.assert_equal(actual, expected, "message", step_name="Step Name")

☐ 4. Keep fixtures intact:
      - test_context (no changes needed)
      - page (already injected, just pass it)
      - conftest.py hooks (already added, automatic)

☐ 5. Update imports in all step files:
      grep -r "from utils.assertions import" tests/bdd/steps/
      Replace with: from utils.soft_assertions_enhanced import

☐ 6. Test locally:
      pytest tests/bdd/ --headed  # See screenshots being captured
      allure serve allure-results  # View HTML reports

☐ 7. Verify Allure output:
      ✅ Test shows PASSED with ⚠️ warning
      ✅ Screenshots attached
      ✅ HTML summary table visible
      ✅ Yellow/orange warning label visible


CHECKLIST FOR NEW TESTS:

☐ Always use EnhancedSoftAssertions with page reference
☐ Include step_name in each assertion for clarity
☐ Use with context manager (automatic __enter__ and __exit__)
☐ Don't mix hard assertions with soft assertions
☐ Test passes with warnings - that's the intended behavior
"""

# ============================================================================
# 11. TROUBLESHOOTING
# ============================================================================

"""
PROBLEM: Screenshots not appearing in Allure report
SOLUTIONS:
  1) Check that page is passed: EnhancedSoftAssertions(page)
  2) Verify page is valid: print(page.url) before creating soft assertions
  3) Check Allure results exist: ls allure-results/ | grep -i screenshot
  4) Try: allure clean && pytest && allure serve

PROBLEM: HTML summary not showing
SOLUTIONS:
  1) Ensure assertions actually failed (at least 1 failure)
  2) Check that context manager exited normally (no outer exception)
  3) Verify: allure report has attachment "⚠️ Soft Assertions Summary Report"
  4) Try: pytest -v to see if warnings were caught

PROBLEM: Test is still marked as FAILED in Allure
SOLUTIONS:
  1) Check report.when == "teardown" in pytest hook
  2) Verify SoftAssertionWarning is actually raised
  3) Ensure pytest_runtest_makereport hook is in conftest.py
  4) Check: pytest --collect-only | grep pytest_runtest_makereport

PROBLEM: Yellow warning label not visible
SOLUTIONS:
  1) Verify Allure is using latest version: allure --version
  2) Check hook added label: logger warnings for "Adding label: severity"
  3) Refresh Allure report: allure clean && allure serve
  4) Try hard refresh browser: Ctrl+Shift+R (Windows)

PROBLEM: Multiple soft assertion blocks producing duplicate HTML
SOLUTIONS:
  1) Each __exit__ generates HTML - that's expected
  2) Multiple contexts = multiple reports (intentional design)
  3) Each with block is independent report
  4) If cluttering report, merge into single with block

PROBLEM: Step name not appearing in HTML table
SOLUTIONS:
  1) Verify step_name parameter passed: soft.assert_equal(..., step_name="Name")
  2) Check HTML template includes: {data['step_name']}
  3) See "N/A" if step_name not provided (this is OK)
  4) Add step_name to assertion for better reporting
"""

# ============================================================================
# 12. BEST PRACTICES
# ============================================================================

"""
✅ DO:
- Pass page parameter to enable screenshots
- Use step_name for context (e.g., "Verify User Name")
- Include descriptive messages in assertions
- Group related assertions in single with block
- Check soft.has_failures() after block for additional logging
- Use assert_in/assert_not_in for container checks
- Let test PASS with warning (that's the design)

❌ DON'T:
- Mix hard assert and soft assert in same step
- Forget to pass page (screenshots won't work)
- Use empty messages (make them descriptive)
- Create multiple soft assertion blocks unnecessarily
- Try to fail the test manually (let soft assertions handle it)
- Use soft assertions for critical path (only for non-blocking checks)
- Expect test to FAIL (it stays PASSED + warning)

🚀 PERFORMANCE:
- Soft assertions add ~150-300ms per test (negligible)
- Screenshots use minimal memory
- Parallel execution fully supported
- No cleanup needed (automatic)

📊 REPORTING:
- All information visible in Allure (no log reading needed)
- HTML summary is scan-friendly (2-3 seconds to understand issue)
- Screenshots show actual page state
- JSON diffs make complex comparisons clear
"""

# ============================================================================
# 13. EXAMPLE OUTPUT IN ALLURE
# ============================================================================

"""
ALLURE DASHBOARD:
┌────────────────────────────────────────────────────────────────┐
│ Test Results                                        Duration    │
│ ✅ PASSED 847                                                   │
│ ⚠️ PASSED WITH WARNINGS 23                                     │
│ ❌ FAILED 5                                                     │
│                                                                 │
│ Easy to find problem tests - filter by "PASSED WITH WARNINGS" │
└────────────────────────────────────────────────────────────────┘

TEST DETAIL VIEW:
┌────────────────────────────────────────────────────────────────┐
│ test_user_profile_update          ✅ PASSED ⚠️ WARNING         │
├────────────────────────────────────────────────────────────────┤
│ SEVERITY: warning                                               │
│ STATUS: ⚠️ WARNINGS                                            │
├────────────────────────────────────────────────────────────────┤
│ ATTACHMENTS:                                                    │
│ ├─ [SA #1] Check User Name (screenshot.png)     [View]        │
│ ├─ [SA #2] Verify Email (screenshot.png)        [View]        │
│ ├─ ⚠️ Soft Assertions Summary Report            [View]        │
│ │   • #1: Name is "John" not "Jane"                            │
│ │   • #2: Email is null not "john@example.com"                │
│ └─ ⚠️ Soft Assertions Warning Summary           [View]        │
│                                                                 │
│ DESCRIPTION:                                                    │
│ Steps executed successfully                                     │
│ 2 soft assertion failures detected                             │
│ See HTML summary for details                                   │
└────────────────────────────────────────────────────────────────┘

HTML SUMMARY DISPLAY:
┌────────────────────────────────────────────────────────────────┐
│            ⚠️ Soft Assertions Summary Report                  │
├────────────────────────────────────────────────────────────────┤
│ Total Failures: 2                                               │
│ Report Generated: 2024-01-15 14:30:45                          │
│ Status: ⚠️ WARNING (Test PASSED with warnings)                │
│                                                                 │
│ #  Step Name      Message              Expected   Actual       │
│ 1  Verify Name    Name mismatch        John       Jane         │
│ 2  Check Email    Email required       john@...   (null)       │
│                                                                 │
│ For each: Shows full Expected vs Actual with timestamps       │
└────────────────────────────────────────────────────────────────┘
"""

# ============================================================================
# END OF ARCHITECTURE GUIDE
# ============================================================================
