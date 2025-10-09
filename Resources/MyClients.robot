*** Settings ***
Library    SeleniumLibrary
Variables    ../PO/Page_Locators.py


*** Keywords ***
Open My Clients page
    click link          My Clients
    sleep               1s
    select frame        ${Iframe_MyClients}
    page should contain link                Client List
    #wait until page contains element        ${Client_List_Breadcrum}        20s
    #page should contain element             ${Client_List_Breadcrum}
    element attribute value should be       ${Client_List_Link}         class       first selected${SPACE*1}



Verify 'My Clients' option is highlighted
    unselect frame
    wait until element is enabled           ${My_Clients_NavOption}         20s
    element attribute value should be       ${My_Clients_NavOption}         style       background-color: rgb(11, 100, 180); font-weight: 500; width: 208px; height: 40px; display: flex; align-items: center; padding: 22px 24px; border-radius: 8px;
    capture page screenshot

Access 'Holdings-All Holdings' page
    select frame                                ${Iframe_MyClients}
    wait until page contains element            ${Client_expand_arrow}      20s
    click element                               ${Client_expand_arrow}
    wait until page contains element            ${Client_Acct_Regis}        20s
    click element                               ${Client_Acct_Regis}
    page should contain                         ASSET CLASS

Verify Holding tab is highlighted
    select frame                                ${Iframe_MyClients}
    element attribute value should be           ${Holding_Tab}      class       first selected${SPACE*1}

Access 'Holdings by Asset Class' page
    select frame                                ${Iframe_MyClients}
    sleep                                       1s
    click link                                  Holdings by Asset Class
    page should contain                         Equity

Access 'Activity' page
    click link                                  Activity
    page should contain                         Total Items:

Verify 'Activity' tab is highlighted
    select frame                                ${Iframe_MyClients}
    element attribute value should be           ${Activity_Tab}      class       selected${SPACE*1}

Access 'Performance-Account Performance' page
    #select frame                                ${Iframe_MyClients}
    click link                                  Performance
    page should contain                         Select a date range to see performance

Access 'Performance-Display Options' page
    select frame                                ${Iframe_MyClients}
    sleep                                       3s
    click link                                  Display Options
    page should contain                         Please use the dropdown menus below to customize performance

Verify 'Performance' tab is highlighted
    select frame                                ${Iframe_MyClients}
    element attribute value should be           ${Performance_Tab}      class       selected${SPACE*1}

Access 'Gain/Loss-Realized Gain/Loss' page
    #wait until page contains element            ${Iframe_MyClients}         20s
    #select frame                                ${Iframe_MyClients}
    sleep                                       5s
    click link                                  Gain/Loss
    page should contain                         Accounting Method

Access 'Gain/Loss-Unrealized Gain/Loss' page
    select frame                                ${Iframe_MyClients}
    click link                                  Unrealized Gain/Loss
    page should contain                         For tax lot level detail, click Download

Verify 'Gain/Loss' tab is highlighted
    select frame                                ${Iframe_MyClients}
    element attribute value should be           ${GainLoss_Tab}      class       selected${SPACE*1}

Access 'Investment History-Investment Change History' page
    click link                                  Investment History
    page should contain                         Market Value Summary

Access 'Investment History-Historical Market Values' page
    select frame                                ${Iframe_MyClients}
    click link                                  Historical Market Values
    page should contain                         Market values at month end

Verify 'Investment History' tab is highlighted
    select frame                                ${Iframe_MyClients}
    element attribute value should be           ${InvHistory_Tab}      class       selected${SPACE*1}

Access 'Account Information' page
    click link                                  Account Information
    page should contain                         ACCOUNT DETAILS

Verify 'Account Information' tab is highlighted
    select frame                                ${Iframe_MyClients}
    element attribute value should be           ${AcctInfo_Tab}      class       selected${SPACE*1}

Access 'Fees-Fee Schedules' page
    click link                                  Fees
    page should contain                         Current Market Value

Access 'Fees-Change Your Financial Advisor Fee' page
    select frame                                ${Iframe_MyClients}
    click link                                  Change Your Financial Advisor Fee
    page should contain                         Change your Financial Advisor Fee

Access 'Fees-Fee Transactions' page
    select frame                                ${Iframe_MyClients}
    click link                                  Fee Transactions
    page should contain                         Total Items:

Verify 'Fees' tab is highlighted
    select frame                                ${Iframe_MyClients}
    element attribute value should be           ${Fees_Tab}      class       selected${SPACE*1}

Access 'On-Demand Report' page
    click link                                  On-Demand Report
    page should contain                         Customize Your On-Demand Report

Verify 'On-Demand Report' tab is highlighted
    select frame                                ${Iframe_MyClients}
    element attribute value should be           ${OndemandReport_Tab}      class       selected${SPACE*1}
