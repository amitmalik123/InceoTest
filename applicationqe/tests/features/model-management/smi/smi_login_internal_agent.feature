@smoke @model_management @SMI_InternalAgent
Feature: Internal Agent Login and Menu Navigation
  As an internal agent
  I want to log in to SMI and navigate all menu bar sections
  So that I can verify the full menu workflow for internal agents

  Scenario: Successful SMI login as an internal agent
    Given I am on the login page of SMI
    When I login with valid credentials on the login page
    Then I print the title of the landing page
    Then I take a screenshot of the landing page
    Then I should see the main menu bar
    And I print the list of main navigation menu items
    And I print submenu options for each menu item
    And I click on each menu item one by one and verify
