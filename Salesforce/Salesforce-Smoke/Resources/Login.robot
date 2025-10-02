*** Settings ***
Library          Browser
Resource         ../Resources/CommonWeb.robot
Variables        ../PageObjects/Locators.py



*** Keywords ***
Navigate to Partial SBX
    [Arguments]        ${UserName}    ${Password}
    Go To        ${Partial_SBX_URL}
    Wait For Elements State    ${TextBox_UserName}    visible    timeout=50s
    Fill Text    ${TextBox_UserName}    ${Username}
    Fill Text    ${TextBox_Password}    ${Password}
    Click        ${SignIn}    left
#    Click    ${Azure_Button}    left
#    Sleep    15s
    Wait For Elements State    ${Button_SetupGear}    visible    timeout=50s
#    Take Screenshot    embed=True

Navigate to Full SBX
    Go To    ${Full_SBX_URL}
    Wait For Elements State    ${Button_SetupGear}    visible    timeout=50s