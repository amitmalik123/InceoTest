*** Settings ***
Library            Browser
Resource           ../Resources/SalesforceApp.robot
Suite Setup        Start Salesoforce Testing Session
Suite Teardown     End Salesoforce Testing Session


*** Variables ***
${Username}        nilesh.chaudhari@assetmark.com.partial
${Password}        SriRam@2025
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
    [Tags]              Smoke
    SalesforceApp.Log in to Salesforce Partial SBX
    SalesforceApp.Access Setup Page
    SalesforceApp.Change User
    SalesforceApp.Open Lead page
    SalesforceApp.Create New Lead With Random String
     
       

