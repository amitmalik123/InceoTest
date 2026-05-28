"""Step definitions for Create Family feature."""

import logging

from pytest_bdd import then, when

from utils.database import get_sql_query


logger = logging.getLogger(__name__)


REQUIRED_FIELDS = [
    "family_name",
    "manager_type_code",
    "program_name",
    "is_uma_custom",
    "has_minimum",
    "standard_discount_eligible",
    "style_code",
    "style_description",
    "manager_style_description",
    "research_group",
    "schedule_group",
]

def _resolve_value(raw_value: str, data_row: dict) -> str:
    token = str(raw_value).strip()
    if token.startswith("<") and token.endswith(">"):
        key = token[1:-1].strip()
        if key not in data_row:
            available_columns = ", ".join(sorted(data_row.keys()))
            raise KeyError(
                f"Missing column '{key}' in create_family_data.csv. Available columns: {available_columns}"
            )
        return str(data_row[key]).strip()
    return token


def _validate_required_fields(data: dict):
    return [field for field in REQUIRED_FIELDS if str(data.get(field, "")).strip() == ""]


@when("the user clicks Create Model Family button")
def click_create_model_family(create_family_page):
    create_family_page.click_create_model_family()


@when("the user verifies the Create new Family form is displayed")
def verify_create_family_form(create_family_page):
    create_family_page.verify_create_family_form()


@when("the user fills in the family form with the following data:")
def fill_family_form(request, create_family_page, create_family_data_row, datatable=None, table=None):
    data = {}

    if datatable:
        for row in datatable:
            if len(row) >= 2:
                key = str(row[0]).strip()
                value = _resolve_value(str(row[1]).strip(), create_family_data_row)
                data[key] = value
    elif table:
        for line in table.strip().split("\n"):
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) == 2:
                key = parts[0].strip()
                value = _resolve_value(parts[1].strip(), create_family_data_row)
                data[key] = value
    else:
        raise ValueError("No data table was provided for family form step.")

    missing_or_blank = _validate_required_fields(data)
    request.node.create_family_missing_fields = missing_or_blank
    request.node.create_family_row_id = str(create_family_data_row.get("family_name", "")).strip() or "unknown_row"

    if missing_or_blank:
        row_id = request.node.create_family_row_id
        request.node.create_family_validation_status = "missing_mandatory_fields"
        logger.warning(
            "Mandatory field(s) are blank in create_family_data.csv for row '%s': %s. Continuing to submit so UI validation popup can be verified.",
            row_id,
            ", ".join(missing_or_blank),
        )

    create_family_page.create_family(data)


@then("the user verifies the family was created successfully")
def verify_family_created(request, create_family_page, create_family_data_row):
    if getattr(request.node, "create_family_validation_status", "") == "missing_mandatory_fields":
        create_family_page.verify_missing_field_popup(getattr(request.node, "create_family_missing_fields", []))
        return

    family_name = str(create_family_data_row.get("family_name", "")).strip()
    result = create_family_page.verify_family_created(expected_family_name=family_name)
    if result == "duplicate":
        return


@then("the user verifies the family exists in the Family table")
def verify_family_exists_in_database(request, create_family_data_row):
    if getattr(request.node, "create_family_validation_status", "") == "missing_mandatory_fields":
        return

    family_name = str(create_family_data_row.get("family_name", "")).strip()
    if not family_name:
        raise AssertionError("Family name is required to verify the database record after creation.")

    db_query = get_sql_query("family_exists_by_name")
    db = request.getfixturevalue("db_manager").get_vault_db("billing")
    rows = db.execute_query(db_query, params=(family_name,))

    if not rows:
        raise AssertionError(f"Family '{family_name}' was created in the UI but was not found in the Family table.")

    logger.info("Verified family '%s' exists in the Family table. Rows found: %d", family_name, len(rows))
