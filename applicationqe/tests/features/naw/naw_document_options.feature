
Feature: retain account in NAW

  @documentsVerification
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
    When User download the combined document
    Then Validate form bundle documents in downloaded document

    Examples: 
      | SheetName | RowNumber | retainAccount |
      | documentsVerification       |        2  | Yes           |
    #  | documentsVerification       |        3  | No            |


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
    When User download the combined document
    Then Validate form bundle documents in downloaded document

    Examples: 
      | SheetName | RowNumber | retainAccount |
      | documentsVerification       |       4  | Yes           |
      | documentsVerification       |       5  | No            |

 
  Scenario Outline: NAW_Agent_NewAccount_GNW
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
    When User download the combined document
    Then Validate form bundle documents in downloaded document

    Examples: 
      | SheetName | RowNumber |
      | documentsVerification       |        6  |


  Scenario Outline: NAW_Agent_NewAccount_PRS
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
    Then User clicks on account features button
    Then User clicks on funding method button
    When User navigates to funding tab and enter funding method
    Then User click on online access document delivery button
    When User navigates to online access document delivery tab and click on review all accounts button
    Then User navigates to review all accounts tab and click on proceed to create documents button
    Then User click on create documents button
    When User download the combined document
    Then Validate form bundle documents in downloaded document

    Examples: 
      | SheetName | RowNumber |
      | documentsVerification       |        7  |      