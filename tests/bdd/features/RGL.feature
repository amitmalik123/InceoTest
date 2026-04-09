Feature: Verify RGL page functionality
  As a user, I want to validate the functionalities of the RGL page.

  @regression @rgl 
  Scenario Outline: User login and navigate to RGL page
    Given user click on clients tab
    When user navigates to the RGL page "<ClientName>"
    Then RGL page should be displayed

    Examples:
      | SheetName  | RowNumber | ClientName  |
      | PR         |         2 | ClientName  |

  @regression @rgl
  Scenario Outline: Validate all RGL page headers are present
    Given user click on clients tab
    When user navigates to the RGL page "<Client name>"
    Then user  validate all the headers are present

    Examples:
      | SheetName  | RowNumber | Client name |
      | PR         |         2 | ClientName |

  @regression @rgl
  Scenario Outline: Validate RGL financial values
    Given user click on clients tab
    When user navigates to the RGL page "<Client name>"
    Then user validate the Costbasis,Proceeds,Gain/Loss

    Examples:
      | SheetName  | RowNumber | Client name |
      | PR         |         2 | ClientName |

  @regression
  Scenario Outline: Verify Bancorp Link Redirects to Correct URL
    Given navigates to account information screen for cash advantage account
    Then user can see the updated Bancorp Link

    Examples:
      | SheetName | RowNumber |
      | PR        |         2 |

  @regression
  Scenario Outline: Confirm Outdated Bancorp URL Is Not Present
    Given navigates to account information screen for cash advantage account
    Then user can see Outdated Bancorp URL Is Not Present

    Examples:
      | SheetName | RowNumber |
      | PR        |         2 |

  @regression
  Scenario Outline: Validate No Impact to Other Account Types
    Given navigates to account information screen for non cash advantage account
    Then user cannot see any Bancorp URL Present

    Examples:
      | SheetName | RowNumber |
      | PR        |         2 |

  # @regression @rgl @newNavBar
  # Scenario Outline: User login and navigate to RGL page with new navbar
  #   When Login application
  #   When User clicks on the clients tab
  #   When user navigates to the new navbar RGL page using "<SheetName>" , <RowNumber>
  #   Then new navbar RGL page should be displayed
  #
  #   Examples:
  #     | SheetName | RowNumber |
  #     | PR        |         2 |

  # @regression @rgl @newNavBar
  # Scenario Outline: Validate all RGL page headers are present with new navbar
  #   When Login application
  #   When User clicks on the clients tab
  #   When user navigates to the new navbar RGL page using "<SheetName>" , <RowNumber>
  #   Then user  validate all the headers are present
  #
  #   Examples:
  #     | SheetName | RowNumber |
  #     | PR        |         2 |

  # @regression @rgl @newNavBar
  # Scenario Outline: Validate RGL financial values with new navbar
  #   When Login application
  #   When User clicks on the clients tab
  #   When user navigates to the new navbar RGL page using "<SheetName>" , <RowNumber>
  #   Then user validate the Costbasis,Proceeds,Gain/Loss
  #
  #   Examples:
  #     | SheetName | RowNumber |
  #     | PR        |         2 |