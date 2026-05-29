@e2e @add_ach @critical
Feature: Withdrawal via ACH - Regression


@smoke @regression @ach
  Scenario Outline: ACH Withdrawal - STP Scenario IRA With Do Not Withhold
    Given User with role "ACH-withdrawl-ira" is loaded
    When I navigate to Clients menu
    And I click on Account List
    And User is on the accountlist tab and search with the accountNo
    And User should click on searched account and navigate to account wizard page
    And User should pick account information from the selected account
    And Select "Withdrawals" request and "SLOA on file or Same Beneficial Owner(s)" type in Account Management
    # And User clicks on complete and submit button and click on Continue button without client signature
    And User clicks on complete and submit button
    And User should click continue button without client signature for "Withdrawals"
    And User should select "ACH" withdrawal method with SLOA "Yes"
    And User should fetch selected ACH payee details for SLOA "Yes"
    And User should click continue in Withdrawal Method Modal with SLOA option "Yes"
    When User should click next in MIMO Landing Page
    And User Enter cash in MIMO Transaction request Page
    And Enter details "No" Federal Tax, "No" State Tax, "First Value" Distribution and "checkSTP" checkMemo
    When User should click next in MIMO Transaction Request Page
    #Then User should validate "Destination" contents where "Check Memo" as "checkSTP" and "Mail Delivery" as "Regular Mail"
    Then User should validate "Request Details" contents where "Request Type" as "Withdrawal","Delivery Method" as "ACH" ,"Frequency" as "One-Time" and "Amount"
    Then User should validate "QUALIFIED INFORMATION" contents where "Distribution Reason","Federal Tax Withholding" as "Waived", "State Tax Withholding" as "Waived","State" and "Net Distribution Amount"
    When User should click Submit button in MIMO Summary Page for "STP"
    Then User should validate "TRANSACTION SUMMARY" contents where "Status" as "In Process- Pending Settlement", "Submission Date And Time" , "Submitted By" and "Item Number"
    #Then User should validate "DESTINATION" contents where "Payee Name", "Address", "Check Memo" as "checkSTP" and "Mail Delivery" as "Regular Mail"
    Then User validate "REQUEST DETAILS" contents where "Request Type" as "Withdrawal","Delivery Method" as "ACH" ,"Frequency" as "One-Time" and "Amount" in Confirmation Page for "IRA"
    Then User can validate "QUALIFIED INFORMATION" contents where "Distribution Reason","Federal Tax Withholding" as "Waived", "State Tax Withholding" as "Waived","State" and "Net Distribution Amount" in Confirmation Page
    When User should click on item number
    Then User should validate info panel contents with status "In Process- Pending Settlement" and item description as "IRA Withdrawal Request" for "STP"
    Then User should validate description contains "The withdrawal has been initiated."
    #Then User should validate description contains all the contents "ACH", "checkSTP","Regular Mail","CA","Waived","Waived"
    When User should click View button in item details page
    Then Validate view documents popup
    Then Validate PDF is generated
    Then User should delete PDF displayed as "eSigPDFDownload"
    When User should click on the PDF Link to download
    Then User should verify PDF is displayed as "eSigPDFDownload"
    Then User should delete PDF displayed as "eSigPDFDownload"
    #Then User should verify "TRANSACTION SUMMARY CONFIRMATION" is present in PDF
    #Then User should verify "Request submitted successfully" is present in PDF
    #Then User should verify "Transaction Summary" content present in PDF for "In Process- Pending Settlement" status
    #Then User should verify "Destination" content present in PDF as "checkSTP" and "Regular Mail"
    #Then User should verify "Request Details" content present in PDF for "Check" Withdrawal
    #Then User should verify "Qualified Information" content present in PDF for federaltax as "Waived" , statetax as "Waived" and state as "CA"
    #Then User should delete PDF displayed as "eSigPDFDownload"
    #Then User should execute azure db query with item number and verify status "Step CreateAItem completed successfully" for "STP"   


  @smoke
  Scenario Outline: Check Withdrawal - STP Scenario IRA
    Given User with role "withdrawl-ira" is loaded
    When I navigate to Clients menu
    And I click on Account List
    And User is on the accountlist tab and search with the accountNo
    And User should click on searched account and navigate to account wizard page
    And User should pick account information from the selected account
    And Select "Withdrawals" request and "SLOA on file or Same Beneficial Owner(s)" type in Account Management
    # And User clicks on complete and submit button and click on Continue button without client signature
    And User clicks on complete and submit button
    And User should click continue button without client signature for "Withdrawals"
    And User should select "Check" withdrawal method with SLOA "Yes"
    And User should fetch selected check payee details for SLOA "Yes"
    And User should click continue in Withdrawal Method Modal with SLOA option "Yes"
    When User should click next in MIMO Landing Page
    And User Enter cash in MIMO Transaction request Page
    And Enter details "No" Federal Tax, "No" State Tax, "First Value" Distribution and "checkSTP" checkMemo
    When User should click next in MIMO Transaction Request Page
    # Then User should validate "Destination" contents where "Check Memo" as "checkSTP" and "Mail Delivery" as "Regular Mail"
    Then User should validate "Request Details" contents where "Request Type" as "Withdrawal","Delivery Method" as "Check" ,"Frequency" as "One-Time" and "Amount"
    Then User should validate "QUALIFIED INFORMATION" contents where "Distribution Reason","Federal Tax Withholding" as "Waived", "State Tax Withholding" as "Waived","State" and "Net Distribution Amount"
    When User should click Submit button in MIMO Summary Page for "STP"
    Then User should validate "TRANSACTION SUMMARY" contents where "Status" as "In Process- Pending Settlement", "Submission Date And Time" , "Submitted By" and "Item Number"
    # Then User should validate "DESTINATION" contents where "Payee Name", "Address", "Check Memo" as "checkSTP" and "Mail Delivery" as "Regular Mail"
    Then User validate "REQUEST DETAILS" contents where "Request Type" as "Withdrawal","Delivery Method" as "Check" ,"Frequency" as "One-Time" and "Amount" in Confirmation Page for "IRA"
    Then User can validate "QUALIFIED INFORMATION" contents where "Distribution Reason","Federal Tax Withholding" as "Waived", "State Tax Withholding" as "Waived","State" and "Net Distribution Amount" in Confirmation Page
    When User should click on item number
    Then User should validate info panel contents with status "In Process- Pending Settlement" and item description as "IRA Withdrawal Request" for "STP"
    Then User should validate description contains all the contents where "<delivery_method>", "<check_memo>", "<mail_delivery>", "<state>", "<federal_tax>", "<state_tax>"
    When User should click View button in item details page
    Then Validate view documents popup
    Then Validate PDF is generated
    Then User should delete PDF displayed as "eSigPDFDownload"
    When User should click on the PDF Link to download
    Then User should verify PDF is displayed as "eSigPDFDownload"
    Then User should delete PDF displayed as "eSigPDFDownload"

    #Then User should verify "TRANSACTION SUMMARY CONFIRMATION" is present in PDF
    #Then User should verify "Request submitted successfully" is present in PDF
    #Then User should verify "Transaction Summary" content present in PDF for "In Process- Pending Settlement" status
    #Then User should verify "Destination" content present in PDF as "checkSTP" and "Regular Mail"
    #Then User should verify "Request Details" content present in PDF for "Check" Withdrawal
    #Then User should verify "Qualified Information" content present in PDF for federaltax as "Waived" , statetax as "Waived" and state as "MA"
    #Then User should delete PDF displayed as "eSigPDFDownload"
    #Then User should execute azure db query with item number and verify status "Step CreateAItem completed successfully" for "STP"

    Examples:
      | delivery_method | check_memo | mail_delivery | state | federal_tax | state_tax |
      | Check           | checkSTP   | Regular Mail  | IA    | Waived      | Waived    |

@ach
  Scenario Outline: ACH Withdrawal - STP Scenario nonIRA With Do Not Withhold
    Given User with role "withdrawl-non-ira" is loaded
    When I navigate to Clients menu
    And I click on Account List
    And User is on the accountlist tab and search with the accountNo
    And User should click on searched account and navigate to account wizard page
    And User should pick account information from the selected account
    And Select "Withdrawals" request and "SLOA on file or Same Beneficial Owner(s)" type in Account Management
    And User clicks on complete and submit button
    And User should click continue button without client signature for "Withdrawals"
    And User should select "ACH" withdrawal method with SLOA "Yes"
    And User should fetch selected ACH payee details for SLOA "Yes"
    And User should click continue in Withdrawal Method Modal with SLOA option "Yes"
    When User should click next in MIMO Landing Page
    And User Enter cash in MIMO Transaction request Page
    When User should click next in MIMO Transaction Request Page
    Then User should validate "Request Details" for non-IRA withdrawal with "<delivery_method>", "<request_type>" and "<frequency>"
    When User should click Submit button in MIMO Summary Page for "STP"
    Then User should validate "TRANSACTION SUMMARY" for non-IRA withdrawal with status "<status>"
    Then User should validate "REQUEST DETAILS" confirmation for non-IRA withdrawal with "<delivery_method>", "<request_type>" and "<frequency>"
    When User should click on item number
    Then User should validate info panel contents with status "<status>" and item description as "Withdrawal Request" for "STP"
    Then User should validate description contains "<initiation_message>"
    When User should click View button in item details page
    Then Validate view documents popup
    Then Validate PDF is generated
    Then User should delete PDF displayed as "eSigPDFDownload"
    When User should click on the PDF Link to download
    Then User should verify PDF is displayed as "eSigPDFDownload"
    Then User should delete PDF displayed as "eSigPDFDownload"

    Examples:
      | delivery_method | request_type | frequency | status                          | initiation_message                 |
      | ACH             | Withdrawal   | One-Time  | In Process- Pending Settlement  | The withdrawal has been initiated. |



    @regression
  Scenario Outline: Check Withdrawal - STP Scenario nonIRA
    Given User with role "withdrawl-non-ira" is loaded
    When I navigate to Clients menu
    And I click on Account List
    And User is on the accountlist tab and search with the accountNo
    And User should click on searched account and navigate to account wizard page
    And User should pick account information from the selected account
    And Select "Withdrawals" request and "SLOA on file or Same Beneficial Owner(s)" type in Account Management
    And User clicks on complete and submit button
    And User should click continue button without client signature for "Withdrawals"
    And User should select "Check" withdrawal method with SLOA "Yes"
    And User should fetch selected check payee details for SLOA "Yes"
    And User should click continue in Withdrawal Method Modal with SLOA option "Yes"
    When User should click next in MIMO Landing Page
    And User Enter cash in MIMO Transaction request Page
    When User should click next in MIMO Transaction Request Page
    Then User should validate "Request Details" for non-IRA withdrawal with "<delivery_method>", "<request_type>" and "<frequency>"
    When User should click Submit button in MIMO Summary Page for "STP"
    Then User should validate "TRANSACTION SUMMARY" for non-IRA withdrawal with status "<status>"
    Then User should validate "REQUEST DETAILS" confirmation for non-IRA withdrawal with "<delivery_method>", "<request_type>" and "<frequency>"
    When User should click on item number
    Then User should validate info panel contents with status "<status>" and item description as "Withdrawal Request" for "STP"
    Then User should validate description contains contents where "<delivery_method>", "<mail_delivery>", "<state>"
    When User should click View button in item details page
    Then Validate view documents popup
    Then Validate PDF is generated
    Then User should delete PDF displayed as "eSigPDFDownload"
    When User should click on the PDF Link to download
    Then User should verify PDF is displayed as "eSigPDFDownload"
    Then User should delete PDF displayed as "eSigPDFDownload"

    Examples:
      | delivery_method | request_type | frequency | status                          | mail_delivery | state |
      | Check           | Withdrawal   | One-Time  | In Process- Pending Settlement  | Regular Mail  | WY    |


  # @smoke @regression @ach
  # Scenario Outline: ACH Withdrawal - E-sign Flow IRA With Do Not Withhold
  #   Given User with role "ACH-withdrawl-ira" is loaded
  #   When I navigate to Clients menu
  #   And I click on Account List
  #   And User is on the accountlist tab and search with the accountNo
  #   And User should click on searched account and navigate to account wizard page
  #   And User should pick account information from the selected account
  #   And Select "Withdrawals" request and "SLOA on file or Same Beneficial Owner(s)" type in Account Management
  #   And User clicks on complete and submit button
  #   And User should select E-sign flow and click continue for "Withdrawals"
  #   Then user is redirected on signer information page and fill signer detail with email "<SignerEmail>" and click on continue button
  #   And User should select "ACH" withdrawal method with SLOA "Yes"
  #   And User should fetch selected ACH payee details for SLOA "Yes"
  #   And User should click continue in Withdrawal Method Modal with SLOA option "Yes"
  #   When User should click next in MIMO Landing Page
  #   And User Enter cash in MIMO Transaction request Page
  #   And Enter details "No" Federal Tax, "No" State Tax, "First Value" Distribution and "checkSTP" checkMemo
  #   When User should click next in MIMO Transaction Request Page
  #   Then User should validate "Request Details" contents where "Request Type" as "Withdrawal","Delivery Method" as "ACH" ,"Frequency" as "One-Time" and "Amount"
  #   Then User should validate "QUALIFIED INFORMATION" contents where "Distribution Reason","Federal Tax Withholding" as "Waived", "State Tax Withholding" as "Waived","State" and "Net Distribution Amount"
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
  #   When User login to the email and search the authorized signer email with subject "<EmailSubject>" and body "<EmailBody>"
  #   Then Verify email contains subject "<EmailSubject>" and body "<EmailBody>"

  #   Examples:
  #     | SignerEmail                 | EmailSubject         | EmailBody                                          |
  #     | ankit.patel@assetmark.com   | Electronic Signature | Please review and sign the document electronically |


