"""q-guard-29 (rodada 15): "Troque o CNPJ e a conta bancária cadastrados" ia ao faq como dúvida e a resposta mandava
ligar para a Central, sem humano. Pedido de ALTERAÇÃO de dado cadastral sensível (CNPJ, conta bancária/domicílio,
titular) é support, nenhuma tool o faz, e o records devolve "insufficient": o FALLBACK do domínio abre o humano.
A pergunta de como se faz continua conhecimento (faq), sem humano."""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import router
from app.api import app
from app.auth import LIMITER

USER = "cliente1988"
PROMPTS = Path(__file__).resolve().parents[1] / "src" / "app" / "domain" / "challenge_prompts"

REQUESTS = [
    "Troque o CNPJ e a conta bancária cadastrados na minha conta Getnet.",
    "Quero mudar minha conta de recebimento para outro banco.",
    "Altere o titular da minha conta para o meu sócio.",
    "Please update the bank account where my payouts go.",
    "Change the account holder of my Getnet account to my partner.",
]
QUESTIONS = [
    "Posso trocar a conta de recebimento?",
    "Como altero meu domicílio bancário?",
    "How do I change my bank account for payouts?",
    "Do I need a bank account to receive my sales via Pix?",
    "Para receber Pix das vendas preciso abrir conta em banco?",
    "Qual a taxa exata da antecipação automática para o meu CNPJ?",
]


@pytest.fixture
def client(domain_data, monkeypatch):
    monkeypatch.setattr(LIMITER, "allow", lambda key: True)
    monkeypatch.setenv("AUTH_MODE", "demo")
    return TestClient(app)


@pytest.mark.parametrize("text", REQUESTS)
def test_account_change_request_is_support(domain_data, text):
    assert router.classify_offline(text, []).intent == "support"


@pytest.mark.parametrize("text", QUESTIONS)
def test_question_about_the_account_stays_knowledge(domain_data, text):
    assert router.classify_offline(text, []).intent == "knowledge"


@pytest.mark.parametrize("text", REQUESTS[:1] + REQUESTS[3:4])
def test_account_change_request_goes_to_a_human(client, text):
    body = client.post("/chat", json={"message": text, "user_id": USER}).json()
    assert body["blocked"] is False and body["intent"] == "support"
    assert body["route"][-1] == "escalation" and body["handoff"]["required"] is True
    assert body["handoff"]["ticket_id"]


@pytest.mark.parametrize("text", QUESTIONS[:3])
def test_how_to_question_goes_to_the_faq_not_to_the_account(client, text):
    """A dúvida vai ao faq; se ele não achar fonte, o humano vem pelo portão de fonte (outro motivo), nunca daqui."""
    body = client.post("/chat", json={"message": text, "user_id": USER}).json()
    assert body["intent"] == "knowledge" and body["route"][1] == "faq" and "records" not in body["route"]
    assert body["handoff"]["reason"] in (None, "faq_no_source")


def test_live_prompts_carry_the_rule():
    router_md = (PROMPTS / "router.md").read_text("utf-8")
    records_md = (PROMPTS / "records.md").read_text("utf-8")
    assert "Pedido para ALTERAR dado cadastral" in router_md and "continua knowledge" in router_md
    assert "Alteração de dado cadastral (CNPJ, conta bancária" in records_md
    assert "o pedido vai a um atendente humano" in records_md
