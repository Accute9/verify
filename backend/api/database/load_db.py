from supabase import create_client
import os
from dotenv import load_dotenv
import time

load_dotenv()

supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

def store_transcript(transcript: str, id: int) -> int:
    ts = int(time.time())
    supabase.table("Transcripts").insert({"transcript": transcript, "transcript_id": id, "created_at": ts}).execute()
    return id

def store_subclaims(subclaims: list, id: int) -> int:
    ts = int(time.time())
    for subclaim in subclaims:
        supabase.table("Subclaims").insert({"subclaim": subclaim, "transcript_id": id, "created_at": ts}).execute()
    return id

def store_evaluation(claim: str, id: int, evaluation_data: dict, confidence: int, reasoning: str, url: str, subclaim_title: str,) -> int:
    ts = int(time.time())
    supabase.table("Claim Evaluation").insert({"created_at": ts, "claim": claim, "transcript_id": id, "evaluation_data": evaluation_data, "confidence": confidence, "url": url, "reasoning": reasoning, "subclaim_title": subclaim_title}).execute()
    return id

