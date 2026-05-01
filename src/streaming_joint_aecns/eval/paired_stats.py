from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Any


def load_paired_rows(path: str | Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            utt_id = row.get("utt_id")
            if not utt_id:
                continue
            if row.get("doubletalk_preservation_error") is None and row.get("doubletalk_nearend_l1") is not None:
                row["doubletalk_preservation_error"] = row["doubletalk_nearend_l1"]
            if row.get("preservation_error") is None and row.get("nearend_l1") is not None:
                row["preservation_error"] = row["nearend_l1"]
            rows[utt_id] = row
    return rows


def metric_direction(metric_name: str) -> str:
    return "lower" if metric_name.endswith("_l1") or metric_name.endswith("_error") else "higher"


def paired_bootstrap(deltas: list[float], iterations: int, seed: int) -> tuple[float, float, float]:
    rng = random.Random(seed)
    means = []
    for _ in range(iterations):
        sample = [deltas[rng.randrange(len(deltas))] for _ in range(len(deltas))]
        means.append(sum(sample) / len(sample))
    means.sort()
    lower = means[int(0.025 * (len(means) - 1))]
    upper = means[int(0.975 * (len(means) - 1))]
    center = sum(deltas) / len(deltas)
    return center, lower, upper


def sign_test_pvalue(deltas: list[float]) -> float:
    positive = sum(delta > 0 for delta in deltas)
    negative = sum(delta < 0 for delta in deltas)
    trials = positive + negative
    if trials == 0:
        return 1.0
    tail = min(positive, negative)
    probability = 0.0
    for k in range(tail + 1):
        probability += math.comb(trials, k) * (0.5**trials)
    return min(1.0, 2.0 * probability)


def compute_paired_metric_stats(
    candidate_rows: dict[str, dict[str, Any]],
    reference_rows: dict[str, dict[str, Any]],
    *,
    metrics: list[str],
    iterations: int,
    seed: int,
) -> dict[str, Any]:
    shared_ids = sorted(set(candidate_rows) & set(reference_rows))
    if not shared_ids:
        raise ValueError("No shared utt_id rows between candidate and reference.")

    results: dict[str, Any] = {
        "num_examples": len(shared_ids),
        "metrics": {},
    }
    for metric in metrics:
        direction = metric_direction(metric)
        deltas = []
        for utt_id in shared_ids:
            candidate_value = candidate_rows[utt_id].get(metric)
            reference_value = reference_rows[utt_id].get(metric)
            if candidate_value is None or reference_value is None:
                continue
            delta = float(candidate_value) - float(reference_value)
            if direction == "lower":
                delta = -delta
            deltas.append(delta)
        if not deltas:
            continue
        mean_delta, ci_low, ci_high = paired_bootstrap(deltas, iterations, seed)
        results["metrics"][metric] = {
            "direction": direction,
            "mean_improvement": mean_delta,
            "ci95_low": ci_low,
            "ci95_high": ci_high,
            "sign_test_pvalue": sign_test_pvalue(deltas),
            "num_pairs": len(deltas),
        }
    return results
