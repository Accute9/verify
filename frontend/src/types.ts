export interface SubclaimEvaluation {
  subclaim: string;
  evaluation: string;
  subclaim_confidence_score: number;
}

export interface EvalResult {
  claim_evaluation: string;
  confidence: number;
  reasoning: string;
  key_source: string;
  subclaim_evaluations: SubclaimEvaluation[];
}

export type RecordingStatus = "idle" | "recording";
