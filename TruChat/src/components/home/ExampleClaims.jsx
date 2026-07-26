const ExampleClaims = ({ onSelectClaim }) => {
  const examples = [
    "Vaccines secretly contain tracking microchips",
    "WHO confirms 12% drop in global disease burden",
    "Government plans to phase out paper currency by 2028",
  ];

  return (
    <div className="space-y-2 font-serif">
      <h3 className="text-[11px] font-bold uppercase tracking-wider text-neutral-600">
        TRY AN EXAMPLE CLAIM:
      </h3>
      <div className="flex flex-wrap gap-2">
        {examples.map((claim, idx) => (
          <button
            key={idx}
            onClick={() => onSelectClaim(claim)}
            className="text-xs bg-[#EFECE6] border border-neutral-300 px-3 py-1.5 text-neutral-800 hover:bg-neutral-200 hover:border-neutral-700 transition-all text-left font-serif"
          >
            {claim}
          </button>
        ))}
      </div>
    </div>
  );
};

export default ExampleClaims;
