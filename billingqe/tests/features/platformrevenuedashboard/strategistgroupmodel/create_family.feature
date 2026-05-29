Feature: Create Model Family
  As a user of the Billing application
  I want to create a new Model Family
  So that I can manage model families in the system

  Background:
    Given the user is logged into the application
    And the user verifies login is successful

  @create @family @regression
  Scenario: Create Model Family with valid data
    When the user navigates to Strategist Group Model
    And the user verifies Strategist Group Model page is loaded
    And the user clicks the Family tab
    And the user clicks Create Model Family button
    And the user verifies the Create new Family form is displayed
    And the user fills in the family form with the following data:
      | family_name                    | <family_name>                    |
      | manager_type_code              | <manager_type_code>              |
      | program_name                   | <program_name>                   |
      | is_uma_custom                  | <is_uma_custom>                  |
      | has_minimum                    | <has_minimum>                    |
      | standard_discount_eligible     | <standard_discount_eligible>     |
      | discount_package               | <discount_package>               |
      | product_name                   | <product_name>                   |
      | create_style_code              | <create_style_code>              |
      | style_code                     | <style_code>                     |
      | style_description              | <style_description>              |
      | manager_style_description      | <manager_style_description>      |
      | category                       | <category>                       |
      | option                         | <option>                         |
      | research_group                 | <research_group>                 |
      | schedule_group                 | <schedule_group>                 |
    And the user submits the form
    And the user confirms the submission
    Then the user verifies the family was created successfully
    And the user verifies the family exists in the Family table
    And the user logs out
