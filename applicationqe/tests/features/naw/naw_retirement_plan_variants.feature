@NAW
Feature: NAW Retirement Plan Variants

  @GNW_Ind_401k @Regression @prodSmoke
  Scenario Outline: NAW_Agent_NewAccount_GNW_Individual_401k
    When User is on Account Wizard tab and click on go button for New Client creation
    And User navigates to client profile page and enter required information
    Then User clicks on next button on client profile page
    When User navigates to Construct portfolio page and enter required information
    Then User clicks on next button on construct portfolio page
    When User navigates to fee page and enter require data
    Then User navigates to portfolio details page and click on Account setup button
    When User navigates to trustee tab and enter require information
    Then User clicks on Participant button
    Then User fills participant information and click on save button
    Then User clicks on retirement plan information button
    When User fills Retirement Plan Information
    Then User clicks on account features button
    Then User clicks on funding method button
    When User navigates to funding tab and enter funding method
    Then User click on online access document delivery button
    When User navigates to online access document delivery tab and click on review all accounts button
    Then User navigates to review all accounts tab and click on proceed to create documents button
    Then User click on create documents button
    When User perform actions on view documents page and fetch require data
    When User clicks on Separate Documents and select Accounts Establishment option
    # When User does the agent esignature with "in person" method
    # When User does the client signature
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
    And User click on run icon
    And User switch to "NAA Coach" page
    And User clicks on "New Account Application" b number open button
    When Click on "select" button under account number association
    Then Validate added account number and account name
    When Click on save exit button
    When expand the account and click on vieweditappdata button
    When User does the activate account
    Then User validate the activated account and switch to eWM
    # Then Navigate to tracking center page
    # When User search item number and fetch description "after activation"
    #Column Name -ParticipantName either Bussiness Owner or Spouse employee
    #Column Name -IRSPlanDocuType: Option 2 = Yes — With another outside Third Party Administrator, but converting to EPIC Retirement Services
    #                              Option 5 = No — I would like to establish the plan with an outside Third Party Administrator (unbundled)
    #Column Name -ParticipantType: "New Participant" = fill all participant details | "Existing Trustee" = select from existing, only ParticipantName radio needed

    Examples:
      | SheetName | RowNumber | ParticipantName  | IRSPlanDocuType | ParticipantType    |
      | NAW       | 10        | Bussiness Owner  | Option 2        | New Participant    |
      # | NAW       | 10        | Bussiness Owner  | Option 2        | Existing Trustee |
      # | NAW       | 10        | Bussiness Owner  | Option 5        | New Participant  |
      # | NAW       | 10        | Bussiness Owner  | Option 5        | Existing Trustee |
      # | NAW       | 10        | Spouse           | Option 2        | New Participant  |
      # | NAW       | 10        | Spouse           | Option 2        | Existing Trustee |
      # | NAW       | 10        | Spouse           | Option 5        | New Participant  |
      # | NAW       | 10        | Spouse           | Option 5        | Existing Trustee |