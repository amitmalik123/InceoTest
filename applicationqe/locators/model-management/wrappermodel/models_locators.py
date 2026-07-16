"""Locators for model-management wrapper model page objects."""

from playwright.sync_api import Locator, Page


class ModelsLocators:
    """Factory methods that return Playwright locators for Models UI elements."""

    @staticmethod
    def models_link(page: Page) -> Locator:
        return page.locator("a:has-text('Models'), [role='link']:has-text('Models')").first

    @staticmethod
    def published_tab(page: Page) -> Locator:
        return page.locator(
            "[role='tab']:text-matches('^\\s*published\\s*$', 'i'), "
            "button:text-matches('^\\s*published\\s*$', 'i'), "
            "[role='tab'][aria-label*='published' i], "
            "button[aria-label*='published' i]"
        ).first

    @staticmethod
    def drafts_tab(page: Page) -> Locator:
        return page.locator(
            "[role='tab']:text-matches('^\\s*drafts?\\s*$', 'i'), "
            "button:text-matches('^\\s*drafts?\\s*$', 'i'), "
            "[role='tab'][aria-label*='draft' i], "
            "button[aria-label*='draft' i]"
        ).first

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
        return page.locator(
            "button:visible:text-matches('^\\s*add\\s+strateg(y|ies)\\s*$', 'i'), "
            "[role='button']:visible:text-matches('^\\s*add\\s+strateg(y|ies)\\s*$', 'i'), "
            "button:visible:has-text('Add Strategy'), "
            "button:visible:has-text('Add strategy'), "
            "button:visible:has-text('Add Strategies'), "
            "button:visible[aria-label*='add strategy' i], "
            "[role='button']:visible[aria-label*='add strategy' i], "
            "button:visible[data-testid*='add-strategy' i], "
            "[role='button']:visible[data-testid*='add-strategy' i], "
            "button:visible[class*='add' i][class*='strategy' i]"
        ).first

    @staticmethod
    def strategy_modal(page: Page) -> Locator:
        return page.locator("[role='dialog']").first

    @staticmethod
    def choose_strategies_title(page: Page) -> Locator:
        return page.locator("text=Choose Strategies, text='Choose strategies'").first

    @staticmethod
    def add_strategies_button(page: Page) -> Locator:
        return page.locator(
            "[role='dialog'] button:has-text('Add Strategies'), "
            "[role='dialog'] button:has-text('Add strategies')"
        ).first

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
        return page.locator(
            # Exact wrappermodel action button variant provided by DOM snippet.
            "button.css-gvxwld-actionButton-secondaryButton-ActionButtons:visible:text-matches('^\\s*save\\s+as(\\s+a)?\\s+draft\\s*$', 'i'), "
            "button[class*='actionButton-secondaryButton-ActionButtons' i]:visible:text-matches('^\\s*save\\s+as(\\s+a)?\\s+draft\\s*$', 'i'), "
            "button.css-bi4yv8-actionButton-primaryButton-ActionButtons:visible:text-matches('^\\s*save\\s+as(\\s+a)?\\s+draft\\s*$', 'i'), "
            "button[class*='actionButton-primaryButton-ActionButtons' i]:visible:text-matches('^\\s*save\\s+as(\\s+a)?\\s+draft\\s*$', 'i'), "
            # Prefer model-detail header/top-right action bar first.
            "[class*='modelAnalyticsHeader'] button:visible:text-matches('^\\s*save(\\s+as(\\s+a)?)?\\s+draft\\s*$', 'i'), "
            "[class*='modelHeader'] button:visible:text-matches('^\\s*save(\\s+as(\\s+a)?)?\\s+draft\\s*$', 'i'), "
            "[class*='headerAction'] button:visible:text-matches('^\\s*save(\\s+as(\\s+a)?)?\\s+draft\\s*$', 'i'), "
            # Some variants render top-right button text as plain 'Save'.
            "[class*='modelAnalyticsHeader'] button:visible:text-matches('^\\s*save\\s*$', 'i'), "
            "[class*='modelHeader'] button:visible:text-matches('^\\s*save\\s*$', 'i'), "
            "[class*='headerAction'] button:visible:text-matches('^\\s*save\\s*$', 'i'), "
            "[class*='modelAnalyticsHeader'] [role='button']:visible:text-matches('^\\s*save\\s*$', 'i'), "
            "[class*='modelHeader'] [role='button']:visible:text-matches('^\\s*save\\s*$', 'i'), "
            "[class*='headerAction'] [role='button']:visible:text-matches('^\\s*save\\s*$', 'i'), "
            "[role='main'] button:visible:text-matches('^\\s*save(\\s+as(\\s+a)?)?\\s+draft\\s*$', 'i'), "
            "button:visible:text-matches('^\\s*save(\\s+as(\\s+a)?)?\\s+draft\\s*$', 'i'), "
            "[role='button']:visible:text-matches('^\\s*save(\\s+as(\\s+a)?)?\\s+draft\\s*$', 'i'), "
            "button:visible:text-matches('^\\s*save\\s+as\\s+a\\s+draft\\s*$', 'i'), "
            "[role='button']:visible:text-matches('^\\s*save\\s+as\\s+a\\s+draft\\s*$', 'i'), "
            "button:visible[aria-label*='save' i][aria-label*='draft' i], "
            "[role='button']:visible[aria-label*='save' i][aria-label*='draft' i], "
            "button:visible[title*='save' i][title*='draft' i], "
            "[role='button']:visible[title*='save' i][title*='draft' i], "
            "button:visible[data-testid*='save-as-draft' i], "
            "[role='button']:visible[data-testid*='save-as-draft' i], "
            "button:visible[data-testid*='save' i][data-testid*='as' i][data-testid*='draft' i], "
            "[role='button']:visible[data-testid*='save' i][data-testid*='as' i][data-testid*='draft' i], "
            "button:visible[data-testid*='save' i][data-testid*='draft' i], "
            "[role='button']:visible[data-testid*='save' i][data-testid*='draft' i], "
            "button:visible[class*='save' i][class*='draft' i]"
        ).first

    @staticmethod
    def publish_model_button(page: Page) -> Locator:
        # Use exact-ish matching to avoid hitting 'Continue to Publish' or 'Published'.
        return page.locator(
            # Prefer sticky footer / bottom-right action areas first.
            "[class*='footer'] button:visible:text-matches('^\\s*publish(\\s+model)?\\s*$', 'i'), "
            "[class*='bottom'] button:visible:text-matches('^\\s*publish(\\s+model)?\\s*$', 'i'), "
            "[class*='actionBar'] button:visible:text-matches('^\\s*publish(\\s+model)?\\s*$', 'i'), "
            "[class*='sticky'] button:visible:text-matches('^\\s*publish(\\s+model)?\\s*$', 'i'), "
            "[class*='right'] button:visible:text-matches('^\\s*publish(\\s+model)?\\s*$', 'i'), "
            "[role='main'] button:visible:text-matches('^\\s*publish(\\s+model)?\\s*$', 'i'), "
            "button:has-text('Publish Model'):visible, "
            "button:has-text('Publish model'):visible, "
            "button:has-text('Publish'):not(:has-text('Continue')):visible, "
            "[role='button']:has-text('Publish Model'):visible, "
            "[role='button']:has-text('Publish'):not(:has-text('Continue')):visible, "
            "button:text-matches('^\\s*publish(\\s+model)?\\s*$', 'i'):visible, "
            "[role='button']:text-matches('^\\s*publish(\\s+model)?\\s*$', 'i'):visible, "
            "button[aria-label*='publish model' i]:visible, "
            "button[aria-label*='publish' i]:visible, "
            "[role='button'][aria-label*='publish model' i]:visible, "
            "[role='button'][aria-label*='publish' i]:visible, "
            "button[title*='publish model' i]:visible, "
            "button[title*='publish' i]:visible, "
            "[role='button'][title*='publish model' i]:visible, "
            "[role='button'][title*='publish' i]:visible, "
            "button[data-testid*='publish-model' i]:visible, "
            "button[data-testid*='publish' i]:visible, "
            "[role='button'][data-testid*='publish-model' i]:visible, "
            "[role='button'][data-testid*='publish' i]:visible, "
            "button[class*='publishModel' i]:visible, "
            "button[class*='publish' i]:visible"
        ).first

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
        return page.locator(
            "button:text-matches('^\\s*continue\\s+to\\s+publish\\s*$', 'i'), "
            "[role='button']:text-matches('^\\s*continue\\s+to\\s+publish\\s*$', 'i'), "
            "button:text-matches('^\\s*continue.*publish\\s*$', 'i'), "
            "[role='button']:text-matches('^\\s*continue.*publish\\s*$', 'i'), "
            "button:has-text('Continue to Publish'), "
            "button:has-text('Continue & Publish'), "
            "button:has-text('Continue and Publish'), "
            "button[aria-label*='continue to publish' i], "
            "[role='button'][aria-label*='continue to publish' i], "
            "button[title*='continue to publish' i], "
            "[role='button'][title*='continue to publish' i], "
            "[data-testid*='continue' i][data-testid*='publish' i], "
            "button:text-matches('^\\s*publish(\\s+model)?\\s*$', 'i'), "
            "[role='button']:text-matches('^\\s*publish(\\s+model)?\\s*$', 'i')"
        ).first

    @staticmethod
    def model_published_successfully_text(page: Page) -> Locator:
        return page.locator(
            "text='Model published successfully', "
            "text='Published successfully', "
            "text='Model Published Successfully', "
            "text='Model is now published', "
            "text='Model has been published'"
        ).first

    @staticmethod
    def edit_model_button(page: Page) -> Locator:
        return page.locator(
            "button:text-matches('^\\s*edit(\\s+model)?\\s*$', 'i'), "
            "[role='button']:text-matches('^\\s*edit(\\s+model)?\\s*$', 'i'), "
            "button[aria-label*='edit model' i], "
            "[data-testid*='edit' i][data-testid*='model' i]"
        ).first

    @staticmethod
    def edit_draft_button(page: Page) -> Locator:
        return page.locator("button:has-text('Edit Draft'), button:has-text('Edit')").first
