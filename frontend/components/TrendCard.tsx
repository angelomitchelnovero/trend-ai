type Trend = { id?: number; term: string; title: string; summary: string | null; url: string | null; ticker: string | null; category: string | null; source: string; scope: string; score?: number | null; };

const colors: Record<string, string> = { AI: "var(--coral)", Tech: "var(--manila-blue)", Politics: "var(--manila-blue)", Finance: "var(--teal)", Entertainment: "var(--sunrise-gold)" };

export default function TrendCard({ trend, isWatched = false, onToggleWatch }: { trend: Trend; isWatched?: boolean; onToggleWatch?: (trend: Trend) => void; }) {
  const color = colors[trend.category || ""] || "var(--ink)";
  return <article className="h-full border rounded-sm p-5 flex flex-col" style={{ borderColor: "var(--line)" }}>
    <div className="flex gap-2 items-center mb-3 font-mono text-[11px]">
      {trend.category && <span className="px-2 py-1 rounded-full" style={{ background: color, color: "var(--paper)" }}>{trend.category}</span>}
      {trend.ticker && <span className="opacity-60">{trend.ticker}</span>}
      <span className="ml-auto opacity-40">{trend.scope === "global" ? "global" : "PH"}</span>
    </div>
    <h3 className="font-display text-xl leading-snug mb-2">{trend.title || trend.term}</h3>
    <p className="text-sm leading-relaxed opacity-75 flex-1">{trend.summary || "A rising story worth tracking. Open the source for the latest reporting and context."}</p>
    {trend.scope === "global" && <details className="mt-4 text-xs opacity-70"><summary className="cursor-pointer font-mono">Why it&apos;s trending</summary><p className="mt-2 leading-relaxed">This is a global {trend.category || "technology"} signal selected from recent reporting and labeled from the topic&apos;s source query. Its brief is based on the publisher&apos;s available reporting.</p></details>}
    <div className="mt-5 flex items-center justify-between gap-3">
      {trend.url ? <a className="font-mono text-xs" style={{ color }} href={trend.url} target="_blank" rel="noopener noreferrer">Read source →</a> : <span />}
      {onToggleWatch && <button onClick={() => onToggleWatch(trend)} className="font-mono text-xs underline underline-offset-4" style={{ color: isWatched ? "var(--coral)" : "var(--ink)" }}>{isWatched ? "Following" : "Follow"}</button>}
    </div>
  </article>;
}
