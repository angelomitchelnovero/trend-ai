"use client";

import { useState, useEffect } from "react";

export default function SearchBar({
  onSearch,
  value,
}: {
  onSearch: (query: string) => void;
  value: string;
}) {
  const [input, setInput] = useState(value);

  // Keeps the input in sync when a ticker click sets the query externally.
  useEffect(() => {
    setInput(value);
  }, [value]);

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSearch(input.trim());
      }}
      className="flex gap-2 mb-6"
    >
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Search news and trends..."
        className="flex-1 border rounded-sm px-3 py-2 text-sm bg-transparent focus:outline-none"
        style={{ borderColor: "var(--line)" }}
      />
      <button
        type="submit"
        className="font-mono text-xs px-4 py-2 rounded-sm"
        style={{ background: "var(--manila-blue)", color: "var(--paper)" }}
      >
        Search
      </button>
      {value && (
        <button
          type="button"
          onClick={() => {
            setInput("");
            onSearch("");
          }}
          className="font-mono text-xs px-3 py-2 opacity-60 hover:opacity-100"
        >
          Clear
        </button>
      )}
    </form>
  );
}
