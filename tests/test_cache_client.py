import pytest

from jevkit import ask_jev, ask_llm, load_task
from jevkit.client import QuestionNotReady, cost_so_far, reset_cost


def test_load_task_reads_rows(cache_env):
    task = load_task()
    assert task.name == "Mini scam"
    assert [r.label for r in task.rows] == ["yes", "no", "yes", "no"]


def test_cache_mode_matching_variant(cache_env):
    task = load_task()
    reset_cost()
    answers = ask_jev(task, task.variants[0], task.rows)
    assert [a.pick for a in answers] == ["yes", "no", "no", "yes"]
    assert cost_so_far() == pytest.approx(0.00004)


def test_cache_mode_own_question_falls_back_to_variant_1(cache_env, capsys):
    task = load_task()
    answers = ask_jev(task, {"instructions": "my own words", "criteria": {"true": "x", "false": "y"}}, task.rows[:1])
    assert answers[0].pick == "yes"
    assert "prepared question 1" in capsys.readouterr().out


def test_todo_question_is_rejected_with_skeleton(cache_env):
    task = load_task()
    with pytest.raises(QuestionNotReady) as e:
        ask_jev(task, {"instructions": "TODO", "criteria": {"true": "TODO", "false": "TODO"}}, task.rows)
    assert '"true"' in str(e.value)


def test_cache_llm(cache_env):
    task = load_task()
    out = ask_llm(task, task.variants[0], task.rows[2:3])
    assert out[3].pick == "yes"
