"""SPRINT 3 · JEV + LLM — Jev answers when it is sure; an LLM answers the rest.

Run:        uv run sprints/s3_gate.py
Done when:  your DEMO CARD prints. Put it on the projector for the demo.
"""
from jevkit import accuracy, ask_llm
from jevkit.report import header, print_card, show_gate_table, todo

from s2_measure import QUESTION, get_answers, task

# TODO 3a: pick your threshold. Look at the table first, then choose.
THRESHOLD = 0.9

# TODO 3c: look at the SURPRISE row on your card. Why do you think Jev got it wrong?
GUESS = "TODO"


def final_answer(jev_answer, llm_answers):
    # TODO 3b: if jev_answer.confidence >= THRESHOLD, keep jev_answer.
    #   Otherwise return the LLM's answer for that row: llm_answers[jev_answer.row_id]
    todo("3b", "final_answer() in sprints/s3_gate.py")


if __name__ == "__main__":
    header(task)
    jev = get_answers()
    unsure = [row for row, a in zip(task.rows, jev) if a.confidence < max(THRESHOLD, 0.95)]
    llm = ask_llm(task, QUESTION, unsure)
    show_gate_table(task, jev, llm)
    final = [final_answer(a, llm) for a in jev]
    c, t = accuracy(task.rows, final)
    print(f"  YOUR FLOW at {THRESHOLD:.2f}: {c} / {t} correct\n")
    print_card(task, QUESTION, jev, llm, THRESHOLD, GUESS)
