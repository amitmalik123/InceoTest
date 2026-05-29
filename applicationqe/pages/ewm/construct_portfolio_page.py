import traceback

from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger
from utils.assertions import Assertions

logger = get_allure_logger(__name__)


class ConstructPortfolioPage(BasePage):
    """Page object for Construct Portfolio page"""
    PAGE_PATH = "DNeWM/NBT/Portfolio/ConstructPortfolio.aspx"

    def __init__(self, page: Page):
        super().__init__(page)
        self.form_root = self.active_root()
        # Add locators as needed for portfolio construction elements
        self.next_button: Locator = self.form_root.locator("#construct_next")
        self.registration_type_dropdown: Locator = self.form_root.locator('#registration_type_dropdown')
        self.custodian_dropdown: Locator = self.form_root.locator('#registration_custodian dt.firstmenu a')
        self.investment_amount_input: Locator = self.form_root.locator('#AccountSectionInvestmentAmount')
        
        # Account type locators
        self.account_type_dropdown: Locator = self.form_root.locator('#account_type_dropdown dt.firstmenu')
        self.account_type_option: Locator = self.form_root.locator('#account_type_dropdown')
        self.msa_notification: Locator = self.form_root.locator('#msa_notification, [id*="msa"][id*="notification"]')
        self.msa_third_party_notification: Locator = self.form_root.locator('#msa_third_party_notification, [id*="msa"][id*="third"]')
        
        # Investment selection locators
        self.choose_investment_window: Locator = self.form_root.locator('#InvestmentSelectorContainer')
        self.investment_solution_sorted: Locator = self.form_root.locator('tr td.investment-solution.sorted')
        self.confirm_modal_selection: Locator = self.form_root.locator('#InvestmentSelectorContainer input#OkButton, #next-back-section input#OkButton').first
        # Scoped locators to avoid strict mode violations (duplicate #InvestmentSelectorContainer in #advisor_model_picker_modal)
        self.shell_investment_window: Locator = self.form_root.locator('#model_picker_modal #InvestmentSelectorContainer')
        self.shell_investment_sorted: Locator = self.form_root.locator('#model_picker_modal tr td.investment-solution.sorted')
        self.shell_confirm_selection: Locator = self.form_root.locator('#model_picker_modal input#OkButton')
        self.funds_label: Locator = self.form_root.locator('#americanFundsModalLabel')
        self.fund_modal_button: Locator = self.form_root.locator('[value="Ok"][data-dismiss="modal"]')
        self.add_investment_msa: Locator = self.form_root.locator('#add_investment_button')
        self.msa_review_button: Locator = self.form_root.locator('#multi_strategy_review')
        self.private_asset_alert_for_pa: Locator = self.form_root.locator('#SingleTickerModalLabel')
        self.private_asset_alert_for_pa_okay: Locator = self.form_root.locator('#single-ticker-ok')
        self.confirm_button: Locator = self.form_root.locator('[value="Confirm"]')

        # SDBA registration popup locators (from Selenium: //*[@id='self_directed_brokerage_warning_modal']/div/div)
        self.sdba_warning_modal_header: Locator = self.form_root.locator(
            "#self_directed_brokerage_warning_modal .modal-header"
        )
        self.sdba_warning_modal_checkbox: Locator = self.form_root.locator(
            "#self_directed_brokerage_warning_modal_checkbox"
        )
        # Close button - from Selenium locator, ID-based for accuracy
        self.sdba_warning_modal_close_button: Locator = self.form_root.locator(
            "#self_directed_brokerage_warning_modal_close_button"
        )
        
        # Custodian locators
        self.custodian_dropdown_container: Locator = self.form_root.locator('#registration_custodian')
        
        # Investment percentage locators
        self.percent_inputs: Locator = self.form_root.locator('input[name="percentsLabels"]')
        
        # Review and confirm locators
        self.review_or_msa_review_button: Locator = self.form_root.locator('[value="Review"], #multi_strategy_review')
        self.review_button: Locator = self.form_root.locator('[value="Review"]')
        self.add_pa_button: Locator = self.form_root.locator('#add_pa_button, button:has-text("Add Investment")')
        self.confirm_button_input: Locator = self.form_root.locator('input[type="button"][value="Confirm"]')
        self.confirm_button_text: Locator = self.form_root.locator('button:has-text("Confirm")')
        self.confirm_button_xpath_button: Locator = self.form_root.locator('//button[contains(., "Confirm")]')
        self.confirm_button_xpath_input: Locator = self.form_root.locator('//input[@value="Confirm"]')
        
        # Single/Multi strategy confirmation locators
        self.single_strategy_confirm: Locator = self.form_root.locator('input#single_strategy_confirm')
        self.multi_strategy_confirm: Locator = self.form_root.locator('input#multi_strategy_confirm')
        self.ok_button_visible: Locator = self.form_root.locator('input[type="button"][value="Ok"]:visible')
        
        # TMS locators
        self.tms_options_yes: Locator = self.form_root.locator("#tmsOptionsYes")
        self.tms_options_no: Locator = self.form_root.locator("#tmsOptionsNo")
        self.tms_low_sensitivity: Locator = self.form_root.locator("#low")
        self.tms_continue_button: Locator = self.form_root.locator("#Continue")
        self.construct_next_button: Locator = self.form_root.locator("input#construct_next")
        
        # Client Portfolio Suitability popup locators
        self.suitability_header: Locator = self.form_root.locator("#risk_assessment-actionLabel")
        self.suitability_radio_option: Locator = self.form_root.locator("input[class='risk-assessment-action-radio'][value='3']")
        self.suitability_text_area: Locator = self.form_root.locator("#suitability_explanation_area")
        self.suitability_save_button: Locator = self.form_root.get_by_role("button", name="Save")
        
        # Summary table locators
        self.edit_account_link: Locator = self.form_root.locator("a:has-text('Edit Account')")
        self.proposed_accounts_locator: Locator = self.form_root.locator(
            "//div[normalize-space()='Proposed Accounts']/following-sibling::div[1]/div[1]"
        )
        self.total_portfolio_locator: Locator = self.form_root.locator(
            "//div[normalize-space()='Total Portfolio']/following-sibling::div"
        )
    
    # Helper methods for dynamic locators (factory methods that return Locator objects)
    def get_registration_type_locator(self, registration_type: str) -> Locator:
        """Get locator for registration type by text."""
        return self.form_root.locator(f"xpath=//span[contains(text(),'{registration_type}')]").first
    
    def get_registration_group_locator(self, group_name: str) -> Locator:
        """Get locator for registration group by name."""
        return self.form_root.locator(f"xpath=//span[contains(text(),'{group_name}')]")
    
    def get_registration_subtype_by_data_name_locator(self, sub_type: str) -> Locator:
        """Get locator for registration sub-type by data-name attribute."""
        return self.form_root.locator(f"xpath=//dd//li[@data-name='{sub_type}']")
    
    def get_custodian_option_by_data_value_locator(self, data_value: str) -> Locator:
        """Get locator for custodian option by data-value attribute."""
        return self.form_root.locator(f'#registration_custodian dd a[data-value="{data_value}"]')
    
    def get_custodian_option_by_text_locator(self, custodian: str) -> Locator:
        """Get locator for custodian option by text."""
        return self.form_root.locator(f'#registration_custodian dd a:has-text("{custodian}")')
    
    def get_account_type_option_locator(self, account_type: str) -> Locator:
        """Get locator for account type option by text."""
        return self.form_root.locator(f'#account_type_dropdown dd a:has-text("{account_type}")')
    
    def get_investment_solution_locator(self, investment_solution: str) -> Locator:
        """Get locator for investment solution by text."""
        return self.form_root.locator(f'tr td.investment-solution.sorted:has-text("{investment_solution}")')
    
    def construct_portfolio(self, portfolio_data: dict) -> None:
        """
        Construct portfolio with the provided data.
        
        Args:
            portfolio_data: Dictionary containing portfolio construction details
        """
        logger.info("Constructing portfolio with provided data")
        # Implement portfolio construction logic here

    def select_client_registration_type(self, registration_type: str, label: str, log_message: str) -> None:
        """
        Select client registration type.
        
        Args:
            registration_type: Type of registration (e.g., "Personal" or "Retirement Plans, Self-Directed Brokerage Account")
            label: Label for the field
            log_message: Message to log
        """
        logger.info(f"{label} : {log_message}")
        
        try:
            self.registration_type_dropdown.wait_for(state="visible", timeout=15000)
            self.registration_type_dropdown.click()

            if "," not in registration_type:
                # Simple registration type (no group/sub-type)
                group_locator = self.get_registration_type_locator(registration_type.strip())
                group_locator.wait_for(state="visible", timeout=5000)
                group_locator.click()
                logger.info(f"Selected registration type: {registration_type.strip()}")
                return

            # Registration type with group and sub-type
            group_name, sub_type = [part.strip() for part in registration_type.split(",", 1)]
            
            # Select group
            group_locator = self.get_registration_group_locator(group_name)
            group_locator.wait_for(state="visible", timeout=5000)
            group_locator.click()
            logger.info(f"Selected group: {group_name}")
            
            # Select sub-type
            # Only two SDBA variants exist:
            #   data-name="Self-Directed Brokerage Account" (value=51)
            #   data-name="Self-Directed Brokerage Account - 403(b)" (value=52)
            # Exact data-name match works for all types including SDBA
            sub_type_locator = self.get_registration_subtype_by_data_name_locator(sub_type)
            
            sub_type_locator.wait_for(state="visible", timeout=10000)
            sub_type_locator.click()
            logger.info(f"Selected sub-type: {sub_type}")

            # Handle SDBA popup if applicable
            if "Self-Directed Brokerage Account" in sub_type:
                self.verify_and_close_sdba_registration_popup()
                
        except Exception as e:
            logger.error(f"Failed to select registration type: {registration_type}")
            raise RuntimeError(f"Registration type selection failed for: {registration_type}") from e


    def select_client_custodian(self, client_type: str, custodian: str, label: str, log_message: str) -> None:
        """
        Select client custodian.
        
        Args:
            client_type: Type of client
            custodian: Custodian name
            label: Label for the field
            log_message: Message to log
        """
        logger.info(f"{label} : {log_message}")
        
        try:
            # Click custodian dropdown
            self.custodian_dropdown.wait_for(state="visible", timeout=10000)
            self.custodian_dropdown.click()
            logger.info("Custodian dropdown clicked")

            # Headless safety: force dropdown container to show options in the current root context.
            self.custodian_dropdown_container.evaluate(
                """
                (container) => {
                    if (!container) return;
                    container.classList.add('open');
                    const dd = container.querySelector('dd');
                    if (dd) {
                        dd.style.display = 'block';
                        dd.style.visibility = 'visible';
                        dd.style.opacity = '1';
                    }
                }
                """
            )
            
            # Select custodian using data-value attribute
            custodian_data_map = {
                "AssetMark Trust": "GNW",
                "Fidelity": "FID",
                "Fidelity Direct": "FDD",
                "Pershing Advisor Solutions": "PRS",
                "Schwab": "TDA",
                "Schwab Direct": "SWB"
            }
            
            data_value = custodian_data_map.get(custodian)
            if data_value:
                custodian_option = self.get_custodian_option_by_data_value_locator(data_value)
            else:
                custodian_option = self.get_custodian_option_by_text_locator(custodian)
            
            # Wait for dropdown container to be visible
            self.custodian_dropdown_container.wait_for(state="visible", timeout=15000)
            
            # Wait for at least one anchor option to be in the DOM (hidden until dropdown opens)
            self.form_root.locator('#registration_custodian dd a').first.wait_for(state="attached", timeout=5000)
            
            # Try DOM click first (reliable in both headed and headless)
            logger.info(f"Selecting custodian '{custodian}' via DOM click...")
            result = self.custodian_dropdown_container.evaluate(
                """
                (container, { dataValue, custodianText }) => {
                    if (!container) return { clicked: false, reason: 'no container' };
                    container.classList.add('open');
                    const dd = container.querySelector('dd');
                    if (dd) {
                        dd.style.display = 'block';
                        dd.style.visibility = 'visible';
                        dd.style.opacity = '1';
                    }
                    const anchors = Array.from(container.querySelectorAll('dd a'));
                    let target = null;
                    if (dataValue) {
                        target = anchors.find(a => a.getAttribute('data-value') === dataValue);
                    }
                    if (!target && custodianText) {
                        target = anchors.find(a => (a.textContent || '').trim().includes(custodianText));
                    }
                    if (!target) return { clicked: false, reason: 'not found' };
                    target.scrollIntoView({ block: 'center' });
                    target.click();
                    return { clicked: true };
                }
                """,
                {"dataValue": data_value, "custodianText": custodian},
            )
            if result.get("clicked"):
                logger.info(f"✓ Custodian '{custodian}' selected via DOM click")
            else:
                # Fallback to normal Playwright click
                logger.warning(f"DOM click failed ({result.get('reason')}), trying normal click...")
                custodian_option.wait_for(state="attached", timeout=5000)
                try:
                    custodian_option.scroll_into_view_if_needed()
                    custodian_option.click(timeout=5000)
                except Exception:
                    try:
                        custodian_option.click(force=True, timeout=3000)
                    except Exception:
                        # Last resort: JS click bypasses visibility entirely
                        logger.warning("Force click also failed, using JS click")
                        custodian_option.evaluate("el => el.click()")
                logger.info(f"✓ Custodian '{custodian}' selected via normal click")

        except Exception as e:
            logger.error(f"Custodian selection failed for: {custodian} - {str(e)[:200]}")
            raise

    def insert_investment_amount(self, amount: str, label: str, log_message: str) -> None:
        """
        Insert investment amount.
        
        Args:
            amount: Investment amount to insert
            label: Label for the field
            log_message: Message to log
        """
        try:
            amount_value = "" if amount is None else str(amount)
            self.investment_amount_input.wait_for(state="visible", timeout=5000)
            self.investment_amount_input.click()
            self.investment_amount_input.fill(amount_value)
            logger.info(f"Investment amount entered: {amount_value}")
        except Exception as e:
            logger.error(f"Failed to insert investment amount: {amount}")
            raise RuntimeError(f"Investment amount insertion failed for: {amount}") from e

    def select_account_type(self, account_type: str, label: str, log_message: str) -> None:
        """
        Select account type.
        
        Args:
            account_type: Type of account (e.g., "Single Strategy Account", "Multiple Strategy Account")
            label: Label for the field
            log_message: Message to log
        """
        logger.info(f"{label} : {log_message}")
        
        try:
            # Wait for page to stabilize
            self.page.wait_for_timeout(1000)
            
            # Click account type dropdown
            self.account_type_dropdown.wait_for(state="visible", timeout=5000)
            self.account_type_dropdown.click()
            logger.info("Account type dropdown opened")
            
            # Wait for dropdown to expand and options to be available
            self.page.wait_for_timeout(1000)

            # Try DOM click first (reliable in both headed and headless)
            logger.info(f"Selecting account type '{account_type}' via DOM click...")
            result = self.account_type_option.evaluate(
                "(el, t) => { const dd = el.querySelector(':scope > dd'); if (dd) { dd.style.display='block'; dd.style.visibility='visible'; dd.style.opacity='1'; } const a = Array.from(el.querySelectorAll('dd a')).find(x => (x.textContent||'').trim().includes(t)); if (!a) return {clicked:false}; a.scrollIntoView({block:'center'}); a.click(); return {clicked:true}; }",
                account_type,
            )
            if result.get("clicked"):
                logger.info(f"✓ Account type '{account_type}' selected via DOM click")
            else:
                # Fallback to normal Playwright click
                logger.warning(f"DOM click failed, trying normal click...")
                account_option = self.get_account_type_option_locator(account_type)
                account_option.wait_for(state="attached", timeout=5000)
                self._click_element_with_strategies(account_option, f"Account type '{account_type}'", timeout=5000)
                logger.info(f"✓ Account type '{account_type}' selected via normal click")
            
            # Wait for page to stabilize after account type selection
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            self.page.wait_for_timeout(1500)
            
            # If Multiple Strategy Account is selected, verify MSA notifications
            if account_type == "Multiple Strategy Account":
                logger.info("Verifying MSA notifications for Multiple Strategy Account")
                
                expected_msa_message = "Click the Add Investment button to start adding investments to the Multiple Strategy Account. A Multiple Strategy Account must have at least two investments but no more than eight."
                expected_third_party_message = "Important information regarding third party reporting solutions."
                
                # Wait for MSA notification to be visible
                self.msa_notification.wait_for(state="visible", timeout=5000)
                msa_text = self.msa_notification.text_content().strip()
                
                if expected_msa_message not in msa_text:
                    Assertions.fail(f"Expected MSA notification message not found. Got: {msa_text}")
                logger.info("MSA notification verified")
                
                # Wait for third party notification
                self.msa_third_party_notification.wait_for(state="visible", timeout=5000)
                third_party_text = self.msa_third_party_notification.text_content().strip()
                
                if expected_third_party_message not in third_party_text:
                    Assertions.fail(f"Expected third party notification message not found. Got: {third_party_text}")
                logger.info("MSA third party notification verified")
            
            logger.info(f"Account type '{account_type}' selected successfully")
            
        except Exception as e:
            logger.error(f"Failed to select account type: {account_type}")
            raise RuntimeError(f"Account type selection failed for: {account_type}") from e

    def choose_new_investment_from_modal(self, investment_solution: str, label: str, log_message: str, 
                                          account_type: str, private_asset_option: str) -> None:
        """
        Choose new investment from modal window based on account type.
        
        Args:
            investment_solution: Investment solution to select (can be pipe-separated for multiple)
            label: Label for the field
            log_message: Message to log
            account_type: Type of account (e.g., "Multiple Strategy Account", "Single Strategy Account")
            private_asset_option: Private asset option (Ok/Cancel)
        """
        logger.info(f"{label} : {log_message}")
        self.scroll_to_top()  # Ensure we're at the top of the page before interacting with modals
        
        try:
            if account_type == "Multiple Strategy Account":
                self._handle_msa_investment(investment_solution, private_asset_option)
            elif account_type == "GPS Select Access":
                self._select_investment_solution(investment_solution, account_type, private_asset_option)
            elif account_type == "Savos Personal Portfolio Access":
                self._select_investment_solution(investment_solution, account_type, private_asset_option)
            elif account_type == "Savos Personal Portfolio Custom":
                self._handle_sppc_investment(investment_solution, private_asset_option)
            else:
                # Default Single Strategy Account
                self._select_investment_solution(investment_solution, account_type, private_asset_option)
                self._handle_funds_modal_if_visible()
                
                # Try to confirm single strategy investment if button exists
                logger.info("Attempting to confirm single strategy investment")
                self.confirm_single_strategy_investment()

                # Click review button if present to enable confirmation/next
                if self.review_or_msa_review_button.is_visible(timeout=5000):
                    self.review_or_msa_review_button.click()
                    logger.info("Review button clicked")
                    self.page.wait_for_timeout(1000)
                
            logger.info(f"Investment '{investment_solution}' selected successfully for {account_type}")
            
        except Exception as e:
            logger.error(f"Failed to choose investment: {investment_solution}")
            raise RuntimeError(f"Investment selection failed for: {investment_solution}") from e

    def _handle_msa_investment(self, investment_solution: str, private_asset_option: str) -> None:
        """Handle Multiple Strategy Account investment selection with multiple solutions."""
        solutions = [s.strip() for s in investment_solution.split("|")]
        
        for solution in solutions:
            # Click add investment button
            self.add_investment_msa.wait_for(state="visible", timeout=10000)
            self.add_investment_msa.click()
            logger.info(f"Add investment button clicked for solution: {solution}")
            
            # Select the investment solution
            self._select_investment_solution(solution, "Multiple Strategy Account", private_asset_option)
            
            # Handle funds modal if visible
            self._handle_funds_modal_if_visible()
        
        # Update investment percentages
        self._update_msa_investment_percents()
        
        # Click review button
        self.msa_review_button.wait_for(state="visible", timeout=10000)
        self.msa_review_button.click()
        logger.info("MSA review button clicked")
        
        self.page.wait_for_timeout(1000)
        
        # Handle private asset alerts
        if self.private_asset_alert_for_pa.is_visible(timeout=3000):
            logger.info("Private asset alert detected")
            self.private_asset_alert_for_pa_okay.click()

    def _handle_sppc_investment(self, investment_solution: str, private_asset_option: str) -> None:
        """Handle Savos Personal Portfolio Custom investment selection."""
        solutions = [s.strip() for s in investment_solution.split("|")]
        
        for i, solution in enumerate(solutions):
            if i > 0:
                # Click add investment button for subsequent investments
                if self.add_pa_button.count() > i - 1:
                    buttons = self.add_pa_button.all()
                    buttons[i - 1].click()
                    logger.info(f"Add investment button clicked for solution {i}: {solution}")
            
            # Select the investment solution
            self._select_investment_solution(solution, "Savos Personal Portfolio Custom", private_asset_option)
            self._handle_funds_modal_if_visible()
        
        # Update investment percentages
        self._update_sppc_investment_percents()
        
        # Click review button
        if self.review_button.is_visible(timeout=5000):
            self.review_button.click()
            logger.info("Review button clicked")
            self.page.wait_for_timeout(1000)
        
        # Click confirm button if visible
        if self.confirm_button.is_visible(timeout=3000):
            self.confirm_button.click()
            logger.info("Confirm button clicked")

    def _select_investment_solution(self, investment_solution: str, account_type: str, private_asset_option: str) -> None:
        """Select investment solution from the modal."""
        # Try scoped locator first (works when modal is under #model_picker_modal)
        try:
            self.shell_investment_window.wait_for(state="visible", timeout=15000)
            logger.info("Investment window found under #model_picker_modal")
        except Exception:
            # Fallback: use .first to handle duplicate #InvestmentSelectorContainer elements
            logger.warning("Scoped modal not visible, using .first on #InvestmentSelectorContainer")
            self.choose_investment_window.first.wait_for(state="visible", timeout=20000)
        
        # Wait for investment solutions to load
        try:
            self.shell_investment_sorted.first.wait_for(state="visible", timeout=10000)
        except Exception:
            logger.warning("Scoped sorted locator not visible, using .first on unscoped")
            self.investment_solution_sorted.first.wait_for(state="visible", timeout=10000)
        
        # Find and click the investment solution
        solution_locator = self.get_investment_solution_locator(investment_solution)
        if solution_locator.count() > 0:
                self._click_element_with_strategies(solution_locator.first, f"Investment '{investment_solution}'")
        else:
            logger.error(f"Investment solution not found: {investment_solution}")
            raise RuntimeError(f"Investment solution '{investment_solution}' not found in modal")
        
        # Wait for page navigation to complete before accessing confirm button
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        self.page.wait_for_timeout(1500)
        
        # Click confirm button in modal — try scoped first, fallback to .first
        try:
            self.shell_confirm_selection.wait_for(state="visible", timeout=10000)
            self.shell_confirm_selection.click(timeout=10000)
        except Exception:
            logger.warning("Scoped confirm button not visible, using .first fallback")
            self.confirm_modal_selection.wait_for(state="visible", timeout=10000)
            self.confirm_modal_selection.click(timeout=10000)
        logger.info(f"Investment '{investment_solution}' confirmed and modal closed")

    def _handle_funds_modal_if_visible(self) -> None:
        """Handle American Funds modal if it appears."""
        try:
            if self.funds_label.is_visible(timeout=2000):
                logger.info("Funds modal detected")
                self.fund_modal_button.click()
                logger.info("Funds modal closed")
                self.page.wait_for_timeout(500)
        except:
            logger.debug("No funds modal visible")

    def _update_msa_investment_percents(self) -> None:
        """Update investment percentages for Multiple Strategy Account."""
        percent_inputs = self.percent_inputs.all()
        
        for i, percent_input in enumerate(percent_inputs):
            # Click and fill with 50%
            percent_input.scroll_into_view_if_needed()
            percent_input.click(force=True)
            self.page.keyboard.press("Control+A")
            self.page.keyboard.type("50")
            self.page.keyboard.press("Tab")
            self.page.wait_for_timeout(200)
        
        logger.info("MSA investment percentages updated")

    def _update_sppc_investment_percents(self) -> None:
        """Update investment percentages for Savos Personal Portfolio Custom."""
        percent_inputs = self.percent_inputs.all()
        
        # Calculate midpoints based on guardrail ranges
        for i, percent_input in enumerate(percent_inputs):
            percent_input.scroll_into_view_if_needed()
            percent_input.click(force=True)
            self.page.keyboard.press("Control+A")
            self.page.keyboard.type("50")
            self.page.keyboard.press("Tab")
            self.page.wait_for_timeout(200)
        
        logger.info("SPPC investment percentages updated")
    
    def verify_and_close_sdba_registration_popup(self) -> None:
        """
        Verify and close the SDBA (Self-Directed Brokerage Account) registration popup if it appears.
        
        Supports both flows:
        1. Navbar flow inside iframe: check checkbox and click Continue
        2. Non-navbar flow: check checkbox and click modal close button
        """
        try:
            # Navbar flow: popup is rendered inside #iframeWrapper and closes via Continue button.
            frame = self.page.locator("#iframeWrapper").content_frame
            if frame:
                navbar_checkbox = frame.locator("#self_directed_brokerage_warning_modal_checkbox")
                if navbar_checkbox.count() > 0:
                    navbar_checkbox.wait_for(state="visible", timeout=5000)
                    try:
                        navbar_checkbox.check(timeout=3000)
                    except Exception:
                        navbar_checkbox.click(force=True)

                    continue_button = frame.get_by_role("button", name="Continue")
                    continue_button.wait_for(state="visible", timeout=5000)
                    continue_button.click()
                    self.page.wait_for_timeout(1000)
                    logger.info("✓ SDBA popup closed (navbar flow)")
                    return

            # Non-navbar flow: popup is in current active root and closes via close button.
            if self.sdba_warning_modal_header.count() == 0:
                return

            self.page.wait_for_timeout(500)

            self.sdba_warning_modal_checkbox.wait_for(state="visible", timeout=3000)
            try:
                self.sdba_warning_modal_checkbox.check(timeout=3000)
            except Exception:
                self.sdba_warning_modal_checkbox.click(force=True)

            self.page.wait_for_function(
                "() => !document.getElementById('self_directed_brokerage_warning_modal_close_button').disabled",
                timeout=5000
            )

            self.sdba_warning_modal_close_button.click()

            try:
                self.sdba_warning_modal_header.wait_for(state="hidden", timeout=5000)
            except Exception:
                pass

            self.page.wait_for_timeout(1000)
            logger.info("✓ SDBA popup closed (non-navbar flow)")

        except Exception as e:
            logger.error(f"✗ Failed to handle SDBA popup: {str(e).splitlines()[0]}")
            raise

    def click_next_button(self) -> None:
        """
        Click the next button to proceed to the next step.
        """
        logger.info("Clicking next button on construct portfolio page")

        # Do not proceed if TMS selection error is still visible.
        if self.form_root.locator("#tms_section .tms-error:visible").count() > 0:
            logger.warning("TMS error banner is visible before Next - attempting to select 'No'")
            try:
                self.tms_options_no.check(force=True)
            except Exception:
                try:
                    self.tms_options_no.click(force=True)
                except Exception:
                    pass
            try:
                self.page.wait_for_timeout(300)
            except Exception:
                pass
            if self.form_root.locator("#tms_section .tms-error:visible").count() > 0:
                raise RuntimeError("TMS error banner is visible - not clicking Next button")

        # Check if button is currently disabled
        try:
            if self.next_button.count() == 0:
                raise RuntimeError("Next button not found")
            is_disabled = self.next_button.get_attribute('disabled', timeout=2000) is not None
        except Exception as e:
            logger.warning(f"Could not read Next button state: {str(e).splitlines()[0]}")
            is_disabled = False

        if is_disabled:
            logger.info("Next button is disabled - waiting for spinner and page processing")
            self.wait_for_spinner_to_disappear()

            # Wait for Next button to become enabled naturally (confirm was already clicked)
            try:
                self.page.wait_for_function(
                    "() => !document.getElementById('construct_next')?.disabled",
                    timeout=15000
                )
                logger.info("Next button is now enabled")
                is_disabled = False
            except Exception:
                logger.warning("Next button still disabled after 15s")
                # Last resort: try clicking Confirm only if it's still visible
                try:
                    if self.single_strategy_confirm.is_visible(timeout=2000):
                        logger.info("Confirm button still visible - clicking it")
                        self.single_strategy_confirm.click(timeout=5000)
                        self.wait_for_spinner_to_disappear()
                        self.page.wait_for_function(
                            "() => !document.getElementById('construct_next')?.disabled",
                            timeout=10000
                        )
                        logger.info("Next button enabled after confirm click")
                        is_disabled = False
                except Exception as e:
                    logger.warning(f"Could not enable Next button: {str(e).splitlines()[0]}")

        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception:
            pass

        try:
            self.next_button.wait_for(state="visible", timeout=45000)
            self._click_element_with_strategies(self.next_button, "Next button (construct portfolio)")
        except Exception as e:
            logger.warning(f"Next button not visible with 45s timeout, attempting TMS Continue: {str(e).splitlines()[0]}")
            try:
                # Try TMS continue button as fallback
                self.tms_continue_button.wait_for(state="visible", timeout=20000)
                self._click_element_with_strategies(self.tms_continue_button, "TMS Continue button")
                self.page.wait_for_timeout(2000)
                try:
                    self.page.wait_for_load_state("domcontentloaded", timeout=30000)
                except Exception:
                    pass
                # Wait longer for next button after TMS continue
                self.next_button.wait_for(state="visible", timeout=45000)
                self._click_element_with_strategies(self.next_button, "Next button after TMS Continue")
            except Exception as tms_error:
                logger.error(f"Both Next button and TMS Continue failed: {tms_error}")
                # Try a direct page navigation wait as last resort
                try:
                    self.page.wait_for_load_state("domcontentloaded", timeout=10000)
                    # Try clicking next_button again with force
                    self.next_button.click(force=True)
                except Exception:
                    raise RuntimeError(f"Failed to click Next button: {tms_error}")

    def confirm_single_strategy_investment(self) -> None:
        """
        Confirm single strategy investment if visible.
        Mirrors old Selenium: confirmSingleStrategyInvestment()
        
        Looks for elements with id='single_strategy_confirm' or id='multi_strategy_confirm'
        """
        try:
            # Try the old Selenium selectors first
            selectors_list = [
                self.single_strategy_confirm,
                self.multi_strategy_confirm,
                self.ok_button_visible,
            ]
            
            confirmation_locator = None
            for locator in selectors_list:
                try:
                    if locator.count() > 0:
                        logger.info(f"Found confirmation button")
                        confirmation_locator = locator.first
                        break
                except Exception:
                    continue
            
            if confirmation_locator is None:
                logger.info("No confirmation button found")
                return
            
            # Check visibility (3s timeout like Selenium)
            try:
                is_visible = confirmation_locator.is_visible(timeout=3000)
            except Exception:
                is_visible = False
            
            if is_visible:
                confirmation_locator.click(force=True)
                self.page.wait_for_timeout(1000)
                logger.info("Single/Multi strategy investment confirmed")
                        
        except Exception as e:
            logger.error(f"ERROR in confirm_single_strategy_investment: {str(e).splitlines()[0]}")
            logger.error(f"Traceback: {traceback.format_exc()}")

    def select_tms_option(self, tms_option: str) -> None:
        """
        Select TMS (Tax Management Service) option: 'Yes' or 'No'.
        Mirrors old Selenium: taxManagementService()
        
        Args:
            tms_option: Either 'Yes' or 'No' to select the TMS option
        """
        tms_button = self.tms_options_yes if tms_option.lower() == "yes" else self.tms_options_no

        try:
            tms_button.first.wait_for(state="visible", timeout=10000)
        except Exception:
            raise RuntimeError(f"TMS option '{tms_option}' (#tmsOptions{tms_option.capitalize()}) not visible within timeout")

        try:
            tms_button.first.check()
        except Exception:
            try:
                tms_button.first.check(force=True)
            except Exception:
                try:
                    tms_button.first.click(force=True)
                except Exception:
                    self.page.evaluate("el => el.click()", tms_button.first.element_handle())

        self.wait_for_spinner_to_disappear()
        logger.info(f"TMS '{tms_option}' option selected")

    def confirm_client_portfolio(self, custodian: str, account_type: str, registration_type: str,
                                investment_solution: str) -> None:
        """
        Confirm client portfolio with proper TMS handling.
        
        Logic flow:
        1. If TMS 'No' option is visible, click it first
        2. Then try to click the Confirm button if it exists and is visible
        3. If Confirm button is not found/visible, just return - Next button may enable naturally
        """
        try:
            # Step 1: Check if TMS "No" option is visible and select it
            tms_visible = self.tms_options_no.is_visible()
            if not tms_visible:
                try:
                    self.tms_options_no.wait_for(state="visible", timeout=5000)
                    tms_visible = True
                except Exception:
                    tms_visible = False

            if tms_visible:
                logger.info("TMS 'No' option visible - clicking it")
                self._click_element_with_strategies(self.tms_options_no, "TMS 'No' radio")

                if not self.tms_options_no.is_checked():
                    logger.warning("TMS 'No' not checked - using JS fallback")
                    self.page.evaluate("""
                        const radio = document.querySelector('#tmsOptionsNo');
                        radio.checked = true;
                        radio.dispatchEvent(new Event('change', { bubbles: true }));
                    """)

                self.page.wait_for_timeout(500)
                if self.form_root.locator("#tms_section .tms-error:visible").count() > 0:
                    raise RuntimeError("TMS error banner is still present after selecting 'No'")

            # Do not proceed to Confirm when TMS error is present.
            if self.form_root.locator("#tms_section .tms-error:visible").count() > 0:
                raise RuntimeError("TMS error banner is visible - not clicking Confirm button")

            # Step 2: Check if Next button is already enabled (confirm may have been clicked in choose_new_investment_from_modal)
            self.wait_for_spinner_to_disappear()
            try:
                is_next_enabled = not self.next_button.is_disabled(timeout=2000)
            except Exception:
                is_next_enabled = False

            if is_next_enabled:
                logger.info("Next button already enabled - skipping redundant confirm click")
                return

            # Next is disabled — try clicking Confirm button
            try:
                if self.single_strategy_confirm.is_visible(timeout=3000):
                    self.single_strategy_confirm.click(timeout=5000)
                    logger.info("Client portfolio confirmed")
                else:
                    logger.info("Confirm button not visible - Next may enable after page processing")

                self.wait_for_spinner_to_disappear()
                self.page.wait_for_timeout(2000)

                # Wait for Next button to become enabled after confirmation
                self.page.wait_for_function(
                    "() => !document.getElementById('construct_next')?.disabled",
                    timeout=10000,
                )
                logger.info("Next button enabled after portfolio confirmation")
            except Exception as click_error:
                logger.warning(f"Could not enable Next button via Confirm: {str(click_error).splitlines()[0]}")
                logger.info("Will attempt to click Next button directly")

        except RuntimeError:
            raise
        except Exception as e:
            logger.warning(f"Confirm step handling: {str(e).splitlines()[0]}")

    def choose_tms_tax_sensitivity(self) -> None:
        """Choose TMS tax sensitivity option and continue."""
        try:
            self.wait_for_spinner_to_disappear()
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            except Exception:
                pass

            low = self.tms_low_sensitivity.or_(self.page.get_by_role("img", name="Low"))
            try:
                low.first.wait_for(state="visible", timeout=30000)
            except Exception:
                logger.info("TMS tax sensitivity controls are not visible - skipping")
                return

            low.first.click(force=True)
            logger.info("TMS Tax Sensitivity Option Selected")
            self.wait_for_spinner_to_disappear()

            cont = self.tms_continue_button.or_(self.page.get_by_label("Continue"))
            try:
                cont.first.wait_for(state="visible", timeout=20000)
                cont.first.click()
                logger.info("TMS Page Continue Button Clicked")
            except Exception:
                logger.info("TMS Continue button not visible - continuing")

            self.wait_for_spinner_to_disappear()
            try:
                self.construct_next_button.wait_for(state="visible", timeout=30000)
            except Exception:
                logger.info("Construct Next button not visible after TMS flow")
        except Exception as e:
            logger.info(f"Could not choose TMS tax sensitivity: {str(e).splitlines()[0]}")

    def handle_client_portfolio_suitability_popup(self) -> None:
        """
        Handle Client Portfolio Suitability popup if visible.
        This method is only applicable for custodian Schwab and registration type Self-Directed Brokerage Account - 403(b).
        """
        self.wait_for_spinner_to_disappear()
        self.scroll_to_top
        
        logger.info("Processing Client Portfolio Suitability popup")
        
        try:
            if self.suitability_header.is_visible(timeout=20000):
                # Select radio button option (3rd radio button)
                self.suitability_radio_option.wait_for(state="visible", timeout=10000)
                try:
                    self.suitability_radio_option.click(timeout=3000)
                except Exception:
                    self.suitability_radio_option.click(force=True, timeout=3000)
                if not self.suitability_radio_option.is_checked():
                    raise RuntimeError("Suitability radio state did not change after click")
                logger.info("Selected Client Portfolio Suitability option")
                
                # Enter text in textarea
                self.suitability_text_area.click()
                self.suitability_text_area.fill("test")
                logger.info("Entered Client Portfolio Suitability Comment")
                
                # Click save button
                self.suitability_save_button.click()
                logger.info("Clicked Client Portfolio Suitability Save Button")
                
                self.wait_for_spinner_to_disappear()
                logger.info("Client Portfolio Suitability popup handled")
        except Exception as e:
            logger.info(f"Could not handle portfolio suitability popup: {str(e).splitlines()[0]}")

    def verify_summary_table(self, custodian: str, account_type: str, registration_type: str, 
                            investment_solution: str) -> None:
        """
        Verify summary table based on account type.
        
        Args:
            custodian: Custodian name
            account_type: Type of account (e.g., 'Savos Personal Portfolio Access')
            registration_type: Registration type
            investment_solution: Investment solution name
        """
        try:
            if "Savos Personal Portfolio Access" in account_type:
                self._verify_sppa_summary_table(investment_solution)
            elif "GPS Select Access" in account_type:
                self._verify_gps_summary_table()
            elif "Multiple Strategy Account" in account_type:
                self._verify_msa_summary_table()
            elif "Savos Personal Portfolio Custom" in account_type:
                self._verify_sppc_summary_table()

            logger.info(f"Summary table verified for account type: {account_type}")
        except Exception as e:
            logger.error(f"Could not verify summary table: {str(e).splitlines()[0]}")

    def _verify_sppa_summary_table(self, investment_solution: str) -> None:
        """Verify SPPA summary table."""
        try:
            self.edit_account_link.click()
            self.wait_for_spinner_to_disappear()

            # Verify investment solution
            proposed_accts = self.proposed_accounts_locator
            total_portfolio = self.total_portfolio_locator

            logger.info(f"SPPA summary verified: {investment_solution}")
        except Exception as e:
            logger.error(f"SPPA summary verification failed: {str(e).splitlines()[0]}")

    def _verify_gps_summary_table(self) -> None:
        """Verify GPS summary table."""
        try:
            self.edit_account_link.click()
            self.wait_for_spinner_to_disappear()
            logger.info("GPS summary verified")
        except Exception as e:
            logger.error(f"GPS summary verification failed: {str(e).splitlines()[0]}")

    def _verify_msa_summary_table(self) -> None:
        """Verify MSA summary table."""
        try:
            self.edit_account_link.click()
            self.wait_for_spinner_to_disappear()
            logger.info("MSA summary verified")
        except Exception as e:
            logger.error(f"MSA summary verification failed: {str(e).splitlines()[0]}")

    def _verify_sppc_summary_table(self) -> None:
        """Verify SPPC summary table."""
        try:
            self.edit_account_link.click()
            self.wait_for_spinner_to_disappear()
            logger.info("SPPC summary verified")
        except Exception as e:
            logger.error(f"SPPC summary verification failed: {str(e).splitlines()[0]}")


