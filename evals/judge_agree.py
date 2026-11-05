"""Concordância entre o juiz principal e um juiz de OUTRA família sobre as mesmas respostas.

Por quê: um juiz da mesma família do modelo avaliado tende a favorecer o próprio texto. A literatura mede o viés:
avaliadores favorecem o próprio texto (Panickssery et al., NeurIPS 2024) e modelos da mesma linhagem ("preference
leakage", 2025); um júri de famílias diferentes concorda mais com pessoas do que um juiz só
(Verga et al., 2024). Aqui o 2º juiz (`JUDGE_PROVIDER=openai_compat ... python -m evals.judge --out
evals/results/judge_cross.json`) julga as mesmas linhas, e este script compara os dois no "fundamentada": concordância,
kappa e AC1 (o kappa despenca com prevalência alta; o AC1 não), e lista cada divergência para as pessoas olharem.

Uso: python -m evals.judge_agree [--a evals/results/judge.json] [--b evals/results/judge_cross.json]
Grava evals/results/judge_agree.json. Sem LLM.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from evals.label import agreement

RESULTS = Path(__file__).resolve().parent / "results"
OUT = RESULTS / "judge_agree.json"


def _key(v: dict) -> tuple[str, int, str]:
    """Mesma linha E mesmo texto: (id, rodada, sha da resposta julgada). Dois juízes de baterias diferentes têm o
    mesmo (id, rodada) para respostas diferentes; sem o sha, a concordância compararia textos que não são o mesmo."""
    return str(v.get("id")), int(v.get("run") or 0), str(v.get("answer_sha") or "")


def compare(a: dict, b: dict) -> dict:
    """Pares (juiz A, juiz B) do `grounded` nas linhas julgadas pelos dois; divergências com o motivo de cada um."""
    va = {_key(v): v for v in a.get("verdicts") or [] if v.get("grounded") is not None}
    vb = {_key(v): v for v in b.get("verdicts") or [] if v.get("grounded") is not None}
    both = sorted(va.keys() & vb.keys())
    same_row = {k[:2] for k in va} & {k[:2] for k in vb}
    other_text = len(same_row - {k[:2] for k in both})  # mesma linha, texto diferente: fora da conta, contado
    pairs = [(bool(va[k]["grounded"]), bool(vb[k]["grounded"])) for k in both]
    by_split: dict[str, list[tuple[bool, bool]]] = {}
    for k, pair in zip(both, pairs, strict=True):
        by_split.setdefault(str(va[k].get("split")), []).append(pair)
    diverge = [{"id": k[0], "run": k[1], "split": va[k].get("split"),
                "a": {"grounded": va[k]["grounded"], "failure_type": va[k].get("failure_type"),
                      "reason": (va[k].get("reason") or "")[:300]},
                "b": {"grounded": vb[k]["grounded"], "failure_type": vb[k].get("failure_type"),
                      "reason": (vb[k].get("reason") or "")[:300]}}
               for k, (x, y) in zip(both, pairs, strict=True) if x != y]
    return {"juiz_a": {"model": a.get("model"), "family": a.get("judge_family")},
            "juiz_b": {"model": b.get("model"), "family": b.get("judge_family")},
            "familias_diferentes": a.get("judge_family") != b.get("judge_family"),
            "linhas_em_comum": len(both), "so_em_a": len(va.keys() - vb.keys()), "so_em_b": len(vb.keys() - va.keys()),
            "mesma_linha_outro_texto": other_text,
            "fundamentada": {**agreement(pairs),
                             "taxa_a": round(sum(x for x, _ in pairs) / len(pairs), 3) if pairs else None,
                             "taxa_b": round(sum(y for _, y in pairs) / len(pairs), 3) if pairs else None},
            "por_split": {s: agreement(p) for s, p in sorted(by_split.items())},
            "divergencias": diverge}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", type=Path, default=RESULTS / "judge.json")
    ap.add_argument("--b", type=Path, default=RESULTS / "judge_cross.json")
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args(argv)
    if not (args.a.exists() and args.b.exists()):
        print(f"falta {args.a if not args.a.exists() else args.b}: rode os dois juízes antes", file=sys.stderr)
        return 2
    report = compare(json.loads(args.a.read_text(encoding="utf-8")), json.loads(args.b.read_text(encoding="utf-8")))
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    f = report["fundamentada"]
    print(json.dumps({"linhas": report["linhas_em_comum"], "concordancia": f["concordancia"], "kappa": f["kappa"],
                      "ac1": f["ac1"], "divergencias": len(report["divergencias"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
