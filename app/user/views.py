# accounts/views.py

import os
import requests
import urllib.parse
import base64
import hashlib
import secrets
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.shortcuts import redirect
from urllib.parse import urlencode

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import User

from .serializers import (
    LoginSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer,
    ChangePasswordSerializer,
    RegisterSerializer,
    EmailSerializer,
    TokenValidationSerializer,
    ResetPasswordSerializer,
)


# Generate JWT tokens
def build_token_response(user):

    refresh = RefreshToken.for_user(user)

    access = refresh.access_token

    access["sub"] = str(user.id)
    access["role"] = user.role
    access["is_verified"] = user.is_verified

    return {
        "access_token": str(access),
        "refresh_token": str(refresh),
        "token_type": "bearer",
        "is_verified": user.is_verified,
    }


def get_user_from_token(uid, token):
    """Get the user only when Django's signed, expiring token is valid."""
    try:
        user = User.objects.get(pk=force_str(urlsafe_base64_decode(uid)))
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None
    return user if default_token_generator.check_token(user, token) else None


def send_account_email(user, subject, message):
    # Email delivery is configured by Django's email backend/environment.
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)


# Register API
class RegisterView(APIView):

    def post(self, request):

        serializer = RegisterSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        uid = urlsafe_base64_encode(str(user.pk).encode())
        token = default_token_generator.make_token(user)
        verification_url = (
            request.build_absolute_uri("/api/user/verify-email/")
            + f"?uid={uid}&token={token}"
        )
        send_account_email(
            user,
            "Verify your email address",
            f"Verify your email address by opening this link: {verification_url}",
        )

        return Response(
            build_token_response(user),
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(APIView):
    """Confirm a normal-registration email address."""

    def get(self, request):
        serializer = TokenValidationSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        user = get_user_from_token(**serializer.validated_data)
        if not user:
            return Response(
                {"detail": "Invalid or expired verification link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.is_verified:
            user.is_verified = True
            user.save(update_fields=["is_verified"])
        return Response({"detail": "Email verified successfully."})

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password changed successfully."},
            status=status.HTTP_200_OK,
        )

# Login API
class LoginView(APIView):

    def post(self, request):

        serializer = LoginSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        return Response(
            build_token_response(
                serializer.validated_data["user"]
            )
        )


class ForgotPasswordView(APIView):
    """Send a reset link without exposing whether an account exists."""

    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(
            email__iexact=serializer.validated_data["email"], is_active=True
        ).first()

        if user:
            uid = urlsafe_base64_encode(str(user.pk).encode())
            token = default_token_generator.make_token(user)
            FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

            reset_url = (
                f"{FRONTEND_URL}/reset-password"
                f"?uid={uid}&token={token}"
            )
            send_account_email(
                user,
                "Reset your password",
                f"Reset your password by opening this link: {reset_url}",
            )

        return Response({"detail": "If the email exists, a reset link has been sent."})


class ValidateResetTokenView(APIView):
    def post(self, request):
        serializer = TokenValidationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_user_from_token(**serializer.validated_data)
        if not user:
            return Response(
                {"valid": False, "detail": "Invalid or expired reset link."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"valid": True})


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_user_from_token(
            serializer.validated_data["uid"], serializer.validated_data["token"]
        )
        if not user:
            return Response(
                {"detail": "Invalid or expired reset link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(serializer.validated_data["new_password"], user)
        except DjangoValidationError as error:
            return Response(
                {"new_password": error.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])
        return Response({"detail": "Password reset successfully."})

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if refresh_token is None:
            return Response(
                {"error": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {"error": "Invalid refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)



# Profile API
class ProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = ProfileSerializer(
            request.user
        )

        return Response(serializer.data)

class ProfileUpdateView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request):

        serializer = ProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        if "email" in serializer.validated_data:
            uid = urlsafe_base64_encode(str(request.user.pk).encode())
            token = default_token_generator.make_token(request.user)
            verification_url = (
                request.build_absolute_uri("/api/user/verify-email/")
                + f"?uid={uid}&token={token}"
            )
            send_account_email(
                request.user,
                "Verify your new email address",
                f"Verify your email address by opening this link: {verification_url}",
            )

        return Response(serializer.data)

# Google login redirect
class GoogleLoginView(APIView):

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        client_id = os.getenv("GOOGLE_CLIENT_ID")

        if not client_id:
            return Response(
                {"detail": "Google OAuth is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        redirect_uri = os.getenv(
            "GOOGLE_REDIRECT_URI",
            "http://127.0.0.1:8000/api/user/google/callback/",
        )
        state = secrets.token_urlsafe(32)
        code_verifier = secrets.token_urlsafe(64)

        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).rstrip(b"=").decode()

        request.session["google_oauth_state"] = state
        request.session["google_code_verifier"] = code_verifier
        params = {
            "client_id": client_id,

            "redirect_uri":
            redirect_uri,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "response_type": "code",

            "scope": "openid email profile",

            "access_type": "offline",

            "prompt": "select_account",
        }

        url = (
            "https://accounts.google.com/o/oauth2/v2/auth?"
            + urllib.parse.urlencode(params)
        )

        return redirect(url)


# Google callback
from django.shortcuts import redirect
from urllib.parse import urlencode


class GoogleCallbackView(APIView):

    authentication_classes = []
    permission_classes = []

    def get(self, request):

        code = request.GET.get("code")
        received_state = request.GET.get("state")
        expected_state = request.session.pop("google_oauth_state", None)

        if not expected_state or not received_state:
            return Response(
                {"detail": "ERROR 1"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not secrets.compare_digest(received_state, expected_state):
            return Response(
                {"detail": "ERROR 2"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not code:
            return Response(
                {"detail": "ERROR 3"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        redirect_uri = os.getenv(
            "GOOGLE_REDIRECT_URI",
            "http://127.0.0.1:8000/api/user/google/callback/",
        )

        if not client_id or not client_secret:
            return Response(
                {"detail": "Google OAuth is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        code_verifier = request.session.pop("google_code_verifier", None)

        if not code_verifier:
            return Response(
                {"detail": "ERROR 4"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Exchange code for token
        try:
            token_response = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": client_id,
                    "code_verifier": code_verifier,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
                timeout=10,
            )
            token_response.raise_for_status()
        except requests.RequestException:
            return Response(
                {"detail": "Could not exchange Google authorization code."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        token_data = token_response.json()

        access_token = token_data.get("access_token")

        if not access_token:
            return Response(
                {"detail": "Google did not return an access token."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Fetch Google user info
        try:
            user_info_response = requests.get(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                headers={
                    "Authorization": f"Bearer {access_token}"
                },
                timeout=10,
            )
            user_info_response.raise_for_status()
        except requests.RequestException:
            return Response(
                {"detail": "Could not fetch Google user profile."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        user_info = user_info_response.json()

        email = user_info.get("email")

        if not email:
            return Response(
                {"detail": "Google profile did not include an email."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if not user_info.get("verified_email", False):
            return Response(
                {"detail": "Google email is not verified."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email.split("@")[0],
                "is_verified": True,
            },
        )

        if not user.is_verified:
            user.is_verified = True
            user.save(update_fields=["is_verified"])

        refresh = RefreshToken.for_user(user)

        params = urlencode({
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        })

        return redirect(
            f"http://localhost:5173/oauth-success?{params}"
        )