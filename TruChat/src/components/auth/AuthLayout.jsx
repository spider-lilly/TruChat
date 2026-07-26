import { EditorialPanel } from '../login/EditorialPanel.jsx'
import { PaperBackground } from '../ui/PaperBackground.jsx'

export function AuthLayout({ children }) {
  return (
    <PaperBackground>
      <div className="mx-auto flex min-h-svh max-w-6xl flex-col lg:flex-row lg:items-center">
        <section className="border-b border-border lg:flex lg:w-[48%] lg:items-center lg:border-b-0 lg:border-r lg:py-6">
          <EditorialPanel />
        </section>

        <section className="animate-fade-in-delay-2 flex flex-1 items-center justify-center px-4 py-6 md:px-6 lg:w-[52%] lg:px-8 lg:py-6">
          {children}
        </section>
      </div>
    </PaperBackground>
  )
}
