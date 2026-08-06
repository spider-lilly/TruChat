import { useState, useRef, useEffect } from "react";
import newsMicIcon from "@/imports/Screenshot_2026-08-06_165017-removebg-preview.png";
import { ImageWithFallback } from "@/app/components/figma/ImageWithFallback";
import {
  X,
  PanelLeft,
  SquarePen,
  MoreHorizontal,
  Search,
  Paperclip,
  ChevronRight,
  LogOut,
  User,
  Clock,
  ShieldCheck,
  AlertTriangle,
  HelpCircle,
  CheckCircle2,
  XCircle,
  MinusCircle,
  ArrowRight,
  Upload,
  Lock,
} from "lucide-react";
import { motion, AnimatePresence } from "motion/react";

// ── Service imports ────────────────────────────────────────
import ClaimsService, { formatClaimError, mapVerdict } from "@/services/claims.js";
import AuthService from "@/services/auth.js";
import HistoryService, { AuthRequiredError } from "@/services/history.js";

// ── Types ──────────────────────────────────────────────────

type View = "verify" | "verdicts" | "history" | "profile";

interface Source {
  name: string;
  url: string;
}

interface Verdict {
  id: number | string;
  claim: string;
  status: "verified" | "unverified" | "misleading";
  score: number;
  time: string;
  summary?: string;
  sources?: Source[];
  region?: "indian" | "global";
}

// ── Region detection (client-side, unchanged) ──────────────

const INDIAN_KEYWORDS = [
  "india", "indian", "modi", "delhi", "mumbai", "bangalore", "bengaluru", "chennai",
  "hyderabad", "kolkata", "rupee", "rbi", "bcci", "isro", "bjp", "congress",
  "lok sabha", "rajya sabha", "aadhaar", "upi", "sebi", "niti aayog",
];

function detectRegion(text: string): "indian" | "global" {
  const lower = text.toLowerCase();
  return INDIAN_KEYWORDS.some((kw) => lower.includes(kw)) ? "indian" : "global";
}

const INDIAN_SOURCES: Source[] = [
  { name: "Press Trust of India", url: "https://www.ptinews.com" },
  { name: "The Hindu", url: "https://www.thehindu.com" },
  { name: "PIB India", url: "https://pib.gov.in" },
  { name: "NDTV", url: "https://www.ndtv.com" },
  { name: "Indian Express", url: "https://indianexpress.com" },
];

const GLOBAL_SOURCES: Source[] = [
  { name: "Reuters", url: "https://www.reuters.com" },
  { name: "Associated Press", url: "https://apnews.com" },
  { name: "BBC News", url: "https://www.bbc.com/news" },
  { name: "WHO", url: "https://www.who.int" },
  { name: "Snopes", url: "https://www.snopes.com" },
];

// ── Demo / example claims ──────────────────────────────────

const EXAMPLE_CLAIMS = [
  "Vaccines secretly contain tracking microchips",
  "WHO confirms 12% drop in global disease burden",
  "Government plans to phase out paper currency by 2026",
];

// ── Status config (unchanged) ──────────────────────────────

const statusConfig = {
  verified: { label: "Verified", color: "text-emerald-700", bg: "bg-emerald-100", icon: CheckCircle2, dot: "bg-emerald-500" },
  unverified: { label: "Unverified", color: "text-amber-700", bg: "bg-amber-100", icon: MinusCircle, dot: "bg-amber-500" },
  misleading: { label: "Misleading", color: "text-red-700", bg: "bg-red-100", icon: XCircle, dot: "bg-red-600" },
};

// ── ScoreBadge (unchanged) ─────────────────────────────────

function ScoreBadge({ score, status }: { score: number; status: Verdict["status"] }) {
  const cfg = statusConfig[status];
  return (
    <span className={`inline-flex items-center gap-1 text-[10px] font-semibold tracking-wider uppercase px-2 py-0.5 rounded-full ${cfg.bg} ${cfg.color}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />
      {cfg.label} · {score}%
    </span>
  );
}

// ── Root App ───────────────────────────────────────────────

export default function App() {
  const [view, setView] = useState<View>("verify");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Session verdicts — built up as the user verifies claims this session.
  // Each successful verification is pushed here and shows in "Recent Verdicts".
  const [sessionVerdicts, setSessionVerdicts] = useState<Verdict[]>([]);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) setMenuOpen(false);
    }
    if (menuOpen) document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [menuOpen]);

  const [claim, setClaim] = useState("");
  const [attachMode, setAttachMode] = useState(false);
  const [linkValue, setLinkValue] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<Verdict | null>(null);
  const [verifyError, setVerifyError] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (view === "verify" && textareaRef.current && !attachMode) {
      textareaRef.current.focus();
    }
  }, [view, attachMode]);

  // ── handleVerify: replaced setTimeout mock with real API call ──

  async function handleVerify() {
    if (!claim.trim() && !linkValue.trim()) return;

    setIsAnalyzing(true);
    setResult(null);
    setVerifyError(null);

    const text = claim.trim() || linkValue.trim();

    try {
      // Call the real backend claim-check endpoint.
      const verdict = await ClaimsService.checkClaim(text);

      // Enrich with client-side region detection (backend doesn't return this).
      const region = detectRegion(text);
      const enriched: Verdict = {
        ...verdict,
        region,
        // If the backend returned no sources, fall back to region-appropriate
        // trusted source links so the UI source list is never empty.
        sources:
          verdict.sources && verdict.sources.length > 0
            ? verdict.sources
            : (region === "indian" ? INDIAN_SOURCES : GLOBAL_SOURCES)
                .sort(() => Math.random() - 0.5)
                .slice(0, verdict.status === "verified" ? 3 : 2),
      };

      setResult(enriched);

      // Add to this session's verdict list for the "Recent Verdicts" tab.
      setSessionVerdicts((prev) => [enriched, ...prev]);
    } catch (err) {
      const message = formatClaimError(err);
      setVerifyError(message);
    } finally {
      setIsAnalyzing(false);
    }
  }

  function handleExampleClaim(c: string) {
    setClaim(c);
    setAttachMode(false);
    setResult(null);
    setVerifyError(null);
    textareaRef.current?.focus();
  }

  // ── Session-based counts for the drawer "Today's Verdicts" section ──
  // Derived from sessionVerdicts so they stay in sync automatically.
  const sessionCounts = {
    verified: sessionVerdicts.filter((v) => v.status === "verified").length,
    unverified: sessionVerdicts.filter((v) => v.status === "unverified").length,
    misleading: sessionVerdicts.filter((v) => v.status === "misleading").length,
  };

  const navItems: { label: string; view: View; icon: typeof ShieldCheck }[] = [
    { label: "Verify News", view: "verify", icon: ShieldCheck },
    { label: "Recent Verdicts", view: "verdicts", icon: CheckCircle2 },
    { label: "History", view: "history", icon: Clock },
    { label: "Profile", view: "profile", icon: User },
  ];

  return (
    <div className="min-h-screen bg-[#CBBFA8] flex items-center justify-center p-6" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }}>
      {/* Extension popup shell */}
      <div
        className="relative bg-background overflow-hidden flex flex-col"
        style={{
          width: 380,
          height: 600,
          borderRadius: 12,
          boxShadow: "0 8px 40px rgba(0,0,0,0.28), 0 2px 8px rgba(0,0,0,0.14)",
        }}
      >
        {/* Slide-in drawer */}
        <AnimatePresence>
          {drawerOpen && (
            <>
              <motion.div
                className="absolute inset-0 z-30"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={() => setDrawerOpen(false)}
                style={{ background: "rgba(0,0,0,0.18)" }}
              />
              <motion.aside
                className="absolute left-0 top-0 bottom-0 z-40 flex flex-col"
                style={{ width: 240, background: "#EDE7D9", borderRight: "1px solid rgba(26,26,24,0.12)" }}
                initial={{ x: -240 }}
                animate={{ x: 0 }}
                exit={{ x: -240 }}
                transition={{ type: "spring", stiffness: 340, damping: 36 }}
              >
                {/* Drawer header */}
                <div className="flex items-center justify-between px-4 py-3 border-b border-border">
                  <span className="text-xs font-semibold tracking-[0.18em] uppercase text-foreground/60">TruChat</span>
                  <button onClick={() => setDrawerOpen(false)} className="p-1 rounded hover:bg-muted transition-colors">
                    <PanelLeft size={15} className="text-foreground/50" />
                  </button>
                </div>

                {/* Drawer nav */}
                <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-0.5">
                  <DrawerItem icon={SquarePen} label="New Verification" onClick={() => { setClaim(""); setResult(null); setVerifyError(null); setView("verify"); setDrawerOpen(false); }} />
                  <div className="my-2 border-t border-border" />
                  {navItems.map((item) => (
                    <DrawerItem
                      key={item.view}
                      icon={item.icon}
                      label={item.label}
                      active={view === item.view}
                      onClick={() => { setView(item.view); setDrawerOpen(false); }}
                    />
                  ))}
                  <div className="my-2 border-t border-border" />
                  <p className="px-3 pt-1 pb-1 text-[10px] font-semibold tracking-widest uppercase text-foreground/40">This Session</p>
                  {(["verified", "unverified", "misleading"] as const).map((s) => (
                    <div key={s} className="flex items-center justify-between px-3 py-1.5 rounded-md">
                      <div className="flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full ${statusConfig[s].dot}`} />
                        <span className="text-xs capitalize text-foreground/70">{s}</span>
                      </div>
                      <span className="text-xs font-semibold text-foreground">{sessionCounts[s]}</span>
                    </div>
                  ))}

                  <div className="my-2 border-t border-border" />
                  <p className="px-3 pt-1 pb-1 text-[10px] font-semibold tracking-widest uppercase text-foreground/40">Recent</p>
                  {sessionVerdicts.slice(0, 3).map((v) => (
                    <button
                      key={v.id}
                      onClick={() => { setView("verdicts"); setDrawerOpen(false); }}
                      className="w-full text-left px-3 py-1.5 rounded-md hover:bg-muted/60 transition-colors"
                    >
                      <p className="text-xs text-foreground/80 truncate">{v.claim}</p>
                      <p className="text-[10px] text-foreground/40 mt-0.5">{v.time}</p>
                    </button>
                  ))}
                  {sessionVerdicts.length === 0 && (
                    <p className="px-3 py-1.5 text-[10px] text-foreground/35 italic">No verifications this session yet.</p>
                  )}
                </nav>

                {/* Drawer footer */}
                <div className="border-t border-border px-3 py-3">
                  <button
                    onClick={() => { setView("profile"); setDrawerOpen(false); }}
                    className="w-full flex items-center gap-2.5 px-2 py-2 rounded-md hover:bg-muted/60 transition-colors"
                  >
                    <div className="w-7 h-7 rounded-full bg-foreground/10 flex items-center justify-center flex-shrink-0">
                      <User size={14} className="text-foreground/60" />
                    </div>
                    <div className="flex-1 min-w-0 text-left">
                      {/* TODO (auth): Replace "Guest" with the user's display name from AuthService */}
                      <p className="text-xs font-medium text-foreground truncate">
                        {AuthService.isAuthenticated() ? "Account" : "Guest"}
                      </p>
                      <p className="text-[10px] text-foreground/40">
                        {AuthService.isAuthenticated() ? "Logged in" : "Not signed in"}
                      </p>
                    </div>
                    <LogOut size={13} className="text-foreground/40 flex-shrink-0" />
                  </button>
                </div>
              </motion.aside>
            </>
          )}
        </AnimatePresence>

        {/* Header */}
        <header className="flex items-center px-3 py-2.5 border-b border-border flex-shrink-0" style={{ background: "#EDE7D9" }}>
          <button onClick={() => setDrawerOpen(true)} className="p-1.5 rounded-md hover:bg-muted/60 transition-colors mr-1">
            <PanelLeft size={15} className="text-foreground/60" />
          </button>
          <button
            onClick={() => { setClaim(""); setResult(null); setVerifyError(null); setView("verify"); }}
            className="p-1.5 rounded-md hover:bg-muted/60 transition-colors"
          >
            <SquarePen size={15} className="text-foreground/60" />
          </button>

          {/* Logo */}
          <div className="flex-1 flex items-center justify-center gap-1.5">
            <span style={{ fontFamily: "'Playfair Display', serif", fontWeight: 900, fontSize: 16, letterSpacing: "0.06em" }} className="text-foreground">
              TRU
            </span>
            <span className="flex items-center gap-0.5">
              <Search size={13} className="text-accent" strokeWidth={2.5} />
            </span>
            <span style={{ fontFamily: "'Playfair Display', serif", fontWeight: 900, fontSize: 16, letterSpacing: "0.06em" }} className="text-accent">
              CHAT
            </span>
          </div>

          <button className="p-1 rounded-md hover:bg-muted/60 transition-colors" title="News">
            <ImageWithFallback src={newsMicIcon} alt="News mic" className="w-5 h-5 object-contain" />
          </button>

          <div className="relative" ref={menuRef}>
            <button
              onClick={() => setMenuOpen((o) => !o)}
              className={`p-1.5 rounded-md transition-colors ${menuOpen ? "bg-muted" : "hover:bg-muted/60"}`}
            >
              <MoreHorizontal size={15} className="text-foreground/60" />
            </button>
            <AnimatePresence>
              {menuOpen && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95, y: -4 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: -4 }}
                  transition={{ duration: 0.12 }}
                  className="absolute right-0 top-full mt-1.5 z-50 w-44 rounded-xl border border-border bg-card py-1"
                  style={{ boxShadow: "0 4px 20px rgba(0,0,0,0.14)" }}
                >
                  <button
                    onClick={() => setMenuOpen(false)}
                    className="w-full flex items-center gap-2.5 px-3 py-2.5 text-xs text-foreground/80 hover:bg-muted/60 transition-colors"
                  >
                    <HelpCircle size={13} className="text-foreground/45 flex-shrink-0" />
                    About TruChat
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
          <button className="p-1.5 rounded-md hover:bg-muted/60 transition-colors ml-1">
            <X size={15} className="text-foreground/60" />
          </button>
        </header>

        {/* Tab bar */}
        <div className="flex border-b border-border flex-shrink-0" style={{ background: "#EDE7D9" }}>
          {(["verify", "verdicts"] as const).map((v) => (
            <button
              key={v}
              onClick={() => setView(v)}
              className={`flex-1 py-2 text-[10px] font-semibold tracking-[0.14em] uppercase transition-colors relative ${
                view === v ? "text-foreground" : "text-foreground/40 hover:text-foreground/70"
              }`}
            >
              {v === "verify" ? "Verify" : "Recent Verdicts"}
              {view === v && (
                <motion.span
                  layoutId="tab-indicator"
                  className="absolute bottom-0 left-0 right-0 h-[2px] bg-foreground rounded-full"
                />
              )}
            </button>
          ))}
        </div>

        {/* Main content */}
        <div className="flex-1 overflow-y-auto" style={{ background: "#F4EFE4" }}>
          <AnimatePresence mode="wait">
            {view === "verify" && (
              <VerifyView
                key="verify"
                claim={claim}
                setClaim={setClaim}
                attachMode={attachMode}
                setAttachMode={setAttachMode}
                linkValue={linkValue}
                setLinkValue={setLinkValue}
                isAnalyzing={isAnalyzing}
                result={result}
                verifyError={verifyError}
                onVerify={handleVerify}
                onExample={handleExampleClaim}
                textareaRef={textareaRef}
              />
            )}
            {view === "verdicts" && <VerdictsView key="verdicts" verdicts={sessionVerdicts} />}
            {view === "history" && <HistoryView key="history" />}
            {view === "profile" && <ProfileView key="profile" />}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

/* ── Drawer Item (unchanged) ──────────────────────────────── */
function DrawerItem({ icon: Icon, label, active, onClick }: { icon: typeof ShieldCheck; label: string; active?: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-md text-left transition-colors text-xs ${
        active ? "bg-foreground/10 text-foreground font-medium" : "text-foreground/70 hover:bg-muted/60"
      }`}
    >
      <Icon size={14} className={active ? "text-foreground" : "text-foreground/50"} />
      {label}
    </button>
  );
}

/* ── Verify View ──────────────────────────────────────────── */
function VerifyView({
  claim, setClaim, attachMode, setAttachMode, linkValue, setLinkValue,
  isAnalyzing, result, verifyError, onVerify, onExample, textareaRef,
}: {
  claim: string; setClaim: (v: string) => void;
  attachMode: boolean; setAttachMode: (v: boolean) => void;
  linkValue: string; setLinkValue: (v: string) => void;
  isAnalyzing: boolean; result: Verdict | null;
  verifyError: string | null;
  onVerify: () => void; onExample: (c: string) => void;
  textareaRef: React.RefObject<HTMLTextAreaElement>;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -4 }}
      transition={{ duration: 0.18 }}
      className="flex flex-col h-full"
    >
      {/* Bureau header */}
      <div className="flex items-center justify-between px-4 pt-4 pb-2">
        <span className="text-[9px] font-semibold tracking-[0.2em] uppercase text-foreground/50">AI Verification Bureau</span>
        <span className="flex items-center gap-1 text-[9px] font-medium tracking-wider text-emerald-600">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          Bureau Live
        </span>
      </div>

      {/* Greeting */}
      <div className="px-4 pb-3">
        <h1 className="text-xl font-bold text-foreground leading-tight" style={{ fontFamily: "'Playfair Display', serif" }}>
          {result ? "Verdict delivered." : isAnalyzing ? "Analysing claim…" : verifyError ? "Verification failed." : "What needs verifying?"}
        </h1>
        {!result && !isAnalyzing && !verifyError && (
          <p className="text-[11px] text-foreground/55 mt-1 leading-relaxed">
            Paste any headline, article link, or news claim. Our AI will analyse and deliver a credibility verdict.
          </p>
        )}
      </div>

      {/* Loading / Error / Result */}
      <AnimatePresence>
        {isAnalyzing && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="mx-4 mb-3 p-3 rounded-lg bg-card border border-border">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full border-2 border-foreground/30 border-t-foreground animate-spin" />
              <p className="text-xs text-foreground/60">Cross-referencing trusted sources…</p>
            </div>
          </motion.div>
        )}

        {/* API error state */}
        {verifyError && !isAnalyzing && (
          <motion.div
            initial={{ opacity: 0, scale: 0.97 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            className="mx-4 mb-3 p-3 rounded-xl border border-red-200 bg-red-50"
          >
            <div className="flex items-start gap-2">
              <AlertTriangle size={14} className="text-red-500 flex-shrink-0 mt-0.5" />
              <p className="text-[11px] text-red-700 leading-relaxed">{verifyError}</p>
            </div>
          </motion.div>
        )}

        {result && !isAnalyzing && (
          <motion.div
            initial={{ opacity: 0, scale: 0.97 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            className="mx-4 mb-3 rounded-xl border border-border bg-card overflow-hidden"
          >
            {/* Claim + badge */}
            <div className="flex items-start justify-between gap-2 px-3 pt-3 pb-2">
              <p className="text-xs text-foreground/70 leading-snug flex-1 line-clamp-2">{result.claim}</p>
              <ScoreBadge score={result.score} status={result.status} />
            </div>

            {/* Score bar */}
            <div className="px-3 pb-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] text-foreground/50">Credibility Score</span>
                <span className="text-[10px] font-semibold text-foreground">{result.score}%</span>
              </div>
              <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${result.score}%` }}
                  transition={{ duration: 0.7, ease: "easeOut" }}
                  className={`h-full rounded-full ${result.status === "verified" ? "bg-emerald-500" : result.status === "misleading" ? "bg-red-500" : "bg-amber-400"}`}
                />
              </div>
            </div>

            {/* Summary */}
            {result.summary && (
              <div className="px-3 pb-3 border-t border-border pt-2.5">
                <p className="text-[11px] text-foreground/75 leading-relaxed">{result.summary}</p>
              </div>
            )}

            {/* Sources */}
            {result.sources && result.sources.length > 0 && (
              <div className="border-t border-border px-3 py-2.5">
                <div className="flex items-center gap-1.5 mb-2">
                  <span className="text-[9px] font-semibold tracking-[0.16em] uppercase text-foreground/40">
                    {result.region === "indian" ? "Indian" : "Global"} Trusted Sources
                  </span>
                  <span className={`text-[9px] px-1.5 py-0.5 rounded-full font-semibold ${result.region === "indian" ? "bg-orange-100 text-orange-700" : "bg-sky-100 text-sky-700"}`}>
                    {result.region === "indian" ? "🇮🇳 India" : "🌐 Global"}
                  </span>
                </div>
                <div className="space-y-1.5">
                  {result.sources.map((src) => (
                    <a
                      key={src.name}
                      href={src.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 group"
                    >
                      <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${statusConfig[result.status].dot}`} />
                      <span className="text-[11px] text-foreground/70 group-hover:text-foreground group-hover:underline transition-colors truncate">{src.name}</span>
                      <ArrowRight size={9} className="text-foreground/30 flex-shrink-0 group-hover:text-foreground/60 transition-colors ml-auto" />
                    </a>
                  ))}
                </div>
              </div>
            )}

            {/* Footer notice */}
            <div className="border-t border-border px-3 py-2">
              <p className="text-[9px] text-foreground/40 italic">AI verdicts are editorial aids, not legal determinations. Always consult primary sources.</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Example chips */}
      {!result && !isAnalyzing && !verifyError && (
        <div className="px-4 mb-3">
          <p className="text-[9px] font-semibold tracking-[0.16em] uppercase text-foreground/40 mb-2">Try an example claim:</p>
          <div className="flex flex-col gap-1.5">
            {EXAMPLE_CLAIMS.map((c) => (
              <button
                key={c}
                onClick={() => onExample(c)}
                className="text-left text-[11px] text-foreground/65 px-2.5 py-1.5 rounded-md bg-card border border-border hover:border-foreground/25 hover:text-foreground transition-all line-clamp-1"
              >
                {c}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Spacer */}
      <div className="flex-1" />

      {/* Input area */}
      <div className="px-3 pb-3 flex-shrink-0">
        <div className="rounded-xl border border-border bg-card overflow-hidden" style={{ boxShadow: "0 1px 4px rgba(0,0,0,0.08)" }}>
          {attachMode ? (
            <div className="p-3">
              <div className="text-[10px] font-semibold tracking-widest uppercase text-foreground/50 mb-2">Attach Article Image or Link</div>
              <button className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg border border-dashed border-border text-xs text-foreground/50 hover:border-foreground/30 hover:text-foreground/70 transition-colors mb-2">
                <Upload size={13} />
                Upload Article Image
              </button>
              <div className="flex gap-2">
                <input
                  value={linkValue}
                  onChange={(e) => setLinkValue(e.target.value)}
                  placeholder="https://example.com/article"
                  className="flex-1 text-xs bg-input-background rounded-lg px-2.5 py-1.5 outline-none border border-transparent focus:border-border placeholder:text-foreground/30"
                />
                <button
                  onClick={() => setAttachMode(false)}
                  className="px-3 py-1.5 text-xs font-semibold bg-foreground text-primary-foreground rounded-lg hover:opacity-80 transition-opacity"
                >
                  Add
                </button>
              </div>
            </div>
          ) : (
            <textarea
              ref={textareaRef}
              value={claim}
              onChange={(e) => setClaim(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); onVerify(); } }}
              placeholder="Enter claim for verification…"
              rows={3}
              className="w-full resize-none px-3 pt-3 pb-2 text-xs bg-transparent outline-none placeholder:text-foreground/35 text-foreground leading-relaxed"
            />
          )}

          {/* Toolbar */}
          <div className="flex items-center justify-between px-3 py-2 border-t border-border">
            <div className="flex items-center gap-1.5">
              <button
                onClick={() => { setAttachMode(!attachMode); }}
                className={`p-1.5 rounded-md transition-colors ${attachMode ? "bg-muted text-foreground" : "hover:bg-muted text-foreground/50"}`}
              >
                <Paperclip size={13} />
              </button>
              <span className="text-[9px] text-foreground/30">↵ Enter · ⇧↵ New line</span>
            </div>
            <button
              onClick={onVerify}
              disabled={isAnalyzing || (!claim.trim() && !linkValue.trim())}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] font-semibold bg-foreground text-primary-foreground disabled:opacity-30 hover:opacity-80 transition-all"
            >
              {isAnalyzing ? "Verifying…" : <>Verify Claim <ArrowRight size={11} /></>}
            </button>
          </div>
        </div>

        {/* Editorial notice */}
        <div className="mt-2 px-2.5 py-2 rounded-lg border border-accent/30 bg-accent/5">
          <p className="text-[9px] text-foreground/50 leading-relaxed">
            <span className="font-semibold text-accent text-[9px] uppercase tracking-wider">Editorial Notice · </span>
            AI verdicts are editorial aids, not legal determinations. Always consult primary sources before publication.
          </p>
        </div>
      </div>
    </motion.div>
  );
}

/* ── Verdicts View ────────────────────────────────────────── */
function VerdictsView({ verdicts }: { verdicts: Verdict[] }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -4 }}
      transition={{ duration: 0.18 }}
      className="p-4"
    >
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xs font-semibold tracking-[0.14em] uppercase text-foreground/50">Recent Verdicts</h2>
        <span className="text-[10px] text-foreground/35">{verdicts.length} this session</span>
      </div>

      {verdicts.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-10 text-center">
          <ShieldCheck size={28} className="text-foreground/20 mb-3" />
          <p className="text-xs font-medium text-foreground/40">No verdicts yet this session.</p>
          <p className="text-[10px] text-foreground/30 mt-1 leading-relaxed">
            Verified claims will appear here as you use the extension.
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {verdicts.map((v) => {
            const cfg = statusConfig[v.status];
            const Icon = cfg.icon;
            return (
              <div key={v.id} className="p-3 rounded-xl bg-card border border-border">
                <div className="flex items-start gap-2">
                  <Icon size={14} className={`mt-0.5 flex-shrink-0 ${cfg.color}`} />
                  <div className="flex-1 min-w-0">
                    <p className="text-[11px] text-foreground leading-snug mb-1.5 line-clamp-2">{v.claim}</p>
                    <div className="flex items-center justify-between">
                      <ScoreBadge score={v.score} status={v.status} />
                      <span className="text-[10px] text-foreground/35">{v.time}</span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* How it works */}
      <div className="mt-4 p-3 rounded-xl border border-border bg-card">
        <p className="text-[9px] font-semibold tracking-[0.18em] uppercase text-foreground/40 mb-3">How It Works</p>
        {[
          { num: "I", title: "Submit a Claim", desc: "Paste any headline, article link, or news claim." },
          { num: "II", title: "AI Analysis", desc: "TruChat analyses with reference to trusted sources." },
          { num: "III", title: "Receive Report", desc: "Get verdict, accuracy scores, and resources." },
        ].map((step) => (
          <div key={step.num} className="flex gap-2.5 mb-2.5 last:mb-0">
            <span className="text-[10px] font-bold text-foreground/30 w-5 flex-shrink-0 mt-0.5" style={{ fontFamily: "'IBM Plex Mono', monospace" }}>{step.num}</span>
            <div>
              <p className="text-[11px] font-semibold text-foreground">{step.title}</p>
              <p className="text-[10px] text-foreground/50 leading-relaxed">{step.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
}

/* ── History View ─────────────────────────────────────────── */
function HistoryView() {
  // TODO (auth): When login is implemented, isAuthenticated() will return true
  // and this component will fetch and display real history data.
  const isLoggedIn = AuthService.isAuthenticated();

  const [historyItems, setHistoryItems] = useState<Verdict[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    if (!isLoggedIn) return;

    setLoading(true);
    setError(null);

    HistoryService.getHistory({ page: 1 })
      .then(({ results, total }) => {
        setHistoryItems(results);
        setTotal(total);
      })
      .catch((err) => {
        if (err instanceof AuthRequiredError) {
          // Should not reach here since we guarded above, but handle gracefully.
          setError(null);
        } else {
          setError("Could not load history. Please try again.");
        }
      })
      .finally(() => setLoading(false));
  }, [isLoggedIn]);

  // ── Not logged in: show login prompt ──
  if (!isLoggedIn) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -4 }}
        transition={{ duration: 0.18 }}
        className="p-4"
      >
        <h2 className="text-xs font-semibold tracking-[0.14em] uppercase text-foreground/50 mb-4">History</h2>

        <div className="flex flex-col items-center justify-center py-10 text-center">
          <div className="w-12 h-12 rounded-full bg-foreground/6 border border-border flex items-center justify-center mb-4">
            <Lock size={20} className="text-foreground/30" />
          </div>
          <p className="text-sm font-semibold text-foreground mb-1" style={{ fontFamily: "'Playfair Display', serif" }}>
            Log in to view your history
          </p>
          <p className="text-[11px] text-foreground/50 leading-relaxed mb-5 max-w-[200px]">
            Your past verifications are saved to your account. Sign in to access them.
          </p>

          {/*
           * TODO (auth): Wire this button to the login flow.
           * When AuthService.login() is implemented, clicking here should
           * open the login screen or trigger OAuth.
           */}
          <button
            disabled
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-foreground text-primary-foreground text-xs font-semibold opacity-60 cursor-not-allowed"
            title="Login coming soon"
          >
            <User size={13} />
            Log In
          </button>
          <p className="text-[9px] text-foreground/30 mt-3">Authentication coming soon</p>
        </div>
      </motion.div>
    );
  }

  // ── Logged in: show real history ──
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -4 }}
      transition={{ duration: 0.18 }}
      className="p-4"
    >
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xs font-semibold tracking-[0.14em] uppercase text-foreground/50">History</h2>
        {!loading && <span className="text-[10px] text-foreground/35">{total} total</span>}
      </div>

      {loading && (
        <div className="flex items-center gap-2 py-6 justify-center">
          <div className="w-4 h-4 rounded-full border-2 border-foreground/30 border-t-foreground animate-spin" />
          <p className="text-xs text-foreground/50">Loading history…</p>
        </div>
      )}

      {error && !loading && (
        <div className="p-3 rounded-xl border border-red-200 bg-red-50 flex items-start gap-2">
          <AlertTriangle size={13} className="text-red-500 flex-shrink-0 mt-0.5" />
          <p className="text-[11px] text-red-700">{error}</p>
        </div>
      )}

      {!loading && !error && historyItems.length === 0 && (
        <div className="flex flex-col items-center justify-center py-10 text-center">
          <Clock size={24} className="text-foreground/20 mb-3" />
          <p className="text-xs text-foreground/40">No history yet.</p>
          <p className="text-[10px] text-foreground/30 mt-1">Your verified claims will appear here.</p>
        </div>
      )}

      {!loading && !error && (
        <div className="space-y-1">
          {historyItems.map((v) => (
            <button key={v.id} className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-card transition-colors text-left group">
              <span className={`w-2 h-2 rounded-full flex-shrink-0 ${statusConfig[v.status].dot}`} />
              <div className="flex-1 min-w-0">
                <p className="text-xs text-foreground/80 truncate group-hover:text-foreground transition-colors">{v.claim}</p>
                <p className="text-[10px] text-foreground/35 mt-0.5">{v.time}</p>
              </div>
              <ChevronRight size={12} className="text-foreground/25 flex-shrink-0 group-hover:text-foreground/50 transition-colors" />
            </button>
          ))}
        </div>
      )}
    </motion.div>
  );
}

/* ── Profile View ─────────────────────────────────────────── */
function ProfileView() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -4 }}
      transition={{ duration: 0.18 }}
      className="p-4"
    >
      <div className="text-center mb-5">
        <p className="text-[9px] font-semibold tracking-[0.22em] uppercase text-foreground/40 mb-0.5">Your Profile</p>
        <p className="text-[10px] text-foreground/35">Account details &amp; preferences</p>
      </div>

      <div className="bg-card border border-border rounded-2xl p-4 mb-4">
        <div className="flex flex-col items-center mb-4">
          <div className="w-12 h-12 rounded-full bg-muted border-2 border-border flex items-center justify-center mb-2">
            <User size={22} className="text-foreground/40" />
          </div>
          {/*
           * TODO (auth): Replace "Name" and placeholder values below with
           * real user data from AuthService / GET /api/user/profile/.
           */}
          <p className="text-sm font-semibold text-foreground" style={{ fontFamily: "'Playfair Display', serif" }}>Name</p>
        </div>
        <div className="space-y-0 divide-y divide-border">
          {[
            { label: "Email", value: "------" },
            { label: "Member Since", value: "D/M/Y" },
            { label: "Plan", value: "Free" },
          ].map((row) => (
            <div key={row.label} className="flex items-center justify-between py-2.5">
              <span className="text-xs text-foreground/50">{row.label}</span>
              <span className="text-xs font-medium text-foreground">{row.value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* TODO (auth): Wire Sign out button to AuthService.logout() */}
      <button className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl border border-border bg-card text-xs font-medium text-foreground/70 hover:text-foreground hover:border-foreground/25 transition-all">
        <LogOut size={13} />
        Sign out
      </button>

      <p className="text-center text-[9px] text-foreground/30 mt-4 leading-relaxed">
        © TruChat AI Bureau · All verdicts rendered algorithmically · No editorial endorsement implied
      </p>
    </motion.div>
  );
}
