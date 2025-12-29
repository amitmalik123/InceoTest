import { test, expect } from '../../helper/fixtures';

test.describe('Investments Pages', () => {

    test('sub-menus - Strategies, Research, News, Cash, SMA, Guided Portfolios, DAF, Savos, TMS', async ({ page, p, f, log }) => {
        await p.Investments.goToPage();
        await p.Investments.LoadsPage();
        await f.Browser.winSizeDesktop();
        await p.Investments.SubMenusExist();
        await p.img.wholePage('Investments_L2Menus');
        await log('📈 page Investments');
    });

    test('Strategies is the Default Page', async ({ page, p, f, log }) => {
        await p.Investments.goToPage();
        await p.Strategies.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.Strategies.secStrategies,
            p.Strategies.secLegacySiteCore,
            p.Strategies.secSiteCore,
        );
        await p.img.wholePage('Strategies');
        await log('📊 page Investments > Strategies');
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('Research', async ({ page, p, f, log }) => {
        await p.Investments.goToPage();
        await p.Investments.smResearch.click();
        await p.Research.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.Research.secResearch,
            p.Research.secLegacySiteCore,
            p.Research.secSiteCore,
        );
        await p.img.wholePage('Research');
        await log('📊 page Investments > Research');
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });


    test('News', async ({ page, p, f, log }) => {
        await p.Investments.goToPage();
        await p.Investments.smNews.click();
        await p.News.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.News.secNews,
            p.News.secLegacySiteCore,
            p.News.secSiteCore,
        );
        await p.img.wholePage('News');
        await log('📊 page Investments > News');
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('Cash', async ({ page, p, f, log }) => {
        await p.Investments.goToPage();
        await p.Investments.smCash.click();
        await p.Cash.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.Cash.secCash,
            p.Cash.secLegacySiteCore,
            p.Cash.secSiteCore,
        );
        await p.img.wholePage('Cash');
        await log('📊 page Investments > Cash');
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('SMA', async ({ page, p, f, log }) => {
        await p.Investments.goToPage();
        await p.Investments.smSMA.click();
        await p.SMA.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.SMA.secSMA,
            p.SMA.secLegacySiteCore,
            p.SMA.secSiteCore,
        );
        await p.img.wholePage('SMA');
        await log('📊 page Investments > SMA');
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('Guided Portfolios', async ({ page, p, f, log }) => {
        await p.Investments.goToPage();
        await p.Investments.smGuidedPortfolios.click();
        await p.GuidedPortfolios.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.GuidedPortfolios.secGuidedPortfolios,
            p.GuidedPortfolios.secLegacySiteCore,
            p.GuidedPortfolios.secSiteCore,
        );
        await p.img.wholePage('GuidedPortfolios');
        await log('📊 page Investments > Guided Portfolios');
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('DAF', async ({ page, p, f, log }) => {
        await p.Investments.goToPage();
        await p.Investments.smDAF.click();
        await p.DAF.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.DAF.secDAF,
            p.DAF.secLegacySiteCore,
            p.DAF.secSiteCore,
        );
        await p.img.wholePage('DAF');
        await log('📊 page Investments > DAF');
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('Savos', async ({ page, p, f, log }) => {
        await p.Investments.goToPage();
        await p.Investments.smSavos.click();
        await p.Savos.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.Savos.secSavos,
            p.Savos.secLegacySiteCore,
            p.Savos.secSiteCore,
        );
        await p.img.wholePage('Savos');
        await log('📊 page Investments > Savos');
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('TMS', async ({ page, p, f, log }) => {
        await p.Investments.goToPage();
        await p.Investments.smTMS.click();
        await p.TMS.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.TMS.secTMS,
            p.TMS.secLegacySiteCore,
            p.TMS.secSiteCore,
        );
        await p.img.wholePage('TMS');
        await log('📊 page Investments > TMS');
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

});
