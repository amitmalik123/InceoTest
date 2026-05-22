"""Step definitions for Edit Family feature."""

from pytest_bdd import parsers, then, when
def _resolve_value(raw_value: str, data_row: dict) -> str:
    token = str(raw_value).strip()
    if token.startswith("<") and token.endswith(">"):
        key = token[1:-1].strip()
        if key not in data_row:
            available_columns = ", ".join(sorted(data_row.keys()))
            raise KeyError(
                f"Missing column '{key}' in edit_family_data.csv. Available columns: {available_columns}"
            )
        return str(data_row[key]).strip()
    return token


@when(parsers.parse('the user searches for family "{family_name}"'))
def search_family(edit_family_page, edit_family_data_row, family_name):
    edit_family_page.enter_search_family_name(_resolve_value(family_name, edit_family_data_row))


@when("the user clicks Search for family")
def click_search_for_family(edit_family_page):
    edit_family_page.click_search()


@when("the user clicks Edit for family result")
def click_edit_family(request, edit_family_page, edit_family_data_row):
    family_name = str(edit_family_data_row.get("search_family_name", "")).strip()
    target_status = str(edit_family_data_row.get("edit_target_status", "Approved")).strip() or "Approved"
    edit_family_page.click_edit(family_name=family_name, target_status=target_status)
    request.node.skip_submit_for_existing_record = edit_family_page.is_existing_record_warning_seen()


@when(parsers.parse('the user verifies Family Name and Program Name are non-editable for "{family_name}"'))
def verify_non_editable_fields(edit_family_page, edit_family_data_row, family_name):
    target_status = str(edit_family_data_row.get("edit_target_status", "Approved")).strip() or "Approved"
    edit_family_page.verify_non_editable_fields(
        _resolve_value(family_name, edit_family_data_row),
        target_status=target_status,
    )


@when("the user updates family fields with the following data:")
def update_family_fields(edit_family_page, edit_family_data_row, datatable=None, table=None):
    data = {}
    target_status = str(edit_family_data_row.get("edit_target_status", "Approved")).strip() or "Approved"
    is_rejected = target_status.lower() == "rejected"

    if datatable:
        for row in datatable:
            if len(row) >= 2:
                key = str(row[0]).strip()
                if key == "program_name" and not is_rejected:
                    continue
                value = _resolve_value(str(row[1]).strip(), edit_family_data_row)
                data[key] = value
    elif table:
        for line in table.strip().split("\n"):
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) == 2:
                key = parts[0].strip()
                if key == "program_name" and not is_rejected:
                    continue
                value = _resolve_value(parts[1].strip(), edit_family_data_row)
                data[key] = value
    else:
        raise ValueError("No data table was provided for edit family update step.")

    data["edit_target_status"] = target_status
    edit_family_page.apply_edit_data(data)


@when("the user confirms Edit Family submission")
def confirm_edit_family_submission(edit_family_page):
    edit_family_page.confirm_update()


@then("the user verifies Family update was successful")
def verify_edit_family_success(edit_family_page, edit_family_data_row):
    family_name = str(edit_family_data_row.get("search_family_name", "")).strip()
    expected_status = ""
    edit_family_page.verify_update_success(family_name=family_name, expected_status=expected_status)
