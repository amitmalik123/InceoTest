
import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible } from '../../functions/fElementHelper';

export class InvestmentsPage {
    readonly page: Page;
    readonly hInvestments: Locator;
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
    readonly btnInvestmentChange: Locator;
    readonly btnCreateProposal: Locator;
    // readonly smOne: Locator;

    constructor(page: Page) {
        this.page = page;
        this.hInvestments = page.locator('h1[class*="pageHeader"]:has-text("Investments")');
        this.smStrategies = page.getByRole('link', { name: 'Strategies' });
        this.smResearch = page.getByRole('link', { name: 'Research' });
        this.smNews = page.getByRole('link', { name: 'News' });
        this.smCash = page.getByRole('link', { name: 'Cash' });
        this.smSMA = page.getByRole('link', { name: 'SMA' });
        this.smGuidedPortfolios = page.getByRole('link', { name: 'Guided Portfolio' });
        this.smDAF = page.getByRole('link', { name: 'DAF' });
        this.smSavos = page.getByRole('link', { name: 'Savos' });
        this.smTMS = page.getByRole('link', { name: 'TMS' });
        this.smDirectIndexing = page.getByRole('link', { name: 'Direct Indexing' });
        this.smMorningstar = page.getByRole('link', { name: 'Morningstar' });
        this.btnInvestmentChange = page.locator('button', { hasText: 'Investment Change' });
        this.btnCreateProposal = page.locator('button', { hasText: 'Create Proposal' });
        // this.sm = page.getByRole('link', { name: '' });
    }

    async goToPage(){
        await this.page.goto('/investments');
    }

    async LoadsPage() {
        await elemVisible(this.hInvestments, 'Investments Header', undefined, 1000000);
        console.log('Page loaded for Investments > Strategies');
    }

    async SubMenusExist() {
        await elemVisible(this.smStrategies, 'submenu Strategies');
        await elemVisible(this.smResearch, 'submenu Research');
        await elemVisible(this.smNews, 'submenu News');
        await elemVisible(this.smCash, 'submenu Cash');
        await elemVisible(this.smSMA, 'submenu SMA');
        await elemVisible(this.smGuidedPortfolios, 'submenu Guided Portfolio');
        await elemVisible(this.smDAF, 'submenu DAF');
        await elemVisible(this.smSavos, 'submenu Savos');
        await elemVisible(this.smTMS, 'submenu TMS');
        // await elemVisible(this.smDirectIndexing, 'submenu Direct Indexing');
        // await elemVisible(this.smMorningstar, 'submenu Morningstar');
        // await elemVisible(this.btnInvestmentChange, 'button Investment Change ');
        // await elemVisible(this.btnCreateProposal, 'button Create Proposal');
    }

}

