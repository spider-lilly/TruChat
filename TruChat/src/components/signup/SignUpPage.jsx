import { AuthLayout } from '../auth/AuthLayout.jsx'
import { SignUpCard } from './SignUpCard.jsx'

export function SignUpPage() {
  return (
    <AuthLayout>
      <SignUpCard />
    </AuthLayout>
  )
}
