import * as dotenv from 'dotenv';
import * as path from 'path';

/**
 * Loads environment variables from the config directory based on the ENVIRONMENT variable.
 * @param environment - Optional environment name. Defaults to process.env.ENVIRONMENT or 'test11'
 * @param configPath - Optional path to config directory. Defaults to '../config'
 * @returns The environment name that was loaded
 */
export function loadEnvironment(environment?: string, configPath: string = '../config'): string {
    const env = environment || process.env.ENVIRONMENT || process.env.Environment;
    const envFilePath = path.resolve(__dirname, `${configPath}/.env.${env}`);

    // Check if file exists before trying to load it
    const fs = require('fs');
    if (fs.existsSync(envFilePath)) {
        dotenv.config({
            path: envFilePath,
            override: true
        });
    } else {
        console.warn(`Warning: Environment file not found at ${envFilePath}, using existing environment variables`);
    }

    return env;
}
