Feature: Verify Document Vault page functionality client level

  # @regression @e2e @documentvault @newNavBar
  # Scenario Outline: Validation of Document Vault page functionalities Client Level
  #   When Login application
  #   When User clicks on the clients tab
  #   When navigates to document vault with "<SheetName>" , <RowNumber>
  #   And switch the date filter dropdown to All
  #   And validate document vault column headers
  #   Then expand all headers and validate the download functionality
  #   And validate the Restore Default functionality
  #
  #   Examples:
  #     | SheetName | RowNumber |
  #     | PR        |         2 |

  @regression @e2e @documentvault 
  Scenario: Validation of Document Vault page functionalities Agent Level
    Given user click on clients tab
    When navigates to Document vault 
    And validate all the dropdowns are enabled for user interaction
    And click documenttype dropdown and select QPR document
    Then validate find button is enabled for user interaction

  @regression @e2e @documentvault
  Scenario: Validate filter actions and Find button state
    Given user click on clients tab
    When navigates to Document vault
    And click documenttype dropdown and select QPR document
    Then validate find button is enabled for user interaction
    When user clicks Select All filters
    Then verify all filters are selected
    When user clicks Clear All filters
    And verify all filters are cleared
    Then validate View selected and Save selected buttons are enabled or disabled based on filter selection

  @regression @e2e @documentvault
  Scenario: Validate market Value Reports
    Given user click on clients tab
    When navigates to Document vault
    And click documenttype dropdown and select market value report
    And validate the Quarter dropdown should be visible for user interaction
    Then validate find button is enabled for user interaction
    When user clicks Select All filters

  @regression @e2e @documentvault
  Scenario: Validate download functionality of QPR
    Given user click on clients tab
    When navigates to Document vault
    And click documenttype dropdown and select QPR document
    Then validate find button is enabled for user interaction
    When user clicks Select All filters
    Then the user clicks Save Selected and verifies a QPR-year-quarter ZIP download
    And select a single document and click Save selected
    Then user verifies a QPR-year-quarter PDF download

    
