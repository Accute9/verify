const DOT_STYLES: Record<string, string> = {
  true: "bg-green",
  false: "bg-red",
  mixed: "bg-amber",
};

function classify(verdict: string): keyof typeof DOT_STYLES {
  const v = verdict.toLowerCase();
  if (v.includes("true")) return "true";
  if (v.includes("false")) return "false";
  return "mixed";
}

export function VerdictBadge({ verdict }: { verdict: string }) {
  return (
    <span className="inline-flex items-center gap-2 rounded-md border border-border px-3 py-1 text-[12.5px] font-medium text-text">
      <span className={`h-1.5 w-1.5 rounded-full ${DOT_STYLES[classify(verdict)]}`} />
      {verdict}
    </span>
  );
}
