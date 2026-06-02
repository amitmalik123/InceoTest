import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "wrappermodel: wrappermodel BDD scenarios")
    config.addinivalue_line("markers", "models: wrappermodel feature tag")
    config.addinivalue_line("markers", "test_add_model: wrappermodel add-model feature tag")


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


def pytest_collection_modifyitems(items):
    marker = pytest.mark.wrappermodel
    for item in items:
        item.add_marker(marker)
