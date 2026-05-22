Feature: E2E OAM flow for FA, SAU and OA

  @FNT_regression @Prod_Regression @Silo_Regression @T10_Regression @S8
  Scenario: S8_OAM_Initiated by FA_Complete and Print
    When User navigate to Clients menu
    And User click on Account List
    And User is on the Account List tab and search for Account Number
    And User click on searched account and navigate to account wizard page
    Then Account Number is displayed and radio button is selected
    When User select OAM Request and Type
    Then Verify Form Heading must be same as selected OAM Type
    When User select Submission Type
    Then User should be redirected to the DocuSign page
    And Verify docusign Review and continue dialog text "Please review and sign the document electronically."
    When User confirm and Continue the docusign Review and continue dialog
    Then Verify As_authorized_by stamp presence
    When User Finish the DocuSign process
    Then Verify request pop up
    When User click on D number
    Then User should be redirected to Tracking Center Item Detail page
    And Item Detail D number should be same as request submitted pop up D number
    And Verify Tracking Center Item Detail status should be "Awaiting Advisor Submission"
    And Verify Advisor Alert Required value
    And Verify buttons displayed "Cancel,View,Upload"
    When User cancel the request
    Then Verify Tracking Center Item Detail status should be "Request Canceled"
    And Verify buttons displayed "View"
    And Verify Notes description
