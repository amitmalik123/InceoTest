@e2e @add_ach @critical
Feature: Add ACH E2E flow
  As a financial advisor
  I want to add ACH instructions

  # @smoke
  #  Scenario: Successfully login and navigate to Account List
  #    When I navigate to Clients menu

  @regression @ach
  Scenario: Successfully complete Add ACH flow
  # sql db connection steps
    When I verify the retirement billing client in database
   When I verify the am billing accounts data from database

  # azure db connection steps
    When I verify the transfer status in database
    When I verify the account distribution in database
   # excel
   # When I load test data from excel sheet "Shell"

  #  When I navigate to Clients menu
   # And I click on Account List

   # Then User is on the accountlist tab and search with the accountNo
   # And User should click on searched account and navigate to account wizard page
    #And User should pick account information from the selected account
    #And User checks Toggle Functionality for Specific User and Click on Add ACH Instructions on Account Wizard
    #When User should click on the "ACH" radio button and click on Next
    #And User should click on the Add Button to land on the Add ACH Instructions Page
    #And User should fetch ClientHouseholdID
    #Then User should validate "ClientHousehold" API with status code "200"
    #Then User to fetch Client Household API values
    #Then User should enter valid AINS page details "oneAccount" for radio type "ACH" and SLOA option as "Bank Instructions Only - No SLOA" and SLOASubOption as "NoEsign" and role as "Advisor"
    #Then User should click on the Next Button on Add ACH instruction Page to navigate back on summary page
    # Then User should validate AINS summary page details "oneAccount" for radio type "ACH" and SLOA option as "Bank Instructions Only - No SLOA" and SLOASubOption as "NoEsign" and role as "Advisor"
    # Then User should verify "Add_ACH" disclosure Content in Transaction Summary Page
    # Then User should click on the Submit Button on AddACH Summary Page
    # Then User should validate AINS confirmation page details for "NoEsign", "oneAccount" and role as "Advisor"
    # Then User should click on the Item number on AINS Confirmation Page
    # Then User should validate the Notes content for "NoEsign" which are "Add ACH instructions request has been processed. Thank you.", "Name/Title on Bank Account", "Delivery Method" as "ACH", "Additional Name/Title on Bank Account:", "Bank Name" and "Bank Account Number" in "AddACHInstructions" and the role is "Advisor" for InPerson Sign in AddACH
    # Then User should validate the "An email notification regarding completion of this request has been sent to the selected recipient(s) listed in Tracking Center Notification Preferences." Notification on the Tracking Center for "AddACH NoEsign"
    # Then User should execute azure db query with item number and verify note "Step CreateAINSRecord completed successfully" for AINS where stepID is "45"
    # Then User should validate closed date for role Advisor
    # Then User should validate info panel contents with status and item description as Bank/Payee Instructions - Add for Add ACH NoEsign
    # Then User should validate time stamp on tracking center page
    # Then User should execute azure db query and fetch the Instance Audit table notes and validate them for SLOA "NoEsign" and role as "Advisor"
    # When User should click View button in item details page
    # Then Validate view documents popup
    # Then Validate PDF is generated
    # When User should delete PDF displayed as "eSigPDFDownload"
    # When User should click on the PDF Link to download
    # Then User should verify PDF is displayed as "eSigPDFDownload"
    # Then User should delete PDF displayed as "eSigPDFDownload"
