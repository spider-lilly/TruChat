export function AuthCard({
  edition,
  title,
  subtitle,
  children,
  footer,
  showTerms = true,
}) {
  return (
    <article className="animate-fade-in-delay w-full max-w-sm border border-border bg-paper px-5 py-6 shadow-[1px_1px_0_0_rgba(43,43,43,0.15)] sm:max-w-md sm:px-6 sm:py-7">
      <header className="mb-4 border-b border-border pb-4 text-center">
        <p className="font-editorial text-[10px] uppercase tracking-[0.35em] text-muted">
          {edition}
        </p>
        <h2 className="mt-1.5 font-masthead text-2xl font-bold text-ink sm:text-[1.75rem]">
          {title}
        </h2>
        <p className="mt-1.5 font-editorial text-sm italic text-muted">{subtitle}</p>
      </header>

      {children}

      {(footer || showTerms) && (
        <footer className="mt-5 space-y-3 border-t border-border pt-4 text-center">
          {footer}

          {showTerms && (
            <p className="font-body text-[11px] leading-relaxed text-muted">
              By continuing you agree to our{' '}
              <a href="#" className="text-ink underline-offset-2 hover:underline">
                Terms
              </a>{' '}
              &amp;{' '}
              <a href="#" className="text-ink underline-offset-2 hover:underline">
                Privacy Policy
              </a>
              .
            </p>
          )}
        </footer>
      )}
    </article>
  )
}
