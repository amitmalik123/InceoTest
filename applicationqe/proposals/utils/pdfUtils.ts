import fs from 'fs';
import os from 'os';
import path from 'path';
import { randomUUID } from 'crypto';
import { PDFParse } from 'pdf-parse';
import { logger } from './logger';
import type { Page, Response, APIRequestContext } from '@playwright/test';

async function sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Removes all files in the downloads directory.
 */
export function cleanupDownloads(): void {
    const downloadDir = path.join(__dirname, '..', 'downloads');
    if (!fs.existsSync(downloadDir)) {
        return;
    }

    const entries = fs.readdirSync(downloadDir, { withFileTypes: true });
    for (const entry of entries) {
        if (entry.isFile()) {
            fs.unlinkSync(path.join(downloadDir, entry.name));
        }
    }
}

function extractPdfPageCount(pdfBuffer: Buffer): number | null {
    const pdfText = pdfBuffer.toString('latin1');

    // Prefer page-tree counts: objects that declare /Type /Pages with /Count <n>
    const pageTreeMatches = [...pdfText.matchAll(/\/Type\s*\/Pages[\s\S]{0,500}?\/Count\s+(\d+)/g)];
    if (pageTreeMatches.length > 0) {
        const counts = pageTreeMatches
            .map(match => Number.parseInt(match[1], 10))
            .filter(count => Number.isInteger(count) && count > 0);
        if (counts.length > 0) {
            return Math.max(...counts);
        }
    }

    // Fallback for files where the above pattern is not found
    const genericMatches = [...pdfText.matchAll(/\/Count\s+(\d+)/g)];
    const genericCounts = genericMatches
        .map(match => Number.parseInt(match[1], 10))
        .filter(count => Number.isInteger(count) && count > 0);

    return genericCounts.length > 0 ? Math.max(...genericCounts) : null;
}

function hasPdfTrailer(pdfBuffer: Buffer): boolean {
    const start = Math.max(0, pdfBuffer.length - 1024);
    const tail = pdfBuffer.toString('latin1', start);
    return tail.includes('%%EOF');
}

export type ProposalTextValidationOptions = {
    includedSections: string[];
    excludedSections?: string[];
    includeTableOfContents?: boolean;
    tocSections?: string[];
    sectionSnippetRules?: ProposalSectionSnippetRule[];
};

export type ProposalSectionSnippetRule = {
    section: string;
    mustContainAll?: string[];
    mustContainAny?: string[];
    forbid?: string[];
};

function normalizeTextForMatch(value: string): string {
    return value
        .toLowerCase()
        .replace(/[^a-z0-9%$]+/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
}

async function validateProposalPdfText(pdfPath: string, textValidation: ProposalTextValidationOptions): Promise<void> {
    const pdfBuffer = fs.readFileSync(pdfPath);
    const parser = new PDFParse({ data: pdfBuffer });
    const parsed = await parser.getText();
    const rawText = parsed.text ?? '';
    await parser.destroy();

    if (!rawText.trim()) {
        throw new Error(`Unable to extract text from proposal PDF: ${pdfPath}`);
    }

    const normalizedDoc = normalizeTextForMatch(rawText);
    const summarizeList = (items: string[], limit = 8): string => {
        if (items.length === 0) {
            return '(none)';
        }

        const displayed = items.slice(0, limit);
        const suffix = items.length > limit ? ` (+${items.length - limit} more)` : '';
        return `${displayed.join(', ')}${suffix}`;
    };

    // Validate included sections are present (anywhere in the document)
    const normalizedIncluded = textValidation.includedSections.map(section => ({
        original: section,
        normalized: normalizeTextForMatch(section),
    }));

    const foundIncluded = normalizedIncluded
        .filter(section => normalizedDoc.includes(section.normalized))
        .map(section => section.original);
    const missingIncluded = normalizedIncluded
        .filter(section => !normalizedDoc.includes(section.normalized))
        .map(section => section.original);
    if (missingIncluded.length > 0) {
        throw new Error(
            `Proposal section validation failed. Expected included sections: ${summarizeList(
                textValidation.includedSections
            )}. Found included sections: ${summarizeList(foundIncluded)}. Missing sections: ${summarizeList(
                missingIncluded
            )}`
        );
    }

    // Validate excluded sections are absent
    const normalizedExcluded = (textValidation.excludedSections ?? []).map(section => ({
        original: section,
        normalized: normalizeTextForMatch(section),
    }));

    const presentExcluded = normalizedExcluded
        .filter(section => section.normalized.length > 0 && normalizedDoc.includes(section.normalized))
        .map(section => section.original);
    if (presentExcluded.length > 0) {
        throw new Error(
            `Proposal excluded-section validation failed. Expected excluded sections not present: ${summarizeList(
                normalizedExcluded.map(section => section.original)
            )}. Found excluded sections in document: ${summarizeList(presentExcluded)}`
        );
    }

    // Validate snippet rules (snippets must appear anywhere in the document)
    if ((textValidation.sectionSnippetRules ?? []).length > 0) {
        for (const rule of textValidation.sectionSnippetRules ?? []) {
            // Verify the section this rule refers to is in the included list
            const normalizedSectionName = normalizeTextForMatch(rule.section);
            const sectionIsIncluded = normalizedIncluded.some(s => s.normalized === normalizedSectionName);

            if (!sectionIsIncluded) {
                // Skip rules for sections that aren't included in this proposal
                continue;
            }

            const mustContainAll = (rule.mustContainAll ?? []).map(snippet => normalizeTextForMatch(snippet));
            const mustContainAny = (rule.mustContainAny ?? []).map(snippet => normalizeTextForMatch(snippet));
            const forbid = (rule.forbid ?? []).map(snippet => normalizeTextForMatch(snippet));

            const missingAll = mustContainAll.filter(snippet => snippet.length > 0 && !normalizedDoc.includes(snippet));
            if (missingAll.length > 0) {
                const foundRequired = (rule.mustContainAll ?? []).filter(snippet =>
                    normalizedDoc.includes(normalizeTextForMatch(snippet))
                );
                throw new Error(
                    `Proposal snippet validation failed for section '${rule.section}'. Expected required snippets: ${summarizeList(
                        rule.mustContainAll ?? []
                    )}. Found required snippets: ${summarizeList(foundRequired)}. Missing required snippets: ${summarizeList(
                        (rule.mustContainAll ?? []).filter(snippet =>
                            missingAll.includes(normalizeTextForMatch(snippet))
                        )
                    )}`
                );
            }

            const anyCandidates = mustContainAny.filter(snippet => snippet.length > 0);
            if (anyCandidates.length > 0 && !anyCandidates.some(snippet => normalizedDoc.includes(snippet))) {
                const foundAny = (rule.mustContainAny ?? []).filter(snippet =>
                    normalizedDoc.includes(normalizeTextForMatch(snippet))
                );
                throw new Error(
                    `Proposal any-of snippet validation failed for section '${rule.section}'. Expected one of: ${summarizeList(
                        rule.mustContainAny ?? []
                    )}. Found matches: ${summarizeList(foundAny)}`
                );
            }

            const forbiddenHits = forbid.filter(snippet => snippet.length > 0 && normalizedDoc.includes(snippet));
            if (forbiddenHits.length > 0) {
                throw new Error(
                    `Proposal forbidden-snippet validation failed for section '${rule.section}'. Expected forbidden snippets absent: ${summarizeList(
                        rule.forbid ?? []
                    )}. Found forbidden snippets: ${summarizeList(
                        (rule.forbid ?? []).filter(snippet => forbiddenHits.includes(normalizeTextForMatch(snippet)))
                    )}`
                );
            }
        }
    }

    // Validate TOC if requested
    if (textValidation.includeTableOfContents) {
        const rawPages = rawText.split('\f');
        const normalizedPages = rawPages.map(pageText => normalizeTextForMatch(pageText));
        const tocMarker = normalizeTextForMatch('Table of Contents');
        const tocPageIndex = normalizedPages.findIndex(pageText => pageText.includes(tocMarker));

        if (tocPageIndex === -1) {
            throw new Error('Expected a table of contents page but it was not found in the proposal PDF');
        }

        const tocSections = (textValidation.tocSections ?? textValidation.includedSections).map(section => ({
            original: section,
            normalized: normalizeTextForMatch(section),
        }));

        const tocPage = normalizedPages[tocPageIndex];
        const missingFromToc = tocSections
            .filter(section => !tocPage.includes(section.normalized))
            .map(section => section.original);

        if (missingFromToc.length > 0) {
            const foundInToc = tocSections
                .filter(section => tocPage.includes(section.normalized))
                .map(section => section.original);
            throw new Error(
                `TOC validation failed. Expected TOC sections: ${summarizeList(
                    tocSections.map(section => section.original)
                )}. Found TOC sections: ${summarizeList(foundInToc)}. Missing TOC sections: ${summarizeList(
                    missingFromToc
                )}`
            );
        }
    }

    logger.debug(`Proposal text validation passed for ${pdfPath}`);
}

function isPdfComplete(pdfPath: string, expectedPageCount: number): boolean {
    // Fast existence check.
    if (!fs.existsSync(pdfPath)) {
        return false;
    }

    const pdfBuffer = fs.readFileSync(pdfPath);
    // Reject empty or partial files.
    if (pdfBuffer.length <= 1000) {
        return false;
    }

    // Validate the PDF header.
    const pdfHeader = pdfBuffer.toString('ascii', 0, 4);
    if (pdfHeader !== '%PDF') {
        return false;
    }

    // Require a PDF trailer to reduce partial reads.
    if (!hasPdfTrailer(pdfBuffer)) {
        return false;
    }

    // Confirm the expected page count is present.
    const actualPageCount = extractPdfPageCount(pdfBuffer);
    return actualPageCount >= expectedPageCount;
}

/**
 * Validates that a downloaded PDF file has content
 * @param pdfPath Path to the PDF file to validate
 * @throws Error if PDF validation fails
 * @returns void (throws on failure)
 */
export async function validatePdfContent(pdfPath: string, expectedPageCount: number): Promise<void> {
    // Ensure the file exists before reading.
    if (!fs.existsSync(pdfPath)) {
        throw new Error(`PDF file not found at path: ${pdfPath}`);
    }

    const pdfBuffer = fs.readFileSync(pdfPath);

    // Guard against zero-byte or partial files.
    // Validate PDF file has content (min 1000 bytes indicates real PDF data)
    if (pdfBuffer.length <= 1000) {
        throw new Error(`PDF file too small (${pdfBuffer.length} bytes) - likely empty or invalid`);
    }

    // Confirm the PDF header is present.
    // Check for PDF magic bytes (%PDF header)
    const pdfHeader = pdfBuffer.toString('ascii', 0, 4);
    if (pdfHeader !== '%PDF') {
        throw new Error(`Invalid PDF header. Expected '%PDF' but got '${pdfHeader}'`);
    }

    // Extract and verify the page count.
    const actualPageCount = extractPdfPageCount(pdfBuffer);
    if (actualPageCount === null) {
        throw new Error(`Unable to determine PDF page count for: ${pdfPath}`);
    }
    if (actualPageCount !== expectedPageCount) {
        throw new Error(`Expected ${expectedPageCount} pages but found ${actualPageCount} in PDF: ${pdfPath}`);
    }

    logger.debug(
        `PDF validation passed: File size ${pdfBuffer.length} bytes, valid header, page count ${actualPageCount}`
    );
}

/**
 * Downloads and validates a PDF from the page through the provided callback
 * @param downloadCallback Async function that triggers the download on the page
 * @param validationOptions Optional configuration for validation
 * @returns Path to the downloaded and validated PDF file
 */
export async function downloadAndValidatePdf(
    downloadCallback: () => Promise<string>,
    validationOptions: {
        expectedPageCount: number;
        validateContent?: boolean;
        proposalTextValidation?: ProposalTextValidationOptions;
    }
): Promise<string> {
    const options = {
        validateContent: true,
        ...validationOptions,
    };

    try {
        const pdfPath = await downloadCallback();
        logger.debug(`PDF downloaded successfully to: ${pdfPath}`);

        if (options.validateContent) {
            await validatePdfContent(pdfPath, options.expectedPageCount);
        }

        if (options.proposalTextValidation) {
            await validateProposalPdfText(pdfPath, options.proposalTextValidation);
        }

        return pdfPath;
    } catch (err) {
        const errorDetails = err instanceof Error ? { message: err.message, stack: err.stack } : err;
        logger.error('Failed to download or validate PDF', errorDetails);
        throw err;
    }
}

/**
 * Clicks an element that triggers a PDF download, saves it, and validates content
 * @param page Playwright page used to wait for download events
 * @param clickDownload Callback that clicks the download trigger
 * @param options Optional configuration for validation and filename prefix
 * @returns Path to the downloaded and validated PDF file
 */
export async function downloadAndValidatePdfFromClick(
    page: Page,
    clickDownload: () => Promise<void>,
    options: {
        expectedPageCount: number;
        validateContent?: boolean;
        filenamePrefix?: string;
        expectedBrowserFilename: string;
        proposalTextValidation?: ProposalTextValidationOptions;
    }
): Promise<string> {
    const settings = {
        validateContent: true,
        filenamePrefix: 'download',
        ...options,
    };

    return downloadAndValidatePdf(
        async () => {
            const downloadDir = path.join(__dirname, '..', 'downloads');
            const systemDownloadsDir = path.join(os.homedir(), 'Downloads');
            const downloadTimeoutMs = 60000;
            const stabilityDelayMs = 500;
            const stabilityChecksRequired = 3;
            const completeChecksRequired = 2;
            if (!fs.existsSync(downloadDir)) {
                fs.mkdirSync(downloadDir, { recursive: true });
            }

            const expectedStem = path.parse(settings.expectedBrowserFilename).name.toLowerCase();

            const isPdfResponse = (response: Response): boolean => {
                const contentType = response.headers()['content-type'] ?? '';
                return contentType.toLowerCase().includes('application/pdf');
            };

            const isLikelyPdfBuffer = (buffer: Buffer): boolean => {
                if (buffer.length < 5) {
                    return false;
                }

                return buffer.subarray(0, 5).toString('latin1') === '%PDF-';
            };

            const savePdfBuffer = (buffer: Buffer, source: string): string => {
                const tempPath = path.join(downloadDir, `temp-${randomUUID()}.pdf`);
                fs.writeFileSync(tempPath, buffer);
                logger.debug(`PDF saved from ${source}: ${tempPath} (${buffer.length} bytes)`);
                return tempPath;
            };

            const fetchAndSavePdfFromResponse = async (
                pdfResponse: Response,
                requestContext: APIRequestContext
            ): Promise<string> => {
                const responseUrl = pdfResponse.url();

                // Prefer the captured browser response body when it is actual PDF bytes.
                const capturedBuffer = await pdfResponse.body().catch(() => Buffer.alloc(0));
                if (isLikelyPdfBuffer(capturedBuffer)) {
                    return savePdfBuffer(capturedBuffer, 'captured response');
                }

                const originalRequest = pdfResponse.request();
                const originalMethod = originalRequest.method();
                const originalData = originalRequest.postData() ?? undefined;
                const methodsToTry = [originalMethod, originalMethod === 'GET' ? 'POST' : 'GET'];
                const attemptedStatuses: string[] = [];

                for (const method of methodsToTry) {
                    logger.debug(`Fetching PDF directly from URL using ${method}: ${responseUrl}`);

                    const refetch = await requestContext.fetch(responseUrl, {
                        method,
                        data: method === 'GET' ? undefined : originalData,
                        failOnStatusCode: false,
                    });

                    attemptedStatuses.push(`${method}=${refetch.status()} ${refetch.statusText()}`);
                    if (!refetch.ok()) {
                        continue;
                    }

                    const refetchedBuffer = await refetch.body();
                    if (isLikelyPdfBuffer(refetchedBuffer)) {
                        return savePdfBuffer(refetchedBuffer, `direct fetch (${method})`);
                    }
                }

                throw new Error(
                    `Failed to fetch valid PDF from ${responseUrl}. Attempts: ${attemptedStatuses.join(', ')}`
                );
            };

            const finalizeDownload = (matchedPath: string): string => {
                const filename = `${settings.filenamePrefix}-${randomUUID()}.pdf`;
                const downloadPath = path.join(downloadDir, filename);

                if (path.dirname(matchedPath) === downloadDir) {
                    fs.renameSync(matchedPath, downloadPath);
                } else {
                    fs.copyFileSync(matchedPath, downloadPath);
                }

                logger.debug(`Downloaded file renamed to: ${downloadPath}`);
                return downloadPath;
            };

            const findLatestExpectedPdf = (minMtimeMs: number): string | null => {
                const candidateDirs = [downloadDir, systemDownloadsDir];
                const candidates: Array<{ fullPath: string; mtimeMs: number; size: number }> = [];

                for (const dirPath of candidateDirs) {
                    if (!fs.existsSync(dirPath)) {
                        continue;
                    }

                    const files = fs.readdirSync(dirPath);
                    for (const file of files) {
                        if (!file.toLowerCase().endsWith('.pdf')) {
                            continue;
                        }

                        const fileStem = path.parse(file).name.toLowerCase();
                        if (!fileStem.includes(expectedStem)) {
                            continue;
                        }

                        const fullPath = path.join(dirPath, file);
                        const stats = fs.statSync(fullPath);
                        if (stats.mtimeMs < minMtimeMs || stats.size <= 1000) {
                            continue;
                        }

                        candidates.push({ fullPath, mtimeMs: stats.mtimeMs, size: stats.size });
                    }
                }

                if (candidates.length === 0) {
                    return null;
                }

                candidates.sort((a, b) => {
                    if (b.mtimeMs !== a.mtimeMs) {
                        return b.mtimeMs - a.mtimeMs;
                    }
                    return b.size - a.size;
                });

                return candidates[0].fullPath;
            };

            const waitForCompleteExpectedPdf = async (minMtimeMs: number): Promise<string> => {
                const deadline = Date.now() + downloadTimeoutMs;
                let lastPath = '';
                let lastSize = -1;
                let stableCount = 0;
                let completeCount = 0;

                while (Date.now() < deadline) {
                    const candidatePath = findLatestExpectedPdf(minMtimeMs);
                    if (!candidatePath) {
                        await sleep(stabilityDelayMs);
                        continue;
                    }

                    const tempPath = `${candidatePath}.crdownload`;
                    if (fs.existsSync(tempPath)) {
                        logger.debug(`Found temp download file, waiting: ${tempPath}`);
                        await sleep(stabilityDelayMs);
                        continue;
                    }

                    const currentSize = fs.statSync(candidatePath).size;
                    logger.debug(`Candidate PDF: ${candidatePath} (${currentSize} bytes, previous: ${lastSize})`);

                    if (candidatePath === lastPath && currentSize === lastSize && currentSize > 1000) {
                        stableCount++;
                        if (stableCount >= stabilityChecksRequired) {
                            if (isPdfComplete(candidatePath, settings.expectedPageCount)) {
                                completeCount++;
                            } else {
                                completeCount = 0;
                            }

                            if (completeCount >= completeChecksRequired) {
                                return candidatePath;
                            }
                        }
                    } else {
                        stableCount = 0;
                        completeCount = 0;
                    }

                    lastPath = candidatePath;
                    lastSize = currentSize;
                    await sleep(stabilityDelayMs);
                }

                throw new Error(
                    `Expected PDF did not appear as a complete file for stem '${expectedStem}' in ${downloadDir} or ${systemDownloadsDir}`
                );
            };

            // Use CDP to force downloads instead of opening PDFs in browser
            const client = await page.context().newCDPSession(page);
            await client.send('Page.setDownloadBehavior', {
                behavior: 'allow',
                downloadPath: downloadDir,
            });

            const context = page.context();

            // Set up event listeners BEFORE clicking
            logger.debug('Setting up event listeners for download and new page/popup...');
            const downloadOnCurrentPage = page
                .waitForEvent('download', { timeout: 5000 })
                .then(download => {
                    logger.debug('Download event fired on current page');
                    return { download, page };
                })
                .catch(() => {
                    logger.debug('No download event on current page within timeout');
                    return null;
                });

            const newPagePromise = context
                .waitForEvent('page', { timeout: 5000 })
                .then(newPage => {
                    logger.debug(`New page detected with URL: ${newPage.url()}`);
                    return newPage;
                })
                .catch(() => {
                    logger.debug('No new page event within timeout');
                    return null;
                });

            const popupPromise = page
                .waitForEvent('popup', { timeout: 5000 })
                .then(popup => {
                    logger.debug(`Popup window detected with URL: ${popup.url()}`);
                    return popup;
                })
                .catch(() => {
                    logger.debug('No popup event within timeout');
                    return null;
                });

            logger.debug('Triggering PDF download action...');
            const clickStartedAt = Date.now();
            await clickDownload();

            logger.debug('Waiting for download event, new page, or popup...');
            const firstResult = await Promise.race([downloadOnCurrentPage, newPagePromise, popupPromise]);
            let download = firstResult && 'download' in firstResult ? firstResult.download : null;
            let targetPage = page;
            let fetchedPath: string | null = null;

            if (!download) {
                // Check if we got a new page or popup
                if (firstResult && typeof firstResult === 'object' && 'url' in firstResult) {
                    targetPage = firstResult;
                    logger.debug(`New window opened initially at: ${targetPage.url()}`);

                    // Configure download behavior on the new window too
                    const newWindowClient = await context.newCDPSession(targetPage);
                    await newWindowClient.send('Page.setDownloadBehavior', {
                        behavior: 'allow',
                        downloadPath: downloadDir,
                    });

                    // If the new window loads a PDF viewer, capture the PDF URL and fetch it directly
                    const pdfResponse = await targetPage
                        .waitForResponse(response => isPdfResponse(response), { timeout: 10000 })
                        .catch(() => null);
                    if (pdfResponse) {
                        logger.debug(`PDF response detected on new window: ${pdfResponse.url()}`);
                        fetchedPath = await fetchAndSavePdfFromResponse(pdfResponse, targetPage.request);
                    }

                    // Only wait for download event if we haven't already fetched the PDF
                    if (!fetchedPath) {
                        logger.debug('Waiting for download to start on new window...');
                        download = await targetPage.waitForEvent('download', { timeout: 60000 }).catch(() => {
                            logger.debug('No download event on new window within 60s');
                            return null;
                        });
                    } else {
                        logger.debug('PDF already fetched directly, skipping download event wait');
                    }
                }

                if (!download) {
                    if (!fetchedPath) {
                        // Try to capture a PDF response on the current page as a last resort
                        const pdfResponse = await page
                            .waitForResponse(response => isPdfResponse(response), { timeout: 5000 })
                            .catch(() => null);
                        if (pdfResponse) {
                            logger.debug(`PDF response detected on current page: ${pdfResponse.url()}`);
                            fetchedPath = await fetchAndSavePdfFromResponse(pdfResponse, page.request);
                        }
                    }

                    if (fetchedPath) {
                        return finalizeDownload(fetchedPath);
                    }

                    logger.debug('No download event detected, falling back to expected filename polling.');
                    const matchedPath = await waitForCompleteExpectedPdf(clickStartedAt - 2000);
                    return finalizeDownload(matchedPath);
                }
            }

            // If we didn't get a download event or catch it via fallbacks, throw error
            if (!download) {
                throw new Error(
                    `Failed to capture PDF: no download event fired and fallback methods did not find/return a file`
                );
            }

            const failure = await download.failure();
            if (failure) {
                throw new Error(`Download failed: ${failure}`);
            }

            // Wait for the browser to download the file with the expected filename
            logger.debug(`Waiting for browser to download file: ${settings.expectedBrowserFilename}`);

            const matchedPath = await waitForCompleteExpectedPdf(clickStartedAt - 2000);
            return finalizeDownload(matchedPath);
        },
        {
            expectedPageCount: settings.expectedPageCount,
            validateContent: settings.validateContent,
            proposalTextValidation: settings.proposalTextValidation,
        }
    );
}
