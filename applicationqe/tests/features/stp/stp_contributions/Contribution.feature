
@e2e @add_ach @critical
Feature: Contribution via ACH - Regression
  
  
  @smoke @regression
  Scenario Outline: Contribution via ACH IRA
    Given User with role "contribution-ira" is loaded
    When I navigate to Clients menu
    And I click on Account List
    And User is on the accountlist tab and search with the accountNo
    And User should click on searched account and navigate to account wizard page
    And User should pick account information from the selected account
    When Select "Contributions" request and "SLOA on file or" type in Account Management
    And User clicks on complete and submit button
    And User should click continue button without client signature for "Contributions"
    And User should select Bank for Contributions request with sloa "Any"
    When User should click next in MIMO Landing Page
    Then User should Validate under the Transaction Details left section the "CURRENT YEAR" title, "Contribution Limit" value, "Contributed" value and "Remaining" value
    Then User should Validate under the Transaction Details right section the "PRIOR YEAR" title, "Contribution Limit" value, "Contributed" value and "Remaining" value
    When User Enter cash in MIMO Transaction request Page
    When User should select "Rollover" as Contribution Reason
    #And User should increase the Contribution Date from the System
    When User should get contribution date
    Then User should verify "<Message>" Important Notes Section
    When User should click next in MIMO Transaction Request Page
    Then User validate "Request Details" Section for "ACH" Contribution and "Rollover" reason in Transaction Summary Page for "IRA"
    Then User should verify "Contribution" disclosure Content in Transaction Summary Page
    When User should click Submit button in MIMO Summary Page for "STP"
    Then User should verify title of the page "TRANSACTION SUMMARY CONFIRMATION"
    Then User should verify confirmation screen success message as "Request submitted successfully"
    Then User should validate Print button is enabled for TSC
    #And User should click print button and Validate the Tab size as 2 in Confirmation Page
    Then User should verify account information displayed in confirmation page
    Then User should validate "TRANSACTION SUMMARY" contents where "Status" as "In Process- Pending Settlement", "Submission Date And Time" , "Submitted By" and "Item Number"
    Then User validate "REQUEST DETAILS" contents where "Request Type" as "Contribution","Delivery Method" as "ACH" ,"Frequency" as "One-Time" and "Amount" in Confirmation Page for "IRA"
    When User should click on item number
    When User should click View button in item details page
    Then Validate view documents popup
    Then Validate PDF is generated
    Then User should delete PDF displayed as "eSigPDFDownload"
    When User should click on the PDF Link to download
    Then User should verify PDF is displayed as "eSigPDFDownload"
    Then User should delete PDF displayed as "eSigPDFDownload"

    Examples: 
      | SheetName     | RowNumber | Message                                    |
      | Contributions |        17 | The year-to-date contribution amount only applies to contributions to this specific account. The contribution limit indicates the total max contributions you can make annually to all your Traditional and Roth IRA accounts. Ensure to consider all IRA contributions and consult a tax professional for additional guidance. |




  # Scenario Outline: Contribution via ACH IRA via E-sign flow
  #   Given User with role "contribution-ira" is loaded
  #   When I navigate to Clients menu
  #   And I click on Account List
  #   And User is on the accountlist tab and search with the accountNo
  #   And User should click on searched account and navigate to account wizard page
  #   And User should pick account information from the selected account
  #   When Select "Contributions" request and "SLOA on file or" type in Account Management
  #   And User clicks on complete and submit button
  #   # And User should click continue button without client signature for "Contributions"
  #   And User should select E-sign flow and click continue for "Contributions"
  #   Then user is redirected on signer information page and fill signer detail with name "<SignerName>" email "<SignerEmail>" phone "<SignerPhone>" and click on continue button
  #   When User should select Bank for Contributions request with sloa "Any"
  #   When User should click next in MIMO Landing Page
  #   Then User should Validate under the Transaction Details left section the "CURRENT YEAR" title, "Contribution Limit" value, "Contributed" value and "Remaining" value
  #   Then User should Validate under the Transaction Details right section the "PRIOR YEAR" title, "Contribution Limit" value, "Contributed" value and "Remaining" value
  #   When User Enter cash in MIMO Transaction request Page
  #   When User should select "Rollover" as Contribution Reason
  #   And User should increase the Contribution Date from the System
  #   When User should get contribution date
  #   Then User should verify "<Message>" Important Notes Section
  #   When User should click next in MIMO Transaction Request Page
  #   Then User validate "Request Details" Section for "ACH" Contribution and "Rollover" reason in Transaction Summary Page for "IRA"
  #   Then User should verify "Contribution" disclosure Content in Transaction Summary Page
  #   When User should click Submit button in MIMO Summary Page for "Esign"
  #   When User should accept DocuSign Electronic Record consent and click continue
  #   Then User is redirected to DocuSign document page and URL is verified
  #   When User scrolls to last page clicks on sign icon and verifies signature
  #   Then User gets the D number from DocuSign document
  #   When User clicks on Finish button in DocuSign
  #   Then eSignature Process Complete modal is displayed
  #   When User clicks on D number link in eSignature complete modal
  #   When User clicks on eSignature button on Tracking Center Item Detail page
  #   Then Electronic Signature Management modal is displayed
  #   # When User clicks on Resend button in Electronic Signature Management modal
  #   When User login to the email and search the authorized signer email with subject "<EmailSubject>" and body "<EmailBody>"
  #   Then Verify email contains subject "<EmailSubject>" and body "<EmailBody>"
  #   When User click on Review Document link in authorized signer email
  #   When User clicks Send Now button on DocuSign verification page
  #   When User fetches OTP from Outlook and submits on DocuSign
  #   When User accepts DocuSign Electronic Record consent and clicks continue
  #   When User scrolls to sign button clicks on it adopts signature and clicks Finish
  #   Then DocuSign shows "You're Done Signing" and user clicks Continue

  #   Examples: 
  #     | SheetName     | RowNumber | SignerName        | SignerEmail                    | SignerPhone  | EmailSubject         | EmailBody                                            | Message                                    |
  #     | Contributions |        26 | Henry Ssassafras  | ankit.patel@assetmark.com      | 9255329706   | Electronic Signature | Please review and sign the document electronically   | The year-to-date contribution amount only applies to contributions to this specific account. The contribution limit indicates the total max contributions you can make annually to all your Traditional and Roth IRA accounts. Ensure to consider all IRA contributions and consult a tax professional for additional guidance. |

