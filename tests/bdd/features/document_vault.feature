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
    And navigates to Document vault 
    Then validate all the dropdowns are enabled for user interaction