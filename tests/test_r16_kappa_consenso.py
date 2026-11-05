"""Rodada 16 (#14): pessoas × checagem automática pelo rótulo de consenso, com AC1, negativos por lado e a causa de
cada divergência. Rodada 15: a manchete usava só o 1º rotulador (ordem alfabética), antes do consenso, e o kappa −0,081
saía sem dizer que havia 1 reprovação da checagem."""
from __future__ import annotations

from evals import label


def _rec(rater, key, human, **csv):
    return {"rater": rater, "key": key, "human": human, "planted": False,
            "csv": {"humano": "pass" if human else "fail", "nota": csv.pop("nota", ""), **csv}}


def test_consensus_labels_single_agreed_resolved_and_open():
    recs = [_rec("a", "x", True), _rec("b", "x", True),          # concordam
            _rec("a", "y", False), _rec("b", "y", True),         # divergem, consenso diz pass
            _rec("a", "z", False), _rec("b", "z", True),         # divergem, sem consenso
            _rec("a", "w", False, nota="wrong_route")]           # uma pessoa só
    got, open_ = label.consensus_labels(recs, {"y": {"v": "pass"}, "z": {"v": "diverge"}})
    assert {r["id"]: r["humano"] for r in got} == {"x": "pass", "y": "pass", "w": "fail"}
    assert open_ == ["z"]


def test_vs_auto_reports_ac1_negatives_reading_and_causes():
    labeled = [{"id": f"p{i}", "humano": "pass", "nota": ""} for i in range(17)]
    labeled += [{"id": "m2", "humano": "fail", "nota": "wrong_route", "c1": "nao", "c2": "nao", "c3": "sim"},
                {"id": "m3", "humano": "fail", "nota": "wrong_route", "c1": "nao", "c2": "nao", "c3": "sim"},
                {"id": "o4", "humano": "pass", "nota": ""}]
    auto = {r["id"]: r["id"] != "o4" for r in labeled}
    rows = {"o4": {"checks": {"facts": False, "resolved": False, "language": True}}}
    out = label._vs_auto(labeled, auto, rows)
    assert (out["concordancia"], out["kappa"], out["ac1"]) == (0.85, -0.071, 0.826)  # os números da rodada 15
    assert out["negativos"] == {"humano": 2, "automatico": 1} and out["kappa_leitura"].startswith("sem leitura: 1")
    causes = {d["id"]: (d["pessoa_reprovou"], d["checagem_falhou"]) for d in out["divergencias"]}
    assert causes == {"m2": (["c1"], []), "m3": (["c1"], []), "o4": ([], ["facts", "resolved"])}


def test_enough_negatives_on_both_sides_reads_kappa():
    labeled = [{"id": f"i{i}", "humano": "pass" if i % 2 else "fail", "nota": ""} for i in range(20)]
    out = label._vs_auto(labeled, {r["id"]: r["humano"] == "pass" for r in labeled})
    assert out["kappa"] == 1.0 and out["kappa_leitura"] is None
