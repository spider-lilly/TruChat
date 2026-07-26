import api from "./api";

export const registerUser = (data) =>
  api.post("/user/register/", data);

export const loginUser = (data) =>
  api.post("/user/login/", data);

export const logoutUser = (refreshToken) =>
  api.post("/user/logout/", {
    refresh_token: refreshToken,
  });

export const getUserProfile = () =>
  api.get("/user/profile/");

export const updateUserProfile = (data) =>
  api.patch("/user/profile/update/", data);

export const changePassword = (data) =>
  api.post("/user/change-password/", data);

export const forgotPassword = (data) =>
  api.post("/user/forgot-password/", data);

export const validateResetToken = (data) =>
  api.post("/user/forgot-password/validate/", data);

export const resetPassword = (data) =>
  api.post("/user/reset-password/", data);

export const deleteAccount = (password) =>
  api.delete("/user/delete-account/", { data: { password } });
