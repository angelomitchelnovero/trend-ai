"use client";

type TrendingTerm = {
  term: string;
  source: string;
  score: number | null;
};

export default function TrendingTicker({ terms }: { terms: TrendingTerm[] }) {
  if (!terms.length) return null;

  // Duplicate the list so the scroll loops seamlessly.
  const loop = [...terms, ...terms];

  return (
    <div
      className="w-full overflow-hidden border-y"
      style={{ background: "var(--manila-blue)", borderColor: "var(--manila-blue)" }}
      aria-label="Trending now ticker"
    >
      <div className="ticker-track flex items-center gap-10 py-2 whitespace-nowrap">
        {loop.map((t, i) => (
          <span
            key={i}
            className="font-mono text-xs tracking-wide"
            style={{ color: "var(--sunrise-gold)" }}
          >
            <span className="opacity-70 mr-2">{t.source === "reddit" ? "r/" : "▲"}</span>
            {t.term}
          </span>
        ))}
      </div>

      <style jsx>{`
        .ticker-track {
          width: max-content;
          animation: scroll-left 40s linear infinite;
        }
        @keyframes scroll-left {
          from { transform: translateX(0); }
          to { transform: translateX(-50%); }
        }
        @media (prefers-reduced-motion: reduce) {
          .ticker-track { animation: none; }
        }
      `}</style>
    </div>
  );
}
