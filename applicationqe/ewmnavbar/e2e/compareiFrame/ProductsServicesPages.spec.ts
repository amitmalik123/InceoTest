import { test, expect } from '../../helper/fixtures';

test.describe('Investments Pages', () => {

    test('sub-menus - Strategies, Research, News, Cash, SMA, Guided Portfolios, DAF, Savos, TMS', async ({ p, f, log }) => {
        await log('📢 Checking visibility of all submenus under Investments.');

        // 1. Navigate
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mInvestments, 'menu Investments');
        
        // 2. Check Submenus
        await p.Investments.LoadsPage();
        await f.Browser.sizeDesktop();
        await p.Investments.SubMenusExist();
        
        // 3. Evidence
        await p.img.wholePage('Investments_L2Menus');
        await log('✅ All submenus are visible.');
    });

    test('Strategies is the Default Page', async ({ p, f, log }) => {
        await log('📢 Comparing element counts between New App and Legacy App (Strategies).');

        // 1. Navigate
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mInvestments, 'menu Investments');
        await f.Element.clickElem(p.Investments.smStrategies, 'submenu Strategies');
        await p.Strategies.LoadsPage();
        
        // 2. Compare Pages
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.Strategies.secStrategies,
            p.Strategies.secLegacySiteCore,
            p.Strategies.secSiteCore,
        );
        
        // 3. Evidence
        await p.img.wholePage('Strategies');
        await log('✅ Content verification complete for Strategies.');
        
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('Research', async ({ p, f, log }) => {
        await log('📢 Comparing element counts between New App and Legacy App (Research).');

        // 1. Navigate
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mInvestments, 'menu Investments');
        await f.Element.clickElem(p.Investments.smResearch, 'submenu Research');
        await p.Research.LoadsPage();
        
        // 2. Compare Pages
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.Research.secResearch,
            p.Research.secLegacySiteCore,
            p.Research.secSiteCore,
        );
        
        // 3. Evidence
        await p.img.wholePage('Research');
        await log('✅ Content verification complete for Research.');
        
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('News', async ({ p, f, log }) => {
        await log('📢 Comparing element counts between New App and Legacy App (News).');

        // 1. Navigate
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mInvestments, 'menu Investments');
        await f.Element.clickElem(p.Investments.smNews, 'submenu News');
        await p.News.LoadsPage();
        
        // 2. Compare Pages
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.News.secNews,
            p.News.secLegacySiteCore,
            p.News.secSiteCore,
        );
        
        // 3. Evidence
        await p.img.wholePage('News');
        await log('✅ Content verification complete for News.');
        
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('Cash', async ({ p, f, log }) => {
        await log('📢 Comparing element counts between New App and Legacy App (Cash).');

        // 1. Navigate
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mInvestments, 'menu Investments');
        await f.Element.clickElem(p.Investments.smCash, 'submenu Cash');
        await p.Cash.LoadsPage();
        
        // 2. Compare Pages
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.Cash.secCash,
            p.Cash.secLegacySiteCore,
            p.Cash.secSiteCore,
        );
        
        // 3. Evidence
        await p.img.wholePage('Cash');
        await log('✅ Content verification complete for Cash.');
        
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('SMA', async ({ p, f, log }) => {
        await log('📢 Comparing element counts between New App and Legacy App (SMA).');

        // 1. Navigate
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mInvestments, 'menu Investments');
        await f.Element.clickElem(p.Investments.smSMA, 'submenu SMA');
        await p.SMA.LoadsPage();
        
        // 2. Compare Pages
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.SMA.secSMA,
            p.SMA.secLegacySiteCore,
            p.SMA.secSiteCore,
        );
        
        // 3. Evidence
        await p.img.wholePage('SMA');
        await log('✅ Content verification complete for SMA.');
        
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('Guided Portfolios', async ({ p, f, log }) => {
        await log('📢 Comparing element counts between New App and Legacy App (Guided Portfolios).');

        // 1. Navigate
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mInvestments, 'menu Investments');
        await f.Element.clickElem(p.Investments.smGuidedPortfolios, 'submenu Guided Portfolios');
        await p.GuidedPortfolios.LoadsPage();
        
        // 2. Compare Pages
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.GuidedPortfolios.secGuidedPortfolios,
            p.GuidedPortfolios.secLegacySiteCore,
            p.GuidedPortfolios.secSiteCore,
        );
        
        // 3. Evidence
        await p.img.wholePage('GuidedPortfolios');
        await log('✅ Content verification complete for Guided Portfolios.');
        
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('DAF', async ({ p, f, log }) => {
        await log('📢 Comparing element counts between New App and Legacy App (DAF).');

        // 1. Navigate
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mInvestments, 'menu Investments');
        await f.Element.clickElem(p.Investments.smDAF, 'submenu DAF');
        await p.DAF.LoadsPage();
        
        // 2. Compare Pages
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.DAF.secDAF,
            p.DAF.secLegacySiteCore,
            p.DAF.secSiteCore,
        );
        
        // 3. Evidence
        await p.img.wholePage('DAF');
        await log('✅ Content verification complete for DAF.');
        
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('Savos', async ({ p, f, log }) => {
        await log('📢 Comparing element counts between New App and Legacy App (Savos).');

        // 1. Navigate
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mInvestments, 'menu Investments');
        await f.Element.clickElem(p.Investments.smSavos, 'submenu Savos');
        await p.Savos.LoadsPage();
        
        // 2. Compare Pages
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.Savos.secSavos,
            p.Savos.secLegacySiteCore,
            p.Savos.secSiteCore,
        );
        
        // 3. Evidence
        await p.img.wholePage('Savos');
        await log('✅ Content verification complete for Savos.');
        
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('TMS', async ({ p, f, log }) => {
        await log('📢 Comparing element counts between New App and Legacy App (TMS).');

        // 1. Navigate
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mInvestments, 'menu Investments');
        await f.Element.clickElem(p.Investments.smTMS, 'submenu TMS');
        await p.TMS.LoadsPage();
        
        // 2. Compare Pages
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.TMS.secTMS,
            p.TMS.secLegacySiteCore,
            p.TMS.secSiteCore,
        );
        
        // 3. Evidence
        await p.img.wholePage('TMS');
        await log('✅ Content verification complete for TMS.');
        
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

});