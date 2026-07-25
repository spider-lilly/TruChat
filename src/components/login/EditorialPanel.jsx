import { Shield } from 'lucide-react'
import { NewspaperDivider } from '../ui/NewspaperDivider.jsx'
import { NewspaperHeadline } from '../ui/NewspaperHeadline.jsx'

const HEADLINE_ITEMS = [
  { text: 'AI Fact Checking' },
  { text: 'Trusted Sources' },
  { text: 'Explainable Results' },
  { text: 'Browser Extension', comingSoon: true },
]

export function EditorialPanel() {
  return (
    <aside className="animate-fade-in w-full px-5 py-6 md:px-8 lg:px-10 lg:py-4">
      <header className="text-center lg:text-left">
        <div className="mb-1.5 flex items-center justify-center gap-2 lg:justify-start">
          <Shield className="h-4 w-4 text-accent" strokeWidth={1.5} aria-hidden="true" />
          <p className="font-editorial text-[11px] uppercase tracking-[0.3em] text-muted">
            Est. 2026 · Independent Verification
          </p>
        </div>

        <h1 className="font-masthead text-4xl font-black uppercase leading-none tracking-tight text-ink sm:text-5xl lg:text-6xl">
          TruChat
        </h1>

        <p className="mt-2 font-editorial text-lg italic text-muted sm:text-xl">
          Daily Truth Verification
        </p>
      </header>

      <NewspaperDivider className="my-5" />

      <div className="mx-auto max-w-md space-y-3 text-center lg:mx-0 lg:text-left">
        <p className="font-editorial text-xl font-semibold leading-snug text-ink sm:text-2xl">
          Verify Before You Share.
        </p>

        <p className="font-body text-sm leading-relaxed text-muted">
          AI-powered news verification that compares your claims with trusted news
          sources and fact-checking organizations to provide transparent and
          explainable results.
        </p>
      </div>

      <div className="mt-5 border-t border-border pt-5 lg:mt-6">
        <NewspaperHeadline items={HEADLINE_ITEMS} />
      </div>
    </aside>
  )
}
