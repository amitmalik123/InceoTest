@e2e
Feature: Address Change

   @smoke @regression
  Scenario Outline: E2E Address Change GNW - CheckBox
    Given User with role "address" is loaded
    When I navigate to Clients menu
    And I click on Account List
    And User is on the accountlist tab and search with the accountNo
    And User should click on searched account and navigate to account wizard page
    And User should execute db query to get HouseholdID
    And User should add request header parameters For "ClientHousehold"
    And User should post the response for "ClientHousehold" endpoint
    Then User should verify status code 200 for ClientHousehold Accounts Display
    Then User to fetch Client Household API values
    # Then User should check custodianIDs to determine address change flows
    And User Should click on Update Addresses for "<Test>" and verify the page layout
    Then User should navigate To Address Change Edit Modal and click on Checkbox
    And User should fill all required data and click Save
    And User should verify the changes in Address For "<Test>" and click submit
    When User visits confirmation page to verify Address details for "<Test>"
    And User retrieves ItemNumber and clicks on Close Btn
    And User visits Update Addresses section to verify New Address details and click Cancel
    And User should click on clients tab and navigate to Client Information
    # Then User should verify that mailing Address from Client Information contains New Address details
    # And User visits Tracking center to verify Address details for "<Test>" and click View Btn

    Examples: 
      | SheetName     | RowNumber | Test     |
      | AddressChange |         2 | CheckBox |
