"""Load your group's dataset and task."""
import csv
import json
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from .log import get_logger

log = get_logger("data")
_ROOT = Path(__file__).resolve().parent.parent
GROUPS = ["scam", "injection", "tickets", "email", "reviews"]


@dataclass(frozen=True)
class Row:
    id: int
    text: str
    label: object


@dataclass(frozen=True)
class Task:
    group: str
    name: str
    type: str
    labels: list
    state_key: str
    variants: list
    rows: list
    dir: Path


def data_dir() -> Path:
    return Path(os.getenv("JEV_DATA_DIR", _ROOT / "data"))


def load_task(group: str | None = None) -> Task:
    load_dotenv(_ROOT / ".env")
    group = group or os.getenv("GROUP", "").strip()
    d = data_dir() / group
    if not group or not d.is_dir():
        raise SystemExit(f"Set GROUP in .env to one of: {', '.join(GROUPS)} (now: {group!r})")
    spec = json.loads((d / "task.json").read_text())
    labels = spec["labels"]
    as_label = int if spec["type"] == "score" else str
    with open(d / "rows.csv", newline="") as f:
        rows = [Row(int(r["id"]), r["text"], as_label(r["label"])) for r in csv.DictReader(f)]
    log.info("loaded group=%s type=%s rows=%d", group, spec["type"], len(rows))
    return Task(group, spec["name"], spec["type"], labels, spec["state_key"], spec["variants"], rows, d)
