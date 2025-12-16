import { test, expect } from '../../helper/fixtures';

test.describe('Dashboard Pages', () => {

    test('sub-menus - Overview, Insights, Advisor Benefits, Statements & Reports', async ({ page, p, f, log }) => {
        await p.Dashboard.goToPage();
        await p.Dashboard.LoadsPage();
        await p.Home.MenusExist();
        await p.Dashboard.SubMenusExist();
        await p.img.wholePage('Dashboard_L2Menus');
        await log('📊 page Dashbard');
    });

    test('Overview is the Default Page', async ({ page, p, log }) => {
        await p.Dashboard.goToPage();
        await p.Dashboard.LoadsPage();
        await p.Overview.ElementsExist();
        await p.img.wholePage('Overview');
        await log('📊 page Dashbard > Overview');
    });

    test('Insights', async ({ page, p, log }) => {
        await p.Dashboard.goToPage();
        await p.Dashboard.LoadsPage();
        await p.Overview.ElementsExist();
        await p.Dashboard.smInsights.click();
        await p.Insights.LoadsPage();
                await p.img.wholePage('Insights');

        await p.Insights.ElementsExist();
        await p.img.wholePage('Insights');
        await log('📊 page Dashbard > Insights');

    });

    test('Advisor Benefits', async ({ page, p, f, log }) => {
        await p.Dashboard.goToPage();
        await p.Dashboard.smAdvisorBenefits.click();
        await p.AdvisorBenefits.LoadsPage();

        await f.ComparePages.compareNavBarwithLegacy(
            p.AdvisorBenefits.secAdvisorBenefits,
            p.AdvisorBenefits.secLegacySiteCore,
            p.AdvisorBenefits.secSiteCore,
        );
        await p.img.wholePage('Advisor Benefits');
        await log('📊 page Dashbard > Advisor Benefits');
    });

    test('Statements & Reports', async ({ page, p, f, log }) => {
        await p.Dashboard.goToPage();
        await p.Dashboard.smStatementsReports.click();
        await p.StatementsReports.LoadsPage();

        await f.ComparePages.compareNavBarwithLegacy(
            p.StatementsReports.secStatementsReports,
            p.StatementsReports.secLegacySiteCore,
            p.StatementsReports.secSiteCore,
        );
        await p.img.wholePage('StatementsReports');
        await log('📊 page Dashbard > Statements & Reports');
    });

});
