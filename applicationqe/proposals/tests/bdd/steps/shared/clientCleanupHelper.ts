import { navigateToHomePage } from '@helperfunctions/navigateToHomePage';
import { PortfolioEnginePage } from '../../../../pages/PortfolioEngineObjectModel';
import { logger } from '../../../../utils/logger';

/**
 * Delete a test client by name
 * @param portfolioEnginePage - The PortfolioEnginePage instance for client operations
 * @param clientNames - Array of client names to delete (format: "FirstName LastName")
 */
export async function deleteTestClient(portfolioEnginePage: PortfolioEnginePage, clientNames: string[]): Promise<void> {
    await navigateToHomePage(portfolioEnginePage.page);
    for (const clientName of clientNames) {
        try {
            await portfolioEnginePage.searchForClient(clientName);
            // Convert "FirstName LastName" to "LastName, FirstName" format to match table display
            const nameParts = clientName.split(' ');
            const displayName =
                nameParts.length > 1
                    ? `${nameParts[nameParts.length - 1]}, ${nameParts.slice(0, -1).join(' ')}`
                    : clientName;

            // Wait for search results to finish loading by waiting for either results or "no results" message
            const clientNameCells = portfolioEnginePage.page
                .locator('#ClientListGrid tbody tr.jqgrow td[aria-describedby="ClientListGrid_clientName"]')
                .filter({ hasText: displayName });

            await Promise.race([
                portfolioEnginePage.noResultsMessage.waitFor({ state: 'visible', timeout: 5000 }).catch(() => {}),
                clientNameCells
                    .first()
                    .waitFor({ state: 'visible', timeout: 5000 })
                    .catch(() => {}),
            ]);

            if (await portfolioEnginePage.noResultsMessage.isVisible()) {
                logger.warn(`No search results found for client ${clientName}`);
                continue;
            }

            const matchCount = await clientNameCells.count();
            if (matchCount === 0) {
                logger.warn(`No matching client rows found for ${clientName}`);
                continue;
            }

            for (let i = 0; i < matchCount; i += 1) {
                await portfolioEnginePage.searchForClient(clientName);
                const currentClientNameCell = clientNameCells.nth(i);

                await Promise.race([
                    portfolioEnginePage.noResultsMessage.waitFor({ state: 'visible', timeout: 5000 }).catch(() => {}),
                    currentClientNameCell.waitFor({ state: 'visible', timeout: 5000 }).catch(() => {}),
                ]);

                if (await portfolioEnginePage.noResultsMessage.isVisible()) {
                    logger.warn(`No search results found for client ${clientName} on iteration ${i + 1}`);
                    break;
                }

                if (await currentClientNameCell.isVisible()) {
                    await currentClientNameCell.click();
                    // Wait for the delete link to be visible after clicking the client
                    await portfolioEnginePage.deleteClientLink.waitFor({ state: 'visible', timeout: 5000 });
                    await portfolioEnginePage.deleteClient();
                    logger.debug(`Deleted client: ${clientName} (${i + 1}/${matchCount})`);
                }
            }
        } catch (err) {
            logger.warn(`Could not delete client ${clientName} - may not exist or already deleted`);
            throw err;
        }
    }

    // await navigateToHomePage(portfolioEnginePage.page);
    // for (const clientName of clientNames) {
    //     try {
    //         await portfolioEnginePage.searchForClient(clientName);
    //         // Convert "FirstName LastName" to "LastName, FirstName" format to match table display
    //         const nameParts = clientName.split(' ');
    //         const displayName = nameParts.length > 1
    //             ? `${nameParts[nameParts.length - 1]}, ${nameParts.slice(0, -1).join(' ')}`
    //             : clientName;

    //         // Wait for search results to finish loading by waiting for either results or "no results" message
    //         const clientNameCell = portfolioEnginePage.getClientNameCell(displayName);

    //         await Promise.race([
    //             portfolioEnginePage.noResultsMessage.waitFor({ state: 'visible', timeout: 5000 }).catch(() => {}),
    //             clientNameCell.waitFor({ state: 'visible', timeout: 5000 }).catch(() => {}),
    //         ]);

    //         if (await portfolioEnginePage.noResultsMessage.isVisible()) {
    //             logger.warn(`No search results found for client ${clientName}`);
    //         } else if (await clientNameCell.isVisible()) {
    //             await clientNameCell.click();
    //             // Wait for the delete link to be visible after clicking the client
    //             await portfolioEnginePage.deleteClientLink.waitFor({ state: 'visible', timeout: 5000 });
    //             await portfolioEnginePage.deleteClient();
    //             logger.debug(`Deleted client: ${clientName}`);
    //         }
    //     } catch (err) {
    //         logger.warn(`Could not delete client ${clientName} - may not exist or already deleted`);
    //         throw err;
    //     }
    // }
}
