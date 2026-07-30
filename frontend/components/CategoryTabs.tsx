"use client";

const CATEGORIES = [
  "AI",
  "Tech",
  "Politics",
  "Finance",
  "Entertainment",
  "Sports",
  "Weather/Disaster",
  "Local",
];

export default function CategoryTabs({
  active,
  onSelect,
}: {
  active: string | null;
  onSelect: (category: string | null) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2 mb-6 font-mono text-xs">
      <button
        onClick={() => onSelect(null)}
        className="px-3 py-1 rounded-full border"
        style={{
          borderColor: "var(--line)",
          background: active === null ? "var(--manila-blue)" : "transparent",
          color: active === null ? "var(--paper)" : "var(--ink)",
        }}
      >
        All
      </button>
      {CATEGORIES.map((cat) => (
        <button
          key={cat}
          onClick={() => onSelect(active === cat ? null : cat)}
          className="px-3 py-1 rounded-full border"
          style={{
            borderColor: "var(--line)",
            background: active === cat ? "var(--manila-blue)" : "transparent",
            color: active === cat ? "var(--paper)" : "var(--ink)",
          }}
        >
          {cat}
        </button>
      ))}
    </div>
  );
}
