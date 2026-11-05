"""Segundo juiz, sem LLM: um modelo pequeno de inferência textual (NLI) confere cada frase da resposta contra o que o
assistente tinha em mãos (trechos do site e dados das tools).

Por que existe: o juiz principal (evals/judge.py) é um LLM da mesma família do modelo avaliado, e uma avaliação real
apontou isso. Este roda local (onnxruntime, sem chave, sem rede depois de baixar), é de outra família (mDeBERTa
multilíngue treinado em XNLI) e serve de 2ª opinião independente: o RESULTS mostra a concordância dos dois por
resposta. Não substitui o juiz LLM nem entra na manchete.

Regra (fixada antes de medir): frase factual = frase com 4+ palavras que não é pergunta, oferta nem ausência
declarada; ela tem base se algum trecho a implica com probabilidade >= ENTAIL; a resposta é fundamentada se nenhuma
frase factual é contradita (>= CONTRA no trecho que mais se parece com ela) e se pelo menos SHARE delas têm base.

Modelo: Xenova/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7 (ONNX int8, ~317 MB), na revisão e com o sha256 fixados
abaixo; baixado em var/models/nli na 1ª chamada (ou em NLI_MODEL_DIR).
Uso: python -m evals.nli_judge [evals/results/live_official.json ...]   (grava evals/results/nli_judge.json)
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = HERE / "results"
OUT = RESULTS / "nli_judge.json"

REPO = "Xenova/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
REVISION = "0864ced79bf1ef851bfaf9dd9de0aa54d735d9d0"
FILES = {"onnx/model_int8.onnx": "0e00534691cac71d2a9a0319bce19df9d7c6f003acea00bef9967560584c1a77",
         "tokenizer.json": "e23095eb61ba944c7be3a5d3e8ec19e37ce7ced0daa03550bde03e83c21b3f8a"}
LABELS = ("entailment", "neutral", "contradiction")
ENTAIL, CONTRA, SHARE = 0.5, 0.6, 0.8
_SKIP = re.compile(r"\?\s*$|^(?:se quiser|posso|quer que|if you|would you|i can|can i)\b|"
                   r"\b(?:n[ãa]o (?:encontrei|trazem|dizem|informam)|sources? (?:don.t|do not)|couldn.t find)\b", re.I)


def model_dir() -> Path:
    return Path(os.getenv("NLI_MODEL_DIR") or ROOT / "var" / "models" / "nli")


def ensure_model() -> Path:
    """Baixa o modelo na revisão fixada e confere o sha256 de cada arquivo (arquivo diferente = erro, nunca usa)."""
    base = model_dir()
    for rel, sha in FILES.items():
        path = base / rel
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            url = f"https://huggingface.co/{REPO}/resolve/{REVISION}/{rel}"
            tmp = path.with_suffix(path.suffix + ".part")
            urllib.request.urlretrieve(url, tmp)  # noqa: S310 (URL fixa acima, https)
            tmp.replace(path)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != sha:
            raise RuntimeError(f"{rel}: sha256 {digest[:12]} ≠ o fixado {sha[:12]}: apague {path} e rode de novo")
    return base


class NLI:
    def __init__(self) -> None:
        import onnxruntime as ort
        from tokenizers import Tokenizer

        base = ensure_model()
        self.tok = Tokenizer.from_file(str(base / "tokenizer.json"))
        self.tok.enable_truncation(512)
        self.sess = ort.InferenceSession(str(base / "onnx" / "model_int8.onnx"), providers=["CPUExecutionProvider"])
        self.inputs = {i.name for i in self.sess.get_inputs()}

    def probs(self, premise: str, hypothesis: str) -> dict[str, float]:
        import numpy as np

        enc = self.tok.encode(premise, hypothesis)
        feed = {"input_ids": np.array([enc.ids], dtype=np.int64),
                "attention_mask": np.array([enc.attention_mask], dtype=np.int64)}
        if "token_type_ids" in self.inputs:
            feed["token_type_ids"] = np.array([enc.type_ids], dtype=np.int64)
        logits = self.sess.run(None, feed)[0][0]
        e = np.exp(logits - logits.max())
        return dict(zip(LABELS, (e / e.sum()).round(4).tolist(), strict=True))


def flatten(evidence: str) -> str:
    """Dado de tool em JSON vira "chave: valor" por linha (o NLI lê texto, não JSON); trecho do site fica igual."""
    try:
        data = json.loads(evidence)
    except (ValueError, TypeError):
        return evidence
    out: list[str] = []

    def walk(x, key=""):
        if isinstance(x, dict):
            for k, v in x.items():
                walk(v, k)
        elif isinstance(x, list):
            for v in x:
                walk(v, key)
        elif x not in (None, ""):
            out.append(f"{key}: {x}" if key else str(x))
    walk(data)
    return ". ".join(out)


def factual_sentences(answer: str) -> list[str]:
    from app.claims import split_sentences

    plain = re.sub(r"\[\d+\]|\*\*", "", answer)
    return [s.text.strip(" -•") for s in split_sentences(plain)
            if len(s.text.split()) >= 4 and not _SKIP.search(s.text.strip())]


_WORD = re.compile(r"[\wÀ-ÿ%$,.-]{3,}")


def windows(chunks: list[str], size: int = 2) -> list[str]:
    """Janelas de `size` frases de cada trecho: o NLI lê premissa curta (trecho inteiro de 512 tokens dava
    implicação baixa até para frase certa: medido, concordância de 15% com o juiz LLM)."""
    from app.claims import split_sentences

    out = []
    for c in chunks:
        sents = [x.text for x in split_sentences(c)] or [c]
        out += [" ".join(sents[i:i + size]) for i in range(0, max(1, len(sents) - size + 1))]
    return out


def nearest(wins: list[str], hypothesis: str, k: int = 3) -> list[str]:
    """As k janelas com mais palavras em comum com a frase (números inclusive): o NLI só roda nelas."""
    h = {w.lower() for w in _WORD.findall(hypothesis)}
    return sorted(wins, key=lambda w: -len(h & {x.lower() for x in _WORD.findall(w)}))[:k]


def judge_row(nli: NLI, row: dict) -> dict:
    chunks = [flatten(e)[:4000] for e in (row.get("evidence") or []) if e]
    wins = windows(chunks)
    sents = factual_sentences(row.get("answer") or "")
    detail = []
    for s in sents:
        scores = [nli.probs(c, s) for c in nearest(wins, s)] if wins else []
        best = max(scores, key=lambda p: p["entailment"], default={"entailment": 0, "contradiction": 0})
        near = max(scores, key=lambda p: p["entailment"] + p["contradiction"], default=best)
        detail.append({"frase": s[:200], "base": best["entailment"] >= ENTAIL,
                       "contradita": near["contradiction"] >= CONTRA, "entail": best["entailment"]})
    supported = sum(d["base"] for d in detail)
    contradicted = sum(d["contradita"] for d in detail)
    grounded = bool(detail) and not contradicted and supported >= SHARE * len(detail)
    return {"id": row.get("id"), "run": row.get("run", 0), "frases": len(detail), "com_base": supported,
            "contraditas": contradicted, "grounded": grounded if detail else None, "detalhe": detail}


def agreement(rows: list[dict], llm_verdicts: dict) -> dict:
    pairs = [(r["grounded"], llm_verdicts[(r["source"], r["id"], r["run"])]) for r in rows
             if r["grounded"] is not None and (r["source"], r["id"], r["run"]) in llm_verdicts]
    if not pairs:
        return {"n": 0}
    agree = sum(a == b for a, b in pairs) / len(pairs)
    pa, pb = sum(a for a, _ in pairs) / len(pairs), sum(b for _, b in pairs) / len(pairs)
    pe = pa * pb + (1 - pa) * (1 - pb)
    kappa = (agree - pe) / (1 - pe) if pe < 1 else None
    return {"n": len(pairs), "concordancia": round(agree, 3), "kappa": round(kappa, 3) if kappa is not None else None,
            "nli_fundamentadas": round(pa, 3), "juiz_llm_fundamentadas": round(pb, 3)}


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    files = [Path(a) for a in argv] or sorted(RESULTS.glob("live_*.json"))
    nli = NLI()
    out_rows = []
    for f in files:
        for row in (json.loads(f.read_text(encoding="utf-8")).get("rows") or []):
            if row.get("answer"):
                out_rows.append({**judge_row(nli, row), "source": f.name})
    llm = {}
    judge = RESULTS / "judge.json"
    if judge.exists():
        for v in json.loads(judge.read_text(encoding="utf-8")).get("verdicts") or []:
            if "grounded" in v:
                llm[(v.get("source"), v.get("id"), v.get("run", 0))] = bool(v["grounded"])
    report = {"modelo": f"{REPO}@{REVISION[:7]} (int8)", "regra": {"entail": ENTAIL, "contra": CONTRA, "share": SHARE},
              "respostas": len(out_rows), "nli_x_juiz_llm": agreement(out_rows, llm), "rows": out_rows}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "rows"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
