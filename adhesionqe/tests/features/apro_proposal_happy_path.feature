@proposal @e2e @happypath
Feature: APro proposal happy path

    @regression @smoke
    Scenario: Create Prospect Proposal Happy Path
        When I navigate to the APro prospects page
        Then I should see the APro prospects page
        And I start a new proposal
        And I complete the Details step for Guy Apro with investment amount 1000000
        And I skip the risk assessment
        And I complete the Allocation step with Brandes International ADR
        # Test resume proposal mid-workflow to verify continuation
        When I navigate back to the prospects list
        Then the proposal should appear in the prospects list
        And the proposal investment amount should match the created proposal
        And the proposal advisor should match the logged-in advisor
        And the proposal strategy should be populated
        And the proposal Risk Assessment Completed column should have today's date
        And the proposal composite should match the selected allocation
        When I resume the original proposal from the prospects list
        And I navigate to the Holdings step
        # Test manual holdings entry
        And I complete the Holdings step with [["GOOG", 5, 250, "01/01/2025"], ["NVDA", 2, 150], ["AAPL", 3, 170]]
        Then the holdings [["GOOG", 5, 250, "01/01/2025"], ["NVDA", 2, 150], ["AAPL", 3, 170]] should be added to the proposal
        # Test holdings import modal workflow
        When I open the holdings import modal
        And I download the holdings template
        Then the template file should be named "Holdings_Template_*.csv"
        And the template should contain the expected column headers
        When I upload a holdings import file with sample data
        Then the import preview should display the holdings accurately
        And the preview should show correct row count
        When I submit the import
        Then the imported holdings should appear in the holdings grid
        # Test editing an imported holding post-import
        When I select the first imported holding row
        And I update the holding symbol to GME
        And I save the tax lot
        Then the holding symbol should display GME in the grid
        When I click Next from the Holdings step
        And I complete the Fees step
        Then The proposal details should contain the expected information
        And I preview the proposal
        And I complete the Generate Report step with all reports
        Then the proposal should be generated with all reports
        Then the History/Actions step should contain the expected information
        When I navigate back to the prospects list
        Then the proposal should appear in the prospects list
        And the proposal finished date should be today
        When I resume the original proposal from the prospects list
        # Test copy proposal flow
        And I click the Copy Proposal action
        Then the proposal Details step should open for the copied proposal
        # Complete the copy proposal workflow (Details already populated from original)
        When I proceed from the populated Details step
        And I skip the risk assessment
        And I complete the Allocation step with Brandes International ADR
        And I select the first holding row
        And I update the holding symbol to VTI
        And I save the tax lot
        When I click Next from the Holdings step
        And I complete the Fees step
        # After fees, refresh to return to prospects list (simpler approach)
        When I refresh the page
        # Resume the copied proposal to continue to Generate Report step
        When I resume the copied proposal from the prospects list
        And I navigate to the Generate Proposal step
        And I preview the proposal
        # Use same generate report workflow as original proposal
        And I complete the Generate Report step with all reports
        Then the proposal should be generated with all reports
        When I navigate back to the prospects list
        Then the copied proposal should appear as a new row with a finished date

# Scenario: Create Client Proposal Happy Path
#     When I search for client "45255105"
#     And I click the Proposals (New) link
#     And I select the existing proposal
#     Then The client details should be prefilled
#     When I set the investment amount to $1
#     When I edit the first holding in the list
#     Then The total shares should be updated accordingly
