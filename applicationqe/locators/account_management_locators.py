from typing import Dict

from playwright.sync_api import Locator, Page


def initialize_locators(page: Page) -> Dict[str, Locator]:
    return {
        "account_management_link": page.get_by_role(
            "link", name="Account Information change"
        ),
        "request_dropdown": page.locator("#ctl00_cphContentArea_ddlRequest"),
        "type_dropdown": page.locator("#ctl00_cphContentArea_ddlType"),
        "complete_and_print_button": page.get_by_role("button", name="Complete and Print"),
        "docusign_continue_button": page.get_by_role("button", name="Continue"),
        "docusign_finish_button": page.get_by_role("button", name="Finish"),
        "tracking_id_element": page.locator(
            "#trackingId, .tracking-id, [data-tracking-id]"
        ),
        "close_button": page.get_by_role("button", name="Close"),
        "upload_pdf_input": page.locator("input[type='file']"),
        "upload_button": page.get_by_role("button", name="Upload"),
    }
