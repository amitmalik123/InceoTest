*** Settings ***
Library            Browser
Resource           ../Resources/SalesforceApp.robot
Suite Setup        Start Salesoforce Testing Session
Suite Teardown     End Salesoforce Testing Session


*** Variables ***
${User}        Lynda Clark
${FN}          Regression 
${ACTNAME}     TestTwoAdFirm  
${STRADD}      111 Pine Street   
${CITY}        San Francisco  
${STATE}       CA  
${ZIPCODE}     94520 
${COUNTRY}     USA



*** Test Cases ***
TC#01: Verify user is able to create IP contact type With Random String
    [Documentation]     This test case verifies an errors for keeping required fields blank and then creation of Investment Professional contact with random string
    [Tags]              Regression, Smoke
    SalesforceApp.Log in to Salesforce Partial SBX
    SalesforceApp.Access Setup Page
    SalesforceApp.Change User
    SalesforceApp.Open Contact page
    SalesforceApp.Create New IP Contact With Random String

TC#02: Verify user is able to create IPP contact type With Random String
    [Documentation]     This test case verifies an errors for keeping required fields blank and then creation of Investment Professional Prospect contact with random string
    [Tags]              Regression
    SalesforceApp.Log in to Salesforce Partial SBX
    SalesforceApp.Access Setup Page
    SalesforceApp.Change User
    SalesforceApp.Open Contact page
    SalesforceApp.Create New IPP Contact With Random String

TC#03: Verify user is able to create NP contact type With Random String
    [Documentation]     This test case verifies an errors for keeping required fields blank and then creation of Non Producer contact with random string
    [Tags]              Regression
    SalesforceApp.Log in to Salesforce Partial SBX
    SalesforceApp.Access Setup Page
    SalesforceApp.Change User
    SalesforceApp.Open Contact page
    SalesforceApp.Create New NP Contact With Random String
    

   