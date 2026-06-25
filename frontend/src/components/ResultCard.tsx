import type { EvalResult } from "../types";
import { VerdictBadge } from "./VerdictBadge";
import { ConfidenceBar } from "./ConfidenceBar";
import { SubclaimItem } from "./SubclaimItem";

export function ResultCard({ result }: { result: EvalResult | null }) {
  return (
    <div className="flex flex-col overflow-hidden rounded-lg border border-border bg-surface">
      <div className="border-b border-border px-5 py-4">
        <h2 className="text-[13px] font-medium text-text-dim">Fact-Check Result</h2>
      </div>
      <div className="flex-1 p-5">
        {!result ? (
          <p className="text-[13.5px] italic text-text-faint">
            Fact-check results will appear here after a claim is evaluated…
          </p>
        ) : (
          <div className="max-h-[420px] overflow-y-auto">
            <div className="mb-1">
              <VerdictBadge verdict={result.claim_evaluation} />
            </div>

            <ConfidenceBar confidence={result.confidence} />

            <p className="mb-4 text-[13.5px] leading-relaxed text-text-dim">
              {result.reasoning}
            </p>

            <a
              href={result.key_source}
              target="_blank"
              rel="noopener noreferrer"
              className="mb-5 inline-flex items-center gap-1.5 text-[13px] font-medium text-text underline decoration-border underline-offset-2 hover:decoration-text-faint"
            >
              View Source ↗
            </a>

            <div className="mb-2.5 text-[11.5px] font-medium uppercase tracking-wide text-text-faint">
              Subclaim Analysis
            </div>
            <ul className="flex flex-col gap-2">
              {result.subclaim_evaluations.map((sc, i) => (
                <SubclaimItem key={i} {...sc} />
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
