import ArticleCard from "@/components/ArticleCard";
import DigestBanner from "@/components/DigestBanner";
import TrendingTicker from "@/components/TrendingTicker";
import { getArticles, getDigest, getTrending } from "@/lib/api";

export default async function FeedPage() {
  let articles: Awaited<ReturnType<typeof getArticles>>["items"] = [];
  let trending: { term: string; source: string; score: number | null }[] = [];
  let digest: { content: string; generated_at: string } | null = null;
  let backendReachable = true;

  try {
    const [articlesRes, trendingRes] = await Promise.all([
      getArticles({ page: "1", page_size: "20" }),
      getTrending(),
    ]);
    articles = articlesRes.items ?? [];
    trending = trendingRes;
  } catch {
    backendReachable = false;
  }

  try {
    digest = await getDigest();
  } catch {
    // No digest yet, or backend unreachable — DigestBanner handles null.
  }

  return (
    <main className="min-h-screen">
      <TrendingTicker terms={trending} />

      <div className="max-w-3xl mx-auto px-6 py-10">
        <header className="mb-10">
          <h1 className="font-display text-4xl font-semibold mb-1">Trend.ai</h1>
          <p className="font-mono text-xs opacity-50">
            what's trending in the Philippines, summarized by AI
          </p>
        </header>

        <DigestBanner
          content={digest?.content ?? null}
          generatedAt={digest?.generated_at ?? null}
        />

        <section aria-label="Article feed">
          {!backendReachable && (
            <div className="border rounded-sm p-5 mb-6" style={{ borderColor: "var(--line)" }}>
              <p className="font-mono text-xs opacity-50">
                Can't reach the backend at {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}.
                Make sure `uvicorn app.main:app --reload` is running.
              </p>
            </div>
          )}

          {backendReachable && articles.length === 0 && (
            <div className="border rounded-sm p-5 mb-6" style={{ borderColor: "var(--line)" }}>
              <p className="font-mono text-xs opacity-50">
                Connected, but no articles yet — run ingestion to pull real data.
              </p>
            </div>
          )}

          {articles.map((article) => (
            <ArticleCard key={article.id} article={article} />
          ))}
        </section>
      </div>
    </main>
  );
}
