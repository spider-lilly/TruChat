import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Lock } from "lucide-react";

import {
  validateResetToken,
  resetPassword,
} from "../../services/auth";

import { AuthCard } from "../ui/AuthCard.jsx";
import { PasswordInput } from "../ui/PasswordInput.jsx";
import { PrimaryButton } from "../ui/PrimaryButton.jsx";

export function ResetPasswordCard() {
  const [searchParams] = useSearchParams();

  const uid = searchParams.get("uid");
  const token = searchParams.get("token");

  const [view, setView] = useState("loading");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [touched, setTouched] = useState({
    password: false,
    confirm: false,
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState("");

  const passwordValidation = useMemo(() => {
    const errors = [];

    if (!newPassword.trim()) {
      errors.push("Password is required.");
    }

    if (newPassword.length > 0 && newPassword.length < 8) {
      errors.push("Password must be at least 8 characters.");
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }, [newPassword]);

  const confirmErrors = useMemo(() => {
    const errors = [];

    if (!confirmPassword.trim()) {
      errors.push("Please confirm your password.");
    }

    if (
      confirmPassword &&
      newPassword &&
      confirmPassword !== newPassword
    ) {
      errors.push("Passwords do not match.");
    }

    return errors;
  }, [confirmPassword, newPassword]);

  const isFormValid =
    passwordValidation.isValid &&
    confirmErrors.length === 0;

  useEffect(() => {
    async function verifyToken() {
      if (!uid || !token) {
        setView("expired");
        return;
      }

      try {
        await validateResetToken({
          uid,
          token,
        });

        setView("form");
      } catch (error) {
        setSubmitError(
          error.response?.data?.detail ||
            "Invalid or expired reset link."
        );

        setView("expired");
      }
    }

    verifyToken();
  }, [uid, token]);

  const handleReset = async () => {
    setTouched({
      password: true,
      confirm: true,
    });

    if (!isFormValid || isSubmitting) return;

    setSubmitError("");
    setIsSubmitting(true);

    try {
      await resetPassword({
        uid,
        token,
        new_password: newPassword,
        confirm_password: confirmPassword,
      });

      setView("success");
    } catch (error) {
      if (error.response?.data) {
        const data = error.response.data;
        const firstError = Object.values(data)[0];

        setSubmitError(
          Array.isArray(firstError)
            ? firstError[0]
            : String(firstError)
        );
      } else {
        setSubmitError("Unable to reset password.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (view === "loading") {
    return (
      <AuthCard
        edition="Correspondence Desk"
        title="Verifying Reset Link"
        subtitle="Please wait while we verify your password reset link."
        showTerms={false}
      >
        <p className="text-center font-body text-sm text-muted">
          Verifying your secure link...
        </p>
      </AuthCard>
    );
  }

  if (view === "expired") {
    return (
      <AuthCard
        edition="Correspondence Desk"
        title="Reset Link Expired"
        subtitle="This password reset link is invalid or has expired."
        showTerms={false}
      >
        <div className="space-y-4">
          {submitError && (
            <p className="font-body text-xs text-accent">
              {submitError}
            </p>
          )}

          <Link to="/forgot-password">
            <PrimaryButton>
              Request New Reset Link
            </PrimaryButton>
          </Link>
        </div>
      </AuthCard>
    );
  }

  if (view === "success") {
    return (
      <AuthCard
        edition="Correspondence Desk"
        title="Password Updated"
        subtitle="Your password has been reset successfully."
        showTerms={false}
      >
        <Link to="/login">
          <PrimaryButton>
            Return to Login
          </PrimaryButton>
        </Link>
      </AuthCard>
    );
  }

  return (
    <AuthCard
      edition="Correspondence Desk"
      title="Create a New Password"
      subtitle="Enter a new password for your TruChat account."
      showTerms={false}
    >
      <div className="space-y-4">
        <PasswordInput
          id="new-password"
          label="New Password"
          placeholder="Enter your new password"
          value={newPassword}
          onChange={(value) => {
            setNewPassword(value);
            setTouched((current) => ({
              ...current,
              password: true,
            }));
          }}
          icon={Lock}
          autoComplete="new-password"
          errors={passwordValidation.errors}
          showErrors={touched.password}
        />

        <PasswordInput
          id="confirm-password"
          label="Confirm Password"
          placeholder="Re-enter your new password"
          value={confirmPassword}
          onChange={(value) => {
            setConfirmPassword(value);
            setTouched((current) => ({
              ...current,
              confirm: true,
            }));
          }}
          icon={Lock}
          autoComplete="new-password"
          errors={confirmErrors}
          showErrors={touched.confirm}
        />

        {submitError && (
          <p className="font-body text-xs text-accent">
            {submitError}
          </p>
        )}

        <PrimaryButton
          onClick={handleReset}
          disabled={!isFormValid || isSubmitting}
        >
          {isSubmitting
            ? "Resetting..."
            : "Reset Password"}
        </PrimaryButton>
      </div>
    </AuthCard>
  );
}