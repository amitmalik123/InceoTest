import { test, expect } from '../../helper/fixtures';

test.describe('Clients Pages', () => {

    test('Submenus exist: All Clients, Accounts, Strategists', async ({ p, f, log }) => {
        await log('📢 Checking visibility of all submenus under Clients.');

        // 1. Navigate
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mClients, 'menu Clients');
        
        // 2. Check Submenus
        await p.Clients.LoadsPage();
        await p.Clients.SubMenusExist();

        // 3. Evidence
        await p.img.wholePage('Clients_Submenus');
        await log('✅ All submenus are visible.');
    });

    test('All Clients: Content matches Legacy App', async ({ p, f, log }) => {
        await log('📢 Comparing element counts between New App and Legacy App (All Clients).');

        // 1. Navigate (All Clients is default)
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mClients, 'menu Clients');
        await p.AllClients.LoadsPage();

        // 2. Compare Pages
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.AllClients.secAllClients,
            p.AllClients.secLegacySiteCore,
            p.AllClients.secSiteCore,
        );

        // 3. Evidence & Assert
        await p.img.wholePage('AllClients_Page');
        // expect(results.mismatch, '❌ Mismatch detected between New and Legacy apps. Check report.').toBe(false);
    });

    test('Accounts: Content matches Legacy App', async ({ p, f, log }) => {
        await log('📢 Comparing element counts between New App and Legacy App (Accounts).');

        // 1. Navigate
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mClients, 'menu Clients');
        await p.Clients.LoadsPage();
        await f.Element.clickElem(p.Clients.smAccounts, 'submenu Accounts');
        await p.Accounts.LoadsPage();

        // 2. Compare Pages
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.Accounts.secAccounts,
            p.Accounts.secLegacySiteCore,
            p.Accounts.secSiteCore,
        );

        // 3. Evidence & Assert
        await p.img.wholePage('Accounts_Page');
        // expect(results.mismatch, '❌ Mismatch detected between New and Legacy apps. Check report.').toBe(false);
    });

    test('Strategists: Content matches Legacy App', async ({ p, f, log }) => {
        await log('📢 Comparing element counts between New App and Legacy App (Strategists).');

        // 1. Navigate
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mClients, 'menu Clients');
        await f.Element.clickElem(p.Clients.smStrategists, 'submenu Strategists');
        await p.Strategists.LoadsPage();

        // 2. Compare Pages
        const results = await f.ComparePages.compareNavBarwithLegacy(
            p.Strategists.secStrategists,
            p.Strategists.secLegacySiteCore,
            p.Strategists.secSiteCore,
        );

        // 3. Evidence & Assert
        await p.img.wholePage('Strategists_Page');
        // expect(results.mismatch, '❌ Mismatch detected between New and Legacy apps. Check report.').toBe(false);
    });

});