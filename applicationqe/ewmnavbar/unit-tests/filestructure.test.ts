/////unit-tests/filestructure
import { describe, it, expect } from 'vitest';
import { getFileStructure } from '../helper/getFileStructure';
import path from 'path';

const PROJECT_ROOT = path.resolve(process.cwd());

//// --- CANONICAL PROJECT STRUCTURE ---
//// When you Add, Remove, or Rename a file => 
const EXPECTED_STRUCTURE: string[] = [

    'README.md',
    'azurePipeline.yaml',
    'data',
    'data/corruptedUsers.json',
    'data/rbac2.json',
    'data/securityRoles.json',
    'data/titlesUrls.json',
    'e2e',
    'e2e/auth',
    'e2e/auth/ActionItemsPages.spec.ts',
    'e2e/auth/ClientsPages.spec.ts',
    'e2e/auth/DashboardPages.spec.ts',
    'e2e/auth/InvestmentsPages.spec.ts',
    'e2e/auth/ModelsPage.spec.ts',
    'e2e/auth/ProductsServicesPages.spec.ts',
    'e2e/auth/HelpSupportPages.spec.ts',
    'e2e/local',
    'e2e/local/InvestmentsPage.spec.ts',
    'e2e/local/Menus.spec.ts',
    'e2e/local/ProductsServicesPage.spec.ts',
    'e2e/local/SubMenus.spec.ts',
    'e2e/local/experiment.spec.ts',
    'e2e/local/goodUsers.spec.ts',
    'e2e/local/uDashboardPages.spec.ts',
    'e2e/unauth',
    'e2e/unauth/Advisor.spec.ts',
    'e2e/unauth/Agent.spec.ts',
    'e2e/unauth/GlobalMenus.spec.ts',
    'e2e/unauth/OfficeAdmin.spec.ts',
    'e2e/unauth/SharedAccess.spec.ts',
    'env',
    "helper",
    'functions',
    'functions/fBrowser.ts',
    'functions/allFunctions.ts',
    'functions/fComparePages.ts',
    'helper/dbconnect.ts',
    'helper/fixtures.ts',
    'helper/getFileStructure.ts',
    'helper/getImage.ts',
    'helper/global.auth.setup.spec.ts',
    'navbar',
    'package.json',
    'pages',
    'pages/ActionItemsPages',
    'pages/ActionItemsPages/pClosed.ts',
    'pages/ActionItemsPages/pNeedsAction.ts',
    'pages/ActionItemsPages/pOpenItems.ts',
    'pages/allPages.ts',
    'pages/ClientsPages',
    'pages/ClientsPages/pAccounts.ts',
    'pages/ClientsPages/pAllClients.ts',
    'pages/ClientsPages/pStrategists.ts',
    'pages/HomePages',
    'pages/HomePages/pHome.ts',
    'pages/HomePages/pLogin.ts',
    'pages/HomePages/pModalCookies.ts',
    'pages/DashboardPages',
    'pages/DashboardPages/pAdvisorBenefits.ts',
    'pages/DashboardPages/pInsights.ts',
    'pages/DashboardPages/pOverview.ts',
    'pages/DashboardPages/pStatementsReports.ts',
    'pages/HelpSupportPages',
    'pages/HelpSupportPages/pComplianceResources.ts',
    'pages/HelpSupportPages/pContactUs.ts',
    'pages/HelpSupportPages/pCustodialServices.ts',
    'pages/HelpSupportPages/pEvents.ts',
    'pages/HelpSupportPages/pKnowledgeBase.ts',
    'pages/HelpSupportPages/pMarketingResources.ts',
    'pages/HelpSupportPages/pRMDResources.ts',
    'pages/HelpSupportPages/pTaxResources.ts',
    'pages/HelpSupportPages/pFees.ts',
    'pages/HelpSupportPages/pGlossary.ts',
    'pages/InvestmentsPages',
    'pages/InvestmentsPages/pCash.ts',
    'pages/InvestmentsPages/pDAF.ts',
    'pages/InvestmentsPages/pDirectIndexing.ts',
    'pages/InvestmentsPages/pGuidedPortfolios.ts',
    'pages/InvestmentsPages/pMorningstar.ts',
    'pages/InvestmentsPages/pNews.ts',
    'pages/InvestmentsPages/pResearch.ts',
    'pages/InvestmentsPages/pSMA.ts',
    'pages/InvestmentsPages/pSavos.ts',
    'pages/InvestmentsPages/pStrategies.ts',
    'pages/InvestmentsPages/pTMS.ts',
    'pages/ProductsServicesPages',
    'pages/ProductsServicesPages/pBusinessConsulting.ts',
    'pages/ProductsServicesPages/pFinancialPlanning.ts',
    'pages/ProductsServicesPages/pLending.ts',
    'pages/ProductsServicesPages/pRetirementServices.ts',
    'pages/MenuPages',
    'pages/MenuPages/pActionItems.ts',
    'pages/MenuPages/pClients.ts',
    'pages/MenuPages/pDashboard.ts',
    'pages/MenuPages/pHelpSupport.ts',
    'pages/MenuPages/pInvestments.ts',
    'pages/MenuPages/pModels.ts',
    'pages/MenuPages/pProductsServices.ts',
    'playwright.config.ts',
    'tsconfig.json',
    'unit-tests',
    'unit-tests/allpages.test.ts',
    'unit-tests/e2e.test.ts',
    'unit-tests/filestructure.test.ts',
    'unit-tests/fixtures.test.ts',
    'unit-tests/globalauth.test.ts',
    'unit-tests/pageobjectname.test.ts',
    'unit-tests/playwrightconfig.test.ts',
    'vitest.config.ts',
    'vitest.setup.js',
].sort(); //// Ensure the hardcoded list is sorted for a reliable comparison

describe('Project File Structure Integrity Check', () => {
    it('should match the canonical file structure exactly', () => {
        //// 1. Get the actual file structure from the disk
        const actualStructure = getFileStructure(PROJECT_ROOT, PROJECT_ROOT);

        //// 2. Perform comparison
        expect(actualStructure).toEqual(EXPECTED_STRUCTURE);

        //// Detailed check for easier debugging (useful if the array comparison fails)
        const missingFiles = EXPECTED_STRUCTURE.filter(f => !actualStructure.includes(f));
        const unexpectedFiles = actualStructure.filter(f => !EXPECTED_STRUCTURE.includes(f));

        if (missingFiles.length > 0) {
            console.error('ERROR: Files expected in the structure are missing from the disk:', missingFiles);
        }
        if (unexpectedFiles.length > 0) {
            console.error('ERROR: Unexpected files found on disk (Update EXPECTED_STRUCTURE if intentional):', unexpectedFiles);
        }
    });
});