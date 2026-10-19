"""Post-hoc confidence calibration via isotonic regression (PAVA).

The model's self-reported confidence is systematically overconfident (see
compute_ece.py's reliability_breakdown). This module fits a monotonic
correction g(raw_confidence) -> calibrated_probability against the labeled
eval set in ece_results.json, so the confidence shown to users reflects
historical accuracy at that confidence level instead of the raw self-report.

Usage:
    python -m backend.api.ece_calibration.calibrate     # refit and save

This fits on the full eval set, which is what you want for the deployed
calibration_map.json (more data makes a better curve), but fitting and
scoring on the same examples overstates how well the fit generalizes. See
cross_validate.py for a 5-fold held-out ECE that isn't subject to that bias.

At runtime, llm.evaluate_claim() loads the saved map and applies it to the
raw averaged confidence before returning it to the caller. The raw value
is still what's persisted to the DB and what compute_ece.py collects into
ece_results.json, so refits are always against the model's true raw output
rather than an already-calibrated number.
"""
import json
from pathlib import Path

CALIBRATION_MAP_PATH = Path(__file__).parent / "calibration_map.json"
DEFAULT_RESULTS_PATH = Path(__file__).parent.parent.parent.parent / "ece_results.json"


def _is_correct(item: dict) -> bool:
    return item["predicted_eval"] == item["eval"]


def fit_isotonic(results: list[dict]) -> list[dict]:
    """Pool-Adjacent-Violators fit of P(correct) as a function of raw confidence.

    Returns control points [{"x": raw_confidence, "y": calibrated_p, "n": weight}, ...]
    sorted by x, with y non-decreasing, ready for linear interpolation.
    """
    points = sorted(
        ((item["confidence"], 1.0 if _is_correct(item) else 0.0) for item in results),
        key=lambda p: p[0],
    )

    # Each block starts as a single point; merge adjacent blocks whenever the
    # earlier block's average would otherwise exceed the later one's.
    blocks = [{"sum": y, "weight": 1, "x_sum": x} for x, y in points]
    i = 0
    while i < len(blocks) - 1:
        avg_i = blocks[i]["sum"] / blocks[i]["weight"]
        avg_next = blocks[i + 1]["sum"] / blocks[i + 1]["weight"]
        if avg_i > avg_next:
            blocks[i:i + 2] = [{
                "sum": blocks[i]["sum"] + blocks[i + 1]["sum"],
                "weight": blocks[i]["weight"] + blocks[i + 1]["weight"],
                "x_sum": blocks[i]["x_sum"] + blocks[i + 1]["x_sum"],
            }]
            if i > 0:
                i -= 1  # a merge can create a new violation with the previous block
        else:
            i += 1

    return [
        {"x": b["x_sum"] / b["weight"], "y": b["sum"] / b["weight"], "n": b["weight"]}
        for b in blocks
    ]


def save_calibration_map(control_points: list[dict], path: Path = CALIBRATION_MAP_PATH) -> None:
    with open(path, "w") as f:
        json.dump(control_points, f, indent=2)


def load_calibration_map(path: Path = CALIBRATION_MAP_PATH) -> list[dict] | None:
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def apply_calibration(raw_confidence: float, control_points: list[dict] | None) -> float:
    """Map a raw confidence through the fitted step function: linearly
    interpolate between control points, clipping outside the fitted range."""
    if not control_points:
        return raw_confidence

    if raw_confidence <= control_points[0]["x"]:
        return control_points[0]["y"]
    if raw_confidence >= control_points[-1]["x"]:
        return control_points[-1]["y"]

    for lo, hi in zip(control_points, control_points[1:]):
        if lo["x"] <= raw_confidence <= hi["x"]:
            if hi["x"] == lo["x"]:
                return lo["y"]
            frac = (raw_confidence - lo["x"]) / (hi["x"] - lo["x"])
            return lo["y"] + frac * (hi["y"] - lo["y"])

    return raw_confidence  # unreachable given the bounds checks above


if __name__ == "__main__":
    with open(DEFAULT_RESULTS_PATH) as f:
        results = json.load(f)

    control_points = fit_isotonic(results)
    save_calibration_map(control_points)

    print(f"Fit isotonic calibration on n={len(results)} examples")
    print(f"Saved {len(control_points)} control points to {CALIBRATION_MAP_PATH}\n")
    print(f"{'raw_confidence':>15}{'calibrated_p':>15}{'n':>6}")
    for cp in control_points:
        print(f"{cp['x']:>15.3f}{cp['y']:>15.3f}{cp['n']:>6.0f}")
