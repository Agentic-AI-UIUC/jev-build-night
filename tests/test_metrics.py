from jevkit.answers import Answer
from jevkit.data import Row
from jevkit.metrics import accuracy, gate, split_by_confidence, wrong_rows

ROWS = [Row(1, "a", "yes"), Row(2, "b", "no"), Row(3, "c", "yes"), Row(4, "d", "no")]
JEV = [Answer(1, "yes", 0.97), Answer(2, "no", 0.95), Answer(3, "no", 0.70), Answer(4, "yes", 0.95)]


def test_accuracy_counts_correct_rows():
    assert accuracy(ROWS, JEV) == (2, 4)


def test_split_by_confidence():
    high, low = split_by_confidence(ROWS, JEV, 0.9)
    assert high == (2, 3)
    assert low == (0, 1)


def test_wrong_rows_most_confident_first():
    wrong = wrong_rows(ROWS, JEV)
    assert [r.id for r, _ in wrong] == [4, 3]


def test_gate_sends_low_confidence_rows_to_llm():
    llm = {3: Answer(3, "yes", None)}
    g = gate(ROWS, JEV, llm, 0.9)
    assert g.jev_rows == 3 and g.jev_correct == 2
    assert g.llm_rows == 1 and g.llm_correct == 1
    assert (g.correct, g.total) == (3, 4)
