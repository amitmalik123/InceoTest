@NAW
Feature: NAW eSignature and Approval Variants

  @TrackingCenterESign @Regression @prodSmoke
  Scenario Outline: Create a new Account with Shared User or OfficeAdmin in NAW_GNW_eSign Method = Tracking center
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
    Then User navigates to review all accounts tab and click on proceed to create documents button
    Then User click on create documents button
    When User perform actions on view documents page and fetch require data
    When User clicks on Separate Documents and select Accounts Establishment option
    # When User does the agent esignature with "in person" method and selects "Finish Later"
    # When User does the client from tracking center page
    # When User wait for "30" seconds
    # Then Navigate to tracking center page
    # When User search item number and fetch description "before activation"

    Examples:
      | SheetName | RowNumber |
      | NAW       | 8         |

  @smokeTest11 @Regression @internal_admin @prodSmoke
  Scenario Outline: Internal_Admin_NAW_Agent_NewAccount_GNW_Individual
    When Internal Admin user impersonates into an agent account "click agent"
    When User is on Account Wizard tab and click on go button for New Client creation
    And User navigates to client profile page and enter required information
    Then User clicks on next button on client profile page
    When User navigates to Construct portfolio page and enter required information
    Then User clicks on next button on construct portfolio page
    When User navigates to fee page and enter require data
    Then User navigates to portfolio details page and click on Account setup button
    When User navigates to account holder tab and enter require information
    Then User clicks on account information button
    Then User clicks on account features button
    Then User clicks on funding method button
    When User navigates to funding tab and enter funding method
    Then User click on online access document delivery button
    When User navigates to online access document delivery tab and click on review all accounts button
    Then User navigates to review all accounts tab and click on proceed to create documents button
    Then User click on create documents button
    When User perform actions on view documents page and fetch require data
    When User clicks on Separate Documents and select Accounts Establishment option
    # When User does the internal admin esignature with "in person" method
    # When User does the agent esignature from outlook using tracking number
    # When User logs in as agent in a new browser context
    # When User navigates to tracking center and searches item number
    # When User does the client from tracking center page
    # When User wait for "30" seconds
    # Then Navigate to tracking center page
    # When User search item number and fetch description "before activation"

    Examples:
      | SheetName | RowNumber |
      | NAW       | 9         |

  @OnlineBD
  Scenario Outline: NAW_Agent_NewAccount_GNW_LLC_OnlineBD_Approval
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
    Then User navigates to review all accounts tab and click on proceed to create documents button
    Then User click on create documents button
    When User perform actions on view documents page and fetch require data
    When User clicks on Separate Documents and select Accounts Establishment option
    When User does the agent esignature with "in person" method
    When User does the client signature
    When User wait for "600" seconds
    When Internal Admin user impersonates into an agent account "click broker dealer"
    Then User clicks account approval tab
    Then User selects the client fullname and clicks on approval request
    Then User "Approve" the account
    Then Navigate to tracking center page
    When User search item number and fetch description "before activation"

    Examples:
      | SheetName | RowNumber  |
      | NAW       | 11         |