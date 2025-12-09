import { test, expect } from '../../helper/fixtures';

test.describe('Help & Support Pages', () => {

    test('sub-menus - Knowledge Base, Contact Us, Tax Resources, Fees, Glossary, Custodial Services, Compliance Resources, Marketing Resources, Events, RMD Resources', async ({ p, f, log }) => {
        await p.HelpSupport.goToPage();
        await p.HelpSupport.LoadsPage();
        await f.Browser.winSizeDesktop();
        await p.HelpSupport.SubMenusExist();
        await p.img.wholePage('HelpSupport_L2Menus');
        await log('📈 page Help & Support');
    });

    test('Knowledge Base is the Default Page', async ({ p, f, log }) => {
        await p.HelpSupport.goToPage();
        await p.KnowledgeBase.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.KnowledgeBase.secKnowledgeBase,
            p.KnowledgeBase.secLegacySiteCore,
            p.KnowledgeBase.secSiteCore,
        );
        await p.img.wholePage('Knowledge Base');
        await log('📊 page Help & Support > Knowledge Base');
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('Contact Us', async ({ p, f, log }) => {
        await p.HelpSupport.goToPage();
        await p.HelpSupport.smContactUs.click();
        await p.ContactUs.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.ContactUs.secContactUs,
            p.ContactUs.secLegacySiteCore,
            p.ContactUs.secSiteCore,
        );
        await p.img.wholePage('ContactUs');
        await log('📊 page Help & Support > Contact Us');
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('Tax Resources', async ({ p, f, log }) => {
        await p.HelpSupport.goToPage();
        await p.HelpSupport.smTaxResources.click();
        await p.TaxResources.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.TaxResources.secTaxResources,
            p.TaxResources.secLegacySiteCore,
            p.TaxResources.secSiteCore,
        );
        await p.img.wholePage('TaxResources');
        await log('📊 page Help & Support > Tax Resources');
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('Fees', async ({ p, f, log }) => {
        await p.HelpSupport.goToPage();
        await p.HelpSupport.smFees.click();
        await p.Fees.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.Fees.secFees,
            p.Fees.secLegacySiteCore,
            p.Fees.secSiteCore,
        );
        await p.img.wholePage('Fees');
        await log('📊 page Help & Support > Fees');
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('Glossary', async ({ p, f, log }) => {
        await p.HelpSupport.goToPage();
        await p.HelpSupport.smGlossary.click();
        await p.Glossary.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.Glossary.secGlossary,
            p.Glossary.secLegacySiteCore,
            p.Glossary.secSiteCore,
        );
        await p.img.wholePage('Glossary');
        await log('📊 page Help & Support > Glossary');
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('Custodial Services', async ({ p, f, log }) => {
        await p.HelpSupport.goToPage();
        await p.HelpSupport.smCustodialServices.click();
        await p.CustodialServices.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.CustodialServices.secCustodialServices,
            p.CustodialServices.secLegacySiteCore,
            p.CustodialServices.secSiteCore,
        );
        await p.img.wholePage('CustodialServices');
        await log('📊 page Help & Support > Custodial Services');
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

     test('Compliance Resources', async ({p, f, log }) => {
        await p.HelpSupport.goToPage();
        await p.HelpSupport.smComplianceResources.click();
        await p.ComplianceResources.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.ComplianceResources.secComplianceResources,
            p.ComplianceResources.secLegacySiteCore,
            p.ComplianceResources.secSiteCore,
        );
        await p.img.wholePage('ComplianceResources');
        await log('📊 page Help & Support > Compliance Resources');
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

     test('Marketing Resources', async ({p, f, log }) => {
        await p.HelpSupport.goToPage();
        await p.HelpSupport.smMarketingResources.click();
        await p.MarketingResources.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.MarketingResources.secMarketingResources,
            p.MarketingResources.secLegacySiteCore,
            p.MarketingResources.secSiteCore,
        );
        await p.img.wholePage('MarketingResources');
        await log('📊 page Help & Support > Marketing Resources');
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('Events', async ({ p, f, log }) => {
        await p.HelpSupport.goToPage();
        await f.Browser.winSizeDesktop();
        await p.HelpSupport.smEvents.click();
        await p.Events.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.Events.secEvents,
            p.Events.secLegacySiteCore,
            p.Events.secSiteCore,
        );
        await p.img.wholePage('Events');
        await log('📊 page Help & Support > Events');
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

     test('RMD Resources', async ({p, f, log }) => {
        await p.HelpSupport.goToPage();
        await f.Browser.winSizeDesktop();
        await p.HelpSupport.smRMDResources.click();
        await p.RMDResources.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.RMDResources.secRMDResources,
            p.RMDResources.secLegacySiteCore,
            p.RMDResources.secSiteCore,
        );
        await p.img.wholePage('RMDResources');
        await log('📊 page Help & Support > RMD Resources');
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

});
