"""Rodada 17: docs/CI.md com cada job, resultado e duração, para quem não abre o Actions."""
from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "ci_summary.py"
spec = importlib.util.spec_from_file_location("ci", SCRIPT)
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)


def test_renders_jobs_with_duration_and_counts_green():
    md = ci.render({"run": {"name": "CI", "head_sha": "abcdef123", "conclusion": "success",
                            "created_at": "2026-11-05T10:00:00Z", "updated_at": "2026-11-05T10:09:30Z",
                            "html_url": "https://github.com/o/r/actions/runs/1"},
                    "jobs": {"jobs": [{"name": "check (core)", "conclusion": "success",
                                       "started_at": "2026-11-05T10:00:10Z", "completed_at": "2026-11-05T10:05:10Z"},
                                      {"name": "check (docker)", "conclusion": "failure"}]}})
    assert "`abcdef1`" in md and "**success**" in md and "1 de 2 jobs verdes" in md and "9 min 30 s" in md
    assert "| check (core) | success | 5 min 00 s |" in md and "| check (docker) | failure | — |" in md
