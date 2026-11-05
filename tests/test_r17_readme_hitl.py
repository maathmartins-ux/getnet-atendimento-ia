"""O README cita o atendimento humano de verdade quando docs/HITL_HUMANO.md existe, com o nome e o tempo do arquivo."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_human_block_cites_the_real_operator_file(tmp_path):
    hitl, fill = _load("hitl_humano"), _load("fill_readme")
    rec = {"message": "quero um atendente", "first": {"answer": "Abri o caso."},
           "ticket": {"id": "T-1", "reason": "pedido", "created_at": 1000.0, "answered_at": 1185.0,
                      "answer": "Estornei a cobrança."},
           "resumed": {"content": "O atendente estornou.", "ts": 1190.0},
           "audit": [{"actor": "operator:ana", "detail": {"channel": "console"}, "ts": 1185.0}]}
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "HITL_HUMANO.md").write_text(hitl.markdown(rec, "ana", "abc1234", "hoje", "anthropic"),
                                                      encoding="utf-8")
    results = tmp_path / "evals" / "results"
    results.mkdir(parents=True)
    out = fill.human_block(results)
    assert "`pessoa:ana`" in out and "3 min 05 s" in out and "commit `abc1234`" in out
    (tmp_path / "docs" / "HITL_HUMANO.md").unlink()
    assert "pessoa:" not in fill.human_block(results)  # sem o arquivo, nada é dito
