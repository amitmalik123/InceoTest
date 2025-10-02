*** Settings ***
Library     Browser
Library     String
Variables   ../PageObjects/Locators.py



*** Keywords ***
Navigate to Contacts Page
    Set Selector Prefix        ${None}
    #Reload    timeout=50s    waitUntil=load
    Wait For Elements State    ${Dropdown_Navigation}    visible    timeout=30s
    Click    ${Dropdown_Navigation}
    Wait For Elements State    ${Option_Contacts}    visible    timeout=10s
    Click    ${Option_Contacts}
    

Contact Page should be displayed
    Wait For Elements State    ${Heading_Contacts}    visible    timeout=30s
    Get Text    ${Heading_Contacts}    ==    Contacts
    
    
Click New Contact button    
    Click    ${Button_New}
    Wait For Elements State    ${Radio_Button_IP}    visible    timeout=30s


Select Contact Type Radio Button
    [Arguments]    ${ContactType}
    Run Keyword If    '${ContactType}'=='Investment Professional'    Click    ${Radio_Button_IP}
    ...    ELSE IF    '${ContactType}'=='Investment Professional - Prospect'    Click    ${Radio_Button_IPP}
    ...    ELSE IF    '${ContactType}'=='Non-Producer'    Click    ${Radio_Button_NP}
    Click    ${Button_Next}


Verify New Contact Page is Open
    [Arguments]    ${ContactType}
    Wait For Elements State    ${Header_New_Contact}    visible    timeout=30s
    Run Keyword If    '${ContactType}'=='Investment Professional'    Get Text    ${Header_New_Contact}    ==    New Contact: Investment Professional
    ...    ELSE IF    '${ContactType}'=='Investment Professional - Prospect'    Get Text    ${Header_New_Contact}    ==    New Contact: Investment Professional - Prospect
    ...    ELSE IF    '${ContactType}'=='Non-Producer'    Get Text    ${Header_New_Contact}    ==    New Contact: Non-Producer
    ...    END
    

Verify an errors and then create Contact With Random String
    [Arguments]                         ${FN}   ${ACTNAME}  ${STRADD}    ${CITY}     ${STATE}    ${ZIPCODE}      ${COUNTRY}
    ${lastname}=                        Generate Random String    5    [LETTERS]
    ${crd}=                             Generate Random String    5    [NUMBERS]
    ${fullname}=                        Set Variable    ${FN} ${lastname}
    ${email}=                           Set Variable    ${lastname}@test.com
    Wait For Elements State             ${Text_Box_First_Name}    visible    timeout=30s
    Fill Text                           ${Text_Box_First_Name}    ${FN}
    Fill Text                           ${Text_Box_Last_Name}     ${lastname}
    Click                               ${Button_Save}
    Scroll To Element                   ${Label_Office}
    Sleep                               2s
    Wait For Elements State             ${Error_AccountName}    visible    timeout=20s
    Get Text                            ${Error_AccountName}    ==    Account Name\nComplete this field.
    Take Screenshot                     embed=True
    Click                               ${Button_Error_Icon}
    Click                               ${ComboBox_AccountName}
    Fill Text                           ${ComboBox_AccountName}      ${ACTNAME}
    Sleep                               3s
    Press Keys                          ${ComboBox_AccountName}      ArrowUp
    Press Keys                          ${ComboBox_AccountName}      ArrowUp
    Wait For Elements State             ${Option_AccountName}    visible    timeout=20s
    Click                               ${Option_AccountName}
    Sleep                               2s
    Fill Text                           ${Text_Box_Last_Name}       ${EMPTY}
    Click                               ${Button_Save}
    Wait For Elements State             ${Error_LastName}    visible    timeout=20s
    Get Text                            ${Error_LastName}    ==    Last Name\nComplete this field.      
    Take Screenshot                     embed=True
    IF  '${Header_New_Contact}' == 'New Contact: Non-Producer'    
        Fill Text                       ${Text_Box_Last_Name}       ${lastname}
        Fill Text                       ${Text_Box_Email}           ${email}
        Fill Text                       ${Text_Box_MailingStreet}   ${STRADD}
        Fill Text                       ${Text_Box_MailingCity}     ${CITY}
        Fill Text                       ${Text_Box_MailingState}    ${STATE}
        Fill Text                       ${Text_Box_MailingZipcode}  ${ZIPCODE}
        Fill Text                       ${Text_Box_MailingCountry}  ${COUNTRY}
        Click                           ${Button_Save}
        Get Text                        ${Label_FullName}     ==    ${fullname}
        Take Screenshot                 embed=True
    ELSE
        Fill Text                       ${Text_Box_Last_Name}       ${lastname}
        Fill Text                       ${Text_Box_CRD}             ${crd}
        Fill Text                       ${Text_Box_Email}           ${email}
        Fill Text                       ${Text_Box_MailingStreet}   ${STRADD}
        Fill Text                       ${Text_Box_City}            ${CITY}
        Fill Text                       ${Text_Box_State}           ${STATE}
        Fill Text                       ${Text_Box_Zipcode}         ${ZIPCODE}
        Fill Text                       ${Text_Box_Country}         ${COUNTRY}
        Click                           ${Button_Save}
        Wait For Condition              title    ==   ${fullname} | Contact | Salesforce      timeout=50s
        #Wait For Elements State         ${Label_FullName}    visible    timeout=50s
        #Get Text                        ${Label_FullName}     ==    ${fullname}
        #Get Title                       ==    ${fullname} - Contact - Salesforce    
        Take Screenshot                 embed=True
    END
    