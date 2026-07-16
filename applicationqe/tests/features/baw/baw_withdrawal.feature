@squad5SmokeTest
Feature: BAW Withdrawal Backlog

  #  @ewm @withdrawal
  # Scenario Outline: C123917_BAW - Withdrawal Submission - Check Bank - IRA with No Tax
  #   When User should click on clients tab and navigate to account list page
  #   And User is on the accountlist tab and search with the account
  #   And User should click on searched account and navigate to account "holding" page
  #   And Select request and type in Account Management
  #   When User clicks on complete and print button
  #   And User select withdrawal method and click on continue button
  #   Then User navigates to docu sign page and clicks on Continue & Finish button
  #   And Fetch the tracking id and click on close button
  #   And User upload the PDF file
  #   And User verify the tracking Id starts with B
  #   When User wait for 1 min

  #   Examples:
  #     | SheetName  | RowNumber |
  #     | Withdrawal | 6         |

  @baw @DE_Withdrawal @withdrawal
  Scenario Outline: C123917_BAW - Withdrawal Submission - Check Bank - NON IRA
    When User click on Open New Work Item button
    When User creates withdrawal work item and adds withdrawal document
    When User searches work item by instance ID and copies B number
    When User runs withdrawal B number in Dashboard
    When User completes the OCR Screen
    Then User completes the IWR process with delivery method "Check"
    When User clicks on Place Withdrawal OA button
    Then User clicks on Submit to BETA button
    Then Validate withdrawal note "Initiated $10,000.00 distribution"

      Examples:
        | SheetName  | RowNumber |
        | Withdrawal | 2         |