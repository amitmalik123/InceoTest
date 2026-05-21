from pytest_bdd import parsers, then

from pages.ewm.account_approval_page import AccountApprovalPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@then("User clicks account approval tab")
def user_clicks_account_approval_tab(test_context):
    """Click the Account Approval tab in the main navigation menu."""
    admin_page = test_context["admin_page"]
    approval_page = AccountApprovalPage(admin_page)
    with logger.step("User clicks account approval tab", page=admin_page, screenshot=True):
        approval_page.click_account_approval_tab()


@then("User selects the client fullname and clicks on approval request")
def user_selects_client_fullname_and_clicks_approval(test_context):
    """Enter the client full name in the search field and click Go."""
    client_full_name = test_context.get("client_full_name", "")
    if not client_full_name:
        raise ValueError("client_full_name not found in test_context. Ensure the client profile step ran first.")
    admin_page = test_context["admin_page"]
    approval_page = AccountApprovalPage(admin_page)
    with logger.step("User selects client fullname and clicks approval request", page=admin_page, screenshot=True):
        approval_page.search_client_and_submit(client_full_name)


@then(parsers.parse('User "{action}" the account'))
def user_approves_or_rejects_account(action, test_context):
    """Approve, Reject, or Cancel the account, then switch back to agent tab."""
    admin_page = test_context["admin_page"]
    approval_page = AccountApprovalPage(admin_page)
    with logger.step(f"User {action} the account", page=admin_page, screenshot=True):
        approval_page.approve_or_reject_account(action)
        child_context = test_context.pop("admin_browser_context", None)
        test_context.pop("admin_page", None)
        approval_page.switch_to_parent_window(child_context)
