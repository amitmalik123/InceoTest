@smoke @regression @portfolioEngine @widgetTests
Feature: Portfolio Engine Widgets
    Scenario: Verify Portfolio Engine Widgets Load
        Given I am on the Portfolio Engine page
        When I click the manage portfolios button
        And I create a new model portfolio
        And I select AssetMark Platform Strategies as portfolio type
        And I add the following strategies to the portfolio "assetmark income builder, profile 2, conservative; blackrock equity dividend; savos us risk controlled strategy, profile 6; AIM Decathlon Growth, Profile 5; jpmorgan absolute return - profile 1"
        And I enter portfolio name "Widget Test Portfolio"
        And I save the portfolio
        When I enable all Portfolio Engine widgets
        Then the Portfolio Engine widgets should load successfully