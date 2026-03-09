@smoke @regression @newAccountWizard @TMS @e2e
Feature: New Account Wizard Happy Path TMS Test

    Scenario: Complete New Account Wizard TMS E2E - Create Proposal and Verify Document
        When I click on the Account Wizard link
        And I decide to create a new client
        And I complete the client profile with first name "Guy" and last name "NAWTMS"
        And I Complete the Construct Portfolio section
        And I add all strategies to the account
            | assetmark income builder, profile 2, conservative            |
            | blackrock equity dividend                                    |
            | savos us risk controlled strategy, profile 6                 |
            | alphasimplex, alternative model portfolio, profile 5, growth |
            | jpmorgan absolute return - profile 1                         |
        And I allocate equal percentages to all strategies
        And I opt into tax management services
        When I upload a holdings template
        Then The UI summary should be generated
        Then the investment summary should display correctly with all strategies and allocations
        And I set a flat fee of "0.5" percent
        Then the portfolio fees should be valid
        When I create the proposal document
        Then the proposal document should be generated successfully
        And the document should contain all the relevant information from the proposal
        And the cover page section should be verified
        And the table of contents section should be verified
        And the introduction section should be verified
        And the investing is personal section should be verified
        And the equities vs bonds section should be verified
        And the cycle of emotions section should be verified
        And the staying invested section should be verified
        And the investment team section should be verified
        And the portfolio strategists section should be verified
        And the custodian selection section should be verified
        And the ongoing review section should be verified
        And the financial analysis section should be verified
        And the recommended portfolio section should be verified
        And the allocation by asset class section should be verified
        And the top holdings section should be verified
        And the proposed accounts section should be verified
        And the hypothetical performance sections should be verified
        And the rates section should be verified
        And the calendar year returns section should be verified
        And the historical cumulative section should be verified
        And the risk versus return section should be verified
        And the fee schedule section should be verified
        And the tiered fee schedule section should be verified
        And the estimated expense section should be verified
        And the important information section should be verified
        And the disclosures section should be verified
        And the tax management services section should be verified
        And the client signature section should be verified
        And the investment policy statement section should be verified
        And I save the proposal
        Then the proposal should be saved successfully with 95 pages including Tax Management Services