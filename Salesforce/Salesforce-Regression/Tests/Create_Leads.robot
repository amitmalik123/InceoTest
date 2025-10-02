*** Settings ***
Library            Browser
Resource           ../Resources/SalesforceApp.robot
Suite Setup        Start Salesoforce Testing Session
Suite Teardown     End Salesoforce Testing Session


*** Variables ***
${User}            Howard Choy
${FN}              Regression 
${COMPANYNAME}     Regression Company  
${STRADD}          111 Pine Street   
${CITY}            Zeigler  
${STATE}           IL  
${ZIPCODE}         62999 
${COUNTRY}         USA



*** Test Cases ***
TC#01: Verify user is able to create Lead With Random String
    [Documentation]     This test case verifies an errors for keeping required fields blank and then creation of Lead with random string
    [Tags]              Regression, Smoke
    SalesforceApp.Log in to Salesforce Partial SBX
    SalesforceApp.Access Setup Page
    SalesforceApp.Change User
    SalesforceApp.Open Lead page
    SalesforceApp.Create New Lead With Random String
     

TC#02: Verify the Phone and Extension fields on Lead creation page
    [Documentation]     This test case verifies Phone and Extension fields on Lead creation page
    [Tags]              Regression
    SalesforceApp.Log in to Salesforce Partial SBX
    SalesforceApp.Access Setup Page
    SalesforceApp.Change User
    SalesforceApp.Open Lead page
    SalesforceApp.Search Newly Created Lead
    SalesforceApp.Verify Phone and Extension fields
     

TC#03: Verify the Lead Sources on Lead creation page
    [Documentation]     This test case verifies Lead Sources on Lead creation page
    [Tags]              Regression
    SalesforceApp.Log in to Salesforce Partial SBX
    SalesforceApp.Access Setup Page
    SalesforceApp.Change User
    SalesforceApp.Open Lead page
    SalesforceApp.Search Newly Created Lead
    SalesforceApp.Verify Lead Sources


TC#04: Verify Team Members on Lead detail page
    [Documentation]     This test case verifies Team Members on Lead detail page
    [Tags]              Regression
    SalesforceApp.Log in to Salesforce Partial SBX
    SalesforceApp.Access Setup Page
    SalesforceApp.Change User
    SalesforceApp.Open Lead page
    SalesforceApp.Search Newly Created Lead
    SalesforceApp.Verify Team Members         

