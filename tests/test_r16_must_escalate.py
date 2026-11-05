"""Rodada 16: pedido de ação que nenhuma tool faz abre o caso humano (hook `must_escalate` do domínio).
Medido ao vivo: a troca de CNPJ/conta e o pagamento de boleto saíam só com a OFERTA de atendente."""
from __future__ import annotations

from app import domain, pipeline
from app.agents import AgentResult, Context
from app.schemas import Handoff


def _ctx(intent="support") -> Context:
    return Context(text="Troque o CNPJ da minha conta.", user_id="u1", conversation_id="c1", intent=intent,
                   language="pt", history=[])


def _esc(monkeypatch, calls):
    def fake(ctx):
        calls.append(ctx.handoff_reason)
        return AgentResult(agent="escalation", status="ok", text="Abri o caso CASE-1 para um atendente.",
                           handoff=Handoff(required=True, reason=ctx.handoff_reason, ticket_id="CASE-1"))
    monkeypatch.setattr(pipeline, "escalation_agent", fake)


def test_request_without_tool_opens_the_case_and_drops_the_offer(monkeypatch):
    calls: list = []
    _esc(monkeypatch, calls)
    monkeypatch.setattr(domain.active(), "must_escalate", lambda t: "account_change", raising=False)
    route = ["router", "faq"]
    answer, handoff = pipeline.must_escalate(
        "Não consigo trocar o CNPJ por aqui. Se quiser, posso abrir um caso para um atendente humano.",
        Handoff(), _ctx(), "Troque o CNPJ da minha conta.", route)
    assert handoff.required and handoff.ticket_id == "CASE-1" and calls == ["account_change"]
    assert route[-1] == "escalation"
    assert "Se quiser" not in answer and answer.startswith("Não consigo trocar o CNPJ por aqui.")
    assert answer.endswith("Abri o caso CASE-1 para um atendente.")


def test_without_hook_or_reason_nothing_changes(monkeypatch):
    calls: list = []
    _esc(monkeypatch, calls)
    monkeypatch.delattr(domain.active(), "must_escalate", raising=False)
    assert pipeline.must_escalate("ok", Handoff(), _ctx(), "x", []) == ("ok", Handoff())
    monkeypatch.setattr(domain.active(), "must_escalate", lambda t: None, raising=False)
    assert pipeline.must_escalate("ok", Handoff(), _ctx(), "x", []) == ("ok", Handoff())
    assert calls == []


def test_already_escalated_turn_does_not_open_a_second_case(monkeypatch):
    calls: list = []
    _esc(monkeypatch, calls)
    monkeypatch.setattr(domain.active(), "must_escalate", lambda t: "account_change", raising=False)
    done = Handoff(required=True, reason="supervisor_decision", ticket_id="CASE-0")
    assert pipeline.must_escalate("ok", done, _ctx(), "x", []) == ("ok", done)
    assert calls == []


def test_offer_only_calls_the_domain_hook_with_text_not_context(monkeypatch):
    """Achado da revisão: o gancho recebia o Context e o do domínio espera o texto (TypeError ao escalar por lacuna)."""
    from app import agents

    seen = []
    monkeypatch.setattr(domain.active(), "must_escalate", lambda t: seen.append(t) or ("account_change" if "CNPJ" in t
                                                                                       else None), raising=False)
    gap = _ctx("knowledge")
    gap.handoff_reason = "faq_partial_coverage"
    gap.text = "Como funciona o Pix?"
    assert agents.escalation_offer_only(gap) is True and seen == ["Como funciona o Pix?"]
    gap.text = "Troque o CNPJ da minha conta."
    assert agents.escalation_offer_only(gap) is False  # o domínio exige o caso: abre, não oferece
