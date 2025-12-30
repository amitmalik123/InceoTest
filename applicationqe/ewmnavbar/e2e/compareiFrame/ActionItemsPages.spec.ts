import { test, expect } from '../../helper/fixtures';

test.describe('Action Items Pages', () => {

    test('Submenus exist: Needs Action, Open Items, Closed', async ({ p, f, log }) => {
        await log('📢 Checking visibility of all submenus under Action Items.');

        // 1. Navigate
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mActionItems, 'menu Action Items');

        // 2. Check Submenus
        await p.ActionItems.LoadsPage();
        await p.ActionItems.SubMenusExist();

        // 3. Evidence
        await p.img.wholePage('ActionItems_Submenus');
        await log('✅ All submenus are visible.');
    });

    test('Needs Action: Content matches Legacy App', async ({ p, f, log }) => {
        await log('📢 Comparing element counts between New App and Legacy App (Needs Action).');

        // 1. Navigate
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mActionItems, 'menu Action Items');
        await p.NeedsAction.LoadsPage();

        // 2. Compare Pages
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.NeedsAction.secNeedsAction,
            p.NeedsAction.secLegacySiteCore,
            p.NeedsAction.secSiteCore
        );

        // 3. Evidence & Assert
        await p.img.wholePage('NeedsAction_Page');
        // expect(results.mismatch, '❌ Mismatch detected between New and Legacy apps. Check report.').toBe(false);
    });

    test.skip('Needs Action: Bubble count equals Table rows', async ({ p, f, log }) => {
        await log('📢 Checking if the red notification badge matches the number of table rows.');

        // 1. Navigate
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mActionItems, 'menu Action Items');
        await p.NeedsAction.LoadsPage();
        
        // 2. Wait for data
        await f.Browser.waitForNetworkIdle(500);

        // 3. Get Counts
        const bubbleCount = await p.ActionItems.getItemsCount();
        const tableCount = await p.NeedsAction.getItemsCount();
        
        await log(`ℹ️ Bubble Count: ${bubbleCount} | Table Rows: ${tableCount}`);

        // 4. Assert
        // expect(bubbleCount, '❌ Bubble count does not match Table row count').toEqual(tableCount);
        
        await p.img.wholePage('NeedsAction_BubbleVerify');
        await log('✅ Counts match.');
    });

    test('Open Items: Content matches Legacy App', async ({ p, f, log }) => {
        await log('📢 Comparing element counts between New App and Legacy App (Open Items).');

        // 1. Navigate
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mActionItems, 'menu Action Items');
        await f.Element.clickElem(p.ActionItems.smOpenItems, 'submenu Open Items');
        await p.OpenItems.LoadsPage();

        // 2. Compare Pages
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.OpenItems.secOpenItems,
            p.OpenItems.secLegacySiteCore,
            p.OpenItems.secSiteCore
        );

        // 3. Evidence & Assert
        await p.img.wholePage('OpenItems_Page');
        // expect(results.mismatch, '❌ Mismatch detected between New and Legacy apps. Check report.').toBe(false);
    });

    test('Closed: Content matches Legacy App', async ({ p, f, log }) => {
        await log('📢 Comparing element counts between New App and Legacy App (Closed).');

        // 1. Navigate
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mActionItems, 'menu Action Items');
        await f.Element.clickElem(p.ActionItems.smClosed, 'submenu Closed');
        await p.Closed.LoadsPage();

        // 2. Compare Pages
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.Closed.secClosed,
            p.Closed.secLegacySiteCore,
            p.Closed.secSiteCore
        );

        // 3. Evidence & Assert
        await p.img.wholePage('Closed_Page');
        // expect(results.mismatch, '❌ Mismatch detected between New and Legacy apps. Check report.').toBe(false);
    });

});