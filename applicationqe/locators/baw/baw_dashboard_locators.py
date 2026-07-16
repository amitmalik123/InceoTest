"""Locators for BAW dashboard workflows."""


class BawDashboardLocators:
    COACH_IFRAME = "//*[@data-viewid='CoachViewer']//iframe[@title]"
    DASHBOARD_IFRAME = "xpath=//iframe[@title='Dashboard']"

    OPEN_NEW_WORKITEM_BUTTON = "#ButtonGroup5_Button0"
    SEARCH_B_NUMBER_INPUT = "#txtBNum"
    SEARCH_BUTTON = "#ButtonGroup4_Search"
    TASK_TABLE = "#CustomHTML5 > table"
    TASK_TABLE_ROWS = "#TaskTable > tbody > tr"

    SHOW_MORE_LINK = "xpath=//a[contains(normalize-space(), 'Show more')]"
    MENU_LINK_BY_TITLE_XPATH = "//div[contains(@class,'menu_link')]//a[@title='{tab_name}']"
    DASHBOARD_LINK_XPATH = "//a[contains(text(),'Dashboard')]"
    SEARCH_B_NUMBER_ROLE = "B#:"
    SEARCH_BUTTON_ROLE = "Search"

    # Dashboard menu
    COLLAPSE_DASHBOARD_MENU = "#collapseDashboardsMenu"
    SEARCH_B_NUMBER_FALLBACK_XPATH = "xpath=//input[@id='txtBNum']"
    COACH_IFRAME_TITLE = 'iframe[title="Coach"]'

    # Run icon locators (dynamic templates use .format(b_tracking_id=...))
    RUN_ICON_BY_ONCLICK_TPL = "img[onclick*='{b_tracking_id}']"
    RUN_ICON_FALLBACK_XPATH_TPL = "xpath=//a[text()='{b_tracking_id}']//parent::td//preceding-sibling::td[3]"
    RUN_ICON_ROW_XPATH_TPL = "xpath=//tr[.//*[normalize-space(text())='{b_tracking_id}']]//td[1]//img"
    RUN_ICON_BROAD_ROW_XPATH_TPL = "xpath=//tr[.//*[normalize-space(text())='{b_tracking_id}']]//td[1]//*[self::img or self::button or @role='button' or contains(@class,'icon')]"
    RUN_ICON_FIRST_ROW_IMG = "#TaskTable > tbody > tr:first-child > td:first-child img"
    RUN_ICON_DEFAULT = "#TaskTable > tbody > tr > td > img"
    RUN_ICON_LAST_ROW_XPATH = "xpath=//table[@id='TaskTable']//tbody//tr[position() = (last() - 1)]/td/img"
