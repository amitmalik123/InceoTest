@NAW
Feature: WFI Regression- NAW

  @navbar
  Scenario Outline: navbar_NAW_Agent_NewAccount_GNW_LLC_navbar
    When Login application
    When User clicks on the clients tab
    And User clicks on the add a client button
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
    When User does the agent esignature with "by mail" method
    When User does the client signature
    When User wait for "30" seconds
    Then Navigate to tracking center page
    When User search item number and fetch description "before activation"
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
    When User select CIP status "Exception Granted" and save client
    And User clicks on "New Account Application" b number open button
    When Click on "select" button under account number association
    Then Validate added account number and account name
    When Click on save exit button
    And User clicks on "New Account Tax Management" b number open button for tms
    When Click on "Add" button under account number association for tms
    When User does the activate account
    Then User validate the activated account and switch to eWM

    Examples: 
      | SheetName | RowNumber |
      | NAW       |        2  |

  @navbar
  Scenario Outline: navbar_NAW_Agent_NewAccount_Fidelity_Trust
    When Login application
    When User clicks on the clients tab
    And User clicks on the add a client button
    When User navigates to client profile page and enter required information
    Then User clicks on next button on client profile page
    When User navigates to Construct portfolio page and enter required information
    Then User clicks on next button on construct portfolio page
    When User navigates to fee page and enter require data
    Then User navigates to portfolio details page and click on Account setup button
    When User navigates to trustee tab and enter require information
    Then User clicks on grantor button
    When Navigate to Account information page and select existing client
    Then User clicks on trust information button
    When User fills Trust information
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
    When User wait for "30" seconds
    Then Navigate to tracking center page
    When User search item number and fetch description "before activation"
    Examples:
      | SheetName | RowNumber |
      | NAW       | 3         |

  @navbar
  Scenario Outline: navbar_NAW_Agent_NewAccount_PRS_Beneficiary_Roth_IRA_Trust
    When Login application
    When User clicks on the clients tab
    And User clicks on the add a client button
    And User navigates to client profile page and enter required information
    Then User clicks on next button on client profile page
    When User navigates to Construct portfolio page and enter required information
    Then User clicks on next button on construct portfolio page
    When User navigates to fee page and enter require data
    Then User navigates to portfolio details page and click on Account setup button
    When User navigates to account holder tab and enter require information
    Then User clicks on Trustors button
    When Navigate to Account information page and select existing client
    Then User clicks on account information button
    When User fills additional account information
    Then User clicks on account features button
    Then User clicks on funding method button
    When User navigates to funding tab and enter funding method
    Then User click on online access document delivery button
    When User navigates to online access document delivery tab and click on review all accounts button
    Then User navigates to review all accounts tab and click on proceed to create documents button
    Then User click on create documents button
    When User perform actions on view documents page and fetch require data
    When User clicks on Separate Documents and select Accounts Establishment option
    When User does the agent esignature with "by mail" method
    When User does the client signature
    When User wait for "30" seconds
    Then Navigate to tracking center page
    When User search item number and fetch description "before activation"
    Examples:
      | SheetName | RowNumber |
      | NAW       | 4         |

  @navbar
  Scenario Outline: navbar_SWB_Agent_NewAccount_SWB_Beneficiary_Roth_IRA_Individual
    When Login application
    When User clicks on the clients tab
    And User clicks on the add a client button
    When User navigates to client profile page and enter required information
    Then User clicks on next button on client profile page
    When User navigates to Construct portfolio page and enter required information
    Then User clicks on next button on construct portfolio page
    When User navigates to fee page and enter require data
    Then User navigates to portfolio details page and click on Account setup button
    When User navigates to account holder tab and enter require information
    Then User clicks on account information button
    When User fills additional account information
    Then User clicks on account features button
    Then User click on online access document delivery button without fundingpage
    When User navigates to online access document delivery tab and click on review all accounts button
    Then User navigates to review all accounts tab and click on proceed to create documents button
    Then User click on create documents button
    When User perform actions on view documents page and fetch require data
    When User clicks on Separate Documents and select Accounts Establishment option
    When User does the agent esignature with "by mail" method
    When User does the client signature
    When User wait for "30" seconds
    Then Navigate to tracking center page
    When User search item number and fetch description "before activation"

    Examples: 
      | SheetName | RowNumber |
      | NAW       |        5  |

  @navbar
  Scenario Outline: navbar_NAW_Agent_NewAccount_TDA_Self-Directed_Brokerage_Account_403_(b)
    When Login application
    When User clicks on the clients tab
    And User clicks on the add a client button
    And User navigates to client profile page and enter required information
    Then User clicks on next button on client profile page
    When User navigates to Construct portfolio page and enter required information
    Then User clicks on next button on construct portfolio page
    When User navigates to fee page and enter require data
    Then User navigates to portfolio details page and click on Account setup button
    When User navigates to account holder tab and enter require information
    Then User clicks on account information button
    When User fills additional account information
    Then User clicks on account features button
    Then User click on online access document delivery button without fundingpage
    When User navigates to online access document delivery tab and click on review all accounts button
    Then User navigates to review all accounts tab and click on proceed to create documents button
    Then User click on create documents button
    When User perform actions on view documents page and fetch require data
    When User clicks on Separate Documents and select Accounts Establishment option
    When User does the agent esignature with "in person" method
    When User does the client signature
    When User wait for "30" seconds
    Then Navigate to tracking center page
    When User search item number and fetch description "before activation"

    Examples: 
      | SheetName | RowNumber |
      | NAW       |        6  |

  @navbar
  Scenario Outline: navbar_FDD_Agent_NewAccount_FDD_Traditional_IRA
    When Login application
    When User clicks on the clients tab
    And User clicks on the add a client button
    And User navigates to client profile page and enter required information
    Then User clicks on next button on client profile page
    When User navigates to Construct portfolio page and enter required information
    Then User clicks on next button on construct portfolio page
    When User navigates to fee page and enter require data
    Then User navigates to portfolio details page and click on Account setup button
    When User navigates to account holder tab and enter require information
    Then User clicks on account information button
    When User fills additional account information
    Then User clicks on account features button
    Then User click on online access document delivery button without fundingpage
    When User navigates to online access document delivery tab and click on review all accounts button
    Then User navigates to review all accounts tab and click on proceed to create documents button
    Then User click on create documents button
    When User perform actions on view documents page and fetch require data
    When User clicks on Separate Documents and select Accounts Establishment option
    When User does the agent esignature with "in person" method
    When User does the client signature
    When User wait for "30" seconds
    Then Navigate to tracking center page
    When User search item number and fetch description "before activation"
    Examples: 
      | SheetName | RowNumber |
      | NAW       |        7  |
