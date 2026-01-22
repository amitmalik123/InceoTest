export type LogData = Record<string, unknown> | string | undefined;

function formatData(data?: LogData) {
    if (data === undefined) return '';
    if (typeof data === 'string') return ` ${data}`;
    try {
        return ' ' + JSON.stringify(data);
    } catch {
        return ' [unserializable data]';
    }
}

function levelEnabled(level: 'debug' | 'info' | 'warn' | 'error') {
    const envLevel = (process.env.LOG_LEVEL || process.env.NODE_ENV || '').toLowerCase();
    if (process.env.DEBUG && process.env.DEBUG !== '0') return true;
    if (!envLevel) return true; // default: enabled
    const order = { debug: 0, info: 1, warn: 2, error: 3 } as const;
    const levelOrder = order[level];
    const envOrder = (order as Record<string, number | undefined>)[envLevel];
    if (envOrder === undefined) return true;
    return levelOrder >= envOrder;
}

export const logger = {
    info: (message: string, data?: LogData) => {
        if (!levelEnabled('info')) return;
        // keep a concise, structured format
        console.log(`[INFO] ${new Date().toISOString()} - ${message}${formatData(data)}`);
    },
    warn: (message: string, data?: LogData) => {
        if (!levelEnabled('warn')) return;
        console.warn(`[WARN] ${new Date().toISOString()} - ${message}${formatData(data)}`);
    },
    error: (message: string, data?: LogData) => {
        if (!levelEnabled('error')) return;
        console.error(`[ERROR] ${new Date().toISOString()} - ${message}${formatData(data)}`);
    },
    debug: (message: string, data?: LogData) => {
        if (!levelEnabled('debug')) return;
        console.debug(`[DEBUG] ${new Date().toISOString()} - ${message}${formatData(data)}`);
    },
};
