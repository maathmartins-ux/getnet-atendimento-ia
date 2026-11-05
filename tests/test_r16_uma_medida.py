"""Rodada 15: o docs/RESULTS.md dizia "official resolvidas 90%" e "official 80% completas" (e dependent 100% × 50%):
duas medidas com o mesmo nome. Agora cada uma tem o seu ("resolvidas pela regra", "resolvidas por completo",
"…, offline") e o check reprova o mesmo nome com 2 valores no mesmo split."""
from scripts import check

OLD = """**Resolvidas** (sem humano, …): official **80.0%** [IC95 62.7–90.5; n=30] · pass^3 70%
| `official` | resolvidas **90%** [74.4–96.5] (n=30) | 26/30 | x | 1 s | 0.6 |
"""
NEW = """**Resolvidas por completo** (sem humano, …): official **80.0%** [IC95 62.7–90.5; n=30]; pela regra: 90.0%
**Resolvidas pela regra, offline** (só lexical, …): official **80.0%** [IC95 49–94; n=10]
| `official` | resolvidas pela regra **90%** [74.4–96.5] (n=30) | 26/30 | x | 1 s | 0.6 |
#### Split `dependent` — `live_dependent.json`
resolvidas pela regra **100%** [72.2–100] (n=10) · intenção **100%** [72.2–100] (n=10)
"""


def test_old_names_fail_with_both_values(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "RESULTS.md").write_text(OLD, encoding="utf-8")
    name, ok, _, detail = check.one_value_per_measure(tmp_path)
    assert not ok and "official: 'resolvidas' com [80.0, 90.0]" in detail


def test_one_name_per_measure_passes_and_every_value_is_read(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "RESULTS.md").write_text(NEW, encoding="utf-8")
    assert check.one_value_per_measure(tmp_path)[1]
    v = check.measure_values(NEW)
    assert v[("official", "resolvidas por completo")] == {80.0}
    assert v[("official", "resolvidas pela regra")] == {90.0}  # a tabela e o "pela regra:" da linha batem
    assert v[("official", "resolvidas pela regra, offline")] == {80.0}
    assert v[("dependent", "resolvidas pela regra")] == {100.0}  # linha de taxas abaixo do "#### Split"


def test_same_name_two_values_across_readme_and_results_fails(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "RESULTS.md").write_text(NEW, encoding="utf-8")
    (tmp_path / "README.md").write_text("| `official` | resolvidas pela regra **85%** (n=30) |\n", encoding="utf-8")
    _, ok, _, detail = check.one_value_per_measure(tmp_path)
    assert not ok and "'resolvidas pela regra' com [85.0, 90.0]" in detail


def test_the_check_is_part_of_the_delivery_docs():
    import inspect

    assert "one_value_per_measure(root)" in inspect.getsource(check.delivery_doc_checks)
