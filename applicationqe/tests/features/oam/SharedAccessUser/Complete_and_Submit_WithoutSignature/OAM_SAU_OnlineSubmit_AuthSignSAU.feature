Feature: S6_OAM_Initiated by SAU_Online Submit_Authorized Signer_Required_SAU

@FNT_regression @OAM_S6
  Scenario Outline: S6_OAM_Initiated by SAU_Online Submit_Authorized Signer_Required_SAU
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
    When User fetch signers information from database
    Then Verify Authorized Signer dropdown
    When User provide Authorized Signers information
    And Click on Continue
    Then User should be redirected to the DocuSign page
    And Verify docusign Review and continue dialog text "Please review and sign the document electronically."
    When User confirm and Continue the docusign Review and continue dialog
    And User Finish the DocuSign process
    Then Verify request pop up
    When User click on D number
    Then User should be redirected to Tracking Center Item Detail page
    And Item Detail D number should be same as request submitted pop up D number
    And Verify Tracking Center Item Detail status should be "Awaiting Advisor Submission"
    And Verify Advisor Alert Required value
    And Verify buttons displayed "Cancel,View,eSignature"
    # When User login to the email and search the authorized signer email
    # Then Verify authorized signer email content
    # When User click on Review Document and submit the otp
    # Then Verify docusign Review and continue dialog text "Your Shared Access User has prepared one or more documents that are ready for you to sign electronically."
    # When User confirm and Continue the docusign Review and continue dialog
    # And User click on Sign and add signature
    # And User Finish the DocuSign process
    # Then Verify Tracking Center Item Detail status should be "Document Submitted"
    # And Verify buttons displayed "View"
    # And Verify Notes description
    # And Verify Agent Name

  Examples:
    | SheetName | RowNumber   |
    | OAM       | 6           |