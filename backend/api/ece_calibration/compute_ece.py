import asyncio
from backend.api.database.load_db import supabase
from ..llm import evaluate_claim


async def compute_ece():
    eval_claims = (supabase.table("ece_calibration").select("*").execute().data)[:200]
    results = []
    for claim in eval_claims:
        prediction = await evaluate_claim(claim["claim"], claim["eval_id"])
        predicted_eval = prediction["claim_evaluation"]
        confidence = prediction["confidence"]
        try:
            results.append({
                "eval_id": claim["eval_id"],
                "claim": claim["claim"],
                "eval": claim["eval"],
                "predicted_eval": predicted_eval,
                "confidence": confidence
            })
        except Exception as e:
            print(f"Error processing claim with eval_id {claim['eval_id']}: {e}")
    return results

if __name__ == "__main__":
    results = asyncio.run(compute_ece())
    for result in results:
        print(result)