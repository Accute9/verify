from supabase import create_client
import os
from dotenv import load_dotenv
import time
import uuid

load_dotenv()

supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

def store_transcript(transcript: str, transcript_id: int) -> int:
    ts = int(time.time())
    supabase.table("transcripts").insert({"transcript": transcript, "transcript_id": transcript_id, "created_at": ts}).execute()
    return transcript_id

def store_subclaim_evaluations(subclaim_evaluations: list, claim_id: int, search_results: list = None):
    for i, subclaim in enumerate(subclaim_evaluations):
        subclaim_id = uuid.uuid4().int
        ts = int(time.time())
        top_result = search_results[i][0] if search_results and i < len(search_results) and search_results[i] else {}
        supabase.table("subclaim_evaluations").insert({
            "subclaim_id": subclaim_id,
            "claim_id": claim_id,
            "subclaim_text": subclaim["subclaim"],
            "verdict": subclaim["evaluation"],
            "confidence": subclaim["subclaim_confidence_score"],
            "source_url": top_result.get("url"),
            "source_title": top_result.get("title"),
            "created_at": ts
        }).execute()

def store_claim_evaluation(claim_id: int, transcript_id: int, overall_verdict: str, overall_confidence: float, reasoning: str):
    ts = int(time.time())
    supabase.table("claim_evaluation").insert({
        "claim_id": claim_id,
        "transcript_id": transcript_id,
        "overall_verdict": overall_verdict,
        "overall_confidence": overall_confidence,
        "reasoning": reasoning,
        "created_at": ts
    }).execute()