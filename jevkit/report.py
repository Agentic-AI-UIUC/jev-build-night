"""Printing helpers so the sprint files stay short."""
from .card import demo_card
from .client import cost_so_far, mode, used_simulated_cache
from .metrics import accuracy, gate, split_by_confidence, wrong_rows


def todo(number: str, what: str):
    raise SystemExit(f"\nTODO {number} is not done yet: {what}\n")


def header(task):
    print(f"\n  GROUP {task.name}  ·  question type: {task.type}  ·  mode: {mode()}\n")


def show_measure(task, answers, threshold=0.9):
    c, t = accuracy(task.rows, answers)
    high, low = split_by_confidence(task.rows, answers, threshold)
    print(f"  ACCURACY        {c} / {t} correct  ({100 * c / t:.0f}%)")
    print(f"  conf ≥ {threshold:.2f}     {high[0]} / {high[1]} correct")
    print(f"  conf < {threshold:.2f}     {low[0]} / {low[1]} correct\n")
    wrong = wrong_rows(task.rows, answers)
    print(f"  WRONG ROWS ({len(wrong)}), most confident first:")
    for row, a in wrong[:5]:
        print(f"   #{row.id:<2} Jev {a.pick!s:<9} {a.confidence:.2f} · label {row.label!s:<9} {row.text[:34]}…")
    if not wrong:
        print("   none. Jev got every row right.")
    print()


def show_gate_table(task, jev, llm, thresholds=(0.7, 0.8, 0.9, 0.95)):
    print("  THRESHOLD   Jev alone      sent to LLM    full flow")
    for th in thresholds:
        g = gate(task.rows, jev, llm, th)
        print(f"    {th:.2f}      {g.jev_rows:>2} rows {g.jev_correct:>2} ok   {g.llm_rows:>2} rows {g.llm_correct:>2} ok   {g.correct} / {g.total}")
    print()


def print_card(task, question, jev, llm, threshold, guess):
    high, low = split_by_confidence(task.rows, jev, threshold)
    wrong = wrong_rows(task.rows, jev)
    surprise = (wrong[0][0].text, wrong[0][1].pick, wrong[0][1].confidence) if wrong else None
    if "TODO" in guess:
        guess = "______________________ (fill in GUESS in s3_gate.py)"
    print(demo_card(
        group=task.name, qtype=task.type, instructions=question["instructions"],
        acc=accuracy(task.rows, jev), high=high, low=low, surprise=surprise, guess=guess,
        threshold=threshold, g=gate(task.rows, jev, llm, threshold), cost=cost_so_far(),
        simulated=used_simulated_cache(),
    ))
