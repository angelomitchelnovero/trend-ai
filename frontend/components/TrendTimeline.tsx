"use client";

import { useEffect, useState } from "react";
import { getGlobalTimeline } from "@/lib/api";

type Point = { day: string; AI: number; Tech: number };

export default function TrendTimeline() {
  const [points, setPoints] = useState<Point[]>([]);
  useEffect(() => { getGlobalTimeline().then((result) => setPoints(result.points)).catch(() => setPoints([])); }, []);
  if (!points.length) return null;
  const maximum = Math.max(...points.map((point) => point.AI + point.Tech), 1);
  return <section className="mb-10" aria-label="Global signal timeline"><div className="flex items-end justify-between mb-3"><div><p className="font-mono text-xs opacity-50 mb-1">MOMENTUM</p><h2 className="font-display text-2xl">Global signal timeline</h2></div><span className="font-mono text-xs opacity-50">AI / Tech signals retained</span></div><div className="flex h-28 items-end gap-2 border-b pb-1" style={{ borderColor: "var(--line)" }}>{points.map((point) => <div key={point.day} className="flex flex-1 flex-col justify-end gap-1 text-center" title={`${point.day}: ${point.AI} AI, ${point.Tech} Tech`}><div className="flex flex-col justify-end gap-px" style={{ height: "76px" }}><div style={{ height: `${(point.AI / maximum) * 76}px`, background: "var(--coral)" }} /><div style={{ height: `${(point.Tech / maximum) * 76}px`, background: "var(--manila-blue)" }} /></div><span className="font-mono text-[9px] opacity-50">{point.day.slice(5)}</span></div>)}</div><p className="mt-2 font-mono text-[10px] opacity-55"><span style={{ color: "var(--coral)" }}>■</span> AI&nbsp;&nbsp; <span style={{ color: "var(--manila-blue)" }}>■</span> Tech</p></section>;
}
