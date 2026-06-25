import type { SubclaimEvaluation } from "../types";

const DOT_STYLES: Record<string, string> = {
  supported: "bg-green",
  refuted: "bg-red",
  inconclusive: "bg-amber",
};

function classify(evaluation: string): keyof typeof DOT_STYLES {
  const e = evaluation.toLowerCase();
  if (e.includes("support")) return "supported";
  if (e.includes("refut")) return "refuted";
  return "inconclusive";
}

export function SubclaimItem({ subclaim, evaluation, subclaim_confidence_score }: SubclaimEvaluation) {
  return (
    <li className="rounded-md border border-border px-3.5 py-3">
      <p className="mb-2 text-[13px] leading-relaxed text-text">{subclaim}</p>
      <div className="flex items-center justify-between gap-2.5">
        <span className="inline-flex items-center gap-1.5 text-[11.5px] font-medium text-text-dim">
          <span className={`h-1.5 w-1.5 rounded-full ${DOT_STYLES[classify(evaluation)]}`} />
          {evaluation}
        </span>
        <span className="font-mono text-[11.5px] text-text-faint">
          confidence {subclaim_confidence_score}
        </span>
      </div>
    </li>
  );
}
