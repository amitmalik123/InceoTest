import { test, expect } from '../../helper/fixtures';

test.describe('Agent', () => {

    test('Can see all the menus and Sub menus', async ({ page, p, f, log }) => {
        await page.goto(process.env.URL);
        await p.Login.Login(process.env.AGENT_LIFESPAN_INC_ID, process.env.PASSWORD)

         await p.Dashboard.LoadsPage();
        await p.Home.MenusExist();
        await p.img.wholePage('HomePage_L1Menu');
        await log('🏠 Home page Main Menus');

        await p.Dashboard.LoadsPage();
        await p.Dashboard.SubMenusExist();
        await p.img.wholePage('Dashboard_L2Menus');
        await log('📊 page Dashbard');

        await p.Home.mClients.click();
        await p.Clients.LoadsPage();
        await p.Clients.SubMenusExist();
        await p.img.wholePage('Clients_L2Menus');
        await log('📝 page Clients');

        await p.Home.mActionItems.click();
        await p.ActionItems.LoadsPage();
        await p.ActionItems.SubMenusExist();
        await p.img.wholePage('ActionItems_L2Menus');
        await log('📝 page Action Items');

        await p.Home.mModels.click();
        await p.Models.LoadsPage();
        await p.img.wholePage('Models_L2Menus');
        await log('📄 page Models');


        await p.Home.mInvestments.click();
        await p.Investments.LoadsPage();
        await f.Browser.winSizeDesktop();
        await p.Investments.SubMenusExist();
        await p.img.wholePage('Investments_L2Menus');
        await log('📈 page Investments');

        await p.Home.mProductsServices.click();
        await p.ProductsServices.LoadsPage();
        await p.ProductsServices.SubMenusExist();
        await p.img.wholePage('Models_L2Menus');
        await log('📦 page Products and Services');

        await p.Home.mHelpSupport.click();
        await p.HelpSupport.LoadsPage();
        await p.HelpSupport.SubMenusExist();
        await p.img.wholePage('HelpSupport_L2Menus');
        await log('🦮 page Help and Support');

    });


});
