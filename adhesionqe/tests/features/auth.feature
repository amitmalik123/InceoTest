Feature: Authentication
    Verify that an authenticated storage state can be loaded and used.

    Scenario: Successfully load stored session
        Given an authenticated page
        When I refresh the page
        Then I should not be on the login page
