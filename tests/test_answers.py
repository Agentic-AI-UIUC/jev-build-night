import pytest

from jevkit.answers import normalize


def test_noul_yes_and_confidence():
    a = normalize("noul", ["yes", "no"], {"type": "noul", "noul": 0.8})
    assert a.pick == "yes"
    assert a.confidence == pytest.approx(0.8)


def test_noul_no_uses_distance_from_half():
    a = normalize("noul", ["yes", "no"], {"type": "noul", "noul": 0.1})
    assert a.pick == "no"
    assert a.confidence == pytest.approx(0.9)


def test_choice_uses_max_probability():
    raw = {"type": "choice", "choice": "billing",
           "probabilities": {"billing": 0.7, "technical": 0.2, "account": 0.1}}
    a = normalize("choice", ["billing", "technical", "account"], raw)
    assert a.pick == "billing"
    assert a.confidence == pytest.approx(0.7)


def test_choice_falls_back_to_confidence_field():
    a = normalize("choice", ["a", "b"], {"type": "choice", "choice": "b", "confidence": 0.6})
    assert (a.pick, a.confidence) == ("b", pytest.approx(0.6))


def test_score_maps_zero_based_level_to_stars():
    a = normalize("score", [1, 2, 3, 4, 5], {"type": "score", "score": 3.1})
    assert a.pick == 4
    assert a.confidence == pytest.approx(0.8)


def test_score_is_clamped_to_labels():
    a = normalize("score", [1, 2, 3, 4, 5], {"type": "score", "score": 4.4})
    assert a.pick == 5
