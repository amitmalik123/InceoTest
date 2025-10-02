*** Settings ***
Library        Browser
Library        String
Variables     ../PageObjects/Locators.py


*** Variables ***
${LEAD_FULL_NAME}



*** Keywords ***
Navigate to Lead page
    Set Selector Prefix        ${None}
    Wait For Elements State    ${Dropdown_Navigation}    visible    timeout=30s
    Click    ${Dropdown_Navigation}
    Wait For Elements State    ${Option_Leads}    visible    timeout=10s
    Click    ${Option_Leads}

Lead Page should be displayed
    Wait For Elements State    ${Heading_Leads}    visible    timeout=30s
    Get Text    ${Heading_Leads}    ==    Leads 

Click New Lead button   
    Click    ${Button_New}
    Wait For Elements State    ${Header_New_Lead}    visible    timeout=30s

Verify New Lead Page is Open
    Get Text    ${Header_New_Lead}    ==    New Lead: Investment Professional

Verify an errors and then create Lead With Random String
    [Arguments]                         ${FN}   ${COMPANYNAME}  ${STRADD}   ${CITY}     ${STATE}    ${ZIPCODE}  ${COUNTRY}
    ${lastname} =                       generate random string    5     [LETTERS]
    ${crd} =                            generate random string    4     [NUMBERS]
    ${full name} =                      set variable    ${FN} ${lastname}
    ${email} =                          set variable    ${lastname}@gmail.com
    set global variable                 ${LEAD_FULL_NAME}         ${full name}
    Fill Text                           ${Text_Box_First_Name}    ${FN}
    Fill Text                           ${Text_Box_Last_Name}     ${lastname}
    Fill Text                           ${Text_Box_Phone}       34121649501234
    Fill Text                           ${Text_Box_CRD}         ${crd}
    Fill Text                           ${Text_Box_Email}        ${email}
    Fill Text                           ${Text_Box_Street}      ${STRADD}
    Fill Text                           ${Text_Box_City}        ${CITY}
    Fill Text                           ${Text_Box_State}       ${STATE}
    Fill Text                           ${Text_Box_Zipcode}     ${ZIPCODE}
    Fill Text                           ${Text_Box_Country}     ${COUNTRY}
    Scroll To Element                   ${Text_Box_Company}
    Fill Text                           ${Text_Box_Company}     ${COMPANYNAME}
    Click                               ${Button_Save}
    Wait For Elements State             ${Error_LeadSource}    visible    timeout=30s
    Get Text                            ${Error_LeadSource}    ==    Lead Source\nComplete this field.
    Sleep                               2s
    Take Screenshot                     embed=True
    Click                               ${Button_Error_Icon}
    Click                               ${Combobox_LeadSource}
    Sleep                               3s
    Press Keys                          ${Combobox_LeadSource}    ArrowDown
    Press Keys                          ${Combobox_LeadSource}    ArrowDown
    Sleep                               3s
    Press Keys                          ${Combobox_LeadSource}    Enter
    Fill Text                           ${Text_Box_Company}     ${EMPTY}
    Click                               ${Button_Save}
    Wait For Elements State             ${Error_Company}    visible    timeout=20s
    Get Text                            ${Error_Company}    ==    Company\nComplete this field.
    Sleep                               2s
    Take Screenshot                     embed=True
    Fill Text                           ${Text_Box_Company}     ${COMPANYNAME}
    Fill Text                           ${Text_Box_Last_Name}     ${EMPTY}
    Click                               ${Button_Save}
    Wait For Elements State             ${Error_LastName}    visible    timeout=20s
    Get Text                            ${Error_LastName}    ==    Last Name\nComplete this field.
    Sleep                               2s
    Take Screenshot                     embed=True
    Fill Text                           ${Text_Box_Last_Name}     ${lastname}
    Fill Text                           ${Text_Box_CRD}         ${EMPTY}
    Click                               ${Button_Save}
    Wait For Elements State             ${Error_CRD}    visible    timeout=20s
    Get Text                            ${Error_CRD}    ==    Discovery Data Rep CRD\nComplete this field.
    Sleep                               2s
    Take Screenshot                     embed=True
    Fill Text                           ${Text_Box_CRD}         ${crd}
    Click                               ${Button_Save}
    Wait For Condition                  Title    ==     ${full name} | Lead | Salesforce    timeout=50s
    Sleep                               2s
    Take Screenshot                     embed=True    fullPage=True    timeout=10s
    

Search Newly Created Lead
    [Arguments]                         ${LEAD_FULL_NAME}
    Fill Text                           ${Search_Box_Leads}     ${LEAD_FULL_NAME}
    Press Keys                          ${Search_Box_Leads}     Enter
    Wait For Elements State             ${Link_Lead}    visible    timeout=20s
    Click                               ${Link_Lead}
    Wait For Condition                  Title    ==     ${LEAD_FULL_NAME} | Lead | Salesforce    timeout=50s
    #Wait For Load State                 domcontentloaded    timeout=50s


Verify Phone and Extension fields
    Reload
    Wait For Elements State             ${Output_Phone}    visible    timeout=50s
    Get Text                            ${Output_Phone}           ==    (341) 216-4950
    Get Text                            ${Output_PhoneExt}        ==    1234
    

Verify Lead Sources
    Reload
    Wait For Elements State             ${Output_LeadSource}    visible    timeout=50s
    Scroll To Element                   ${Output_LeadSource}        
    Get Text                            ${Output_LeadSource}      ==    AssetMark Event
    Click                               ${Button_Edit_LeadSource}
    Click                               ${Combobox_LeadSource}
    Press Keys                          ${Combobox_LeadSource}    ArrowDown
    Press Keys                          ${Combobox_LeadSource}    Enter
    Get Text                            ${Combobox_LeadSource}      ==    AssetMark Leadership Advantage
    Click                               ${Combobox_LeadSource}
    Press Keys                          ${Combobox_LeadSource}    ArrowDown
    Press Keys                          ${Combobox_LeadSource}    Enter
    Get Text                            ${Combobox_LeadSource}      ==    BD Conference
    Click                               ${Combobox_LeadSource}
    Press Keys                          ${Combobox_LeadSource}    ArrowDown
    Press Keys                          ${Combobox_LeadSource}    Enter
    Get Text                            ${Combobox_LeadSource}      ==    BD Rep List
    Click                               ${Combobox_LeadSource}
    Press Keys                          ${Combobox_LeadSource}    ArrowDown
    Press Keys                          ${Combobox_LeadSource}    Enter
    Get Text                            ${Combobox_LeadSource}      ==    Database - Discovery
    Click                               ${Combobox_LeadSource}
    Press Keys                          ${Combobox_LeadSource}    ArrowDown
    Press Keys                          ${Combobox_LeadSource}    Enter
    Get Text                            ${Combobox_LeadSource}      ==    Digital Lead Generation
    Click                               ${Combobox_LeadSource}
    Press Keys                          ${Combobox_LeadSource}    ArrowDown
    Press Keys                          ${Combobox_LeadSource}    Enter
    Get Text                            ${Combobox_LeadSource}      ==    Inbound Call
    Click                               ${Combobox_LeadSource}
    Press Keys                          ${Combobox_LeadSource}    ArrowDown
    Press Keys                          ${Combobox_LeadSource}    Enter
    Get Text                            ${Combobox_LeadSource}      ==    NPA Up
    Click                               ${Combobox_LeadSource}
    Press Keys                          ${Combobox_LeadSource}    ArrowDown
    Press Keys                          ${Combobox_LeadSource}    Enter
    Get Text                            ${Combobox_LeadSource}      ==    OSJ/Producer Group
    Click                               ${Combobox_LeadSource}
    Press Keys                          ${Combobox_LeadSource}    ArrowDown
    Press Keys                          ${Combobox_LeadSource}    Enter
    Get Text                            ${Combobox_LeadSource}      ==    Other
    Click                               ${Combobox_LeadSource}
    Press Keys                          ${Combobox_LeadSource}    ArrowDown
    Press Keys                          ${Combobox_LeadSource}    Enter
    Get Text                            ${Combobox_LeadSource}      ==    Outbound Call
    Click                               ${Combobox_LeadSource}
    Press Keys                          ${Combobox_LeadSource}    ArrowDown
    Press Keys                          ${Combobox_LeadSource}    Enter
    Get Text                            ${Combobox_LeadSource}      ==    Referral - Advisor
    Click                               ${Combobox_LeadSource}
    Press Keys                          ${Combobox_LeadSource}    ArrowDown
    Press Keys                          ${Combobox_LeadSource}    Enter
    Get Text                            ${Combobox_LeadSource}      ==    Referral - BD
    Click                               ${Combobox_LeadSource}
    Press Keys                          ${Combobox_LeadSource}    ArrowDown
    Press Keys                          ${Combobox_LeadSource}    Enter
    Get Text                            ${Combobox_LeadSource}      ==    Referral Program
    Click                               ${Combobox_LeadSource}
    Press Keys                          ${Combobox_LeadSource}    ArrowDown
    Press Keys                          ${Combobox_LeadSource}    Enter
    Get Text                            ${Combobox_LeadSource}      ==    Referral - Strategist
    Click                               ${Combobox_LeadSource}
    Press Keys                          ${Combobox_LeadSource}    ArrowDown
    Press Keys                          ${Combobox_LeadSource}    Enter
    Get Text                            ${Combobox_LeadSource}      ==    Third Party Event
    Click                               ${Combobox_LeadSource}
    Press Keys                          ${Combobox_LeadSource}    ArrowDown
    Press Keys                          ${Combobox_LeadSource}    Enter
    Get Text                            ${Combobox_LeadSource}      ==    --None--
    Click                               ${Combobox_LeadSource}
    Press Keys                          ${Combobox_LeadSource}    ArrowDown
    Press Keys                          ${Combobox_LeadSource}    Enter
    Click                               ${Button_Save}


Verify Team Members
    Reload
    Wait For Elements State             ${Output_Lead_Owner}    visible    timeout=50s
    Scroll To Element                   ${Output_Lead_Owner}
    Get Text                            ${Output_Lead_Owner}      ==    Eric Arave
    Get Text                            ${Output_Ensemble_Team}   ==    Great Lakes
    Get Text                            ${Output_Division}       ==    Central