"""Score Jev against the labels."""
from dataclasses import dataclass


def _by_id(rows):
    return {r.id: r for r in rows}


def accuracy(rows, answers) -> tuple[int, int]:
    truth = _by_id(rows)
    return sum(a.pick == truth[a.row_id].label for a in answers), len(answers)


def split_by_confidence(rows, answers, threshold):
    """(correct, total) for answers at or above the threshold, then below it."""
    high = [a for a in answers if a.confidence >= threshold]
    low = [a for a in answers if a.confidence < threshold]
    return accuracy(rows, high), accuracy(rows, low)


def wrong_rows(rows, answers):
    """Wrong answers as (row, answer), the most confident mistake first."""
    truth = _by_id(rows)
    wrong = [(truth[a.row_id], a) for a in answers if a.pick != truth[a.row_id].label]
    return sorted(wrong, key=lambda ra: -ra[1].confidence)


@dataclass(frozen=True)
class Gate:
    jev_rows: int
    jev_correct: int
    llm_rows: int
    llm_correct: int

    @property
    def correct(self):
        return self.jev_correct + self.llm_correct

    @property
    def total(self):
        return self.jev_rows + self.llm_rows


def gate(rows, jev_answers, llm_answers: dict, threshold) -> Gate:
    """Keep Jev's answer at or above the threshold; use the LLM's answer below it."""
    truth = _by_id(rows)
    kept = [a for a in jev_answers if a.confidence >= threshold]
    sent = [llm_answers[a.row_id] for a in jev_answers if a.confidence < threshold]
    ok = lambda xs: sum(a.pick == truth[a.row_id].label for a in xs)
    return Gate(len(kept), ok(kept), len(sent), ok(sent))
