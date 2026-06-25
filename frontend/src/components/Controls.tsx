import type { RecordingStatus } from "../types";

interface ControlsProps {
  status: RecordingStatus;
  onStart: () => void;
  onStop: () => void;
}

export function Controls({ status, onStart, onStop }: ControlsProps) {
  const isLive = status === "recording";

  return (
    <div className="mb-9 flex flex-wrap items-center justify-center gap-3.5">
      <button
        type="button"
        disabled={isLive}
        onClick={onStart}
        className="inline-flex items-center gap-2.5 rounded-md bg-accent-strong px-6 py-3 text-[14px] font-medium text-bg transition enabled:hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-30 active:enabled:scale-[0.98]"
      >
        <span className="h-2 w-2 rounded-full bg-current" />
        Start Recording
      </button>
      <button
        type="button"
        disabled={!isLive}
        onClick={onStop}
        className="inline-flex items-center gap-2.5 rounded-md border border-border px-6 py-3 text-[14px] font-medium text-text transition enabled:hover:border-text-faint disabled:cursor-not-allowed disabled:opacity-30 active:enabled:scale-[0.98]"
      >
        <span className="h-2 w-2 rounded-[2px] bg-current" />
        Stop Recording
      </button>
    </div>
  );
}
