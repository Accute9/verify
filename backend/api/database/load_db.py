from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime, timezone
import os
import time
import uuid

load_dotenv()

supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

def generate_bigint_id() -> int:
    """uuid4().int is 128 bits and overflows Postgres bigint; keep the top 63 bits."""
    return uuid.uuid4().int >> 65

def store_transcript(transcript: str, transcript_id: int) -> int:
    supabase.table("transcripts").insert({"transcript": transcript, "transcript_id": transcript_id}).execute()
    return transcript_id

def store_subclaim_evaluations(subclaim_evaluations: list, claim_id: int, search_results: list = None):
    for i, subclaim in enumerate(subclaim_evaluations):
        subclaim_id = generate_bigint_id()
        top_result = search_results[i][0] if search_results and i < len(search_results) and search_results[i] else {}
        supabase.table("subclaim_evaluations").insert({
            "subclaim_id": subclaim_id,
            "claim_id": claim_id,
            "subclaim_text": subclaim["subclaim"],
            "verdict": subclaim["evaluation"],
            "confidence": subclaim["subclaim_confidence_score"],
            "source_url": top_result.get("url"),
            "source_title": top_result.get("title"),
        }).execute()

def store_claim_evaluation(claim_id: int, transcript_id: int, overall_verdict: str, overall_confidence: float, reasoning: str):
    supabase.table("claim_evaluation").insert({
        "claim_id": claim_id,
        "transcript_id": transcript_id,
        "overall_verdict": overall_verdict,
        "overall_confidence": overall_confidence,
        "reasoning": reasoning,
    }).execute()

def store_scrapped_eval_data(claim_id: int, eval: str, source: str, summary: str):
    supabase.table("ece-calibration").insert({
        "claim_id": claim_id,
        "eval": eval,
        "source": source,
        "summary": summary,
    }).execute()