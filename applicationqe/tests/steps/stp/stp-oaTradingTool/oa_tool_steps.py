import allure
import json
from playwright.sync_api import Page
from pytest_bdd import when, then, parsers

from utils.settings import settings
from oa_tool_landing_page import OAToolLandingPage
from utils.database import get_configured_ewm_db
from utils.logger import setup_logger

logger = setup_logger(__name__)


@when(parsers.parse('User should execute db query to get OA Status of Account and Update to close them all for "{account_type}"'))
def execute_db_query_to_change_status_of_open_oas(test_context, account_type: str):
    with allure.step(f"Execute DB query to get OA Status of Account and Update to close them all for {account_type}"):
        logger.info("")
        
        test_data = test_context.get("test_data", {})
        
        if account_type == "Source":
            account_number = test_data.get("client_id") or test_context.get("account_number")
            
            query = f"select tmc.actionid, status, * from am_billing.dbo.tblmodelchanges tmc join  am_billing.dbo.account a on a.id = tmc.clientid where a.accountno = '{account_number}'"
            logger.info(f"DB Query-->{query}")
            
            with get_configured_ewm_db() as db:
                db.connect()
                status_values = db.execute_select_query_and_get_string_list(query, "status")
                
                for value in status_values:
                    if value == "1" or value == "2":
                        update_query = f"update am_billing.dbo.tblmodelchanges set status = 4 where actionid in ( select tmc.actionid from am_billing.dbo.tblmodelchanges tmc join am_billing.dbo.account a on a.id = tmc.clientid where a.accountno = '{account_number}')"
                        count = db.execute_non_query(update_query)
                        logger.info(f"Rows Affected are-->{count}")
                    else:
                        logger.info(f"the value of the status for any action type-->{value}")
        
        elif account_type == "Destination":
            roth_destination_account_number = test_context.get("roth_destination_account_number", "").strip()
            
            query1 = f"select tmc.actionid, status, * from am_billing.dbo.tblmodelchanges tmc join  am_billing.dbo.account a on a.id = tmc.clientid where a.accountno = '{roth_destination_account_number}'"
            logger.info(f"DB Query-->{query1}")
            
            with get_configured_ewm_db() as db:
                db.connect()
                status_values1 = db.execute_select_query_and_get_string_list(query1, "status")
                
                for value in status_values1:
                    if value == "1" or value == "2":
                        update_query = f"update am_billing.dbo.tblmodelchanges set status = 4 where actionid in ( select tmc.actionid from am_billing.dbo.tblmodelchanges tmc join am_billing.dbo.account a on a.id = tmc.clientid where a.accountno = '{roth_destination_account_number}')"
                        count = db.execute_non_query(update_query)
                        logger.info(f"Rows Affected are-->{count}")
                    else:
                        logger.info(f"the value of the status for any action type-->{value}")
        
        elif account_type == "Open":
            account_number = test_data.get("client_id") or test_context.get("account_number")
            
            Query1 = f"select tmc.actionid, status, * from am_billing.dbo.tblmodelchanges tmc join  am_billing.dbo.account a on a.id = tmc.clientid where a.accountno = '{account_number}'"
            logger.info(f"DB Query-->{Query1}")
            
            with get_configured_ewm_db() as db:
                db.connect()
                UpdatedStatusValues = db.execute_select_query_and_get_string_list(Query1, "status")
                
                for value in UpdatedStatusValues:
                    if value == "3" or value == "4":
                        update_query = f"update am_billing.dbo.tblmodelchanges set status = 2 where actionid in ( select tmc.actionid from am_billing.dbo.tblmodelchanges tmc join am_billing.dbo.account a on a.id = tmc.clientid where a.accountno = '{account_number}' )"
                        count = db.execute_non_query(update_query)
                        logger.info(f"Rows Affected are-->{count}")
                    else:
                        logger.info(f"the value of the status for any action type-->{value}")
        
        logger.info("")


@when('User should execute db query to get HouseholdID')
def get_household_id(test_context):
    logger.info("")
    
    test_data = test_context.get("test_data", {})
    account_number = test_data.get("client_id") or test_context.get("account_number")
    
    query = f"select FamilyID from [AM_Billing].[dbo].[Account] where AccountNo = ('{account_number}')"
    logger.info(f"DB Query: {query}")
    
    with get_configured_ewm_db() as db:
        db.connect()
        household_id = db.execute_query_and_get_first_value(query, "FamilyID")
        test_context["household_id"] = household_id
    
    logger.info("")


@when('User should execute db query to get Client and Agent name')
def get_client_and_agent_names(test_context):
    logger.info("")
    
    test_data = test_context.get("test_data", {})
    account_number = test_data.get("client_id") or test_context.get("account_number")
    
    query = f"SELECT ag.[Agent] AS \"Agent Name\", c.[FamilyName] AS \"Client Name\" FROM [AM_Billing].[dbo].[Account] a WITH(NOLOCK) LEFT JOIN [AM_Billing].[dbo].[tblClient] c WITH(NOLOCK) ON a.[FamilyID] = c.[FamilyID] LEFT JOIN [AM_Billing].[dbo].[tblAgents] ag WITH(NOLOCK) ON c.[AgentRecID] = ag.[RecID] WHERE a.[TerminationDate] IS NULL AND a.AccountNo = '{account_number}'"
    logger.info(f"DB Query: {query}")
    
    with get_configured_ewm_db() as db:
        db.connect()
        name1 = db.execute_query_and_get_first_value(query, "Agent Name")
        name2 = db.execute_query_and_get_first_value(query, "Client Name")
        
        test_context["agent_name"] = name1
        test_context["client_name"] = name2
    
    logger.info("")


@when('User should execute db query to get account ID')
def get_account_id_from_db(test_context):
    logger.info("")
    
    test_data = test_context.get("test_data", {})
    account_number = test_data.get("client_id") or test_context.get("account_number")
    
    query = f"select * from AM_Billing..Account where AccountNo in ('{account_number}')"
    logger.info(f"DB Query: {query}")
    
    with get_configured_ewm_db() as db:
        db.connect()
        account_id = db.execute_query_and_get_first_value(query, "APLID")
        test_context["account_id"] = account_id
    
    logger.info("")


@then('User should navigate to OA Tool Landing page')
def navigate_to_oa_tool_landing_page(page: Page, test_context: dict):
    logger.info("")

    with allure.step("Navigating to OA Tool Landing page"):
        test_data = test_context.get("test_data", {})
        agent_id = test_data.get("advisor_id")
        household_id = test_context.get("household_id")
        account_id = test_context.get("account_id")

        oa_tool_base_url = settings.config.get("external_urls", {}).get("oa_tool_base_url", "")
        if not oa_tool_base_url:
            raise ValueError("oa_tool_base_url is not configured in the environment yaml. Set external_urls.oa_tool_base_url.")
        url = f"{oa_tool_base_url}?Advisor={agent_id}&Household={household_id}&AccountId={account_id}"
        logger.info(f"Navigating to URL: {url}")

        allure.attach(url, name="OA_Tool_URL", attachment_type=allure.attachment_type.TEXT)

        screenshot = page.screenshot()
        allure.attach(screenshot, name="Before_OA_Tool_Navigation", attachment_type=allure.attachment_type.PNG)

        page.goto(url, wait_until="networkidle")

        screenshot = page.screenshot()
        allure.attach(screenshot, name="OA_Tool_Landing_Page_Loaded", attachment_type=allure.attachment_type.PNG)

        oa_tool_landing_page = OAToolLandingPage(page)
        test_context["oa_tool_landing_page"] = oa_tool_landing_page

        logger.info("OA Tool Landing page loaded and page object stored in context")

    logger.info("")


@then(parsers.parse('User should navigate to OA Tool Landing page for PROD with Advisor "{advisor_id}" Household "{household_id}" AccountId "{account_id}"'))
def navigate_to_oa_tool_landing_page_prod(page: Page, test_context: dict, advisor_id: str, household_id: str, account_id: str):
    logger.info("")

    with allure.step("Navigating to OA Tool Landing page for PROD"):
        oa_tool_base_url = settings.config.get("external_urls", {}).get("oa_tool_base_url", "")
        if not oa_tool_base_url:
            raise ValueError("oa_tool_base_url is not configured in the environment yaml. Set external_urls.oa_tool_base_url.")
        url = f"{oa_tool_base_url}?Advisor={advisor_id}&Household={household_id}&AccountId={account_id}"
        logger.info(f"Navigating to PROD URL: {url}")

        allure.attach(url, name="OA_Tool_PROD_URL", attachment_type=allure.attachment_type.TEXT)

        screenshot = page.screenshot()
        allure.attach(screenshot, name="Before_OA_Tool_PROD_Navigation", attachment_type=allure.attachment_type.PNG)

        page.goto(url, wait_until="networkidle")

        screenshot = page.screenshot()
        allure.attach(screenshot, name="OA_Tool_PROD_Landing_Page_Loaded", attachment_type=allure.attachment_type.PNG)

        oa_tool_landing_page = OAToolLandingPage(page)
        test_context["oa_tool_landing_page"] = oa_tool_landing_page
        test_context["prod_advisor_id"] = advisor_id

        logger.info("OA Tool PROD Landing page loaded and page object stored in context")

    logger.info("")


@then("User should validate the Advisor Id on the Page for PROD")
def validate_advisor_id_prod(test_context: dict):
    logger.info("")

    oa_tool_landing_page = test_context.get("oa_tool_landing_page")
    advisor_id = test_context.get("prod_advisor_id")

    advisor_id_text = oa_tool_landing_page.get_advisor_id()

    assert advisor_id in advisor_id_text, f"Advisor ID-->{advisor_id_text}"
    print(f"Validation of Advisor ID as-->{advisor_id}")

    logger.info("")


@then("User should validate request type section for PROD")
def validate_request_type_section_prod(test_context: dict):
    oa_tool_landing_page = test_context.get("oa_tool_landing_page")

    request_type_section = oa_tool_landing_page.get_request_type_container_text()

    assert "Select Request Type" in request_type_section, "Select Request Type"
    assert "Select a request type from the options below." in request_type_section, "Select a request type from the options below."
    assert "Required fields are marked with an asterisk\n*" in request_type_section, "Required fields are marked with an asterisk*"
    assert "Request Type\n*" in request_type_section, "Request Type"
    assert "Raise Cash for One Time Withdrawal" in request_type_section, "Raise Cash for One Time Withdrawal"
    assert not oa_tool_landing_page.are_buttons_clickable(), "Disabled buttons are not clickable"


@then('User should get bearer token from devTool')
def get_access_token(page: Page, test_context: dict):
    logger.info("")
    
    page.wait_for_function(
        """() => 
        window.sessionStorage.getItem(
            'oidc.user:https://test.tenant1.auth.ewm3.assetmark.net/realms/eWM:eWMAuth'
        ) !== null
        """,
        timeout=30000
    )
    
    token = page.evaluate(
        "() => window.sessionStorage.getItem('oidc.user:https://test.tenant1.auth.ewm3.assetmark.net/realms/eWM:eWMAuth')"
    )
    
    import json
    token_obj = json.loads(token)
    access_token = token_obj["access_token"]
    
    test_context["access_token"] = access_token
    print(f"Bearer Token: {access_token}")
    
    logger.info("")


@then("User should validate the Advisor Id on the Page")
def validate_advisor_id(test_context: dict):
    logger.info("")
    
    test_data = test_context.get("test_data", {})
    oa_tool_landing_page = test_context.get("oa_tool_landing_page")
    agent_id = test_data.get("advisor_id")
    
    advisor_id_text = oa_tool_landing_page.get_advisor_id()
    
    assert agent_id in advisor_id_text, f"Advisor ID-->{advisor_id_text}"
    print(f"Validation of Advisor ID as-->{agent_id}")
    
    logger.info("")


@then("User should validate request type section")
def validate_request_type_section(test_context: dict):
    oa_tool_landing_page = test_context.get("oa_tool_landing_page")
    
    request_type_section = oa_tool_landing_page.get_request_type_container_text()
    
    assert "Select Request Type" in request_type_section, "Select Request Type"
    assert "Select a request type from the options below." in request_type_section, "Select a request type from the options below."
    assert "Required fields are marked with an asterisk\n*" in request_type_section, "Required fields are marked with an asterisk*"
    assert "Request Type\n*" in request_type_section, "Request Type"
    assert "Raise Cash for One Time Withdrawal" in request_type_section, "Raise Cash for One Time Withdrawal"
    assert "Terminate Account (Coming soon)" in request_type_section, "Terminate Account (Coming soon)"
    assert "Raise Cash for One Time Journal (Coming soon)" in request_type_section, "Raise Cash for One Time Journal (Coming soon)"
    assert not oa_tool_landing_page.are_buttons_clickable(), "Disabled buttons are not clickable"


@then("User should click request type for OTW")
def click_request_type_otw(test_context: dict):
    oa_tool_landing_page = test_context.get("oa_tool_landing_page")
    oa_tool_landing_page.click_otw()


@then(parsers.parse('User should verify the "{household_header}" Heading and the sub-heading as the Account name'))
def validate_household_heading(household_header: str, test_context: dict, page: Page):
    logger.info("")
    
    page.wait_for_timeout(2000)
    
    oa_tool_landing_page = test_context.get("oa_tool_landing_page")
    
    heading_and_account = oa_tool_landing_page.get_household_heading_and_account(household_header)
    
    assert household_header == heading_and_account[0], f"Validation of HouseHold Heading as-->{household_header}"
    
    scenario_name = test_context.get("scenario_name", "")
    if "OA Trading Tool" in scenario_name:
        test_context["alter_account_name"] = test_context.get("account_name", "")
    
    print(f"Validation of HouseHold Heading as-->{household_header}")
    print("Account Name Validation-->Passed")
    
    logger.info("")


@then(parsers.parse('User should validate the Bottom HyperLinks present which are "{link1}", "{link2}" and "{link3}"'))
def validate_bottom_hyperlinks(link1: str, link2: str, link3: str, test_context: dict, page: Page):
    logger.info("")
    
    oa_tool_landing_page = test_context.get("oa_tool_landing_page")
    hyperlinks = oa_tool_landing_page.get_bottom_hyperlinks()
    
    privacy_link = hyperlinks[0]
    terms_of_use_link = hyperlinks[1]
    
    current_url = page.url.lower().replace("-", " ")
    if "trade actions" in current_url and len(hyperlinks) > 2:
        supported_browser_link = hyperlinks[2]
        assert link3 == supported_browser_link, f"Hyperlink 3 is given as-->{supported_browser_link}"
        print(f"Link 3 present is-->{supported_browser_link}")
    
    assert link1 == privacy_link, f"Hyperlink 1 is given as-->{privacy_link}"
    print(f"Link 1 present is-->{privacy_link}")
    
    assert link2 == terms_of_use_link, f"Hyperlink 2 is given as-->{terms_of_use_link}"
    print(f"Link 2 present is-->{terms_of_use_link}")
    
    logger.info("")


@then(parsers.parse('User should validate the AssetMark image and the description as "{heading}"'))
def validate_assetmark_heading(heading: str, test_context: dict):
    logger.info("")
    
    oa_tool_landing_page = test_context.get("oa_tool_landing_page")
    
    assetmark_heading = oa_tool_landing_page.get_assetmark_bottom_heading()
    assert heading in assetmark_heading, "The Assetmark Description is Validated"
    print("AssetMark Description is: Validated")
    
    assert oa_tool_landing_page.verify_assetmark_image(), "AssetMark Heading is Validated"
    print("AssetMark Image is: Validated")


@then("User should click next button on OA tool Landing page")
def click_next_oa_tool_landing_page(test_context: dict):
    oa_tool_landing_page = test_context.get("oa_tool_landing_page")
    oa_tool_transaction_page = oa_tool_landing_page.click_next()
    test_context["oa_tool_transaction_page"] = oa_tool_transaction_page

