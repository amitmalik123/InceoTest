from playwright.sync_api import Page
from pytest_bdd import parsers, when

from pages.baw.naa_coach_page import NAACoachPage
from pages.tracking_center_page import TrackingCenterPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@when(parsers.parse('User search item number and fetch description "{phase}"'))
def user_search_item_number_and_fetch_description(tracking_center_page, test_context, phase):
    """Search item in tracking center and capture item/work descriptions.
    phase='before activation' — existing search + fetch logic.
    phase='after activation'  — same search + Item Detail validation."""
    with logger.step(
        f"User search item number and fetch description '{phase}'",
        page=tracking_center_page.page,
        screenshot=True,
    ):
        search_text = test_context.get("client_full_name")
        if not search_text:
            raise ValueError("client_full_name not found in test_context")

        logger.info(f"Searching for item number/text: {search_text}")
        item_number = tracking_center_page.search_for_item_number(str(search_text).strip())
        test_context["tracking_item_number"] = item_number
        logger.info(f"Item Number Is - {item_number}")

        if phase == "before activation":
            work_item_description = tracking_center_page.get_work_item_description()
            description = tracking_center_page.fetch_description()
            test_context["tracking_work_item_description"] = work_item_description
            test_context["tracking_descriptions"] = description
            logger.info(f"Fetched Description(s)\n{description}")

        elif phase == "after activation":
            parent_b_number = test_context.get("parent_b_number") or test_context.get("b_tracking_id")
            if not parent_b_number:
                raise ValueError("parent_b_number / b_tracking_id not found in test_context")

            test_data = test_context.get("test_data", {})
            account_activation = (test_data.get("AccountActivation", "") or "").strip().lower()

            if account_activation == "no":
                activated_account = ""
                logger.info("AccountActivation is 'no', skipping activated account number validation", attach_to_allure=True)
            else:
                activated_account = NAACoachPage.activated_account_number
                if not activated_account:
                    raise ValueError("NAACoachPage.activated_account_number is empty — activation may have failed")

            logger.info(f"Parent B Number: {parent_b_number}")
            tracking_center_page.navigate_to_item_detail(parent_b_number)
            result = tracking_center_page.validate_item_detail(
                parent_b_number, activated_account
            )

            test_context["tc_item_number"] = result["item_number"]
            test_context["tc_description"] = result["description"]
            test_context["tc_account_number"] = result["account_number"]
            logger.attach_summary_table({
                "Username": test_data.get("UserName") or test_data.get("username", ""),
                "Client Full Name": test_context.get("client_full_name", ""),
                "Item Number": result["item_number"],
                "Description": result["description"],
                "Account Number": result["account_number"],
                "Parent B Number": parent_b_number,
                "Activated Account": activated_account or "N/A",
            }, name="Tracking Center - After Activation")

        # --- Conditional description validations (both phases) ---
        test_data = test_context.get("test_data", {})

        esignature_option = test_data.get("ESignatureOption", "")
        if esignature_option == "yes":
            logger.info("ESignatureOption is 'yes' — validating eSignature description")
            tracking_center_page.validate_description_text(
                "Document has been completed by all signers",
                f"ESignature_Description_{phase.replace(' ', '_')}",
            )

        bd_approval = test_data.get("BDApproval", "")
        if bd_approval == "yes":
            logger.info("BDApproval is 'yes' — validating BD Approval description")
            tracking_center_page.validate_description_text(
                "Document approved by Broker Dealer",
                f"BD_Approval_Description_{phase.replace(' ', '_')}",
            )


@when("User navigates to tracking center and searches item number")
def step_search_tracking_center_new_context(test_context):
    """Navigate to Tracking Center on the new context page and search by client name."""
    logger.info("[STEP] User navigates to tracking center and searches item number - BEGIN")

    new_page = test_context.get("new_page")
    if not new_page:
        raise RuntimeError("[tracking-ctx] new_page not found. Run 'User logs in as agent in a new browser context' first.")

    search_text = test_context.get("client_full_name")
    if not search_text:
        raise ValueError("[tracking-ctx] client_full_name not found in test_context")

    tracking_center_page = TrackingCenterPage(new_page)
    tracking_center_page.click_tracking_center_tab()

    with logger.step("Search item in tracking center (new context)", page=new_page, screenshot=True):
        logger.info(f"[tracking-ctx] Searching tracking center for: {search_text}")
        item_number = tracking_center_page.search_for_item_number(str(search_text).strip())
        test_context["tracking_item_number"] = item_number
        logger.info(f"[tracking-ctx] Item Number: {item_number}")

    logger.info("[STEP] User navigates to tracking center and searches item number - END")

