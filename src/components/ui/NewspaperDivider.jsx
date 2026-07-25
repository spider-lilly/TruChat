export function NewspaperDivider({ label, className = '' }) {
  if (label) {
    return (
      <div className={`flex items-center gap-4 ${className}`}>
        <span className="h-px flex-1 bg-border" aria-hidden="true" />
        <span className="font-editorial text-xs uppercase tracking-[0.25em] text-muted">
          {label}
        </span>
        <span className="h-px flex-1 bg-border" aria-hidden="true" />
      </div>
    )
  }

  return <hr className={`border-0 border-t border-border ${className}`} />
}
