from jevkit.card import demo_card
from jevkit.metrics import Gate


def test_card_has_all_four_parts_and_sim_banner():
    card = demo_card(
        group="Mini scam", qtype="noul", instructions="Is this a scam?",
        acc=(17, 20), high=(10, 10), low=(7, 10),
        surprise=("Your package is held. Pay $1.99", "no", 0.94), guess="Looks like a real shipping text",
        threshold=0.9, g=Gate(12, 12, 8, 7), cost=0.0004, simulated=True,
    )
    for part in ["1 TASK", "2 NUMBER", "3 SURPRISE", "4 GATE", "17 / 20", "19 / 20", "SIMULATED"]:
        assert part in card
    widths = {len(line) for line in card.splitlines()}
    assert len(widths) == 1, "every card line has the same width"


def test_long_text_is_cut_to_two_lines():
    card = demo_card(
        group="G", qtype="noul", instructions="word " * 60, acc=(1, 2), high=(1, 1), low=(0, 1),
        surprise=("long " * 60, "yes", 0.95), guess="x", threshold=0.9, g=Gate(1, 1, 1, 0),
        cost=0.0, simulated=False,
    )
    assert card.count("…") == 2
    assert len(card.splitlines()) <= 24
