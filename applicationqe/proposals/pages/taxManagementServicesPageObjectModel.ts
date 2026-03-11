import { type Page, type Locator } from '@playwright/test';
import path from 'path';
import fs from 'fs';

export class TaxManagementServicesPage {
    readonly page: Page;

    // File Upload
    readonly uploadInput: Locator;
    readonly viewResultsButton: Locator;

    // Tax Rate Inputs
    readonly shortTermRateInput: Locator;
    readonly longTermRateInput: Locator;
    readonly stateRateInput: Locator;

    // File Information Section
    readonly fileNameHeading: Locator;
    readonly fileNameValue: Locator;

    // Estimated Tax Benefits Section
    readonly estimatedTaxBenefitsSection: Locator;

    // Client Account Tax Management Summary Section
    readonly clientAccountTaxSummarySection: Locator;

    // Tax Sensitivity Buttons
    readonly lowSensitivityButton: Locator;
    readonly mediumSensitivityButton: Locator;
    readonly highSensitivityButton: Locator;
    readonly veryHighSensitivityButton: Locator;

    // Download and Continue Buttons
    readonly downloadButton: Locator;
    readonly continueButton: Locator;

    // Proposal Date (dynamic, needs masking)
    readonly proposalDate: Locator;

    constructor(page: Page) {
        this.page = page;

        // File Upload
        this.uploadInput = page.locator('label#upload').locator('..').locator('input[type="file"]');
        this.viewResultsButton = page.locator('#VIEWRESULTS').or(page.locator('#VIEW RESULTS')); // Handle both with and without space

        // Tax Rate Inputs
        this.shortTermRateInput = page.locator('input#ShortTerm');
        this.longTermRateInput = page.locator('input#LongTerm');
        this.stateRateInput = page.locator('input#State');

        // File Information Section
        this.fileNameHeading = page.getByRole('heading', { name: 'File', level: 1 });
        this.fileNameValue = this.fileNameHeading.locator('xpath=following-sibling::p[1]');

        // Estimated Tax Benefits Section
        this.estimatedTaxBenefitsSection = page
            .locator('div')
            .filter({ has: page.getByText('Estimated Tax Benefits', { exact: true }) })
            .first();

        // Client Account Tax Management Summary Section
        this.clientAccountTaxSummarySection = page
            .locator('div')
            .filter({ has: page.getByText(/Client Account Tax Management Summary|Account Summary/i) })
            .first();

        // Tax Sensitivity Buttons
        this.lowSensitivityButton = page.getByLabel('Low');
        this.mediumSensitivityButton = page.getByLabel('Medium');
        this.highSensitivityButton = page.getByLabel('High', { exact: true });
        this.veryHighSensitivityButton = page.getByLabel('Very High');

        // Download and Continue Buttons
        this.downloadButton = page.getByLabel('Download');
        this.continueButton = page.getByLabel('Continue');

        // Proposal Date (dynamic, needs masking)
        this.proposalDate = page.locator('p:has-text("Proposal Date")');
    }

    getEstimatedTaxBenefitsValues(): Locator {
        return this.estimatedTaxBenefitsSection
            .locator('div, span, p, td')
            .filter({ hasText: /^\s*(?:\+\/-)?\$?\d[\d,]*(?:\.\d+)?%?\s*$/ });
    }

    getClientAccountSummaryValues(): Locator {
        return this.clientAccountTaxSummarySection.locator('div:has(>h2)>p');
    }

    async getEstimatedTaxBenefitsTableData(): Promise<Array<{ label: string; values: string[] }>> {
        const rows = this.estimatedTaxBenefitsSection.locator('table tr');
        const rowCount = await rows.count();
        const results: Array<{ label: string; values: string[] }> = [];

        for (let i = 0; i < rowCount; i++) {
            const row = rows.nth(i);
            const cells = row.locator('th, td');
            const cellCount = await cells.count();
            if (cellCount === 0) {
                continue;
            }

            const label = (await cells.nth(0).innerText()).trim();
            const values: string[] = [];

            for (let c = 1; c < cellCount; c++) {
                const value = (await cells.nth(c).innerText()).trim();
                if (value) {
                    values.push(value);
                }
            }

            if (label) {
                results.push({ label, values });
            }
        }

        return results;
    }

    async getClientAccountSummaryData(): Promise<Array<{ label: string; value: string }>> {
        const items = this.clientAccountTaxSummarySection.locator('div:has(>h2)');
        const itemCount = await items.count();
        const results: Array<{ label: string; value: string }> = [];

        for (let i = 0; i < itemCount; i++) {
            const item = items.nth(i);
            const label = (await item.locator('h2').innerText()).trim();
            const value = (await item.locator('p').innerText()).trim();

            if (label && value) {
                results.push({ label, value });
            }
        }

        return results;
    }

    // Methods
    async uploadHoldingsTemplate(fileName: string = 'NEW-REVISED Sample TMS ticker file.csv'): Promise<void> {
        const filePath = path.resolve(__dirname, `../data/${fileName}`);
        await this.uploadInput.setInputFiles(filePath);
        await this.page.waitForLoadState();
        await this.viewResultsButton.click();
    }

    async selectTaxSensitivity(sensitivity: 'Low' | 'Medium' | 'High' | 'Very High'): Promise<void> {
        const button =
            sensitivity === 'Low'
                ? this.lowSensitivityButton
                : sensitivity === 'Medium'
                  ? this.mediumSensitivityButton
                  : sensitivity === 'High'
                    ? this.highSensitivityButton
                    : this.veryHighSensitivityButton;

        await button.click();
        // Wait for UI to update after selection
        await this.page.locator('body').evaluate(() => new Promise(resolve => setTimeout(resolve, 500)));
    }

    getScreenshotMaskLocators(): Locator[] {
        return [
            this.shortTermRateInput,
            this.longTermRateInput,
            this.stateRateInput,
            this.fileNameValue,
            this.proposalDate,
            this.getClientAccountSummaryValues(),
            this.getEstimatedTaxBenefitsValues(),
        ];
    }

    /**
     * Force download the PDF when clicking the download button
     * @returns Path to the downloaded PDF file
     */
    async downloadPdf(): Promise<string> {
        // Create downloads directory in qeautomation/applicationqe/proposals
        const downloadDir = path.join(__dirname, '..', 'downloads');
        if (!fs.existsSync(downloadDir)) {
            fs.mkdirSync(downloadDir, { recursive: true });
        }

        // Use CDP to force downloads instead of opening PDFs in browser
        const client = await this.page.context().newCDPSession(this.page);
        await client.send('Page.setDownloadBehavior', {
            behavior: 'allow',
            downloadPath: downloadDir,
        });

        // Set up download event listener before clicking
        const downloadPromise = this.page.waitForEvent('download');

        // Click the download button
        await this.downloadButton.click();

        // Wait for the download to start
        const download = await downloadPromise;

        const failure = await download.failure();
        if (failure) {
            throw new Error(`Download failed: ${failure}`);
        }

        const filename = download.suggestedFilename() || `tax-management-services-${Date.now()}.pdf`;
        const downloadPath = path.join(downloadDir, filename);

        // Wait for the file to appear in the download directory
        const deadline = Date.now() + 15000;
        while (Date.now() < deadline) {
            if (fs.existsSync(downloadPath)) {
                const stats = fs.statSync(downloadPath);
                if (stats.size > 0) {
                    return downloadPath;
                }
            }
            await this.page.locator('body').evaluate(() => new Promise(resolve => setTimeout(resolve, 300)));
        }

        throw new Error(`Downloaded file not found or empty: ${downloadPath}`);
    }
}
