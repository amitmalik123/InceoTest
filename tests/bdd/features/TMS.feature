Feature: Verify TMS page functionality
  As a user, I want to validate the functionalities of the TMS page.

  @regression @tms
  Scenario Outline: User login and navigate to TMS page
    Given User should login to the application and impersonate into an agent "<SheetName>" , <RowNumber>
    When user navigates to the TMS page "<Account number>"
    Then TMS page should be displayed

    Examples:
      | SheetName | RowNumber | Account number |
      | Econ      |         6 | AccountNumber |

  @regression @tms
  Scenario Outline: User login and validate TMS values for another test case
    Given User should login to the application and impersonate into an agent "<SheetName>" , <RowNumber>
    When user navigates to the TMS page "<Account number>"
    And validate the Federal Short Term and Federal Long Term

    Examples:
      | SheetName | RowNumber | Account number |
      | Econ      |         6 | AccountNumber |

  @regression @tms
  Scenario Outline: User login and validate TMS gain budget values
    Given User should login to the application and impersonate into an agent "<SheetName>" , <RowNumber>
    When user navigates to the TMS page "<Account number>"
    And validate the Short Term Gain Budget and Long Term Gain Budget

    Examples:
      | SheetName | RowNumber | Account number |
      | Econ      |         6 | AccountNumber |

  @regression @tms
  Scenario Outline: User login and validate TMS account fields are alphanumeric and not editable
    Given User should login to the application and impersonate into an agent "<SheetName>" , <RowNumber>
    When user navigates to the TMS page "<Account number>"
    Then validate the account name and account number are alphanumeric and not editable

    Examples:
      | SheetName | RowNumber | Account number |
      | Econ      |         6 | AccountNumber |

  @regression @tms @newNavBar
  Scenario Outline: User login and navigate to TMS page with new navbar
    When Login application
    When User clicks on the clients tab
    When user navigates to the new navbar TMS page using "<SheetName>" , <RowNumber>
    Then TMS page should be displayed

    Examples:
      | SheetName | RowNumber |
      | Econ      |         6 |

  @regression @tms @newNavBar
  Scenario Outline: navigate to TMS page with new navbar validate Federal Short Term and Federal Long Term
    When Login application
    When User clicks on the clients tab
    When user navigates to the new navbar TMS page using "<SheetName>" , <RowNumber>
    And validate the Federal Short Term and Federal Long Term

    Examples:
      | SheetName | RowNumber |
      | Econ      |         6 |      
  
  @regression @tms @newNavBar
  Scenario Outline: navigate to TMS page validate the Short Term and Long Term Gain Budget
    When Login application
    When User clicks on the clients tab
    When user navigates to the new navbar TMS page using "<SheetName>" , <RowNumber>
    And validate the Short Term Gain Budget and Long Term Gain Budget

    Examples:
      | SheetName | RowNumber |
      | Econ      |         6 |

  @regression @tms @newNavBar
  Scenario Outline: navigate to TMS page validate the account name and account number
    When Login application
    When User clicks on the clients tab
    When user navigates to the new navbar TMS page using "<SheetName>" , <RowNumber>
    Then validate the account name and account number are alphanumeric and not editable
    Examples:
      | SheetName | RowNumber |
      | Econ      |         6 |