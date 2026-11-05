"""Rodada 16 (#3): a pergunta de requisito ganha a busca de requisitos que o domínio escreve, na última vaga do plano.
O trecho com os critérios ficava fora das fontes (7º na busca do cliente): medido no replay da busca da rodada 15."""
from __future__ import annotations

from app import agents, domain
from app.agents import QueryPlan, with_requirement_query


def _plan(*queries: str, entities=()) -> QueryPlan:
    return QueryPlan(list(queries), list(entities), "pt", [True] * len(queries))


def _hook(monkeypatch, fn):
    monkeypatch.setattr(domain.active(), "requirement_query", fn, raising=False)


def test_without_hook_the_plan_is_unchanged(monkeypatch):
    monkeypatch.delattr(domain.active(), "requirement_query", raising=False)
    plan = _plan("preciso de conta para receber Pix?", "Pix conta")
    assert with_requirement_query(plan, plan.queries[0]) is plan


def test_requirement_query_takes_the_last_slot_and_keeps_the_customer_words_first(monkeypatch):
    _hook(monkeypatch, lambda q: "critérios de elegibilidade para habilitação do Pix")
    monkeypatch.setattr(agents, "faq_max_searches", lambda: 3)
    plan = with_requirement_query(_plan("own", "llm-1", "llm-2"), "own")
    assert plan.queries == ["own", "llm-1", "critérios de elegibilidade para habilitação do Pix"]
    assert plan.translated == [True, True, True]


def test_short_plan_just_gains_the_query(monkeypatch):
    _hook(monkeypatch, lambda q: "req")
    monkeypatch.setattr(agents, "faq_max_searches", lambda: 3)
    assert with_requirement_query(_plan("own"), "own").queries == ["own", "req"]


def test_no_requirement_comparison_or_repeat_keeps_the_plan(monkeypatch):
    _hook(monkeypatch, lambda q: None)
    plan = _plan("own", "llm")
    assert with_requirement_query(plan, "own") is plan
    _hook(monkeypatch, lambda q: "req")
    cmp = _plan("a", "b", entities=["Get Mini", "Get Smart"])
    assert with_requirement_query(cmp, "a") is cmp
    same = _plan("own", "REQ")
    assert with_requirement_query(same, "own") is same


def test_single_search_budget_keeps_only_the_customer_search(monkeypatch):
    _hook(monkeypatch, lambda q: "req")
    monkeypatch.setattr(agents, "faq_max_searches", lambda: 1)
    plan = _plan("own")
    assert with_requirement_query(plan, "own") is plan
