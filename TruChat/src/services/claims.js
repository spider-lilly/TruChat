import api from "./api";

export const checkClaim = (claimText) =>
  api.post("/data/claims/check/", { claim_text: claimText });
