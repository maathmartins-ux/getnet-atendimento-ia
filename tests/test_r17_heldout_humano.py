"""Rodada 17: perguntas escritas por pessoas antes do relógio viram casos heldout-H3 com autor pessoa."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("imp", ROOT / "scripts" / "import_heldout_humano.py")
imp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(imp)


def test_people_questions_become_h3_cases_and_replace_old_h3(tmp_path):
    out = tmp_path / "heldout_blind.jsonl"
    out.write_text(json.dumps({"id": "heldout-H1-01", "message": "x", "expect": {}}) + "\n"
                   + json.dumps({"id": "heldout-H3-01", "message": "velha", "expect": {}}) + "\n", encoding="utf-8")
    dump = tmp_path / "dump.json"
    dump.write_text(json.dumps([
        {"author": "Bianca", "items": [{"q": "minha maquininha ta sem sinal, o que faço?", "tipo": "troubleshoot",
                                        "hum": "nao"},
                                       {"q": "quero falar com alguém agora", "tipo": "human_request", "hum": "sim"}]},
        {"author": "Matheus", "items": [{"q": "How much did I sell yesterday?", "tipo": "support", "hum": "nao"},
                                        {"q": "ok", "tipo": "support", "hum": "nao"},  # curta demais: fora
                                        {"q": "Quero falar com alguém agora", "tipo": "human_request", "hum": "sim"}]},
    ]), encoding="utf-8")
    assert imp.main([str(dump), "--out", str(out)]) == 0
    lines = [json.loads(x) for x in out.read_text(encoding="utf-8").splitlines()]
    h3 = [r for r in lines if r["id"].startswith("heldout-H3-")]
    assert [r["id"] for r in lines][0] == "heldout-H1-01" and len(h3) == 3  # repetida e curta saem; a velha também
    assert {r["author"] for r in h3} == {"pessoa:Bianca", "pessoa:Matheus"}
    en = next(r for r in h3 if r["message"].startswith("How"))
    assert en["expect"] == {"intent": "support", "language": "en", "handoff": False}
    assert next(r for r in h3 if r["expect"]["intent"] == "human_request")["expect"]["handoff"] is True


def test_page_saves_each_person_in_own_doc():
    page = (ROOT / "scripts" / "templates" / "heldout_humano.html").read_text(encoding="utf-8")
    assert 'db.doc("heldout/" + uid)' in page and "<title>Perguntas de Lojista</title>" in page
