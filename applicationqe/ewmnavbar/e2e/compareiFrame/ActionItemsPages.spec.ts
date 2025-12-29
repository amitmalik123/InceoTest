import { test, expect } from '../../helper/fixtures';

test.describe('Action Items Pages', () => {

    test('sub-menus - Needs Action, Open Items, Closed', async ({ p, f, log }) => {
        await log('This test verifies the sub-menus under Action Items which are Needs Action, Open Items and Closed exist');
        await p.ActionItems.goToPage();
        await p.ActionItems.LoadsPage();
        await p.ActionItems.SubMenusExist();
        await p.img.wholePage('ActionItems_L2Menus');
        await log('📈 page Action Items');
    });

    test('Needs Action is the Default Page', async ({ p, f, log, testInfo }) => {
        await p.ActionItems.goToPage();
        await p.NeedsAction.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.NeedsAction.secNeedsAction,
            p.NeedsAction.secLegacySiteCore,
            p.NeedsAction.secSiteCore
        );

        if (results.legacyUrl) {
            const legacyPage = await p.ActionItems.page.context().newPage();
            await legacyPage.goto(results.legacyUrl, { waitUntil: 'domcontentloaded' });
            try {
                await legacyPage.waitForSelector('#main, .main-content, .content, body', { state: 'visible', timeout: 15000 });
            } catch { }
            await legacyPage.waitForTimeout(1500);
            const screenshot = await legacyPage.screenshot({ fullPage: true });
            await testInfo.attach('LegacyAppScreenshot', { body: screenshot, contentType: 'image/png' });
            await legacyPage.close();
        }

        await p.img.wholePage('NeedsAction');
        await log('📊 page ActionItems > Needs Action');
        expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('Needs Action - Bubble Count vs Table Count matches', async ({ p, f, log, testInfo }) => {
        await p.ActionItems.goToPage();
        await p.NeedsAction.LoadsPage();

        const BubbleCount = await p.ActionItems.getItemsCount();
        const TableCount = await p.NeedsAction.getItemsCount();
        await log('Bubble Count = ' + BubbleCount);
        await log('Table Count = ' + TableCount);
        expect(BubbleCount, 'Bubble count matches Row count').toEqual(TableCount);
        await p.img.wholePage('NeedsAction_Bubble');
        await log('📊 page ActionItems > Needs Action > Bubble count matches the row count');
        // expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('Open Items', async ({ p, f, log, testInfo }) => {
        await p.ActionItems.goToPage();
        await p.ActionItems.smOpenItems.click();
        await p.OpenItems.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.OpenItems.secOpenItems,
            p.OpenItems.secLegacySiteCore,
            p.OpenItems.secSiteCore
        );

        if (results.legacyUrl) {
            const legacyPage = await p.ActionItems.page.context().newPage();
            await legacyPage.goto(results.legacyUrl, { waitUntil: 'domcontentloaded' });
            try {
                await legacyPage.waitForSelector('#main, .main-content, .content, body', { state: 'visible', timeout: 15000 });
            } catch { }
            await legacyPage.waitForTimeout(1500);
            const screenshot = await legacyPage.screenshot({ fullPage: true });
            await testInfo.attach('LegacyAppScreenshot', { body: screenshot, contentType: 'image/png' });
            await legacyPage.close();
        }
        await p.img.wholePage('Open Items');
        await log('📊 page ActionItems > Open Items');
        // expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('Closed', async ({ p, f, log, testInfo }) => {
        await p.ActionItems.goToPage();
        await p.ActionItems.smClosed.click();
        await p.Closed.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.Closed.secClosed,
            p.Closed.secLegacySiteCore,
            p.Closed.secSiteCore
        );

        if (results.legacyUrl) {
            const legacyPage = await p.ActionItems.page.context().newPage();
            await legacyPage.goto(results.legacyUrl, { waitUntil: 'domcontentloaded' });
            try {
                await legacyPage.waitForSelector('#main, .main-content, .content, body', { state: 'visible', timeout: 15000 });
            } catch { }
            await legacyPage.waitForTimeout(1500);
            const screenshot = await legacyPage.screenshot({ fullPage: true });
            await testInfo.attach('LegacyAppScreenshot', { body: screenshot, contentType: 'image/png' });
            await legacyPage.close();
        }
        await p.img.wholePage('Closed');
        await log('📊 page ActionItems > Closed');
        // expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });


});
