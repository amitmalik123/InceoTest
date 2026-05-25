@model_management @SMI_Reallocation
Feature: SMI Reallocation - End-to-End Reallocation Workflow
  As an internal agent
  I want to create and submit a reallocation for a strategist
  So that an executive agent can review and approve it

  Scenario: Internal agent creates reallocation and executive agent approves
    Given I am logged into SMI as an internal agent
    When I perform a new reallocation for strategist "Apollo - (APOLLO)"
    And I submit the reallocation for approval
    Then I log out of SMI
    And I login as executive agent
    And I verify the executive agent landing page
