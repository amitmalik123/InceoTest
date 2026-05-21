@smoke
Feature: Lead Conversion - Validation rules
    As a Salesforce user
    I want to convert a Lead in the Monarch Console app
    So that I can verify the Lead Conversion validation rules

    Background:
        Given I am logged in to Salesforce as the configured user
        And I have switched to the "Monarch Console" app
        And I have opened the Leads tab

    Scenario: Lead Conversion validation for Corporate Referral / Corporate Advisor channels
        Given I have created a Lead with valid data
        When I attempt to convert the Lead with missing Broker Dealer Account and CRD Advisor
        Then a Lead Conversion validation error should be displayed
