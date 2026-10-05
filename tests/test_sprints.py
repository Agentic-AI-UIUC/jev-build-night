"""The unfilled starter must fail with a helpful message, not a stack trace."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(script, group="scam"):
    env = {**os.environ, "GROUP": group, "JEV_MODE": "cache", "OPENROUTER_API_KEY": ""}
    env.pop("JEV_DATA_DIR", None)
    return subprocess.run([sys.executable, f"sprints/{script}"], cwd=ROOT, env=env, capture_output=True, text=True)


def test_unfilled_s1_prints_skeleton_for_group():
    r = run("s1_call.py", "tickets")
    assert r.returncode == 1
    assert '"billing": "TODO' in r.stderr
    assert "Traceback" not in r.stderr


def test_unfilled_s2_points_at_todo_2():
    r = run("s2_measure.py")
    assert r.returncode == 1
    assert "TODO" in r.stderr and "Traceback" not in r.stderr
