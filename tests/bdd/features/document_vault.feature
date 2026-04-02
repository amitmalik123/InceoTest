Feature: Verify Document Vault page functionality client level

  @regression @e2e @documentvault @newNavBar
  Scenario Outline: Validation of Document Vault page functionalities Client Level
    When Login application
    When User clicks on the clients tab
    When navigates to document vault with "<SheetName>" , <RowNumber>
    And switch the date filter dropdown to All
    And validate document vault column headers
    Then expand all headers and validate the download functionality
    And validate the Restore Default functionality

    Examples:
      | SheetName | RowNumber |
      | Econ      |         5 |
