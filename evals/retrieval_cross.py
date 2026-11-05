"""Busca medida num gold que o time não escreveu: o juiz de OUTRA família marca, entre os 10 primeiros trechos que o
caminho do agente traz, quais respondem cada pergunta real e cada pergunta do held-out.

Por quê: um gold escrito pelo mesmo time que calibra os limiares mede a busca nas perguntas que o time escolheu. O
limiar continua calibrado no gold do time (`--calibrate-gate`); aqui a medida sai em perguntas que o time não escolheu
(reais, coletadas com link, e held-out escrito às cegas), com rótulos de relevância de um modelo de outra família.
Rótulo de relevância por LLM concorda bem com o de pessoas em busca (TREC 2024, avaliação UMBRELA); a ressalva é a de
todo gold por "pool": só o que entrou nos 10 primeiros pode ser marcado, então a medida é de ordenação dentro do que
a busca acha (hit@3, hit@5, MRR@10) e de quantas perguntas ficam sem nenhum trecho útil.

Uso (precisa do juiz cruzado: JUDGE_PROVIDER=openai_compat, JUDGE_BASE_URL, JUDGE_MODEL, JUDGE_API_KEY):
    python -m evals.retrieval_cross --max-usd 1
Grava evals/results/retrieval_cross.json.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "retrieval_cross.json"
POOL = 10
CHARS = 700
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["relevant"],
          "properties": {"relevant": {"type": "array", "items": {"type": "integer"}}}}
SYSTEM = ("Você avalia uma busca. Recebe a pergunta de um cliente e trechos numerados de um site. Marque os "
          "números dos trechos que trazem informação que responde a pergunta, inteira ou em parte. Trecho só do "
          "mesmo assunto, sem a informação pedida, não conta. Responda só o JSON pedido; lista vazia se nenhum "
          "responde.")


def questions(heldout: Path, real: Path) -> list[dict]:
    """Perguntas que pedem conhecimento do site: as reais (todas) e as do held-out de intenção conhecimento/multi."""
    out = []
    for path, keep in ((real, lambda r: True),
                       (heldout, lambda r: (r.get("expect") or {}).get("intent") in ("knowledge", "multi"))):
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip() and keep(row := json.loads(line)):
                out.append({"id": row["id"], "split": row.get("split") or path.stem, "message": row["message"]})
    return out


def label(llm, question: str, hits: list) -> tuple[list[int], float]:
    """(posições 1..N dos trechos que respondem, US$ da chamada)."""
    from app.llm import LLMError
    from app.observability import llm_cost

    blocks = "\n\n".join(f"[{i + 1}] {h.doc.title}\n{h.doc.text[:CHARS]}" for i, h in enumerate(hits))
    try:
        reply = llm.complete(SYSTEM, [{"role": "user", "content": f"Pergunta: {question}\n\nTrechos:\n{blocks}"}],
                             max_tokens=512, schema=SCHEMA)
    except LLMError:
        return None, 0.0  # a pergunta fica "sem rótulo"; o que já foi pago nas outras não se perde
    cost = llm_cost(reply.model, reply.input_tokens, reply.output_tokens)
    try:
        got = json.loads(reply.text).get("relevant") or []
        return sorted({int(i) for i in got if str(i).lstrip("-").isdigit() and 1 <= int(i) <= len(hits)}), cost
    except (ValueError, TypeError, AttributeError):
        return None, cost


def score(rows: list[dict]) -> dict:
    """hit@3, hit@5 e MRR@10 nas perguntas com algum trecho útil; e quantas não têm nenhum entre os 10."""
    answered = [r for r in rows if r["relevant"]]
    n = len(answered)

    def hit(k: int) -> float | None:
        return round(sum(min(r["relevant"]) <= k for r in answered) / n, 3) if n else None

    mrr = round(sum(1 / min(r["relevant"]) for r in answered) / n, 3) if n else None
    return {"perguntas": len(rows), "com_trecho_util": n, "sem_trecho_util": len(rows) - n,
            "hit@3": hit(3), "hit@5": hit(5), "mrr@10": mrr}


def run(llm, retriever, items: list[dict], max_usd: float | None = None) -> dict:
    from app.agents import expand_query

    rows, spent, unlabeled = [], 0.0, []
    for q in items:
        if max_usd is not None and spent >= max_usd:
            break
        # a mesma consulta do gold do time (retrieval_eval._query: pergunta + glossário), para as duas medidas
        # serem comparáveis; o caminho do agente faz o resto (plano de busca e rerank)
        hits = retriever.search(expand_query(q["message"]), k=POOL)[:POOL]
        relevant, cost = label(llm, q["message"], hits) if hits else ([], 0.0)
        spent += cost
        if relevant is None:
            unlabeled.append(q["id"])
            continue
        rows.append({**q, "relevant": relevant, "ids": [h.doc.id for h in hits]})
    spent = round(spent, 4)
    by_split = {s: score([r for r in rows if r["split"] == s]) for s in sorted({r["split"] for r in rows})}
    return {"juiz": {"model": getattr(llm, "model", "?"), "provider": getattr(llm, "provider", "?")},
            "pool": POOL, "status": "complete" if len(rows) + len(unlabeled) == len(items) else "aborted_max_usd",
            "sem_rotulo": unlabeled,
            "spent_usd": spent, **score(rows), "por_split": by_split, "linhas": rows}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-usd", type=float, default=1.0)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args(argv)
    if os.getenv("JUDGE_PROVIDER") != "openai_compat":
        print("precisa do juiz de outra família (JUDGE_PROVIDER=openai_compat + JUDGE_*); nada gravado",
              file=sys.stderr)
        return 2
    from app.llm import get_judge_llm
    from evals.run_evals import AgentPathRetriever

    report = run(get_judge_llm(), AgentPathRetriever(),
                 questions(HERE / "heldout_blind.jsonl", HERE / "real_questions.jsonl"), args.max_usd)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("status", "perguntas", "com_trecho_util", "hit@3", "hit@5", "mrr@10",
                                             "spent_usd")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
