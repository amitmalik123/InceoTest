import { test, expect } from '../../helper/fixtures';

test.describe('Models Page', () => {

    test('Only Page', async ({ p, f, log }) => {
        await log('📢 Go to menu Models. Page exists. That is all');
        await p.Home.goToHomePage();
        await f.Element.clickElem(p.Home.mModels, 'menu Models');
        await p.Models.LoadsPage();
        await p.Models.ElementsExist();
        await p.img.wholePage('Models');
        await log('📊 page Models');
    });


});
