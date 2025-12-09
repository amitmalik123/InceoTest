import { expect, type Locator, type Page } from "@playwright/test";

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
        await expect(this.hInvestments).toBeVisible({ timeout: 1000000 });
        console.log('Page loaded for Investments > Strategies');
    }

    async SubMenusExist() {
        await expect(this.smStrategies).toBeVisible();
        await expect(this.smResearch).toBeVisible();
        await expect(this.smNews).toBeVisible();
        await expect(this.smCash).toBeVisible();
        await expect(this.smSMA).toBeVisible();
        await expect(this.smGuidedPortfolios).toBeVisible();
        await expect(this.smDAF).toBeVisible();
        await expect(this.smSavos).toBeVisible();
        await expect(this.smTMS).toBeVisible();
        // await expect(this.smDirectIndexing).toBeVisible();
        // await expect(this.smMorningstar).toBeVisible();
        await expect(this.btnInvestmentChange).toBeVisible();
        await expect(this.btnCreateProposal).toBeVisible();
    }

}

