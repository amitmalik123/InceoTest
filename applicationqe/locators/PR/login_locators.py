from typing import Dict

from playwright.sync_api import Locator, Page


def initialize_locators(page: Page) -> Dict[str, Locator]:
    return {
        "allow_all_button": page.get_by_role("button", name="Allow All"),
        "username_input_field": page.get_by_label("Username"),
        "password_input_field": page.get_by_label("Password"),
        "sign_in_button": page.get_by_role("button", name="SIGN IN"),
        "login_form": page.locator("form#form19.primary-auth-form.o-form.o-form-edit-mode"),
    }
