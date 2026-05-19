"""Locators for model-management wrapper model page objects."""

from playwright.sync_api import Locator, Page


class ModelsLocators:
    """Factory methods that return Playwright locators for Models UI elements."""

    @staticmethod
    def models_link(page: Page) -> Locator:
        return page.locator("a:has-text('Models'), [role='link']:has-text('Models')").first

    @staticmethod
    def published_tab(page: Page) -> Locator:
        return page.locator("[role='tab']:has-text('Published'), button:has-text('Published')").first

    @staticmethod
    def drafts_tab(page: Page) -> Locator:
        return page.locator("[role='tab']:has-text('Draft'), button:has-text('Draft')").first

    @staticmethod
    def create_model_button(page: Page) -> Locator:
        return page.locator("button:has-text('Create Model')").first

    @staticmethod
    def model_name_field(page: Page) -> Locator:
        return page.locator("input[placeholder*='Model'], input[name*='model']").first

    @staticmethod
    def model_name_box(page: Page) -> Locator:
        return page.locator("input[placeholder*='name'], input[name*='name']").first

    @staticmethod
    def confirm_name_button(page: Page) -> Locator:
        return page.locator("button:has-text('Confirm'), button:has-text('Continue')").first

    @staticmethod
    def add_strategy_button(page: Page) -> Locator:
        return page.locator("button:has-text('Add Strategy'), button:has-text('Add strategy')").first

    @staticmethod
    def strategy_modal(page: Page) -> Locator:
        return page.locator("[role='dialog']").first

    @staticmethod
    def choose_strategies_title(page: Page) -> Locator:
        return page.locator("text=Choose Strategies, text='Choose strategies'").first

    @staticmethod
    def add_strategies_button(page: Page) -> Locator:
        return page.locator("button:has-text('Add Strategies'), button:has-text('Add')").first

    @staticmethod
    def strategy_checkboxes(page: Page) -> Locator:
        return page.locator("input[type='checkbox']")

    @staticmethod
    def model_analytics_header(page: Page) -> Locator:
        return page.locator("h1:has-text('Model'), h2:has-text('Model Analytics')").first

    @staticmethod
    def allocation_row_inputs(page: Page) -> Locator:
        return page.locator("[role='gridcell'] input[type='text']")

    @staticmethod
    def allocation_total_indicator(page: Page) -> Locator:
        return page.locator("text=100%, text='Total 100%'").first

    @staticmethod
    def strategy_row(page: Page) -> Locator:
        return page.locator("[role='row'][row-index]")

    @staticmethod
    def model_summary_widget(page: Page) -> Locator:
        return page.locator("text='Model Summary', text='Model summary'").first

    @staticmethod
    def asset_allocation_widget(page: Page) -> Locator:
        return page.locator("text='Asset Allocation', text='Asset allocation'").first

    @staticmethod
    def risk_return_widget(page: Page) -> Locator:
        return page.locator("text='Risk/Return', text='Risk / Return'").first

    @staticmethod
    def performance_widget(page: Page) -> Locator:
        return page.locator("text='Performance'").first

    @staticmethod
    def save_draft_button(page: Page) -> Locator:
        return page.locator("button:has-text('Save Draft'), button:has-text('Save draft')").first

    @staticmethod
    def publish_model_button(page: Page) -> Locator:
        return page.locator("button:has-text('Publish Model'), button:has-text('Publish')").first

    @staticmethod
    def asset_class_allocation_widget(page: Page) -> Locator:
        return page.locator("text='Asset Class Allocation', text='Asset class allocation'").first

    @staticmethod
    def holdings_section(page: Page) -> Locator:
        return page.locator("text='Holdings', section:has-text('Holdings')").first

    @staticmethod
    def continue_to_validations_button(page: Page) -> Locator:
        return page.locator("button:has-text('Continue to Validations'), button:has-text('Continue')").first

    @staticmethod
    def no_critical_issues_text(page: Page) -> Locator:
        return page.locator("text='No critical issues', text='No Critical Issues'").first

    @staticmethod
    def continue_to_publish_button(page: Page) -> Locator:
        return page.locator("button:has-text('Continue to Publish'), button:has-text('Continue')").first

    @staticmethod
    def model_published_successfully_text(page: Page) -> Locator:
        return page.locator("text='Model published successfully', text='Published successfully'").first

    @staticmethod
    def edit_model_button(page: Page) -> Locator:
        return page.locator("button:has-text('Edit Model'), button:has-text('Edit')").first

    @staticmethod
    def edit_draft_button(page: Page) -> Locator:
        return page.locator("button:has-text('Edit Draft'), button:has-text('Edit')").first
