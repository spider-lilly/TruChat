/**
 * Extension API Configuration
 *
 * Set VITE_API_BASE_URL in your .env file to point at the deployed backend.
 * Example:
 *   VITE_API_BASE_URL=https://your-deployed-api.com/api
 *
 * Do NOT hardcode localhost or any specific URL here.
 */

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

/**
 * Storage keys used across services.
 * Centralised here so renaming them later is a one-line change.
 */
export const STORAGE_KEYS = {
  ACCESS_TOKEN: "extension_accessToken",
  REFRESH_TOKEN: "extension_refreshToken",
};
