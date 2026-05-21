from playwright.sync_api import Page
from pytest_bdd import when, then

from config.settings import get_settings
from utils.allure_logger import get_allure_logger
from utils.assertions import Assertions

logger = get_allure_logger(__name__)


class ConstructPortfolioStep:
    """Step class for Construct Portfolio functionality"""
    
    # Class-level variables
    tms = ""
    client_registration_type = ""
    registration_type = ""
    custodian = ""
    reg_type = ""
    investment_amount = ""
    account_type = ""
    investment_solution = ""
    account_number = ""
    private_asset_option = ""
    is_tms_eligible = False
    user_role = ""
    agent_channel = ""
    is_sub_advisory = "Non SubAdvisory"
    is_esignature_eligible = True
    agent_authorized_by = ""
    signed_by = ""
    w_number = ""

    def __init__(self, test_context: dict, page: Page = None):
        """Initialize with test context and page object"""
        self.test_data = test_context.get("test_data", {})
        self.page = page
        self.test_context = test_context

    def get_reg_type_and_custodian(self) -> None:
        """
        Extract registration type and custodian information from test data.
        Parses registration type split by comma and gets other portfolio details.
        """
        try:
            # Get registration type and split if multiple values
            reg_type_data = self.test_data.get("RegistrationType") or self.test_data.get(
                "registration_type", ""
            )
            reg_types = reg_type_data.split(",")
            
            if len(reg_types) <= 1:
                ConstructPortfolioStep.reg_type = reg_types[0].strip()
            else:
                ConstructPortfolioStep.reg_type = reg_types[1].strip()
            
            # Get custodian and other portfolio details
            ConstructPortfolioStep.custodian = self.test_data.get("Custodian") or self.test_data.get(
                "custodian", ""
            )
            ConstructPortfolioStep.account_number = self.test_data.get("AccountNumber") or self.test_data.get(
                "account_number", ""
            )
            ConstructPortfolioStep.client_registration_type = self.test_data.get(
                "ClientType"
            ) or self.test_data.get("client_type", "")
            ConstructPortfolioStep.investment_amount = self.test_data.get("Amount") or self.test_data.get(
                "amount", ""
            )
            ConstructPortfolioStep.account_type = self.test_data.get("ClientAccountType") or self.test_data.get(
                "account_type", ""
            )
            ConstructPortfolioStep.investment_solution = self.test_data.get(
                "InvestmentSolution"
            ) or self.test_data.get("investment_solution", "")
            ConstructPortfolioStep.private_asset_option = self.test_data.get(
                "PrivateAssetOption"
            ) or self.test_data.get("private_asset_option", "")
            
            logger.info(f"Registration Type: {ConstructPortfolioStep.reg_type}")
            logger.info(f"Custodian: {ConstructPortfolioStep.custodian}")
            logger.info(f"Client Registration Type: {ConstructPortfolioStep.client_registration_type}")
            logger.info(f"Investment Amount: {ConstructPortfolioStep.investment_amount}")
            logger.info(f"Account Type: {ConstructPortfolioStep.account_type}")
            logger.info(f"Investment Solution: {ConstructPortfolioStep.investment_solution}")
            
        except Exception as e:
            logger.error(f"Error retrieving registration type and custodian: {str(e).splitlines()[0]}")
            raise

    def agent_details(self, sheet_name: str) -> None:
        """
        Fetch agent details from Excel/test data and populate class variables.
        Reads whatever columns are available in the test data — no sheet-name gating.
        """
        try:
            # Always extract registration type and custodian if columns exist
            self.get_reg_type_and_custodian()

            user_name = self.test_data.get("UserName") or self.test_data.get("username", "")

            # IsSubAdvisory: Convert "0"/"1" to "Non SubAdvisory"/"SubAdvisory"
            is_sub_advisory_value = self.test_data.get("IsSubAdvisory", "0")
            if str(is_sub_advisory_value).strip() in ["1", 1, "True", True]:
                ConstructPortfolioStep.is_sub_advisory = "SubAdvisory"
            else:
                ConstructPortfolioStep.is_sub_advisory = "Non SubAdvisory"

            # UserRole
            ConstructPortfolioStep.user_role = (self.test_data.get("UserRole", "") or "").strip()

            # AgentChannel: validate against allowed values
            agent_channel_value = (self.test_data.get("AgentChannel", "") or "").strip()
            ConstructPortfolioStep.agent_channel = agent_channel_value if agent_channel_value in ["ADG", "IPG"] else "Blank"

            # IsEsignatureEligible: Convert "0"/"1" to False/True
            esignature_value = self.test_data.get("IsEsignatureEligible", "0")
            ConstructPortfolioStep.is_esignature_eligible = str(esignature_value).strip() in ["1", 1, "True", True]

            # SignedBy
            ConstructPortfolioStep.signed_by = (self.test_data.get("SignedBy", "") or "").strip()

            # AuthorizedBy
            ConstructPortfolioStep.agent_authorized_by = (self.test_data.get("AuthorizedBy", "") or "").strip()

            # Log all fetched data
            log_details = {
                "<b>Username</b>": user_name,
                "<b>Role</b>": ConstructPortfolioStep.user_role,
                "<b>Channel</b>": ConstructPortfolioStep.agent_channel,
                "<b>Advisory Type</b>": ConstructPortfolioStep.is_sub_advisory,
                "<b>eSign Eligible</b>": str(ConstructPortfolioStep.is_esignature_eligible),
                "<b>Agent Authorized By Name</b>": ConstructPortfolioStep.agent_authorized_by,
                "<b>Agent Signed By Name</b>": ConstructPortfolioStep.signed_by,
            }

            logger.info("Agent Details from Excel Sheet:")
            for key, value in log_details.items():
                logger.info(f"  {key}: {value}")

            logger.info("Agent details loaded from Excel sheet successfully")

        except Exception as e:
            logger.error(f"Error loading agent details: {str(e).splitlines()[0]}")
            # Don't raise - allow tests to continue even if agent details are missing
            logger.warning("Continuing test execution despite agent details load failure")
        



@when("User navigates to Construct portfolio page and enter required information")
def user_navigates_to_construct_portfolio_page(
    page: Page, construct_portfolio_page, test_context, _pytest_bdd_example
):
    """Navigate to construct portfolio page and enter required information"""
    # Wait for page to navigate to Construct Portfolio URL
    try:
        page.wait_for_url("**/Portfolio/Construct**", timeout=30000)
    except Exception:
        logger.warning(f"Construct portfolio URL not reached, current URL: {page.url}")
    logger.info("Construct portfolio page loaded")
    
    # Initialize step helper and get portfolio configuration
    portfolio_step = ConstructPortfolioStep(test_context)
    
    # Fetch agent details from database (similar to Java's agentDetails() call)
    # Get sheet name from scenario Examples table
    sheet_name = _pytest_bdd_example.get("SheetName", "NAW")
    portfolio_step.agent_details(sheet_name)
    
    # Close any chat popups that may have appeared during DB queries / page load
    construct_portfolio_page.close_chat_popups()

    # Get client registration type and TMS value
    client_registration_type = portfolio_step.test_data.get("ClientType") or portfolio_step.test_data.get(
        "client_type", ""
    )
    tms = portfolio_step.test_data.get("TMS") or portfolio_step.test_data.get("tms", "")
    
    logger.info(f"Client Registration Type: {client_registration_type}")
    logger.info(f"TMS: {tms}")
    
    registration_type = portfolio_step.test_data.get("RegistrationType") or portfolio_step.test_data.get(
        "registration_type", ""
    )
    
    logger.info(f"Investment solution: {portfolio_step.investment_solution}")
    ConstructPortfolioStep.tms = tms
    
    # Select registration type if not donor advised
    if "donor advised" not in client_registration_type.lower():
        logger.info(f"Selecting registration type: {registration_type}")
        construct_portfolio_page.select_client_registration_type(
            registration_type, 
            "Registration type: ", 
            f"Select registration type: {registration_type}"
        )
    else:
        logger.info(f"Skipping registration type selection for {client_registration_type}")
    
    # Select custodian
    logger.info(f"Selecting custodian: {portfolio_step.custodian}")
    construct_portfolio_page.select_client_custodian(
        client_registration_type,
        portfolio_step.custodian,
        "Select client custodian",
        f"Select custodian type: {portfolio_step.custodian}"
    )
    
    # Insert investment amount
    construct_portfolio_page.insert_investment_amount(
        portfolio_step.investment_amount,
        "Entering client investment amount",
        f"enter investment amount: {portfolio_step.investment_amount}"
    )
    
    # Select account type
    logger.info(f"Selecting account type: {portfolio_step.account_type}")
    construct_portfolio_page.select_account_type(
        portfolio_step.account_type,
        "Entering client amount type",
        f"select account type {portfolio_step.account_type}"
    )
    
    # Choose investment from modal
    logger.info(f"Selecting investment solution: {portfolio_step.investment_solution}")
    construct_portfolio_page.choose_new_investment_from_modal(
        portfolio_step.investment_solution,
        "Selecting new investment in modal window",
        f"select new investment: {portfolio_step.investment_solution}",
        portfolio_step.account_type,
        portfolio_step.private_asset_option
    )


@then("User clicks on next button on construct portfolio page")
def user_clicks_on_next_button_on_construct_portfolio_page(page: Page, construct_portfolio_page, test_context):
    """Click on next button on construct portfolio page and handle TMS logic"""
    logger.info("User clicks on next button on construct portfolio page")
    # Get test data and portfolio details
    test_data = test_context.get("test_data", {})
    portfolio_step = ConstructPortfolioStep(test_context)
    
    # Extract registration type and custodian
    portfolio_step.get_reg_type_and_custodian()
    
    # Get portfolio values
    tms = test_data.get("TMS", "").strip()
    account_type = test_data.get("ClientAccountType", "").strip()
    investment_solution = test_data.get("InvestmentSolution", "").strip()
    custodian = portfolio_step.custodian
    reg_type = portfolio_step.reg_type
    
    logger.info(f"TMS: {tms}, Account Type: {account_type}, Investment Solution: {investment_solution}")
    
    # Check TMS eligibility conditions
    is_tms_eligible = (
        tms.lower() in ["yes", "1"] or 
        ("Savos Personal Portfolio Custom" in account_type and "TMS" in investment_solution)
    )
    ConstructPortfolioStep.is_tms_eligible = is_tms_eligible
    
    try:
        if is_tms_eligible:
            logger.info("TMS is eligible - executing TMS workflow")
            
            # Select TMS option
            construct_portfolio_page.select_tms_option("Yes")
            logger.info("Selected TMS option: Yes")
            
            # Confirm single strategy investment
            construct_portfolio_page.confirm_single_strategy_investment()
            logger.info("Confirmed single strategy investment")
            
            # Choose TMS tax sensitivity
            
            construct_portfolio_page.choose_tms_tax_sensitivity()
            logger.info("Chose TMS tax sensitivity")
            
            # Verify summary table - do not remove this
            #construct_portfolio_page.verify_summary_table(custodian, account_type, reg_type, investment_solution)
            #logger.info("Verified summary table")

            # Click next button
            construct_portfolio_page.click_next_button()
            logger.info("Clicked next button")

            # Handle portfolio suitability popup
            if custodian == "AssetMark Trust" and "Individual" in reg_type:
                construct_portfolio_page.handle_client_portfolio_suitability_popup()
                logger.info("Handled portfolio suitability popup")

        
        else:
            logger.info("TMS is not eligible - executing standard workflow")

            # Confirm client portfolio
            construct_portfolio_page.confirm_client_portfolio(custodian, account_type, reg_type, investment_solution)
            logger.info("Confirmed client portfolio")

            # Choose TMS tax sensitivity (may be applicable in some scenarios)
            # if not (custodian == "Fidelity" and "Trust" in reg_type) and \
            #    not (custodian == "Pershing Advisor Solutions" and "Beneficiary Roth IRA Trust" in reg_type) and \
            #    not (custodian == "Schwab Direct" and "Beneficiary Roth IRA Individual" in reg_type):
            #     construct_portfolio_page.choose_tms_tax_sensitivity()
            # logger.info("Chose TMS tax sensitivity")

            # Verify summary table - do not remove this
            #construct_portfolio_page.verify_summary_table(custodian, account_type, reg_type, investment_solution)
            #logger.info("Verified summary table")

            # Click next button
            construct_portfolio_page.click_next_button()
            logger.info("Clicked next button")

            # Handle portfolio suitability popup
            if (custodian == "Schwab" and "Self-Directed Brokerage Account - 403(b)" in reg_type) or \
               (custodian == "Pershing Advisor Solutions" and "Beneficiary Roth IRA Trust" in reg_type):
                construct_portfolio_page.handle_client_portfolio_suitability_popup()
                logger.info("Handled portfolio suitability popup")
        
        logger.info("Successfully completed construct portfolio page next button workflow")
        
    except Exception as e:
        logger.error(f"Failed during construct portfolio page next button workflow: {str(e).splitlines()[0]}")
        raise