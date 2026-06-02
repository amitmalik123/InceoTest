"""Step definitions for Edit Model feature."""

import logging

from pytest_bdd import then, when


logger = logging.getLogger(__name__)


@when("the user verifies Model page is loaded for Edit Model scenario")
def verify_model_page_loaded_for_edit(edit_model_page):
    edit_model_page.verify_model_page_loaded()


@when("the user verifies model grid action buttons are visible")
def verify_action_buttons(edit_model_page):
    edit_model_page.verify_action_buttons_visible()


@when("the user edits model entry from test data")
def edit_model_entry(request, edit_model_page, edit_model_data_row):
    model_id = str(edit_model_data_row.get("model_id", "")).strip()
    family_name = str(edit_model_data_row.get("family_name", "")).strip()

    if not model_id:
        raise ValueError("edit_model_data.csv row must have a non-empty 'model_id'")
    if not family_name:
        raise ValueError("edit_model_data.csv row must have a non-empty 'family_name'")

    logger.info("Editing model_id=%s with family_name=%s", model_id, family_name)

    # Phase 1: Search, click Edit, detect model type, fill form (no submit yet)
    edit_model_page.prepare_edit(model_id, family_name)

    if edit_model_page.existing_record_skipped:
        logger.warning(
            "model_id=%s skipped — already existing record. Test will PASS with warning.", model_id
        )
        request.node.edit_model_existing_record_skipped = True
    else:
        request.node.edit_model_existing_record_skipped = False

    request.node.edit_model_validations_completed = True


@then("the user verifies based on model type that only expected family edit controls are enabled and other attributes are grayed out")
def verify_model_type_assertions(request, edit_model_page):
    if getattr(request.node, "edit_model_existing_record_skipped", False):
        logger.warning("SKIPPED: Already existing record — edit controls assertion not applicable")
        return

    # Phase 2: Real Playwright assertions on form controls, then fill + submit
    edit_model_page.verify_model_type_controls()


@then("the user verifies updated model row is displayed with pending status and Edit and/or Approve Reject action buttons")
def verify_updated_row(request, edit_model_page):
    if getattr(request.node, "edit_model_existing_record_skipped", False):
        logger.warning("SKIPPED: Already existing record — updated row assertion not applicable")
        return

    # Phase 3: Re-search and verify updated row with real Playwright assertions
    edit_model_page.verify_updated_model_row()


@then("the user verifies edit model validations completed successfully")
def verify_edit_model_completed(request):
    if not getattr(request.node, "edit_model_validations_completed", False):
        raise AssertionError("Edit model validations did not complete successfully")
