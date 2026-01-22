import { Locator } from 'playwright';

export async function selectIfVisible(thingToSelect: Locator) {
    if (await thingToSelect.isVisible()) {
        await thingToSelect.click();
        return;
    }
    return;
}
