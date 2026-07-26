export function PaperBackground({ children, className = '' }) {
  return (
    <div className={`paper-texture min-h-svh ${className}`}>{children}</div>
  )
}
