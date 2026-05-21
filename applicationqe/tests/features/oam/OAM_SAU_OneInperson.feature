Feature: OAM_SAU_eSignature_With One Inperson Client Signature_Authorized Signer_NOT required

@FNT_regression @S9
  Scenario: S9_OAM_Initiated by SAU_eSignature_With One Inperson Client Signature_Authorized Signer_NOT required
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
    When User provide client signature details
    And User select Signer eSign Method
    And User select Authorized Signer Approval option
    And Click on Continue
    Then User should be redirected to the DocuSign page
    And Verify docusign Review and continue dialog text "Please review and sign the document electronically."
    When User confirm and Continue the docusign Review and continue dialog
    And User add Signature 
    Then Signature and today's date should be added on the document
    And Verify As_authorized_by stamp presence
    When User Finish the DocuSign process
    Then Client In Person Signing dialog should be displayed
    When User click on "Start Client Signing" button
    Then User should be redirected to the DocuSign page
    When User click on send now and fetch OTP from mail
    Then Verify docusign Review and continue dialog text "Your Shared Access User has prepared one or more documents that are ready for you to sign electronically."
    When User confirm and Continue the docusign Review and continue dialog
    And User add Signature 
    And User Finish the DocuSign process
    Then Verify eSignature Process Complete dialog should be displayed
    When User navigate to Tracking Center
    And Search the DNumber and open the item details page
    Then Verify Tracking Center Item Detail status should be "Request Received"
    And Verify buttons displayed "View,Upload"
    And Verify Notes description
    And Verify Agent Name