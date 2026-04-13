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
    if (process.env.Environment === 'prod' || process.env.ENVIRONMENT === 'prod' || process.env.Environment === 'silo' || process.env.ENVIRONMENT === 'silo') {
        await expect(tmsPage.page).toHaveScreenshot('tax-sensitivity-low.prod.png', {
            mask: screenshotMaskLocators,
            fullPage: true,
            maxDiffPixelRatio: 0.03,
        });
    } else {
        await expect(tmsPage.page).toHaveScreenshot('tax-sensitivity-low.png', {
            mask: screenshotMaskLocators,
            fullPage: true,
            maxDiffPixelRatio: 0.03,
        });
    }

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
    if (process.env.Environment === 'prod' || process.env.ENVIRONMENT === 'prod' || process.env.Environment === 'silo' || process.env.ENVIRONMENT === 'silo') {
        await expect(tmsPage.page).toHaveScreenshot('tax-sensitivity-medium.prod.png', {
            mask: screenshotMaskLocators,
            fullPage: true,
            maxDiffPixelRatio: 0.03,
        });
    } else {
        await expect(tmsPage.page).toHaveScreenshot('tax-sensitivity-medium.png', {
            mask: screenshotMaskLocators,
            fullPage: true,
            maxDiffPixelRatio: 0.03,
        });
    }

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
    if (process.env.Environment === 'prod' || process.env.ENVIRONMENT === 'prod' || process.env.Environment === 'silo' || process.env.ENVIRONMENT === 'silo') {
        await expect(tmsPage.page).toHaveScreenshot('tax-sensitivity-high.prod.png', {
            mask: screenshotMaskLocators,
            fullPage: true,
            maxDiffPixelRatio: 0.03,
        });
    } else {
        await expect(tmsPage.page).toHaveScreenshot('tax-sensitivity-high.png', {
            mask: screenshotMaskLocators,
            fullPage: true,
            maxDiffPixelRatio: 0.03,
        });
    }

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
    if (process.env.Environment === 'prod' || process.env.ENVIRONMENT === 'prod' || process.env.Environment === 'silo' || process.env.ENVIRONMENT === 'silo') {
        await expect(tmsPage.page).toHaveScreenshot('tax-sensitivity-very-high.prod.png', {
            mask: screenshotMaskLocators,
            fullPage: true,
            maxDiffPixelRatio: 0.03,
        });
    } else {
        await expect(tmsPage.page).toHaveScreenshot('tax-sensitivity-very-high.png', {
            mask: screenshotMaskLocators,
            fullPage: true,
            maxDiffPixelRatio: 0.03,
        });
    }

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
