Feature: OAM_SAU_Online Submit_Authorized Approval_Tracking Center_Blue Banner_Trigger Advisor Mail 
 
 @S11
  Scenario: S11_PRODENG_33109_OAM_SAU_Online Submit_Authorized Approval_Tracking Center_Blue Banner_Trigger Advisor Mail
    When User navigate to Clients menu
    And User click on Account List
    And User is on the Account List tab and search for Account Number
    And User click on searched account and navigate to account wizard page
    Then Account Number is displayed and radio button is selected
    When User select OAM Request and Type
    Then Verify Form Heading must be same as selected OAM Type
    When User select Submission Type
    Then Client Signature Not Required dialog should be displayed
    When User select Client Signature Method
    Then Signer(s) Information dialog should be displayed
    And Verify Authorized Signer Approval section should be displayed on Signer(s) Information dialog
    When User select Authorized Signer Approval option
    Then Authorized Signer eSign Method section should be displayed
    When User select Signer eSign Method
    Then Verify appropriate fields are displayed based on eSign Method selected