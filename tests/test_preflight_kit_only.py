"""Arquivos do processo que o pré-voo tira da entrega (preflight.KIT_ONLY): avaliação real, "~15 mil linhas, 1.533
testes, difícil de manter". A lista só nomeia o que existe no kit, nada que fica na entrega os cita pelo caminho ou
pelo import, e a suíte sem eles ainda é coletada inteira (sem import quebrado)."""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.preflight import KIT_ONLY

ROOT = Path(__file__).resolve().parents[1]
DOMAIN_FILES = ROOT / "docs" / "kit" / "dominio" / "files"
TEXT = (".py", ".sh", ".ps1", ".js", ".md", ".yml", ".yaml", ".toml", ".json", ".jsonl", ".cfg", ".txt", ".html")


def _kept() -> list[str]:
    """O que fica no repositório da entrega: versionado (ou novo, não ignorado), fora de docs/kit e do KIT_ONLY."""
    out = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    gone = set(KIT_ONLY)
    return [f for f in out.split("\0")
            if f and not f.startswith("docs/kit/") and f not in gone and (ROOT / f).is_file()]


def _citations(rel: str) -> re.Pattern:
    """O caminho do arquivo e, para módulo Python, o import dele (`from scripts import x`, `import test_x`)."""
    stem = Path(rel).stem
    forms = [re.escape(rel)]
    if rel.startswith("scripts/") and rel.endswith(".py"):
        forms += [rf"scripts\.{stem}\b", rf"from scripts import [\w, ]*\b{stem}\b"]
    if rel.startswith("tests/") and rel.endswith(".py"):
        forms += [rf"^\s*(?:from|import) {stem}\b"]
    return re.compile("|".join(forms), re.MULTILINE)


def test_kit_only_names_files_that_exist_in_the_kit():
    missing = [rel for rel in KIT_ONLY if not (ROOT / rel).is_file()]
    assert not missing, f"KIT_ONLY cita arquivo que não existe no kit (renomeado ou apagado): {missing}"
    assert len(KIT_ONLY) == len(set(KIT_ONLY))


@pytest.mark.skipif(shutil.which("git") is None, reason="sem git")
def test_nothing_that_stays_in_the_delivery_cites_a_removed_file():
    patterns = {rel: _citations(rel) for rel in KIT_ONLY}
    # + o domínio montado (docs/kit/dominio/files/: README, docs, testes do domínio), que vai para a entrega no T+0
    mounted = [p for p in DOMAIN_FILES.rglob("*") if p.is_file()] if DOMAIN_FILES.exists() else []
    files = [ROOT / f for f in _kept()] + mounted
    hits = []
    for path in files:
        rel_path = path.relative_to(ROOT).as_posix()
        if rel_path == "scripts/preflight.py" or not path.name.endswith(TEXT) and path.name != "Makefile":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        hits += [f"{rel_path} → {rel}" for rel, rx in patterns.items() if rx.search(text)]
    assert not hits, ("arquivo que fica na entrega cita um arquivo que o pré-voo tira (tire-o do KIT_ONLY ou a "
                      "citação): " + "; ".join(hits))


@pytest.mark.skipif(shutil.which("git") is None, reason="sem git")
def test_suite_without_the_process_files_still_collects(tmp_path):
    copy = tmp_path / "entrega"
    for f in _kept():
        (copy / f).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / f, copy / f)
    r = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider",
                        "-p", "no:xdist"], cwd=copy, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env={**os.environ, "PYTHONPATH": str(copy / "src")}, timeout=300)
    assert r.returncode == 0, "a suíte da entrega não coleta sem os arquivos do processo:\n" + r.stdout[-3000:]
    assert re.search(r"^\d+ tests collected", r.stdout, re.MULTILINE), r.stdout[-1000:]
