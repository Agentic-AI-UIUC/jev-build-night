from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "data"


@pytest.fixture
def cache_env(monkeypatch):
    monkeypatch.setenv("JEV_DATA_DIR", str(FIXTURES))
    monkeypatch.setenv("GROUP", "mini")
    monkeypatch.setenv("JEV_MODE", "cache")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("JEV_VARIANT", raising=False)
