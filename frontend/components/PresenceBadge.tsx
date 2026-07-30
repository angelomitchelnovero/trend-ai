"use client";

import { useEffect, useState } from "react";
import { getPresenceCount, sendHeartbeat } from "@/lib/api";

const HEARTBEAT_INTERVAL_MS = 20_000;

export default function PresenceBadge() {
  const [count, setCount] = useState<number | null>(null);

  useEffect(() => {
    // One random id per tab load — not persisted, not tied to any user identity.
    const sessionId =
      typeof crypto !== "undefined" && crypto.randomUUID
        ? crypto.randomUUID()
        : Math.random().toString(36).slice(2);

    const beat = () => {
      sendHeartbeat(sessionId);
      getPresenceCount().then(setCount);
    };

    beat();
    const interval = setInterval(beat, HEARTBEAT_INTERVAL_MS);
    return () => clearInterval(interval);
  }, []);

  if (count === null || count < 1) return null;

  return (
    <div className="font-mono text-xs opacity-60 mb-4">
      <span className="inline-block w-1.5 h-1.5 rounded-full mr-2" style={{ background: "var(--teal)" }} />
      {count} {count === 1 ? "person" : "people"} exploring trends right now
    </div>
  );
}
