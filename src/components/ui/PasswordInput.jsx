import { Eye, EyeOff } from 'lucide-react'
import { useState } from 'react'

export function PasswordInput({
  id,
  label,
  placeholder,
  value,
  onChange,
  icon: Icon,
  autoComplete,
  errors = [],
  showErrors = false,
}) {
  const [visible, setVisible] = useState(false)

  return (
    <div className="space-y-2">
      <label
        htmlFor={id}
        className="flex items-center gap-2 font-editorial text-sm font-medium text-ink"
      >
        {Icon && (
          <Icon className="h-4 w-4 text-muted" strokeWidth={1.5} aria-hidden="true" />
        )}
        {label}
      </label>

      <div className="relative">
        <input
          id={id}
          type={visible ? 'text' : 'password'}
          placeholder={placeholder}
          value={value}
          autoComplete={autoComplete}
          onChange={(event) => onChange(event.target.value)}
          className="w-full border border-border bg-paper py-2.5 pr-11 pl-3.5 font-body text-sm text-ink placeholder:text-muted/70 outline-none transition-colors focus:border-ink"
        />

        <button
          type="button"
          onClick={() => setVisible((current) => !current)}
          className="absolute top-1/2 right-3 -translate-y-1/2 text-muted transition-colors hover:text-ink"
          aria-label={visible ? 'Hide password' : 'Show password'}
        >
          {visible ? (
            <EyeOff className="h-4 w-4" strokeWidth={1.5} aria-hidden="true" />
          ) : (
            <Eye className="h-4 w-4" strokeWidth={1.5} aria-hidden="true" />
          )}
        </button>
      </div>

      {showErrors && errors.length > 0 && (
        <ul className="space-y-1">
          {errors.map((error) => (
            <li key={error} className="font-body text-xs text-accent">
              {error}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
