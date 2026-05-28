"""Step definitions for Approve/Reject Family feature."""

from pytest_bdd import then, when
def _resolve_value(raw_value: str, data_row: dict) -> str:
    token = str(raw_value).strip()
    if token.startswith("<") and token.endswith(">"):
        key = token[1:-1].strip()
        if key not in data_row:
            available_columns = ", ".join(sorted(data_row.keys()))
            raise KeyError(
                f"Missing column '{key}' in approve_reject_family_data.csv. "
                f"Available columns: {available_columns}"
            )
        return str(data_row[key]).strip()
    return token


@when("the user verifies Family page is loaded with Approve/Reject button")
def verify_family_page_with_approve_reject_button(approve_reject_family_page):
    approve_reject_family_page.verify_family_page_with_approve_reject()


@when("the user searches for family to approve or reject from test data")
def search_family_to_approve_reject(approve_reject_family_page, approve_reject_family_data_row):
    family_name = str(approve_reject_family_data_row.get("family_name", "")).strip()
    if not family_name:
        raise ValueError("'family_name' column is required in approve_reject_family_data.csv")
    approve_reject_family_page.enter_search_family_name(_resolve_value(family_name, approve_reject_family_data_row))


@when("the user clicks Search for family")
def click_search_for_family(approve_reject_family_page):
    approve_reject_family_page.click_search()


@when("the user verifies search results are displayed")
def verify_search_results_displayed(approve_reject_family_page):
    approve_reject_family_page.verify_search_results()


@when("the user clicks Approve/Reject button for the family")
def click_approve_reject_button(approve_reject_family_page):
    approve_reject_family_page.click_approve_reject_button()


@when("the user verifies Approve/Reject dialog is displayed")
def verify_approve_reject_dialog(approve_reject_family_page):
    approve_reject_family_page.verify_approve_reject_dialog()


@when("the user performs the approve or reject action based on test data")
def perform_approve_or_reject_action(approve_reject_family_page, approve_reject_family_data_row):
    action = str(approve_reject_family_data_row.get("action", "")).strip().lower()

    if not action:
        raise ValueError(
            "'action' column is required in approve_reject_family_data.csv with values: "
            "'approve', 'reject', or 'cancel'"
        )

    if action == "approve":
        approve_reject_family_page.click_approve()
    elif action == "reject":
        approve_reject_family_page.click_reject()
    elif action == "cancel":
        approve_reject_family_page.click_cancel()
    else:
        raise ValueError(f"Invalid action '{action}' in approve_reject_family_data.csv")


@then("the user verifies the action was successful")
def verify_action_successful(approve_reject_family_page, approve_reject_family_data_row):
    action = str(approve_reject_family_data_row.get("action", "")).strip().lower()
    family_name = _resolve_value(
        str(approve_reject_family_data_row.get("family_name", "")).strip(),
        approve_reject_family_data_row,
    )

    if action == "approve":
        approve_reject_family_page.verify_approval_success_message(family_name)
        approve_reject_family_page.click_ok_button()
    elif action == "reject":
        approve_reject_family_page.verify_rejection_success_message(family_name)
        approve_reject_family_page.click_ok_button()


@then("the user verifies the family status is updated correctly")
def verify_family_status_updated(approve_reject_family_page, approve_reject_family_data_row):
    action = str(approve_reject_family_data_row.get("action", "")).strip().lower()
    family_name = _resolve_value(
        str(approve_reject_family_data_row.get("family_name", "")).strip(),
        approve_reject_family_data_row,
    )

    if action == "approve":
        approve_reject_family_page.verify_family_status_approved(family_name)
    elif action == "reject":
        approve_reject_family_page.verify_family_status_rejected(family_name)
