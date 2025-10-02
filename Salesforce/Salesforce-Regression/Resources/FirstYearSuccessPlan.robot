*** Settings ***
Library    Browser
Variables    ../PageObjects/Locators.py


*** Keywords ***
Search NPA Contact
    [Arguments]    ${NPA_Contact}
    Set Selector Prefix        ${None}
    Wait For Elements State    ${Button_Global_SearchBox}    visible    timeout=20s
    Click            ${Button_Global_SearchBox}
    Fill Text       ${Search_Box_Global}    ${NPA_Contact}
    Wait For Elements State    ${Option_ContactName}    visible    timeout=20s
    Click            ${Option_ContactName}
    Wait For Elements State    ${Label_FullName}    visible    timeout=20s
    Reload


Search Non-NPA Contact
    [Arguments]    ${Non_NPA_Contact}
    Reload
    Wait For Elements State    ${Button_Global_SearchBox}    visible    timeout=20s
    Click            ${Button_Global_SearchBox}
    Fill Text       ${Search_Box_Global}    ${Non_NPA_Contact}
    Wait For Elements State    ${Option_ContactName}    visible    timeout=20s
    Click            ${Option_ContactName}
    Wait For Elements State    ${Label_FullName}    visible    timeout=20s
    Reload


Navigate to First Year Success Plan Page
    Wait For Elements State    ${Button_SuccessPlan}    visible    timeout=20s
    Click    ${Button_SuccessPlan}
    Wait For Elements State    ${Heading_SuccessPlan}    visible    timeout=20s
    Get Text    ${Heading_SuccessPlan}    ==    Create Success Plan


Verify Success Plan screen
    Get Text    ${Heading_SuccessPlan}    ==    Create Success Plan
    Get Text    ${Label_Advisor}  ==  Advisor: Logan Marcus
    Get Text    ${Label_Expected_AUM_Field}  ==  Expected AUM Commitment 12 Months
    Get Text    ${Label_Advisor_Accomplish_Field}  ==  What does this advisor want to accomplish working with AssetMark?
    Get Text    ${Button_Next}    ==    Next


Verify The Message For AUM < 5mn
    Fill Text    ${Text_Box_Expected_AUM_Field}    {None}
    Fill Text    ${Text_Box_Expected_AUM_Field}    4000000
    Fill Text    ${Text_Box_Advisor_Accomplish_Field}    Test AUM less than 5mn
    Click    ${Button_Next}
    Wait For Elements State    ${Message_AUM_Less_Than_5mn}    visible    timeout=20s
    Get Text    ${Message_AUM_Less_Than_5mn}    ==    A Success Plan is not needed for this level of engagement. Continue to use the Opportunity to support your sales process.
    Click    ${Button_Previous}


Verify The Tasks For 5mn < AUM < 15mn
    Fill Text    ${Text_Box_Expected_AUM_Field}    {None}
    Fill Text    ${Text_Box_Expected_AUM_Field}    14999999
    Fill Text    ${Text_Box_Advisor_Accomplish_Field}    Test AUM between 5mn and 15mn
    Click    ${Button_Next}
    Wait For Elements State    ${Table_Default_Tasks}    visible    timeout=20s
    ${table1} =      Set Variable    ${Table_Default_Tasks}
    ${Value1.1} =     Get Table Cell Element    ${table1}    0    1
    Get Text    ${Value1.1}    ==    First-Year Success
    ${table2} =      Set Variable    ${Table_Optional_Tasks}
    ${Value2.1} =     Get Table Cell Element    ${table2}    1    1
    ${Value2.2} =     Get Table Cell Element    ${table2}    1    2
    ${Value2.3} =     Get Table Cell Element    ${table2}    1    3
    Get Text    ${Value2.1}    ==    Retirement Services
    Get Text    ${Value2.2}    ==    Business Consulting
    Get Text    ${Value2.3}    ==    Transition Team
    Click    ${Button_Previous}

Verify The Tasks For 15mn < AUM < 25mn
    Fill Text    ${Text_Box_Expected_AUM_Field}    {None}
    Fill Text    ${Text_Box_Expected_AUM_Field}    15000000
    Fill Text    ${Text_Box_Advisor_Accomplish_Field}    Test AUM between 15mn and 25mn
    Click    ${Button_Next}
    Wait For Elements State    ${Table_Default_Tasks}    visible    timeout=20s
    ${table1} =      Set Variable    ${Table_Default_Tasks}
    ${Value1.1} =     Get Table Cell Element    ${table1}    0    1
    ${Value1.2} =     Get Table Cell Element    ${table1}    0    2
    Get Text    ${Value1.1}    ==    First-Year Success
    Get Text    ${Value1.2}    ==    Business Consulting
    ${table2} =      Set Variable    ${Table_Optional_Tasks}
    ${Value2.1} =     Get Table Cell Element    ${table2}    1    1
    ${Value2.2} =     Get Table Cell Element    ${table2}    1    2
    ${Value2.3} =     Get Table Cell Element    ${table2}    1    3
    Get Text    ${Value2.1}    ==    Retirement Services
    Get Text    ${Value2.2}    ==    Transition Team
    Get Text    ${Value2.3}    ==    Investment Consulting
    Click    ${Button_Previous}


Verify The Tasks For AUM > 25mn
    Fill Text    ${Text_Box_Expected_AUM_Field}    {None}
    Fill Text    ${Text_Box_Expected_AUM_Field}    25000001
    Fill Text    ${Text_Box_Advisor_Accomplish_Field}    Test AUM between greater than 25mn
    Click    ${Button_Next}
    Wait For Elements State    ${Table_Default_Tasks}    visible    timeout=20s
    ${table1} =      Set Variable    ${Table_Default_Tasks}
    ${Value1.1} =     Get Table Cell Element    ${table1}    0    1
    ${Value1.2} =     Get Table Cell Element    ${table1}    0    2
    Get Text    ${Value1.1}    ==    First-Year Success
    Get Text    ${Value1.2}    ==    Business Consulting
    ${table2} =      Set Variable    ${Table_Optional_Tasks}
    ${Value2.1} =     Get Table Cell Element    ${table2}    1    1
    ${Value2.2} =     Get Table Cell Element    ${table2}    1    2
    ${Value2.3} =     Get Table Cell Element    ${table2}    1    3
    Get Text    ${Value2.1}    ==    Retirement Services
    Get Text    ${Value2.2}    ==    Investment Consulting
    Get Text    ${Value2.3}    ==    Implementation Manager
    Click    ${Button_Previous}


Verify The Tasks For AUM > 5mn for Non-NPA Eligible Contact
    Fill Text    ${Text_Box_Expected_AUM_Field}    {None}
    Fill Text    ${Text_Box_Expected_AUM_Field}    5000001
    Fill Text    ${Text_Box_Advisor_Accomplish_Field}    Test AUM greater than 5mn for Non NPA Eligible Contact
    Click    ${Button_Next}
    Wait For Elements State    ${Table_Non_NPA_Tasks}    visible    timeout=20s
    ${table} =      Set Variable    ${Table_Non_NPA_Tasks}
    ${Value1} =     Get Table Cell Element    ${table}    1    1
    ${Value2} =     Get Table Cell Element    ${table}    1    2
    Get Text    ${Value1}    ==    First-Year Success
    Get Text    ${Value2}    ==    Transition Team
    Click    ${Button_Previous}
    Wait For Elements State    ${Error_Message}    visible    timeout=20s
    Get Text    ${Error_Message}    ==    Please select minimum 1 rows
    Check Checkbox    ${Checkbox_Task_Option}
    Click    ${Button_Submit}


Create Success Plan for Non-NPA Eligible advisor
    Wait For Elements State    ${TextBox_FirstYearSuccessGoal}    visible    timeout=20s
    Fill Text    ${TextBox_FirstYearSuccessGoal}    Test
    Fill Text    ${TextBox_PrimaryReasonForAMK}    Test
    Fill Text    ${TextBox_PotentialImpediments}    Test
    Fill Text    ${TextBox_WhatValuesDrive}    Test
    Fill Text    ${TextBox_WhatImpOutsideWork}    Test
    Fill Text    ${TextBox_InvPhilosophy}    Test
    Fill Text    ${TextBox_PracticeandOperInfo}    Test
    Click        ${Button_Finish}
    Wait For Condition              title    ==   Steve D. Lindberg - Success Plan | TaskRay Project | Salesforce      timeout=50s


Create Success Plan for NPA Eligible advisor
    Fill Text    ${Text_Box_Expected_AUM_Field}    {None}
    Fill Text    ${Text_Box_Expected_AUM_Field}    15000000
    Fill Text    ${Text_Box_Advisor_Accomplish_Field}    Test AUM between 15mn and 25mn
    Click    ${Button_Next}
    Wait For Elements State    ${Table_Default_Tasks}    visible    timeout=20s
    Click    ${Button_Submit}
    Wait For Elements State    ${TextBox_FirstYearSuccessGoal}    visible    timeout=20s
    Fill Text    ${TextBox_FirstYearSuccessGoal}    Test
    Fill Text    ${TextBox_PrimaryReasonForAMK}    Test
    Fill Text    ${TextBox_PotentialImpediments}    Test
    Fill Text    ${TextBox_WhatValuesDrive}    Test
    Fill Text    ${TextBox_WhatImpOutsideWork}    Test
    Fill Text    ${TextBox_InvPhilosophy}    Test
    Fill Text    ${TextBox_PracticeandOperInfo}    Test
    Click        ${Button_Submit}
    Wait For Elements State    ${Success_Message}    visible    timeout=50s
    Click        ${Button_Finish}
    Wait For Condition              title    ==   Logan Marcus - Success Plan | TaskRay Project | Salesforce      timeout=50s


Archieve Success Plan
    Reload
    Wait For Elements State    ${Button_Edit_Archieved}    visible    timeout=30s
    Click    ${Button_Edit_Archieved}
    Wait For Elements State    ${Checkbox_Archieved}    visible    timeout=20s
    Click    ${Checkbox_Archieved}
    Click    ${Button_Save}
    