*** Settings ***
Library    SeleniumLibrary
Variables    ../PO/Page_Locators.py


*** Keywords ***
Verify Homepage is displayed
    wait until page contains        Making Awareness Month Campaigns a Win-Win-Win
    page should contain             Making Awareness Month Campaigns a Win-Win-Win


Verify 'My Practice' option on LHN is highlighted
    #get element attribute       ${My_Practice_NavOption}
    element attribute value should be       ${My_Practice_NavOption}        style       background-color: rgb(11, 100, 180); font-weight: 500; width: 80%;
    capture page screenshot
