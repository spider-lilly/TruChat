import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Mail } from 'lucide-react'
import { forgotPassword } from "../../services/auth";
import { AuthCard } from '../ui/AuthCard.jsx'
import { AuthInput } from '../ui/AuthInput.jsx'
import { PrimaryButton } from '../ui/PrimaryButton.jsx'

export function ForgotPasswordCard() {
  const [email, setEmail] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')

  const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim());

  const handleSubmit = async () => {
  if (!emailValid || isSubmitting) return;

  setErrorMessage("");
  setIsSubmitting(true);

  try {
    await forgotPassword({
      email: email.trim(),
    });

    setSubmitted(true);
  } catch (error) {
    setErrorMessage(
      error.response?.data?.message ||
        "Unable to send reset link."
    );
  }

  setIsSubmitting(false);
};

  return (
    <AuthCard
      edition="Correspondence Desk"
      title="Forgot Your Password?"
      subtitle="Enter the email address associated with your TruChat account. We'll send you a secure password reset link."
      showTerms={false}
      footer={
        <p className="font-body text-sm text-muted">
          Remember your password?{' '}
          <Link
            to="/login"
            className="font-medium text-ink underline-offset-2 hover:underline"
          >
            Log In
          </Link>
        </p>
      }
    >
      {submitted ? (
        <div className="space-y-4 text-center">
          <p className="font-body text-sm leading-relaxed text-ink">
            If an account with that email exists, we&apos;ve sent a password reset
            link.
          </p>

          <Link
            to="/login"
            className="inline-block font-editorial text-sm text-muted underline-offset-2 transition-colors hover:text-ink hover:underline"
          >
            Return to Log In
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          <AuthInput
            id="forgot-email"
            label="Email Address"
            type="email"
            placeholder="Enter your email address"
            value={email}
            onChange={setEmail}
            icon={Mail}
            autoComplete="email"
          />

          {errorMessage && (
            <p className="font-body text-xs text-accent">{errorMessage}</p>
          )}

          <PrimaryButton
            onClick={handleSubmit}
            disabled={!emailValid || isSubmitting}
          >
            {isSubmitting ? 'Sending...' : 'Send Password Reset Link'}
          </PrimaryButton>
        </div>
      )}
    </AuthCard>
  )
}
