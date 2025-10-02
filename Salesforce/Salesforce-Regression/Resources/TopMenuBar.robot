*** Settings ***
Library    Browser
Variables    ../PageObjects/Locators.py


*** Keywords ***
Click Set Up gear icon in Top Menu Bar
    Wait For Elements State    ${Button_SetupGear}    visible    timeout=20s
    Click            ${Button_SetupGear}
    Wait For Elements State    ${Option_Setup}    visible    timeout=20s
    Click            ${Option_Setup}
    Sleep            3s
    ${Windows} =     Get Page Ids
    Switch Page      ${Windows}[1]
    Switch Page      ${Windows}[0]
    Reload
    Wait For Elements State    ${Search_Setup}    visible    timeout=20s

    