*** Settings ***
Library     SeleniumLibrary
Resource    ../Resources/CommonWeb.robot
Resource    ../Resources/HomePage.robot
Resource    ../Resources/MyClients.robot


*** Keywords ***
Login to Test Environment
   CommonWeb.Access Test Environment URL
   CommonWeb.Login to Test Environment

Login to Nav URL
    CommonWeb.Login to Nav URL

Logout from Test Environment
    CommonWeb.Logout from Test Environment

Change User
    CommonWeb.Switch User           ${USER}

Verify user is landed on Homepage
    HomePage.Verify Homepage is displayed

Verify 'My Practice' option on LHN is highlighted
    HomePage.Verify 'My Practice' option on LHN is highlighted

Verify user is landed on Client List page
    MyClients.Open My Clients page

Verify 'My Clients' option on LHN is highlighted
    MyClients.Verify 'My Clients' option is highlighted

Verify whether the Footer is available on the page
    CommonWeb.Verify whether the Footer is available on the page

Access test environment and land on Homepage
    Login to Test Environment
    Change User
    Login to Nav URL
    Verify user is landed on Homepage

Access 'Holdings-All Holdings' page
    MyClients.Access 'Holdings-All Holdings' page

Verify 'Holdings' tab is highlighted
    MyClients.Verify Holding tab is highlighted
    capture page screenshot

Access Holdings by Asset Class
    MyClients.Access 'Holdings by Asset Class' page

Access 'Activity' page
    MyClients.Access 'Activity' page

Verify 'Activity' tab is highlighted
    MyClients.Verify 'Activity' tab is highlighted
    capture page screenshot

Access 'Performance-Account Performance' page
    MyClients.Access 'Performance-Account Performance' page

Access 'Performance-Display Options' page
    MyClients.Access 'Performance-Display Options' page

Verify 'Performance' tab is highlighted
    MyClients.Verify 'Performance' tab is highlighted
    capture page screenshot

Access 'Gain/Loss-Realized Gain/Loss' page
    MyClients.Access 'Gain/Loss-Realized Gain/Loss' page

Access 'Gain/Loss-Unrealized Gain/Loss' page
    MyClients.Access 'Gain/Loss-Unrealized Gain/Loss' page

Verify 'Gain/Loss' tab is highlighted
    MyClients.Verify 'Gain/Loss' tab is highlighted
    capture page screenshot

Access 'Investment History-Investment Change History' page
    MyClients.Access 'Investment History-Investment Change History' page

Access 'Investment History-Historical Market Values' page
    MyClients.Access 'Investment History-Historical Market Values' page

Verify 'Investment History' tab is highlighted
    MyClients.Verify 'Investment History' tab is highlighted
    capture page screenshot

Access 'Account Information' page
    MyClients.Access 'Account Information' page

Verify 'Account Information' tab is highlighted
    MyClients.Verify 'Account Information' tab is highlighted
    capture page screenshot

Access 'On-Demand Report' page
    MyClients.Access 'On-Demand Report' page

Verify 'On-Demand Report' tab is highlighted
    MyClients.Verify 'On-Demand Report' tab is highlighted
    capture page screenshot

Access 'Fees-Fee Schedules' page
    MyClients.Access 'Fees-Fee Schedules' page

Access 'Fees-Change Your Financial Advisor Fee' page
    MyClients.Access 'Fees-Change Your Financial Advisor Fee' page

Access 'Fees-Fee Transactions' page
    MyClients.Access 'Fees-Fee Transactions' page

Verify 'Fees' tab is highlighted
    MyClients.Verify 'Fees' tab is highlighted
    capture page screenshot