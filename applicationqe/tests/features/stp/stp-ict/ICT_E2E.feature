@e2e @ict @critical
Feature: ICT(Investment change tool) Flow
  As a financial advisor
  I want to change investement model

  Background:
    Given the test data is loaded from CSV
    And I am on the login page

  @smoke @regression @ICT
  Scenario: Successfully complete ICT
    When I login with valid credentials
    Then I should be redirected to the home page
    
    When I navigate to Clients menu
    And I click on Account List
    Then I should see the Account List page
    
    When I search for the client
    And I select the client account
    Then I should see the Account Detail page
    
    When I click on Account Wizard
    And I click on Change Investments
    And I click on Source account
    And I click on Select Destination Investments dropdown
    And I select New Investment
    And I select Single Strategy Account under Open Design
    And I choose "AssetMark Asset Builder, Profile 2, Conservative" in Choose a New Investment
    And I click OK on Select Destination
    And I select 100% radio button
    And I click Next on Select Destination
    And I select account number option
    And I answer Client Suitability questions
    And I click Next on Client Suitability
    And I enter fee on Create Fees page
    And I click Next on Create Fees
   #And I click Enroll on Tax Management page
   #And I click Next on Tax Management
   #And I select Medium risk level
   #And I click Continue on Tax Management Enroll
   #And I click Yes on the confirmation dialog
    And I click Next on ICT Summary
    Then I should see all required ICT forms
    When I click Complete and Submit on Create Forms
    And I select Proceed without client signature
    Then User should be redirected to the DocuSign page
    And Verify docusign Review and continue dialog text
    And Verify As_authorized_by stamp presence
    When User confirm and Continue the docusign Review and continue dialog
    And User Finish the DocuSign process
    Then Verify request pop up
    When User click on D number
    Then User should be redirected to Tracking Center Item Detail page
    And Item Detail D number should be same as request submitted pop up D number
    And Verify Tracking Center Item Detail status should be "Document Submitted"
    Then I should see the item number as B# in Tracking Center


  