from pytest_bdd import when


@when("User is on Account Wizard tab and click on go button for New Client creation")
def user_navigate_to_account_wizard_and_click_go_button_for_new_client_creation(account_wizard_page):
    """Navigate to Account Wizard and click Go button for New Client creation"""
    account_wizard_page.click_Go_Button()
