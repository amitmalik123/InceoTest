import * as dotenv from 'dotenv';
import * as path from 'path';

/**
 * Loads environment variables from the config directory based on the ENVIRONMENT variable.
 * @param environment - Optional environment name. Defaults to process.env.ENVIRONMENT or 'test11'
 * @param configPath - Optional path to config directory. Defaults to '../config'
 * @returns The environment name that was loaded
 */
export function loadEnvironment(environment?: string, configPath: string = '../config'): string {
    const env = environment || process.env.ENVIRONMENT || 'test11';
    dotenv.config({
        path: path.resolve(__dirname, `${configPath}/.env.${env}`),
        override: true
    });
    return env;
}
