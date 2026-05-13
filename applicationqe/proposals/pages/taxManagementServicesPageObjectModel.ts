import { type Page, type Locator, type Request } from '@playwright/test';
import path from 'path';
import fs from 'fs';

export class TaxManagementServicesPage {
    readonly page: Page;

    // File Upload
    readonly uploadInput: Locator;
    readonly viewResultsButton: Locator;
    readonly loadingSpinner: Locator;

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
        this.viewResultsButton = page
            .locator('#VIEWRESULTS')
            .or(page.locator('#VIEW RESULTS'))
            .or(page.locator('[aria-label="VIEW RESULTS"]'))
            .or(page.locator('[label="VIEW RESULTS"]')); // variations to handle slight differences in how the button may be labeled across environments
        this.loadingSpinner = page.locator('[class*="LoadingImageLargeIcon"]').last(); // targets the hoverFilled overlay that blocks interactions

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
    async uploadHoldingsTemplate(fileName: string = 'NEW-REVISED Sample TMS ticker file.csv'): Promise<Request[]> {
        const filePath = path.resolve(__dirname, `../data/${fileName}`);
        await this.page.waitForLoadState();
        await this.uploadInput.setInputFiles(filePath);
        await this.page.waitForLoadState();
        return await this.clickViewResultsWithRetry();
    }

    /**
     * Click the VIEW RESULTS button and wait for all 3 TMS API requests to be initiated.
     * Waits for: Proposal, Holdings, and overlaysetting endpoint requests
     * Retries up to 3 times if the click fails or any API request isn't triggered.
     * Returns all 3 API requests for assertion in step files.
     * @throws Error if all retry attempts fail
     */
    private async clickViewResultsWithRetry(maxRetries: number = 3): Promise<Request[]> {
        let lastError: Error | null = null;

        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                await this.page.waitForLoadState('networkidle');
                
                // Wait for any loading spinner overlay to disappear before setting up API listeners
                // (prevents "intercepts pointer events" errors and ensures button is clickable)
                let spinnerHidden = false;
                const maxWaitTime = 30000; // 30 second max wait
                const startTime = Date.now();
                while (!spinnerHidden && Date.now() - startTime < maxWaitTime) {
                    spinnerHidden = await this.loadingSpinner.isHidden();
                    if (!spinnerHidden) {
                        await this.page.waitForTimeout(100);
                    }
                }
                
                // NOW set up listeners for all 3 TMS API endpoint requests AFTER ensuring spinner won't block click
                const proposalPromise = this.page.waitForRequest(
                    request => request.url().includes('/api/v1/tms/Proposal/'),
                    { timeout: 10000 }
                );

                const holdingsPromise = this.page.waitForRequest(
                    request => request.url().includes('/api/v1/tms/Holdings/'),
                    { timeout: 10000 }
                );

                const overlaySettingPromise = this.page.waitForRequest(
                    request => request.url().includes('/api/v1/tms/overlaysetting/'),
                    { timeout: 10000 }
                );
                
                // Click the button
                await this.viewResultsButton.click({ timeout: 5000 });

                // Wait for any loading spinner that appears after the click to disappear
                spinnerHidden = false;
                const clickStartTime = Date.now();
                while (!spinnerHidden && Date.now() - clickStartTime < maxWaitTime) {
                    spinnerHidden = await this.loadingSpinner.isHidden();
                    if (!spinnerHidden) {
                        await this.page.waitForTimeout(100);
                    }
                }

                // Wait for all 3 API requests to be initiated
                const [proposalRequest, holdingsRequest, overlayRequest] = await Promise.all([
                    proposalPromise,
                    holdingsPromise,
                    overlaySettingPromise,
                ]);

                // Return all requests for assertion in step files
                return [proposalRequest, holdingsRequest, overlayRequest];
            } catch (error) {
                lastError = error as Error;

                if (attempt < maxRetries) {
                    // Log the attempt and wait before retrying
                    console.warn(`View Results click failed (attempt ${attempt}/${maxRetries}): ${lastError.message}`);

                    // Wait before retrying to allow page to stabilize
                    await this.page.waitForTimeout(1000 * attempt);
                } else {
                    console.error(`View Results click failed after ${maxRetries} attempts: ${lastError.message}`);
                }
            }
        }

        throw new Error(`Failed to click View Results button after ${maxRetries} attempts: ${lastError?.message}`);
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
