import { PortfolioEnginePage } from '@pages/PortfolioEngineObjectModel';
import NewAccountWizardPage from '@pages/newAccountWizardPageObjectModel';
import { EwmPage } from '@pages/ewmPageObjectModel';
import { TaxManagementServicesPage } from '@pages/taxManagementServicesPageObjectModel';
import { logger } from '../../../../utils/logger';

// Store instances per worker to support parallel test execution
const _portfolioEnginePageInstances = new Map<string, PortfolioEnginePage>();
const _newAccountWizardPageInstances = new Map<string, NewAccountWizardPage>();
const _ewmPageInstances = new Map<string, EwmPage>();
const _taxManagementServicesPageInstances = new Map<string, TaxManagementServicesPage>();

/**
 * Get the current worker ID to isolate instances per worker
 */
function getWorkerId(): string {
    return process.env.TEST_WORKER_INDEX || '0';
}

/**
 * Set the PortfolioEnginePage instance for the current worker
 * @param instance - The PortfolioEnginePage instance to store
 */
export function setPortfolioEnginePageInstance(instance: PortfolioEnginePage) {
    const workerId = getWorkerId();
    logger.debug(`[Worker ${workerId}] Setting PortfolioEnginePage instance`);
    _portfolioEnginePageInstances.set(workerId, instance);
    logger.debug(`[Worker ${workerId}] Instance stored. Instances map size: ${_portfolioEnginePageInstances.size}`);
}

/**
 * Get the PortfolioEnginePage instance for the current worker
 * @returns The stored PortfolioEnginePage instance for this worker
 * @throws Error if instance has not been initialized for this worker
 */
export function getPortfolioEnginePageInstance(): PortfolioEnginePage {
    const workerId = getWorkerId();
    const instance = _portfolioEnginePageInstances.get(workerId);
    if (!instance) {
        throw new Error(
            `PortfolioEnginePage instance not initialized for worker ${workerId}. Call setPortfolioEnginePageInstance() first.`
        );
    }
    return instance;
}

/**
 * Set the NewAccountWizardPage instance for the current worker
 * @param instance - The NewAccountWizardPage instance to store
 */
export function setNewAccountWizardPageInstance(instance: NewAccountWizardPage) {
    const workerId = getWorkerId();
    logger.debug(`[Worker ${workerId}] Setting NewAccountWizardPage instance`);
    _newAccountWizardPageInstances.set(workerId, instance);
}

/**
 * Get the NewAccountWizardPage instance for the current worker
 * @returns The stored NewAccountWizardPage instance for this worker
 * @throws Error if instance has not been initialized for this worker
 */
export function getNewAccountWizardPageInstance(): NewAccountWizardPage {
    const workerId = getWorkerId();
    const instance = _newAccountWizardPageInstances.get(workerId);
    if (!instance) {
        throw new Error(
            `NewAccountWizardPage instance not initialized for worker ${workerId}. Call setNewAccountWizardPageInstance() first.`
        );
    }
    return instance;
}

/**
 * Set the EwmPage instance for the current worker
 * @param instance - The EwmPage instance to store
 */
export function setEwmPageInstance(instance: EwmPage) {
    const workerId = getWorkerId();
    logger.debug(`[Worker ${workerId}] Setting EwmPage instance`);
    _ewmPageInstances.set(workerId, instance);
}

/**
 * Get the EwmPage instance for the current worker
 * @returns The stored EwmPage instance for this worker
 * @throws Error if instance has not been initialized for this worker
 */
export function getEwmPageInstance(): EwmPage {
    const workerId = getWorkerId();
    const instance = _ewmPageInstances.get(workerId);
    if (!instance) {
        throw new Error(`EwmPage instance not initialized for worker ${workerId}. Call setEwmPageInstance() first.`);
    }
    return instance;
}

/**
 * Set the TaxManagementServicesPage instance for the current worker
 * @param instance - The TaxManagementServicesPage instance to store
 */
export function setTaxManagementServicesPageInstance(instance: TaxManagementServicesPage) {
    const workerId = getWorkerId();
    logger.debug(`[Worker ${workerId}] Setting TaxManagementServicesPage instance`);
    _taxManagementServicesPageInstances.set(workerId, instance);
}

/**
 * Get the TaxManagementServicesPage instance for the current worker
 * @returns The stored TaxManagementServicesPage instance for this worker
 * @throws Error if instance has not been initialized for this worker
 */
export function getTaxManagementServicesPageInstance(): TaxManagementServicesPage {
    const workerId = getWorkerId();
    const instance = _taxManagementServicesPageInstances.get(workerId);
    if (!instance) {
        throw new Error(
            `TaxManagementServicesPage instance not initialized for worker ${workerId}. Call setTaxManagementServicesPageInstance() first.`
        );
    }
    return instance;
}
