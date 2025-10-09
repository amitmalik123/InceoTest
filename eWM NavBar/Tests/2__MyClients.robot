*** Settings ***
Resource            ../Resources/eWMApp.robot
Variables           ../PO/Page_Locators.py
Suite Setup         Start eWM Test
#Suite Teardown     End eWM Test
Documentation       This suite tests the links available on 'My Clients' page on Chrome browser

*** Test Cases ***
TC#01: Verify user is landed on Client List page after clicking on 'My Clients' link
    [Documentation]     This test case verifies whethger user is landed on clients page
    [Tags]              Regression
    eWMApp.Access test environment and land on Homepage
    eWMApp.Verify user is landed on Client List page

TC#02: Verify 'My Clients' option on LHN pane is highlighted
    [Tags]              Regression
    eWMApp.Verify 'My Clients' option on LHN is highlighted

TC#03: Verify the footer is available on 'My Clients' page
    [Tags]              Regression
    eWMApp.Verify whether the Footer is available on the page

TC#04: Verify the links under 'Holdings' tab
    [Tags]              Smoke
    eWMApp.Access 'Holdings-All Holdings' page
    eWMApp.Access Holdings by Asset Class
    eWMApp.Verify 'Holdings' tab is highlighted

TC#05: Verify the links under 'Activity' tab
    [Tags]              Smoke
    eWMApp.Access 'Activity' page
    eWMApp.Verify 'Activity' tab is highlighted

TC#06: Verify the links under 'Performance' tab
    [Tags]              Smoke
    eWMApp.Access 'Performance-Account Performance' page
    eWMApp.Access 'Performance-Display Options' page
    eWMApp.Verify 'Performance' tab is highlighted

TC#07: Verify the links under 'Gain/Loss' tab
    [Tags]              Smoke
    eWMApp.Access 'Gain/Loss-Realized Gain/Loss' page
    eWMApp.Access 'Gain/Loss-Unrealized Gain/Loss' page
    eWMApp.Verify 'Gain/Loss' tab is highlighted

TC#08: Verify the links under 'Investment History' tab
    [Tags]              Smoke
    eWMApp.Access 'Investment History-Investment Change History' page
    eWMApp.Access 'Investment History-Historical Market Values' page
    eWMApp.Verify 'Investment History' tab is highlighted

TC#09: Verify the links under 'Account Information' tab
    [Tags]              Smoke
    eWMApp.Access 'Account Information' page
    eWMApp.Verify 'Account Information' tab is highlighted

TC#10: Verify the links under 'On-Demand Report' tab
    [Tags]              Smoke
    eWMApp.Access 'On-Demand Report' page
    eWMApp.Verify 'On-Demand Report' tab is highlighted

TC#11: Verify the links under 'Fees' tab
    [Tags]              Smoke
    eWMApp.Access 'Fees-Fee Schedules' page
    eWMApp.Access 'Fees-Change Your Financial Advisor Fee' page
    eWMApp.Access 'Fees-Fee Transactions' page
    eWMApp.Verify 'Fees' tab is highlighted


