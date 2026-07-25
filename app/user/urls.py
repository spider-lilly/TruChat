# accounts/urls.py

from django.urls import path

from .views import (
    RegisterView,
    ChangePasswordView,
    LoginView,
    LogoutView,
    ProfileView,
    ProfileUpdateView,
    GoogleLoginView,
    GoogleCallbackView,
    VerifyEmailView,
    ForgotPasswordView,
    ValidateResetTokenView,
    ResetPasswordView,
    ResendVerificationView,
    DeleteAccountView,
)

urlpatterns = [

    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),
    path(
        "change-password/",
        ChangePasswordView.as_view(),
        name="change-password",
    ),
    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path(
        "resend-verification/",
        ResendVerificationView.as_view(),
        name="resend-verification",
    ),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path(
        "forgot-password/validate/",
        ValidateResetTokenView.as_view(),
        name="validate-reset-token",
    ),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
    path(
        "logout/",
        LogoutView.as_view(),
        name="logout",
    ),
    path("delete-account/", DeleteAccountView.as_view(), name="delete-account"),

    path(
        "profile/",
        ProfileView.as_view(),
        name="profile",
    ),

    path(
        "profile/update/",
        ProfileUpdateView.as_view(),
        name="profile-update",
    ),
    path(
        "google/",
        GoogleLoginView.as_view(),
        name="google-login",
    ),

    path(
        "google/callback/",
        GoogleCallbackView.as_view(),
        name="google-callback",
    ),
]
