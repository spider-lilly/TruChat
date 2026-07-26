import { Link } from 'react-router-dom'

const buttonClassName =
  'block w-full border border-border bg-ink px-5 py-3 text-center font-body text-sm font-medium tracking-wide text-white transition-colors duration-200 hover:bg-hover disabled:cursor-not-allowed disabled:opacity-45'

export function PrimaryButton({
  children,
  onClick,
  disabled = false,
  type = 'button',
  to,
}) {
  if (to) {
    return (
      <Link to={to} className={buttonClassName}>
        {children}
      </Link>
    )
  }

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={buttonClassName}
    >
      {children}
    </button>
  )
}
