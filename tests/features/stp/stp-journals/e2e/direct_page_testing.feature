@direct_page_testing @no_login
Feature: Direct Page Testing Without Login
    As a test automation engineer
    I want to test specific pages without going through login every time
    So that I can develop and debug page functionality more efficiently

    @landing_page @development
    Scenario: Test landing page functionality directly
        Given I am authenticated and on the "landing" page
        When I take a screenshot for verification
        Then I should be on the "landing" page
        And I can verify landing page elements are displayed correctly

    @journal_transfer @development  
    Scenario: Test journal transfer page directly
        Given I am authenticated and on the "journal_transfer" page
        When I take a screenshot for verification
        Then I should be on the "journal_transfer" page
        And I can verify transfer form elements are displayed

    @page_navigation @development
    Scenario: Navigate between pages with authentication maintained
        Given I am authenticated and ready to test any page
        When I navigate to the "clients" page
        And I take a screenshot for verification
        Then I should be on the "clients" page
        When I navigate to the "landing" page
        Then I should be on the "landing" page
        When I navigate to the "journal_transfer" page  
        Then I should be on the "journal_transfer" page

    @multi_page @development
    Scenario Outline: Test multiple pages directly
        Given I am authenticated and on the "<page_name>" page
        When I take a screenshot for verification
        Then I should be on the "<page_name>" page

        Examples:
            | page_name       |
            | landing         |
            | journal_transfer|  
            | clients         |