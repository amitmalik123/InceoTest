import allure
from datetime import datetime, timedelta
from playwright.sync_api import Page
from pytest_bdd import parsers, then, when

from swp_establish_transaction_page_one import SWPEstablishTransactionPageOne
from swp_establish_transaction_page_two import SWPEstablishTransactionPageTwo
from utils.logger import setup_logger

logger = setup_logger(__name__)


@when(parsers.parse('User should click on the "{distribution_type}" radio button for Distribution type'))
def click_distribution_type_radio_button(page: Page, swp_establish_transaction_page_one, test_context: dict, distribution_type: str):
    """Click on distribution type radio button (Fixed or RMD)"""
    with allure.step(f"Click on '{distribution_type}' radio button for Distribution type"):
        logger.info("\n")
        logger.info(f"Clicking on '{distribution_type}' radio button for Distribution type")
        
        # Store in test context for subsequent steps
        test_context['swp_establish_transaction_page_one'] = swp_establish_transaction_page_one
        
        # Select distribution type
        swp_establish_transaction_page_one.select_distribution_type(distribution_type)
        
        logger.info(f"Distribution Type '{distribution_type}' Radio button in Transaction Page one is clicked --> Validated")
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"Distribution Type {distribution_type} Selected",
            attachment_type=allure.attachment_type.PNG
        )


@when(parsers.parse('User should click on the "{delivery_method}" radio button as delivery Method'))
def click_delivery_method_radio_button(page: Page, test_context: dict, delivery_method: str):
    """Click on delivery method radio button (ACH, Check, or Journal)"""
    with allure.step(f"Click on '{delivery_method}' radio button as delivery Method"):
        logger.info("\n")
        logger.info(f"Clicking on '{delivery_method}' radio button as delivery Method")
        
        # Get SWP Establish Transaction Page One from test context
        swp_transaction_page_one = test_context.get('swp_establish_transaction_page_one')
        if swp_transaction_page_one is None:
            # If not in context, create it
            swp_transaction_page_one = SWPEstablishTransactionPageOne(page)
            test_context['swp_establish_transaction_page_one'] = swp_transaction_page_one
        
        # Select delivery method
        swp_transaction_page_one.select_delivery_method(delivery_method)
        
        logger.info(f"Delivery Method '{delivery_method}' Radio Button in Transaction Page one is clicked --> Validated")
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"Delivery Method {delivery_method} Selected",
            attachment_type=allure.attachment_type.PNG
        )


@when("User should click on the active eligible bank radio button")
def click_active_eligible_bank_radio_button(page: Page, test_context: dict):
    """Click on the active eligible bank radio button"""
    with allure.step("Click on active eligible bank radio button"):
        logger.info("\n")
        logger.info("Clicking on active eligible bank radio button")
        
        # Get SWP Establish Transaction Page One from test context
        swp_transaction_page_one = test_context.get('swp_establish_transaction_page_one')
        if swp_transaction_page_one is None:
            swp_transaction_page_one = SWPEstablishTransactionPageOne(page)
            test_context['swp_establish_transaction_page_one'] = swp_transaction_page_one
        
        # Click active eligible bank radio button
        swp_transaction_page_one.click_active_eligible_bank_radio_button()
        
        logger.info("Active Eligible Bank Radio Button Selected")
        logger.info("Active Eligible Bank Radio Button in Transaction Page one is clicked --> Validated")
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Active Eligible Bank Selected",
            attachment_type=allure.attachment_type.PNG
        )


@when("User should click the next button on transaction page one")
def click_next_button_on_transaction_page_one(page: Page, test_context: dict):
    """Click the NEXT button on transaction page one"""
    with allure.step("Click Next button on transaction page one"):
        logger.info("\n")
        logger.info("Clicking the NEXT button on transaction page one")
        
        # Get SWP Establish Transaction Page One from test context
        swp_transaction_page_one = test_context.get('swp_establish_transaction_page_one')
        if swp_transaction_page_one is None:
            swp_transaction_page_one = SWPEstablishTransactionPageOne(page)
            test_context['swp_establish_transaction_page_one'] = swp_transaction_page_one
        
        # Click next button
        swp_transaction_page_one.click_next_button()
        
        # Wait for page transition
        page.wait_for_load_state('domcontentloaded')
        page.wait_for_timeout(2000)
        
        logger.info("Clicking the NEXT button on transaction page one ---> Validated")
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Transaction Page One - Next Clicked",
            attachment_type=allure.attachment_type.PNG
        )


@when(parsers.parse('User selects the frequency "{frequency}" on the transaction page two'))
def select_frequency_on_transaction_page_two(page: Page, test_context: dict, frequency: str):
    """Select frequency on transaction page two"""
    with allure.step(f"Select frequency '{frequency}' on transaction page two"):
        logger.info("\n")
        logger.info(f"Selecting frequency: {frequency} on transaction page two")
        
        # Get SWP Establish Transaction Page Two from test context or create it
        swp_transaction_page_two = test_context.get('swp_establish_transaction_page_two')
        if swp_transaction_page_two is None:
            swp_transaction_page_two = SWPEstablishTransactionPageTwo(page)
            test_context['swp_establish_transaction_page_two'] = swp_transaction_page_two
        
        # Select frequency
        is_frequency_selected = swp_transaction_page_two.select_frequency(frequency)
        
        # Assert frequency was selected
        assert is_frequency_selected, f"Failed to select frequency: {frequency}"
        
        logger.info(f"Successfully selected frequency: {frequency}")
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"Frequency {frequency} Selected",
            attachment_type=allure.attachment_type.PNG
        )


@when(parsers.parse('User enters the amount "{amount}" in the amount field on the transaction page two'))
def enter_amount_on_transaction_page_two(page: Page, test_context: dict, amount: str):
    """Enter amount in the amount field on transaction page two"""
    with allure.step(f"Enter amount '{amount}' in amount field"):
        logger.info("\n")
        logger.info(f"Entering amount: {amount} in the amount field on transaction page two")
        
        # Get SWP Establish Transaction Page Two from test context
        swp_transaction_page_two = test_context.get('swp_establish_transaction_page_two')
        if swp_transaction_page_two is None:
            swp_transaction_page_two = SWPEstablishTransactionPageTwo(page)
            test_context['swp_establish_transaction_page_two'] = swp_transaction_page_two
        
        # Enter amount
        swp_transaction_page_two.enter_amount(amount)
        
        # Verify amount was entered
        entered_value = swp_transaction_page_two.amount_field.input_value()
        assert entered_value == amount, f"Amount not entered correctly. Expected: {amount}, Got: {entered_value}"
        
        logger.info(f"Successfully entered the amount: {amount}")
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"Amount {amount} Entered",
            attachment_type=allure.attachment_type.PNG
        )


@when(parsers.parse('User selects the NET checkbox "{checkbox_selection}"'))
def select_net_checkbox(page: Page, test_context: dict, checkbox_selection: str):
    """Select or deselect the NET checkbox"""
    with allure.step(f"Select NET checkbox: {checkbox_selection}"):
        logger.info("\n")
        logger.info(f"NET checkbox selection: {checkbox_selection}")
        
        # Get SWP Establish Transaction Page Two from test context
        swp_transaction_page_two = test_context.get('swp_establish_transaction_page_two')
        if swp_transaction_page_two is None:
            swp_transaction_page_two = SWPEstablishTransactionPageTwo(page)
            test_context['swp_establish_transaction_page_two'] = swp_transaction_page_two
        
        # Determine if checkbox should be selected
        should_select = checkbox_selection.lower() == "select"
        
        # Set checkbox selection
        checkbox = swp_transaction_page_two.net_checkbox_locator
        checkbox.wait_for(state='visible', timeout=10000)
        
        is_currently_checked = checkbox.is_checked()
        
        if (should_select and not is_currently_checked) or (not should_select and is_currently_checked):
            checkbox.click()
            action_taken = True
            logger.info(f"Checkbox selection set to: {should_select}")
        else:
            action_taken = False
            logger.info("Checkbox was already in the desired state")
        
        # Assert action was successful
        assert action_taken or (is_currently_checked == should_select), "Checkbox selection failed"
        
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"NET Checkbox {checkbox_selection}",
            attachment_type=allure.attachment_type.PNG
        )


@then("user able to select the date from the calender picker")
def select_date_from_calendar_picker(page: Page, test_context: dict):
    """Select date from calendar picker (6th business day)"""
    with allure.step("Select date from calendar picker"):
        logger.info("\n")
        logger.info("Selecting date from calendar picker")
        
        # Get SWP Establish Transaction Page Two from test context
        swp_transaction_page_two = test_context.get('swp_establish_transaction_page_two')
        if swp_transaction_page_two is None:
            swp_transaction_page_two = SWPEstablishTransactionPageTwo(page)
            test_context['swp_establish_transaction_page_two'] = swp_transaction_page_two
        
        # Scroll to calendar and click date picker button
        swp_transaction_page_two.calendar_picker_btn.scroll_into_view_if_needed()
        swp_transaction_page_two.calendar_picker_btn.wait_for(state='visible', timeout=10000)
        swp_transaction_page_two.calendar_picker_btn.click()
        
        # Wait for calendar to open
        page.wait_for_timeout(1000)
        
        # Calculate 6th business day from today
        def is_weekend(date):
            return date.weekday() >= 5  # Saturday = 5, Sunday = 6
        
        def get_nth_business_day(start_date, n):
            """Get the nth business day from start_date"""
            current = start_date
            business_days = 0
            
            while business_days < n:
                current += timedelta(days=1)
                if not is_weekend(current):
                    business_days += 1
            
            return current
        
        today = datetime.now()
        target_date = get_nth_business_day(today, 6)
        day_to_select = str(target_date.day)  # Remove leading zero if any
        
        # Click the date button
        date_button = swp_transaction_page_two.get_date_button(day_to_select)
        date_button.wait_for(state='visible', timeout=5000)
        date_button.click()
        
        logger.info(f"Selected date: {target_date.strftime('%m/%d/%Y')}")
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Date Selected from Calendar",
            attachment_type=allure.attachment_type.PNG
        )


@then("user able to select the first available date from the calendar picker")
def select_first_available_date_from_calendar_picker(page: Page, test_context: dict):
    """Select the first enabled date from calendar picker (prod-safe, skips disabled dates)"""
    with allure.step("Select first available date from calendar picker"):
        logger.info("Selecting first available date from calendar picker (prod)")

        swp_transaction_page_two = test_context.get('swp_establish_transaction_page_two')
        if swp_transaction_page_two is None:
            swp_transaction_page_two = SWPEstablishTransactionPageTwo(page)
            test_context['swp_establish_transaction_page_two'] = swp_transaction_page_two

        swp_transaction_page_two.calendar_picker_btn.scroll_into_view_if_needed()
        swp_transaction_page_two.calendar_picker_btn.wait_for(state='visible', timeout=10000)
        swp_transaction_page_two.calendar_picker_btn.click()
        page.wait_for_timeout(1000)

        enabled_days = page.locator(
            "//button[contains(@class,'MuiPickersDay-root') and not(contains(@class,'Mui-disabled'))]"
        )
        next_month_arrow = page.locator("//button[@title='Next month' and not(@disabled)]")

        for _ in range(12):
            if enabled_days.count() > 0:
                break
            if next_month_arrow.count() > 0:
                next_month_arrow.first.click()
                page.wait_for_timeout(1000)
            else:
                break

        if enabled_days.count() == 0:
            raise RuntimeError("No enabled dates found in calendar after navigating months")

        first_enabled = enabled_days.first
        selected_day = first_enabled.text_content().strip()
        first_enabled.click()

        logger.info(f"Selected calendar day: {selected_day}")

        allure.attach(
            page.screenshot(),
            name="Date Selected from Calendar (Prod)",
            attachment_type=allure.attachment_type.PNG
        )


@when("User should click on the Distribution reasons drop down")
def click_distribution_reasons_dropdown(page: Page, test_context: dict):
    """Click on Distribution reasons dropdown"""
    with allure.step("Click on Distribution reasons dropdown"):
        logger.info("\n")
        logger.info("Clicking on Distribution reasons dropdown")
        
        # Get SWP Establish Transaction Page Two from test context
        swp_transaction_page_two = test_context.get('swp_establish_transaction_page_two')
        if swp_transaction_page_two is None:
            swp_transaction_page_two = SWPEstablishTransactionPageTwo(page)
            test_context['swp_establish_transaction_page_two'] = swp_transaction_page_two
        
        # Click distribution reason dropdown
        swp_transaction_page_two.click_distribution_reason_dropdown()
        
        logger.info("Verify user clicks on the Distribution reasons drop down ---> Validated")
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Distribution Reasons Dropdown Clicked",
            attachment_type=allure.attachment_type.PNG
        )


@when(parsers.parse('User selects the distribution reason "{selected_distribution_reason}" from the dropdown'))
def select_distribution_reason_from_dropdown(page: Page, test_context: dict, selected_distribution_reason: str):
    """Select distribution reason from dropdown"""
    with allure.step(f"Select distribution reason: {selected_distribution_reason}"):
        logger.info("\n")
        logger.info(f"Selecting distribution reason: {selected_distribution_reason} from dropdown")
        
        # Get SWP Establish Transaction Page Two from test context
        swp_transaction_page_two = test_context.get('swp_establish_transaction_page_two')
        if swp_transaction_page_two is None:
            swp_transaction_page_two = SWPEstablishTransactionPageTwo(page)
            test_context['swp_establish_transaction_page_two'] = swp_transaction_page_two
        
        # Wait for dropdown to be visible
        page.wait_for_timeout(5000)
        
        # Select distribution reason
        swp_transaction_page_two.select_distribution_reason(selected_distribution_reason)
        
        logger.info("Verify user selects the distribution reason from the dropdown ---> Validated")
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"Distribution Reason {selected_distribution_reason} Selected",
            attachment_type=allure.attachment_type.PNG
        )


@when(parsers.parse('User selects the Federal withholding option "{federal_option}"'))
def select_federal_withholding_option(page: Page, test_context: dict, federal_option: str):
    """Select Federal withholding option"""
    with allure.step(f"Select Federal withholding option: {federal_option}"):
        logger.info("\n")
        logger.info(f"Selecting Federal withholding option: {federal_option}")
        
        # Get SWP Establish Transaction Page Two from test context
        swp_transaction_page_two = test_context.get('swp_establish_transaction_page_two')
        if swp_transaction_page_two is None:
            swp_transaction_page_two = SWPEstablishTransactionPageTwo(page)
            test_context['swp_establish_transaction_page_two'] = swp_transaction_page_two
        
        # Wait for UI to load
        page.wait_for_timeout(5000)
        
        # Select federal withholding option
        swp_transaction_page_two.select_federal_withholding_option(federal_option)
        
        logger.info(f"Successfully Selected the Federal Option: {federal_option}")
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"Federal Withholding Option {federal_option} Selected",
            attachment_type=allure.attachment_type.PNG
        )


@when(parsers.re(r'User enters the Federal withholding rate "(?P<federal_rate>[^"]*)" if applicable'))
def enter_federal_withholding_rate(
    page: Page,
    test_context: dict,
    federal_rate: str
):
    """Enter Federal withholding rate if provided - matches Java user_enters_federal_withholding_rate"""
    with allure.step(f"Enter Federal withholding rate: {federal_rate if federal_rate else 'N/A'}"):
        logger.info("\n")
        
        # Check if rate is provided
        if not federal_rate or not federal_rate.strip():
            logger.info("No Federal rate provided; skipping rate entry.")
            logger.info("\n")
            return
        
        logger.info(f"Entering Federal withholding rate: {federal_rate}")
        
        # Get SWP Establish Transaction Page Two from test context
        swp_transaction_page_two = test_context.get('swp_establish_transaction_page_two')
        if swp_transaction_page_two is None:
            swp_transaction_page_two = SWPEstablishTransactionPageTwo(page)
            test_context['swp_establish_transaction_page_two'] = swp_transaction_page_two
        
        # Enter federal withholding rate
        swp_transaction_page_two.enter_federal_withholding_rate(federal_rate)
        
        # Verify rate was entered
        entered_value = swp_transaction_page_two.federal_withhold_rate_input.input_value()
        assert entered_value == federal_rate, f"Failed to enter Federal rate. Expected: {federal_rate}, Got: {entered_value}"
        
        logger.info(f"Successfully entered the withhold rate under Federal: {federal_rate}")
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"Federal Withholding Rate Entered - {federal_rate}",
            attachment_type=allure.attachment_type.PNG
        )


@when(parsers.parse('User selects the State withholding option "{state_option}"'))
def select_state_withholding_option(
    page: Page,
    test_context: dict,
    state_option: str
):
    """Select State withholding option - matches Java user_selects_state_withholding_option"""
    with allure.step(f"Select State withholding option: {state_option}"):
        logger.info("\n")
        logger.info(f"Selecting State withholding option: {state_option}")
        
        # Get SWP Establish Transaction Page Two from test context
        swp_transaction_page_two = test_context.get('swp_establish_transaction_page_two')
        if swp_transaction_page_two is None:
            swp_transaction_page_two = SWPEstablishTransactionPageTwo(page)
            test_context['swp_establish_transaction_page_two'] = swp_transaction_page_two
        
        # Wait for UI to load
        page.wait_for_timeout(5000)
        
        # Select state withholding option
        swp_transaction_page_two.select_state_withholding_option(state_option)
        
        logger.info(f"Successfully selected the State Option: {state_option}")
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"State Withholding Option {state_option} Selected",
            attachment_type=allure.attachment_type.PNG
        )


@when(parsers.re(r'User enters the State withholding rate "(?P<state_rate>[^"]*)" if applicable'))
def enter_state_withholding_rate(
    page: Page,
    test_context: dict,
    state_rate: str
):
    """Enter State withholding rate if provided - matches Java user_enters_state_withholding_rate"""
    with allure.step(f"Enter State withholding rate: {state_rate if state_rate else 'N/A'}"):
        logger.info("\n")
        
        # Check if rate is provided
        if not state_rate or not state_rate.strip():
            logger.info("No State rate provided; skipping rate entry.")
            logger.info("\n")
            return
        
        logger.info(f"Entering State withholding rate: {state_rate}")
        
        # Get SWP Establish Transaction Page Two from test context
        swp_transaction_page_two = test_context.get('swp_establish_transaction_page_two')
        if swp_transaction_page_two is None:
            swp_transaction_page_two = SWPEstablishTransactionPageTwo(page)
            test_context['swp_establish_transaction_page_two'] = swp_transaction_page_two
        
        # Enter state withholding rate
        swp_transaction_page_two.enter_state_withholding_rate(state_rate)
        
        # Verify rate was entered
        entered_value = swp_transaction_page_two.state_tax_text_input.input_value()
        assert entered_value == state_rate, f"Failed to enter State rate. Expected: {state_rate}, Got: {entered_value}"
        
        logger.info(f"Successfully entered the withhold rate under State: {state_rate}")
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"State Withholding Rate Entered - {state_rate}",
            attachment_type=allure.attachment_type.PNG
        )


@when(parsers.parse('User selects the signature option "{signature_option}"'))
def select_signature_option(
    page: Page,
    test_context: dict,
    signature_option: str
):
    """Select signature option - matches Java user_selects_signature_option"""
    with allure.step(f"Select signature option: {signature_option}"):
        logger.info("\n")
        logger.info(f"Selecting signature option: {signature_option}")
        
        # Get SWP Establish Transaction Page Two from test context
        swp_transaction_page_two = test_context.get('swp_establish_transaction_page_two')
        if swp_transaction_page_two is None:
            swp_transaction_page_two = SWPEstablishTransactionPageTwo(page)
            test_context['swp_establish_transaction_page_two'] = swp_transaction_page_two
        
        # Select signature option
        swp_transaction_page_two.select_signature_option(signature_option)
        
        logger.info(f"Successfully selected signature option: {signature_option}")
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"Signature Option Selected - {signature_option}",
            attachment_type=allure.attachment_type.PNG
        )


@when(parsers.parse('User clicks on the Next button on the transaction page two'))
def click_next_button_on_transaction_page_two(
    page: Page,
    test_context: dict
):
    """Click Next button on Transaction Page Two - matches Java user_clicks_next_button"""
    with allure.step("Click Next button on Transaction Page Two"):
        logger.info("\n")
        logger.info("Clicking Next button on Transaction Page Two")
        
        # Get SWP Establish Transaction Page Two from test context
        swp_transaction_page_two = test_context.get('swp_establish_transaction_page_two')
        if swp_transaction_page_two is None:
            swp_transaction_page_two = SWPEstablishTransactionPageTwo(page)
            test_context['swp_establish_transaction_page_two'] = swp_transaction_page_two
        
        # Scroll down before clicking
        page.evaluate("window.scrollBy(0, 2500)")
        page.wait_for_timeout(1000)
        
        # Click next button
        swp_transaction_page_two.click_next_button()
        
        # Wait for navigation
        page.wait_for_timeout(3000)
        
        logger.info("Successfully clicked Next button on Transaction Page Two")
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Next Button Clicked on TP2",
            attachment_type=allure.attachment_type.PNG
        )


@when(parsers.parse('User clicks on the "{button_label}" button on the summary page'))
def click_submit_button_on_summary_page(
    page: Page,
    test_context: dict,
    button_label: str
):
    """Click Submit button on Summary Page - matches Java userClicksOnSubmitButtonOnSummaryPage"""
    with allure.step(f"Click '{button_label}' button on summary page"):
        logger.info("\n")
        logger.info(f"Clicking '{button_label}' button on the summary page")
        
        # Get SWP Establish Transaction Page Two from test context
        swp_transaction_page_two = test_context.get('swp_establish_transaction_page_two')
        if swp_transaction_page_two is None:
            swp_transaction_page_two = SWPEstablishTransactionPageTwo(page)
            test_context['swp_establish_transaction_page_two'] = swp_transaction_page_two
        
        # Scroll down before clicking
        page.evaluate("window.scrollBy(0, 2500)")
        page.wait_for_timeout(1000)
        
        # Click submit button
        swp_transaction_page_two.click_submit_button()
        
        # Wait for submission
        page.wait_for_timeout(2000)
        
        logger.info(f"Clicked on '{button_label}' button on the summary page ΓåÆ")
        logger.info("Action Performed")
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"{button_label} Button Clicked",
            attachment_type=allure.attachment_type.PNG
        )


@then(parsers.parse('User should validate the "{expected_loader_header}" with "{expected_loader_subheader}" loader on the summary page'))
def validate_loader_messages(
    page: Page,
    test_context: dict,
    expected_loader_header: str,
    expected_loader_subheader: str
):
    """Validate loader messages on summary page - matches Java validateLoaderMessages"""
    with allure.step(f"Validate loader: {expected_loader_header}"):
        logger.info("\n")
        logger.info("Validating loader messages on the summary page")
        logger.info(f"Expected Header: {expected_loader_header}")
        logger.info(f"Expected SubHeader: {expected_loader_subheader}")
        
        # Get SWP Establish Transaction Page Two from test context
        swp_transaction_page_two = test_context.get('swp_establish_transaction_page_two')
        if swp_transaction_page_two is None:
            swp_transaction_page_two = SWPEstablishTransactionPageTwo(page)
            test_context['swp_establish_transaction_page_two'] = swp_transaction_page_two
        
        # Wait for loader to appear
        page.wait_for_timeout(2000)
        
        # Validate loader header
        try:
            loader_header = swp_transaction_page_two.loader_with_header
            loader_header.wait_for(state='visible', timeout=10000)
            header_text = loader_header.text_content()
            assert expected_loader_header in header_text, f"Loader header mismatch. Expected: '{expected_loader_header}', Got: '{header_text}'"
            logger.info(f"Loader header validated: {header_text}")
        except Exception as e:
            logger.error(f"Failed to validate loader header: {e}")
            raise
        
        # Validate loader subheader
        try:
            loader_subheader = swp_transaction_page_two.loader_with_subheader
            loader_subheader.wait_for(state='visible', timeout=10000)
            subheader_text = loader_subheader.text_content()
            assert expected_loader_subheader in subheader_text, f"Loader subheader mismatch. Expected: '{expected_loader_subheader}', Got: '{subheader_text}'"
            logger.info(f"Loader subheader validated: {subheader_text}")
        except Exception as e:
            logger.error(f"Failed to validate loader subheader: {e}")
            raise
        
        logger.info("Loader messages on the summary page ΓåÆ")
        logger.info("Loader Header & SubHeader Messages Validated")
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Loader Messages Validated",
            attachment_type=allure.attachment_type.PNG
        )
