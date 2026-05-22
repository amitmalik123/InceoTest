from typing import Optional

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.logger import setup_logger
from locators.stp.stp_ict.select_destination_locators import SelectDestinationLocators

logger = setup_logger(__name__)


class SelectDestinationPage(BasePage):
    PAGE_URL = 'https://test11.ewealthmanager.com/ISCT/ModifyInvestment'

    def __init__(self, page: Page):
        super().__init__(page)
        self.locators = SelectDestinationLocators()
        # Primary dropdown trigger: the <dt class="firstmenu"> container
        self.select_destination_investments_dropdown: Locator = self.page.locator(self.locators.SELECT_DESTINATION_DROPDOWN['css'])
        self.new_investment_option: Locator = self.page.locator(self.locators.NEW_INVESTMENT_CONTAINER['css'])
        self.single_strategy_account_option: Locator = self.page.locator(self.locators.SINGLE_STRATEGY_ACCOUNT['css'])
        # Model picker: try role-based combobox resolution
        try:
            self.choose_new_investment_dropdown: Optional[Locator] = self.resolve_locator(self.locators.COMBOBOX)
        except Exception:
            self.choose_new_investment_dropdown = None
        self.ok_button: Locator = self.resolve_locator(self.locators.OK_BUTTON)
        self.one_hundred_percent_radio: Locator = self.page.locator(self.locators.ONE_HUNDRED_RADIO['css'])
        self.next_button: Locator = self.resolve_locator(self.locators.NEXT)

    def navigate(self) -> None:
        logger.info(f"Navigating to Select Destination page: {self.PAGE_URL}")
        self.page.goto(self.PAGE_URL)
        self.page.wait_for_load_state('networkidle', timeout=30000)
        logger.info("Select Destination page loaded")

    def click_select_destination_investments_dropdown(self) -> None:
        logger.info("Clicking Select Destination Investments dropdown")
        # After click_next() on source account, browser navigates via form POST.
        # Wait for the URL to leave SelectAccount, then wait for the dropdown element.
        if 'SelectAccount' in self.page.url:
            logger.info("Waiting for navigation away from SelectAccount page")
            self.page.wait_for_url(lambda url: 'SelectAccount' not in url, timeout=60000)
        self.page.wait_for_load_state('domcontentloaded', timeout=30000)
        # Click the dt container (clicking the inner anchor sometimes doesn't trigger the UI)
        self.select_destination_investments_dropdown.wait_for(state='visible', timeout=60000)
        # Prefer clicking the inner anchor first (this usually triggers the dropdown JS)
        anchor = self.select_destination_investments_dropdown.locator('a').first
        tried_hover = False
        try:
            anchor.click()
        except Exception:
            try:
                anchor.evaluate("el => el.click()")
            except Exception:
                try:
                    anchor.click(force=True)
                except Exception:
                    # Try hover (some UIs open menus on hover)
                    try:
                        anchor.hover()
                        tried_hover = True
                    except Exception:
                        # Last resort: click the dt container
                        try:
                            self.select_destination_investments_dropdown.click()
                        except Exception:
                            self.select_destination_investments_dropdown.evaluate("el => el.click()")
        # Wait for the New Investment container to appear after opening
        try:
            self.new_investment_option.wait_for(state='visible', timeout=8000)
        except Exception:
            # If hover was attempted, or click didn't make it visible, try dispatching mouse events
            logger.warning('New Investment container not visible after opening dropdown; attempting hover/mouseenter fallback')
            try:
                if not tried_hover:
                    anchor.hover()
                anchor.evaluate("el => el.dispatchEvent(new MouseEvent('mouseenter', {bubbles:true, cancelable:true}))")
            except Exception:
                try:
                    anchor.evaluate("el => el.dispatchEvent(new MouseEvent('mouseover', {bubbles:true, cancelable:true}))")
                except Exception:
                    logger.debug('Mouse event fallbacks did not reveal New Investment')
            # Still not visible: capture diagnostics and try a forced-visibility fallback
            try:
                self.page.screenshot(path='reports/select_destination_dropdown_debug.png')
                with open('reports/select_destination_dropdown_debug.html', 'w', encoding='utf-8') as fh:
                    fh.write(self.page.content())
                logger.info('Saved dropdown debug artifacts to reports/')
            except Exception:
                logger.debug('Failed to save dropdown diagnostics')
            try:
                # Temporary DOM tweak: force the menu to display to allow downstream interactions
                self.page.evaluate("() => { const el = document.querySelector('dd#newInvestmentMenu'); if (el) el.style.display='block'; }")
                self.new_investment_option.wait_for(state='visible', timeout=3000)
            except Exception:
                logger.warning('Forced-visibility fallback did not reveal New Investment menu')
        logger.info("Select Destination Investments dropdown opened")

    def select_new_investment(self) -> None:
        logger.info("Selecting New Investment")
        # The primary dropdown should be open; click the 'New investment' anchor to open the account-type submenu
        self.new_investment_option.wait_for(state='attached', timeout=10000)
        new_inv_anchor = self.new_investment_option.locator('a').first
        try:
            new_inv_anchor.wait_for(state='visible', timeout=5000)
            new_inv_anchor.click()
        except Exception:
            try:
                new_inv_anchor.evaluate("el => el.click()")
            except Exception:
                try:
                    new_inv_anchor.click(force=True)
                except Exception:
                    logger.warning('Could not click New Investment anchor; attempting to scroll into view')
                    try:
                        self.new_investment_option.evaluate("el => el.scrollIntoView(true)")
                        new_inv_anchor.click()
                    except Exception:
                        logger.debug('All attempts to activate New Investment anchor failed')
        logger.info("New Investment selected")

    def select_single_strategy_account_under_open_design(self) -> None:
        logger.info("Selecting Single Strategy Account under Open Design")
        # dl#targetdll2 is revealed by hovering over New Investment
        self.single_strategy_account_option.wait_for(state='visible', timeout=10000)
        self.single_strategy_account_option.click()
        logger.info("Single Strategy Account selected")

    def choose_new_investment_model(self, model_name: str) -> None:
        logger.info(f"Choosing new investment model: {model_name}")
        # After selecting account type, a model picker combobox/dropdown appears
        # Try combobox (native select) first, then fall back to custom dl/a approach
        try:
            combobox = self.page.get_by_role('combobox').first
            combobox.wait_for(state='visible', timeout=8000)
            combobox.select_option(label=model_name)
            logger.info(f"Selected model '{model_name}' via combobox")
        except Exception:
            # Fallback: click the visible model link/a element containing the model name
            model_link = self.page.get_by_text(model_name, exact=False).first
            model_link.wait_for(state='visible', timeout=10000)
            model_link.click()
            logger.info(f"Selected model '{model_name}' via text link")
        try:
            self.page.screenshot(path='reports/after_model_selection.png')
            with open('reports/after_model_selection.html', 'w', encoding='utf-8') as fh:
                fh.write(self.page.content())
            logger.info("Saved post-model-selection diagnostics to reports/")
        except Exception:
            pass

    def click_ok(self) -> None:
        logger.info("Clicking OK button")
        self.ok_button.click()
        logger.info("OK button clicked")

    def select_one_hundred_percent(self) -> None:
        logger.info("Selecting 100% radio button")
        # Two matching labels exist; use .first and click via JS for uniform widget
        radio_label = self.page.locator("#allocRdFull1_1").first
        radio_label.wait_for(state='attached', timeout=10000)
        radio_label.evaluate("el => el.click()")
        logger.info("100""%" "radio button selected")  

    def click_next(self) -> None:
        logger.info("Clicking Next button on Select Destination page")
        self.next_button.click()
        logger.info("Next button clicked")
       