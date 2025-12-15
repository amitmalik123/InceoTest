
import { test, expect } from '../../helper/fixtures';
import { fileURLToPath } from 'url';
import * as path from 'path';
import * as fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const usersFilePath = path.join(__dirname, '..', '..', 'data', 'rbac2.json');

if (!fs.existsSync(usersFilePath)) {
    throw new Error(`User data file not found at: ${usersFilePath}`);
}

const usersMap: { [key: string]: { userId: string } } =
    JSON.parse(fs.readFileSync(usersFilePath, 'utf-8'));


const userIds: string[] = Object.values(usersMap).map(user => user.userId);

const password = process.env.PASSWORD;

if (userIds.length === 0) {
    throw new Error("User data from 'securityRoles.json' is gone.");
}
if (!password) {
    throw new Error("PASSWORD environment variable is gone.");
}


test.describe.skip('EWM L1 > L2 User Loop', () => {

    userIds.forEach((userId) => {

        test(`Home page => Menus - and submenus for user - ${userId}`, async ({ page, p, f, log }) => {

            await log(`Attempting login for user: ${userId}`);
            await page.goto(process.env.URL);
            await p.Login.Login(userId, password);
            await p.img.wholePage('Login Page');
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


});
