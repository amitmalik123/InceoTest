Feature: Verify TMS page functionality
  As a user, I want to validate the functionalities of the TMS page.

  @regression @tms
  Scenario Outline: User login and navigate to TMS page
    Given User should login to the application and impersonate into an agent "<Agentid>"
    When user navigates to the TMS page "<Account number>"
    Then TMS page should be displayed

    Examples:
      | Agentid | Account number |
      | AGAXNV  | 13190618 |

  @regression @tms
  Scenario Outline: User login and validate TMS values for another test case
    Given User should login to the application and impersonate into an agent "<Agentid>"
    When user navigates to the TMS page "<Account number>"
    And validate the Federal Short Term and Federal Long Term

    Examples:
      | Agentid | Account number |
      | AGAXNV  | 13190618 |

  @regression @tms
  Scenario Outline: User login and validate TMS gain budget values
    Given User should login to the application and impersonate into an agent "<Agentid>"
    When user navigates to the TMS page "<Account number>"
    And validate the Short Term Gain Budget and Long Term Gain Budget

    Examples:
      | Agentid | Account number |
      | AGAXNV  | 13190618 |

  @regression @tms
  Scenario Outline: User login and validate TMS account fields are alphanumeric and not editable
    Given User should login to the application and impersonate into an agent "<Agentid>"
    When user navigates to the TMS page "<Account number>"
    Then validate the account name and account number are alphanumeric and not editable

    Examples:
      | Agentid | Account number |
      | AGAXNV  | 13190618 |

  
  
