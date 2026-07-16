Feature: BAW Check Coach IWR Extractions

  @C12346 @BAW_Checkcoach_IWRExtractions 
  Scenario Outline: C12346_BAW_Checkcoach_IWRExtractions
    When User click on Open New Work Item button
    When Select work item type "Contribution by Check - LYN"
    When Enter Custodial Account value
    # And Select individual owner and click run now
    # And Fetch b number from shell process page
    # 
    Then Select the Document click on commit button
    And Wait for BAW dashboard to be displayed
    Then Click on "Search Work Item BAW" tab
    Then Enter captured Work Item ID and fetch B number from results
    Then Navigate to Dashboard and search captured B number
    Then Click on Create New Digital Record button and click on the Add or Update Check Details button
    And Cancel check coach and wait for validation to complete then reenter check details
    #Then Cancel check coach and wait for validation to complete fetch check image validation status
    
    Examples:
        | SheetName | RowNumber |
        | BAW       | 3         |
       # | BAW       | 4        |

 @iwr @baw 
  Scenario Outline: check upload note validation
    When User click on Open New Work Item button
    When Select work item type "Digital Check"
    When Enter Custodial Account value
    When Click add document button and upload the check document
    When Click submit button and store work item number
    When Click Search Work Item BAW and enter the stored work item number
    When Click search button and fetch the B number from results
    When Click dashboard and enter the fetched B number in search bar
    When Click the run icon
    Then Validate the view note "A single check front has been found for extract"
    When Click Create New Digital record and Add/Update check details
    Then Validates the Check Extraction in the Check Images Validation section
    Examples:
      | SheetName | RowNumber |
      | TOAR      | 2         |
    
        


 