"""Ao vivo só com os casos de um arquivo, numa cópia descartável da tentativa, e o juiz reaproveitando canários e
calibração do judge.json gravado (mesmo modelo e prompt). Uso:
  LLM_PROVIDER=anthropic LIVE_EVAL_ALLOW_STALE_GATE=1 python live_subset.py <repo> <casos.jsonl> <saida> <splits>
      <repeat> <teto conversas> <teto juiz>"""
import json
import sys
from pathlib import Path

repo, cases, out, splits, rep, mx, jmx = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4], \
    sys.argv[5], sys.argv[6], float(sys.argv[7])
sys.path.insert(0, str(repo / "src"))
sys.path.insert(0, str(repo))
from evals import judge, run_evals  # noqa: E402

out.mkdir(parents=True, exist_ok=True)
run_evals.CASES = cases
run_evals.HELDOUT = repo / "var" / "nenhum.jsonl"
run_evals.RESULTS_DIR = out
run_evals.RESULTS = repo / "evals" / "results" / "latest.json"
code = run_evals.main(["--live", "--splits", splits, "--repeat", rep, "--workers", "8", "--max-usd", mx])
files = sorted(out.glob("live_*.json"))
head = json.loads((repo / "evals" / "results" / "judge.json").read_text(encoding="utf-8"))
TRUST = ("canaries", "calibration_pairs", "calibration_refused", "model", "prompt_sha")
trust = {k: head[k] for k in TRUST if k in head}
from app.llm import get_judge_llm  # noqa: E402

rep_j = judge.run(get_judge_llm(), files, max_usd=jmx, previous=trust, reuse_trust=True)
(out / "judge.json").write_text(json.dumps(rep_j, indent=2, ensure_ascii=False), encoding="utf-8")
spent = sum(float(json.loads(f.read_text())["spent_usd"] or 0) for f in files)
print(f"CONVERSAS US$ {spent:.3f} · JUIZ US$ {rep_j.get('spent_usd')} · status {rep_j.get('status')} · "
      f"trust_reused {rep_j.get('trust_reused')} · rc {code}")
ver = {}
for v in rep_j.get("verdicts", []):
    vv = v.get("verdict") or v
    ver.setdefault(v["id"], []).append((vv.get("grounded"), vv.get("helpful"), vv.get("failure_type")))
for f in files:
    for r in json.loads(f.read_text())["rows"]:
        bad = [k for k, val in (r.get("checks") or {}).items() if val is False]
        print(r["id"], r.get("run"), "regra:", "ok" if not bad else bad)
for i, vs in sorted(ver.items()):
    print("JUIZ", i, vs)
