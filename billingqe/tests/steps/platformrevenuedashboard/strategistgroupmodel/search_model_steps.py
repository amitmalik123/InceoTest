"""Step definitions for Search Model feature."""

from pytest_bdd import then, when


@when("the user clicks the Model tab")
def click_model_tab(search_model_page):
    search_model_page.click_model_tab()


@when("the user verifies Model page is loaded for Search Model scenario")
def verify_model_page_loaded(search_model_page):
    search_model_page.verify_model_page_loaded()


@when("the user executes search model validations from test data")
def execute_search_model_validations(request, search_model_page, search_model_data_row):
    model_id = str(search_model_data_row.get("model_id", "")).strip()

    if not model_id:
        raise ValueError(
            "search_model_data.csv row must have a non-empty 'model_id'"
        )

    search_model_page.search_model_by_id(model_id)

    # Auto-detect: if records are present, validate action buttons by status;
    # otherwise verify no-records state.  The user does NOT need to pre-know
    # whether the model exists in the system.
    if search_model_page.has_model_rows():
        search_model_page.verify_action_button_visibility_by_status()
    else:
        search_model_page.verify_no_records_found(model_id=model_id)

    request.node.search_model_validations_completed = True


@then("the user verifies search model validations completed successfully")
def verify_search_model_validations_completed(request):
    if not getattr(request.node, "search_model_validations_completed", False):
        raise AssertionError("Search model validations did not complete successfully")

