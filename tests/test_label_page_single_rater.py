"""Um rotulador só (ensaio 13): a página sai sem nome fictício e o script avisa que a concordância não é medida.

Roda no processo do pytest, com respostas ao vivo de teste no tmp_path: o conftest desvia para o tmp_path o
evals/human_selection.json, o evals/validation/ e o sal das páginas. Tentativa simulada da rodada 15: este teste
rodava o script num subprocesso, onde o desvio não vale; com a fumaça julgada commitada (live_*.json no repo), cada
pytest gravava uma página de teste na seleção e no conjunto congelado da tentativa, que o scripts/final.sh commita.
"""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _live(results: Path, n: int) -> None:
    rows = [{"id": f"official-{i:02d}", "split": "official", "message": f"pergunta {i}", "answer": f"resposta {i}",
             "checks": {"intent": True, "numbers": True}, "run": 0, "route": ["router", "faq"],
             "source_ids": ["s1"], "sources": [{"id": "s1", "url": "https://x/y"}]} for i in range(n)]
    results.mkdir(parents=True, exist_ok=True)
    (results / "live_official.json").write_text(json.dumps({"rows": rows, "provider": "anthropic",
                                                            "status": "complete"}), encoding="utf-8")


def test_single_rater_is_allowed_with_a_warning(tmp_path, monkeypatch, capsys):
    from evals import label

    real_selection, real_validation = ROOT / "evals" / "human_selection.json", ROOT / "evals" / "validation"
    before = (real_selection.exists() and real_selection.read_bytes(),
              sorted(p.name for p in real_validation.glob("*.json")))
    monkeypatch.setattr(label, "RESULTS", tmp_path / "results")
    _live(tmp_path / "results", 4)
    spec = importlib.util.spec_from_file_location("label_page", ROOT / "scripts" / "label_page.py")
    page = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(page)
    rc = page.main(["--raters", "Matheus", "--n", "2", "--out", str(tmp_path / "p.html")])
    out = capsys.readouterr()
    assert "pede 2+ pessoas" not in out.err
    assert "1 rotulador" in out.err
    assert rc == 0 and json.loads(out.out.strip().splitlines()[-1])["raters"] == ["Matheus"]
    assert label.SELECTION_FILE.is_relative_to(tmp_path) and label.SELECTION_FILE.exists()  # a seleção foi para o tmp
    after = (real_selection.exists() and real_selection.read_bytes(),
             sorted(p.name for p in real_validation.glob("*.json")))
    assert after == before  # e o repo não recebeu página de teste
