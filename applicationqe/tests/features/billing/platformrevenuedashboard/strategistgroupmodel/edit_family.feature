Feature: Edit Family
  As a user of the Billing application
  I want to edit an existing Family
  So that I can update family details

  Background:
    Given the user is logged into the application
    And the user verifies login is successful

  @edit @family @regression
  Scenario: Edit Family with valid data
    When the user navigates to Strategist Group Model
    And the user verifies Strategist Group Model page is loaded
    And the user clicks the Family tab
    And the user searches for family "<search_family_name>"
    And the user clicks Search for family
    And the user clicks Edit for family result
    And the user verifies Family Name and Program Name are non-editable for "<search_family_name>"
    And the user updates family fields with the following data:
      | program_name              | <program_name>              |
      | manager_type_code         | <manager_type_code>         |
      | is_uma_custom             | <is_uma_custom>             |
      | has_minimum               | <has_minimum>               |
      | standard_discount_eligible| <standard_discount_eligible>|
      | discount_package          | <discount_package>          |
      | product_name              | <product_name>              |
      | create_style_code         | <create_style_code>         |
      | style_code                | <style_code>                |
      | style_description         | <style_description>         |
      | manager_style_description | <manager_style_description> |
      | category                  | <category>                  |
      | option                    | <option>                    |
      | research_group            | <research_group>            |
      | schedule_group            | <schedule_group>            |
    And the user submits the form
    And the user confirms Edit Family submission
    Then the user verifies Family update was successful
    And the user logs out
