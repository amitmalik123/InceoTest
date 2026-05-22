@smoke
Feature: Lead Creation Page - Field, Picklist and Validation Checks
    As a Salesforce user
    I want to create Leads in the Monarch Console app
    So that I can verify the Lead page fields, picklists, validations and happy path

    Background:
        Given I am logged in to Salesforce as the configured user
        And I have switched to the "Monarch Console" app
        And I have opened the Leads tab

    Scenario: Verify standard fields on the Lead creation page
        When I open the new Lead form
        Then the standard Lead fields should be displayed on the new Lead form

    Scenario: Verify dependent picklist values on the Lead creation page
        Then the dependent Lead Channel picklist values should be correct

    Scenario: Verify picklist values on the Lead creation page
        Then the Lead Source picklist values should be correct
        # And the Lead Status picklist values should be correct
        # And the Lead Type picklist values should be correct
        And the Marketing Funnel picklist values should be correct
        And the Registered Rep Type picklist values should be correct

    Scenario: Verify error messages for mandatory fields
        When I try to save the Lead without filling mandatory fields
        Then validation errors should be displayed for mandatory fields

    Scenario: Verify lookup fields on the Lead creation page
        Then the Lead lookup fields should be displayed

    Scenario: Verify CRD fields on the Lead creation page
        Then the CRD fields should be displayed

    # Scenario: Verify opportunity related fields on the Lead creation page
        # Then the opportunity related fields should be displayed

    Scenario: Create a Lead with valid data
        When I create a Lead with valid data
        Then the Lead detail page should display the new Lead's name

    Scenario: Verify the Lead path on the Leads page
        Then the Lead path stages should display the correct descriptions
