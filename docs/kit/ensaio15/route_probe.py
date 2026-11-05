"""Router-only, ao vivo (Haiku): intenção e standalone de cada caso official+memory, com o histórico tirado do cassete
gravado na fumaça (a resposta do atendimento de cada turno anterior).

  DOMAIN=challenge LLM_PROVIDER=anthropic python route_probe.py <repo da tentativa> <rótulo> <rodadas>
"""
import json
import sys
from pathlib import Path

repo, label, reps = Path(sys.argv[1]), sys.argv[2], int(sys.argv[3])
sys.path.insert(0, str(repo / "src"))
sys.path.insert(0, str(repo))
from app import router  # noqa: E402
from app.llm import get_llm  # noqa: E402
from evals import run_evals  # noqa: E402

cases = {c["id"]: c for c in run_evals.load_cases() if c["split"] in ("official", "memory")}
turns: dict[str, list] = {}
for split in ("official", "memory"):
    for line in open(repo / "evals" / "cassettes" / f"{split}.jsonl", encoding="utf-8"):
        e = json.loads(line)
        cid = e["scope"].split("#")[0]
        if not e["scope"].endswith("#0") or cid not in cases:
            continue
        t = turns.setdefault(cid, [])
        text = " ".join(x.get("text", "") for x in e["response"]["content"] if x.get("type") == "text")
        if e["role"] == "router":
            t.append({"router": json.loads(text), "answer": ""})
        elif e["role"] == "supervisor" and text and t:
            t[-1]["answer"] = text
out, spent = [], 0.0
llm = get_llm("router")
for cid, c in sorted(cases.items()):
    prev = turns.get(cid, [])
    history = []
    for msg, tr in zip(c.get("before") or [], prev, strict=False):
        history += [{"role": "user", "content": msg, "intent": tr["router"].get("intent")},
                    {"role": "assistant", "content": tr["answer"]}]
    for k in range(reps):
        d = router.route(c["message"], history)
        dec = getattr(d, "decision", d)
        got = getattr(dec, "intent", None)
        out.append({"id": cid, "rep": k, "intent": got, "expected": c["expect"].get("intent"),
                    "standalone": getattr(d, "standalone", None) or getattr(dec, "standalone", None),
                    "source": getattr(d, "source", None)})
        print(label, cid, k, got, "esperado", c["expect"].get("intent"), "|", out[-1]["standalone"], flush=True)
import re as _re  # noqa: E402

from app.observability import METRICS  # noqa: E402

COST = r"^llm_cost_usd_total\{[^}]*\} ([0-9.eE+-]+)$"
cost = sum(float(m.group(1)) for m in _re.finditer(COST, METRICS.render(), _re.M))
print(f"{label}: custo US$ {cost:.4f}")
ok = sum(r["intent"] == r["expected"] for r in out if r["expected"])
print(f"{label}: {ok}/{sum(1 for r in out if r['expected'])} intenções certas")
Path(f"route_{label}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
