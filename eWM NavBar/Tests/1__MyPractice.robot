*** Settings ***
Resource            ../Resources/eWMApp.robot
Variables           ../PO/Page_Locators.py
Suite Setup         Start eWM Test
#Suite Teardown     End eWM Test


*** Test Cases ***
TC#01: Verify user is able to access test environment and landed on Homepage
    eWMApp.Login to Test Environment
    eWMApp.Change User
    eWMApp.Login to Nav URL
    eWMApp.Verify user is landed on Homepage
    #eWMApp.Logout from Test Environment

TC#02: Verify 'My Practice' option on LHN pane is highlighted
    eWMApp.Verify 'My Practice' option on LHN is highlighted

TC03: Verify the footer is available on 'My Practice' page
    eWMApp.Verify whether the Footer is available on the page


