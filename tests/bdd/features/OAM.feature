Feature: E2E OAM flow for FA, SAU and OA

  @FNT_regression @Silo_Regression @smoke
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
    And Verify docusign Review and continue dialog text "Please review and sign the document electronically."
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
    #And Verify Agent Name
    #And Verify the Routing Order in database

  @HappyPath @FNT_regression @Silo_Regression @T10_Regression @Prod_Regression
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
    And Verify docusign Review and continue dialog text "Please review and sign the document electronically."
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
    #And Verify Agent Name
    #And Verify the Routing Order in database

  @FNT_regression
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
    And Verify docusign Review and continue dialog text "Please review and sign the document electronically."
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
    And Verify the Routing Order in database


  @FNT_regression
  Scenario: OAM_Initiated_by_OA_Complete_And_Print
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
    And Verify the Routing Order in database


  @FNT_regression
  Scenario: OAM_Initiated by SAU_Online Submit_Authorized Signer_Required_FA
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
    When User login to the email and search the authorized signer email
    Then Verify authorized signer email content
    When User click on Review Document and submit the otp
    Then Verify docusign Review and continue dialog text "Your Shared Access User has prepared one or more documents that are ready for you to sign electronically."
    When User confirm and Continue the docusign Review and continue dialog
    And User click on Sign and add signature
    And User Finish the DocuSign process
    Then Verify Tracking Center Item Detail status should be "Document Submitted"
    And Verify buttons displayed "View"
    And Verify Notes description
    And Verify Agent Name
    And Verify the Routing Order in database

  @FNT_regression
  Scenario: OAM_Initiated by SAU_Online Submit_Authorized Signer_Required_SAU
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
    When User login to the email and search the authorized signer email
    Then Verify authorized signer email content
    When User click on Review Document and submit the otp
    Then Verify docusign Review and continue dialog text "Your Shared Access User has prepared one or more documents that are ready for you to sign electronically."
    When User confirm and Continue the docusign Review and continue dialog
    And User click on Sign and add signature
    And User Finish the DocuSign process
    Then Verify Tracking Center Item Detail status should be "Document Submitted"
    And Verify buttons displayed "View"
    And Verify Notes description
    And Verify Agent Name

  Scenario: Prod_OAM_Initiated by SAU_Online Submit_Authorized Signer_Required_FA
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
    When User cancel the request
    Then Verify Tracking Center Item Detail status should be "Request Canceled"
    And Verify buttons displayed "View"
    And Verify Notes description


  @SiloRegression_OneCleanUp
  Scenario: Prod_OAM_Initiated by FA_Complete and Print
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

  Scenario: OAM_Initiated by SAU_eSignature_With One Inperson Client Signature_Authorized Signer_NOT required
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
    Then Verify Tracking Center Item Detail status should be "Document Submitted"
    And Verify buttons displayed "View,Upload"
    And Verify Notes description
    And Verify Agent Name

  @InDev
  Scenario: OAM_Initiated by FA_Online Submit_Finish Later
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
    And Verify docusign Review and continue dialog text "Please review and sign the document electronically."
    When User confirm and Continue the docusign Review and continue dialog
    Then Verify As_authorized_by stamp presence
    When User Finish later the DocuSign process
    Then Finish Later pop up should be displayed
    When User save the document for finsih later
    And User navigate to Tracking Center
    And Search the DNumber and open the item details page
    Then Verify Tracking Center Item Detail status should be "Awaiting Advisor Submission"
    And Verify buttons displayed "Cancel,View,Finish Now"
    When User click on Finish Now button
    Then User should be redirected to the DocuSign page
    And Verify docusign Review and continue dialog text "Please review and sign the document electronically."
    When User confirm and Continue the docusign Review and continue dialog
    And User Finish the DocuSign process
    Then Verify Tracking Center Item Detail status should be "Document Submitted"
    And Verify buttons displayed "View"
    And Verify Advisor Alert Required value
    And Verify Notes description
    And Verify Agent Name

  @FNT_regression
  Scenario: OAM_Initiated_by_OA_Complete_And_Print
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
    And Verify the Routing Order in database