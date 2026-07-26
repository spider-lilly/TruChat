import { Newspaper } from 'lucide-react'

export function NewspaperHeadline({
  title = "Today's Headlines",
  items,
  className = '',
}) {
  return (
    <section className={className} aria-label={title}>
      <div className="mb-4 flex items-center gap-2 border-b border-border pb-2">
        <Newspaper className="h-4 w-4 text-accent" strokeWidth={1.5} aria-hidden="true" />
        <h3 className="font-editorial text-lg font-semibold uppercase tracking-wide text-ink">
          {title}
        </h3>
      </div>

      <ul className="columns-1 gap-8 sm:columns-2">
        {items.map((item) => (
          <li
            key={item.text}
            className="mb-3 break-inside-avoid font-body text-sm leading-relaxed text-ink"
          >
            <span className="mr-2 font-editorial text-accent" aria-hidden="true">
              ✓
            </span>
            {item.text}
            {item.comingSoon && (
              <span className="ml-1 font-editorial text-xs italic text-muted">
                (Coming Soon)
              </span>
            )}
          </li>
        ))}
      </ul>
    </section>
  )
}
