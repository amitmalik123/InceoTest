import { test, expect } from '../../helper/fixtures';

test.describe('Office Admin', () => {

    test('Global Menu Verification', async ({ page, p, f, log }) => {
        await log('🚀 Starting Test: Office Admin Global Menu Verification');

        // --- STEP 1: LOGIN ---
        await test.step('🔐 Login to Application', async () => {
            await log('👉 Step 1: Login');
            await f.Browser.goToURL(process.env.URL);
        await p.Login.Login(process.env.OFFICE_ADMIN_THOMSON_ID, process.env.PASSWORD);
        });

        // --- STEP 2: DASHBOARD ---
        await test.step('🏠 Verify Home & Dashboard', async () => {
            await log('👉 Step 2: Verify Home & Dashboard Menus');
            await p.Dashboard.LoadsPage();
            
            await p.Home.MenusExist();
            await p.img.wholePage('HomePage_L1Menu');

            await p.Dashboard.LoadsPage();
            await p.Dashboard.SubMenusExist();
            await p.img.wholePage('Dashboard_L2Menus');
            await log('✅ Dashboard verified');
        });

        // --- STEP 3: CLIENTS ---
        await test.step('👥 Verify Clients Menu', async () => {
            await log('👉 Step 3: Verify Clients Menu');
            await f.Element.clickElem(p.Home.mClients, 'menu Clients');
            
            await p.Clients.LoadsPage();
            await p.Clients.SubMenusExist();
            await p.img.wholePage('Clients_L2Menus');
            await log('✅ Clients verified');
        });

        // --- STEP 4: ACTION ITEMS ---
        await test.step('💫 Verify Action Items Menu', async () => {
            await log('👉 Step 4: Verify Action Items Menu');
            await f.Element.clickElem(p.Home.mActionItems, 'menu Action Items');
            
            await p.ActionItems.LoadsPage();
            await p.ActionItems.SubMenusExist();
            await p.img.wholePage('ActionItems_L2Menus');
            await log('✅ Action Items verified');
        });

        // --- STEP 5: MODELS ---
        await test.step('🧩 Verify Models Menu', async () => {
            await log('👉 Step 5: Verify Models Menu');
            await f.Element.clickElem(p.Home.mModels, 'menu Models');
            
            await p.Models.LoadsPage();
            await p.img.wholePage('Models_L2Menus');
            await log('✅ Models verified');
        });

        // --- STEP 6: INVESTMENTS ---
        await test.step('📈 Verify Investments Menu', async () => {
            await log('👉 Step 6: Verify Investments Menu');
            await f.Element.clickElem(p.Home.mInvestments, 'menu Investments');
            
            await p.Investments.LoadsPage();
            await f.Browser.sizeDesktop(); 
            
            await p.Investments.SubMenusExist();
            await p.img.wholePage('Investments_L2Menus');
            await log('✅ Investments verified');
        });

        // --- STEP 7: PRODUCTS & SERVICES ---
        await test.step('📦 Verify Products & Services Menu', async () => {
            await log('👉 Step 7: Verify Products & Services Menu');
            await f.Element.clickElem(p.Home.mProductsServices, 'menu Products and Services');
            
            await p.ProductsServices.LoadsPage();
            await p.ProductsServices.SubMenusExist();
            await p.img.wholePage('ProductsServices_L2Menus');
            await log('✅ Products & Services verified');
        });

        // --- STEP 8: HELP & SUPPORT ---
        await test.step('🛟 Verify Help & Support Menu', async () => {
            await log('👉 Step 8: Verify Help & Support Menu');
            await f.Element.clickElem(p.Home.mHelpSupport, 'menu Help and Support');
            
            await p.HelpSupport.LoadsPage();
            await p.HelpSupport.SubMenusExist();
            await p.img.wholePage('HelpSupport_L2Menus');
            await log('✅ Help & Support verified');
        });

        await log('🏁 Test Complete: All Office Admin menus verified successfully.');
    });

});