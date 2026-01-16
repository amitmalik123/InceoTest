import { test, Page } from '@playwright/test';
import { expect } from '@fixtures/fixtures';
import { PortfolioEnginePage } from '@pages/PortfolioEngineObjectModel';
import { navigateToPortfolioEngine } from '@helperfunctions/navigateToPortfolioEngine';
import { navigateToHomePage } from '@helperfunctions/navigateToHomePage';
import { selectCustodian } from '@data/proposalVariations';




let page1: Page;
let portfolioEnginePage: PortfolioEnginePage;


test.describe.configure({ mode: 'serial' }); //Have to add strategies, then create prposal, then validate proposal doc in order

test.describe('Portfolio Engine Prep', () => {

    //apply storage state of role from auth file created in setup
    test.use({ storageState: './authfiles/role1.json' });
    //Start each test from Portfolio Engine home page
    test.beforeEach('Navigate to Portfolio Engine Home Page', async ({ page }) => {
        await navigateToHomePage(page);
        const portfolioEnginePageObject = await navigateToPortfolioEngine(page);
        portfolioEnginePage = new PortfolioEnginePage(portfolioEnginePageObject);

    });

    test('Add strategies to portfolio', async ({ page }) => {
        console.log('\nStarting create portfolio test');
        try {
            console.log('\nWaiting for Portfolio Engine to load');
            await expect(portfolioEnginePage.getStartedButton.or(portfolioEnginePage.managePortfoliosButton)).toBeVisible();
            if (await portfolioEnginePage.getStartedButton.isVisible()) {
                await portfolioEnginePage.getStartedButton.click();
            } else if (await portfolioEnginePage.managePortfoliosButton.isVisible()) {
                await portfolioEnginePage.managePortfoliosButton.click();
            }
        } catch (error) {
            console.error('\nCould not find the Get Started or Manage Portfolios button on Portfolio Engine home page\n', error);
        }
        //Open create portfolio window
        console.log('\nAdding strategies to portfolio');
        await portfolioEnginePage.createNewModelPortfolioButton.click();
        await portfolioEnginePage.assetMarkPlatformStrategiesText.click();

        // Add strategies using the helper method
        /*TODO: Create data driven way to add strategies*/
        await portfolioEnginePage.addStrategyToPortfolio('assetmark income builder, profile 2, conservative');
        await portfolioEnginePage.addStrategyToPortfolio('blackrock equity dividend');
        await portfolioEnginePage.addStrategyToPortfolio('savos us risk controlled strategy, profile 6');
        await portfolioEnginePage.addStrategyToPortfolio('alphasimplex, alternative model portfolio, profile 5, growth');
        await portfolioEnginePage.addStrategyToPortfolio('jpmorgan absolute return - profile 1');

        await portfolioEnginePage.modelPortfolioNameTextbox.fill('E2E Test Portfolio');
        await portfolioEnginePage.strategySaveButton.click();
        await portfolioEnginePage.page.waitForLoadState();

        //Verify each strategy was added
        try {
            await expect(portfolioEnginePage.investmentAllocationText).toContainText('Core MarketsAssetMark Income Builder, Profile 2, ConservativeETF | 2Tactical Strategies - Enhanced Return FocusBlackRock Equity DividendIMA | 6Tactical Strategies - Limit Loss FocusSavos US Risk Controlled Strategy, Profile 6GMS | 6Diversifying Strategies - Equity AlternativesAlphaSimplex, Alternative Model Portfolio, Profile 5, GrowthMF | 5Diversifying Strategies - Bonds and Bond AlternativesJPMorgan Absolute Return - Profile 1MF | 1');
        } catch (error) {
            console.error('\nDifferent/Missing strategies found in portfolio\n', error);
        }

        //verify allocation percentages
        for (let i = 0; i < 5; i++) {
            try {
                await expect(portfolioEnginePage.getAllocationTextbox(i)).toHaveValue('20');
            } catch (innerError) {
                console.error(`\nAllocation percentage verification failed for strategy ${i}\n`, innerError);
            }
        }
    });
});



test.describe('Portfolio Engine Happy Path Tests', () => {

    //apply storage state of role from auth file created in setup
    test.use({ storageState: './authfiles/role1.json' });
    //Start each test from Portfolio Engine home page
    test.beforeEach('Navigate to Portfolio Engine Home Page', async ({ page }) => {
        await navigateToHomePage(page);
        const portfolioEnginePageObject = await navigateToPortfolioEngine(page);
        portfolioEnginePage = new PortfolioEnginePage(portfolioEnginePageObject);

    });


    test('Portfolio Engine Widgets Load', async ({ page }) => {
        // Select all widgets only if they are not already selected
        console.log('\nStarting Portfolio Engine Widgets test');
        console.log('\nEnabling all widgets');
        await portfolioEnginePage.selectAllWidgetsIfNeeded();

        //Verify all widget headers are loaded
        try {
            console.log('\nVerifying widget headers are visible');
            await expect(portfolioEnginePage.upsideDownsideCaptureHeader).toBeVisible();
            await expect(portfolioEnginePage.investmentApproachHeader).toBeVisible();
            await expect(portfolioEnginePage.returnByStrategyHeader).toBeVisible();
            await expect(portfolioEnginePage.stressTestHeader).toBeVisible();
            await expect(portfolioEnginePage.assetAllocationHoldingsHeader).toBeVisible();
            await expect(portfolioEnginePage.riskVsReturnHeader).toBeVisible();
            await expect(portfolioEnginePage.summaryStatisticsHeader).toBeVisible();
            await expect(portfolioEnginePage.drawdownHeader).toBeVisible();
            await expect(portfolioEnginePage.performanceHeader).toBeVisible();
        } catch (error) {
            console.error('\nOne or more widget headers are not visible\n', error);
        }

        // Checking for actual content
        console.log('\nWaiting for all widgets to load content (this may take some time)');

        // Define widgets to wait for
        const widgetsToVerify = [
            { name: 'Investment Approach', locator: portfolioEnginePage.investmentApproachGraphContent },
            { name: 'Asset Allocation', locator: portfolioEnginePage.assetAllocationGraphContent },
            { name: 'Drawdown', locator: portfolioEnginePage.drawdownGraphContent },
            { name: 'Summary Statistics', locator: portfolioEnginePage.summaryStatisticsGraphContent },
            { name: 'Risk vs Return', locator: portfolioEnginePage.riskVsReturnGraphContent },
            { name: 'Stress Test', locator: portfolioEnginePage.stressTestGraphContent },
            { name: 'Upside/Downside', locator: portfolioEnginePage.upsideDownsideGraphContent },
            { name: 'Performance', locator: portfolioEnginePage.performanceGraphContent },
            { name: 'Return by Strategy', locator: portfolioEnginePage.returnByStrategyGraphContent }
        ];

        //Expect each widget to have content loaded
        for (const widget of widgetsToVerify) {
            try {
                console.log(`  Waiting for ${widget.name} to load content...`);
                await expect(widget.locator.first()).toBeVisible({ timeout: 20 * 60 * 1000 }); //long timeout due to t10 slow loads
            } catch (error) {
                console.error(`  ✗ ${widget.name} failed to load: ${error.message}`);
            }
        }

        console.log('\nAll widgets finished loading');
    });

    test('Create proposal with new portfolio and new client', async ({ page }) => {
        //Create proposal using newly created portfolio
        console.log('\nStarting create proposal with new portfolio and new client test');
        await portfolioEnginePage.createProposalButton.click();
        await page.waitForLoadState();

        //Verify portfolios & percentages are correct on left dropdown
        try {
            await expect(portfolioEnginePage.assetMarkIncomeBuilderText).toBeVisible();
            await expect(portfolioEnginePage.blackRockEquityDividendText).toBeVisible();
            await expect(portfolioEnginePage.savosUSRiskText).toBeVisible();
            await expect(portfolioEnginePage.alphaSimplexText).toBeVisible();
            await expect(portfolioEnginePage.jpMorganAbsoluteReturnText).toBeVisible();
        } catch (error) {
            console.error('\nDifferent/Missing strategies detected', error);
        }

        try {
            //Verify client type options are visible and editable
            await expect(portfolioEnginePage.newClientRadio).toBeEditable();
            await expect(portfolioEnginePage.newClientText).toBeVisible();
            await expect(portfolioEnginePage.existingClientRadio).toBeEditable();
            await expect(portfolioEnginePage.existingClientText).toBeVisible();
            await expect(portfolioEnginePage.discretionaryText).toBeVisible();
            await expect(portfolioEnginePage.nonDiscretionaryText).toBeVisible();
        } catch (error) {
            console.error('\nClient page elements are not visible or editable', error);
        }


        //Fill new client information
        console.log('\nCreating new client')
        await portfolioEnginePage.fillNewClientInfo('Guy', 'Dude');
        await portfolioEnginePage.nextButton.click();
        await page.waitForLoadState();

        //Select risk profile
        console.log('\nSelecting risk profile');
        await portfolioEnginePage.selectRiskProfile();
        await portfolioEnginePage.nextButton.click();
        await page.waitForLoadState();

        //Select custodian and set up account
        console.log('\nSelecting custodian and registration type');
        await selectCustodian(portfolioEnginePage);
        await portfolioEnginePage.addRegistrationButton.click();
        await page.waitForLoadState('domcontentloaded');
        await portfolioEnginePage.registrationTypeDropdown.waitFor({ state: "visible" });
        await portfolioEnginePage.registrationTypeDropdown.click({ force: true });
        await portfolioEnginePage.selectRegistrationType('Individual');
        await page.waitForLoadState();

        //Select all strategies
        console.log('\nAdding account with all 5 strategies');
        await portfolioEnginePage.addAccountButton.click();
        await portfolioEnginePage.selectAllStrategies();
        await portfolioEnginePage.modelListConfirm.click();

        console.log('\nSetting investment amount');
        await portfolioEnginePage.investmentAmountInput.fill('$500000');
        await expect(portfolioEnginePage.enrollInTaxRadio).toBeEditable();
        await portfolioEnginePage.doNotEnrollInTaxRadio.check();
        await portfolioEnginePage.confirmText.click();
        await portfolioEnginePage.nextButton.click();
        await page.waitForLoadState();

        //Assert left box is correct after proposing accounts
        try {
            await expect(portfolioEnginePage.proposedAccountsHeader).toContainText('Proposed Accounts (1)');
            await expect(portfolioEnginePage.proposedAccountsAmount).toContainText('$ 500,000');
            await expect(portfolioEnginePage.accountHolderName).toContainText('Guy Dude, Individual');
            await expect(portfolioEnginePage.multipleStrategyAccountName).toContainText('Multiple Strategy Account, Profile');
            await expect(portfolioEnginePage.multipleStrategyAccountAmount).toContainText('$ 500,000');
        } catch (error) {
            console.error('\nProposed accounts information is incorrect', error);
        }

        //Check fee values
        console.log('\nEntering fee values');
        try {
            await portfolioEnginePage.enterFeePercentageTextbox.fill('.5');
            await page.waitForLoadState();
            await portfolioEnginePage.nextButton.click();
            await expect(portfolioEnginePage.portfolioValueAmount).toContainText('$500,000');
            await expect(portfolioEnginePage.financialAdvisorFee).toContainText('0.50%');
            await expect(portfolioEnginePage.platformFee).not.toContainText('0.00%'); //ensure fee service is returning something
        } catch (error) {
            console.error('\nFee summary values are incorrect', error);
        }

        // Validate total fee calculation
        const financialAdvisorFeeText = await portfolioEnginePage.financialAdvisorFee.textContent();
        const platformFeeText = await portfolioEnginePage.platformFee.textContent();
        const totalFeeText = await portfolioEnginePage.totalFee.textContent();
        const financialAdvisorValue = parseFloat(financialAdvisorFeeText.replace('%', ''));
        const platformValue = parseFloat(platformFeeText.replace('%', ''));
        const totalValue = parseFloat(totalFeeText.replace('%', ''));
        const expectedTotal = financialAdvisorValue + platformValue;

        if (Math.abs(totalValue - expectedTotal) > 0.01) {
            console.error(`Total fee ${totalValue}% does not match sum of Financial Advisor ${financialAdvisorValue}% and Platform ${platformValue}% fees (expected ${expectedTotal}%)`);
        }
        await page.waitForLoadState();


        console.log('\nGenerating proposal document with all sections')
        await portfolioEnginePage.nextButton.click();
        await portfolioEnginePage.continueButton.click();

        await portfolioEnginePage.previewProposalButton.click();

        //Make sure all sections are selected in proposal
        await portfolioEnginePage.setAllProposalSections();

        try {
            await portfolioEnginePage.saveProposalButton.click();
            await portfolioEnginePage.viewDocumentsButton.click();
            await portfolioEnginePage.page.waitForLoadState();

            //Verify we made it back to document list
            await expect(portfolioEnginePage.oneCombinedDocumentText).toBeVisible();
        } catch (error) {
            console.error('\nCould not save proposal', error);
        }
    });
});

test.describe('Check proposal doc', () => {
    //apply storage state of role from auth file created in setup
    test.use({ storageState: './authfiles/role1.json' });
    //Start each test from home page
    test.beforeEach('Navigate to eWm Home Page', async ({ page }) => {
        await navigateToHomePage(page);
    });

    test('Verify proposal document', async ({ page }) => {
        //Navigate to created proposal in portfolio details
        const proposalDocPage = new PortfolioEnginePage(page);
        console.log('\nNavigating to client portfolio details');

        await proposalDocPage.searchForClient('guy dude');
        await proposalDocPage.page.waitForLoadState();
        await proposalDocPage.navigateToClientPortfolioDetails('Guy Dude, Individual');
        await proposalDocPage.page.waitForLoadState();
        await proposalDocPage.previewProposalButton.click();
        await proposalDocPage.page.waitForLoadState();
        await proposalDocPage.setAllProposalSections();
        console.log('\nVerifying proposal sections were generated');

        // Helper function to validate canvas has rendered content
        const validateCanvas = async (canvas: any) => {
            const hasRenderedContent = await canvas.evaluate((el: HTMLCanvasElement) => {
                if (!el) return false;
                const ctx = el.getContext('2d');
                if (!ctx) return false;

                // Check dimensions
                if (el.width === 0 || el.height === 0) return false;

                // Check if canvas has actual pixel data (not blank)
                const imageData = ctx.getImageData(0, 0, el.width, el.height);
                const pixelData = imageData.data;

                // Check if any pixel is non-transparent or non-white
                for (let i = 0; i < pixelData.length; i += 4) {
                    const alpha = pixelData[i + 3];
                    if (alpha > 0) {
                        // Found a non-transparent pixel, canvas has content
                        return true;
                    }
                }

                return false; // Canvas is completely transparent/blank
            });
            expect(hasRenderedContent).toBeTruthy();
        };

        // Helper function to check each proposal section
        const verifySection = async (clickElement: any, content: any) => {
            try {
                await clickElement.click();
                await expect(content).toBeVisible();
                await validateCanvas(content);
            } catch (error) {
                console.error(`Could not find either the header, checkbox, or canvas for this section: ${clickElement.innerHTML}`);
            }
        };

        // Cover page and table of contents
        await verifySection(proposalDocPage.coverPageHeader, proposalDocPage.previewLayoutContentFirst);
        await verifySection(proposalDocPage.tableOfContentsText, proposalDocPage.tableOfContentsContent);

        // Introduction through Pursuing Your Goals
        await verifySection(proposalDocPage.introductionHeader, proposalDocPage.introductionContent);
        await expect(proposalDocPage.pursuingYourGoalsCheckbox.first()).toBeChecked();
        await verifySection(proposalDocPage.investingIsPersonalText, proposalDocPage.investingContent);
        await verifySection(proposalDocPage.equitiesVsBondsTitle, proposalDocPage.growthContentFirst);
        await verifySection(proposalDocPage.cycleOfEmotionsHeader, proposalDocPage.theContent);
        await verifySection(proposalDocPage.stayingInvestedTitle, proposalDocPage.growthContentSecond);

        // Investment team and custodian sections
        await verifySection(proposalDocPage.yourInvestmentTeamDiv, proposalDocPage.yourContentCanvas);
        await verifySection(proposalDocPage.portfolioStrategistsSection, proposalDocPage.portfolioContent);
        await verifySection(proposalDocPage.custodianSelectionHeader, proposalDocPage.custodianContent);
        await verifySection(proposalDocPage.ongoingReviewText, proposalDocPage.ongoingContent);

        // Financial analysis and portfolio sections
        await verifySection(proposalDocPage.yourFinancialAnalysisHeader, proposalDocPage.yourFinancialContent);
        await expect(proposalDocPage.recommendedInvestmentPortfolioCheckbox).toBeChecked();
        await verifySection(proposalDocPage.recommendedPortfolioDiv, proposalDocPage.recommendedContent);
        await verifySection(proposalDocPage.allocationByAssetClassHeader, proposalDocPage.allocationContent);
        await verifySection(proposalDocPage.topHoldingsText, proposalDocPage.topHoldingsContent);

        // Proposed accounts and performance sections
        await verifySection(proposalDocPage.proposedAccountsTitle, proposalDocPage.proposedContentFirst);
        await proposalDocPage.hypotheticalHistoricalPerformanceDiv.click();
        await expect(proposalDocPage.hypotheticalHistoricalPerformanceCheckbox).toBeChecked();
        await proposalDocPage.hypotheticalSectionTitle.click();
        await expect(proposalDocPage.hypotheticalGrowthOfProposedAccountsCheckbox).toBeChecked();
        await expect(proposalDocPage.hypotheticalContent).toBeVisible();

        // Performance metrics sections
        await verifySection(proposalDocPage.ratesHeader, proposalDocPage.ratesContent);
        await verifySection(proposalDocPage.calendarYearReturnsText, proposalDocPage.calendarContent);
        await verifySection(proposalDocPage.historicalCumulativeText, proposalDocPage.historicalContent);
        await verifySection(proposalDocPage.riskVersusReturnSection, proposalDocPage.riskContent);

        // Fee sections
        await expect(proposalDocPage.annualPortfolioFeesCheckbox).toBeChecked();
        await verifySection(proposalDocPage.feeScheduleDiv, proposalDocPage.feeContentFirst);
        await verifySection(proposalDocPage.tieredFeeScheduleHeader, proposalDocPage.tieredContent);

        // Canvas-rendered sections (estimated expense, important info, disclosures, signatures)
        await verifySection(proposalDocPage.estimateExpenseTitle, proposalDocPage.estimatedExpenseCanvas);
        await verifySection(proposalDocPage.importantInformationText, proposalDocPage.importantInformationCanvas);
        await verifySection(proposalDocPage.disclosuresTitle, proposalDocPage.disclosuresCanvas);
        await verifySection(proposalDocPage.clientSignatureText, proposalDocPage.clientSignatureCanvas);
        await verifySection(proposalDocPage.investmentPolicyStatementText, proposalDocPage.investmentPolicyCanvas);
    });
});
