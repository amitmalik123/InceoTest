// functions/fAuthUtils.ts

export class AuthUtils {
    /**
     * Decodes the KEYCLOAK_IDENTITY JWT to extract UID (sub) and role claims.
     * Does not require an external library.
     */
    decodeJWT(token: string) {
        try {
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = Buffer.from(base64, 'base64').toString();
            return JSON.parse(jsonPayload);
        } catch (error) {
            throw new Error(`AuthUtils: Failed to decode JWT token. Error: ${error.message}`);
        }
    }

    verifyCookieExists(cookies: any[], cookieName: string) {
        const cookie = cookies.find(c => c.name === cookieName);
        if (!cookie) throw new Error(`AuthUtils: Missing required cookie: ${cookieName}`);
        return cookie;
    }
}