Feature: E2E OAM flow for FA, SAU and OA

  @smoke @FNT_regression
  Scenario: OAM_Initiated by FA_Online Submit_Finish
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
    Then User should be redirected to the DocuSign page
    And Verify docusign Review and continue dialog text
    And Verify As_authorized_by stamp presence
    When User confirm and Continue the docusign Review and continue dialog
    And User Finish the DocuSign process
    Then Verify request pop up
    When User click on D number
    Then User should be redirected to Tracking Center Item Detail page
    And Item Detail D number should be same as request submitted pop up D number
    And Verify Tracking Center Item Detail status should be "Document Submitted"
    And Verify Advisor Alert Required value
    And Verify buttons displayed "View"
    And Verify Notes description
    And Verify Agent Name
    And Verify the Routing Order in database

  @HappyPath @smoke @FNT_regression
  Scenario: OAM_Initiated by SAU_Online Submit_Authorized Signer_Not_Required
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
    And Click on Continue
    Then User should be redirected to the DocuSign page
    And Verify docusign Review and continue dialog text
    When User confirm and Continue the docusign Review and continue dialog
    And User add Signature 
    Then Signature and today's date should be added on the document
    And Verify As_authorized_by stamp presence
    When User Finish the DocuSign process
    Then Verify request pop up
    When User click on D number
    Then User should be redirected to Tracking Center Item Detail page
    And Item Detail D number should be same as request submitted pop up D number
    And Verify Tracking Center Item Detail status should be "Document Submitted"
    And Verify Advisor Alert Required value
    And Verify buttons displayed "View"
    And Verify Notes description
    And Verify Agent Name
    And Verify the Routing Order in database

  

  @InDev
  Scenario: OAM_Initiated by SAU_Complete and Print 
    When User navigate to Clients menu
    And User click on Account List
    And User is on the Account List tab and search for Account Number
    And User click on searched account and navigate to account wizard page
    Then Account Number is displayed and radio button is selected
    When User select OAM Request and Type
    Then Verify Form Heading must be same as selected OAM Type
    When User select Submission Type
    Then User should be redirected to the DocuSign page
    And Verify docusign Review and continue dialog text
    And Verify As_authorized_by stamp presence
    When User confirm and Continue the docusign Review and continue dialog
    And User Finish the DocuSign process
    Then Verify request pop up
    When User click on D number
    Then User should be redirected to Tracking Center Item Detail page
    And Item Detail D number should be same as request submitted pop up D number
    And Verify Tracking Center Item Detail status should be "Awaiting Advisor Submission"
    And Verify Agent Name
    And Verify Advisor Alert Required value
    And Verify buttons displayed "Cancel,View,Upload"
    And Verify Notes description
    #And Verify the Routing Order in database