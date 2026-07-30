import FeedClient from "@/components/FeedClient";
import { getArticles, getDigest, getGlobalDigest, getNewsAnalyzer, getTrending } from "@/lib/api";

export default async function FeedPage() {
  let articles: Awaited<ReturnType<typeof getArticles>>["items"] = [];
  let trending: { id?: number; term: string; source: string; score: number | null; title?: string | null; summary?: string | null; url?: string | null; ticker?: string | null; category?: string | null; scope?: string | null }[] = [];
  let digest: { content: string; generated_at: string } | null = null;
  let globalDigest: { content: string; generated_at: string } | null = null;
  let analyzedNews: Awaited<ReturnType<typeof getNewsAnalyzer>>["items"] = [];
  let backendReachable = true;

  try {
    const [articlesRes, trendingRes, analyzerRes] = await Promise.all([getArticles({ page: "1", page_size: "20" }), getTrending(), getNewsAnalyzer()]);
    articles = articlesRes.items ?? [];
    trending = trendingRes;
    analyzedNews = analyzerRes.items ?? [];
  } catch {
    backendReachable = false;
  }

  try { digest = await getDigest(); } catch { /* No Philippine digest or summarized stories yet. */ }
  try { globalDigest = await getGlobalDigest(); } catch { /* No global digest or enriched cards yet. */ }

  return <main className="min-h-screen"><FeedClient initialArticles={articles} initialTrending={trending} backendReachable={backendReachable} digestContent={digest?.content ?? null} digestGeneratedAt={digest?.generated_at ?? null} globalDigestContent={globalDigest?.content ?? null} globalDigestGeneratedAt={globalDigest?.generated_at ?? null} analyzedNews={analyzedNews} /></main>;
}
