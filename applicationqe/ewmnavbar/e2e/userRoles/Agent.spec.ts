import { test, expect } from '../../helper/fixtures';

test.describe('Agent', () => {

    test('Can see all the menus and Sub menus', async ({ page, p, f, log }) => {
        await page.goto(process.env.URL);
        await p.Login.Login(process.env.AGENT_LIFESPAN_INC_ID, process.env.PASSWORD, log)

        await p.Dashboard.LoadsPage();
        await p.Home.MenusExist();
        await p.img.wholePage('HomePage_L1Menu');
        await log('🏠 Home Page: Main menus verified');

        await p.Dashboard.LoadsPage();
        await p.Dashboard.SubMenusExist();
        await p.img.wholePage('Dashboard_L2Menus');
        await log('📊 Dashboard: All submenus are visible');

        await f.clickLink(p.Home.mClients, 'menu Clients', log);
        await p.Clients.LoadsPage();
        await p.Clients.SubMenusExist();
        await p.img.wholePage('Clients_L2Menus');
        await log('👥 Clients: All submenus are visible'); 

        await f.clickLink(p.Home.mActionItems, 'menu Action Items', log);
        await p.ActionItems.LoadsPage();
        await p.ActionItems.SubMenusExist();
        await p.img.wholePage('ActionItems_L2Menus');
        await log('💫 Action Items: All submenus are visible');

        await f.clickLink(p.Home.mModels, 'menu Models', log);
        await p.Models.LoadsPage();
        await p.img.wholePage('Models_L2Menus');
        await log('🧩 Models: Has no Submenus');

        await f.clickLink(p.Home.mInvestments, 'menu Investments', log);
        await p.Investments.LoadsPage();
        await f.Browser.winSizeDesktop();
        await p.Investments.SubMenusExist();
        await p.img.wholePage('Investments_L2Menus');
        await log('📈 Investments: All submenus are visible');

        await f.clickLink(p.Home.mProductsServices, 'menu Products and Services', log);
        await p.ProductsServices.LoadsPage();
        await p.ProductsServices.SubMenusExist();
        await p.img.wholePage('ProductsServices_L2Menus');
        await log('📦 Products & Services: All submenus are visible');

        await f.clickLink(p.Home.mHelpSupport, 'menu Help and Support', log);
        await p.HelpSupport.LoadsPage();
        await p.HelpSupport.SubMenusExist();
        await p.img.wholePage('HelpSupport_L2Menus');
        await log('🛟 Help & Support: All submenus are visible'); 
    });


});
