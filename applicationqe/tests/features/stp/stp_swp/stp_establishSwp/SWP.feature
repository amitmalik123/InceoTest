
Feature: SWP Withdrawal - Regression
  As a financial advisor
  I want to cancel a Systematic Withdrawal Plan (SWP) instruction
  So that I can manage my clients' withdrawal preferences

  @smoke
  Scenario Outline: Cancel SWP Withdrawal- Select a ACH SWP and Cancel this instruction_E2E
    Given User with role "cancel-swp-ira-account" is loaded
    When I navigate to Clients menu
    And I click on Account List
    And User is on the accountlist tab and search with the accountNo
    And User should click on searched account and navigate to account wizard page
    And User should pick account information from the selected account
    And Select "Withdrawals" request and "Cancel" type in Account Management
    When User should generate bearer token for Cancel_SWP
    And User should add request header parameters For cancelSWP
    And User should design request body for "<Meth>" and accType "IRA"
    And User should post the response for "CreatePeriodicWithdrawalInstructions" endpoint
    #Then User should verify status code 200
    Then User should verify the response body to confirm creation of instruction
    When User clicks on complete and submit button
    And User should click continue button without client signature for "Cancel"
    Then User should verify Account information displayed on MimoTransaction1 page
    And User should validate "<Message>" under the section "INSTRUCTIONS ON FILE*"
    And User Should check the number of Records and Validate the Pagination Concept
    And User should select First instruction displayed for "<Meth>"
    And User should get the UI value from the Instructions for Selected Radio
    And User should click on the Expand Btn for Selected Instruction
    And User should store the UI Value to be validated
    When User should add request header parameters For "GetPeriodicWithdrawalInstruction"
    And User should post the response for "GetPeriodicWithdrawalInstruction" endpoint
    Then User should verify status code 200
    #And User should retrive the Instruction details to be selected for cancellation
    When User should click next in MIMO Landing Page
    Then User should verify Account information displayed on MimoSummarypage
    # And User should validate under the "DESTINATION" Heading the "Bank Name" header and "Account Number" Header and their values
    And User should validate "Request Details" contents where "Request Type" as "Systematic Withdrawal Request - Cancel","Delivery Method" as "ACH" ,"Frequency" as "Monthly" and "Amount"
    #this is main validation which i need to add
    # And User should validate "Request Details" additional fields where "Cancellation Date" and "Distribution Type"
    #And User should verify "Cancel" disclosure Content in Transaction Summary Page
    When User should click Submit button in MIMO Summary Page for "STP"
    And User should add request header parameters For "GetPeriodicWithdrawalInstructionsByAccount"
    And User should design request body for "GetPeriodicWithdrawalInstructionsByAccount" API
    And User should post the response for "GetPeriodicWithdrawalInstructionsByAccount" endpoint
    Then User should verify status code 200
    #And User should validate the voiding of selected "<Meth>" Instruction from API response
    Then User should verify title of the page "TRANSACTION SUMMARY CONFIRMATION"
    Then User should verify confirmation screen success message as "Request submitted successfully"
    And User should validate Print button is enabled for TSC
    When User should click print button and Validate the Tab size as 2 in Confirmation Page
    Then User should verify account information displayed in confirmation page
    Then User should validate "TRANSACTION SUMMARY" contents where "Status" as "Complete", "Submission Date And Time" , "Submitted By" and "Item Number"
    # Then User should validate "DESTINATION" contents "Bank Name" Header and "Account Number" Header for "ACH" Method in Cancel SWP
    Then User should validate "REQUEST DETAILS" contents where "Request Type" is "Systematic Withdrawal Request - Cancel", "Delivery Method" is "ACH", "Frequency", "Amount", "Cancellation Date" and "Distribution Type" for  Cancel SWP
    When User should click on item number
    Then User should validate info panel contents with status "Complete" and item description as "Systematic Withdrawal Request - Cancel" for "STP"
    Then User should validate description contains "Systematic withdrawal cancellation request has been processed. Thank you."
    #Then User should validate the Notes content which are "Systematic withdrawal cancellation request has been processed. Thank you.", "Amount", "Delivery Method" as "ACH", "Destination", "Cancellation Date" and "Distribution Type" in "CancelSWP"

  Examples:
    | SheetName | RowNumber | Message                                               | Meth |
    | CancelSWP | 3         | Please select a systematic withdrawal plan to cancel. | ACH  |
    #| CancelSWP | 17        | Please select a systematic withdrawal plan to cancel. | ACH_RMD |
    #| CancelSWP | 27        | Please select a systematic withdrawal plan to cancel. | ACH_DivInt |


  @smoke
  Scenario Outline: SWP Establish E2E (Online Submit)
    Given User with role "ACH-withdrawl-ira" is loaded
    When I navigate to Clients menu
    And I click on Account List
    And User is on the accountlist tab and search with the accountNo
    And User should click on searched account and navigate to account wizard page
    And User should pick account information from the selected account
    And Select "Withdrawals" request and "Establish" type in Account Management
    When User should generate bearer token for Beta Access
    And User should add request header parameters For "updateAccountForBeta"
    And User should design request body for state as "<State>" and postal code as "<code>" by updateAccountForBeta for SWP Establish
    And User should post the response for "UpdateAccountForBeta" endpoint
    Then User should verify status code 200
    When User clicks on next button for SWP
    And User should click on the Add button to add a new SWP record
    And User should click on the "<DistributionType>" radio button for Distribution type
    And User should click on the "<DeliveryMethod>" radio button as delivery Method
    And User should click on the active eligible bank radio button
    And User should click the next button on transaction page one
    And User selects the frequency "<Frequency>" on the transaction page two
    And User enters the amount "<Amount>" in the amount field on the transaction page two
    And User selects the NET checkbox "<CheckboxSelection>"
    #And User enters the start date "<StartDate>"
    #And User enters the end date "<EndDate>"
    Then user able to select the date from the calender picker
    When User should click on the Distribution reasons drop down
    And User selects the distribution reason "<SelectedDistributionReason>" from the dropdown
    And User selects the Federal withholding option "<FederalOption>"
    And User enters the Federal withholding rate "<FederalRate>" if applicable
    And User selects the State withholding option "<StateOption>"
    And User enters the State withholding rate "<StateRate>" if applicable
    And User selects the signature option "<SignatureOption>"
    And User clicks on the Next button on the transaction page two
    And User clicks on the "SUBMIT" button on the summary page
    # Then User should validate the "Your submission is in progress." with "Do not refresh this page as it can result in the duplication of the request." loader on the summary page
    Then User should validate the Header Section of "SWP Establish".
    When User should get Item Number from Confirmation Page for SWP Establish
    Then User should verify confirmation screen success message as "Request submitted successfully" for SWP Establish.
    Then User should validate "TRANSACTION SUMMARY" contents where "Status:" as "Complete", "Submission date and time:" , "Submitted by:" and "Item number:" for SWP Establish
    When User should validate all header details and their values for "Systematic Withdrawal Plan - Establish" and method as "ACH" on the SWP Establish Confirmation Page
    And User should get Item Number from Confirmation Page for SWP Establish
    And User should click on item number for SWP Establish
    Then User should validate info panel contents with status "Complete" and item description as "Systematic Withdrawal Request - Establish" for "SWP Establish Online"
    Then User should validate the Notes content whicnh are "The Systematic Withdrawal Plan has been set up.", "Amount", "Delivery Method" as "ACH", "Destination" and "Federal Tax Withholding" in "SWP Establish Online"
    Then User should validate the "An email notification regarding completion of this request has been sent to the selected recipient(s) listed in Tracking Center Notification Preferences." Notification on the Tracking Center for "SWP Establish"
    When User should click View button in item details page
    Then Validate view documents popup
    Then Validate PDF is generated
    Then User should delete PDF displayed as "eSigPDFDownload"
    When User should click on the PDF Link to download
    Then User should verify PDF is displayed as "eSigPDFDownload"
    Then User should delete PDF displayed as "eSigPDFDownload"
    #Then User should delete PDF displayed as "eSigPDFDownload"

  Examples:
      | SheetName    | RowNumber | DistributionType | DeliveryMethod |Frequency |Amount|CheckboxSelection|StartDate |EndDate   |SelectedDistributionReason|FederalOption  |FederalRate    |StateOption              |StateRate|State|code |SignatureOption|
      | CancelSWP |        3 | Fixed            | ACH            |Monthly   |100.55|Select           |09/05/2025|09/06/2025|Normal Distribution        |do_not_withhold|               |do_not_withhold          |         |MI   |48001|Do Not Obtain Client Signature(s) - Only Advisor Authorization Required|


  
