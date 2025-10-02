*** Settings ***
Library        Browser
Variables      ../PageObjects/Locators.py



*** Keywords ***
Search User in Setup
    [Arguments]                ${username}
    Wait For Elements State    ${Search_Setup}    visible    timeout=50s
    Fill Text                  ${Search_Setup}    ${username}
    Press Keys                 ${Search_Setup}    Enter
    Wait For Elements State    ${Link_User}    visible    timeout=50s
    Click                      ${Link_User}
    Wait For Elements State    ${Heading_Users}    visible    timeout=50s

Login as User
    Set Selector Prefix        ${Frame_User}
    Wait For Elements State    ${Button_Login}    visible    timeout=50s
    Click                      ${Button_Login}    

    
    