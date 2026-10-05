"""SPRINT 1 · CALL — ask Jev one question about your data.

Run:        uv run sprints/s1_call.py
Done when:  you see Jev's answer and confidence for 3 rows.
"""
from jevkit import ask_jev, load_task
from jevkit.report import header

task = load_task()

# TODO 1: write your question for Jev.
#   Run this file once: it prints the exact shape for your group.
#   Tip: describe each option clearly. Jev can only pick from your options.
#   No key? Use one of the prepared questions:  QUESTION = task.variants[0]
QUESTION = {
    "instructions": "TODO",
    "criteria": "TODO",
}

if __name__ == "__main__":
    header(task)
    for row in task.rows[:3]:
        answer = ask_jev(task, QUESTION, [row])[0]
        print(f"  row {row.id}: {row.text[:72]}")
        print(f"     Jev: {answer.pick}   confidence: {answer.confidence:.2f}   (label: {row.label})\n")
