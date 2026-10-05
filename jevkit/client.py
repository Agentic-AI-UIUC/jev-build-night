"""Call Jev and the LLM through OpenRouter, or replay saved answers in cache mode."""
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor

import httpx

from .answers import Answer, normalize
from .log import get_logger

log = get_logger("client")

JEV_URL = "https://openrouter.ai/api/alpha/decisions"
JEV_MODEL = "typesafe/jev-1.13"
LLM_URL = "https://openrouter.ai/api/v1/chat/completions"
LLM_MODEL = "openai/gpt-6-luna"
RETRY_STATUS = {429, 500, 502, 503, 529}
_cost = {"usd": 0.0}
_simulated = {"seen": False}


class QuestionNotReady(SystemExit):
    """The question still has TODO in it."""


def cost_so_far() -> float:
    return _cost["usd"]


def reset_cost() -> None:
    _cost["usd"] = 0.0


def used_simulated_cache() -> bool:
    return _simulated["seen"]


def mode() -> str:
    m = os.getenv("JEV_MODE", "").strip().lower()
    if m in ("live", "cache"):
        return m
    return "live" if os.getenv("OPENROUTER_API_KEY") else "cache"


def skeleton(task) -> str:
    if task.type == "noul":
        criteria = '{\n        "true": "TODO: what YES means",\n        "false": "TODO: what NO means",\n    }'
    elif task.type == "choice":
        body = "".join(f'        "{k}": "TODO: what {k} means",\n' for k in task.labels)
        criteria = "{\n" + body + "    }"
    else:
        body = "".join(f'        "TODO: what {s} star{"s" * (s > 1)} means",\n' for s in task.labels)
        criteria = "[\n" + body + "    ]"
    return f'QUESTION = {{\n    "instructions": "TODO: one clear question about the {task.state_key}",\n    "criteria": {criteria},\n}}'


def _check_ready(task, question):
    if "TODO" in json.dumps(question):
        raise QuestionNotReady(
            "\nYour QUESTION in sprints/s1_call.py still has TODO in it.\n"
            f"For the '{task.group}' group ({task.type}), it must look like this:\n\n{skeleton(task)}\n"
        )


def _post(url, payload, what):
    key = os.getenv("OPENROUTER_API_KEY", "")
    if not key:
        raise SystemExit("No OPENROUTER_API_KEY in .env. Paste the key from your group's card, or set JEV_MODE=cache.")
    for attempt in range(5):
        t0 = time.time()
        try:
            r = httpx.post(url, json=payload, headers={"Authorization": f"Bearer {key}"}, timeout=30)
        except httpx.HTTPError as e:
            log.warning("%s network error (%s), retrying…", what, e)
            time.sleep(2 ** attempt)
            continue
        log.debug("%s status=%s ms=%d", what, r.status_code, (time.time() - t0) * 1000)
        if r.status_code in RETRY_STATUS:
            log.warning("%s got %s, retrying…", what, r.status_code)
            time.sleep(2 ** attempt)
            continue
        if r.status_code >= 400:
            log.error("%s failed status=%s body=%s", what, r.status_code, r.text[:300])
            raise SystemExit(f"{what} failed ({r.status_code}): {r.text[:200]}\nTip: set JEV_MODE=cache in .env to keep going.")
        return r.json()
    raise SystemExit(f"{what} kept failing. Set JEV_MODE=cache in .env to keep going.")


def _load_cache(task, name):
    data = json.loads((task.dir / "cache" / name).read_text())
    if data.get("simulated"):
        _simulated["seen"] = True
    return data


_told_variant: list[int] = []


def _cache_variant(task, question) -> int:
    for i, v in enumerate(task.variants, start=1):
        if v == question:
            return i
    n = int(os.getenv("JEV_VARIANT", "1"))
    if not _told_variant:
        print(f"(cache mode: your own words need a live key, so this uses prepared question {n})")
        _told_variant.append(n)
    return n


def ask_jev(task, question, rows) -> list[Answer]:
    """Ask Jev one question about each row. Returns one Answer per row, in order."""
    _check_ready(task, question)
    log.info("ask_jev group=%s mode=%s rows=%d", task.group, mode(), len(rows))
    if mode() == "cache":
        data = _load_cache(task, f"jev_v{_cache_variant(task, question)}.json")
        for r in rows:
            _cost["usd"] += data.get("usage", {}).get(str(r.id), {}).get("cost", 0.0)
        return [normalize(task.type, task.labels, data["answers"][str(r.id)], r.id) for r in rows]

    def one(row):
        body = {"model": JEV_MODEL, "state": {task.state_key: row.text},
                "questions": {"q": {"type": task.type, **question}}}
        resp = _post(JEV_URL, body, f"Jev row {row.id}")
        _cost["usd"] += resp.get("usage", {}).get("cost", 0.0)
        return normalize(task.type, task.labels, resp["answers"]["q"], row.id)

    with ThreadPoolExecutor(max_workers=8) as pool:
        out = list(pool.map(one, rows))
    log.info("ask_jev done rows=%d cost=%.6f", len(out), cost_so_far())
    return out


def _parse_label(task, text):
    t = text.strip().lower()
    for label in task.labels:
        if t == str(label).lower():
            return label
    for label in sorted(task.labels, key=lambda x: -len(str(x))):
        if str(label).lower() in t:
            return label
    log.warning("LLM reply not a label: %r", text[:80])
    return None


def ask_llm(task, question, rows) -> dict[int, Answer]:
    """Ask the LLM the same question about each row. Returns {row id: Answer}."""
    log.info("ask_llm group=%s mode=%s rows=%d", task.group, mode(), len(rows))
    if mode() == "cache":
        data = _load_cache(task, "llm.json")
        return {r.id: Answer(r.id, data["answers"][str(r.id)], None) for r in rows}
    options = ", ".join(str(x) for x in task.labels)

    def one(row):
        msgs = [
            {"role": "system", "content": f"Answer with exactly one of: {options}. No other words."},
            {"role": "user", "content": f"{question['instructions']}\nOptions: {json.dumps(question['criteria'])}\n\n{task.state_key}: {row.text}"},
        ]
        resp = _post(LLM_URL, {"model": LLM_MODEL, "messages": msgs, "max_tokens": 10}, f"LLM row {row.id}")
        _cost["usd"] += resp.get("usage", {}).get("cost", 0.0)
        return row.id, Answer(row.id, _parse_label(task, resp["choices"][0]["message"]["content"]), None)

    with ThreadPoolExecutor(max_workers=8) as pool:
        return dict(pool.map(one, rows))
