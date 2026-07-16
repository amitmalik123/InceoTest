@smoke @regression @portfolioEngine @e2e
Feature: Portfolio Engine Happy Path E2E Test

    Scenario: Complete Portfolio Engine E2E - Create Portfolio, Create Proposal, and Verify Document
        # Create Portfolio with Strategies
        Given I am on the Portfolio Engine page
        When I click the manage portfolios button
        And I create a new model portfolio
        And I select AssetMark Platform Strategies as portfolio type
        And I add the following strategies to the portfolio "assetmark income builder, profile 2, conservative; blackrock equity dividend; savos us risk controlled strategy, profile 6; AIM Decathlon Growth, Profile 5; jpmorgan absolute return - profile 1"
        And I enter portfolio name "E2E Test Portfolio"
        And I save the portfolio
        Then the portfolio should contain the expected strategies
        And all strategies should have "20" percent allocation

        # Create Proposal with New Client
        When I click the create proposal button
        Then the portfolio strategies should be displayed correctly
        And the client type options should be visible and editable
        When I fill new client information with first name "Guy" and last name "PeE2E"
        And I select a risk profile
        And I select a custodian and set up account registration
        And I add an account with all strategies and investment amount "$500000"
        Then the proposed accounts should display correctly with amount "$ 500,000", first name "Guy", and last name "PeE2E"
        When I enter fee percentage ".5"
        Then the fee summary should display correctly with portfolio value "$500,000" and financial advisor fee "0.50%"
        And the total fee calculation should be correct
        When I generate the proposal document with all sections
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
        And the client signature section should be verified
        And the investment policy statement section should be verified
        And I save the proposal
        Then the proposal should be saved successfully with 92 pages