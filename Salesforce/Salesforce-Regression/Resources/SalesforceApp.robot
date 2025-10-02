*** Settings ***
Library     Browser
Resource    ../Resources/Login.robot
Resource    ../Resources/CommonWeb.robot
Resource    ../Resources/TopMenuBar.robot
Resource    ../Resources/SetupPage.robot
Resource    ../Resources/Contacts.robot
Resource    ../Resources/Leads.robot
Resource    ../Resources/FirstYearSuccessPlan.robot


*** Keywords ***
Log in to Salesforce Partial SBX
    Login.Navigate to Partial SBX

Log in to Salesforce Full SBX
    Login.Navigate to Full SBX

Access Setup Page
    TopMenuBar.Click Set Up gear icon in Top Menu Bar

Change User
    SetupPage.Search User in Setup    ${User}
    SetupPage.Login as User

Open Contact page
    Contacts.Navigate to Contacts Page
    Contacts.Contact Page should be displayed
    
Create New IP Contact With Random String   
    Contacts.Click New Contact button
    Contacts.Select Contact Type Radio Button    Investment Professional
    Contacts.Verify New Contact Page is Open     Investment Professional
    Contacts.Verify an errors and then create Contact With Random String    ${FN}   ${ACTNAME}  ${STRADD}    ${CITY}     ${STATE}    ${ZIPCODE}      ${COUNTRY}

Create New IPP Contact With Random String   
    Contacts.Click New Contact button
    Contacts.Select Contact Type Radio Button    Investment Professional - Prospect
    Contacts.Verify New Contact Page is Open     Investment Professional - Prospect
    Contacts.Verify an errors and then create Contact With Random String    ${FN}   ${ACTNAME}  ${STRADD}    ${CITY}     ${STATE}    ${ZIPCODE}      ${COUNTRY}

Create New NP Contact With Random String   
    Contacts.Click New Contact button
    Contacts.Select Contact Type Radio Button    Non-Producer
    Contacts.Verify New Contact Page is Open     Non-Producer
    Contacts.Verify an errors and then create Contact With Random String    ${FN}   ${ACTNAME}  ${STRADD}    ${CITY}     ${STATE}    ${ZIPCODE}      ${COUNTRY}

Open Lead page
    Leads.Navigate to Lead page
    Leads.Lead Page should be displayed

Create New Lead With Random String
    Leads.Click New Lead button
    Leads.Verify New Lead Page is Open
    Leads.Verify an errors and then create Lead With Random String    ${FN}   ${COMPANYNAME}  ${STRADD}   ${CITY}     ${STATE}    ${ZIPCODE}  ${COUNTRY}

Search Newly Created Lead
    Leads.Search Newly Created Lead    ${LEAD_FULL_NAME}

Verify Phone and Extension fields
    Leads.Verify Phone and Extension fields

Verify Lead Sources
    Leads.Verify Lead Sources

Verify Team Members
    Leads.Verify Team Members

Search NPA Contact
    FirstYearSuccessPlan.Search NPA Contact    ${NPA_CONTACT}

Search Non-NPA Contact
    FirstYearSuccessPlan.Search Non-NPA Contact    ${NonNPA_CONTACT}

Navigate to First Year Success Plan Page
    FirstYearSuccessPlan.Navigate to First Year Success Plan Page

Verify Success Plan screen
    FirstYearSuccessPlan.Verify Success Plan screen

Verify The Message For AUM < 5mn
    FirstYearSuccessPlan.Verify The Message For AUM < 5mn

Verify The Tasks For 5mn < AUM < 15mn
    FirstYearSuccessPlan.Verify The Tasks For 5mn < AUM < 15mn

Verify The Tasks For 15mn < AUM < 25mn
    FirstYearSuccessPlan.Verify The Tasks For 15mn < AUM < 25mn

Verify The Tasks For AUM > 25mn
    FirstYearSuccessPlan.Verify The Tasks For AUM > 25mn

Verify The Tasks For AUM > 5mn for Non-NPA Eligible Contact
    FirstYearSuccessPlan.Verify The Tasks For AUM > 5mn for Non-NPA Eligible Contact

Create Success Plan for Non-NPA Eligible advisor
    FirstYearSuccessPlan.Create Success Plan for Non-NPA Eligible advisor

Create Success Plan for NPA Eligible advisor
    FirstYearSuccessPlan.Create Success Plan for NPA Eligible advisor

Archieve Success Plan
    FirstYearSuccessPlan.Archieve Success Plan

