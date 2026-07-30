type Article = {
  id: number;
  title: string;
  summary: string | null;
  url: string;
  published_at: string | null;
  source: string | null;
  category: string | null;
  cluster_id: number | null;
};

const CATEGORY_COLORS: Record<string, string> = {
  Politics: "var(--manila-blue)",
  Finance: "var(--teal)",
  Entertainment: "var(--coral)",
  Sports: "var(--sunrise-gold)",
  "Weather/Disaster": "var(--coral)",
  Local: "var(--teal)",
  AI: "var(--coral)",
  Tech: "var(--manila-blue)",
};

function timeAgo(iso: string | null): string {
  if (!iso) return "";
  const diffMs = Date.now() - new Date(iso).getTime();
  const hours = Math.floor(diffMs / 3_600_000);
  if (hours < 1) return "just now";
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export default function ArticleCard({ article, variant = "feed" }: { article: Article; variant?: "feed" | "card" }) {
  const categoryColor = article.category
    ? CATEGORY_COLORS[article.category] || "var(--ink)"
    : "var(--ink)";

  return (
    <a
      href={article.url}
      target="_blank"
      rel="noopener noreferrer"
      className={variant === "card"
        ? "block border rounded-sm p-5 h-full group focus:outline-none focus-visible:ring-2"
        : "block border-b py-5 group focus:outline-none focus-visible:ring-2"}
      style={{ borderColor: "var(--line)" }}
    >
      <div className="flex items-center gap-3 mb-2 font-mono text-xs">
        {article.category && (
          <span style={{ color: categoryColor }}>{article.category}</span>
        )}
        {article.source && <span className="opacity-50">{article.source}</span>}
        <span className="opacity-40">{timeAgo(article.published_at)}</span>
        {article.cluster_id !== null && (
          <span className="opacity-40">· multiple outlets</span>
        )}
      </div>

      <h2
        className="font-display text-xl leading-snug mb-1 group-hover:underline decoration-2 underline-offset-2"
        style={{ textDecorationColor: categoryColor }}
      >
        {article.title}
      </h2>

      {article.summary && (
        <p className="text-sm opacity-80 leading-relaxed max-w-2xl">
          {article.summary}
        </p>
      )}
    </a>
  );
}
