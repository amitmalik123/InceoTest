import { test, expect, Page } from '@playwright/test';


let page1: Page;

test.describe('Portfolio Engine Happy Path Tests', () => {
    //apply storage state of role from auth file created in setup
    test.use({ storageState: './authfiles/role1.json' });
    //Start each test from home page
    test.beforeEach('Navigate to Home Page', async ({ page }) => {
        console.log('baseURL:', process.env.baseURL);

        await page.goto(process.env.baseURL + '/en.aspx');
        await page.waitForLoadState('networkidle');
        //Navigate to Portfolio Engine
        await page.getByRole('link', { name: 'Investments' }).click();
        await page.getByRole('link', { name: 'PortfolioEngine', exact: true }).click();
        const page1Promise = page.waitForEvent('popup');
        await page.getByRole('img', { name: 'Launch Portfolio Engine' }).first().click();
        page1 = await page1Promise;
        await page.waitForLoadState('domcontentloaded');
        await page.waitForLoadState('networkidle');
        
        
    });

    test('Portfolio Engine Widgets Load', async ({ page }) => {
        /**TODO: Add code to select all widgets if necessary */
        //Verify all widgets is loading
        await expect(page1.locator('header').filter({ hasText: 'Upside/Downside Capture' })).toBeVisible();
        await expect(page1.locator('header').filter({ hasText: 'Investment Approach' })).toBeVisible();
        await expect(page1.locator('header').filter({ hasText: 'Return by Strategy' })).toBeVisible();
        await expect(page1.locator('header').filter({ hasText: 'Stress Test' })).toBeVisible();
        await expect(page1.locator('header').filter({ hasText: 'Asset Allocation & Holdings' })).toBeVisible();
        await expect(page1.locator('header').filter({ hasText: 'Risk vs Return' })).toBeVisible();
        await expect(page1.locator('header').filter({ hasText: 'Summary Statistics' })).toBeVisible();
        await expect(page1.locator('header').filter({ hasText: 'Drawdown' })).toBeVisible();
        await expect(page1.locator('header').filter({ hasText: 'Performance' })).toBeVisible();
        
    });


    test('Add strategies to portfolio', async ({ page }) => {
        //add strategies to portfolio
        await page1.getByRole('button', { name: 'Manage Portfolios' }).click();
        await page1.getByRole('button', { name: 'Create New Model Portfolio' }).click();
        await page1.getByText('AssetMark Platform Strategies', { exact: true }).click();
        await page1.getByRole('textbox', { name: 'Search' }).fill('assetmark income builder, profile 2, conservative');
        await page1.getByText('Add to Portfolio').click();
        await page1.getByRole('textbox', { name: 'Search' }).fill('blackrock equity dividend');
        await page1.getByText('Add to Portfolio').click();
        await page1.getByRole('textbox', { name: 'Search' }).fill('savos us risk controlled strategy, profile 6');
        await page1.getByText('Add to Portfolio').click();
        await page1.getByRole('textbox', { name: 'Search' }).fill('alphasimplex, alternative model portfolio, profile 5, growth');
        await page1.getByText('Add to Portfolio').click();
        await page1.getByRole('textbox', { name: 'Search' }).fill('jpmorgan absolute return - profile 1');
        await page1.getByText('Add to Portfolio').click();
        await page1.getByRole('textbox', { name: 'Model Portfolio Name' }).fill('Test Portfolio');
        await page1.getByRole('button', { name: 'Save' }).click();
        page1.waitForLoadState('domcontentloaded'); //wait for page to load
        //Verify each strategy was added
        await expect(page1.getByText('Investment Allocation100 %Add')).toContainText('Core MarketsAssetMark Income Builder, Profile 2, ConservativeETF | 2Tactical Strategies - Enhanced Return FocusBlackRock Equity DividendIMA | 6Tactical Strategies - Limit Loss FocusSavos US Risk Controlled Strategy, Profile 6GMS | 6Diversifying Strategies - Equity AlternativesAlphaSimplex, Alternative Model Portfolio, Profile 5, GrowthMF | 5Diversifying Strategies - Bonds and Bond AlternativesJPMorgan Absolute Return - Profile 1MF | 1');
        //verify allocation percentages
        await expect(page1.getByRole('textbox').first()).toHaveValue('20');
        await expect(page1.getByRole('textbox').nth(1)).toHaveValue('20');
        await expect(page1.getByRole('textbox').nth(2)).toHaveValue('20');
        await expect(page1.getByRole('textbox').nth(3)).toHaveValue('20');
        await expect(page1.getByRole('textbox').nth(4)).toHaveValue('20');
    });

    test('Create proposal with new portfolio and new client', async ({ page }) => {
        //Create proposal using newly created portfolio
        await page1.getByRole('button', { name: 'Create Proposal' }).click();
        await page1.getByRole('img').nth(1).click();
        await page1.getByRole('button', { name: 'Create Proposal' }).click(); //opening twice becuase the page does not always load the first time
        await page.waitForLoadState('networkidle');
        //Verify portfolios & percentages are correct on left dropdown
        await expect(page1.getByText('AssetMark Income Builder, Profile 2, Conservative20%')).toBeVisible();
        await expect(page1.getByText('BlackRock Equity Dividend20%')).toBeVisible();
        await expect(page1.getByText('Savos US Risk Controlled Strategy, Profile 620%')).toBeVisible();
        await expect(page1.getByText('AlphaSimplex, Alternative Model Portfolio, Profile 5, Growth20%')).toBeVisible();
        await expect(page1.getByText('JPMorgan Absolute Return - Profile 120%')).toBeVisible();

        //existing client route
        // await page1.getByRole('radio', { name: 'Existing Client' }).check();
        // await page1.getByRole('searchbox').click();
        // await page1.getByRole('searchbox').fill('guy');
        // await page1.getByRole('button', { name: 'Dude, Guy' }).first().click();


        await expect(page1.getByRole('radio', { name: 'New Client' })).toBeEditable();
        await expect(page1.getByText('New Client')).toBeVisible();
        await expect(page1.getByRole('radio', { name: 'Existing Client' })).toBeEditable();
        await expect(page1.getByText('Existing Client')).toBeVisible();
        await expect(page1.getByRole('radio', { name: 'Discretionary', exact: true })).toBeEditable();
        await expect(page1.getByText('Discretionary', { exact: true })).toBeVisible();
        await expect(page1.getByRole('radio', { name: 'Non-Discretionary' })).toBeEditable();
        await expect(page1.getByText('Non-Discretionary')).toBeVisible();
        await page1.getByRole('textbox', { name: 'First' }).fill('Guy');
        await page1.getByRole('textbox', { name: 'Last' }).fill('Dude');
        await page1.getByRole('button', { name: 'NEXT' }).click();
        await page.waitForTimeout(1000); //wait for page to load
        await page1.getByRole('radio', { name: 'Moderate', exact: true }).check();
        await page1.getByRole('radio', { name: '- 9 years' }).check();
        await page1.getByRole('radio', { name: '- 50%' }).check();
        await page1.getByRole('radio', { name: '3 - Moderate' }).check();
        await page1.getByRole('button', { name: 'NEXT' }).click();
        await page.waitForTimeout(1000); //wait for page to load
        await page1.locator('div').filter({ hasText: /^Select$/ }).click();
        await page1.getByText('Fidelity').click();
        await page1.getByRole('img', { name: 'imgEnable' }).click();
        await page1.getByRole('textbox').click();
        await page1.getByRole('textbox').fill('Test Registration');
        await page1.getByRole('img', { name: 'ArrowDown' }).nth(1).click();
        await page1.getByRole('paragraph').filter({ hasText: 'Individual' }).hover();
        await page1.getByRole('listitem').filter({ hasText: /^Individual$/ }).click();

        await page1.getByRole('img', { name: 'img' }).click();
        await page1.getByRole("checkbox", { name: 'AssetMark Income Builder, Profile 2, Conservative' }).click();
        await page1.getByRole("checkbox", { name: 'BlackRock Equity Dividend' }).click();
        await page1.getByRole("checkbox", { name: 'Savos US Risk Controlled Strategy, Profile 6' }).click();
        await page1.getByRole("checkbox", { name: 'AlphaSimplex, Alternative Model Portfolio, Profile 5, Growth' }).click();
        await page1.getByRole("checkbox", { name: 'JPMorgan Absolute Return - Profile 1' }).click();

        await page1.locator('#modelListConfirmEnable').click();
        await page.waitForTimeout(1000); //wait for page to load
        await page1.locator('input[name="investmentAmount"]').fill('$500000');
        await expect(page1.getByRole('radio', { name: 'Enroll in Tax Management Services', exact: true })).toBeEditable();
        await page1.getByRole('radio', { name: 'Do not enroll in Tax' }).check();
        await page1.getByText('CONFIRM', { exact: true }).click();
        await page1.getByRole('button', { name: 'NEXT' }).click();
        
        //assert left box is correct after proposing accounts
        await expect(page1.getByText('Proposed Accounts (1)$')).toContainText('Proposed Accounts (1)$ 500,000');
        await expect(page1.getByRole('paragraph').filter({ hasText: 'Guy Dude, Individual' })).toBeVisible();
        await expect(page1.getByRole('paragraph').filter({ hasText: 'Multiple Strategy Account, Profile ' })).toBeVisible();
        //check fee values
        await page1.getByRole('textbox', { name: 'Enter %' }).fill('1');
        await page1.getByRole('button', { name: 'NEXT' }).click();
        await expect(page1.getByText('Portfolio Value$')).toContainText('500,000');
        await expect(page1.getByText('Financial Advisor1')).toContainText('1.00%');
        await expect(page1.getByText('Platform0')).not.toContainText('0.00%'); //ensure fee service is calculated
        await expect(page1.getByText('Total1')).toContainText('1.54%', { timeout: 30000 }); //ensure total annual fee is calculated
        await page1.getByRole('button', { name: 'NEXT' }).click();
        await page1.getByRole('button', { name: 'Continue' }).click();
        
        //Assert left boxes are correct
        await expect(page1.getByText('Proposed Accounts $500,000New')).toBeVisible();
        await expect(page1.getByText('Guy Dude, Individual$')).toContainText('Guy Dude, Individual$500,000');
        await expect(page1.locator('div').filter({ hasText: /^Funded Accounts\(0\) \$0$/ }).first()).toBeVisible();
        await page1.getByRole('button', { name: 'Preview Proposal' }).click();
        
        //Make sure all sections are selected in proposal
        //check introduction
        page1.locator('.th-wrap.th-Introduction-wrap > .th-header > .th-title > .checkbox-container > .clsA').setChecked(true);
        //check pursue your goals
        await page1.locator('.th-wrap.th-Investing > .th-header > .th-title > .checkbox-container > .clsA').setChecked(true);
        await page1.locator('.th-wrap.th-Investing > .th-header > .th-title > span > .icon-holder > .glyphicon').click();
        //check investing is personal
        await page1.locator('.th-title.th-listview-title.listview-child > .checkbox-container > .clsA').first().setChecked(true);
        //check equities vs bonds
        await page1.locator('.th-wrap.th-Growth > .th-header > .th-title > .checkbox-container > .clsA').first().setChecked(true)
        //check cycle of emotions
        await page1.locator('.th-wrap.th-The > .th-header > .th-title > .checkbox-container > .clsA').setChecked(true);
        //check staying invested
        await page1.locator('.th-wrap.th-Growth > .th-header > .th-title > .checkbox-container > .clsA').nth(1).setChecked(true);
        //check your investment team top box
        await page1.locator('.th-wrap.th-Your > div > .th-title > .checkbox-container > .clsA').first().setChecked(true);
        //check your investment team inside dropdown box
        await page1.locator('.th-wrap.th-Your > div > .th-title > .checkbox-container > .clsA').nth(1).setChecked(true);
        //check portfolio strategists
        await page1.locator('.th-wrap.th-Portfolio > .th-header > .th-title > .checkbox-container > .clsA').setChecked(true);
        //check custodian selection
        await page1.locator('.th-wrap.th-Custodian > .th-header > .th-title > .checkbox-container > .clsA').setChecked(true);
        //check ongoing review
        await page1.locator('.th-wrap.th-Ongoing > .th-header > .th-title > .checkbox-container > .clsA').setChecked(true);
        //check recommended investment portfolio
        await page1.locator('.th-wrap.th-Recommended > div > .th-title > .checkbox-container > .clsA').first().setChecked(true);
        await page1.locator('span').filter({ hasText: 'Recommended Investment Portfolio (4)' }).locator('i').click();
        //check allocation by asset class
        await page1.locator('.th-wrap.th-Allocation > .th-header > .th-title > .checkbox-container > .clsA').setChecked(true);
        //check top holdings
        await page1.locator('.th-wrap.th-Top > .th-header > .th-title > .checkbox-container > .clsA').setChecked(true);
        //check proposed accounts estimated yield
        await page1.locator('.th-wrap.th-Proposed > .th-header > .th-title > .checkbox-container > .clsA').setChecked(true);
        //check hypothetical historical performance
        await page1.locator('.th-wrap.th-Hypothetical > div > .th-title > .checkbox-container > .clsA').first().setChecked(true);
        await page1.locator('.th-wrap.th-Hypothetical > div > .th-title > span > .icon-holder > .glyphicon').click();
        //check hypothetical section
        await page1.locator('.th-wrap.th-Hypothetical > div:nth-child(2) > .th-title > .checkbox-container > .clsA').setChecked(true);
        //check rates section
        await page1.locator('.th-wrap.th-Rates > .th-header > .th-title > .checkbox-container > .clsA').setChecked(true);
        //check calendar year returns
        await page1.locator('.th-wrap.th-Calendar > .th-header > .th-title > .checkbox-container > .clsA').setChecked(true);
        //check historical cumulative performance
        await page1.locator('.th-wrap.th-Historical > .th-header > .th-title > .checkbox-container > .clsA').setChecked(true);
        //check risk versus return
        await page1.locator('.th-wrap.th-Risk > .th-header > .th-title > .checkbox-container > .clsA').setChecked(true);
        //check annual portfolio fees
        await page1.locator('.th-wrap.th-Fee > div > .th-title > .checkbox-container > .clsA').first().setChecked(true);
        await page1.locator('.th-wrap.th-Fee > div > .th-title > span > .icon-holder > .glyphicon').click();
        //check tiered fee schedule
        await page1.locator('.th-wrap.th-Tiered > .th-header > .th-title > .checkbox-container > .clsA').setChecked(true);
        //check estimate expense
        await page1.locator('.th-wrap.th-Estimated > .th-header > .th-title > .checkbox-container > .clsA').setChecked(true);
        //check client signature
        await page1.locator('.th-wrap.th-Client > .th-header > .th-title > .checkbox-container > .clsA').setChecked(true);
        //check investment policy statement
        await page1.locator('.th-wrap.th-Investment > .th-header > .th-title > .checkbox-container').setChecked(true);
        await page1.getByRole('button', { name: 'save proposal' }).click();
        await page1.getByRole('button', { name: 'View Documents' }).click();
        await page1.waitForLoadState('networkidle');
        //Verify we made it back to document list
        await expect(page1.getByText('One Combined Document')).toBeVisible();
    });
});

test.describe('Check proposal doc', () => {
        //apply storage state of role from auth file created in setup
    test.use({ storageState: './authfiles/role1.json' });
    //Start each test from home page
    test.beforeEach('Navigate to Home Page', async ({ page }) => {
        await page.goto(process.env.baseURL + '/en.aspx');
        await page.waitForLoadState('domcontentloaded');
    });

    test('Verify proposal document', async ({ page }) => {
        //Navigate to created proposal in portfolio details
        await page.getByRole('link', { name: 'Clients' }).click();
        await page.locator('#loadingImageModal').click();
        await page.locator('#client_search_input').fill('guy dude');
        await page.locator('#searchbutton').click();
        await page.locator('.ui-sgcollapsed > a').first().click();
        await page.getByRole('link', { name: 'Guy Dude, Individual' }).click();
        await page.getByRole('link', { name: 'View Document History' }).click();
        await page.getByRole('link', { name: 'Portfolio Details' }).click();
        await page.getByRole('button', { name: 'Preview Proposal' }).click();
        await page.waitForLoadState('networkidle');
        //Click through each section and make sure doc is generated
        //check cover page;
        await page.locator('.th-header').first().click();
        await page.getByText('Pursue Your Goals', { exact: true }).click();
        await expect(page.locator('.preview-layout-content').first()).toBeVisible();
        //check table of contents
        await page.getByText('Table Of Contents', { exact: true }).click();
        await expect(page.locator('.page-wrap.Table > .page-component > .preview-layout-component > .preview-layout-content')).toBeVisible();
        //check introduction
        await expect(page.locator('.th-wrap.th-Introduction-wrap > .th-header > .th-title > .checkbox-container > .clsA')).toBeChecked()
        await page.locator('.th-wrap.th-Introduction-wrap > .th-header').click();
        await expect(page.locator('.page-wrap.Introduction-page-component-wrap > .page-component > .preview-layout-component > .preview-layout-content')).toBeVisible();
        //check pursure your goals
        await expect(page.locator('.th-wrap.th-Investing > .th-header > .th-title > .checkbox-container > .clsA')).toBeChecked();
        await page.locator('.th-wrap.th-Investing > .th-header > .th-title > span > .icon-holder > .glyphicon').click();
        //check investing is personal
        await expect(page.locator('.th-title.th-listview-title.listview-child > .checkbox-container > .clsA').first()).toBeChecked();
        await page.getByText('Investing is Personal', { exact: true }).click();
        await expect(page.locator('.page-wrap.Investing > .page-component > .preview-layout-component > .preview-layout-content')).toBeVisible();
        //check equities vs bonds
        await expect(page.locator('.th-wrap.th-Growth > .th-header > .th-title > .checkbox-container > .clsA').first()).toBeChecked();
        await page.locator('.th-wrap.th-Growth > .th-header > .th-title').first().click();
        await expect(page.locator('.page-wrap.Growth > .page-component > .preview-layout-component > .preview-layout-content').first()).toBeVisible();
        //check cycle of emotions
        await expect(page.locator('.th-wrap.th-The > .th-header > .th-title > .checkbox-container > .clsA')).toBeChecked();
        await page.locator('.th-wrap.th-The > .th-header').click();
        await expect(page.locator('.page-wrap.The > .page-component > .preview-layout-component > .preview-layout-content')).toBeVisible();
        //check staying invested
        await expect(page.locator('.th-wrap.th-Growth > .th-header > .th-title > .checkbox-container > .clsA').nth(1)).toBeChecked();
        await page.locator('.th-wrap.th-Growth > .th-header > .th-title').nth(1).click();
        // change this to select the actual text box await page.getByRole('listitem').filter({ hasText: '4' }).click();
        await expect(page.locator('.page-wrap.Growth > .page-component > .preview-layout-component > .preview-layout-content').nth(1)).toBeVisible();
        //check your investment team
        await expect(page.locator('.th-wrap.th-Your > div > .th-title > .checkbox-container > .clsA').first()).toBeChecked();
        await page.locator('.th-wrap.th-Your > div:nth-child(2)').click();
        await expect(page.locator('.page-wrap.Your > .page-component > .preview-layout-component > .preview-layout-content > div > .react-pdf__Document > .react-pdf__Page > .react-pdf__Page__canvas').first()).toBeVisible();
        //check portfolio strategists
        await expect(page.locator('.th-wrap.th-Portfolio > .th-header > .th-title > .checkbox-container > .clsA')).toBeChecked();
        await page.locator('.th-wrap.th-Portfolio').click();
        await expect(page.locator('.page-wrap.Portfolio > .page-component > .preview-layout-component > .preview-layout-content')).toBeVisible();
        //check custodian selection
        await expect(page.locator('.th-wrap.th-Custodian > .th-header > .th-title > .checkbox-container > .clsA')).toBeChecked();
        await page.locator('.th-wrap.th-Custodian > .th-header').click();
        await expect(page.locator('.page-wrap.Custodian > .page-component > .preview-layout-component > .preview-layout-content')).toBeVisible();
        //check ongoing review
        await expect(page.locator('.th-wrap.th-Ongoing > .th-header > .th-title > .checkbox-container > .clsA')).toBeChecked();
        await page.getByText('Ongoing Review of Your Portfolio', { exact: true }).click();
        await expect(page.locator('.page-wrap.Ongoing > .page-component > .preview-layout-component > .preview-layout-content')).toBeVisible();
        //check your financial analysis;
        await page.locator('.th-wrap.th-Your.Financial > .th-header').click();
        await expect(page.locator('.page-wrap.Your.Financial > .page-component > .preview-layout-component > .preview-layout-content')).toBeVisible();
        //check recommended investment portfolio
        await expect(page.locator('.th-wrap.th-Recommended > div > .th-title > .checkbox-container > .clsA').first()).toBeChecked();
        await page.locator('span').filter({ hasText: 'Recommended Investment Portfolio (4)' }).locator('i').click();
        //check recommended portfolio
        await page.locator('.th-wrap.th-Recommended > div:nth-child(2)').click();
        await expect(page.locator('.page-wrap.Recommended > .page-component > .preview-layout-component > .preview-layout-content')).toBeVisible();
        //check allocation by asset class
        //await expect(page.locator('.th-wrap.th-Allocation > .th-header > .th-title > .checkbox-container > .clsA')).toBeChecked();
        await page.locator('.th-wrap.th-Allocation > .th-header').click();
        await expect(page.locator('.page-wrap.Allocation > .page-component > .preview-layout-component > .preview-layout-content')).toBeVisible();
        //check top holdings
        //await expect(page.locator('.th-wrap.th-Top > .th-header > .th-title > .checkbox-container > .clsA')).toBeChecked();
        await page.getByText('Top Holdings').first().click();
        await expect(page.locator('.page-wrap.Top > .page-component > .preview-layout-component > .preview-layout-content')).toBeVisible();
        //check proposed accounts estimated yield
        await expect(page.locator('.th-wrap.th-Proposed > .th-header > .th-title > .checkbox-container > .clsA')).toBeChecked();
        await page.locator('.th-wrap.th-Proposed > .th-header > .th-title').click();
        await expect(page.locator('.page-wrap.Proposed > .page-component > .preview-layout-component > .preview-layout-content').first()).toBeVisible();
        //check hypothetical historical performance
        //await expect(page.locator('.th-wrap.th-Hypothetical > div > .th-title > .checkbox-container > .clsA').first()).toBeChecked();
        await page.locator('div').filter({ hasText: /^Hypothetical Historical Performance \(5\)$/ }).nth(2).click();
        await page.locator('.th-wrap.th-Hypothetical > div > .th-title > span > .icon-holder > .glyphicon').click();
        //check hypothetical section
        //await expect(page.locator('.th-wrap.th-Hypothetical > div:nth-child(2) > .th-title > .checkbox-container > .clsA')).toBeChecked();
        await page.locator('.th-wrap.th-Hypothetical > div:nth-child(2) > .th-title').click();
        await expect(page.locator('.page-wrap.Hypothetical > .page-component > .preview-layout-component > .preview-layout-content')).toBeVisible();
        //check rates section
        await expect(page.locator('.th-wrap.th-Rates > .th-header > .th-title > .checkbox-container > .clsA')).toBeChecked();
        await page.locator('.th-wrap.th-Rates > .th-header').click();
        await expect(page.locator('.page-wrap.Rates > .page-component > .preview-layout-component > .preview-layout-content')).toBeVisible();
        //check calendar year returns
        //await expect(page.locator('.th-wrap.th-Calendar > .th-header > .th-title > .checkbox-container > .clsA')).toBeChecked();
        await page.getByText('Calendar Year Returns', { exact: true }).click();
        await expect(page.locator('.page-wrap.Calendar > .page-component > .preview-layout-component > .preview-layout-content')).toBeVisible();
        //check historical cumulative performance
        //await expect(page.locator('.th-wrap.th-Historical > .th-header > .th-title > .checkbox-container > .clsA')).toBeChecked();
        await page.getByText('Historical Cumulative').first().click();
        await expect(page.locator('.page-wrap.Historical > .page-component > .preview-layout-component > .preview-layout-content')).toBeVisible();
        //check risk versus return
        //await expect(page.locator('.th-wrap.th-Risk > .th-header > .th-title > .checkbox-container > .clsA')).toBeChecked();
        await page.locator('.th-wrap.th-Risk').click();
        await expect(page.locator('.page-wrap.Risk > .page-component > .preview-layout-component > .preview-layout-content')).toBeVisible();
        //check annual portfolio fees
        await expect(page.locator('.th-wrap.th-Fee > div > .th-title > .checkbox-container > .clsA').first()).toBeChecked();
        await page.locator('.th-wrap.th-Fee > .th-header > .th-title > span > .icon-holder > .glyphicon').click();
        //check fee schedule
        await page.locator('.th-wrap.th-Fee > div:nth-child(2)').click();
        await expect(page.locator('.page-wrap.Fee > .page-component > .preview-layout-component > .preview-layout-content').first()).toBeVisible();
        //check tiered fee schedule
        await expect(page.locator('.th-wrap.th-Tiered > .th-header > .th-title > .checkbox-container > .clsA')).toBeChecked();
        await page.locator('.th-wrap.th-Tiered > .th-header').click();
        await expect(page.locator('.page-wrap.Tiered > .page-component > .preview-layout-component > .preview-layout-content')).toBeVisible();
        //check estimate expense
        await expect(page.locator('.th-wrap.th-Estimated > .th-header > .th-title > .checkbox-container > .clsA')).toBeChecked();
        await page.locator('.th-wrap.th-Estimated > .th-header > .th-title').click();
        await expect(page.locator('.page-wrap.Estimated.Expense > .page-component > .preview-layout-component > .preview-layout-content > div > .react-pdf__Document > .react-pdf__Page > .react-pdf__Page__canvas')).toBeVisible();
        //check important information
        await page.getByText('Important Information and Standardized Performance Returns', { exact: true }).click();
        await expect(page.locator('.page-wrap.Important.Information > .page-component > .preview-layout-component > .preview-layout-content > div > .react-pdf__Document > .react-pdf__Page > .react-pdf__Page__canvas')).toBeVisible();
        //check disclosures
        await page.locator('.th-wrap.th-Disclosures > .th-header > .th-title').click();
        await expect(page.locator('.page-wrap.Disclosures > .page-component > .preview-layout-component > .preview-layout-content > div > .react-pdf__Document > .react-pdf__Page > .react-pdf__Page__canvas')).toBeVisible();
        //check client signature
        await expect(page.locator('.th-wrap.th-Client > .th-header > .th-title > .checkbox-container > .clsA')).toBeChecked();
        await page.getByText('Client Signature', { exact: true }).click();
        await expect(page.locator('.page-wrap.Client > .page-component > .preview-layout-component > .preview-layout-content > div > .react-pdf__Document > .react-pdf__Page > .react-pdf__Page__canvas')).toBeVisible();
        //check investment policy statement
        await expect(page.locator('.th-wrap.th-Investment > .th-header > .th-title > .checkbox-container')).toBeChecked();
        await page.getByText('Investment Policy Statement', { exact: true }).click();
        await expect(page.locator('.page-wrap.Investment.Policy > .page-component > .preview-layout-component > .preview-layout-content > div > .react-pdf__Document > .react-pdf__Page > .react-pdf__Page__canvas')).toBeVisible();
    });
});

test.describe('Teardown - Cleanup created portfolio and logout', () => {
    //apply storage state of role from auth file created in setup
    test.use({ storageState: './authfiles/role1.json' });
    //Start each test from home page
    test.beforeEach('Navigate to Home Page', async ({ page }) => {
        await page.goto(process.env.baseURL + '/en.aspx');
        await page.waitForLoadState('networkidle');
    });
/*Move to teardown to ensure cleanup happens even if a test fails*/
    test('Cleanup - Delete created portfolio and logout', async ({ page }) => {        
        //delete created portfolio
        console.log(process.env.baseURL)
        await page.goto(process.env.baseURL + '/portfolioengine/create');
        await page.getByRole('button', { name: 'Manage Portfolios' }).click();
        await page.locator('tr:nth-child(2) > .table-component__cell__2rhe1.table-child__cell__3SV_1.table-child__cell_controls__2U_PE > div').click();
        await page.getByText('Delete').click();
        await page.getByRole('button', { name: 'Delete' }).click();
    });

    test('Logout', async ({ page }) => {
        //logout
        await page.getByRole('link', { name: 'Logout' }).click();
        await page.waitForLoadState('networkidle');
        await expect(page.getByRole('textbox', { name: 'Username' })).toBeVisible();
        await page.close();
    });
});