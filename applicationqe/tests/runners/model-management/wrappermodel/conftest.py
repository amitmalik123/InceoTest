import os
from collections.abc import Sequence

import pytest


def _is_truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def pytest_configure(config) -> None:
    config.addinivalue_line("markers", "wrappermodel: wrappermodel BDD scenarios")
    config.addinivalue_line("markers", "models: wrappermodel feature tag")
    config.addinivalue_line("markers", "test_add_model: wrappermodel add-model feature tag")
    if _is_truthy(os.getenv("WRAPPERMODEL_HEADED")):
        config.option.headed = True


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args, request):
    headed = request.config.getoption("--headed", default=False)
    launch_args = list(browser_type_launch_args.get("args", []))

    if headed and "--start-maximized" not in launch_args:
        launch_args.append("--start-maximized")

    return {
        **browser_type_launch_args,
        "args": launch_args,
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, request):
    headed = request.config.getoption("--headed", default=False)
    context_args = {
        **browser_context_args,
        "ignore_https_errors": True,
        "accept_downloads": True,
    }

    if headed:
        context_args["no_viewport"] = True
        context_args.pop("viewport", None)

    return context_args


def pytest_collection_modifyitems(items: Sequence[pytest.Item]) -> None:
    wrapper_marker = pytest.mark.wrappermodel
    app_marker = pytest.mark.app("wrapper")
    for item in items:
        item.add_marker(wrapper_marker)
        item.add_marker(app_marker)


def pytest_sessionfinish(session, exitstatus) -> None:
    """Push WrapperModel execution metrics to InfluxDB/Grafana after the run."""
    try:
        from pages.model_management.wrappermodel.influx_reporter import AllureToInfluxDB

        reporter = AllureToInfluxDB()
        allure_results_dir = session.config.getoption("--alluredir") or "reports/allure-results"
        reporter.allure_results_dir = allure_results_dir

        if reporter.auto_push:
            reporter.run()
        else:
            print(
                "\nWrapperModel InfluxDB auto-push disabled "
                "(set 'auto_push': true in config/model-management/wrappermodel/influxdb_config.json)"
            )
    except Exception as e:
        print(f"\nWARNING: WrapperModel metrics push failed: {e}")
