"""docs/CI.md: o resultado da CI de um commit, para quem lê o repositório sem abrir o Actions.

Por quê: quem lê o repositório nem sempre abre o histórico do Actions. A CI roda no GitHub; este script escreve,
a partir do JSON da execução (o que a API do GitHub devolve para a run e os jobs; na nuvem quem busca é a sessão, pela
ferramenta do GitHub), uma tabela com cada job, resultado e duração, o commit e o link.
Uso: python scripts/ci_summary.py var/ci_run.json [--out docs/CI.md]
Entrada: {"run": {html_url, head_sha, conclusion, created_at, updated_at, name}, "jobs": [{name, conclusion,
started_at, completed_at}]} (aceita também {"jobs": {"jobs": [...]}}, o formato da API).
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _ts(value: str | None) -> datetime.datetime | None:
    if not value:
        return None
    return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))


def _dur(a: str | None, b: str | None) -> str:
    x, y = _ts(a), _ts(b)
    if not (x and y):
        return "—"
    s = int((y - x).total_seconds())
    return f"{s // 60} min {s % 60:02d} s"


def render(data: dict) -> str:
    run = data.get("run") or {}
    jobs = data.get("jobs") or []
    if isinstance(jobs, dict):
        jobs = jobs.get("jobs") or []
    ok = sum(j.get("conclusion") == "success" for j in jobs)
    ordered = sorted(jobs, key=lambda j: j.get("name") or "")
    rows = [f"| {j.get('name')} | {j.get('conclusion') or j.get('status') or '—'} | "
            f"{_dur(j.get('started_at'), j.get('completed_at'))} |" for j in ordered]
    return "\n".join([
        "# Integração contínua",
        "",
        f"Execução `{run.get('name') or 'CI'}` do commit `{str(run.get('head_sha') or '')[:7]}`: "
        f"**{run.get('conclusion') or run.get('status') or '—'}**, {ok} de {len(jobs)} jobs verdes, "
        f"{_dur(run.get('created_at'), run.get('updated_at'))} do início ao fim. Link: {run.get('html_url') or '—'}",
        "",
        "| job | resultado | duração |",
        "|---|---|---:|",
        *rows,
        "",
        "Gerado por `scripts/ci_summary.py` a partir da execução no GitHub Actions; a CI é a mesma em todo push.",
        "",
    ])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_json", type=Path)
    ap.add_argument("--out", type=Path, default=ROOT / "docs" / "CI.md")
    args = ap.parse_args(argv)
    args.out.write_text(render(json.loads(args.run_json.read_text(encoding="utf-8"))), encoding="utf-8")
    print(f"gravado {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
