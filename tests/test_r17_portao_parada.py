"""Portão sem fonte com parada no 1º trecho que passa: a mesma resposta do portão com menos pares no cross-encoder.

Na ordem do base o portão só pergunta se ALGUM trecho tem nota >= limiar (agents.covered_hits). Pontuando na ordem e
parando no primeiro que passa, a resposta é a mesma por construção; a calibração do limiar (retrieval_eval.evaluate)
continua lendo a maior nota, com todos os pares pontuados.
"""
import random

import pytest

from app import agents, rag
from app.rag import Doc, Hit


class _Base:
    name = "dense"

    def __init__(self, hits):
        self.hits = hits

    def search(self, query, k=3):
        return self.hits[:k]


class _Scorer:
    """Nota fixa por trecho (pelo número no fim do texto) e a conta dos pares pontuados."""

    name = "conta"
    pairwise = True

    def __init__(self, notes):
        self.notes, self.seen = notes, []

    def score(self, query, texts):
        self.seen += texts
        return [self.notes[int(t.rsplit(" ", 1)[1])] for t in texts]


def _pool(n=10):
    return [Hit(Doc(f"d{i}", f"t{i}", f"u{i}", f"texto {i}"), 1.0 - i / 100, bm25=1.0, cosine=0.9 - i / 100)
            for i in range(n)]


def _retriever(notes, limiar):
    scorer = _Scorer(notes)
    r = rag.CrossRerankRetriever(_Base(_pool(len(notes))), scorer, pool=len(notes), chars=600, order="base")
    r.gate = {"min_rerank": limiar}
    return r, scorer


def _full(notes, limiar):
    """A resposta do portão com todos os pares pontuados (o caminho de antes)."""
    r, scorer = _retriever(notes, limiar)
    token = rag.FULL_RERANK.set(True)
    try:
        return agents.covered_search(r, "q", 5), len(scorer.seen)
    finally:
        rag.FULL_RERANK.reset(token)


@pytest.mark.parametrize("limiar, pares", [(-2.0, 1), (0.5, 4), (9.0, 5)])
def test_gate_answer_is_the_same_and_stops_at_the_first_passing_pair(limiar, pares):
    notes = [-1.5, -1.0, 0.2, 0.7, 1.1, 3.0, 3.0, 3.0, 3.0, 3.0]  # o 6º em diante nem chega ao top 5
    r, scorer = _retriever(notes, limiar)
    got = agents.covered_search(r, "q", 5)
    full, full_pairs = _full(notes, limiar)
    assert [h.doc.id for h in got] == [h.doc.id for h in full]  # mesma resposta do portão e mesmos trechos
    assert len(scorer.seen) == pares and full_pairs == 5
    assert bool(got) == (limiar <= max(notes[:5]))  # 9,0: nenhum passa, sem fonte nos dois caminhos
    hits = _retriever(notes, limiar)[0].search("q", k=5, enough=limiar)
    assert [h.rerank for h in hits[:pares]] == notes[:pares]  # a nota que existe é a mesma
    assert all(h.rerank is None for h in hits[pares:])  # depois do que passou, ninguém foi pontuado


def test_random_notes_and_thresholds_never_change_the_gate():
    rnd = random.Random(17)
    for _ in range(300):
        notes = [round(rnd.uniform(-8, 4), 2) for _ in range(10)]
        limiar = round(rnd.uniform(-9, 5), 2)
        got = agents.covered_search(_retriever(notes, limiar)[0], "q", 5)
        full, _ = _full(notes, limiar)
        assert [h.doc.id for h in got] == [h.doc.id for h in full]


def test_calibration_reads_every_note():
    """A calibração do limiar lê a maior nota de cada pergunta: dentro do evaluate, todos os pares."""
    from evals import retrieval_eval

    seen = {}
    real = retrieval_eval._evaluate
    try:
        retrieval_eval._evaluate = lambda path, retriever, warmup: seen.setdefault("full", rag.FULL_RERANK.get())
        retrieval_eval.evaluate(None, None)
    finally:
        retrieval_eval._evaluate = real
    assert seen["full"] is True and rag.FULL_RERANK.get() is False
    r, scorer = _retriever([-1.5, -1.0, 0.2, 0.7, 1.1], -2.0)
    token = rag.FULL_RERANK.set(True)
    try:
        hits = r.search("q", k=5, enough=-2.0)
    finally:
        rag.FULL_RERANK.reset(token)
    assert len(scorer.seen) == 5 and max(h.rerank for h in hits) == 1.1


def test_cross_order_and_retrievers_without_the_stop_ignore_the_threshold():
    notes = [-1.5, -1.0, 0.2, 0.7, 1.1, 3.0]
    scorer = _Scorer(notes)
    ranked = rag.CrossRerankRetriever(_Base(_pool(6)), scorer, pool=6, chars=600, order="cross")
    ranked.search("q", k=5, enough=-2.0)
    assert len(scorer.seen) == 6  # reordenar pela nota precisa da nota de todos

    class Plain(_Base):  # buscador sem rerank: a busca não recebe o limiar
        def search(self, query, k=3):
            return super().search(query, k)

    plain = Plain(_pool(3))
    plain.gate = {"min_rerank": -2.0}
    assert isinstance(agents.covered_search(plain, "q", 3), list)  # sem `enough` na assinatura: não quebra


def test_broken_scorer_mid_way_still_answers_in_the_base_order():
    class Breaks(_Scorer):
        def score(self, query, texts):
            if self.seen:
                raise RuntimeError("onnx quebrou")
            self.seen += texts
            return [-9.0]  # o 1º não passa; o 2º quebra

    r = rag.CrossRerankRetriever(_Base(_pool(10)), Breaks([0] * 10), pool=10, chars=600, order="base")
    got = r.search("q", k=5, enough=-2.0)
    assert [h.doc.id for h in got] == ["d0", "d1", "d2", "d3", "d4"] and all(h.rerank is None for h in got)


def test_nan_note_never_decides_the_gate_and_both_paths_agree():
    """Nota NaN no 1º par: a parada segue para o próximo e o portão completo também a ignora (o max com NaN mentia)."""
    nan = float("nan")
    for notes, limiar, pares in (([nan, 0.5, -3, -3, -3], 0.0, 2), ([nan, -3, -3, -3, -3], 0.0, 5)):
        r, scorer = _retriever(notes, limiar)
        got = agents.covered_search(r, "q", 5)
        full, _ = _full(notes, limiar)
        assert [h.doc.id for h in got] == [h.doc.id for h in full] and len(scorer.seen) == pares
    assert agents.covered_search(_retriever([nan, 0.5, -3, -3, -3], 0.0)[0], "q", 5)  # o 2º trecho tem fonte


def test_batch_scorer_is_never_called_pair_by_pair():
    """Scorer em lote (sem `pairwise`): a busca não recebe o limiar e pontua tudo numa chamada só."""
    class Batch(_Scorer):
        pairwise = False

        def score(self, query, texts):
            self.calls = getattr(self, "calls", 0) + 1
            return super().score(query, texts)

    scorer = Batch([-1.5, -1.0, 0.2, 0.7, 1.1])
    r = rag.CrossRerankRetriever(_Base(_pool(5)), scorer, pool=5, chars=600, order="base")
    r.gate = {"min_rerank": -2.0}
    assert not r.stops_at_gate
    agents.covered_search(r, "q", 5)
    assert scorer.calls == 1 and len(scorer.seen) == 5
