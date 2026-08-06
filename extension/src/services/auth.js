/**
 * AuthService — Extension Authentication Interface
 *
 * This module is a STUB. Authentication is NOT implemented yet.
 *
 * It provides the interface and storage contract so that:
 *  1. All other services can call AuthService.isAuthenticated() safely today.
 *  2. When JWT login is added, only THIS file and the login UI need to change.
 *  3. api.js already reads the token from storage — it will work automatically.
 *
 * TODO (auth): Implement the following when authentication is built:
 *  - login(email, password) → POST /api/user/login/ → store tokens
 *  - logout() → POST /api/user/logout/ with refresh token → clear storage
 *  - refreshToken() → POST /api/user/token/refresh/ → update access token
 *  - getUserProfile() → GET /api/user/profile/
 *  - Register, forgot password, reset password flows
 */

import { STORAGE_KEYS } from "./config.js";

const AuthService = {
  /**
   * Returns true if there is a stored access token.
   *
   * TODO (auth): Add token expiry validation here.
   * TODO (auth): Optionally verify the token is not expired using jwt-decode
   * before returning true, to avoid optimistic auth on expired tokens.
   */
  isAuthenticated() {
    const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
    return Boolean(token);
  },

  /**
   * Returns the stored access token, or null if not authenticated.
   */
  getToken() {
    return localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN) || null;
  },

  /**
   * TODO (auth): Implement login.
   * Steps:
   *   1. POST /api/user/login/ with { email, password }
   *   2. Store access + refresh tokens in localStorage
   *   3. Return the user object
   */
  async login(_email, _password) {
    throw new Error(
      "Authentication is not yet implemented. " +
        "See AuthService TODO comments in src/services/auth.js"
    );
  },

  /**
   * TODO (auth): Implement logout.
   * Steps:
   *   1. POST /api/user/logout/ with { refresh_token }
   *   2. Clear localStorage tokens
   */
  async logout() {
    // For now, just clear any tokens that might exist.
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
  },

  /**
   * TODO (auth): Implement token refresh.
   * Called by api.js on a 401 response to attempt a silent re-authentication.
   * Steps:
   *   1. POST /api/user/token/refresh/ with { refresh: refreshToken }
   *   2. Store the new access token
   *   3. Retry the original request
   */
  async refreshToken() {
    throw new Error("Token refresh is not yet implemented.");
  },
};

export default AuthService;
