import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Lock, Mail, User } from 'lucide-react'
import { AuthCard } from '../ui/AuthCard.jsx'
import { AuthInput } from '../ui/AuthInput.jsx'
import { GoogleButton } from '../ui/GoogleButton.jsx'
import { NewspaperDivider } from '../ui/NewspaperDivider.jsx'
import { PrimaryButton } from '../ui/PrimaryButton.jsx'
import { useAuth } from '../../context/AuthContext'

export function SignUpCard() {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const navigate = useNavigate()
  const { register } = useAuth()

  const isFormValid = useMemo(() => {
    const trimmedUsername = username.trim()
    const trimmedEmail = email.trim()
    const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmedEmail)

    return (
      trimmedUsername.length > 0 &&
      emailValid &&
      password.length >= 6 &&
      password === confirmPassword
    )
  }, [username, email, password, confirmPassword])

  const handleGoogleSignUp = () => {
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";
    window.location.href = `${apiBaseUrl}/user/google/`;
  };

  const handleCreateAccount = async () => {
    if (!isFormValid || isSubmitting) return

    setErrorMessage("")
    setIsSubmitting(true)

    try {
      await register({
        username: username.trim(),
        email: email.trim(),
        password,
        role: "user",
      })

      navigate("/dashboard")
    } catch (error) {
      if (error.response?.data) {
        const data = error.response.data
        const firstError = Object.values(data)[0]

        if (Array.isArray(firstError)) {
          setErrorMessage(firstError[0])
        } else {
          setErrorMessage(String(firstError))
        }
      } else {
        setErrorMessage("Unable to create account.")
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <AuthCard
      edition="New Subscription"
      title="Join the Press"
      subtitle="Create your reader account to begin."
      footer={
        <p className="font-body text-sm text-muted">
          Already have an account?{' '}
          <Link
            to="/login"
            className="font-medium text-ink underline-offset-2 hover:underline"
          >
            Log In
          </Link>
        </p>
      }
    >
      <div className="space-y-4">
        <GoogleButton onClick={handleGoogleSignUp} />

        <NewspaperDivider label="Or" />

        <div className="space-y-4">
          <AuthInput
            id="signup-username"
            label="Username"
            placeholder="Choose a username"
            value={username}
            onChange={setUsername}
            icon={User}
            autoComplete="username"
          />

          <AuthInput
            id="signup-email"
            label="Email"
            type="email"
            placeholder="Enter your email address"
            value={email}
            onChange={setEmail}
            icon={Mail}
            autoComplete="email"
          />

          <AuthInput
            id="signup-password"
            label="Password"
            type="password"
            placeholder="Create a password"
            value={password}
            onChange={setPassword}
            icon={Lock}
            autoComplete="new-password"
          />

          <AuthInput
            id="signup-confirm-password"
            label="Confirm Password"
            type="password"
            placeholder="Re-enter your password"
            value={confirmPassword}
            onChange={setConfirmPassword}
            icon={Lock}
            autoComplete="new-password"
          />

          {confirmPassword.length > 0 && password !== confirmPassword && (
            <p className="font-body text-xs text-red-600">
              Passwords do not match.
            </p>
          )}

          {errorMessage && (
            <p className="font-body text-sm text-red-600">
              {errorMessage}
            </p>
          )}            

          <PrimaryButton onClick={handleCreateAccount} disabled={!isFormValid || isSubmitting}>
            {isSubmitting ? "Creating Account..." : "Create Account"}
          </PrimaryButton>
        </div>
      </div>
    </AuthCard>
  )
}
