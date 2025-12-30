import { test, expect } from '../../helper/fixtures';

test.describe('Investments Pages', () => {

    test('sub-menus - Strategies, Research, News, Cash, SMA, Guided Portfolios, DAF, Savos, TMS', async ({ p, f, log }) => {
        await log('📢 Checking visibility of all submenus under Strategies.');
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mInvestments, 'menu Investments');
        
        await p.Investments.LoadsPage();
        await f.Browser.sizeDesktop();
        
        await p.Investments.SubMenusExist();
        await p.img.wholePage('Investments_L2Menus');
        await log('📈 page Investments');
    });

    test('Strategies: is the Default Page', async ({ p, f, log }) => {
         await log('📢 Comparing element counts between New App and Legacy App ( Strategies).');
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mInvestments, 'menu Investments');
        await f.Element.clickElem(p.Investments.smStrategies, 'submenu Strategies');
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

    test('Research', async ({ p, f, log }) => {
         await log('📢 Comparing element counts between New App and Legacy App (Research).');
        await p.Home.goToHomePage();
        
        await f.Element.clickElem(p.Home.mInvestments, 'menu Investments');
        await f.Element.clickElem(p.Investments.smResearch, 'submenu Research');
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

    test('News', async ({ p, f, log }) => {
         await log('📢 Comparing element counts between New App and Legacy App (News).');
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mInvestments, 'menu Investments');
        await f.Element.clickElem(p.Investments.smNews, 'submenu News');
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

    test('Cash', async ({ p, f, log }) => {
        await log('📢 Comparing element counts between New App and Legacy App (Cash).');
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mInvestments, 'menu Investments');
        await f.Element.clickElem(p.Investments.smCash, 'submenu Cash');
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

    test('SMA', async ({ p, f, log }) => {
        await log('📢 Comparing element counts between New App and Legacy App (SMA).');
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mInvestments, 'menu Investments');
        await f.Element.clickElem(p.Investments.smSMA, 'submenu SMA');
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

    test('Guided Portfolios', async ({ p, f, log }) => {
        await log('📢 Comparing element counts between New App and Legacy App (Guided Portfolios).');
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mInvestments, 'menu Investments');
        await f.Element.clickElem(p.Investments.smGuidedPortfolios, 'submenu Guided Portfolios');
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

    test('DAF', async ({ p, f, log }) => {
        await log('📢 Comparing element counts between New App and Legacy App (DAF).');
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mInvestments, 'menu Investments');
        await f.Element.clickElem(p.Investments.smDAF, 'submenu DAF');
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

    test('Savos', async ({ p, f, log }) => {
        await log('📢 Comparing element counts between New App and Legacy App (Savos).');
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mInvestments, 'menu Investments');
        await f.Element.clickElem(p.Investments.smSavos, 'submenu Savos');
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

    test('TMS', async ({ p, f, log }) => {
        await log('📢 Comparing element counts between New App and Legacy App (TMS).');
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mInvestments, 'menu Investments');
        await f.Element.clickElem(p.Investments.smTMS, 'submenu TMS');
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