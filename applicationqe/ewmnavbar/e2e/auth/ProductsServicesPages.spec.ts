import { test, expect } from '../../helper/fixtures';

test.describe('Products & Services Pages', () => {

    test('sub-menus - Business Consulting, Lending, Financial Planning, Retirement Services', async ({ page, p, f, log }) => {
        await p.ProductsServices.goToPage();
        await p.ProductsServices.LoadsPage();
        await p.ProductsServices.SubMenusExist();
        await p.img.wholePage('ProductsServices_L2Menus');
        await log('📈 page Products & Services');
    });

    test('Business Consulting is the Default Page', async ({ page, p, f, log }) => {
        await p.ProductsServices.goToPage();
        await p.BusinessConsulting.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.BusinessConsulting.secBusinessConsulting,
            p.BusinessConsulting.secLegacySiteCore,
            p.BusinessConsulting.secSiteCore,
        );
        await p.img.wholePage('BusinessConsulting');
        await log('📊 page Investments > Business Consulting');
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('Lending', async ({ page, p, f, log }) => {
        await p.ProductsServices.goToPage();
        await p.ProductsServices.smLending.click();
        await p.Lending.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.Lending.secLending,
            p.Lending.secLegacySiteCore,
            p.Lending.secSiteCore,
        );
        await p.img.wholePage('Lending');
        await log('📊 page Investments > Lending');
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('Financial Planning', async ({ page, p, f, log }) => {
        await p.ProductsServices.goToPage();
        await p.ProductsServices.smFinancialPlanning.click();
        await p.FinancialPlanning.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.FinancialPlanning.secFinancialPlanning,
            p.FinancialPlanning.secLegacySiteCore,
            p.FinancialPlanning.secSiteCore,
        );
        await p.img.wholePage('FinancialPlanning');
        await log('📊 page Investments > Financial Planning');
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('Retirement Services', async ({ page, p, f, log }) => {
        await p.ProductsServices.goToPage();
        await p.ProductsServices.smRetirementServices.click();
        await p.RetirementServices.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.RetirementServices.secRetirementServices,
            p.RetirementServices.secLegacySiteCore,
            p.RetirementServices.secSiteCore,
        );
        await p.img.wholePage('RetirementServices');
        await log('📊 page Investments > Retirement Services');
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

});
