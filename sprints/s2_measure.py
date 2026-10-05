"""SPRINT 2 · MEASURE — how often is Jev right, and is its confidence honest?

Run:        uv run sprints/s2_measure.py
Done when:  you have an accuracy number, and you read the most confident WRONG row.
"""
from jevkit import ask_jev
from jevkit.report import header, show_measure, todo

from s1_call import QUESTION, task


def get_answers():
    # TODO 2: ask Jev your QUESTION about EVERY row in task.rows, and return the answers.
    #   Hint: look at how s1_call.py calls ask_jev. Jev answers all rows in parallel.
    todo("2", "get_answers() in sprints/s2_measure.py")


if __name__ == "__main__":
    header(task)
    show_measure(task, get_answers())
    # TODO 2b (if time): change QUESTION in s1_call.py and run again. Can you beat your number?
