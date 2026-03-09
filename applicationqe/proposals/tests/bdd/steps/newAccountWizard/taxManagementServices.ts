import { expect, Then, When } from '../../../../fixtures/fixtures';
import { logger } from '../../../../utils/logger';
import { downloadAndValidatePdfFromClick } from '../../../../utils/pdfUtils';
import { getTaxManagementServicesPageInstance } from '../shared/instanceManager';

When('I upload a holdings template', async ({}) => {
    const tmsPage = getTaxManagementServicesPageInstance();
    logger.debug('\nUploading completed template');
    await tmsPage.uploadHoldingsTemplate();
});

Then('The UI summary should be generated', async ({}) => {
    const tmsPage = getTaxManagementServicesPageInstance();
    logger.debug('\nVerifying UI summary is generated');
    const screenshotMaskLocators = tmsPage.getScreenshotMaskLocators();

    // Hide chat widget in prod by directly manipulating DOM
    await tmsPage.page.evaluate(() => {
        const chatWidget = document.getElementById('chatpillid');
        if (chatWidget) {
            chatWidget.style.display = 'none';
        }
    });

    // Low sensitivity
    await tmsPage.page.bringToFront();
    await tmsPage.selectTaxSensitivity('Low');
    const lowSensitivitySnapshot =
        process.env.Environment === 'prod' ? 'tax-sensitivity-low.prod.png' : 'tax-sensitivity-low.png';
    await expect(tmsPage.page).toHaveScreenshot(lowSensitivitySnapshot, {
        mask: screenshotMaskLocators,
        fullPage: true,
        maxDiffPixelRatio: 0.03,
    });

    // Test PDF download for Low sensitivity
    logger.debug('\nAttempting to download PDF for Low sensitivity');
    await downloadAndValidatePdfFromClick(tmsPage.page, () => tmsPage.downloadButton.click(), {
        expectedPageCount: 2,
        filenamePrefix: 'tax-management-services',
        expectedBrowserFilename: 'TMS_Report.pdf',
    });

    // Medium sensitivity
    await tmsPage.page.bringToFront();
    await tmsPage.selectTaxSensitivity('Medium');
    const mediumSensitivitySnapshot =
        process.env.Environment === 'prod' ? 'tax-sensitivity-medium.prod.png' : 'tax-sensitivity-medium.png';
    await expect(tmsPage.page).toHaveScreenshot(mediumSensitivitySnapshot, {
        mask: screenshotMaskLocators,
        fullPage: true,
        maxDiffPixelRatio: 0.03,
    });

    // Test PDF download for Medium sensitivity
    logger.debug('\nAttempting to download PDF for Medium sensitivity');
    await downloadAndValidatePdfFromClick(tmsPage.page, () => tmsPage.downloadButton.click(), {
        expectedPageCount: 2,
        filenamePrefix: 'tax-management-services',
        expectedBrowserFilename: 'TMS_Report.pdf',
    });

    // High sensitivity
    await tmsPage.page.bringToFront();
    await tmsPage.selectTaxSensitivity('High');
    const highSensitivitySnapshot =
        process.env.Environment === 'prod' ? 'tax-sensitivity-high.prod.png' : 'tax-sensitivity-high.png';
    await expect(tmsPage.page).toHaveScreenshot(highSensitivitySnapshot, {
        mask: screenshotMaskLocators,
        fullPage: true,
        maxDiffPixelRatio: 0.03,
    });

    // Test PDF download for High sensitivity
    logger.debug('\nAttempting to download PDF for High sensitivity');
    await downloadAndValidatePdfFromClick(tmsPage.page, () => tmsPage.downloadButton.click(), {
        expectedPageCount: 2,
        filenamePrefix: 'tax-management-services',
        expectedBrowserFilename: 'TMS_Report.pdf',
    });

    // Very High sensitivity
    await tmsPage.page.bringToFront();
    await tmsPage.selectTaxSensitivity('Very High');
    const veryHighSensitivitySnapshot =
        process.env.Environment === 'prod' ? 'tax-sensitivity-very-high.prod.png' : 'tax-sensitivity-very-high.png';
    await expect(tmsPage.page).toHaveScreenshot(veryHighSensitivitySnapshot, {
        mask: screenshotMaskLocators,
        fullPage: true,
        maxDiffPixelRatio: 0.03,
    });

    // Test PDF download for Very High sensitivity
    logger.debug('\nAttempting to download PDF for Very High sensitivity');
    await downloadAndValidatePdfFromClick(tmsPage.page, () => tmsPage.downloadButton.click(), {
        expectedPageCount: 2,
        filenamePrefix: 'tax-management-services',
        expectedBrowserFilename: 'TMS_Report.pdf',
    });

    await tmsPage.page.bringToFront();
    await tmsPage.continueButton.click();
});
