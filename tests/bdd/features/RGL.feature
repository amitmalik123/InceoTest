Feature: Verify RGL page functionality
  As a user, I want to validate the functionalities of the RGL page.

  @regression @rgl 
  Scenario Outline: User login and navigate to RGL page
    Given User should login to the application and impersonate into an agent "<Agentid>"
    When user navigates to the RGL page "<Client name>"
    Then RGL page should be displayed

    Examples:
      | Agentid | Client name |
      | AG1634  | TBBK Test 4 |

  @regression @rgl
  Scenario Outline: Validate all RGL page headers are present
    Given User should login to the application and impersonate into an agent "<Agentid>"
    When user navigates to the RGL page "<Client name>"
    Then user  validate all the headers are present

    Examples:
      | Agentid | Client name |
      | AG1634  | TBBK Test 4 |

  @regression @rgl
  Scenario Outline: Validate RGL financial values
    Given User should login to the application and impersonate into an agent "<Agentid>"
    When user navigates to the RGL page "<Client name>"
    Then user validate the Costbasis,Proceeds,Gain/Loss

    Examples:
      | Agentid | Client name |
      | AG1634  | TBBK Test 4 |

 @regression 
 Scenario Outline: Verify Bancorp Link Redirects to Correct URL 
 Given User should login to the application and impersonate into an agent "<Agentid>" 
 When navigates to account information screen for cash advantage account
 Then user can see the updated Bancorp Link
 Examples:
      | Agentid | 
      | AG1634  | 

@regression 
 Scenario Outline: Confirm Outdated Bancorp URL Is Not Present 
 Given User should login to the application and impersonate into an agent "<Agentid>" 
 When navigates to account information screen for cash advantage account
 Then user can see Outdated Bancorp URL Is Not Present
 Examples:
      | Agentid | 
      | AG1634  | 

@regression 
 Scenario Outline: Validate No Impact to Other Account Types 
 Given User should login to the application and impersonate into an agent "<Agentid>" 
 When navigates to account information screen for non cash advantage account
 Then user cannot see any Bancorp URL Present
 Examples:
      | Agentid | 
      | AG1634  |       
