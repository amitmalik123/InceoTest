"""Step definitions for Search Model feature."""

from pytest_bdd import then, when


def _optional_value(data_row: dict, key: str) -> str:
    return str(data_row.get(key, "")).strip()


@when("the user clicks the Model tab")
def click_model_tab(search_model_page):
    search_model_page.click_model_tab()


@when("the user verifies Model page is loaded for Search Model scenario")
def verify_model_page_loaded(search_model_page):
    search_model_page.verify_model_page_loaded()


@when("the user executes search model validations from test data")
def execute_search_model_validations(request, search_model_page, search_model_data_row):
    model_id = _optional_value(search_model_data_row, "model_id")
    missing_model_id = _optional_value(search_model_data_row, "missing_model_id")
    executed_checks = 0

    if model_id:
        search_model_page.search_model_by_id(model_id)
        # model_id rows are expected to be valid model results.
        search_model_page.verify_action_button_visibility_by_status()
        executed_checks += 1

    if missing_model_id:
        search_model_page.search_model_by_id(missing_model_id)
        # Verify no records found for missing model ID.
        search_model_page.verify_no_records_found(model_id=missing_model_id)
        executed_checks += 1

    if executed_checks == 0:
        raise ValueError(
            "search_model_data.csv must contain at least one non-empty value in "
            "'model_id' or 'missing_model_id'"
        )

    request.node.search_model_validations_completed = True


@then("the user verifies search model validations completed successfully")
def verify_search_model_validations_completed(request):
    if not getattr(request.node, "search_model_validations_completed", False):
        raise AssertionError("Search model validations did not complete successfully")

