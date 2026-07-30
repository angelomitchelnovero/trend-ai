const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function getArticles(params = {}) {
  const query = new URLSearchParams(params).toString();
  const res = await fetch(`${API_URL}/articles?${query}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch articles: ${res.status}`);
  return res.json();
}

export async function getTrending(limit = 50) {
  const res = await fetch(`${API_URL}/trending?limit=${limit}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch trending: ${res.status}`);
  return res.json();
}

export async function getGlobalTimeline() {
  const res = await fetch(`${API_URL}/trending/timeline`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch timeline: ${res.status}`);
  return res.json() as Promise<{ points: { day: string; AI: number; Tech: number }[] }>;
}

export async function askTrendAi(question: string) {
  const res = await fetch(`${API_URL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => null);
    throw new Error(data?.detail || "Trend.ai could not answer right now. Please try again.");
  }
  return res.json() as Promise<{ answer: string; sources: { number: number; title: string; url: string }[] }>;
}

export async function getDigest() {
  const res = await fetch(`${API_URL}/digest`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch digest: ${res.status}`);
  return res.json();
}

export async function getGlobalDigest() {
  const res = await fetch(`${API_URL}/digest/global`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch global digest: ${res.status}`);
  return res.json();
}

export async function getNewsAnalyzer() {
  const res = await fetch(`${API_URL}/news-analyzer`, { cache: "no-store" });
  if (!res.ok) throw new Error(`News analyzer failed: ${res.status}`);
  return res.json();
}

export async function search(params: { q?: string; category?: string }) {
  const query = new URLSearchParams(
    Object.fromEntries(Object.entries(params).filter(([, v]) => !!v)) as Record<string, string>
  ).toString();
  const res = await fetch(`${API_URL}/search?${query}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Search failed: ${res.status}`);
  return res.json();
}

export async function sendHeartbeat(sessionId: string) {
  await fetch(`${API_URL}/presence/heartbeat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId }),
  }).catch(() => {
    // Presence is a nice-to-have — a failed heartbeat shouldn't break the page.
  });
}

export async function getPresenceCount(): Promise<number> {
  try {
    const res = await fetch(`${API_URL}/presence/count`, { cache: "no-store" });
    if (!res.ok) return 0;
    const data = await res.json();
    return data.count ?? 0;
  } catch {
    return 0;
  }
}
