import { Locator } from "playwright";


export async function checkIfUnchecked(checkboxToSelect: Locator) {
            checkboxToSelect.setChecked(true);


        // if(!await page1.locator('.th-wrap.th-Calendar > .th-header > .th-title > .checkbox-container > .clsA').isChecked()) {
        //     await page1.locator('.th-wrap.th-Calendar > .th-header > .th-title > .checkbox-container > .clsA').click();
        // }
    return;
}