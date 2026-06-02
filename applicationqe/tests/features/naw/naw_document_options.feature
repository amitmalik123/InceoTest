
@retainAccount
Feature: NAW Document Options

  Scenario Outline: PRODENG-28727_NAW_Agent_NewAccount_TDA_retain_account
    When User is on Account Wizard tab and click on go button for New Client creation
    And User navigates to client profile page and enter required information
    Then User clicks on next button on client profile page
    When User navigates to Construct portfolio page and enter required information
    Then User clicks on next button on construct portfolio page
    When User navigates to fee page and enter require data
    Then User navigates to portfolio details page and click on Account setup button
    When User navigates to account holder tab and enter require information
    Then User clicks on account information button
    When User fills additional account information
    And User decides to retain existing account or not <retainAccount>
    When User navigates to online access document delivery tab and click on review all accounts button
    Then User navigates to review all accounts tab and click on proceed to create documents button
    Then User click on create documents button
    Then validate eSign button is presented on view documents page
    When User downloads the Accounts Establishment document
    Then Validate retain account in downloaded document

    Examples:
      | SheetName     | RowNumber | retainAccount |
      | retainAccount |        2  | Yes           |
      | retainAccount |        2  | No            |

  Scenario Outline: PRODENG-28727_NAW_Agent_NewAccount_Fidelity_retain_account
    When User is on Account Wizard tab and click on go button for New Client creation
    And User navigates to client profile page and enter required information
    Then User clicks on next button on client profile page
    When User navigates to Construct portfolio page and enter required information
    Then User clicks on next button on construct portfolio page
    When User navigates to fee page and enter require data
    Then User navigates to portfolio details page and click on Account setup button
    When User navigates to account holder tab and enter require information
    Then User clicks on account information button
    When User fills additional account information
    And User decides to retain existing account or not <retainAccount>
    When User navigates to online access document delivery tab and click on review all accounts button
    Then User navigates to review all accounts tab and click on proceed to create documents button
    Then User click on create documents button
    Then validate eSign button is presented on view documents page
    When User downloads the Accounts Establishment document
    Then Validate retain account in downloaded document

    Examples:
      | SheetName     | RowNumber | retainAccount |
      | retainAccount |       3   | Yes           |
      | retainAccount |       3   | No            |