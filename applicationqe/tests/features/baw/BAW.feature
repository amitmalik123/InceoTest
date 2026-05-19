@squad5SmokeTest

Feature: TOAR

  @toar @baw @prodSmoke
  Scenario Outline: TOAR_Record
    When User click on Open New Work Item button
    When Select work item type "Custodian Change Request"
    When Enter Custodial Account value
    And Select individual owner and click run now
    And Fetch b number from shell process page
    Then Click on update transfer button
    Then enter transfer details for work item "Custodian Change Request" with "Percent" allocation in destination
    And Validate notes history section "TOAR Record created successfully"

    Examples:
      | SheetName | RowNumber |
      | TOAR      | 2         |

  @Journal @baw @prodSmoke
  Scenario Outline: BAW_Shell_Add journal from BPM_WFI
    When User click on Open New Work Item button
    When Select work item type "Investment Solution Change Journal"
    When Enter Custodial Account value
    And Select individual owner and click run now
    When Update internal status "In Process"
    And Fetch b number from shell process page
  #  Then Establish DB connection and update "request status" in citrix
  #  Then Establish DB connection and update "completionDate" in citrix
    And User fetches custodian account
    And click on Update OA button
    When cancel already created journal
    And Select action type "Journal"
    And User add a journal
    Then Validate Added Journal
    When Click on save and close button on journalUtilityPage page
    When cancel already created journal
    And Click on save and close button on createOAPage page

    Examples:
      | SheetName | RowNumber |
      | Shell     | 2        |

@toad @baw @prodSmoke
  Scenario Outline: TOAD_Record
    When User click on Open New Work Item button
    When Select work item type "<WorkItemType>"
    When Enter Custodial Account value
    And Select individual owner and click run now
    And Fetch b number from shell process page
    Then Click on update transfer button
    Then enter transfer details for work item "<WorkItemType>" with "Percent" allocation in destination
    # And Validate notes history section "TOAD Record created successfully"

  Examples:
      | SheetName | RowNumber | WorkItemType                 |
      | TOAR      | 2         | Full Transfer Out In Kind    |
      | TOAR      | 2         | Partial Transfer Out In Kind | 

  @BAW @AccountActivation @ES5 
  Scenario Outline: C72057_NAW_Agent_NewAccount_GNW_LLC_BAW_Activation
    When User is on Account Wizard tab and click on go button for New Client creation
    When User navigates to client profile page and enter required information
    Then User clicks on next button on client profile page
    When User navigates to Construct portfolio page and enter required information
    Then User clicks on next button on construct portfolio page
    When User navigates to fee page and enter require data
    Then User navigates to portfolio details page and click on Account setup button
    When User navigates to account holder tab and enter require information
    Then User clicks on LLC Information button
    When Navigate to LLC information page and enter info
    Then User clicks on account features button
    Then User clicks on funding method button
    When User navigates to funding tab and enter funding method
    Then User click on online access document delivery button
    When User navigates to online access document delivery tab and click on review all accounts button
    Then User navigates to review all accounts tab and click on create documents button
    Then User click on create documents button
    When User perform actions on view documents page and fetch require data
    When User clicks on Separate Documents and select Accounts Establishment option
    # When User does the agent esignature with "by mail" method
    # When User does the client signature
    # When User wait for 1 min
    # Then Navigate to tracking center page
    # When User search item number and fetch description "before activation"
    Given User should login to BAW application and click on the dashboard
    When User click on Open New Work Item button
    When Select work item type "New Account Application"
    Then Select custodian type for activation
    When Select individual owner and click run now
    When Fetch b number from shell process page
    When User enter hrc number and click on submit
    And Click on "Search Work Item" tab
    And Enter external id and click on search button
    And Fetch parent b number
    And Click on "Dashboard" tab
    When User search via B tracking number "viaeWM"
    And User click on run icon and switch to "NAA Coach" page
    When User select CIP status "Exception Granted" and save client
    And User clicks on "New Account Application" b number open button
    When Click on "select" button under account number association
    Then Validate added account number and account name
    When Click on save exit button
    And User clicks on "New Account Tax Management" b number open button for tms
    When Click on "Add" button under account number association for tms
    When User does the activate account
    Then User validate the activated account and switch to eWM
    Then Navigate to tracking center page
    When User search item number and fetch description "after activation"

    Examples:
      | SheetName | RowNumber |
      | NAW       | 2         |
  # @ewm @withdrawal
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
	# 	|SheetName    |RowNumber|
	# 	|Withdrawal   |6        |