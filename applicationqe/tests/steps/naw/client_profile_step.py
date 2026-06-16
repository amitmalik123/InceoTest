from playwright.sync_api import Page
from pytest_bdd import then, when

from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)

@when("User navigates to client profile page and enter required information")
def user_navigates_to_client_profile_and_enters_information(
    page: Page, client_profile_page, test_context
):
    """Navigate to client profile page and enter required information"""
    test_data = test_context["test_data"]

    client_type = test_data.get("ClientType", "")
    fiduciary_role = test_data.get("FiduciaryRole", "")
    risk_tolerance = test_data.get("RiskTolerance", "")
    investment_horizon = test_data.get("InvestmentHorizon", "")
    total_networth = test_data.get("TotalNetworth", "")
    risk_return_profile = test_data.get("RiskReturnProfile", "")

    if not client_type:
        raise ValueError(
            f"ClientType is missing in test data"
        )
 
    client_profile_page.client_Type(client_type)
    client_full_name = client_profile_page.fill_client_full_name(
        client_type, "Filling Client Full Name"
    )
    test_context["client_full_name"] = client_full_name
    
    # Select fiduciary role if provided
    if fiduciary_role:
        client_profile_page.select_fiduciary_role(fiduciary_role, "Fiduciary Role: ", "select fiduciary role")
    
    # Only select risk tolerance, investment horizon, and net worth if client type is NOT donor
    if "donor" not in client_type.lower():
        logger.info(f"Client type is {client_type} - Selecting risk profile details")
        if risk_tolerance:
            client_profile_page.select_client_risk_tolerance(
                client_type, risk_tolerance, "Select Risk Tolerance"
            )
        if investment_horizon:
            client_profile_page.select_client_investment_horizon(
                investment_horizon, "Select Investment Horizon"
            )
        if total_networth:
            client_profile_page.select_client_total_net_worth(
                total_networth, "Select Total Net Worth"
            )
    else:
        logger.info(f"Skipping risk profile selection for {client_type}")
    
    if risk_return_profile:
        client_profile_page.select_client_risk_profile(
            risk_return_profile, "Select Risk Profile"
        )

    
@then("User clicks on next button on client profile page")
def user_clicks_on_next_button(client_profile_page):
    """Click on next button to proceed from client profile page"""
    client_profile_page.click_next_button()
    logger.info("Successfully clicked next button")