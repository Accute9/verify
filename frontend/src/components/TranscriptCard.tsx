import { useEffect, useRef } from "react";

export function TranscriptCard({ transcript }: { transcript: string }) {
  const bodyRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (bodyRef.current) {
      bodyRef.current.scrollTop = bodyRef.current.scrollHeight;
    }
  }, [transcript]);

  return (
    <div className="flex flex-col overflow-hidden rounded-lg border border-border bg-surface">
      <div className="border-b border-border px-5 py-4">
        <h2 className="text-[13px] font-medium text-text-dim">Live Transcript</h2>
      </div>
      <div className="flex-1 p-5">
        <div
          ref={bodyRef}
          className="h-[260px] max-h-[420px] overflow-y-auto whitespace-pre-wrap break-words font-mono text-[13.5px] leading-relaxed text-text-dim"
        >
          {transcript || (
            <span className="font-sans italic text-text-faint">
              Transcript will appear here once recording starts…
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
