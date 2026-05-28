@model_management @SMI_Rebalance
Feature: SMI Rebalance - End-to-End Rebalance Workflow
  As an internal agent
  I want to create and submit a rebalance for a strategist
  So that an executive agent can review and approve it

  Scenario: Internal agent creates rebalance and executive agent approves
    Given I am logged into SMI as an internal agent
    When I perform a new rebalance for strategist "Apollo - (APOLLO)"
    And I submit the rebalance for approval
    Then I log out of SMI
    And I login as executive agent
    And I verify the executive agent landing page
