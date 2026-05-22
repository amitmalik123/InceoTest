"""Step definitions for Search Family feature."""

from pytest_bdd import then, when


def _optional_value(data_row: dict, key: str) -> str:
    return str(data_row.get(key, "")).strip()


def _run_positive_search(approve_reject_family_page, family_name: str, status: str, expected_status: str = ""):
    approve_reject_family_page.search_family_with_filters(family_name=family_name, status=status)
    approve_reject_family_page.verify_search_results()
    approve_reject_family_page.verify_search_results_match_text(family_name)
    approve_reject_family_page.verify_search_results_have_action_buttons()
    if str(expected_status).strip():
        approve_reject_family_page.verify_search_results_have_status(expected_status)


def _run_no_record_search(approve_reject_family_page, family_name: str, status: str):
    approve_reject_family_page.search_family_with_filters(family_name=family_name, status=status)
    approve_reject_family_page.verify_no_records_found_message()


@when("the user verifies Family page is loaded for Search Family scenario")
def verify_family_page_for_search(approve_reject_family_page):
    approve_reject_family_page.verify_family_page_with_approve_reject()


@when("the user executes all search family validations from test data")
def execute_all_search_family_validations(request, approve_reject_family_page, search_family_data_row):
    executed_checks = 0

    full_name_all = _optional_value(search_family_data_row, "full_name_all")
    if full_name_all:
        _run_positive_search(approve_reject_family_page, family_name=full_name_all, status="ALL")
        executed_checks += 1

    partial_name_all = _optional_value(search_family_data_row, "partial_name_all")
    if partial_name_all:
        _run_positive_search(approve_reject_family_page, family_name=partial_name_all, status="ALL")
        executed_checks += 1

    missing_name_all = _optional_value(search_family_data_row, "missing_name_all")
    if missing_name_all:
        _run_no_record_search(approve_reject_family_page, family_name=missing_name_all, status="ALL")
        executed_checks += 1

    partial_name_pending = _optional_value(search_family_data_row, "partial_name_pending")
    if partial_name_pending:
        _run_positive_search(
            approve_reject_family_page,
            family_name=partial_name_pending,
            status="Pending",
            expected_status="Pending",
        )
        executed_checks += 1

    partial_name_rejected = _optional_value(search_family_data_row, "partial_name_rejected")
    if partial_name_rejected:
        _run_positive_search(
            approve_reject_family_page,
            family_name=partial_name_rejected,
            status="Rejected",
            expected_status="Rejected",
        )
        executed_checks += 1

    missing_name_rejected = _optional_value(search_family_data_row, "missing_name_rejected")
    if missing_name_rejected:
        _run_no_record_search(approve_reject_family_page, family_name=missing_name_rejected, status="Rejected")
        executed_checks += 1

    if executed_checks == 0:
        raise ValueError(
            "search_family_data.csv row must contain at least one search value in one of these columns: "
            "full_name_all, partial_name_all, missing_name_all, partial_name_pending, "
            "partial_name_rejected, missing_name_rejected"
        )

    request.node.search_family_validations_completed = True


@then("the user verifies search family validations completed successfully")
def verify_search_family_validations_completed(request):
    if not getattr(request.node, "search_family_validations_completed", False):
        raise AssertionError("Search family validations did not complete successfully")
