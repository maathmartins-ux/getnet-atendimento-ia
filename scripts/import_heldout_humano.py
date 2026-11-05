"""Perguntas escritas por pessoas (página `scripts/templates/heldout_humano.html`) → casos `heldout-H3-NN`.

Por quê: um held-out escrito só por modelos mede pouco o que um lojista de verdade pergunta. As pessoas escrevem com
calma, antes da medida e sem ver código, casos nem respostas; aqui só se converte. Elas
não precisam conferir contaminação: depois deste script, `tests/test_router_contamination.py` reprova exemplo de treino
ou regra que copie uma pergunta cega (a correção é no TREINO, nunca na pergunta).

Entrada: o que a página gravou (`ArtifactData` → list da coleção `heldout`, salva em var/heldout_humano.json: lista de
documentos {author, items: [{q, tipo, hum}]}, ou {"docs": [...]}). Saída: as linhas H3 no fim de
evals/heldout_blind.jsonl (as H3 antigas saem antes), com `"author": "pessoa:<nome>"`; o idioma vem do detector do
router e a intenção e o "vai ao atendente" são os que a pessoa marcou. Sem `tools` no esperado: quem escreve não sabe
quais ferramentas existem.
Uso: python scripts/import_heldout_humano.py var/heldout_humano.json [--user cliente1988]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
HELDOUT = ROOT / "evals" / "heldout_blind.jsonl"
INTENTS = {"knowledge", "support", "troubleshoot", "human_request", "general", "multi", "blocked"}


def rows(docs: list[dict], user_id: str) -> list[dict]:
    from app.router import detect_language

    out, seen = [], set()
    for doc in sorted(docs, key=lambda d: str(d.get("author") or "")):
        author = str(doc.get("author") or "pessoa").strip()
        for item in doc.get("items") or []:
            q = " ".join(str(item.get("q") or "").split())
            tipo = item.get("tipo")
            if len(q) < 5 or tipo not in INTENTS or q.casefold() in seen:
                continue
            seen.add(q.casefold())
            expect = {"intent": tipo, "language": detect_language(q), "handoff": item.get("hum") == "sim"}
            if tipo == "blocked":
                expect["blocked"] = True
            out.append({"id": f"heldout-H3-{len(out) + 1:02d}", "split": "heldout", "user_id": user_id,
                        "author": f"pessoa:{author}", "message": q, "expect": expect})
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dump", type=Path)
    ap.add_argument("--user", default="cliente1988")
    ap.add_argument("--out", type=Path, default=HELDOUT)
    args = ap.parse_args(argv)
    raw = json.loads(args.dump.read_text(encoding="utf-8"))
    docs = raw.get("docs") if isinstance(raw, dict) else raw
    docs = [d.get("data", d) for d in docs or []]
    new = rows(docs, args.user)
    keep = []
    if args.out.exists():
        keep = [ln for ln in args.out.read_text(encoding="utf-8").splitlines()
                if ln.strip() and not json.loads(ln)["id"].startswith("heldout-H3-")]
    args.out.write_text("\n".join(keep + [json.dumps(r, ensure_ascii=False) for r in new]) + "\n", encoding="utf-8")
    by = {}
    for r in new:
        by[r["author"]] = by.get(r["author"], 0) + 1
    print(json.dumps({"H3": len(new), "por_pessoa": by, "arquivo": str(args.out)}, ensure_ascii=False))
    print("agora: python -m pytest -q -rf tests/test_router_contamination.py (corrige o treino, nunca a pergunta)")
    return 0 if new else 2


if __name__ == "__main__":
    sys.exit(main())
