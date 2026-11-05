"""Rodada 15: a resposta citava "[7][8][10]" com 5 URLs na lista de fontes e mostrava fontes de crediário
numa pergunta de conexão. A numeração era a da lista de trechos recuperados. Agora o "[n]" é a ordem da 1ª citação,
um número por página (URL), e a resposta leva `citations`: só as citadas. `sources` segue com tudo o que o turno
consultou, porque o eval mede a busca nela."""
from types import SimpleNamespace as S

from app.pipeline import cite_in_order


def _src(i, url):
    return S(id=i, title=f"t-{i}", url=url)


SOURCES = [_src("sup-duvidas-05", "https://x/duvidas"), _src("sup-operacional-01", "https://x/operacional"),
           _src("prod-crediario-08", "https://x/crediario"), _src("sup-duvidas-06", "https://x/duvidas"),
           _src("sup-pix-09", "https://x/pix"), _src("sup-erro-adq-1-84-01", "https://x/adq")]


def _render(answer):
    return cite_in_order(answer, SOURCES, {s.id for s in SOURCES}, "pt")


def test_numbers_follow_first_citation_and_list_has_only_cited():
    answer = ("Confira o chip [sup-erro-adq-1-84-01]. Faça o teste de comunicação [sup-duvidas-06]. "
              "Se não voltar, reinicie [sup-duvidas-05][sup-erro-adq-1-84-01].")
    text, cites = _render(answer)
    assert text == ("Confira o chip [1]. Faça o teste de comunicação [2]. Se não voltar, reinicie [1][2].")
    assert [(c.n, c.url) for c in cites] == [(1, "https://x/adq"), (2, "https://x/duvidas")]
    assert cites[1].ids == ["sup-duvidas-06", "sup-duvidas-05"]  # a mesma página divide o número (ordem da citação)
    # crediário e pix foram recuperados e nunca citados: fora da lista que o cliente vê
    assert {c.url for c in cites}.isdisjoint({"https://x/crediario", "https://x/pix"})


def test_every_number_in_the_answer_is_in_the_list():
    import re

    answer = "A [sup-pix-09]. B [sup-operacional-01][sup-pix-09]. C (fontes: sup-duvidas-05 e sup-pix-09)."
    text, cites = _render(answer)
    used = {int(n) for n in re.findall(r"\[(\d+)\]", text)}
    assert used == {c.n for c in cites} == {1, 2, 3}
    assert text.startswith("A [1]. B [1][2]. C [1][3]")  # números ordenados dentro da citação


def test_id_inside_a_comment_gets_no_number():
    """DEMO da rodada 15 (official-01): "[prod-get-tap-04 is not cited for this; the source is [7]]". O id dentro de
    um comentário não vira citação (number_citations deixa o colchete que não é só de ids), então não ganha número
    nem entra na lista. Tirar o comentário em si é outro item (#1)."""
    answer = "Usa chip [sup-duvidas-05]. [sup-pix-09 is not cited here] Teste [sup-duvidas-06]."
    text, cites = _render(answer)
    assert [c.url for c in cites] == ["https://x/duvidas"] and "[1]" in text and "[2]" not in text


def test_answer_without_citation_has_empty_list_and_unchanged_text():
    text, cites = _render("Sua maquininha T1988B está offline há 5 horas.")
    assert cites == [] and text == "Sua maquininha T1988B está offline há 5 horas."


def test_api_returns_citations_that_match_the_numbers():
    import re

    from fastapi.testclient import TestClient

    from app.api import app
    from app.auth import issue_token

    body = TestClient(app).post("/chat", json={"message": "Qual o prazo de entrega?"},
                                headers={"Authorization": f"Bearer {issue_token('u1')}"}).json()
    assert isinstance(body["citations"], list)  # o domínio de exemplo responde sem LLM: a prova ao vivo é o DEMO
    used = {int(n) for n in re.findall(r"\[(\d+)\]", body["answer"])}
    assert used == {c["n"] for c in body["citations"]}
    assert body["sources"]  # o consultado continua para o eval


def test_demo_lists_cited_sources_and_live_data_but_never_uncited_index_pages():
    import importlib.util
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location("demo_md", root / "scripts" / "demo_md.py")
    demo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(demo)
    rows = [{"id": "official-05", "run": 0, "message": "?", "answer": "Confira o chip [1].", "checks": {},
             "sources": [{"id": "sup-duvidas-05", "url": "https://x/duvidas"},
                         {"id": "prod-crediario-08", "url": "https://x/crediario"}],
             "citations": [{"n": 1, "url": "https://x/duvidas", "title": "t", "ids": ["sup-duvidas-05"]}]},
            {"id": "official-07", "run": 0, "message": "?", "answer": "R$ 6,15 (Banco Central).", "checks": {},
             "sources": [{"id": "https://bcb/x", "url": "https://bcb/x"}], "citations": []}]
    md = demo.render({"rows": rows, "split": "official"}, "official", "abc1234", "2026-11-04")
    assert "**Fontes citadas:** [1] <https://x/duvidas>" in md
    assert "crediario" not in md  # recuperada e não citada: fora
    assert "**Dados ao vivo de:** <https://bcb/x>" in md
