@squad5SmokeTest
Feature: BAW Shell Journal

  @Journal @baw @prodSmoke
  Scenario Outline: BAW_Shell_Add journal from BPM_WFI
    When User click on Open New Work Item button
    When Select work item type "Investment Solution Change Journal"
    When Enter Custodial Account value
    And Select individual owner and click run now
    When Update internal status "In Process"
    And Fetch b number from shell process page
  #  Then Establish DB connection and update "request status" in citrix
  #  Then Establish DB connection and update "completionDate" in citrix
    And User fetches custodian account
    And click on Update OA button
    When cancel already created journal
    And Select action type "Journal"
    And User add a journal
    Then Validate Added Journal
    When Click on save and close button on journalUtilityPage page
    When cancel already created journal
    And Click on save and close button on createOAPage page

    Examples:
      | SheetName | RowNumber |
      | Shell     | 2         |