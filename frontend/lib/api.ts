const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function getArticles(params = {}) {
  const query = new URLSearchParams(params).toString();
  const res = await fetch(`${API_URL}/articles?${query}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch articles: ${res.status}`);
  return res.json();
}

export async function getTrending() {
  const res = await fetch(`${API_URL}/trending`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch trending: ${res.status}`);
  return res.json();
}

export async function getDigest() {
  const res = await fetch(`${API_URL}/digest`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch digest: ${res.status}`);
  return res.json();
}
