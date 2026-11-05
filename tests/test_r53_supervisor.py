"""Supervisor: "partial" é resposta (nunca escala por si); offline o insufficient segue o FALLBACK da tabela."""
import pytest
from fakes import fake_llm, resp, text, tool_use

from app import supervisor
from app.agents import AgentResult, Context
from app.llm import get_llm
from app.observability import new_trace_id


def ctx(text_="Qual a taxa do débito?", intent="faq", **facts):
    c = Context(text=text_, language="pt", user_id="u1", conversation_id="c-r53", intent=intent)
    c.facts.update(facts)
    return c


def use_llm(monkeypatch, llm):
    monkeypatch.setattr(supervisor, "get_llm", lambda role="agent": llm)


def stub(monkeypatch, name, status, calls=None, **kw):
    def agent(c):
        if calls is not None:
            calls.append(name)
        return AgentResult(name, status, **kw)
    monkeypatch.setitem(supervisor.AGENTS, name, agent)


PARTIAL = dict(text="A taxa do débito é 1,99% [doc-1]. A fonte não traz a taxa do crédito.", reason="partial")


@pytest.fixture(autouse=True)
def _fresh_turn():
    new_trace_id()  # orçamento por turno zerado


# --- partial é resposta ----------------------------------------------------------------------------------------
def test_partial_on_the_offline_table_is_not_escalated(monkeypatch):
    assert not get_llm("supervisor").enabled  # CI: sem LLM
    stub(monkeypatch, "faq", "partial", **PARTIAL)
    out = supervisor.run(["faq"], ctx(), confidence=0.95)
    assert out.route == ["faq"] and out.replans == [] and not any(r.handoff for r in out.results)


def test_partial_in_a_two_step_plan_keeps_the_plan_and_does_not_escalate(monkeypatch):
    stub(monkeypatch, "faq", "partial", **PARTIAL)
    stub(monkeypatch, "records", "ok", text="Pedido 1002: enviado.")
    out = supervisor.run(["faq", "records"], ctx("taxa e pedido 1002?", "multi"), confidence=0.8)
    assert out.route == ["faq", "records"] and out.replans == []


def test_partial_in_the_llm_engine_does_not_mark_a_handoff_reason(monkeypatch):
    llm, _ = fake_llm([resp("tool_use", tool_use("faq_agent", {"query": "taxa"})), resp("end_turn", text("ok"))])
    use_llm(monkeypatch, llm)
    stub(monkeypatch, "faq", "partial", **PARTIAL)
    c = ctx()
    out = supervisor.run(["faq"], c, confidence=0.95)
    assert out.route == ["faq"] and c.handoff_reason is None


# --- insufficient ----------------------------------------------------------------------------------------------
def test_offline_insufficient_keeps_the_table_fallback(monkeypatch):
    assert not get_llm("supervisor").enabled  # CI: sem LLM, a tabela de sempre
    stub(monkeypatch, "faq", "insufficient", reason="no_source")
    out = supervisor.run(["faq"], ctx("Qual a capital da Mongólia?"), confidence=0.95)
    assert out.engine == "table" and out.route == ["faq", "escalation"]
    assert out.replans == ["faq:no_source->escalation"] and out.results[-1].handoff.reason == "faq_no_source"


def test_llm_supervisor_sees_the_standalone_question(monkeypatch):
    llm, msgs = fake_llm([resp("end_turn", text("ok"))])
    use_llm(monkeypatch, llm)
    supervisor.run(["faq"], ctx("e a outra?", standalone="Qual a taxa da Get Smart?"), confidence=0.95)
    assert "Pergunta completa (router): Qual a taxa da Get Smart?" in msgs.sent[0]["messages"][0]["content"]
