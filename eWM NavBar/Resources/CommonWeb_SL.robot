*** Settings ***
Library      SeleniumLibrary
Variables    ../PO/Page_Locators.py

*** Keywords ***
Start eWM Test
    open browser      about:blank     ${BROWSER}    options=add_argument(--ignore-certificate-errors)
    maximize browser window

Access Test Environment URL
    go to                           ${URL}
    click button                    Allow All

Login to Test Environment
    input text                      ${UserName_TextBox}         ${USERNAME}
    input text                      ${Password_TextBox}         ${PASSWORD}
    click element                   ${Sign_Button}
    #sleep       2s

Login to Nav URL
    go to                           ${URL1}
    wait until element is enabled   ${Iframe}       20s
    select frame                    ${Iframe}

Logout from Test Environment
    wait until page contains        Logout      20s
    click link      Logout

End eWM Test
    close all browsers

Switch User
    [Arguments]                             ${user}
    wait until page contains                Switch ID       20s
    click link                              Switch ID
    wait until page contains element        ${Search_User_Inputbox}     20s
    click element                           ${Search_User_Inputbox}
    input text                              ${Search_User_Inputbox}     ${user}
    click element                           ${Find_Button}
    wait until page contains element        ${SSO_Link}     20s
    click element                           ${SSO_Link}
    sleep                                   1s
    capture page screenshot

Verify whether the Footer is available on the page
    scroll element into view                ${Footer}
    page should contain element             ${Footer}
    capture page screenshot