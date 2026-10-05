"""The demo card that each group shows at the end."""
import textwrap

W = 63  # inner width


def _line(text=""):
    return f"│ {text[:W - 2]:<{W - 2}} │"


def _bar(n, total, width=20):
    filled = round(width * n / total) if total else 0
    return "█" * filled + "░" * (width - filled)


def _wrap2(text, width, max_lines=2):
    """At most max_lines lines; end with … when the text is cut."""
    lines = textwrap.wrap(text, width)
    if len(lines) > max_lines:
        lines = lines[: max_lines - 1] + [lines[max_lines - 1][: width - 1].rstrip() + "…"]
    return lines or [""]


def _pct(c, t):
    return f"{100 * c / t:.0f}%" if t else "—"


def demo_card(*, group, qtype, instructions, acc, high, low, surprise, guess, threshold, g, cost, simulated):
    out = ["╭" + "─" * W + "╮"]
    if simulated:
        out.append(_line("⚠ SIMULATED CACHE: practice numbers, not real Jev"))
    out.append(_line(f"{group.upper()}"))
    out.append("├" + "─" * W + "┤")
    for i, chunk in enumerate(_wrap2(f'"{instructions}"  ({qtype})', W - 14)):
        out.append(_line(("1 TASK      " if i == 0 else " " * 12) + chunk))
    out.append(_line())
    out.append(_line(f"2 NUMBER    {'Jev alone:':<14}{acc[0]} / {acc[1]} correct  ({_pct(*acc)})"))
    out.append(_line(f"            {f'conf ≥ {threshold:.2f}:':<14}{high[0]} / {high[1]} correct"))
    out.append(_line(f"            {f'conf < {threshold:.2f}:':<14}{low[0]} / {low[1]} correct"))
    out.append(_line())
    if surprise:
        text, pick, conf = surprise
        out.append(_line(f"3 SURPRISE  Jev said {str(pick).upper()} at {conf:.2f} confidence:"))
        for chunk in _wrap2(f'"{text}"', W - 14, max_lines=3):
            out.append(_line(" " * 12 + chunk))
    else:
        out.append(_line("3 SURPRISE  Jev made no mistakes. Try a harder question."))
    for i, chunk in enumerate(_wrap2(f"Our guess: {guess}", W - 14)):
        out.append(_line(" " * 12 + chunk))
    out.append(_line())
    out.append(_line(f"4 GATE      threshold {threshold:.2f}"))
    out.append(_line(f"            Jev alone   {_bar(g.jev_rows, g.total)} {g.jev_rows:>2} rows {_pct(g.jev_correct, g.jev_rows):>4}"))
    out.append(_line(f"            sent to LLM {_bar(g.llm_rows, g.total)} {g.llm_rows:>2} rows {_pct(g.llm_correct, g.llm_rows):>4}"))
    out.append(_line(f"            full flow   {g.correct} / {g.total} correct  ({_pct(g.correct, g.total)})"))
    out.append(_line(f"            cost        ${cost:.4f}"))
    out.append("╰" + "─" * W + "╯")
    return "\n".join(out)
