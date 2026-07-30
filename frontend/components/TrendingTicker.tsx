"use client";

type TrendingTerm = {
  id?: number;
  term: string;
  source: string;
  score?: number | null;
};

export default function TrendingTicker({
  terms,
  onTermClick,
}: {
  terms: TrendingTerm[];
  onTermClick?: (term: TrendingTerm) => void;
}) {
  if (!terms.length) return null;

  // Duplicate only a varied list so one item never appears twice on screen.
  const loop = terms.length > 1 ? [...terms, ...terms] : terms;

  return (
    <div
      className="w-full overflow-hidden border-y"
      style={{ background: "var(--manila-blue)", borderColor: "var(--manila-blue)" }}
      aria-label="Trending now ticker"
    >
      <div className="ticker-track flex items-center gap-10 py-2 whitespace-nowrap">
        {loop.map((t, i) => (
          <button
            key={i}
            onClick={() => onTermClick?.(t)}
            className="font-mono text-xs tracking-wide hover:underline focus:outline-none"
            style={{ color: "var(--sunrise-gold)" }}
            title={`Open the fact brief for "${t.term}"`}
          >
            <span className="opacity-70 mr-2">{t.source === "reddit" ? "r/" : "▲"}</span>
            {t.term}
          </button>
        ))}
      </div>

      <style jsx>{`
        .ticker-track {
          width: max-content;
          animation: scroll-left 95s linear infinite;
        }
        .ticker-track:hover {
          animation-play-state: paused;
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
