import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://test11.ewealthmanager.com/ewmLogin/account/login")
    page.get_by_role("button", name="Confirm My Choices").click()
    page.get_by_role("textbox", name="Username").click()
    page.get_by_role("textbox", name="Username").fill("SSOaaktan")
    page.get_by_role("textbox", name="Username").press("Tab")
    page.get_by_role("textbox", name="Password").fill("QAAdminUser_33a")
    page.get_by_role("textbox", name="Password").press("Enter")
    page.get_by_role("button", name="SIGN IN").click()
    page.locator("#radRoles_aaktan_3").check()
    page.get_by_role("button", name="Continue").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
