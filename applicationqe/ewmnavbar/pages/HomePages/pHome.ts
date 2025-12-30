import { type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class HomePage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    // --- Navigation Menu ---
    readonly navLeftBar: Locator;
    readonly mDashboard: Locator;
    readonly mClients: Locator;
    readonly mActionItems: Locator;
    readonly mModels: Locator;
    readonly mInvestments: Locator;
    readonly mProductsServices: Locator;
    readonly mHelpSupport: Locator;

    // --- Header & User Menu ---
    readonly btnProfile: Locator;
    readonly btnArrow: Locator;
    readonly btnMoreMenus: Locator;
    readonly secMoreMenus: Locator;

    // --- Page Content & Footer ---
    readonly lnkBreadCrumbs: Locator;
    readonly secSiteCore: Locator;
    readonly secFooter: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        // Navigation
        this.navLeftBar = page.locator('.css-r80wwa');
        this.mDashboard = page.getByRole('link', { name: 'Dashboard' });
        this.mClients = page.getByRole('link', { name: 'Clients' });
        this.mActionItems = page.getByRole('link', { name: 'Action Items' });
        this.mModels = page.getByRole('link', { name: 'Models' });
        this.mInvestments = page.getByRole('link', { name: 'Investments' });
        this.mProductsServices = page.getByRole('link', { name: 'Products & Services' });
        this.mHelpSupport = page.getByRole('link', { name: 'Help & Support' });

        // Header / User Profile
        this.btnProfile = page.locator('button.MuiButton-outlined:has(svg.lucide-user-round)');
        this.btnArrow = page.locator('.css-wbbo4c');
        this.btnMoreMenus = page.locator('button.MuiButtonBase-root.MuiIconButton-root.MuiIconButton-sizeMedium');
        this.secMoreMenus = page.locator('.MuiPaper-root.MuiPaper-elevation.MuiPaper-rounded'); 

        // Content / Footer
        this.lnkBreadCrumbs = page.locator('.css-1laf4fm.active');
        this.secSiteCore = page.locator('#sitecore-content');
        this.secFooter = page.locator('#footerMenu');
    }

    // ==========================================================
    // 🧭 Navigation Actions
    // ==========================================================

    async goToHomePage() {
        await this.fBrowser.goToURL('/dashboard');
        await this.fElement.log('Going to Home Page');
        await this.fElement.waitForElemVisible(this.mDashboard, 'menu Dashboard');
    }   

    async clickMoreMenus() {
        await this.fElement.clickElem(this.btnMoreMenus, "More Menus Button");
        await this.fElement.elemVisible(this.secMoreMenus, "More Menus Popover");
    }

    // ==========================================================
    // 🔍 Validation Checks
    // ==========================================================

    async MenusExist() {
        // await this.fElement.elemVisible(this.mDashboard, 'menu Dashboard');
        await this.fElement.elemVisible(this.mClients, 'menu Clients');
        await this.fElement.elemVisible(this.mActionItems, 'menu Action Items');
        await this.fElement.elemVisible(this.mModels, 'menu Models');
        await this.fElement.elemVisible(this.mInvestments, 'menu Investments');
        await this.fElement.elemVisible(this.mProductsServices, 'menu Products & Services');
        await this.fElement.elemVisible(this.mHelpSupport, 'menu Help & Support');
        await this.fElement.elemVisible(this.btnProfile, 'button Profile');
    }

    async SectionSiteCoreExists() {
        await this.fElement.elemVisible(this.secSiteCore, 'section Sitecore', 10000);
        await this.fElement.elemVisible(this.secFooter, 'section Footer');
    }
}