"""Locators for BAW tracking center flows."""


class TrackingCenterLocators:
    TRACKING_CENTER_PATH = "AccountsAnalysis/TrackingCenter/TrackingCenter"
    ITEM_DETAIL_PATH = "AccountsAnalysis/TrackingCenter/TrackingCenterItemDetail"

    SEARCH_BOX = "#client_search_input"
    SEARCH_BUTTON = "#searchbutton"
    TRACKING_CENTER_GRID = "#TrackingCenterGrid"
    TRACKING_CENTER_ROWS = "#TrackingCenterGrid tr:has(td[aria-describedby])"

    WORK_ITEM_DESCRIPTION_LABEL = "xpath=//span[normalize-space(text())='Description:']/following-sibling::label"
    DETAIL_DESCRIPTIONS = "xpath=//*[@id='TrackingCenterItemDetailNotesGrid']/tbody/tr/td[4]"
    TRACKING_CENTER_TAB = "xpath=(//a[@id='ctl00_rItems_hLink_2'] | //a[normalize-space()='Tracking Center' and not(@id)] | //a[@id='header_0_content_0_rItems_hLink_2' and contains(normalize-space(),'Tracking Center')])[1]"
    ACTION_ITEMS_TAB = "a[href='/action-items']"

    SIGN_BUTTONS = "input[id^='btnSign']"
