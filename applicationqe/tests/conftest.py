"""
Global Test Configuration

This conftest.py contains:
- Generic pytest hooks (configure, collection, execution, reporting)
- Global test infrastructure
- BDD-specific fixtures are imported from tests/fixtures/hooks_fixtures.py

Fixture Organization:
- Page object fixtures: tests/fixtures/page_fixtures.py
- Test data fixtures: tests/fixtures/data_fixtures.py
- Database fixtures: tests/fixtures/db_fixtures.py
- Authentication fixtures: tests/fixtures/auth_fixtures.py
- Browser fixtures: tests/fixtures/browser_fixtures.py
- BDD hooks: tests/fixtures/hooks_fixtures.py
- Assertion utilities: tests/fixtures/assertion_fixtures.py

BDD Fixtures (imported from hooks_fixtures):
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

from config.settings import get_settings

# Import all fixtures to make them available to all tests
from fixtures import *  # noqa: F401, F403
# Import BDD-specific fixtures from hooks module
from tests.fixtures.hooks_fixtures import *  # noqa: F401, F403

from utils.allure_logger import enable_step_screenshots
from utils.flaky_test_tracker import get_tracker



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

    report_dir = "reports/oam"
    
    dirs_to_clean = [
        f"{report_dir}/allure-results",
        f"{report_dir}/allure-report",
        f"{report_dir}/videos",
        f"{report_dir}/traces",
        f"{report_dir}/screenshots",
        f"{report_dir}/debug_screenshots",
        f"{report_dir}/downloads",
        f"{report_dir}/junit",
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
                print(f"Test {item.nodeid} has soft assertion warnings - keeping as PASSED")
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
            reports_dir = Path("reports/oam")
            reports_dir.mkdir(parents=True, exist_ok=True)

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
        elif current_env == "silo":
            item.add_marker(pytest.mark.silo)
        elif current_env == "prod":
            item.add_marker(pytest.mark.prod)

        # 3. Auto-assign xdist groups for parallel execution
        # Skip if test is marked as serial (must run alone)
        if "serial" not in [mark.name for mark in item.iter_markers()]:
            # Determine group based on test characteristics
            test_name = item.nodeid.lower()

            if "api" in test_name:
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

    # Collect data for Excel report (only on the final call phase outcome)
    if rep.when == "call":
        excel_report.collect_result_from_item(item, rep)

    # In xdist workers, serialize collected results to per-worker file for merge
    if rep.when == "call" and os.environ.get("PYTEST_XDIST_WORKER"):
        _flush_worker_results()
        _flush_worker_flaky_data()


def _flush_worker_results() -> None:
    """Write current worker's collected Excel results to a per-worker JSON file."""
    import json

    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")
    worker_file = Path(f"reports/excel_results_{worker_id}.json")
    worker_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        results = excel_report.test_results
        if results:
            with open(worker_file, "w", encoding="utf-8") as f:
                json.dump(results, f, default=str)
    except Exception:
        pass


def _flush_worker_flaky_data() -> None:
    """Write current worker's flaky test data to a per-worker JSON file."""
    import json

    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")
    tracker = get_tracker()
    if not tracker.flaky_tests:
        return
    worker_file = Path(f"reports/flaky_results_{worker_id}.json")
    worker_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(worker_file, "w", encoding="utf-8") as f:
            json.dump(tracker.flaky_tests, f, default=str)
    except Exception:
        pass


def _merge_worker_files() -> None:
    """Merge worker-isolated log/data files into canonical files after parallel runs.

    Each worker writes to ``<name>_gw0.log``, ``<name>_gw1.log``, etc.
    This function appends all worker fragments into the canonical file
    and removes the fragments. Called once by the controller in ``pytest_sessionfinish``.
    """
    import glob as _glob

    merge_specs = [
        # (canonical_path, glob_pattern)
        ("reports/network_errors.log", "reports/network_errors_*.log"),
        ("reports/http_errors.log", "reports/http_errors_*.log"),
    ]

    for canonical, pattern in merge_specs:
        worker_files = sorted(_glob.glob(pattern))
        if not worker_files:
            continue

        canonical_path = Path(canonical)
        canonical_path.parent.mkdir(parents=True, exist_ok=True)
        with open(canonical_path, "a", encoding="utf-8") as out:
            for wf in worker_files:
                try:
                    with open(wf, "r", encoding="utf-8") as inp:
                        out.write(inp.read())
                    os.remove(wf)
                except Exception as e:
                    print(f"Warning: Failed to merge {wf}: {e}")


def _merge_worker_excel_results() -> None:
    """Merge per-worker Excel result JSON files into the controller's excel_report."""
    import glob as _glob
    import json

    worker_files = sorted(_glob.glob("reports/excel_results_*.json"))
    for wf in worker_files:
        try:
            with open(wf, "r", encoding="utf-8") as f:
                results = json.load(f)
            if results:
                excel_report.test_results.extend(results)
            os.remove(wf)
        except Exception as e:
            print(f"Warning: Failed to merge Excel results from {wf}: {e}")


def _merge_worker_flaky_results() -> None:
    """Merge per-worker flaky test JSON files into the controller's tracker."""
    import glob as _glob
    import json

    tracker = get_tracker()
    worker_files = sorted(_glob.glob("reports/flaky_results_*.json"))
    for wf in worker_files:
        try:
            with open(wf, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data:
                tracker.flaky_tests.update(data)
            os.remove(wf)
        except Exception as e:
            print(f"Warning: Failed to merge flaky results from {wf}: {e}")


def pytest_sessionfinish(session, exitstatus) -> None:  # noqa: C901
    """
    Hook that runs after all tests complete.
    Automatically generates Allure HTML report from JSON results.
    Also generates auto-healing report and flaky test summary.
    Only runs on the controller (or single-process run) — workers skip it.
    """
    # In xdist, workers skip report generation to avoid racing/duplicates
    if hasattr(session.config, "workerinput"):
        return

    # Merge worker-isolated files (xdist parallel support)
    _merge_worker_files()
    _merge_worker_excel_results()
    _merge_worker_flaky_results()

    import json
    import platform
    import shutil
    from datetime import datetime

    # Generate Excel Report
    try:
        report_path = excel_report.generate_excel_report()
        if report_path:
            print(f"Excel Report: {report_path.absolute()}")
    except Exception as e:
        print(f"\nWARNING: Failed to generate Excel report: {e}\n")

    # Generate Auto-Healing Report
    try:
        from pages.base_page import BasePage

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

    # Flaky test summary
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




# ─── BDD Fixtures (merged from tests/bdd/conftest.py) ───────────────────────

@pytest.fixture
def test_context(test_data_manager, _pytest_bdd_example):
    """
    Context to store test data and state across BDD steps.

    Dynamically fetches the correct test data row based on SheetName and RowNumber
    from the scenario's Examples table.
    """
    context = {}

    # Get SheetName and RowNumber from the current scenario's Examples
    sheet_name = _pytest_bdd_example.get("SheetName", "")
    row_number = int(_pytest_bdd_example.get("RowNumber", 0))

    if sheet_name and row_number > 0:
        # Use TestDataManager's get_row_by_number() method
        context["test_data"] = test_data_manager.get_row_by_number(sheet_name, row_number)
    else:
        # Fallback: return first row if no Examples specified
        all_data = test_data_manager.get_all()
        if all_data:
            context["test_data"] = all_data[0]
        else:
            raise ValueError("No test data available")

    return context


@pytest.fixture
def page(request):
    """Use fresh page for internal_admin scenarios, authenticated page for all others."""
    if request.node.get_closest_marker("internal_admin"):
        return request.getfixturevalue("fresh_page")
    return request.getfixturevalue("authenticated_page")
