import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { Lock, User } from 'lucide-react'
import { AuthCard } from '../ui/AuthCard.jsx'
import { AuthInput } from '../ui/AuthInput.jsx'
import { GoogleButton } from '../ui/GoogleButton.jsx'
import { NewspaperDivider } from '../ui/NewspaperDivider.jsx'
import { PrimaryButton } from '../ui/PrimaryButton.jsx'
import { useNavigate } from "react-router-dom";
import { loginUser } from "../../services/auth";

export function LoginCard() {
  const [loginId, setLoginId] = useState('')
  const [password, setPassword] = useState('')

  const isFormValid = useMemo(
    () => loginId.trim().length > 0 && password.length >= 6,
    [loginId, password],
  )

  const handleGoogleSignIn = () => {
    window.location.href = "http://127.0.0.1:8000/api/user/google/";  
  };

  const handleSignIn = async () => {
  if (!isFormValid || isSubmitting) return;

  setIsSubmitting(true);
  setErrorMessage("");

  try {
    const response = await loginUser({
      email: loginId.trim(),
      password,
    });

    localStorage.setItem(
      "accessToken",
      response.data.access_token
    );

    localStorage.setItem(
      "refreshToken",
      response.data.refresh_token
    );

    navigate("/dashboard");
  } catch (error) {
    if (error.response?.data) {
      const data = error.response.data;
      const firstError = Object.values(data)[0];

      if (Array.isArray(firstError)) {
        setErrorMessage(firstError[0]);
      } else {
        setErrorMessage(String(firstError));
      }
    } else {
      setErrorMessage("Invalid email or password.");
    }
  }

  setIsSubmitting(false);
};

  const navigate = useNavigate();

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  return (
    <AuthCard
      edition="Special Edition"
      title="Edition Login"
      subtitle="Sign in to continue reading."
      footer={
        <p className="font-body text-sm text-muted">
          Don&apos;t have an account?{' '}
          <Link
            to="/signup"
            className="font-medium text-ink underline-offset-2 hover:underline"
          >
            Sign Up
          </Link>
        </p>
      }
    >
      <div className="space-y-4">
        <div className="space-y-4">
          <AuthInput
            id="login-id"
            label="Email Address"
            placeholder="Enter your email address"
            value={loginId}
            onChange={setLoginId}
            icon={User}
            autoComplete="email"
          />

          <div className="space-y-2">
            <AuthInput
              id="password"
              label="Password"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={setPassword}
              icon={Lock}
              autoComplete="current-password"
            />

            <div className="text-right">
              <Link
                to="/forgot-password"
                className="font-editorial text-sm text-muted underline-offset-2 transition-colors hover:text-ink hover:underline"
              >
                Forgot Password?
              </Link>
            </div>
          </div>

          {errorMessage && (
            <p className="font-body text-sm text-red-600">
              {errorMessage}
            </p>
          )}

          <PrimaryButton onClick={handleSignIn} disabled={!isFormValid || isSubmitting}>
            {isSubmitting ? "Signing In..." : "Sign In"}
          </PrimaryButton>
        </div>

        <NewspaperDivider label="Or" />

        <GoogleButton onClick={handleGoogleSignIn} />
      </div>
    </AuthCard>
  )
}
