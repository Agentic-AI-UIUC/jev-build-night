# Jev Build Night

Agentic AI @ UIUC · Monday build night.

Tonight your group asks Jev questions about a small dataset.
Jev is a decision model from TypeSafe. You give it text and typed questions. It gives you numbers.
You do three sprints. Each sprint adds one step to the same code.

```
SPRINT 1  CALL       s1_call.py     ask Jev one question about 3 rows
SPRINT 2  MEASURE    s2_measure.py  ask about 20 labeled rows, get accuracy
SPRINT 3  JEV + LLM  s3_gate.py     send the low-confidence rows to an LLM, print the demo card
```

## Setup

Only one laptop in each group must work.

1. Install [uv](https://docs.astral.sh/uv/) if you do not have it: `brew install uv`.
2. Get the code:

   ```bash
   git clone https://github.com/Agentic-AI-UIUC/jev-build-night.git
   cd jev-build-night
   cp .env.example .env
   uv sync
   ```

3. Open `.env`. Set `GROUP` to your group: `scam`, `injection`, `tickets`, `email`, or `reviews`.
4. Write the key from your group card in `OPENROUTER_API_KEY`.
   Do not show the key on a screen. Do not commit `.env`.
5. Run Sprint 1:

   ```bash
   uv run sprints/s1_call.py
   ```

   The first run prints the question template for your group.

## The groups

| GROUP | Data | Question type |
|---|---|---|
| `scam` | Scam text messages | Noul (yes / no) |
| `injection` | Prompt injection | Noul (yes / no) |
| `tickets` | Support tickets | Choice (one team) |
| `email` | Email priority | Choice (one level) |
| `reviews` | Review stars | Score (1 to 5) |

Each group has 20 labeled rows in `data/<group>/rows.csv`.

## The sprints

Each file has one TODO. Do the TODO, then run the file.

| Sprint | Run | TODO | Done when |
|---|---|---|---|
| 1 Call | `uv run sprints/s1_call.py` | Write `QUESTION` | You see Jev's answer for 3 rows |
| 2 Measure | `uv run sprints/s2_measure.py` | Write `get_answers()`. Then change the question words (2b) | You have an accuracy number |
| 3 Jev + LLM | `uv run sprints/s3_gate.py` | Set `THRESHOLD`, write `final_answer()`, write `GUESS` | The demo card prints |

Sprint 3 sends the rows where Jev is not sure to `openai/gpt-6-luna`.
It uses the same key.

## Cache mode (no key, no network)

If the key or the network fails, set this in `.env`:

```
JEV_MODE=cache
```

Cache mode uses saved answers. It works with no key and no network.
Cache mode has only 3 prepared questions. Your own words use prepared question 1 (`task.variants[0]`).
To compare questions in cache mode, use `QUESTION = task.variants[0]`, `[1]`, or `[2]`.
The first prepared question is the best one.

## If something goes wrong

| You see | Do this |
|---|---|
| `TODO 1 is not done yet` | Write your `QUESTION` in `s1_call.py` |
| `401` | The key in `.env` is wrong. Copy it again from the card |
| `retrying…` many times | The network is slow. Wait, or set `JEV_MODE=cache` |
| `Set GROUP in .env to one of` | Set `GROUP` in `.env` to one of the five names |

A full log is in `logs/jevkit.log`.

## Tests

```bash
uv run --group dev python -m pytest
```

## Links

- TypeSafe docs: https://docs.typesafe.ai
- OpenRouter: https://openrouter.ai
