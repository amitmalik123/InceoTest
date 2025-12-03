import { Locator } from "playwright";


export async function checkIfUnchecked(checkboxToSelect: Locator) {
    if(!await checkboxToSelect.isChecked()) {
        await checkboxToSelect.setChecked(true);
        return;
    }
    return;
}