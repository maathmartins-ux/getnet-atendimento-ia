"""Pergunta de requisito de um produto → busca de requisitos (agents.with_requirement_query). Rodada 15: os critérios
para habilitar o Pix ficavam fora das fontes nas 3 rodadas; com a busca, entram em 3º no top-5 fundido."""
from __future__ import annotations

import pytest

from app import agents, domain

REQ = "critérios de elegibilidade para habilitação do"


@pytest.mark.parametrize("text, product", [
    ("Do I need a bank account to receive my sales via Pix?", "Pix"),
    ("Para receber Pix das vendas preciso abrir conta em banco?", "Pix"),
    ("É obrigatório o uso de antifraude para transações Link de Pagamento?", "Link de Pagamento"),
    ("Is a website required to issue a payment link?", "Link de Pagamento"),
])
def test_requirement_question_gets_the_requirement_search(domain_data, text, product):
    assert domain.active().requirement_query(text) == f"{REQ} {product}"


@pytest.mark.parametrize("text", [
    "Como funciona o Pix na maquininha?",          # não é requisito
    "Do I need help with my card machine?",        # requisito sem produto
    "Quanto vendi ontem no Pix?",                   # dado do cliente
])
def test_other_questions_get_none(domain_data, text):
    assert domain.active().requirement_query(text) is None


def test_the_criteria_passage_enters_the_fused_top_k(domain_data):
    """Com as buscas do router gravadas na rodada 15, o trecho dos critérios do Pix entra no top-k fundido."""
    own = "Do I need a bank account to receive my sales via Pix?"
    got = agents.retrieve(own, standalone=own, queries=["Pix recebimento de vendas conta bancária"])
    assert got.plan.queries[0] == own and got.plan.queries[-1] == f"{REQ} Pix"
    assert any("Domicílio bancário Santander" in h.doc.text for h in got.hits)
