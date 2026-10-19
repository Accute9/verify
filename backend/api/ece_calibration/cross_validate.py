"""5-fold cross-validated ECE for the isotonic calibration in calibrate.py.

fit_isotonic() in calibrate.py is fit and scored on the same examples when run
directly, which optimistically overstates how well calibration generalizes.
This script fits a separate curve per fold on the other 4 folds, scores only
the held-out fold with it, pools the held-out predictions across all 5 folds,
and reports ECE on that pooled set alongside the raw (uncalibrated) and
in-sample calibrated baselines for comparison.

Usage:
    python -m backend.api.ece_calibration.cross_validate
"""
import json
import random

from .calibrate import DEFAULT_RESULTS_PATH, apply_calibration, fit_isotonic
from .compute_ece import compute_ece_from_results, is_correct

NUM_FOLDS = 5
SEED = 0


def make_folds(results: list[dict], num_folds: int = NUM_FOLDS, seed: int = SEED) -> list[list[dict]]:
    """Split results into num_folds folds, stratified by correctness so each
    fold has a similar accuracy mix despite the small sample size."""
    correct = [r for r in results if is_correct(r)]
    incorrect = [r for r in results if not is_correct(r)]
    rng = random.Random(seed)
    rng.shuffle(correct)
    rng.shuffle(incorrect)

    folds = [[] for _ in range(num_folds)]
    for group in (correct, incorrect):
        for i, item in enumerate(group):
            folds[i % num_folds].append(item)
    return folds


def cross_validated_predictions(results: list[dict], num_folds: int = NUM_FOLDS) -> list[dict]:
    """Fit one isotonic curve per fold on the other folds, score only the
    held-out fold with it, and return the pooled held-out predictions."""
    folds = make_folds(results, num_folds)
    pooled = []
    for i in range(num_folds):
        test_fold = folds[i]
        train_fold = [item for j, fold in enumerate(folds) if j != i for item in fold]
        control_points = fit_isotonic(train_fold)
        for item in test_fold:
            pooled.append({
                **item,
                "confidence": apply_calibration(item["confidence"], control_points),
            })
    return pooled


if __name__ == "__main__":
    with open(DEFAULT_RESULTS_PATH) as f:
        results = json.load(f)

    raw_ece, _ = compute_ece_from_results(results)

    in_sample_points = fit_isotonic(results)
    in_sample_calibrated = [
        {**item, "confidence": apply_calibration(item["confidence"], in_sample_points)}
        for item in results
    ]
    in_sample_ece, _ = compute_ece_from_results(in_sample_calibrated)

    held_out_predictions = cross_validated_predictions(results)
    held_out_ece, bin_stats = compute_ece_from_results(held_out_predictions)

    print(f"n = {len(results)}, {NUM_FOLDS}-fold CV (seed={SEED})\n")
    print(f"{'raw (uncalibrated)':<28}ECE = {raw_ece:.4f}")
    print(f"{'in-sample calibrated':<28}ECE = {in_sample_ece:.4f}")
    print(f"{'k-fold held-out calibrated':<28}ECE = {held_out_ece:.4f}\n")

    print("Held-out calibrated reliability by bin:")
    for stat in bin_stats:
        print(
            f"{stat['bin']:>14}  n={stat['count']:>4}  "
            f"acc={stat['accuracy']:.3f}  conf={stat['avg_confidence']:.3f}"
        )
