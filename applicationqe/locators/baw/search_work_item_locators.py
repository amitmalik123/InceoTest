"""Locators for BAW Search Work Item page."""


class SearchWorkItemLocators:
    COACH_FRAME = "iframe[title=\"Coach\"]"

    EXTERNAL_ID_TEXTBOX_ROLE = "External ID"
    SEARCH_BUTTON_ROLE = "Search"

    DETAILS_LINK = "xpath=//a[text()='Details' and not(@title)][1]"
    PARENT_B_NUMBER = "xpath=//div[@data-viewid='ParentBNumberCell' and starts-with(text(),'B')]"
    PARENT_B_NUMBER_CELL_ANY = "xpath=//div[@data-viewid='ParentBNumberCell']"
