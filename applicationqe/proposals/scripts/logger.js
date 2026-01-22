const formatData = data => {
    if (data === undefined) return '';
    if (typeof data === 'string') return ` ${data}`;
    try {
        return ' ' + JSON.stringify(data);
    } catch (e) {
        return ' [unserializable data]';
    }
};

const now = () => new Date().toISOString();

module.exports = {
    info: (message, data) => {
        console.log(`[INFO] ${now()} - ${message}${formatData(data)}`);
    },
    warn: (message, data) => {
        console.warn(`[WARN] ${now()} - ${message}${formatData(data)}`);
    },
    error: (message, data) => {
        console.error(`[ERROR] ${now()} - ${message}${formatData(data)}`);
    },
    debug: (message, data) => {
        if (process.env.DEBUG && process.env.DEBUG !== '0')
            console.debug(`[DEBUG] ${now()} - ${message}${formatData(data)}`);
    },
};
