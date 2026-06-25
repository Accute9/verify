import type { RecordingStatus } from "../types";

export function TopBar({ status }: { status: RecordingStatus }) {
  const isLive = status === "recording";

  return (
    <div className="flex items-center justify-between border-b border-border px-5 py-5 sm:px-10 md:px-14 backdrop-blur">
      <div className="flex items-center gap-2.5">
        <div className="flex h-[30px] w-[30px] items-center justify-center rounded-[8px] border border-border">
          <svg viewBox="0 0 24 24" fill="none" className="h-[15px] w-[15px]">
            <path
              d="M5 13l4 4L19 7"
              stroke="currentColor"
              className="text-text"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
        <div>
          <div className="text-[15px] font-semibold tracking-tight text-text">
            Verify
          </div>
          <div className="-mt-0.5 text-[12px] text-text-faint">
            Real-time fact-checking
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2 rounded-full border border-border px-3.5 py-1.5 text-[13px] font-medium text-text-dim">
        <span
          className={`h-1.5 w-1.5 rounded-full ${
            isLive ? "animate-pulse-dot bg-red" : "bg-text-faint"
          }`}
        />
        <span>{isLive ? "Recording" : "Idle"}</span>
      </div>
    </div>
  );
}
