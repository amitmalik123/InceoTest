*** Settings ***
Library        Browser
Resource     ../Resources/CommonWeb.robot



*** Keywords ***
Navigate to Partial SBX
    Go To    ${Partial_SBX_URL}
    Click    ${Azure_Button}    left
    Sleep    15s
    Wait For Elements State    ${Button_SetupGear}    visible    timeout=50s
    Take Screenshot    embed=True

Navigate to Full SBX
    Go To    ${Full_SBX_URL}
    Wait For Elements State    ${Button_SetupGear}    visible    timeout=50s