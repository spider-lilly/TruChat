/**
 * ClaimsService — Claim verification API calls
 *
 * Wraps the backend endpoints:
 *   POST /api/data/claims/check/   — submit a text claim
 *   POST /api/data/ocr/process/    — extract text from an image
 *
 * Both endpoints work without authentication (the backend associates the claim
 * with the authenticated user if a token is present, but it accepts anonymous
 * requests too).
 *
 * The backend returns:
 *   { verdict: "SUPPORTS"|"REFUTES"|"NEI", credibility_score: float, explanation: string }
 *
 * This module maps that to the extension's internal Verdict shape so App.tsx
 * never has to know about the backend's naming conventions.
 */

import api, { ApiError } from "./api.js";

/**
 * Maps the backend verdict string to the extension's status convention.
 *
 * Backend  → Extension UI
 * SUPPORTS → "verified"
 * REFUTES  → "misleading"
 * NEI      → "unverified"  (Not Enough Information)
 */
export function mapVerdict(backendVerdict) {
  switch (backendVerdict) {
    case "SUPPORTS":
      return "verified";
    case "REFUTES":
      return "misleading";
    case "NEI":
    default:
      return "unverified";
  }
}

/**
 * Convert backend credibility_score (0.0 – 1.0 float) to an integer (0–100).
 */
export function mapScore(credibilityScore) {
  return Math.round((credibilityScore ?? 0) * 100);
}

/**
 * Normalise a raw backend response into the extension's Verdict shape.
 * Sources are not included in the claim-check response — the backend does
 * not return them at this endpoint. The UI falls back gracefully when
 * sources is undefined.
 */
export function normaliseClaimResponse(raw, claimText) {
  const status = mapVerdict(raw.verdict);
  const score = mapScore(raw.credibility_score);

  return {
    id: Date.now(),
    claim: claimText,
    status,
    score,
    time: "Just now",
    summary: raw.explanation || null,
    sources: [], // The /claims/check/ endpoint does not return sources.
    region: undefined, // Region detection falls back to client-side logic in App.tsx.
  };
}

/**
 * Format a user-friendly error message from an ApiError.
 */
export function formatClaimError(error) {
  if (error instanceof ApiError) {
    if (error.status === 429) {
      return "Too many requests. Please wait a moment and try again.";
    }
    if (error.status >= 500) {
      return "The verification service is temporarily unavailable. Please try again later.";
    }
    if (error.status === 400) {
      return error.message || "Invalid request. Please check your input.";
    }
    return error.message || "Verification failed. Please try again.";
  }

  // Network error (no status code)
  if (error.name === "TypeError") {
    return "Could not connect to the verification service. Check your internet connection.";
  }

  return "An unexpected error occurred. Please try again.";
}

const ClaimsService = {
  /**
   * Submit a text claim for fact-checking.
   *
   * @param {string} claimText  The claim to verify.
   * @returns {Promise<object>} Normalised Verdict object.
   */
  async checkClaim(claimText) {
    const raw = await api.post("/data/claims/check/", { claim_text: claimText });
    return normaliseClaimResponse(raw, claimText);
  },

  /**
   * Submit an image (or image + optional text hint) for fact-checking.
   * The backend will run OCR and then the fact-checking pipeline.
   *
   * @param {File}    imageFile  The uploaded image file.
   * @param {string}  [claimText]  Optional text hint alongside the image.
   * @returns {Promise<object>} Normalised Verdict object.
   */
  async checkClaimWithImage(imageFile, claimText = "") {
    const formData = new FormData();
    formData.append("image", imageFile);
    if (claimText) {
      formData.append("claim_text", claimText);
    }

    const raw = await api.postForm("/data/claims/check/", formData);
    return normaliseClaimResponse(raw, claimText || imageFile.name);
  },

  /**
   * Extract text from an uploaded image using the backend OCR endpoint.
   * Useful for processing article screenshots before submitting as a claim.
   *
   * @param {File} imageFile
   * @returns {Promise<object>} Raw OCR result from backend.
   */
  async extractTextFromImage(imageFile) {
    const formData = new FormData();
    formData.append("image", imageFile);
    return api.postForm("/data/ocr/process/", formData);
  },
};

export default ClaimsService;
