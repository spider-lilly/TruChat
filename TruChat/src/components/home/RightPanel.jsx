const RightPanel = () => {
  return (
    <aside className="w-80 flex-shrink-0 border-l border-neutral-400 pl-6 space-y-6 font-serif">
      {/* Top Header Live Badge */}
      <div className="flex items-center justify-between border-b border-neutral-400 pb-3 text-xs">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-600 animate-pulse"></span>
          <span className="font-bold uppercase tracking-wider text-neutral-900">BUREAU LIVE</span>
        </div>
        <div className="font-mono font-bold text-neutral-700">3,847</div>
      </div>

      {/* How It Works Section */}
      <div className="space-y-4">
        <h3 className="text-xs uppercase tracking-widest font-bold text-neutral-800 border-b border-neutral-300 pb-1">
          How It Works
        </h3>

        <div className="space-y-4 text-xs text-neutral-800">
          <div className="space-y-1">
            <div className="font-bold flex items-center gap-2">
              <span className="font-serif italic text-neutral-500">I</span>
              <span className="uppercase">Submit a Claim</span>
            </div>
            <p className="text-neutral-600 leading-relaxed pl-4">
              Paste any headline, article link, or news claim into the verification input.
            </p>
          </div>

          <div className="space-y-1">
            <div className="font-bold flex items-center gap-2">
              <span className="font-serif italic text-neutral-500">II</span>
              <span className="uppercase">AI Analysis</span>
            </div>
            <p className="text-neutral-600 leading-relaxed pl-4">
              TruChat will analyse with reference to trusted resources.
            </p>
          </div>

          <div className="space-y-1">
            <div className="font-bold flex items-center gap-2">
              <span className="font-serif italic text-neutral-500">III</span>
              <span className="uppercase">Receive Report</span>
            </div>
            <p className="text-neutral-600 leading-relaxed pl-4">
              Get verdict, accuracy scores and resources.
            </p>
          </div>
        </div>
      </div>

      {/* Editorial Notice Box */}
      <div className="border border-red-300 bg-red-50/60 p-4 space-y-2 text-xs text-red-950 rounded-sm">
        <div className="font-bold uppercase tracking-wider flex items-center gap-1.5 text-red-900">
          <span>⚠</span> EDITORIAL NOTICE
        </div>
        <p className="leading-relaxed text-red-900/90 text-[11px]">
          AI verdicts are editorial aids, not legal determinations. Always consult primary sources before publication.
        </p>
      </div>
    </aside>
  );
};

export default RightPanel;