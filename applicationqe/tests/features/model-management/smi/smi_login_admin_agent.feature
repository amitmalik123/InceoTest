@smoke @model_management @SMI_AdminAgent
Feature: Admin Agent Login and Menu Navigation
  As an admin agent
  I want to log in to SMI and navigate all menu bar sections including Admin
  So that I can verify the full menu workflow for admin agents

  Scenario: Successful SMI login as an admin agent
    Given I am on the login page of SMI
    When I login with valid credentials on the login page
    Then I print the title of the landing page
    Then I take a screenshot of the landing page
    Then I should see the main menu bar
    And I print the list of main navigation menu items
    And I print submenu options for each menu item
    And I click on each menu item one by one and verify
