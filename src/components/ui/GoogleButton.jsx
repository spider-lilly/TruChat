import { GoogleIcon } from './GoogleIcon.jsx'

export function GoogleButton({ onClick, className = '' }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex w-full items-center justify-center gap-3 border border-border bg-ink px-5 py-3 font-body text-sm font-medium tracking-wide text-white transition-colors duration-200 hover:bg-hover focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ink ${className}`}
    >
      <GoogleIcon />
      Continue with Google
    </button>
  )
}
