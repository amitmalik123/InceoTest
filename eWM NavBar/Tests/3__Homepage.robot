*** Settings ***
Resource         ../Resources/CommonWeb_PL.robot
Suite Setup     Start eWM Test
#Suite Teardown  End eWM Test


*** Variables ***




*** Test Cases ***
TC#01 Access eWM Test Environment
    [Documentation]    This test case will access the eWM Test Environment URL
    Access Test Environment URL
    Login to Test Environment
    # Verify whether the Footer is available on the page
    # Verify Footer