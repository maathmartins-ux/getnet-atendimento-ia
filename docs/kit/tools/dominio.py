"""Domínio montado (ordem do dono, 04/11): guarda o domínio de uma tentativa e o aplica no T+0 da seguinte.

  python docs/kit/tools/dominio.py save <repo da tentativa> <commit>   # maestra, antes do relógio: grava
                                                                       # docs/kit/dominio/ (arquivos + MANIFEST)
  python docs/kit/tools/dominio.py mount                               # sessão do relógio, no T+0 (depois do
                                                                       # git archive do kit-fonte)

Vai junto o que é FONTE do domínio (corpus, CRM, casos, gold de busca, prompts, regras, ferramentas, testes e docs
do domínio). NÃO vai o que tem de ser medido ou escrito de novo no relógio: resultados, gravações, held-out e
perguntas reais (autores cegos novos), rótulos humanos, DEMO, FAILURE_MODES, TIMESHEET, RESULTS e PROCEDENCIA
(geradas). O `mount` escreve na PROCEDENCIA de onde o domínio veio (declarar é a condição do dono).
Com docs/kit/dominio/cache/embeddings.tar.gz e um VERSAO do mesmo lock e do mesmo script de modelos, o `mount`
também extrai o cache de vetores do corpus (var/embeddings) e o declara na PROCEDENCIA; versão outra ou tar inseguro:
avisa e segue sem ele.
Fica em docs/kit/ (fora da entrega): só a preparação usa.
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT / "docs" / "kit" / "dominio"

KEEP = [
    "src/app/domain/challenge/*", "src/app/domain/challenge_prompts/*",
    "data/knowledge/**", "data/crm/*", "data/glossary.json", "data/sources.json", "data/sample.jsonl",
    "data/intent_examples.jsonl", "data/intent_examples.d/*",
    "evals/cases.jsonl", "evals/cases.d/*", "evals/retrieval.jsonl", "evals/retrieval.d/*",
    "evals/retrieval.drafts/official.jsonl", "evals/essential/*",
    "evals/judge_calibration.jsonl", "evals/judge_calibration.d/*",
    "tests/test_domain_*.py", "tests/test_tools.py",
    "README.md", "docs/SPEC.md", "docs/ARCHITECTURE.md", "docs/EVAL_STRATEGY.md", "docs/OBSERVABILITY.md",
    "docs/RUNBOOK.md", "docs/SECURITY_ASI.md", "docs/SOURCES.md", "docs/THREAT_MODEL.md", "docs/VIDEO_SCRIPT.md",
    "docs/COBERTURA.md", "docs/adr/*",
]
# escritos de novo no relógio, por autores cegos novos: nunca vêm da tentativa anterior
NEVER = ["evals/cases.d/real.jsonl", "evals/heldout_blind.jsonl", "evals/real_questions.jsonl"]
# exemplo da loja que o pré-voo apagaria (o mount faz o mesmo, porque o pré-voo --mounted não mexe no domínio)
EXAMPLE_GONE = ["data/records.json"]
BLOCK_BEGIN, BLOCK_END = "<!-- dominio-montado:begin -->", "<!-- dominio-montado:end -->"
# Cache de vetores do corpus montado (gerado por docs/kit/ensaio15/build_vector_cache.sh numa árvore SEM held-out nem
# perguntas reais): o eval aquecido do T+0 cai de ~9 min para ~3 min. Só vale com o mesmo lock e o mesmo script de
# modelos (a chave do cache é modelo + texto, não a versão do fastembed/onnxruntime): VERSAO confere os dois.
CACHE_SENTENCE = ("Vetores do corpus pré-calculados no kit (derivados do corpus, sem held-out nem perguntas reais; "
                  "recalculados quando o texto muda).")


def _kept(rel: str) -> bool:
    return rel not in NEVER and any(fnmatch.fnmatch(rel, pat) for pat in KEEP)


def save(repo: Path, commit: str) -> dict:
    files = subprocess.run(["git", "-C", str(repo), "ls-tree", "-r", "--name-only", commit],
                           capture_output=True, text=True, check=True).stdout.split()
    kept = sorted(f for f in files if _kept(f))
    dest = STORE / "files"
    if dest.exists():
        shutil.rmtree(dest)
    for rel in kept:
        blob = subprocess.run(["git", "-C", str(repo), "show", f"{commit}:{rel}"], capture_output=True, check=True)
        out = dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(blob.stdout)
    url = subprocess.run(["git", "-C", str(repo), "remote", "get-url", "origin"], capture_output=True,
                         text=True).stdout.strip()
    manifest = {"source": url, "commit": commit, "saved_at": time.strftime("%Y-%m-%d"), "files": kept}
    (STORE / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    return manifest


def _sha256(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def cache_version(root: Path) -> dict:
    """O que o cache precisa que seja igual na tentativa: o lock do buscador e o script que baixa os modelos."""
    return {"hybrid_lock_sha256": _sha256(root / "requirements-hybrid.lock"),
            "fetch_models_sha256": _sha256(root / "scripts" / "fetch_models.py")}


def cache_dest(root: Path) -> Path:
    """O mesmo lugar de app.config.embed_cache_dir() na tentativa (EMBED_CACHE_DIR ou var/embeddings), sem importar o
    app: o mount roda antes do pip, e um `app` instalado de outra pasta apontaria para o var/ dela."""
    value = os.getenv("EMBED_CACHE_DIR")
    return Path(value) if value else root / "var" / "embeddings"


def _safe_members(tar: tarfile.TarFile) -> list[tarfile.TarInfo]:
    """Só arquivos e pastas com caminho relativo, sem `..`, sem link: um tar fora disso é recusado inteiro."""
    members = tar.getmembers()
    for m in members:
        name = Path(m.name)
        if m.name.startswith(("/", "\\")) or name.is_absolute() or ".." in name.parts or not (m.isfile() or m.isdir()):
            raise ValueError(f"cache de vetores recusado: membro inseguro {m.name!r}")
    return members


def apply_vector_cache(root: Path, store: Path | None = None) -> dict | None:
    """Extrai o cache se ele existe e o VERSAO bate; devolve {"files", "kit"} ou None (sem cache ou de outra versão)."""
    cache = (store or STORE) / "cache"
    archive, version = cache / "embeddings.tar.gz", cache / "VERSAO"
    if not archive.exists():
        return None
    try:
        want = json.loads(version.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        want = {}
    have = cache_version(root)
    if not have["hybrid_lock_sha256"] or any(want.get(k) != v for k, v in have.items()):
        print("AVISO: cache de vetores de outra versão (lock/modelos): eval aquecido recalcula (~9 min)")
        return None
    dest = cache_dest(root)
    try:  # cache ruim nunca derruba o mount do T+0: avisa e segue sem ele (o eval recalcula)
        with tarfile.open(archive, "r:gz") as tar:
            members = _safe_members(tar)  # valida TUDO antes de extrair qualquer coisa
            dest.mkdir(parents=True, exist_ok=True)
            kwargs = {"filter": "data"} if hasattr(tarfile, "data_filter") else {}
            tar.extractall(dest, members=members, **kwargs)
    except (ValueError, OSError, tarfile.TarError) as exc:
        print(f"AVISO: {exc}; segue sem cache de vetores (eval aquecido recalcula, ~9 min)")
        return None
    files = sum(m.isfile() for m in members)
    kit = str(want.get("kit") or "?")
    print(f"cache de vetores: {files} arquivos (kit {kit[:7]})")
    return {"files": files, "kit": kit}


def procedencia_block(manifest: dict, vector_cache: bool = False) -> str:
    return (f"{BLOCK_BEGIN}\n**Domínio montado antes do relógio.** O corpus, o CRM simulado, os casos de avaliação, "
            f"o gold de busca, os prompts e as regras do domínio e os docs do domínio vieram prontos da tentativa "
            f"cronometrada anterior deste mesmo desafio ({manifest['source']}, commit `{manifest['commit'][:7]}`, "
            f"{manifest['saved_at']}). No relógio desta entrega: held-out e perguntas reais escritos de novo por "
            f"autores cegos, todas as medições (offline, ao vivo, juiz), a conferência humana, as correções e esta "
            f"documentação.{(' ' + CACHE_SENTENCE) if vector_cache else ''}\n{BLOCK_END}")


def mount(root: Path = ROOT) -> list[str]:
    manifest = json.loads((STORE / "MANIFEST.json").read_text(encoding="utf-8"))
    src = STORE / "files"
    for rel in manifest["files"]:
        out = root / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src / rel, out)
    for rel in EXAMPLE_GONE:
        (root / rel).unlink(missing_ok=True)
    cached = apply_vector_cache(root)
    proc = root / "docs" / "PROCEDENCIA.md"
    text = proc.read_text(encoding="utf-8")
    block = procedencia_block(manifest, vector_cache=cached is not None)
    if BLOCK_BEGIN in text:
        head, _, rest = text.partition(BLOCK_BEGIN)
        text = head + block + rest.partition(BLOCK_END)[2]
    else:
        anchor = "## 1. O kit e a sua história"
        text = text.replace(anchor, block + "\n\n" + anchor, 1) if anchor in text else text + "\n\n" + block + "\n"
    proc.write_text(text, encoding="utf-8")
    return manifest["files"]


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "save" and len(sys.argv) == 4:
        m = save(Path(sys.argv[2]), sys.argv[3])
        print(f"domínio guardado: {len(m['files'])} arquivos de {m['source']} @ {m['commit'][:7]}")
    elif len(sys.argv) == 2 and sys.argv[1] == "mount":
        print(f"domínio montado: {len(mount())} arquivos; PROCEDENCIA declara a origem")
    else:
        sys.exit(__doc__)
