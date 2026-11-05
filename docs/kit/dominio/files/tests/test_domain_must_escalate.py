"""Pedido de ação que nenhuma tool faz abre o caso humano (pipeline.must_escalate, hook do domínio). Medido ao vivo na
rodada 16: a troca de CNPJ/conta e o pagamento de boleto saíam só com a oferta de atendente."""
from __future__ import annotations

import pytest

from app import domain


@pytest.mark.parametrize("text, reason", [
    ("Troque o CNPJ e a conta bancária cadastrados na minha conta Getnet.", "account_change"),
    ("Please update the bank account where my payouts go.", "account_change"),
    ("Pague agora o boleto do meu fornecedor com o saldo da minha conta.", "unsupported_action"),
    ("Pay this boleto from my supplier using my Getnet balance.", "unsupported_action"),
])
def test_action_without_tool_escalates(domain_data, text, reason):
    assert domain.active().must_escalate(text) == reason


@pytest.mark.parametrize("text", [
    "Registre um chamado: minha maquininha T1988B está sem sinal.",   # tem tool (proposta)
    "Quero antecipar R$ 2.000,00 dos meus recebíveis.",               # tem tool (proposta)
    "Como pago um boleto?",                                           # dúvida
    "Como troco o CNPJ da minha conta?",                              # dúvida
    "Posso trocar a conta de recebimento?",                           # dúvida
    "Quanto vendi ontem?",
])
def test_tool_actions_and_questions_do_not(domain_data, text):
    assert domain.active().must_escalate(text) is None


def test_offline_records_says_the_boleto_is_not_paid_here(domain_data):
    from fastapi.testclient import TestClient

    from app.api import app
    from app.auth import LIMITER, issue_token

    LIMITER.reset()
    body = TestClient(app).post("/chat", json={"message": "Pague agora o boleto do meu fornecedor."},
                                headers={"Authorization": f"Bearer {issue_token('cliente1988')}"}).json()
    assert body["handoff"]["required"] is True and body["route"][-1] == "escalation"
    assert body["answer"].startswith("Pagamento de boleto não é feito por aqui")
