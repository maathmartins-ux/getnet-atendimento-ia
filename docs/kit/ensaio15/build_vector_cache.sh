#!/usr/bin/env bash
# Gera o cache de vetores do domínio montado (docs/kit/dominio/cache/): vetores do corpus, das perguntas do kit e dos
# pares do rerank, numa árvore do kit SEM held-out e SEM perguntas reais (os cegos nascem no relógio e não entram).
# O `dominio.py mount` extrai o cache só se o VERSAO bater com o lock e com os modelos da raiz. Chave de cada vetor =
# modelo + texto (src/app/rag.py): texto mudado no relógio = vetor recalculado, nunca vetor velho.
# Medido (04/11, tentativa simulada com o kit da rodada 15): eval aquecido 550 s sem o cache, 182 s com ele.
# Uso, no repositório do kit, depois do último commit de domínio: docs/kit/ensaio15/build_vector_cache.sh [ref]
set -euo pipefail
REF="${1:-HEAD}"
KIT="$(cd "$(dirname "$0")/../../.." && pwd)"
OUT="$KIT/docs/kit/dominio/cache"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
git -C "$KIT" archive "$REF" | tar -x -C "$T"
rm -f "$T/evals/heldout_blind.jsonl" "$T/evals/real_questions.jsonl" "$T"/docs/kit/dominio/cache/*
cd "$T" && mkdir -p var docs && python3 docs/kit/tools/dominio.py mount > "$T/mount.log"
rm -f "$T/evals/heldout_blind.jsonl" "$T/evals/real_questions.jsonl"   # o domínio montado também não traz cegos
export PYTHONPATH="$T/src" EMBED_CACHE_DIR="$T/var/embeddings"
s=$(date +%s); python3 -m evals.run_evals --out "$T/var/warm.json" > "$T/warm.log" 2>&1
echo "eval aquecido (frio): $(( $(date +%s) - s )) s"
s=$(date +%s); python3 -m evals.run_evals --choose-retriever --fast --keep-default > "$T/retr.log" 2>&1
echo "buscador (frio, sem --apply): $(( $(date +%s) - s )) s"
mkdir -p "$OUT"
tar -czf "$OUT/embeddings.tar.gz" -C "$T/var/embeddings" .
python3 - "$KIT" "$REF" "$OUT/VERSAO" <<'PY'
import hashlib, json, subprocess, sys
from pathlib import Path
kit, ref, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
sha = lambda p: hashlib.sha256((kit / p).read_bytes()).hexdigest()
data = {"hybrid_lock_sha256": sha("requirements-hybrid.lock"), "fetch_models_sha256": sha("scripts/fetch_models.py"),
        "kit": subprocess.run(["git", "-C", str(kit), "rev-parse", "--short", ref], capture_output=True, text=True,
                              check=True).stdout.strip()}
out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
print(json.dumps(data))
PY
echo "cache: $(du -h "$OUT/embeddings.tar.gz" | cut -f1) em $OUT/embeddings.tar.gz ($(tar -tzf "$OUT/embeddings.tar.gz" | grep -c .) entradas)"
