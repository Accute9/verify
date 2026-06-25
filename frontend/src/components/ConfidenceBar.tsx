export function ConfidenceBar({ confidence }: { confidence: number }) {
  const pct = Math.round(confidence * 100);

  return (
    <div className="mb-4.5 mt-3.5">
      <div className="mb-1.5 flex justify-between text-xs font-medium text-text-dim">
        <span>Confidence</span>
        <span>{pct}%</span>
      </div>
      <div className="h-1 overflow-hidden rounded-full bg-surface-2">
        <div
          className="h-full rounded-full bg-accent-strong"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
