
import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible, waitForElem } from '../../functions/fElementHelper';
type Logger = (msg: string) => Promise<void>;

export class HomePage {
    readonly page: Page;
    private logger: Logger;
    readonly navLeftBar: Locator;
    readonly mDashboard: Locator;
    readonly mClients: Locator;
    readonly mActionItems: Locator;
    readonly mModels: Locator;
    readonly mInvestments: Locator;
    readonly mProductsServices: Locator;
    readonly mHelpSupport: Locator;
    readonly btnProfile: Locator;
    readonly btnArrow: Locator;
    readonly btnMoreMenus: Locator;
    readonly secMoreMenus: Locator;
    readonly lnkBreadCrumbs: Locator;
    readonly secSiteCore: Locator;
    readonly secFooter: Locator;



    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;
        this.navLeftBar = page.locator('.css-r80wwa');
        this.mDashboard = page.getByRole('link', { name: 'Dashboard' });
        // this.mDashboard = page.getByRole('link', { name: /Dashboard/i });
        this.mClients = page.getByRole('link', { name: 'Clients' });
        this.mActionItems = page.getByRole('link', { name: 'Action Items' });
        this.mModels = page.getByRole('link', { name: 'Models' });
        this.mInvestments = page.getByRole('link', { name: 'Investments' });
        this.mProductsServices = page.getByRole('link', { name: 'Products & Services' });
        this.mHelpSupport = page.getByRole('link', { name: 'Help & Support' });
        this.btnProfile = page.locator('button.MuiButton-outlined:has(svg.lucide-user-round)');
        this.btnArrow = page.locator('.css-wbbo4c');
        this.btnMoreMenus = page.locator('button.MuiButtonBase-root.MuiIconButton-root.MuiIconButton-sizeMedium');
        this.secMoreMenus = page.locator('MuiPaper-root.MuiPaper-elevation.MuiPaper-rounded');
        this.lnkBreadCrumbs = page.locator('.css-1laf4fm.active');
        this.secSiteCore = page.locator('#sitecore-content');
        this.secFooter = page.locator('#footerMenu');

    }

    async clickMoreMenus() {
        try {
            await expect(this.btnMoreMenus).toBeVisible();

            await this.logger('Cookie modal found. Click button Allow All.');
            await this.btnMoreMenus.click();
            { timeout: 5000 };
            await expect(this.secMoreMenus).toBeVisible();

        } catch (e) {
            await this.logger('clicked on button More Menus.');
        }
    }

    async MenusExist() {
        // await waitForElem(this.mDashboard, 'Menu Dashboard', this.logger);
        await elemVisible(this.mClients, 'menu Clients', this.logger);
        await elemVisible(this.mActionItems, 'menu Action Items', this.logger);
        await elemVisible(this.mModels, 'menu Models', this.logger);
        await elemVisible(this.mInvestments, 'menu Investments', this.logger);
        await elemVisible(this.mProductsServices, 'menu Products & Services', this.logger);
        await elemVisible(this.mHelpSupport, 'menu Help & Support', this.logger);
        await elemVisible(this.btnProfile, 'button Profile', this.logger);
    }

    async SectionSiteCoreExists() {
        await elemVisible(this.secSiteCore, 'section Sitecore', this.logger, 10000);
        await elemVisible(this.secFooter, 'section Footer', this.logger);
    }
}
