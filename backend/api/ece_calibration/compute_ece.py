import asyncio
from backend.api.database.load_db import supabase
from ..llm import evaluate_claim
import json


async def compute_ece():
    eval_claims = (supabase.table("ece_calibration").select("*").execute().data)[:200]
    results = []
    for claim in eval_claims:
        try:
            prediction = await evaluate_claim(claim["claim"], eval_id=claim["eval_id"])
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
        except Exception as e:
            print(f"Error evaluating claim with eval_id {claim['eval_id']}: {e}")
    with open("ece_results.json", "w") as f:
        json.dump(results, f, indent=4)


def is_correct(item):
    return item["predicted_eval"] == item["eval"]


def compute_ece_from_results(results, num_bins=10):
    bins = [[] for _ in range(num_bins)]
    for item in results:
        bin_idx = min(int(item["confidence"] * num_bins), num_bins - 1)
        bins[bin_idx].append(item)

    n = len(results)
    ece = 0.0
    bin_stats = []
    for i, bucket in enumerate(bins):
        if not bucket:
            continue
        accuracy = sum(is_correct(item) for item in bucket) / len(bucket)
        avg_confidence = sum(item["confidence"] for item in bucket) / len(bucket)
        weight = len(bucket) / n
        ece += weight * abs(accuracy - avg_confidence)
        bin_stats.append({
            "bin": f"[{i / num_bins:.1f}, {(i + 1) / num_bins:.1f})",
            "count": len(bucket),
            "accuracy": round(accuracy, 4),
            "avg_confidence": round(avg_confidence, 4),
        })
    return ece, bin_stats

def reliability_breakdown(results, n_buckets=10):
    buckets = [[] for _ in range(n_buckets)]
    for r in results:
        idx = min(int(r["confidence"] * n_buckets), n_buckets - 1)
        correct = r["predicted_eval"] == r["eval"]
        buckets[idx].append(correct)
    
    print(f"{'Bucket':<12} {'Predicted':>12} {'Actual':>10} {'Count':>8} {'Gap':>8}")
    print("-" * 52)
    for i, bucket in enumerate(buckets):
        if not bucket:
            continue
        mid = (i + 0.5) / n_buckets
        acc = sum(bucket) / len(bucket)
        gap = mid - acc
        print(f"{i/n_buckets:.0%}–{(i+1)/n_buckets:.0%}   {mid:>12.2f} {acc:>10.2f} {len(bucket):>8} {gap:>+8.2f}")


if __name__ == "__main__":
    # results = asyncio.run(compute_ece())
    # for result in results:
    #     print(result)
    d = json.load(open("ece_results.json"))

    ece, bin_stats = compute_ece_from_results(d)
    print(f"ECE: {ece:.4f} (n={len(d)})\n")
    for stat in bin_stats:
        print(
            f"{stat['bin']:>14}  n={stat['count']:>4}  "
            f"acc={stat['accuracy']:.3f}  conf={stat['avg_confidence']:.3f}"
        )
    # supabase.table("ece_values").insert({"ece_score": ece, "prompt_version": "v1", "notes": "Baseline, no calibration applied"}).execute()
    reliability_breakdown(d)
    # print a sample to inspect
    for r in d[:10]:
        print(f"predicted: '{r['predicted_eval']}' | eval: '{r['eval']}' | match: {r['predicted_eval'] == r['eval']}")
