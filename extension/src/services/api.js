/**
 * Base API client for the TruChat browser extension.
 *
 * All HTTP requests to the backend go through this module.
 * Authentication headers are attached automatically when a token is present.
 *
 * TODO (auth): When JWT login is implemented, the token will be written to
 * storage by AuthService.login() and will be picked up here automatically
 * on every subsequent request — no other changes needed in this file.
 */

import { API_BASE_URL, STORAGE_KEYS } from "./config.js";

/** Custom error class that carries the HTTP status code. */
export class ApiError extends Error {
  constructor(message, status, data = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

/**
 * Build the request headers, attaching a Bearer token when one is stored.
 *
 * TODO (auth): This function already handles the Authorization header.
 * When AuthService.login() stores a token, it will appear here
 * automatically — no changes needed.
 */
function buildHeaders(extraHeaders = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...extraHeaders,
  };

  const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  return headers;
}

/**
 * Parse a fetch Response into data or throw an ApiError.
 */
async function parseResponse(response) {
  let data = null;
  const contentType = response.headers.get("content-type") || "";

  if (contentType.includes("application/json")) {
    data = await response.json();
  } else {
    data = await response.text();
  }

  if (!response.ok) {
    // Extract a human-readable message from common DRF error shapes.
    const message =
      data?.detail ||
      data?.message ||
      (typeof data === "string" ? data : null) ||
      `Request failed with status ${response.status}`;

    // TODO (auth): On 401, if this is not a login endpoint, clear the
    // stored token and redirect to the login prompt.
    if (response.status === 401) {
      localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
      localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    }

    throw new ApiError(message, response.status, data);
  }

  return data;
}

/**
 * Core request function.
 * All service methods use this internally.
 */
async function request(path, { method = "GET", body, headers = {}, isFormData = false } = {}) {
  const url = `${API_BASE_URL}${path}`;

  const requestHeaders = isFormData
    ? // For FormData, let the browser set Content-Type with the boundary.
      (() => {
        const h = buildHeaders(headers);
        delete h["Content-Type"];
        return h;
      })()
    : buildHeaders(headers);

  const options = {
    method,
    headers: requestHeaders,
  };

  if (body !== undefined) {
    options.body = isFormData ? body : JSON.stringify(body);
  }

  const response = await fetch(url, options);
  return parseResponse(response);
}

/** Convenience wrappers */
export const api = {
  get: (path, options = {}) => request(path, { ...options, method: "GET" }),
  post: (path, body, options = {}) => request(path, { ...options, method: "POST", body }),
  postForm: (path, formData, options = {}) =>
    request(path, { ...options, method: "POST", body: formData, isFormData: true }),
};

export default api;
