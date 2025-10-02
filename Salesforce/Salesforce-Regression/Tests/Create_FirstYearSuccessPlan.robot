*** Settings ***
Library      Browser
Resource     ../Resources/SalesforceApp.robot
Suite Setup   Start Salesoforce Testing Session


*** Variables ***
${USER} =               Brian Fitzgerald
${NPA_CONTACT} =        Logan Marcus
${NON_NPA_CONTACT} =    Steve D. Lindberg


*** Test Cases ***
TC#01: Create First Year Success Plan for NPA Contact
    [Documentation]    Create First Year Success Plan for NPA Contact
    SalesforceApp.Log in to Salesforce Full SBX
    SalesforceApp.Access Setup Page
    SalesforceApp.Change User
    SalesforceApp.Search NPA Contact
    SalesforceApp.Navigate to First Year Success Plan Page
    SalesforceApp.Verify Success Plan screen
    SalesforceApp.Verify The Message For AUM < 5mn
    
TC#02: Verify the tasks when AUM is equal/greater than 5mn but less than 15mn for NPA Eligible advisor
    [Documentation]     This test case verifies the different tasks when AUM is equal/greater than 5mn but less than 15mn for NPA Eligible advisor
    SalesforceApp.Navigate to First Year Success Plan Page
    SalesforceApp.Verify The Tasks For 5mn < AUM < 15mn
    
TC#03: Verify the tasks when AUM is equal/greater than 15mn but less than 25mn for NPA Eligible advisor
    [Documentation]     This test case verifies the different tasks when AUM is equal/greater than 15mn but less than 25mn for NPA Eligible advisor
    SalesforceApp.Verify The Tasks For 15mn < AUM < 25mn

TC#04: Verify the tasks when AUM is equal/greater than 25mn for NPA Eligible advisor
    [Documentation]     This test case verifies the different tasks when AUM is equal/greater than 25mn for NPA Eligible advisor
    SalesforceApp.Verify The Tasks For AUM > 25mn    

TC#05: Verify Sales user is able to create and archieve a Success Plan for NPA Eligible advisor
    [Documentation]     This test case verifies the ability of user to create a Success Plan and Archieve it for NPA Eligible advisor
    SalesforceApp.Create Success Plan for NPA Eligible advisor
    SalesforceApp.Archieve Success Plan

TC#06: Verify the message if Expected AUM Commitment 12 Months provided is less than $5mn for Non-NPA Eligible advisor
    [Documentation]     This test case verifies the message if Expected AUM Commitment 12 Months provided is less than $5mn for Non-NPA Eligible advisor
    SalesforceApp.Search Non-NPA Contact
    SalesforceApp.Navigate to First Year Success Plan Page
    SalesforceApp.Verify Success Plan screen
    SalesforceApp.Verify The Message For AUM < 5mn

TC#07: Verify the tasks when AUM is equal/greater than 5mn for Non-NPA Eligible advisor
    [Documentation]     This test case verifies the different tasks when AUM is equal/greater than 5mn for Non-NPA Eligible advisor
    SalesforceApp.Verify The Tasks For AUM > 5mn for Non-NPA Eligible Contact

TC#08: Verify Sales user is able to create and archieve a Success Plan for Non-NPA Eligible advisor
    [Documentation]     This test case verifies the ability of user to create a Success Plan and Archieve it for Non-NPA Eligible advisor
     SalesforceApp.Create Success Plan for Non-NPA Eligible advisor
     SalesforceApp.Archieve Success Plan   