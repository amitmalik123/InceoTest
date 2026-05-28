"""Step definitions for Approve/Reject Model feature."""

from pytest_bdd import then, when

# NOTE: "the user clicks the Model tab" step is defined in search_model_steps.py
# and reused here via conftest.py wildcard imports.


@when("the user verifies Model page is loaded with action buttons")
def verify_model_page_loaded(approve_reject_model_page):
    approve_reject_model_page.verify_model_page_with_action_buttons()


@when("the user searches for model to approve or reject from test data")
def search_model_to_approve_reject(approve_reject_model_page, approve_reject_model_data_row):
    model_id = str(approve_reject_model_data_row.get("model_id", "")).strip()
    if not model_id:
        raise ValueError("'model_id' column is required in approve_reject_model_data.csv")
    approve_reject_model_page.enter_search_model_id(model_id)


@when("the user clicks Approve/Reject button for the model")
def click_approve_reject_model_button(approve_reject_model_page):
    approve_reject_model_page.click_approve_reject_button()


@when("the user verifies model Approve/Reject dialog is displayed")
def verify_model_approve_reject_dialog(approve_reject_model_page):
    approve_reject_model_page.verify_approve_reject_dialog()


@when("the user performs the approve or reject action for model based on test data")
def perform_model_approve_or_reject(approve_reject_model_page, approve_reject_model_data_row):
    action = str(approve_reject_model_data_row.get("action", "")).strip()
    if not action:
        raise ValueError(
            "'action' column is required in approve_reject_model_data.csv "
            "with values: 'approve' or 'reject'"
        )
    approve_reject_model_page.perform_action(action)


@then("the user verifies the model action was successful")
def verify_model_action_successful(approve_reject_model_page):
    approve_reject_model_page.verify_action_success()


@then("the user verifies the model status is updated correctly")
def verify_model_status_updated(approve_reject_model_page):
    approve_reject_model_page.verify_model_status_updated()
