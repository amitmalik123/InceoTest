const { existsSync } = require('fs');
const { execSync } = require('child_process');
const logger = require('./logger');

// Respect HUSKY=0 to allow CI to skip hook installation deterministically
if (process.env.HUSKY === '0') {
    logger.info('HUSKY=0 detected — skipping husky install');
    process.exit(0);
}

try {
    if (existsSync('.git')) {
        logger.info('.git found — installing husky hooks');
        execSync('npx husky install', { stdio: 'inherit' });
    } else {
        logger.info('.git not found — skipping husky install');
    }
} catch (err) {
    logger.error('prepare-husky failed:', err);
    // Don't fail CI just because hooks couldn't be installed; exit non-zero only for unexpected errors
    process.exit(1);
}
