/**
 * HistoryService — User verification history API calls
 *
 * Wraps the backend endpoints:
 *   GET /api/history/          — paginated list of the user's past claims
 *   GET /api/history/counter/  — verdict counts for the authenticated user
 *
 * Both endpoints require authentication (IsAuthenticated permission class).
 * If the user is not authenticated, this service throws an AuthRequiredError
 * immediately — no HTTP request is made.
 *
 * TODO (auth): When login is implemented, tokens will be stored by AuthService
 * and AuthService.isAuthenticated() will return true. The history calls will
 * then work automatically — no changes needed in this file.
 */

import api from "./api.js";
import AuthService from "./auth.js";
import { mapVerdict, mapScore } from "./claims.js";

/**
 * Sentinel error class to distinguish "not logged in" from real API errors.
 * The UI checks instanceof AuthRequiredError to show the login prompt.
 */
export class AuthRequiredError extends Error {
  constructor() {
    super("Authentication required to view history.");
    this.name = "AuthRequiredError";
  }
}

/**
 * Map a history item from the backend serializer shape to a Verdict-like
 * object the extension UI can render.
 *
 * Backend shape (HistoryItemSerializer):
 *  { id, claim_text, verdict, credibility_score, explanation, created_at, status, ... }
 */
function normaliseHistoryItem(item) {
  const relativeTime = formatRelativeTime(item.created_at);
  return {
    id: item.id,
    claim: item.claim_text || item.normalized_claim || item.cleaned_claim || "—",
    status: mapVerdict(item.verdict),
    score: mapScore(item.credibility_score),
    time: relativeTime,
    summary: item.explanation || null,
    sources: [],
    region: undefined,
  };
}

/**
 * Convert an ISO datetime string to a human-readable relative label.
 * Falls back to the raw string if parsing fails.
 */
function formatRelativeTime(isoString) {
  if (!isoString) return "Unknown";
  try {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60_000);
    const diffHours = Math.floor(diffMs / 3_600_000);
    const diffDays = Math.floor(diffMs / 86_400_000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  } catch {
    return isoString;
  }
}

const HistoryService = {
  /**
   * Fetch the authenticated user's verification history.
   *
   * @param {object} [params]
   * @param {number} [params.page]   Page number (1-based).
   * @param {number} [params.limit]  Items per page (max 20 per backend).
   * @returns {Promise<{ results: Verdict[], total: number, hasNext: boolean, nextPage: number|null }>}
   * @throws {AuthRequiredError} If the user is not authenticated.
   */
  async getHistory({ page = 1, limit = 20 } = {}) {
    // Guard: do not hit the authenticated endpoint if there's no token.
    if (!AuthService.isAuthenticated()) {
      throw new AuthRequiredError();
    }

    const queryString = new URLSearchParams({
      page: String(page),
      limit: String(limit),
    }).toString();

    const raw = await api.get(`/history/?${queryString}`);

    return {
      results: (raw.results || []).map(normaliseHistoryItem),
      total: raw.total ?? 0,
      hasNext: raw.has_next ?? false,
      nextPage: raw.next_page ?? null,
      page: raw.page ?? page,
    };
  },

  /**
   * Fetch verdict counts for the authenticated user.
   *
   * @returns {Promise<{ total, completed, supports, refutes, notEnoughInfo }>}
   * @throws {AuthRequiredError} If the user is not authenticated.
   */
  async getCounter() {
    if (!AuthService.isAuthenticated()) {
      throw new AuthRequiredError();
    }

    const raw = await api.get("/history/counter/");

    return {
      total: raw.total ?? 0,
      completed: raw.completed ?? 0,
      processing: raw.processing ?? 0,
      failed: raw.failed ?? 0,
      // Map backend verdict names to the extension's naming convention.
      verified: raw.supports ?? 0,       // SUPPORTS → verified
      misleading: raw.refutes ?? 0,      // REFUTES  → misleading
      unverified: raw.not_enough_information ?? 0, // NEI → unverified
    };
  },
};

export default HistoryService;
