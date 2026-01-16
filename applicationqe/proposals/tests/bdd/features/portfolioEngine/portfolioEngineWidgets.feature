@smoke @regression @portfolioEngine @widgetTests
Feature: Portfolio Engine Widgets
    Scenario: Verify Portfolio Engine Widgets Load
        Given I am logged into the application
        Given I am on the Portfolio Engine page
        Given I have created a portfolio with strategies
        When I enable all Portfolio Engine widgets
        Then the Portfolio Engine widgets should load successfully