Feature: Manage Beneficiaries flow
  As a financial advisor
  I want to manage beneficiaries for client accounts
  So that I can add, edit, or delete beneficiaries as per requirement

  # Background: User navigates to Manage Beneficiaries page
  #   Given User with role "manage_bene" is loaded
  #   When User should click on user profile and sign out
  #   When I navigate to Clients menu in new nav bar
  #   And I click on Account List on new nav bar
  #   And User switch to new iframe for account list page
  #   And User is on the accountlist tab and search with the accountNo
  #   And User should click on searched account and navigate to manage account page
  #   And User should click on Manage Beneficiaries link on Account Detail Page and redirect to manage bene page

  @manage_bene
  Scenario Outline: Add Individual Primary Beneficiary - Electronic Signature flow
    Given User with role "manage_bene" is loaded
    When User should select and click and redirect to bene page
    And User should verify all allocation sections show 100% total and save to context
    When User should click on Add button and redirected to add beneficiary page
    And User should select beneficiary type as "<bene_type>" and relationship type as "<relation>" and enter first name "<first_name>" and last name "<last_name>" and enter SSN "<ssn>" and DOB "<dob>" and select at least one account
    And User should click Save button and user is redireted back to manage beneficiaries page
    And User should verify befinaficieries is added successfully on manage beneficiaries page with correct information
    And Beneficiary should have "ADDED" badge displayed
    When User selects "Obtain Electronic Client Signature(s)" signature option
    Then "Continue to e-Signature Details" button should be enabled
    When User clicks on "Continue to e-Signature Details" button
    Then User should be navigated to e-Signature details page
    When User selects "<method>" as the signature method on e-Signature Details page
    When User enters email "<email>" and phone "<phone>" on e-Signature Details page
    And User checks consent checkbox and verifies Continue to Review button state
    And User clicks Continue to Review to trigger validation
    Then User should verify added beneficiary is displayed on Review page
    When User clicks Submit to Advisor button
    Then User should be redirected to DocuSign page

    Examples:
      | bene_type  | relation    | first_name | last_name | ssn         | dob        | email              | phone      | method    |
      | New        | Spouse      | Test       | Brown     | 444-55-6666 | 07/22/1975 | test@example.com   | 5555551234 | By Email  |
      | New        | Spouse      | Test       | Brown     | 444-55-6666 | 07/22/1975 | test@example.com   | 5555551234 | In Person |
      | New        | Non-Spouse  | Test       | Johnson   | 555-66-7777 | 03/10/1980 | test2@example.com  | 5555552345 | By Email  |
      | New        | Non-Spouse  | Test       | Johnson   | 555-66-7777 | 03/10/1980 | test2@example.com  | 5555552345 | In Person |
      | New        | Trust       | Michael    | Davis     | 666-77-8888 | 09/25/1975 | test3@example.com  | 5555553456 | By Email  |
      | New        | Trust       | Michael    | Davis     | 666-77-8888 | 09/25/1975 | test3@example.com  | 5555553456 | In Person |
      | New        | Entity      | Lisa       | Miller    | 777-88-9999 | 11/12/1982 | test4@example.com  | 5555554567 | By Email  |
      | New        | Entity      | Lisa       | Miller    | 777-88-9999 | 11/12/1982 | test4@example.com  | 5555554567 | In Person |

  @manage_bene
  Scenario Outline: Add Individual Primary Beneficiary - Print Signature flow
    Given User with role "manage_bene" is loaded
    When User should select and click and redirect to bene page
    And User should verify all allocation sections show 100% total and save to context
    When User should click on Add button and redirected to add beneficiary page
    And User should select beneficiary type as "<bene_type>" and relationship type as "<relation>" and enter first name "<first_name>" and last name "<last_name>" and enter SSN "<ssn>" and DOB "<dob>" and select at least one account
    And User should click Save button and user is redireted back to manage beneficiaries page
    And User should verify befinaficieries is added successfully on manage beneficiaries page with correct information
    And Beneficiary should have "ADDED" badge displayed
    When User selects "Print to Obtain Physical Client Signature(s)" signature option
    Then "Continue to Review" button should be enabled
    When User clicks on "Continue to Review" button
    Then User should be navigated to Review page directly
    Then User should verify added beneficiary is displayed on Review page
    When User clicks Submit to Advisor button
    Then User should be redirected to DocuSign page

    Examples:
      | bene_type  | relation    | first_name | last_name | ssn         | dob        |
      | New        | Spouse      | Test       | Brown     | 444-55-6666 | 07/22/1975 |
      | New        | Non-Spouse  | Test       | Johnson   | 555-66-7777 | 03/10/1980 |
      | New        | Trust       | Michael    | Davis     | 666-77-8888 | 09/25/1975 |
      | New        | Entity      | Lisa       | Miller    | 777-88-9999 | 11/12/1982 |
      | New        | Trust       | James      | Wilson    | 888-99-0000 | 02/14/1978 |
      | New        | Entity      | Patricia   | Anderson  | 999-00-1111 | 04/08/1988 |

  @manage_bene
  Scenario Outline: Add Existing Beneficiary (Spouse/Non-Spouse) - Electronic Signature flow
    Given User with role "manage_bene" is loaded
    When User should select and click and redirect to bene page
    And User should verify all allocation sections show 100% total and save to context
    And User captures first "<relation>" beneficiary name from manage bene page
    When User should click on Add button and redirected to add beneficiary page
    When User selects "<bene_type>" beneficiary from the dropdown and captures the name
    Then Spouse/Non-Spouse beneficiary personal fields should be pre-filled and disabled
    When User should select account "<account_number>" as "<designation>"
    And User should click Save button and user is redireted back to manage beneficiaries page
    And Beneficiary should have "ADDED" badge displayed
    Then User should verify the existing beneficiary appears in the "<designation>" section
    When User selects "Obtain Electronic Client Signature(s)" signature option
    Then "Continue to e-Signature Details" button should be enabled
    When User clicks on "Continue to e-Signature Details" button
    Then User should be navigated to e-Signature details page
    When User selects "<method>" as the signature method on e-Signature Details page
    When User enters email "<email>" and phone "<phone>" on e-Signature Details page
    And User checks consent checkbox and verifies Continue to Review button state
    And User clicks Continue to Review to trigger validation
    Then User should verify added beneficiary is displayed on Review page
    When User clicks Submit to Advisor button
    Then User should be redirected to DocuSign page

    Examples:
      | bene_type | relation   | account_number | designation | email              | phone      | method    |
      | Existing  | Spouse     | 2              | Contingent  | test@example.com   | 5555551234 | By Email  |
      | Existing  | Spouse     | 2              | Contingent  | test@example.com   | 5555551234 | In Person |
      | Existing  | Non-Spouse | 2              | Contingent  | test@example.com   | 5555551234 | By Email  |
      | Existing  | Non-Spouse | 2              | Contingent  | test@example.com   | 5555551234 | In Person |

  
  @manage_bene
  Scenario Outline: Add Existing Beneficiary (Spouse/Non-Spouse) - Electronic Signature flow - Verify Trust and Entity are disabled and relationship type is toggleable
    Given User with role "manage_bene" is loaded
    When User should select and click and redirect to bene page
    And User should verify all allocation sections show 100% total and save to context
    And User captures first "<relation>" beneficiary name from manage bene page
    When User should click on Add button and redirected to add beneficiary page
    When User selects "<bene_type>" beneficiary from the dropdown and captures the name
    Then Trust and Entity relationship options should be disabled
    When User switches to the opposite relationship type
    Then Spouse/Non-Spouse beneficiary personal fields should be pre-filled and disabled
    When User should select account "<account_number>" as "<designation>"
    And User should click Save button and user is redireted back to manage beneficiaries page
    And Beneficiary should have "ADDED" badge displayed
    Then User should verify the existing beneficiary appears in the "<designation>" section
    When User selects "Obtain Electronic Client Signature(s)" signature option
    Then "Continue to e-Signature Details" button should be enabled
    When User clicks on "Continue to e-Signature Details" button
    Then User should be navigated to e-Signature details page
    When User selects "<method>" as the signature method on e-Signature Details page
    When User select first account holder, enters email "<email>" and phone "<phone>" on e-Signature Details page
    And User checks consent checkbox and verifies Continue to Review button state
    And User clicks Continue to Review to trigger validation
    Then User should verify beneficiary is present on Review page
    When User clicks Submit to Advisor button
    Then User should be redirected to DocuSign page

     Examples:
      | bene_type | relation   | account_number | designation | email              | phone      | method    |
      | Existing  | Spouse     | 2              | Contingent  | test@example.com   | 5555551234 | By Email  |
      | Existing  | Spouse     | 2              | Contingent  | test@example.com   | 5555551234 | In Person |
      | Existing  | Non-Spouse | 2              | Contingent  | test@example.com   | 5555551234 | By Email  |
      | Existing  | Non-Spouse | 2              | Contingent  | test@example.com   | 5555551234 | In Person |

  @manage_bene
  Scenario Outline: Add Existing Beneficiary (Trust/Entity) - Electronic Signature flow - Verify Spouse and Non-Spouse are disabled
    Given User with role "manage_bene" is loaded
    When User should select and click and redirect to bene page
    And User should verify all allocation sections show 100% total and save to context
    And User captures first "<relation>" beneficiary name from manage bene page
    When User should click on Add button and redirected to add beneficiary page
    When User selects "<bene_type>" beneficiary from the dropdown and captures the name
    Then Spouse and Non-Spouse relationship options should be disabled
    Then Trust/Entity beneficiary name field should be pre-filled and disabled
    When User should select account "<account_number>" as "<designation>"
    And User should click Save button and user is redireted back to manage beneficiaries page
    And Beneficiary should have "ADDED" badge displayed
    Then User should verify the existing beneficiary appears in the "<designation>" section
    When User selects "Obtain Electronic Client Signature(s)" signature option
    Then "Continue to e-Signature Details" button should be enabled
    When User clicks on "Continue to e-Signature Details" button
    Then User should be navigated to e-Signature details page
    When User selects "<method>" as the signature method on e-Signature Details page
    When User enters email "<email>" and phone "<phone>" on e-Signature Details page
    And User checks consent checkbox and verifies Continue to Review button state
    And User clicks Continue to Review to trigger validation
    Then User should verify beneficiary is present on Review page
    When User clicks Submit to Advisor button
    Then User should be redirected to DocuSign page

    Examples:
      | bene_type | relation | account_number | designation | email            | phone      | method    |
      | Existing  | Trust    | 1              | Contingent  | test@example.com | 5555551234 | By Email  |
      | Existing  | Trust    | 1              | Contingent  | test@example.com | 5555551234 | In Person |
      | Existing  | Entity   | 2              | Contingent  | test@example.com | 5555551234 | By Email  |
      | Existing  | Entity   | 2              | Contingent  | test@example.com | 5555551234 | In Person |


  @manage_bene
  Scenario Outline: Add Existing Beneficiary (Trust/Entity) - Electronic Signature flow
    Given User with role "manage_bene" is loaded
    When User should select and click and redirect to bene page
    And User should verify all allocation sections show 100% total and save to context
    And User captures first "<relation>" beneficiary name from manage bene page
    When User should click on Add button and redirected to add beneficiary page
    When User selects "<bene_type>" beneficiary from the dropdown and captures the name
    Then Trust/Entity beneficiary name field should be pre-filled and disabled
    When User should select account "<account_number>" as "<designation>"
    And User should click Save button and user is redireted back to manage beneficiaries page
    And Beneficiary should have "ADDED" badge displayed
    Then User should verify the existing beneficiary appears in the "<designation>" section
    When User selects "Obtain Electronic Client Signature(s)" signature option
    Then "Continue to e-Signature Details" button should be enabled
    When User clicks on "Continue to e-Signature Details" button
    Then User should be navigated to e-Signature details page
    When User selects "<method>" as the signature method on e-Signature Details page
    When User enters email "<email>" and phone "<phone>" on e-Signature Details page
    And User checks consent checkbox and verifies Continue to Review button state
    And User clicks Continue to Review to trigger validation
    Then User should verify added beneficiary is displayed on Review page
    When User clicks Submit to Advisor button
    Then User should be redirected to DocuSign page

    Examples:
      | bene_type | relation | account_number | designation | email              | phone      | method    |
      | Existing  | Trust    | 1              | Contingent  | test@example.com   | 5555551234 | By Email  |
      | Existing  | Trust    | 1              | Contingent  | test@example.com   | 5555551234 | In Person |
      # | Existing  | Entity   | 2              | Contingent  | test@example.com   | 5555551234 | By Email  |
      # | Existing  | Entity   | 2              | Contingent  | test@example.com   | 5555551234 | In Person |

  @manage_bene
  Scenario Outline: Add Existing Beneficiary - Print Signature flow
    Given User with role "manage_bene" is loaded
    When User should select and click and redirect to bene page
    And User should verify all allocation sections show 100% total and save to context
    And User captures first "<relation>" beneficiary name from manage bene page
    When User should click on Add button and redirected to add beneficiary page
    When User selects "<bene_type>" beneficiary from the dropdown and captures the name
    Then Beneficiary personal fields should be pre-filled and disabled
    When User should select account "<account_number>" as "<designation>"
    And User should click Save button and user is redireted back to manage beneficiaries page
    And Beneficiary should have "ADDED" badge displayed
    Then User should verify the existing beneficiary appears in the "<designation>" section
    When User selects "Print to Obtain Physical Client Signature(s)" signature option
    Then "Continue to Review" button should be enabled
    When User clicks on "Continue to Review" button
    Then User should be navigated to Review page directly
    Then User should verify added beneficiary is displayed on Review page
    When User clicks Submit to Advisor button
    Then User should be redirected to DocuSign page

    Examples:
      | bene_type | relation   | account_number | designation |
      | Existing  | Spouse     | 2              | Contingent  |
      | Existing  | Non-Spouse | 2              | Contingent  |
      | Existing  | Trust      | 1              | Contingent  |
      # | Existing  | Entity     | 2              | Contingent  |

@manage_bene
  Scenario Outline: Edit Existing Beneficiary - Spouse/Non-Spouse - Electronic Signature flow - Verify fields are disabled and relationship type is toggleable
    Given User with role "manage_bene" is loaded
    When User should select and click and redirect to bene page
    And User should verify all allocation sections show 100% total and save to context
    When User captures first "<relation>" beneficiary name from manage bene page, clicks edit button, captures info, and navigates to edit page
    Then Trust and Entity relationship options should be disabled
    Then Beneficiary personal fields should be pre-filled and disabled
    When User switches to the opposite relationship type
    Then Spouse/Non-Spouse beneficiary personal fields should be pre-filled and disabled
    And User should click Save button and user is redireted back to manage beneficiaries page
    And Beneficiary should have "EDITED" badge displayed
    Then User should verify the existing beneficiary appears in the "<designation>" section
    When User selects "Obtain Electronic Client Signature(s)" signature option
    Then "Continue to e-Signature Details" button should be enabled
    When User clicks on "Continue to e-Signature Details" button
    Then User should be navigated to e-Signature details page
    When User selects "<method>" as the signature method on e-Signature Details page
    And User select first account holder, enters email "<email>" and phone "<phone>" on e-Signature Details page
    And User checks consent checkbox and verifies Continue to Review button state
    And User clicks Continue to Review to trigger validation
    Then User should verify beneficiary is present on Review page
    When User clicks Submit to Advisor button
    Then User should be redirected to DocuSign page

    Examples:
      | bene_type | relation   | account_number | designation | method    | email              | phone      |
      | Existing  | Non-Spouse | 1              | Primary     | By Email  | test@example.com   | 5555551234 |
      | Existing  | Spouse     | 2              | Primary     | In Person | test@example.com   | 5555551234 |

@manage_bene
  Scenario Outline: Edit Existing Beneficiary - Spouse/Non-Spouse - Print Physical Signature flow - Verify fields are disabled and relationship type is toggleable
    Given User with role "manage_bene" is loaded
    When User should select and click and redirect to bene page
    And User should verify all allocation sections show 100% total and save to context
    When User captures first "<relation>" beneficiary name from manage bene page, clicks edit button, captures info, and navigates to edit page
    Then Trust and Entity relationship options should be disabled
    Then Beneficiary personal fields should be pre-filled and disabled
    When User switches to the opposite relationship type
    Then Spouse/Non-Spouse beneficiary personal fields should be pre-filled and disabled
    And User should click Save button and user is redireted back to manage beneficiaries page
    And Beneficiary should have "EDITED" badge displayed
    Then User should verify the existing beneficiary appears in the "<designation>" section
    When User selects "Print to Obtain Physical Client Signature(s)" signature option
    Then "Continue to Review" button should be enabled
    When User clicks on "Continue to Review" button
    Then User should be navigated to Review page directly
    Then User should verify beneficiary is present on Review page
    When User clicks Submit to Advisor button
    Then User should be redirected to DocuSign page

    Examples:
      | bene_type | relation   | account_number | designation |
      | Existing  | Non-Spouse | 1              | Primary     |
      | Existing  | Spouse     | 2              | Primary     |
  
  @manage_bene
  Scenario Outline: Add with Edit Modal Existing Beneficiary (Spouse/Non-Spouse) - Electronic Signature flow
    Given User with role "manage_bene" is loaded
    When User should select and click and redirect to bene page
    And User should verify all allocation sections show 100% total and save to context
    When User captures first "<relation>" beneficiary name from manage bene page, clicks edit button, captures info, and navigates to edit page
    Then Spouse/Non-Spouse beneficiary personal fields should be pre-filled and disabled
    When User should select account "<account_number>" as "<designation>"
    And User should click Save button and user is redireted back to manage beneficiaries page
    And Beneficiary should have "ADDED" badge displayed
    Then User should verify the existing beneficiary appears in the "<designation>" section
    When User selects "Obtain Electronic Client Signature(s)" signature option
    Then "Continue to e-Signature Details" button should be enabled
    When User clicks on "Continue to e-Signature Details" button
    Then User should be navigated to e-Signature details page
    When User selects "<method>" as the signature method on e-Signature Details page
    When User enters email "<email>" and phone "<phone>" on e-Signature Details page
    And User checks consent checkbox and verifies Continue to Review button state
    And User clicks Continue to Review to trigger validation
    Then User should verify added beneficiary is displayed on Review page
    When User clicks Submit to Advisor button
    Then User should be redirected to DocuSign page

    Examples:
      | bene_type | relation   | account_number | designation | email              | phone      | method    |
      | Existing  | Non-Spouse | 2              | Contingent  | test@example.com   | 5555551234 | By Email  |
      | Existing  | Spouse     | 2              | Primary     | test@example.com   | 5555551234 | In Person |

  @manage_bene
  Scenario Outline: Add with Edit Modal Existing Beneficiary (Trust/Entity) - Electronic Signature flow
    Given User with role "manage_bene" is loaded
    When User should select and click and redirect to bene page
    And User should verify all allocation sections show 100% total and save to context
    When User captures first "<relation>" beneficiary name from manage bene page, clicks edit button, captures info, and navigates to edit page
    Then Spouse and Non-Spouse relationship options should be disabled
    Then Trust/Entity beneficiary name field should be pre-filled and disabled
    When User should select account "<account_number>" as "<designation>"
    And User should click Save button and user is redireted back to manage beneficiaries page
    And Beneficiary should have "ADDED" badge displayed
    Then User should verify the existing beneficiary appears in the "<designation>" section
    When User selects "Obtain Electronic Client Signature(s)" signature option
    Then "Continue to e-Signature Details" button should be enabled
    When User clicks on "Continue to e-Signature Details" button
    Then User should be navigated to e-Signature details page
    When User selects "<method>" as the signature method on e-Signature Details page
    When User enters email "<email>" and phone "<phone>" on e-Signature Details page
    And User checks consent checkbox and verifies Continue to Review button state
    And User clicks Continue to Review to trigger validation
    Then User should verify added beneficiary is displayed on Review page
    When User clicks Submit to Advisor button
    Then User should be redirected to DocuSign page

    Examples:
      | bene_type | relation | account_number | designation | email            | phone      | method    |
      | Existing  | Trust    | 1              | Contingent  | test@example.com | 5555551234 | By Email  |
      # | Existing  | Entity   | 2              | Contingent  | test@example.com | 5555551234 | In Person |

  @manage_bene
  Scenario Outline: Add with Edit Modal Existing Beneficiary (Spouse/Non-Spouse) - Print Physical Signature flow
    Given User with role "manage_bene" is loaded
    When User should select and click and redirect to bene page
    And User should verify all allocation sections show 100% total and save to context
    When User captures first "<relation>" beneficiary name from manage bene page, clicks edit button, captures info, and navigates to edit page
    Then Spouse/Non-Spouse beneficiary personal fields should be pre-filled and disabled
    When User should select account "<account_number>" as "<designation>"
    And User should click Save button and user is redireted back to manage beneficiaries page
    And Beneficiary should have "ADDED" badge displayed
    Then User should verify the existing beneficiary appears in the "<designation>" section
    When User selects "Print to Obtain Physical Client Signature(s)" signature option
    Then "Continue to Review" button should be enabled
    When User clicks on "Continue to Review" button
    Then User should be navigated to Review page directly
    Then User should verify added beneficiary is displayed on Review page
    When User clicks Submit to Advisor button
    Then User should be redirected to DocuSign page

    Examples:
      | bene_type | relation   | account_number | designation |
      | Existing  | Non-Spouse | 2              | Contingent  |
      | Existing  | Spouse     | 2              | Primary     |

  @manage_bene
  Scenario Outline: Add with Edit Modal Existing Beneficiary (Trust/Entity) - Print Physical Signature flow
    Given User with role "manage_bene" is loaded
    When User should select and click and redirect to bene page
    And User should verify all allocation sections show 100% total and save to context
    When User captures first "<relation>" beneficiary name from manage bene page, clicks edit button, captures info, and navigates to edit page
    Then Spouse and Non-Spouse relationship options should be disabled
    Then Trust/Entity beneficiary name field should be pre-filled and disabled
    When User should select account "<account_number>" as "<designation>"
    And User should click Save button and user is redireted back to manage beneficiaries page
    And Beneficiary should have "ADDED" badge displayed
    Then User should verify the existing beneficiary appears in the "<designation>" section
    When User selects "Print to Obtain Physical Client Signature(s)" signature option
    Then "Continue to Review" button should be enabled
    When User clicks on "Continue to Review" button
    Then User should be navigated to Review page directly
    Then User should verify added beneficiary is displayed on Review page
    When User clicks Submit to Advisor button
    Then User should be redirected to DocuSign page

    Examples:
      | bene_type | relation | account_number | designation |
      | Existing  | Trust    | 1              | Contingent  |
      # | Existing  | Entity   | 2              | Contingent  |

@manage_bene
  Scenario Outline: Edit Existing Beneficiary - Spouse/Non-Spouse - Electronic Signature flow - Verify fields are disabled and Per Stripes is toggleable
    Given User with role "manage_bene" is loaded
    When User should select and click and redirect to bene page
    And User should verify all allocation sections show 100% total and save to context
    When User captures first "<relation>" beneficiary name from manage bene page, clicks edit button, captures info, and navigates to edit page
    Then Trust and Entity relationship options should be disabled
    Then Beneficiary personal fields should be pre-filled and disabled
    When User toggles the Per Stirpes checkbox
    Then Spouse/Non-Spouse beneficiary personal fields should be pre-filled and disabled
    And User should click Save button and user is redireted back to manage beneficiaries page
    And Beneficiary should have "EDITED" badge displayed
    Then User should verify the existing beneficiary appears in the "<designation>" section
    When User selects "Obtain Electronic Client Signature(s)" signature option
    Then "Continue to e-Signature Details" button should be enabled
    When User clicks on "Continue to e-Signature Details" button
    Then User should be navigated to e-Signature details page
    When User selects "<method>" as the signature method on e-Signature Details page
    And User select first account holder, enters email "<email>" and phone "<phone>" on e-Signature Details page
    And User checks consent checkbox and verifies Continue to Review button state
    And User clicks Continue to Review to trigger validation
    Then User should verify beneficiary is present on Review page
    When User clicks Submit to Advisor button
    Then User should be redirected to DocuSign page

    Examples:
      | bene_type | relation   | account_number | designation | method    | email              | phone      |
      | Existing  | Non-Spouse | 1              | Primary     | By Email  | test@example.com   | 5555551234 |
      | Existing  | Spouse     | 2              | Primary     | In Person | test@example.com   | 5555551234 |

@manage_bene
  Scenario Outline: Edit Existing Beneficiary - Spouse/Non-Spouse - Print Physical Signature flow - Verify fields are disabled and Per Stripes is toggleable
    Given User with role "manage_bene" is loaded
    When User should select and click and redirect to bene page
    And User should verify all allocation sections show 100% total and save to context
    When User captures first "<relation>" beneficiary name from manage bene page, clicks edit button, captures info, and navigates to edit page
    Then Trust and Entity relationship options should be disabled
    Then Beneficiary personal fields should be pre-filled and disabled
    When User toggles the Per Stirpes checkbox
    Then Spouse/Non-Spouse beneficiary personal fields should be pre-filled and disabled
    And User should click Save button and user is redireted back to manage beneficiaries page
    And Beneficiary should have "EDITED" badge displayed
    Then User should verify the existing beneficiary appears in the "<designation>" section
    When User selects "Print to Obtain Physical Client Signature(s)" signature option
    Then "Continue to Review" button should be enabled
    When User clicks on "Continue to Review" button
    Then User should be navigated to Review page directly
    Then User should verify beneficiary is present on Review page
    When User clicks Submit to Advisor button
    Then User should be redirected to DocuSign page

    Examples:
      | bene_type | relation   | account_number | designation |
      | Existing  | Non-Spouse | 1              | Primary     |
      | Existing  | Spouse     | 2              | Primary     |

# @manage_bene
#   Scenario Outline: Edit beneficiary first name and last name for new Beneficiary - Electronic Signature flow
#     Given User with role "manage_bene" is loaded
#     When User sends GET request to Beneficiary Household API with household ID "<household_id>" and depth "<depth>"
#     Then User should receive status code "200" from Beneficiary Household API
#     And User should extract account holder names from Beneficiary Household API response
#     When User should select and click on account holder "<account_holder_name>" and redirect to bene page
#     # Then User should get beneficiary name and account info for accounts with no contingent beneficiaries
#     # And User should validate the primary account holder name matches the selected account
#     When User should click on Add button and redirected to add beneficiary page
#     When User should select beneficiary type as "<bene_type>" and relationship type as "<relation>" and enter first name "<first_name>" and last name "<last_name>" and select Suffix "<suffix>" and enter SSN "<ssn>" and DOB "<dob>" and select account "<account_number>" as "<designation>"
#     And User should click Save button
#     Then Verify the beneficiary "<first_name> <last_name>" is added successfully with designation "<designation>"
#     Then Verify "Added" label is displayed for "<first_name> <last_name>"
#     Then click on edit button for the added beneficiary and verify the edit beneficiary form is displayed with correct information
#     Then update the beneficiary first name to "<new_first_name>" and last name to "<new_last_name>" and save
#     Then verify beneficiary "<new_first_name> <new_last_name>" is displayed on the page
#     When User selects "Obtain Electronic Client Signature(s)" signature option
#     Then "Continue to e-Signature Details" button should be enabled
#     When User clicks on "Continue to e-Signature Details" button
#     Then User should be navigated to e-Signature details page
#     When User selects "<method>" as the signature method on e-Signature Details page
#     When User enters email "<email>" and phone "<phone>" on e-Signature Details page
#     And User checks consent checkbox and verifies Continue to Review button state
#     And User clicks Continue to Review to trigger validation
#     Then User should verify added beneficiary is displayed on Review page
#     When User clicks Submit to Advisor button
#     Then User should be redirected to DocuSign page

@manage_bene
  Scenario Outline: Edit beneficiary first name and last name for new Beneficiary - Electronic Signature flow
    Given User with role "manage_bene" is loaded
    When User sends GET request to Beneficiary Household API with household ID "<household_id>" and depth "<depth>"
    Then User should receive status code "200" from Beneficiary Household API
    And User should extract account holder names from Beneficiary Household API response
    When User should select and click on account holder "<account_holder_name>" and redirect to bene page
    # Then User should get beneficiary name and account info for accounts with no contingent beneficiaries
    # And User should validate the primary account holder name matches the selected account
    When User should click on Add button and redirected to add beneficiary page
    When User should select beneficiary type as "<bene_type>" and relationship type as "<relation>" and enter first name "<first_name>" and last name "<last_name>" and enter SSN "<ssn>" and DOB "<dob>" and select account "<account_number>" as "<designation>"
    And User should click Save button
    Then Verify the beneficiary "<first_name> <last_name>" is added successfully with designation "<designation>"
    Then Verify "Added" label is displayed for "<first_name> <last_name>"
    Then click on edit button for the added beneficiary and verify the edit beneficiary form is displayed with correct information
    Then update the beneficiary first name to "<new_first_name>" and last name to "<new_last_name>" and save
    Then verify beneficiary "<new_first_name> <new_last_name>" is displayed on the page
    When User selects "Obtain Electronic Client Signature(s)" signature option
    Then "Continue to e-Signature Details" button should be enabled
    When User clicks on "Continue to e-Signature Details" button
    Then User should be navigated to e-Signature details page
    When User selects "<method>" as the signature method on e-Signature Details page
    When User enters email "<email>" and phone "<phone>" on e-Signature Details page
    And User checks consent checkbox and verifies Continue to Review button state
    And User clicks Continue to Review to trigger validation
    Then User should verify added beneficiary is displayed on Review page
    When User clicks Submit to Advisor button
    Then User should be redirected to DocuSign page

    Examples:
       | bene_type | relation | first_name | last_name | ssn         | dob        | household_id | depth | account_holder_name | account_number | designation | new_first_name | new_last_name | email            | phone      | method    |
       | New       | Spouse   | Test       | Brown     | 444-55-6666 | 07/22/1975 | C19744       | 1     | Tesla C On          | 1              | Contingent  | Updated        | Name          | test@example.com | 5555551234 | By Email  |
       | New       | Spouse   | Test       | Brown     | 444-55-6666 | 07/22/1975 | C19744       | 1     | Tesla C On          | 1              | Contingent  | Updated        | Name          | test@example.com | 5555551234 | In Person |


@manage_bene
  Scenario Outline: Edit beneficiary first name and last name for new Beneficiary - Print Signature flow
    Given User with role "manage_bene" is loaded
    When User sends GET request to Beneficiary Household API with household ID "<household_id>" and depth "<depth>"
    Then User should receive status code "200" from Beneficiary Household API
    And User should extract account holder names from Beneficiary Household API response
    When User should select and click on account holder "<account_holder_name>" and redirect to bene page
    # Then User should get beneficiary name and account info for accounts with no contingent beneficiaries
    # And User should validate the primary account holder name matches the selected account
    When User should click on Add button and redirected to add beneficiary page
    When User should select beneficiary type as "<bene_type>" and relationship type as "<relation>" and enter first name "<first_name>" and last name "<last_name>" and enter SSN "<ssn>" and DOB "<dob>" and select account "<account_number>" as "<designation>"
    And User should click Save button
    Then Verify the beneficiary "<first_name> <last_name>" is added successfully with designation "<designation>"
    Then Verify "Added" label is displayed for "<first_name> <last_name>"
    Then click on edit button for the added beneficiary and verify the edit beneficiary form is displayed with correct information
    Then update the beneficiary first name to "<new_first_name>" and last name to "<new_last_name>" and save
    Then verify beneficiary "<new_first_name> <new_last_name>" is displayed on the page
    When User selects "Print to Obtain Physical Client Signature(s)" signature option
    Then "Continue to Review" button should be enabled
    When User clicks on "Continue to Review" button
    Then User should be navigated to Review page directly
    Then User should verify added beneficiary is displayed on Review page
    When User clicks Submit to Advisor button
    Then User should be redirected to DocuSign page

    Examples:
       | bene_type | relation | first_name | last_name | ssn         | dob        | household_id | depth | account_holder_name | account_number | designation | new_first_name | new_last_name |
       | New       | Spouse   | Test       | Brown     | 444-55-6666 | 07/22/1975 | C19744       | 1     | Tesla C On          | 1              | Contingent  | Updated        | Name          |



@manage_bene
  Scenario Outline: Edit beneficiary first name and last name for Existing beneficiary - Electronic Signature flow
    Given User with role "manage_bene" is loaded
    When User sends GET request to Beneficiary Household API with household ID "<household_id>" and depth "<depth>"
    Then User should receive status code "200" from Beneficiary Household API
    And User should extract account holder names from Beneficiary Household API response
    When User should select and click on account holder "<account_holder_name>" and redirect to bene page
    When User clicks on first Edit button and captures beneficiary info and navigates to edit page
    Then User should verify all Edit Beneficiary fields are disabled
    And User should verify the relationship radio button matches the captured beneficiary info
    And User should verify that unrelated relationship radio buttons are disabled
    When User toggles the relationship type to '<bene_type>'
    # Then update the beneficiary first name to "<new_first_name>" and last name to "<new_last_name>" and save
    # Then verify beneficiary "<new_first_name> <new_last_name>" is displayed on the page
    When User selects "Obtain Electronic Client Signature(s)" signature option
    Then "Continue to e-Signature Details" button should be enabled
    When User clicks on "Continue to e-Signature Details" button
    Then User should be navigated to e-Signature details page
    When User selects "<method>" as the signature method on e-Signature Details page
    When User enters email "<email>" and phone "<phone>" on e-Signature Details page
    And User checks consent checkbox and verifies Continue to Review button state
    And User clicks Continue to Review to trigger validation
    Then User should verify added beneficiary is displayed on Review page
    When User clicks Submit to Advisor button
    Then User should be redirected to DocuSign page

    Examples:
       | bene_type   | relation | first_name | last_name | ssn         | dob        | household_id | depth | account_holder_name | account_number | designation | new_first_name | new_last_name | email            | phone      | method    |
       | non-spouse  | Spouse   | Test       | Brown     | 444-55-6666 | 07/22/1975 | C19744       | 1     | Tesla C On          | 1              | Contingent  | Updated        | Name          | test@example.com | 5555551234 | By Email  |
       | non-spouse  | Spouse   | Test       | Brown     | 444-55-6666 | 07/22/1975 | C19744       | 1     | Tesla C On          | 1              | Contingent  | Updated        | Name          | test@example.com | 5555551234 | In Person |


@manage_bene
  Scenario Outline: Edit beneficiary first name and last name for Existing beneficiary - Print Signature flow
    Given User with role "manage_bene" is loaded
    When User sends GET request to Beneficiary Household API with household ID "<household_id>" and depth "<depth>"
    Then User should receive status code "200" from Beneficiary Household API
    And User should extract account holder names from Beneficiary Household API response
    When User should select and click on account holder "<account_holder_name>" and redirect to bene page
    When User clicks on first Edit button and captures beneficiary info and navigates to edit page
    Then User should verify all Edit Beneficiary fields are disabled
    And User should verify the relationship radio button matches the captured beneficiary info
    And User should verify that unrelated relationship radio buttons are disabled
    When User toggles the relationship type to '<bene_type>'
    # Then update the beneficiary first name to "<new_first_name>" and last name to "<new_last_name>" and save
    # Then verify beneficiary "<new_first_name> <new_last_name>" is displayed on the page
    When User selects "Print to Obtain Physical Client Signature(s)" signature option
    Then "Continue to Review" button should be enabled
    When User clicks on "Continue to Review" button
    Then User should be navigated to Review page directly
    Then User should verify added beneficiary is displayed on Review page
    When User clicks Submit to Advisor button
    Then User should be redirected to DocuSign page

    Examples:
       | bene_type   | relation | first_name | last_name | ssn         | dob        | household_id | depth | account_holder_name | account_number | designation | new_first_name | new_last_name |
       | non-spouse  | Spouse   | Test       | Brown     | 444-55-6666 | 07/22/1975 | C19744       | 1     | Tesla C On          | 1              | Contingent  | Updated        | Name          |



  @manage_bene
  Scenario Outline: Add Individual Primary Beneficiary - Field Validation Errors
    Given User with role "manage_bene" is loaded
    When User should select and click and redirect to bene page
    When User should click on Add button and redirected to add beneficiary page
    And User should fill beneficiary form with type "<bene_type>" and relation "<relation>" and first name "<first_name>" and last name "<last_name>" and SSN "<ssn>" and DOB "<dob>" for validation
    And User should click Save button
    Then Error message should display "<errorMessage>"

    Examples:
      | bene_type | relation   | first_name | last_name | ssn         | dob        | errorMessage                  |
      | New       | Spouse     |            | Doe       | 123-45-6789 | 01/15/1985 | Please enter a first name.    |
      | New       | Spouse     | John       |           | 123-45-6789 | 01/15/1985 | Please enter a last name.     |
      | New       | Non-Spouse |            | Smith     | 987-65-4321 | 05/20/1990 | Please enter a first name.    |
      | New       | Non-Spouse | Jane       |           | 987-65-4321 | 05/20/1990 | Please enter a last name.     |
      | New       | Trust      |            |           | 123-45-6789 | 01/15/2015 | Please enter a name.          |
      | New       | Entity     |            |           | 12-3456789  |            | Please enter a name.          |


  @manage_bene
  Scenario: Allocate Equally button evenly distributes allocation between beneficiaries
    Given User with role "manage_bene" is loaded
    When User should select and click and redirect to bene page
    Given user should identify a primary beneficiary section with more than one beneficiary and allocate equally button should be enabled
    When User reads the current allocation for the identified primary section and saves to context
    When user clicks the Allocate Equally button in the identified section
    Then User reads the allocation again and verifies all primary beneficiaries are equally distributed
    When User adds a new primary beneficiary to the identified section
    When user clicks the Allocate Equally button in the identified section
    Then User reads the allocation again and verifies all primary beneficiaries are equally distributed
    When User deletes the newly added primary beneficiary from the identified section
    Then User reads the allocation again and verifies all primary beneficiaries are equally distributed
    
   
   
   @manage_bene
  Scenario Outline: Allocation input validates value format and range
    Given User with role "manage_bene" is loaded
    When User should select and click and redirect to bene page
    Given user should identify a primary beneficiary section with more than one beneficiary and allocate equally button should be enabled
    When user enters allocation value "<value>" in the two-primary beneficiary section
    Then the allocation input should be in "<expected_state>" state

    Examples:
      | value    | expected_state | notes                                                         |
      | 50.00    | valid          | Accepted XX.XX format — within range                          |
      | 99.99    | valid          | Accepted XX.XX format — just below upper boundary             |
      | 00.01    | valid          | Accepted just-above lower boundary                            |
      | 10.555   | invalid        | Rejected — more than 2 decimal places                         |
      | 0.001    | invalid        | Rejected — more than 2 decimal places and below minimum       |
      | 00.00    | invalid        | Rejected — at lower boundary (must be > 0)                    |
      | 100.01   | invalid        | Rejected — just above upper boundary                          |
      | 1000.00  | invalid        | Rejected — XXXX.XX format exceeds maximum                     |



 @manage_bene
  Scenario Outline: Delete existing primary beneficiary shows REMOVED badge and undo icon restores the row
    Given User with role "manage_bene" is loaded
    When User should select and click and redirect to bene page
    Given user should identify a primary beneficiary section with more than one beneficiary and allocate equally button should be enabled
    When User captures and deletes the "<bene_position>" deletable primary beneficiary in the identified section
    Then the deleted beneficiary row should display the REMOVED badge
    And the undo icon button should be visible next to the REMOVED badge
    And the deleted beneficiary allocation field should be disabled and show 0%
    And the remaining primary beneficiary allocation should be updated to 100%
    When User clicks the undo icon button to restore the removed beneficiary
    Then the REMOVED badge should disappear and the beneficiary row should be restored to normal state
    And the allocation should be restored to the state before deletion

    Examples:
      | bene_position |
      | first         |
      | last          |


@manage_bene
  Scenario Outline: Add new beneficiary and delete permanently removes the row with no REMOVED state
    Given User with role "manage_bene" is loaded
    When User should select and click and redirect to bene page
    Given user should identify a primary beneficiary section with more than one beneficiary and allocate equally button should be enabled
    When User adds a new primary beneficiary with relation "<relation>" first name "<first_name>" last name "<last_name>" SSN "<ssn>" and DOB "<dob>"
    Then the new beneficiary "<first_name> <last_name>" should show the ADDED badge in the primary section
    When User clicks the delete button for the newly added "<first_name> <last_name>" beneficiary
    Then the "<first_name> <last_name>" beneficiary row should be permanently gone with no REMOVED badge

    Examples:
      | relation   | first_name | last_name | ssn         | dob        |
      | Non-Spouse | Alex       | Taylor    | 333-44-5555 | 08/15/1985 |
      | Spouse     | Jordan     | Rivera    | 222-33-4444 | 05/20/1990 |
      | Non-Spouse | Alex       | Taylor    | 333-44-5555 | 08/15/1985 |

  @manage_bene
  Scenario Outline: Validate Signature Options before and after adding beneficiary
    Given User with role "manage_bene" is loaded
    When User should select and click and redirect to bene page
    When User selects "<signature_option>" signature option
    Then "Continue to e-Signature Details" button should be disabled
    When User selects "Print to Obtain Physical Client Signature(s)" signature option
    Then "Continue to Review" button should be disabled
    When User should click on Add button and redirected to add beneficiary page
    And User should select beneficiary type as "<bene_type>" and relationship type as "<relation>" and enter first name "<first_name>" and last name "<last_name>" and enter SSN "<ssn>" and DOB "<dob>" and select at least one account
    And User should click Save button and user is redireted back to manage beneficiaries page
    And User should verify befinaficieries is added successfully on manage beneficiaries page with correct information
    When User selects "<signature_option>" signature option
    Then "<button_name>" button should be enabled
    When User selects "Print to Obtain Physical Client Signature(s)" signature option
    Then "Continue to Review" button should be enabled
    When Delete added benefeciries for clean up

    Examples:
      | bene_type | relation   | first_name | last_name | ssn         | dob        | signature_option                        | button_name                         |
      | New       | Spouse     | John       | Doe       | 123-45-6789 | 01/15/1985 | Obtain Electronic Client Signature(s)   | Continue to e-Signature Details     |
      | New       | Non-Spouse | Jane       | Smith     | 987-65-4321 | 05/20/1990 | Obtain Electronic Client Signature(s)   | Continue to e-Signature Details     |
      | New       | Trust      | Michael    | Davis     | 666-77-8888 | 09/25/1975 | Obtain Electronic Client Signature(s)   | Continue to e-Signature Details     |
      | New       | Entity     | Lisa       | Miller    | 777-88-9999 | 11/12/1982 | Obtain Electronic Client Signature(s)   | Continue to e-Signature Details     |

  @manage_bene
  Scenario: Future dates should be disabled in date picker
    Given User with role "manage_bene" is loaded
    When User should select and click and redirect to bene page
    When User should click on Add button and redirected to add beneficiary page
    And User should click on Date of Birth calendar picker
    Then Future date navigation should be disabled in calendar
    And Only past dates should be selectable

  @manage_bene
  Scenario Outline: Add Individual Primary Beneficiary without selecting any account
    Given User with role "manage_bene" is loaded
    When User should select and click and redirect to bene page
    When User should click on Add button and redirected to add beneficiary page
    And User should select beneficiary type as "<bene_type>" and relationship type as "<relation>" and enter first name "<first_name>" and last name "<last_name>" and SSN "<ssn>" and DOB "<dob>" and do not select any account
    And User should click Save button
    Then Error message should display "Please select at least one account."

    Examples:
      | bene_type | relation | first_name | last_name | ssn         | dob        |
      | New       | Spouse   | John       | Doe       | 123-45-6789 | 01/15/1985 |



  @manage_bene
  Scenario Outline: Add Contingent Beneficiary when Primary Beneficiary exists
    Given User with role "manage_bene" is loaded
    When User sends GET request to Beneficiary Household API with household ID "<household_id>" and depth "<depth>"
    Then User should receive status code "200" from Beneficiary Household API
    And User should extract account holder names from Beneficiary Household API response
    When User should select and click on account holder "<account_holder_name>" and redirect to bene page
    Then User should get beneficiary name and account info for accounts with no contingent beneficiaries
    And User should validate the primary account holder name matches the selected account
    When User should click on Add button and redirected to add beneficiary page
    When User should select beneficiary type as "<bene_type>" and relationship type as "<relation>" and enter first name "<first_name>" and last name "<last_name>" and enter SSN "<ssn>" and DOB "<dob>" and select account "<account_number>" as "<designation>"
    And User should click Save button
    Then Verify the beneficiary "<first_name> <last_name>" is added successfully with designation "<designation>"
    # Then Verify the beneficiary "<first_name> <last_name>" is added successfully with designation "<relation>"
    # And Toast notification should display "<relation> beneficiary "<first_name> <last_name>" added."

    Examples:
       | bene_type  | relation    | first_name | last_name | ssn         | dob        | household_id | depth | account_holder_name   | account_number | designation |
       | New        | Spouse      | Test       | Brown     | 444-55-6666 | 07/22/1975 | C19744       | 1     | Tesla C On    | 1              | Contingent  |



#   @manage_bene
#   Scenario: Single primary beneficiary allows 100 percent allocation without error
#     Given User with role "manage_bene" is loaded
#     When User should select and click and redirect to bene page
#     Given user should identify beneficiaries with 1 primary account and allocate equally button should be disabled
#     When user enters allocation value "100.00" in the single-primary beneficiary section
#     Then the allocation input should be in "valid" state

  
  # @manage_bene
  # Scenario Outline: Primary beneficiary group total validation
  #   Given User with role "manage_bene" is loaded
  #   When User should select and click and redirect to bene page
  #   Given user should identify beneficiaries with 2 primary accounts and allocate equally button should be enabled
  #   When user sets primary allocations to "<alloc1>" and "<alloc2>" in the two-primary beneficiary section
  #   Then the group total should be "<expected_total>" with "<error_expectation>" error state

  #   Examples:
  #     | alloc1 | alloc2 | expected_total | error_expectation | notes                                                              |
  #     | 50.00  | 50.00  | 100.00         | no_error          | Group total 100.00% — no error state expected                      |
  #     | 49.99  | 50.00  | 99.99          | error             | Group total 99.99% — triggers error, all allocations highlighted   |
  #     | 50.01  | 50.00  | 100.01         | error             | Group total 100.01% — triggers error, all allocations highlighted  |

  @manage_bene
  Scenario Outline: Edit beneficiary designation from Contingent to primary
    Given User with role "manage_bene" is loaded
    When User sends GET request to Beneficiary Household API with household ID "<household_id>" and depth "<depth>"
    Then User should receive status code "200" from Beneficiary Household API
    And User should extract account holder names from Beneficiary Household API response
    When User should select and click on account holder "<account_holder_name>" and redirect to bene page
    Then User should get beneficiary name and account info for accounts with no contingent beneficiaries
    And User should validate the primary account holder name matches the selected account
    When User should click on Add button and redirected to add beneficiary page
    When User should select beneficiary type as "<bene_type>" and relationship type as "<relation>" and enter first name "<first_name>" and last name "<last_name>" and enter SSN "<ssn>" and DOB "<dob>" and select account "<account_number>" as "<designation>"
    And User should click Save button
    Then Verify the beneficiary "<first_name> <last_name>" is added successfully with designation "<designation>"
    Then Verify "Added" label is displayed for "<first_name> <last_name>"
    Then click on edit button for the added beneficiary and verify the edit beneficiary form is displayed with correct information
    Then change the designation to "Primary" and save
    

    Examples:
       | bene_type  | relation    | first_name | last_name | ssn         | dob        | household_id | depth | account_holder_name   | account_number | designation |
       | New        | Spouse      | Test       | Brown     | 444-55-6666 | 07/22/1975 | CE6VZ3       | 1     | Cleve Braulio Mohr    | 1              | Contingent  |

  

  @manage_bene
  Scenario Outline: Esignature page validation when clicking on continue to esignature details button
    Given User with role "manage_bene" is loaded
    When User should select and click and redirect to bene page
    When User should click on Add button and redirected to add beneficiary page
    And User should select beneficiary type as "<bene_type>" and relationship type as "<relation>" and enter first name "<first_name>" and last name "<last_name>" and enter SSN "<ssn>" and DOB "<dob>" and select at least one account
    And User should click Save button and user is redireted back to manage beneficiaries page
    And User should verify befinaficieries is added successfully on manage beneficiaries page with correct information
    And Beneficiary should have "ADDED" badge displayed
    When User selects "Obtain Electronic Client Signature(s)" signature option
    Then "Continue to e-Signature Details" button should be enabled
    When User clicks on "Continue to e-Signature Details" button
    Then User should be navigated to e-Signature details page
    
    # And Beneficiary allocation should be "100.00"
    # And "Allocate Equally" button should be disabled

    Examples:
      | bene_type  | relation    | first_name | last_name | ssn         | dob        |
      # | Individual | Spouse      | John       | Doe       | 123-45-6789 | 01/15/1985 |
      # | Individual | Non-Spouse  | Jane       | Smith     | 987-65-4321 | 05/20/1990 |
      | New        | Spouse      | Test       | Brown     | 444-55-6666 | 07/22/1975 |


  @manage_bene
  Scenario Outline: e-Signature Details page field validation on Save
    Given User with role "manage_bene" is loaded
    When User should select and click and redirect to bene page
    When User should click on Add button and redirected to add beneficiary page
    And User should select beneficiary type as "New" and relationship type as "Spouse" and enter first name "Test" and last name "Brown" and enter SSN "444-55-6666" and DOB "07/22/1975" and select at least one account
    And User should click Save button and user is redireted back to manage beneficiaries page
    When User selects "Obtain Electronic Client Signature(s)" signature option
    When User clicks on "Continue to e-Signature Details" button
    Then User should be navigated to e-Signature details page
    When User enters email "<email>" and phone "<phone>" on e-Signature Details page
    And User clicks Continue to Review to trigger validation
    Then Email field should display error "<email_error>"
    And Phone field should display error "<phone_error>"

    Examples:
      | email            | phone      | email_error                          | phone_error                                  |
      |                  |            | Please enter a valid email address.  | Please enter a valid 10-digit phone number.  |
      | invalidemail     |            | Please enter a valid email address.  | Please enter a valid 10-digit phone number.  |
      | invalidemail.com |            | Please enter a valid email address.  | Please enter a valid 10-digit phone number.  |
      |                  | 12345      | Please enter a valid email address.  | Please enter a valid 10-digit phone number.  |
      | test@example.com | 12345      |                                      | Please enter a valid 10-digit phone number.  |
  
  @manage_bene
  Scenario Outline: Contingent beneficiary group total validation
    Given User with role "manage_bene" is loaded
    When User sends GET request to Beneficiary Household API with household ID "<household_id>" and depth "<depth>"
    Then User should receive status code "200" from Beneficiary Household API
    And User should extract account holder names from Beneficiary Household API response
    When User should select and click on account holder "<account_holder_name>" and redirect to bene page
    Then User should get beneficiary name and account info for accounts with 2 contingent beneficiaries
    And User should validate the contingent beneficiary section is displayed
    When user sets contingent allocations to "<alloc1>" and "<alloc2>" in the contingent-beneficiary section
    Then the contingent group total should be "<expected_total>" with "<error_expectation>" error state

    Examples:
       | household_id | depth | account_holder_name   | alloc1 | alloc2 | expected_total | error_expectation | notes                                                              |
       | CE6VZ3       | 1     | Cleve Braulio Mohr    | 50.00  | 50.00  | 100.00         | no_error          | Group total 100.00% � no error state expected                      |
       | CE6VZ3       | 1     | Cleve Braulio Mohr    | 49.99  | 50.00  | 99.99          | error             | Group total 99.99% � triggers error, all allocations highlighted   |
       | CE6VZ3       | 1     | Cleve Braulio Mohr    | 50.01  | 50.00  | 100.01         | error             | Group total 100.01% � triggers error, all allocations highlighted  |

  # @manage_bene
  # Scenario: Allocate Equally for three beneficiaries produces valid rounded split totaling 100.00%
  #   Given User with role "manage_bene" is loaded
  #   When User should select and click and redirect to bene page
  #   Given user should identify beneficiaries with 3 primary accounts and allocate equally button should be enabled
  #   When user clicks the Allocate Equally button in the identified section
  #   Then the three beneficiary allocations should be "33.34%" and "33.33%" and "33.33%" with total "100.00%" with no rounding error

   # # Scenario: Cannot add Contingent Beneficiary without Primary Beneficiary
  # #   When User should select and click and redirect to add bene page
  # #   And User should select beneficiary type as "Individual" and designation as "Contingent" and enter first name "Jane" and last name "Smith" and SSN "987-65-4321" and DOB "05/20/1990" and select at least one account
  # #   And User should click Save button
  # #   Then Tooltip should display "No beneficiaries on this account. Add a primary beneficiary first."
  # #   And Beneficiary should NOT be added
  

#   @manage_bene
#   Scenario: Allocate Equally button is disabled with only one beneficiary
#     Given User with role "manage_bene" is loaded
#     When User should select and click and redirect to bene page
#     Given user should identify beneficiaries with 1 primary account and allocate equally button should be disabled
#     Then Beneficiary allocation should remain "100.00"

  @manage_bene
  Scenario Outline: Deceased account - Bene landing page verification
    Given User with role "manage_bene" is loaded
    When User loads the deceased account bene page
    Then User should see "<banner_text>" warning banner
    And The deceased account card should display "NOT ELIGIBLE" badge
    When User clicks on the deceased account card
    Then User should remain on the same manage beneficiaries page

    Examples:
      | banner_text                        |
      | Deceased Account(s) Not Eligible   |


  @manage_bene
  Scenario Outline: Fraud/Frozen account - Delete beneficiary and complete e-Signature flow
    Given User with role "manage_bene" is loaded
    When User loads the Fraud/Frozen account bene page
    Then User should be on the bene landing page
    When User clicks the first delete icon on the bene detail page
    Then The first beneficiary row should display the "REMOVED" label
    When User selects "Obtain Electronic Client Signature(s)" signature option
    Then "Continue to e-Signature Details" button should be enabled
    When User clicks on "Continue to e-Signature Details" button
    Then User should be navigated to e-Signature details page
    When User selects "<method>" as the signature method on e-Signature Details page
    When User enters email "<email>" and phone "<phone>" on e-Signature Details page for Froud and frozen acccount
    And User checks consent checkbox and verifies Continue to Review button state
    And User clicks Continue to Review to trigger validation
    Then User should see the Fraud or Compliance Hold warning on the Review page
    When User clicks Submit to Advisor button
    Then User should be redirected to DocuSign page
    

    Examples:
      | bene_type | relation | first_name | last_name | ssn         | dob        | email            | phone      | method   | authorized_holder |
      | New       | Spouse   | Test       | Brown     | 444-55-6666 | 07/22/1975 | test@example.com | 5555551234 | By Email | Power of Attorney |




  @manage_bene
  Scenario Outline: Custom bene account - Edit bene and complete e-Signature flow
    Given User with role "manage_bene" is loaded
    When User loads the Custom bene account bene page
    Then User should be on the bene landing page
    When User clicks the first edit icon on the bene detail page
    Then User should be redirected to the edit beneficiary page
    When User checks the Custom Request checkbox on the edit beneficiary form
    Then The "Supporting Documentation for Custom Request" section should be visible
    When User uploads "<pdf_file>" to the Supporting Documentation section

    Examples:
      | bene_type | relation | first_name | last_name | ssn         | dob        | email            | phone      | method   | authorized_holder | pdf_file                                               |
      | New       | Spouse   | Test       | Brown     | 444-55-6666 | 07/22/1975 | test@example.com | 5555551234 | By Email | Power of Attorney | Please_DocuSign_this_document__Billing_Only.pdf        |




  @manage_bene
  Scenario Outline: POA account - Add beneficiary and navigate to e-Signature Details
    Given User with role "manage_bene" is loaded
    When User loads the POA account bene page
    When User should click on Add button and redirected to add beneficiary page
    And User should select beneficiary type as "<bene_type>" and relationship type as "<relation>" and enter first name "<first_name>" and last name "<last_name>" and enter SSN "<ssn>" and DOB "<dob>" and select at least one account
    And User should click Save button and user is redireted back to manage beneficiaries page
    And Beneficiary should have "ADDED" badge displayed
    When User selects "Obtain Electronic Client Signature(s)" signature option
    Then "Continue to e-Signature Details" button should be enabled
    When User clicks on "Continue to e-Signature Details" button
    Then User should be navigated to e-Signature details page
    When User selects "<method>" as the signature method on e-Signature Details page
    When User enters email "<email>" and phone "<phone>" on e-Signature Details page
    And User selects "<authorized_holder>" from the Authorized Account Holder dropdown
    And User checks consent checkbox and verifies Continue to Review button state
    And User clicks Continue to Review to trigger validation
    Then User should verify added beneficiary is displayed on Review page
    When User clicks Submit to Advisor button
    Then User should be redirected to DocuSign page

    Examples:
      | bene_type  | relation    | first_name | last_name | ssn         | dob        | email              | phone      | method    | authorized_holder   |
      | New        | Spouse      | Test       | Brown     | 444-55-6666 | 07/22/1975 | test@example.com   | 5555551234 | By Email  | Power of Attorney   |
      | New        | Spouse      | Test       | Brown     | 444-55-6666 | 07/22/1975 | test@example.com   | 5555551234 | In Person | Power of Attorney   |
      | New        | Non-Spouse  | Test       | Johnson   | 555-66-7777 | 03/10/1980 | test2@example.com  | 5555552345 | By Email  | Power of Attorney   |
      | New        | Non-Spouse  | Test       | Johnson   | 555-66-7777 | 03/10/1980 | test2@example.com  | 5555552345 | In Person | Power of Attorney   |
      | New        | Trust       | Michael    | Davis     | 666-77-8888 | 09/25/1975 | test3@example.com  | 5555553456 | By Email  | Power of Attorney   |
      | New        | Trust       | Michael    | Davis     | 666-77-8888 | 09/25/1975 | test3@example.com  | 5555553456 | In Person | Power of Attorney   |
      | New        | Entity      | Lisa       | Miller    | 777-88-9999 | 11/12/1982 | test4@example.com  | 5555554567 | By Email  | Power of Attorney   |
      | New        | Entity      | Lisa       | Miller    | 777-88-9999 | 11/12/1982 | test4@example.com  | 5555554567 | In Person | Power of Attorney   |



# @manage_bene
#   Scenario Outline: Deceased account - Bene landing page verification for more then one account
#     Given User with role "manage_bene" is loaded
#     When User loads the deceased account bene page for more then one account
#     And The deceased account card should display "NOT ELIGIBLE" badge
#     When User clicks on the deceased account card
#     Then User should remain on the same manage beneficiaries page
#     When User should select and click and redirect to bene page
#     And User should verify all allocation sections show 100% total and save to context
#     When User should click on Add button and redirected to add beneficiary page
#     And User should select beneficiary type as "<bene_type>" and relationship type as "<relation>" and enter first name "<first_name>" and last name "<last_name>" and enter SSN "<ssn>" and DOB "<dob>" and select at least one account
#     And User should click Save button and user is redireted back to manage beneficiaries page
#     And User should verify befinaficieries is added successfully on manage beneficiaries page with correct information
#     And Beneficiary should have "ADDED" badge displayed
#     When User selects "Obtain Electronic Client Signature(s)" signature option
#     Then "Continue to e-Signature Details" button should be enabled
#     When User clicks on "Continue to e-Signature Details" button
#     Then User should be navigated to e-Signature details page
#     When User selects "<method>" as the signature method on e-Signature Details page
#     When User enters email "<email>" and phone "<phone>" on e-Signature Details page
#     And User checks consent checkbox and verifies Continue to Review button state
#     And User clicks Continue to Review to trigger validation
#     Then User should verify added beneficiary is displayed on Review page
#     When User clicks Submit to Advisor button
#     Then User should be redirected to DocuSign page

#     Examples:
#       | bene_type  | relation    | first_name | last_name | ssn         | dob        | email              | phone      | method    |
#       | New        | Spouse      | Test       | Brown     | 444-55-6666 | 07/22/1975 | test@example.com   | 5555551234 | By Email  |
#       | New        | Spouse      | Test       | Brown     | 444-55-6666 | 07/22/1975 | test@example.com   | 5555551234 | In Person |
#       | New        | Non-Spouse  | Test       | Johnson   | 555-66-7777 | 03/10/1980 | test2@example.com  | 5555552345 | By Email  |
#       | New        | Non-Spouse  | Test       | Johnson   | 555-66-7777 | 03/10/1980 | test2@example.com  | 5555552345 | In Person |
#       | New        | Trust       | Michael    | Davis     | 666-77-8888 | 09/25/1975 | test3@example.com  | 5555553456 | By Email  |
#       | New        | Trust       | Michael    | Davis     | 666-77-8888 | 09/25/1975 | test3@example.com  | 5555553456 | In Person |
#       | New        | Entity      | Lisa       | Miller    | 777-88-9999 | 11/12/1982 | test4@example.com  | 5555554567 | By Email  |
#       | New        | Entity      | Lisa       | Miller    | 777-88-9999 | 11/12/1982 | test4@example.com  | 5555554567 | In Person |

