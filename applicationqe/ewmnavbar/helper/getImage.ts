import { expect, type Locator, type Page, type TestInfo } from "@playwright/test";

export class getImage {

    readonly page: Page;
    readonly testInfo: TestInfo; 

    constructor(page: Page, testInfo: TestInfo) { 
        this.page = page;
        this.testInfo = testInfo; 
    }
    

    async wholePage(fileName: string){
        const screenshotPath = `test-results/${fileName}.png`;
        
        // 1. Save the screenshot
        await this.page.screenshot({path: screenshotPath, fullPage: true});

        // 2. Attach the saved image using the stored this.testInfo, if available
        if (this.testInfo && typeof this.testInfo.attach === 'function') {
            await this.testInfo.attach(fileName + ' (Full Page)', {
                path: screenshotPath,
                contentType: 'image/png',
            });
        }
    }

    async element(locator: string, fileName: string){
        const screenshotPath = `test-results/${fileName}.png`;

        // 1. Save the element screenshot
        await this.page.locator(locator).screenshot({ path: screenshotPath });

        // 2. Attach the saved image using the stored this.testInfo
        await this.testInfo.attach(fileName + ' (Element)', {
            path: screenshotPath,
            contentType: 'image/png',
        });
    }
}