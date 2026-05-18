@e2e @roth_conversion @critical
Feature: Roth IRA Conversion Flow
  As a financial advisor
  I want to convert a Traditional IRA to a Roth IRA
  So that I can help my clients with tax planning

  Background:
    Given the test data is loaded from CSV
    And I am on the login page

  @smoke @regression @conversion
  Scenario: Successfully complete Roth IRA conversion
    When I login with valid credentials
    Then I should be redirected to the home page
    
    When I navigate to Clients menu
    And I click on Account List
    Then I should see the Account List page
    
    When I search for the client
    And I select the client account
    Then I should see the Account Detail page
    
    When I click on Account Wizard
    And I select Funded account option
    And I select Move Assets Between Accounts
    And I select Roth IRA Conversion
    And I click Next on Account Wizard
    Then I should see the Roth Conversion page
    
    When I select the destination account
    And I verify the destination account is correct
    And I click Next on destination selection
    And I select Convert Portion option
    And I enter the conversion amount
    And I select Do Not Withhold for federal and state taxes
    And I click Next on conversion details
    Then I should either see STR review message or proceed to tracking
    
    When I navigate to Tracking Center
    Then I should see the Roth Conversion entry for the client
    And I should see "Roth Conversion" in the tracking details
    
    When I logout from the application
    Then I should be logged out successfully
