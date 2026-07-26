export function AuthInput({
  id,
  label,
  type = 'text',
  placeholder,
  value,
  onChange,
  icon: Icon,
  autoComplete,
}) {
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

      <input
        id={id}
        type={type}
        placeholder={placeholder}
        value={value}
        autoComplete={autoComplete}
        onChange={(event) => onChange(event.target.value)}
        className="w-full border border-border bg-paper px-3.5 py-2.5 font-body text-sm text-ink placeholder:text-muted/70 outline-none transition-colors focus:border-ink"
      />
    </div>
  )
}
