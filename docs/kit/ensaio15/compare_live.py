"""Compara, caso a caso, duas pastas com live_*.json + judge.json (antes × depois): regra e juiz.

  python compare_live.py <pasta antes> <pasta depois>
"""
import json
import sys
from pathlib import Path

before, after = Path(sys.argv[1]), Path(sys.argv[2])
def load(d):
    rows = {}
    for f in d.glob("live_*.json"):
        for r in json.loads(f.read_text())["rows"]:
            bad = [k for k, v in (r.get("checks") or {}).items() if v is False]
            rows[(r["id"], r.get("run", 0))] = {"regra": not bad, "falha": bad}
    j = json.loads((d / "judge.json").read_text())
    for v in j["verdicts"]:
        vv = v.get("verdict") or v
        k = (v["id"], v.get("run", 0))
        if k in rows:
            rows[k]["juiz"] = bool(vv.get("grounded")) and bool(vv.get("helpful"))
            rows[k]["tipo"] = vv.get("failure_type")
    return rows
A, B = load(before), load(after)
def ok(x): return x.get("regra") and x.get("juiz", True)
for name, rows in (("antes", A), ("depois", B)):
    judged = [x for x in rows.values() if "juiz" in x]
    print(f"{name}: regra {sum(x['regra'] for x in rows.values())}/{len(rows)} · "
          f"juiz {sum(x['juiz'] for x in judged)}/{len(judged)}")
for k in sorted(set(A) | set(B)):
    a, b = A.get(k, {}), B.get(k, {})
    if ok(a) != ok(b) or "juiz" not in b:
        tag = "MELHOROU" if ok(b) and not ok(a) else ("PIOROU" if ok(a) and not ok(b) else "sem juiz")
        print(tag, k[0], "antes", a.get("falha"), a.get("tipo"), "→ depois", b.get("falha"), b.get("tipo"))
