from playwright.sync_api import Page, expect
from pytest_bdd import then, when

from pages import GlobalNavigationPage


@when("I navigate to the APro prospects page")
def navigate_to_apro_prospects(authenticated_page: Page):
    """Navigate to the APro prospects page via global navigation (constructs page object locally)."""
    gnav = GlobalNavigationPage(authenticated_page)
    gnav.click_menu_trigger()
    gnav.click_proposals_apro()


@then("I should see the APro prospects page")
def verify_apro_prospects_page(authenticated_page: Page):
    """Verify that the APro prospects page is displayed"""
    expect(authenticated_page.get_by_text("Prospects List")).to_be_visible()


@when('I search for client "{client_id}"')
def search_for_client(authenticated_page: Page, client_id: str):
    """Search for a client by client ID using the global search."""
    gnav = GlobalNavigationPage(authenticated_page)
    gnav.search(client_id)
