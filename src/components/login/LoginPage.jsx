import { AuthLayout } from '../auth/AuthLayout.jsx'
import { LoginCard } from './LoginCard.jsx'

export function LoginPage() {
  return (
    <AuthLayout>
      <LoginCard />
    </AuthLayout>
  )
}
