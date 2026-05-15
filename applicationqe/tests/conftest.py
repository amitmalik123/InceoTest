"""
Global Test Configuration

This conftest.py contains:
- Global pytest hooks (configure, collection, execution, reporting)
- Global test infrastructure
- BDD-specific fixtures and hooks (merged from tests/bdd/conftest.py)

Fixture Organization:
- Page object fixtures: tests/fixtures/page_fixtures.py
- Test data fixtures: tests/fixtures/data_fixtures.py
- Database fixtures: tests/fixtures/db_fixtures.py
- Authentication fixtures: tests/fixtures/auth_fixtures.py
- Browser fixtures: tests/fixtures/browser_fixtures.py
- BDD hooks: tests/fixtures/hooks_fixtures.py
- Assertion utilities: tests/fixtures/assertion_fixtures.py

BDD Fixtures:
- test_data: Selects test data based on scenario name from CSV
- test_context: Context to store test data and state across BDD steps
- pytest_runtest_logreport: Logs D_Numbers for BDD scenarios
- pytest_sessionfinish (bdd): Cleanup after BDD test session
- pytest_runtest_makereport (bdd): Handles soft assertion warnings in BDD tests
"""

import os
import subprocess
from collections.abc import Generator
from pathlib import Path

import allure
import pytest

from config.oam.settings import get_settings

# Import all fixtures to make them available to all tests
from fixtures import *  # noqa: F401, F403
from utils.allure_logger import enable_step_screenshots, get_allure_logger
from utils.flaky_test_tracker import get_tracker

logger = get_allure_logger(__name__)


# ==================================================================================
# BDD-SPECIFIC FIXTURES (Merged from tests/bdd/conftest.py)
# ==================================================================================

# Store test_context instances at module level to ensure persistence across steps in BDD scenarios
_test_context_cache = {}

# Store D_Numbers per test_node_id for parallel-safe logging (keyed by test_node_id)
# This is safe for parallel execution because each test has a unique node_id
_test_d_numbers = {}


@pytest.fixture
def test_data(test_data_manager, request) -> dict:
    """
    Select test data based on scenario name matching CSV 'scenario' column.

    Each scenario gets its own data row by matching scenario name exactly.
    This runs BEFORE login, so each scenario uses correct credentials.

    CSV Format:
        scenario,role,username,password,...
        Successfully login and navigate to Account List,non-ira,user1,...
        Successfully complete Add ACH flow,ira,user2,...

    Args:
        test_data_manager: Session-scoped test data manager
        request: Pytest request object with scenario info

    Returns:
        dict: Test data row for this scenario
    """
    # Get actual scenario name from pytest-bdd scenario object
    scenario_name = None

    # pytest-bdd stores the scenario in the test function
    if (
        hasattr(request, "node")
        and hasattr(request.node, "obj")
        and hasattr(request.node.obj, "__scenario__")
    ):
        scenario_name = request.node.obj.__scenario__.name

    # Fallback: extract from test name
    if not scenario_name:
        scenario_name = request.node.name.replace("test_", "").replace("_", " ").title()

    print(f"\n{'=' * 60}")
    print(f"[TEST DATA] Scenario: '{scenario_name}'")

    # Try to find matching data by scenario name
    data = test_data_manager.get_by(scenario=scenario_name)

    if data:
        print("[TEST DATA] MATCHED in CSV!")
        print(f"[TEST DATA] Role: {data.get('role')}")
        print(f"[TEST DATA] Username: {data.get('username')}")
        print(f"[TEST DATA] Client ID: {data.get('client_id')}")
        print(f"[TEST DATA] Account Number: {data.get('account_number')}")
        print(f"{'=' * 60}")
        return data
    else:
        print("[TEST DATA] ❌ NOT FOUND - No exact match in CSV")
        print(f"[TEST DATA] Scenario name: '{scenario_name}'")
        print(f"[TEST DATA] Available scenarios in CSV:")
        available = test_data_manager.get_scenarios()
        for i, scenario in enumerate(available, 1):
            print(f"  {i:2d}. '{scenario}'")
        print(f"{'=' * 60}")

        # IMPORTANT: Do NOT fall back to first row - that causes silent failures!
        # Better to fail early with clear error than to use wrong credentials
        raise ValueError(
            f"❌ TEST DATA MISMATCH\n"
            f"Scenario '{scenario_name}' not found in test data CSV.\n"
            f"This will cause authentication to fail with wrong credentials.\n\n"
            f"SOLUTIONS:\n"
            f"1. Add a row to data/oam/test_data.test11.csv with scenario name: '{scenario_name}'\n"
            f"2. Remove/skip the scenario from OAM.feature\n"
            f"3. Rename scenario in .feature file to match an existing CSV row\n\n"
            f"Available scenarios in CSV:\n"
            + "\n".join(f"  - '{s}'" for s in available)
        )


@pytest.fixture
def test_context(test_data, request) -> dict:
    """
    Context to store test data and state across BDD steps.

    IMPORTANT: This fixture MUST persist across ALL steps in a single BDD scenario.
    Without this, steps cannot share data (e.g., database query results).

    Solution: Cache instances by test node ID so all steps in same scenario share context.

    Args:
        test_data: Injected from test_data fixture (filtered by scenario name)
        request: Pytest request object with node info

    Returns:
        dict: Context with test_data accessible via test_context["test_data"]
              and allows steps to store/retrieve shared state via test_context dict
    """
    # Use test node ID as cache key so all steps in same scenario share context
    test_node_id = request.node.nodeid

    # Create context only once per test, reuse for all steps
    if test_node_id not in _test_context_cache:
        print(f"\n[TEST CONTEXT] Creating new context for: {test_node_id}")
        _test_context_cache[test_node_id] = {"test_data": test_data}
    else:
        print(f"\n[TEST CONTEXT] Reusing existing context for: {test_node_id}")

    context = _test_context_cache[test_node_id]

    # Log current state
    print(f"[TEST CONTEXT] Available keys: {list(context.keys())}")
    for key in context.keys():
        if key != "test_data":  # Don't log large test_data dict
            value = context[key]
            if isinstance(value, list) and len(value) > 0:
                print(f"  - {key}: {len(value)} item(s)")
            else:
                print(f"  - {key}: {value}")

    yield context

    # Cleanup after test completes - LOG D_NUMBER BEFORE CLEANUP
    if test_node_id in _test_context_cache:
        # Extract D_Number before deleting context
        d_number = context.get("d_number", "N/A")

        # Store D_Number in per-test dictionary (thread-safe for parallel execution)
        _test_d_numbers[test_node_id] = d_number

        logger.info(f"\n{'=' * 60}")
        logger.info(f"D_Number generated - {d_number}")
        logger.info(f"{'=' * 60}")

        # Also print to stdout so it's definitely visible
        print(f"\n{'=' * 60}")
        print(f"D_Number generated - {d_number}")
        print(f"{'=' * 60}\n")

        logger.info(f"[TEST CONTEXT] Cleanup: Removing context for {test_node_id}")
        del _test_context_cache[test_node_id]


def pytest_runtest_logreport(report):
    """
    Hook that runs after each test result is logged.
    Logs the D_Number that was generated/used in the test.
    This is PARALLEL-SAFE because it uses test_node_id as the key.

    This hook works with parallel execution (pytest-xdist):
    - Each test has a unique test_node_id
    - D_Numbers are stored in _test_d_numbers dict keyed by test_node_id
    - Multiple workers can run simultaneously without interference
    """
    # Log when test is done (after all steps, after teardown)
    if report.when == "teardown":
        try:
            # Get test node ID - this is unique per test even in parallel execution
            test_node_id = report.nodeid

            # Look up D_Number from the per-test dictionary
            if test_node_id in _test_d_numbers:
                d_number = _test_d_numbers[test_node_id]

                logger.critical(f"D_Number generated - {d_number}")

                # Also print to ensure it's captured
                print(f"\n{'=' * 70}")
                print(f"D_Number generated - {d_number}")
                print(f"{'=' * 70}\n")

                # Clean up this test's entry
                del _test_d_numbers[test_node_id]
        except Exception as e:
            # Don't fail if logging fails
            logger.warning(f"Error logging D_Number in hook: {e}")


def _pytest_sessionfinish_bdd(session):
    """
    Hook that runs at the end of the entire test session.
    Cleans up any remaining D_Numbers from _test_d_numbers dict.
    This is a safety cleanup in case some tests crashed before reporting.
    """
    global _test_d_numbers
    if _test_d_numbers:
        logger.info(f"Session cleanup: Removing {len(_test_d_numbers)} leftover D_Number entries")
        _test_d_numbers.clear()


def _pytest_runtest_makereport_bdd(item, call):
    """
    Hook that processes test results and handles soft assertion warnings.

    Safety net: If SoftAssertionWarning somehow gets raised, catch it and
    keep the test PASSED. Normally assert_all() and __exit__ don't raise,
    but this handles edge cases where raise_with_warning() is called directly.
    """
    from utils.soft_assertions_enhanced import SoftAssertionWarning

    # Only process during the test call phase (when test code runs)
    if call.when == "call":
        if call.excinfo and isinstance(call.excinfo.value, SoftAssertionWarning):
            logger.warning(f"Test {item.nodeid} has soft assertion warnings - keeping as PASSED")

            allure.dynamic.severity(allure.severity_level.MINOR)
            allure.dynamic.tag("⚠️ SOFT_ASSERTION_WARNING")

            # Suppress the exception so test doesn't fail
            call.excinfo = None


# ==================================================================================
# END BDD-SPECIFIC FIXTURES
# ==================================================================================


# Pytest configuration hooks
def pytest_addoption(parser) -> None:
    """Add custom command-line options"""
    parser.addoption(
        "--screenshot-each-step",
        action="store_true",
        default=False,
        help="Take screenshot after each BDD step (can be slow, use for debugging)",
    )


def pytest_configure(config) -> None:
    """Register custom markers and configure retry behavior"""
    # Application and environment markers
    config.addinivalue_line("markers", "env(name): mark test to run only on specific environment")
    config.addinivalue_line("markers", "app(name): mark test to run with specific application (default: ewm)")
    
    # Environment-specific markers
    config.addinivalue_line("markers", "test11: mark test to run only on test11 environment")
    config.addinivalue_line("markers", "test12: mark test to run only on test12 environment")
    config.addinivalue_line("markers", "silo: mark test to run only on silo environment")
    config.addinivalue_line("markers", "prod: mark test to run only on prod environment")
    
    # Test category markers
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
    config.addinivalue_line("markers", "FNT_regression: mark test as FNT regression test")
    config.addinivalue_line("markers", "HappyPath: mark test as happy path test")
    config.addinivalue_line("markers", "slow: mark test as slow")
    
    # Scenario/Test case markers (S1-S11)
    for i in range(1, 12):
        config.addinivalue_line("markers", f"S{i}: mark test as scenario S{i}")
    
    # Regression markers
    config.addinivalue_line("markers", "T10_Regression: mark test as T10 regression")
    config.addinivalue_line("markers", "Silo_Regression: mark test as Silo regression")
    config.addinivalue_line("markers", "Prod_Regression: mark test as Prod regression")
    
    # Execution control markers
    config.addinivalue_line("markers", "serial: mark test to run serially (not in parallel)")
    config.addinivalue_line("markers", "xdist_group(name): mark test with xdist group for parallel execution")

    # Configure step screenshots - Priority: CLI > ENV VAR > CONFIG FILE
    settings_instance = get_settings()
    screenshot_each_step = (
        config.getoption("--screenshot-each-step", default=False)
        or os.getenv("SCREENSHOT_EACH_STEP", "").lower() in ("true", "1", "yes", "on")
        or settings_instance.screenshot_each_step
    )
    enable_step_screenshots(screenshot_each_step)

    # Print screenshot configuration
    status = "ENABLED for ALL steps" if screenshot_each_step else "ENABLED on failure only"
    print(f"\n{'=' * 60}")
    print(f"Step Screenshots: {status}")
    print(f"{'=' * 60}")

    # Enable automatic reruns for flaky test detection
    # This can be overridden with --reruns CLI argument
    # Skip reruns if --pdb is enabled (debug mode)
    if not config.option.reruns and not config.option.usepdb:
        config.option.reruns = 1  # Retry failed tests up to 1 time
        config.option.reruns_delay = 1  # 1 second delay between retries


def pytest_sessionstart(session) -> None:
    """
    Hook that runs before test session starts.
    Clears old Allure results, videos, and traces to ensure fresh artifacts for each run.
    """
    import shutil

    report_dir = "reports"
    
    dirs_to_clean = [
        f"{report_dir}/allure-results",
        f"{report_dir}/videos",
        f"{report_dir}/traces",
        f"{report_dir}/downloads",
    ]

    files_to_clean = [
        f"{report_dir}/network_errors.log",  # Matches http_error_log in pyproject.toml
    ]

    for dir_path in dirs_to_clean:
        if os.path.exists(dir_path):
            try:
                for item in os.listdir(dir_path):
                    item_path = os.path.join(dir_path, item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                print(f"\nCleared old artifacts from {dir_path}")
            except Exception as e:
                print(f"\nWarning: Failed to clear {dir_path}: {e}")
        else:
            os.makedirs(dir_path, exist_ok=True)
            print(f"\nCreated directory: {dir_path}")

    for file_path in files_to_clean:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"\nCleared old log: {file_path}")
            except Exception as e:
                print(f"\nWarning: Failed to clear {file_path}: {e}")


def pytest_collection_modifyitems(config, items) -> None:  # noqa: C901
    """
    Consolidated hook for test collection modification.

    Handles:
    - Environment markers
    - Retry tracking initialization
    - Parallel execution (xdist) grouping
    - Slow test detection
    """
    current_env = get_settings().env
    available_apps = set(get_settings().get_available_apps())

    for item in items:
        # 1. Initialize retry tracking for flaky test detection
        item.execution_count = 0
        item.failed_count = 0
        item.start_time = None

        # 1b. Auto-map feature file tags to @pytest.mark.app()
        # If a scenario is tagged @crm, @ewm, etc. and that tag matches
        # a configured app name, add the app marker automatically.
        if not item.get_closest_marker("app"):
            for mark in item.iter_markers():
                if mark.name in available_apps:
                    item.add_marker(pytest.mark.app(mark.name))
                    break

        # 2. Add environment markers
        if current_env == "test11":
            item.add_marker(pytest.mark.test11)
        elif current_env == "test12":
            item.add_marker(pytest.mark.test12)
        elif current_env == "silo":
            item.add_marker(pytest.mark.silo)
        elif current_env == "prod":
            item.add_marker(pytest.mark.prod)

        # 3. Auto-assign xdist groups for parallel execution
        # Skip if test is marked as serial (must run alone)
        if "serial" not in [mark.name for mark in item.iter_markers()]:
            # Determine group based on test characteristics
            test_name = item.nodeid.lower()

            if "login" in test_name or "auth" in test_name:
                group = "auth"
            elif "api" in test_name:
                group = "api"
            elif "ui" in test_name:
                group = "ui"
            elif "database" in test_name or "db" in test_name:
                group = "database"
            else:
                group = "default"

            # Add xdist_group marker if not already present
            if not any(mark.name == "xdist_group" for mark in item.iter_markers()):
                item.add_marker(pytest.mark.xdist_group(group))

        # 4. Mark slow tests (parametrized tests with many parameters)
        if hasattr(item, "callspec") and item.callspec and len(item.callspec.params) > 5:
            item.add_marker(pytest.mark.slow)


def pytest_runtest_setup(item) -> None:
    """Called before each test execution (including retries)"""
    from datetime import datetime

    item.execution_count += 1
    item.start_time = datetime.now()


# Pytest hooks for screenshot on failure and flaky test detection
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call) -> Generator:
    """
    Pytest hook to:
    1. Capture screenshot on test failure (Allure report)
    2. Detect flaky tests by tracking retries and failures
    """
    # Flaky test detection logic (BEFORE yielding to other hooks)
    if call.when == "call":  # Only track the actual test execution
        from datetime import datetime

        duration_ms = 0
        if hasattr(item, "start_time") and item.start_time:
            duration_ms = int((datetime.now() - item.start_time).total_seconds() * 1000)

        # Track failed attempts
        if call.excinfo is not None:
            item.failed_count += 1

        # Detect flaky test: passed after one or more failures
        if call.excinfo is None and item.execution_count > 1 and item.failed_count > 0:
            # This test is flaky - it failed at least once but eventually passed
            tracker = get_tracker()

            error_msg = ""
            if hasattr(call, "excinfo") and call.excinfo:
                error_msg = str(call.excinfo.value)

            tracker.record_flaky_test(
                test_name=item.nodeid,
                test_id=item.nodeid,
                total_attempts=item.execution_count,
                failed_attempts=item.failed_count,
                final_status="passed",
                duration_ms=duration_ms,
                error_message=error_msg,
            )

    # Screenshot capture logic
    outcome = yield
    rep = outcome.get_result()

    # BDD soft assertion check: suppress SoftAssertionWarning to keep test as PASSED
    if rep.when == "call" and rep.failed:
        if hasattr(rep, "excinfo") and rep.excinfo and hasattr(rep.excinfo, "value"):
            from utils.soft_assertions_enhanced import SoftAssertionWarning

            if isinstance(rep.excinfo.value, SoftAssertionWarning):
                logger.warning(f"Test {item.nodeid} has soft assertion warnings - keeping as PASSED")
                allure.dynamic.severity(allure.severity_level.MINOR)
                allure.dynamic.tag("⚠️ SOFT_ASSERTION_WARNING")
                # Suppress the exception by clearing the failed status
                rep.failed = False

    # Store report on node so fixtures can check pass/fail status (used by _stop_tracing)
    setattr(item, f"rep_{rep.when}", rep)

    # Only take screenshot on failure or error (including setup failures)
    if rep.failed and rep.when in ("call", "setup") and "authenticated_page" in item.funcargs:
        page = item.funcargs["authenticated_page"]
        try:
            # Take screenshot and attach to Allure
            screenshot_bytes = page.screenshot()
            allure.attach(
                screenshot_bytes,
                name=f"screenshot-{item.name}",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception as e:
            print(f"Failed to capture screenshot: {e}")


def pytest_sessionfinish(session, exitstatus) -> None:  # noqa: C901
    """
    Hook that runs after all tests complete.
    Automatically generates Allure HTML report from JSON results
    and pushes flaky test metrics to InfluxDB.
    Also generates auto-healing report.
    """
    import json
    import platform
    import shutil
    from datetime import datetime

    # Generate Auto-Healing Report
    try:
        from pages.oam.base_page import BasePage

        healing_engine = BasePage._healing_engine
        if healing_engine:
            stats = healing_engine.get_stats()

            # Prepare detailed healing report
            healing_report = {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_healing_attempts": stats.get("total_heals", 0),
                    "successful_heals": stats.get("successful_heals", 0),
                    "failed_heals": stats.get("failed_heals", 0),
                    "success_rate": f"{stats.get('success_rate', 0) * 100:.2f}%",
                    "stored_alternatives": stats.get("stored_alternatives", 0),
                },
                "healed_locators": [],
            }

            # Add details of all healed locators
            for key, locator_data in healing_engine.locator_storage.items():
                healing_report["healed_locators"].append(
                    {
                        "hash_key": key,
                        "original_selector": locator_data.get("original", "N/A"),
                        "healed_selector": locator_data.get("selector", "N/A"),
                        "strategy_used": locator_data.get("strategy", "N/A"),
                        "success_count": locator_data.get("success_count", 0),
                        "timestamp": datetime.fromtimestamp(
                            locator_data.get("timestamp", 0)
                        ).isoformat(),
                    }
                )

            # Save to reports directory
            reports_dir = Path("reports")
            reports_dir.mkdir(exist_ok=True)

            healing_report_path = reports_dir / "auto_healing_report.json"
            with open(healing_report_path, "w") as f:
                json.dump(healing_report, f, indent=2)

            # Print summary to console
            if stats.get("total_heals", 0) > 0:
                print(f"\n{'=' * 60}")
                print("AUTO-HEALING SUMMARY")
                print(f"{'=' * 60}")
                print(f"Total Healing Attempts: {stats['total_heals']}")
                print(f"Successful Heals: {stats['successful_heals']}")
                print(f"Failed Heals: {stats['failed_heals']}")
                print(f"Success Rate: {stats['success_rate'] * 100:.2f}%")
                print(f"Stored Alternatives: {stats['stored_alternatives']}")
                print(f"\nDetailed Report: {healing_report_path.absolute()}")
                print(f"{'=' * 60}\n")
            else:
                print("\nOK: No auto-healing attempts in this session\n")
    except Exception as e:
        print(f"\nWARNING: Failed to generate auto-healing report: {e}\n")

    # Push flaky test metrics to InfluxDB
    try:
        tracker = get_tracker()
        summary = tracker.get_flaky_summary()

        if summary["total_flaky_tests"] > 0:
            print(f"\n{'=' * 60}")
            print("WARNING: FLAKY TEST SUMMARY")
            print(f"{'=' * 60}")
            print(f"Total Flaky Tests: {summary['total_flaky_tests']}")
            for test in summary["flaky_tests"]:
                print(
                    f"  - {test['name']}: {test['failed']}/{test['attempts']} failures → {test['status']}"
                )
            print(f"{'=' * 60}\n")

            # Push to InfluxDB
            tracker.push_to_influxdb()
        else:
            print("\nOK: No flaky tests detected in this session\n")
    except Exception as e:
        print(f"\nWARNING: Failed to track flaky tests: {e}\n")

    allure_results_dir = "reports/allure-results"
    allure_report_dir = "reports/allure-report"

    # Only generate report if results directory exists and has files
    if not os.path.exists(allure_results_dir):
        print(f"\nWarning: Allure results directory not found: {allure_results_dir}")
        return

    # Check if there are any result files
    result_files = [f for f in os.listdir(allure_results_dir) if f.endswith("-result.json")]
    if not result_files:
        print(f"\nWarning: No Allure result files found in {allure_results_dir}")
        return

    print(f"\nGenerating Allure HTML report from {len(result_files)} test results...")

    try:
        # Use shell=True on Windows to find allure in PATH
        is_windows = platform.system() == "Windows"

        # Generate Allure HTML report with --single-file for direct browser opening
        result = subprocess.run(
            [
                "allure",
                "generate",
                allure_results_dir,
                "--clean",
                "--single-file",
                "-o",
                allure_report_dir,
            ],
            capture_output=True,
            text=True,
            timeout=60,
            shell=is_windows,  # Required on Windows to find commands in PATH
        )

        if result.returncode == 0:
            import glob

            report_path = os.path.abspath(allure_report_dir)
            index_path = os.path.join(report_path, "index.html")

            # Create timestamped copy of the report
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            timestamped_index = os.path.join(report_path, f"index_{timestamp}.html")

            try:
                shutil.copy2(index_path, timestamped_index)

                # Clean up old timestamped reports (keep last 10)
                try:
                    timestamped_files = sorted(
                        glob.glob(os.path.join(report_path, "index_*.html")),
                        key=os.path.getmtime,
                        reverse=True,  # Newest first
                    )
                    # Keep only the last 10
                    files_to_remove = timestamped_files[10:]
                    for old_file in files_to_remove:
                        os.remove(old_file)
                        print(f"   Cleaned up old report: {os.path.basename(old_file)}")
                except Exception:
                    # Non-critical error, just skip
                    pass

                print("Allure report generated successfully!")
                print(f"Report location: {report_path}")
                print(f"Main report: file:///{index_path.replace(os.sep, '/')}")
                print(f"Timestamped: file:///{timestamped_index.replace(os.sep, '/')}")

                # Show count of historical reports
                timestamped_files = glob.glob(os.path.join(report_path, "index_*.html"))
                timestamped_count = len(timestamped_files)
                if timestamped_count > 1:
                    print(f"Historical reports: {timestamped_count} available (keeping last 10)")

                print("\nAlternative commands:")
                print(f"   allure open {allure_report_dir}")
                print(f"   allure serve {allure_results_dir}")
            except Exception as e:
                print("Allure report generated successfully!")
                print(f"Report location: {report_path}")
                print(f"Open in browser: file:///{index_path.replace(os.sep, '/')}")
                print(f"Warning: Failed to create timestamped copy: {e}")
        else:
            print("Warning: Allure report generation failed:")
            print(f"   {result.stderr}")
    except FileNotFoundError:
        print("\nWarning: Allure CLI not found. Install it with:")
        print("   npm install -g allure-commandline")
        print("   or download from: https://github.com/allure-framework/allure2/releases")
    except subprocess.TimeoutExpired:
        print("\nWarning: Allure report generation timed out (>60s)")
    except Exception as e:
        print(f"\nWarning: Error generating Allure report: {e}")

    # Auto-push test execution metrics to InfluxDB (controlled by config toggle)
    try:
        from utils.influx_reporter import AllureToInfluxDB

        reporter = AllureToInfluxDB()
        if reporter.auto_push:
            reporter.allure_results_dir = allure_results_dir
            reporter.run()
        else:
            print("\nInfluxDB auto-push disabled (set 'auto_push': true in influxdb_config.json to enable)")
    except Exception as e:
        print(f"\nWARNING: Failed to push metrics to InfluxDB: {e}")

    # BDD cleanup: Clear any remaining D_Numbers from test cache
    _pytest_sessionfinish_bdd(session)
