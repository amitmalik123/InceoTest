import { test, expect } from '../../helper/fixtures';

test.describe('Modals Page', () => {

    test('Only Page', async ({ p, f, log }) => {
        await p.Models.goToPage();
        await p.Models.LoadsPage();
        await p.Models.ElementsExist();
        await p.img.wholePage('Models');
        await log('📊 page Models');
    });


});
