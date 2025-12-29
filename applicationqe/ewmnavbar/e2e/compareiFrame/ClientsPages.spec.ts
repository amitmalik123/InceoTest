import { test, expect } from '../../helper/fixtures';

test.describe('Clients Pages', () => {

    test('sub-menus - All Clients, Accounts, Strategists', async ({ page, p, f, log }) => {
        await p.Clients.goToPage();
        await p.Clients.LoadsPage();
        await p.Clients.SubMenusExist();
        await p.img.wholePage('Clients_L2Menus');
        await log('📈 page Clients');
    });

    test('All Clients is the Default Page', async ({ page, p, f, log }) => {
        await p.Clients.goToPage();
        await p.AllClients.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.AllClients.secAllClients,
            p.AllClients.secLegacySiteCore,
            p.AllClients.secSiteCore,
        );
        await p.img.wholePage('AllClients');
        await log('📊 page Clients > All Clients');
        // expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('Accounts', async ({ page, p, f, log }) => {
        await p.Clients.goToPage();
        await p.Clients.smAccounts.click();
        await p.Accounts.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.Accounts.secAccounts,
            p.Accounts.secLegacySiteCore,
            p.Accounts.secSiteCore,
        );
        await p.img.wholePage('Accounts');
        await log('📊 page Clients > Accounts');
        // expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });

    test('Strategists', async ({ page, p, f, log }) => {
        await p.Clients.goToPage();
        await p.Clients.smStrategists.click();
        await p.Strategists.LoadsPage();
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.Strategists.secStrategists,
            p.Strategists.secLegacySiteCore,
            p.Strategists.secSiteCore,
        );
        await p.img.wholePage('Strategists');
        await log('📊 page Clients > Strategists');
        // expect(results.mismatch, 'Content counts mismatched. View logger messages to know where it failed.').toBe(false);
    });



});
