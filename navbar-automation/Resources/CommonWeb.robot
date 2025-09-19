*** Settings ***
Library          Browser
Variables        ../PO/Locators.py

*** Keywords ***
Start eWM Test
    #Open Browser    about:blank    ${BROWSER}    headless=True    pause_on_failure=False
    New Browser    ${BROWSER}    headless=True    args=["--start-maximized"]
    New Context    ignoreHTTPSErrors=True     viewport=None
    New Page       about:blank
    

Access Test Environment URL
    go to                           ${URL}
    Scroll To Element               ${AllowAll_Button}
    Click                           ${AllowAll_Button}    left
    

Login to Test Environment
    Fill Text        ${UserName_TextBox}    ${USERNAME}    force=False
    Fill Text        ${Password_TextBox}    ${PASSWORD}
    Click            ${Sign_Button}    left
    Wait For Elements State       ${H1_Dashboard}    visible    20s
    Take Screenshot    embed=True
    # input text                      ${UserName_TextBox}         ${USERNAME}
    # input text                      ${Password_TextBox}         ${PASSWORD}
    # click element                   ${Sign_Button}
    # #sleep       2s

# Login to Nav URL
#     go to                           ${URL1}
#     wait until element is enabled   ${Iframe}       20s
#     select frame                    ${Iframe}

# Logout from Test Environment
#     wait until page contains        Logout      20s
#     click link      Logout

# End eWM Test
#     close all browsers

# Switch User
#     [Arguments]                             ${user}
#     wait until page contains                Switch ID       20s
#     click link                              Switch ID
#     wait until page contains element        ${Search_User_Inputbox}     20s
#     click element                           ${Search_User_Inputbox}
#     input text                              ${Search_User_Inputbox}     ${user}
#     click element                           ${Find_Button}
#     wait until page contains element        ${SSO_Link}     20s
#     click element                           ${SSO_Link}
#     sleep                                   1s
#     capture page screenshot

# Verify whether the Footer is available on the page
#     scroll element into view                ${Footer}
#     page should contain element             ${Footer}
#     capture page screenshot