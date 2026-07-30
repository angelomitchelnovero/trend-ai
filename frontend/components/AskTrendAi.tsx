"use client";

import { FormEvent, useState } from "react";
import { askTrendAi } from "@/lib/api";

export default function AskTrendAi() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [sources, setSources] = useState<{ number: number; title: string; url: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  async function submit(event: FormEvent) {
    event.preventDefault(); if (!question.trim()) return;
    setLoading(true); setError(null); setAnswer(null);
    try { const result = await askTrendAi(question.trim()); setAnswer(result.answer); setSources(result.sources); }
    catch (err) { setError(err instanceof Error ? err.message : "Trend.ai could not answer right now."); }
    finally { setLoading(false); }
  }
  return <section className="mb-12 rounded-sm p-6" style={{ background: "var(--manila-blue)", color: "var(--paper)" }} aria-label="Ask Trend.ai">
    <p className="font-mono text-xs tracking-[0.16em] mb-2" style={{ color: "var(--sunrise-gold)" }}>ASK TREND.AI</p>
    <h2 className="font-display text-3xl mb-2">Ask about AI and technology</h2>
    <p className="text-sm leading-relaxed opacity-80 mb-4">Ask about current tech products, companies, software, chips, cybersecurity, or AI. Trend.ai checks recent technology reporting—not the Global Signals cards. Questions outside AI and technology are politely declined.</p>
    <form onSubmit={submit} className="flex flex-col sm:flex-row gap-2"><input value={question} onChange={(event) => setQuestion(event.target.value)} maxLength={500} placeholder="What is the latest MacBook today?" className="min-w-0 flex-1 rounded-sm px-3 py-2 text-sm" style={{ color: "var(--ink)" }} /><button type="submit" disabled={loading || !question.trim()} className="rounded-sm px-4 py-2 font-mono text-xs disabled:opacity-50" style={{ background: "var(--sunrise-gold)", color: "var(--ink)" }}>{loading ? "Checking sources..." : "Ask"}</button></form>
    {error && <p className="mt-4 text-sm" style={{ color: "var(--sunrise-gold)" }}>{error}</p>}
    {answer && <div className="mt-5 border-t pt-4" style={{ borderColor: "rgba(250,247,240,.25)" }}><p className="text-sm leading-relaxed whitespace-pre-line">{answer}</p>{sources.length > 0 && <div className="mt-4"><p className="font-mono text-xs opacity-60 mb-2">RECENT TECHNOLOGY SOURCES</p><div className="flex flex-wrap gap-x-4 gap-y-2">{sources.map((source) => <a key={source.number} className="text-xs underline opacity-85" href={source.url} target="_blank" rel="noopener noreferrer">[{source.number}] {source.title}</a>)}</div></div>}</div>}
  </section>;
}
