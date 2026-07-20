export default function DigestBanner({
  content,
  generatedAt,
}: {
  content: string | null;
  generatedAt: string | null;
}) {
  if (!content) {
    return (
      <div
        className="border rounded-sm p-5 mb-8"
        style={{ borderColor: "var(--line)" }}
      >
        <p className="font-mono text-xs opacity-50">
          No digest yet — check back once the scheduler has run.
        </p>
      </div>
    );
  }

  return (
    <div
      className="rounded-sm p-6 mb-8"
      style={{ background: "var(--manila-blue)", color: "var(--paper)" }}
    >
      <div className="flex items-baseline justify-between mb-3">
        <h2 className="font-display text-lg" style={{ color: "var(--sunrise-gold)" }}>
          Today's briefing
        </h2>
        {generatedAt && (
          <span className="font-mono text-xs opacity-60">
            {new Date(generatedAt).toLocaleString("en-PH", {
              month: "short",
              day: "numeric",
              hour: "numeric",
              minute: "2-digit",
            })}
          </span>
        )}
      </div>
      <p className="text-sm leading-relaxed opacity-90">{content}</p>
    </div>
  );
}
