"""Logging for jevkit. Full detail goes to logs/jevkit.log; the terminal shows warnings only."""
import logging
import os
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent


def get_logger(feature: str) -> logging.Logger:
    root = logging.getLogger("jevkit")
    if not root.handlers:
        root.setLevel(os.getenv("LOG_LEVEL", "DEBUG").upper())
        log_dir = _ROOT / "logs"
        log_dir.mkdir(exist_ok=True)
        fh = logging.FileHandler(log_dir / "jevkit.log")
        fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))
        root.addHandler(fh)
        sh = logging.StreamHandler()
        sh.setLevel(logging.WARNING)
        sh.setFormatter(logging.Formatter("[%(name)s] %(message)s"))
        root.addHandler(sh)
    return root.getChild(feature)
