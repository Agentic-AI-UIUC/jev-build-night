"""Turn a raw Jev answer into one pick plus one confidence number."""
from dataclasses import dataclass

# Jev's score is a position on your list of levels. We assume 0 = first level.
# CHECK this at the real-key test: if picks are off by one star, set SCORE_BASE = 1.
SCORE_BASE = 0


@dataclass(frozen=True)
class Answer:
    row_id: int
    pick: object
    confidence: float | None  # None for LLM answers


def normalize(qtype: str, labels: list, raw: dict, row_id: int = 0) -> Answer:
    if qtype == "noul":
        p = float(raw["noul"])
        return Answer(row_id, labels[0] if p >= 0.5 else labels[1], max(p, 1 - p))
    if qtype == "choice":
        probs = raw.get("probabilities") or {}
        conf = max(probs.values()) if probs else float(raw.get("confidence", 0.0))
        return Answer(row_id, raw["choice"], conf)
    if qtype == "score":
        score = float(raw["score"])
        level = min(max(round(score) - SCORE_BASE, 0), len(labels) - 1)
        probs = raw.get("probabilities") or {}
        conf = max(probs.values()) if probs else 1 - 2 * abs(score - round(score))
        return Answer(row_id, labels[level], conf)
    raise ValueError(f"unknown question type {qtype!r}")
