"""Locators for Clients Page elements."""


class ClientsLocators:
    """Raw selector strings for the Clients page."""

    CLIENTS_LINK = "Clients"
    ACCOUNT_LIST_LINK = "Account List"
    ACCOUNTS_LINK_NEW_NAV = "Accounts"
    CLIENTS_TAB_LINK = "//*[@id='mainMenuWrapper']//li/a[@href='/AccountsAnalysis/Clients/ClientList']"
    LOADING_SPINNER = "#theLoadingImage"
    FIRST_RESULT_CLIENT_NAME = "//td[contains(@class,'clientName')]"
    CLIENT_INFO_TAB = "Client Information"
    MAILING_ADDRESS_SECTION = "//div[@aria-label='mailing-address-section'] | //section[contains(@class,'mailing-address')]"
