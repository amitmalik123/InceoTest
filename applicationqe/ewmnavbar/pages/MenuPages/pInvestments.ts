import { type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class InvestmentsPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    readonly hInvestments: Locator;
    
    // --- Sub Menus ---
    readonly smStrategies: Locator;
    readonly smResearch: Locator;
    readonly smNews: Locator;
    readonly smCash: Locator;
    readonly smSMA: Locator;
    readonly smGuidedPortfolios: Locator;
    readonly smDAF: Locator;
    readonly smSavos: Locator;
    readonly smTMS: Locator;
    readonly smDirectIndexing: Locator;
    readonly smMorningstar: Locator;

    // --- Buttons ---
    readonly btnInvestmentChange: Locator;
    readonly btnCreateProposal: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        this.hInvestments = page.locator('h1[class*="pageHeader"]:has-text("Investments")');
        
        // Navigation Links
        this.smStrategies = page.getByRole('link', { name: 'Strategies', exact: true });
        this.smResearch = page.getByRole('link', { name: 'Research', exact: true });
        this.smNews = page.getByRole('link', { name: 'News', exact: true });
        this.smCash = page.getByRole('link', { name: 'Cash', exact: true });
        this.smSMA = page.getByRole('link', { name: 'SMA', exact: true });
        this.smGuidedPortfolios = page.getByRole('link', { name: 'Guided Portfolios', exact: true });
        this.smDAF = page.getByRole('link', { name: 'DAF', exact: true });
        this.smSavos = page.getByRole('link', { name: 'Savos', exact: true });
        this.smTMS = page.getByRole('link', { name: 'TMS', exact: true });
        this.smDirectIndexing = page.getByRole('link', { name: 'Direct Indexing', exact: true });
        this.smMorningstar = page.getByRole('link', { name: 'Morningstar', exact: true });
        
        this.btnInvestmentChange = page.locator('button', { hasText: 'Investment Change' });
        this.btnCreateProposal = page.locator('button', { hasText: 'Create Proposal' });
    }

    // ==========================================================
    // 🧭 Navigation
    // ==========================================================
    async goToPage() {
        await this.fBrowser.goToURL('/investments');
        await this.fElement.log('Navigating to Investments Page');
    }

    // ==========================================================
    // 🔍 Validation Checks
    // ==========================================================
    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.hInvestments, 'Investments Header');
        await this.fElement.log('✅ Landed on Page: Investments');
    }

    async SubMenusExist() {
        await this.fElement.log('📢 Verifying Investments Submenus...');

        await this.fElement.elemVisible(this.smStrategies, 'submenu Strategies');
        await this.fElement.elemVisible(this.smResearch, 'submenu Research');
        await this.fElement.elemVisible(this.smNews, 'submenu News');
        await this.fElement.elemVisible(this.smCash, 'submenu Cash');
        await this.fElement.elemVisible(this.smSMA, 'submenu SMA');
        await this.fElement.elemVisible(this.smGuidedPortfolios, 'submenu Guided Portfolio');
        await this.fElement.elemVisible(this.smDAF, 'submenu DAF');
        await this.fElement.elemVisible(this.smSavos, 'submenu Savos');
        await this.fElement.elemVisible(this.smTMS, 'submenu TMS');

        // Optional / Future items (commented out in original)
        // await this.fElement.elemVisible(this.smDirectIndexing, 'submenu Direct Indexing');
        // await this.fElement.elemVisible(this.smMorningstar, 'submenu Morningstar');
        // await this.fElement.elemVisible(this.btnInvestmentChange, 'button Investment Change');
        // await this.fElement.elemVisible(this.btnCreateProposal, 'button Create Proposal');

        await this.fElement.log('✅ All Investments submenus are visible.');
    }
}