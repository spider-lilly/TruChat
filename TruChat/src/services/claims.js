import api from "./api";

export const processImage = (imageFile) => {
  const formData = new FormData();
  formData.append("image", imageFile);
  return api.post("/data/ocr/process/", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

export const checkClaim = (claimText, imageFile = null) => {
  if (imageFile) {
    const formData = new FormData();
    formData.append("image", imageFile);
    if (claimText) {
      formData.append("claim_text", claimText);
    }
    return api.post("/data/claims/check/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  }
  return api.post("/data/claims/check/", { claim_text: claimText });
};
