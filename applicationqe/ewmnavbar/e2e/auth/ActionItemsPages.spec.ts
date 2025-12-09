

import { test, expect } from '../../helper/fixtures';

test.describe('Models Pages', () => {

    test('sub-menus - All ActionItems, Accounts, Strategists', async ({ p, f, log }) => {
        await p.ActionItems.goToPage();
        await p.ActionItems.LoadsPage();
        await p.ActionItems.SubMenusExist();
        await p.img.wholePage('ActionItems_L2Menus');
        await log('📈 page ActionItems');
    });

    test('Needs Action is the Default Page', async ({ p, f, log }) => {
        await p.ActionItems.goToPage();
        await p.ActionItems.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.NeedsAction.secNeedsAction,
            p.NeedsAction.secLegacySiteCore,
            p.NeedsAction.secSiteCore,
        );
    
        const BubbleCount = await p.ActionItems.getItemsCount();
        const TableCount = await p.NeedsAction.getItemsCount();
        await log('Bubble Count = ' + BubbleCount);
        await log('Table Count = ' + TableCount);
         expect(BubbleCount, 'Bubble count matches Row count').toEqual(TableCount);
        await p.img.wholePage('Needs Action');
        await log('📊 page ActionItems > Needs Action');
        // expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('Open Items', async ({ p, f, log }) => {
        await p.ActionItems.goToPage();
        await p.ActionItems.smOpenItems.click();
        await p.ActionItems.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.OpenItems.secOpenItems,
            p.OpenItems.secLegacySiteCore,
            p.OpenItems.secSiteCore,
        );
        await p.img.wholePage('Open Items');
        await log('📊 page ActionItems > Open Items');
        // expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

   test('Closed', async ({ p, f, log }) => {
        await p.ActionItems.goToPage();
        await p.ActionItems.smClosed.click();
        await p.ActionItems.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.Closed.secClosed,
            p.Closed.secLegacySiteCore,
            p.Closed.secSiteCore,
        );
        await p.img.wholePage('Closed');
        await log('📊 page ActionItems > Closed');
        // expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });


});
