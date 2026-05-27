"""
Step definitions for Add Model feature scenarios.

Business-level steps covering:
  TC1  - Models page access and key columns
  TC2  - Create model and allocate holdings
  TC3  - Edit draft model name
  TC4  - Edit allocation percentages on draft model
  TC5  - Add additional strategies to draft model
  TC7  - Create and publish a model
  TC9  - Add strategy to a published model

All UI interaction logic lives in pages/models_page.py.
"""

from pathlib import Path
import sys

from playwright.sync_api import Page, expect
from pytest_bdd import given, then, when

models_page_dir = (
    Path(__file__).resolve().parents[4] / "pages" / "model-management" / "wrappermodel"
)
if str(models_page_dir) not in sys.path:
    sys.path.insert(0, str(models_page_dir))
from models_page import ModelsPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


# Business-level BDD steps for add_model.feature


@given("the user is on the models page")
def user_is_on_models_page(page: Page, models_page: ModelsPage):
    models_page.navigate()


@given("the user is on the draft models list")
def user_is_on_draft_models_list(page: Page, models_page: ModelsPage):
    models_page.go_to_draft_models_list()


@given("the user is on the published models list")
def user_is_on_published_models_list(page: Page, models_page: ModelsPage):
    models_page.go_to_published_models_list()


@then("published models are shown by default")
def published_models_default(page: Page, models_page: ModelsPage):
    assert models_page.is_published_tab_active(), "Published models are not shown by default"


@then("model creation is available")
def model_creation_available(page: Page, models_page: ModelsPage):
    models_page.assert_model_creation_available()


@then("the models list includes key business columns")
def models_list_has_key_columns(page: Page, models_page: ModelsPage):
    models_page.assert_models_list_includes_key_business_columns()


@then("the drafts tab is available")
def drafts_tab_is_available(page: Page, models_page: ModelsPage):
    models_page.assert_drafts_tab_visible()


@then("the models list displays published model data")
def models_list_displays_published_data(page: Page, models_page: ModelsPage):
    models_page.assert_models_list_has_data()


@when("the user starts a new model")
@when("the user creates a new model")
def user_starts_new_model(page: Page, models_page: ModelsPage, test_context: dict):
    model_name = models_page.start_new_model_with_valid_name()
    test_context["created_model_name"] = model_name


@when("the user adds 2 strategies to the model")
def user_adds_two_strategies(page: Page, models_page: ModelsPage):
    models_page.add_n_strategies(2)


@when("the user allocates holdings equally to total 100 percent")
def user_allocates_equal_100(page: Page, models_page: ModelsPage):
    models_page.allocate_equal_percentages()


@when("the user saves the model as draft")
def user_saves_draft(page: Page, models_page: ModelsPage):
    models_page.click_save_draft()


@then("the model is saved as a draft with a valid model identifier")
def draft_saved_with_valid_id(page: Page, models_page: ModelsPage):
    models_page.assert_draft_saved_with_identifier()


@then("model analytics are available")
def model_analytics_available(page: Page, models_page: ModelsPage):
    models_page.assert_model_analytics_available()


@then("the model can be published")
def model_can_be_published(page: Page, models_page: ModelsPage):
    expect(models_page.publish_model_button).to_be_visible(timeout=10000)


@given("the user opens the most recently updated draft model")
def user_opens_most_recent_draft(page: Page, models_page: ModelsPage):
    models_page.open_most_recent_draft_model()


@given("the user opens a draft model with at least 3 strategies")
def user_opens_draft_with_three_strategies(page: Page, models_page: ModelsPage):
    models_page.open_first_draft_model_with_multiple_strategies()


@when("the user removes one strategy from the model")
def user_removes_one_strategy(page: Page, models_page: ModelsPage):
    models_page.remove_strategy_from_investment_widget()


@then("the save draft button is disabled")
def save_draft_button_disabled(page: Page, models_page: ModelsPage):
    models_page.assert_save_draft_button_disabled()


@when("the user adjusts all holdings to total 100 percent")
def user_adjusts_holdings_to_100(page: Page, models_page: ModelsPage):
    models_page.adjust_remaining_allocation_to_100()


@then("no validation errors are displayed")
def no_validation_errors_displayed(page: Page, models_page: ModelsPage):
    models_page.assert_no_validation_errors()


@when("the user updates the model name")
def user_updates_model_name(page: Page, models_page: ModelsPage, test_context: dict):
    from datetime import datetime

    new_name = f"Test_{datetime.now().strftime('%H%M%S')}"
    actual_name = models_page.edit_draft_model_name(new_name)
    test_context["updated_model_name"] = actual_name


@then("the updated model name is shown")
def updated_name_shown(page: Page, models_page: ModelsPage, test_context: dict):
    updated_name = test_context.get("updated_model_name")
    assert updated_name, "Updated model name not found in test context"
    models_page.assert_model_name_in_header(updated_name)


@then("the updated model name persists after reload")
def updated_name_persists(page: Page, models_page: ModelsPage, test_context: dict):
    updated_name = test_context.get("updated_model_name")
    assert updated_name, "Updated model name not found in test context"
    models_page.assert_name_persists_after_refresh(updated_name)


@when("the user updates holdings allocations to total 100 percent")
def user_updates_allocations(page: Page, models_page: ModelsPage, test_context: dict):
    allocations = models_page.modify_allocation_percentages()
    test_context["updated_allocations"] = allocations


@then("the total allocation is 100 percent")
def total_allocation_100_business(page: Page, models_page: ModelsPage):
    models_page.assert_total_allocation_equals_100()


@then("the updated allocations persist after reload")
def updated_allocations_persist_business(page: Page, models_page: ModelsPage):
    models_page.assert_allocation_persists_after_refresh()


@given("the user notes the current number of holdings")
def user_notes_current_holdings(page: Page, models_page: ModelsPage, test_context: dict):
    count = models_page.get_allocation_row_count()
    test_context["pre_add_strategy_count"] = count


@when("the user adds 2 additional strategies")
def user_adds_additional_strategies(page: Page, models_page: ModelsPage, test_context: dict):
    added_count = models_page.add_n_strategies(2)
    test_context["added_strategy_count"] = added_count


@when("the user allocates all holdings to total 100 percent")
def user_allocates_all_holdings(page: Page, models_page: ModelsPage, test_context: dict):
    values = models_page.allocate_all_strategies_summing_to_100()
    test_context["expected_strategy_count"] = len(values)


@then("the model contains additional strategies with saved allocations")
def model_contains_additional_strategies(page: Page, models_page: ModelsPage, test_context: dict):
    pre_count = test_context.get("pre_add_strategy_count", 0)
    added_count = test_context.get("added_strategy_count", 1)
    models_page.assert_newly_added_strategies_at_zero(
        pre_count, expected_added_min=max(1, int(added_count))
    )


@then("the changes persist after reload")
def changes_persist_after_reload(page: Page, models_page: ModelsPage, test_context: dict):
    expected_count = test_context.get("expected_strategy_count", 1)
    models_page.assert_strategies_and_allocation_persist_after_refresh(expected_count)


@given("the user opens an existing published model in edit mode")
def user_opens_published_model_in_edit_mode(page: Page, models_page: ModelsPage):
    models_page.open_existing_published_model_in_edit_mode()


@when("the user submits the draft for publication")
def user_submits_draft_for_publication(page: Page, models_page: ModelsPage):
    models_page.submit_draft_for_publication()


@then("model update summary metrics are displayed")
def update_summary_metrics_displayed(page: Page, models_page: ModelsPage):
    models_page.assert_model_update_summary_metrics_displayed()


@then("holdings and asset allocation details are displayed")
def holdings_and_asset_allocation_displayed(page: Page, models_page: ModelsPage):
    models_page.assert_holdings_and_asset_allocation_details_displayed()


@then("the model passes critical validations")
def model_passes_critical_validations(page: Page, models_page: ModelsPage):
    models_page.assert_model_passes_critical_validations()


@then("the model is published successfully")
def model_published_successfully_business(page: Page, models_page: ModelsPage):
    models_page.assert_model_is_published_successfully()
