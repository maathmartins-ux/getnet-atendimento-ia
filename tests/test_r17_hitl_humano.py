"""scripts/hitl_humano.py: a prova do atendimento humano só é gravada quando uma chave PESSOAL respondeu o caso pelo
endpoint do console e o assistente retomou a conversa. Aqui a "pessoa" é um operador de teste que faz o que a pessoa
faz no /operator: lista a fila com a chave dela e responde pelo POST /handoffs/{id}/reply."""
from __future__ import annotations

import importlib.util
import threading
import time
from pathlib import Path

from fastapi.testclient import TestClient

from app.api import app
from app.auth import LIMITER, issue_token

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("hitl_humano", ROOT / "scripts" / "hitl_humano.py")
H = importlib.util.module_from_spec(spec)
spec.loader.exec_module(H)
ANSWER = "Olá, sou a Ana do atendimento: abri a contestação da cobrança e o retorno sai em até 5 dias úteis."


def _operator(token: str, stop: threading.Event, answer: str = ANSWER) -> threading.Thread:
    def work():
        console = TestClient(app)
        while not stop.is_set():
            queue = console.get("/handoffs", headers={"X-Operator-Token": token}).json()
            if isinstance(queue, list) and queue:
                console.post(f"/handoffs/{queue[0]['id']}/reply", json={"answer": answer},
                             headers={"X-Operator-Token": token})
                return
            time.sleep(0.05)
    t = threading.Thread(target=work, daemon=True)
    t.start()
    return t


def _run(monkeypatch, token: str, wait_s: float = 20.0):
    monkeypatch.setattr(LIMITER, "allow", lambda key: True)
    monkeypatch.setenv("HITL_SYNC_WAIT_S", "0")  # o turno não espera: a resposta chega depois, como a de uma pessoa
    stop = threading.Event()
    op = _operator(token, stop)
    try:
        return H.run(TestClient(app), {"Authorization": f"Bearer {issue_token('cliente1988')}"}, H.MESSAGE,
                     wait_s=wait_s, poll_s=0.05, resume_s=10)
    finally:
        stop.set()
        op.join(timeout=5)


def test_personal_key_answer_is_recorded_with_times_and_audit(monkeypatch):
    key, entry = H.personal_key("ana")
    assert entry.startswith("ana:") and key not in entry
    monkeypatch.setenv("OPERATOR_KEYS", entry)
    rec = _run(monkeypatch, key)
    assert H.problems(rec, "ana") == []
    assert rec["ticket"]["answered_by"] == "ana" and rec["ticket"]["answer"] == ANSWER
    assert rec["resumed"]["ts"] >= rec["ticket"]["answered_at"] >= rec["ticket"]["created_at"]
    md = H.markdown(rec, "ana", "abc1234", "2026-11-05 12:00 UTC", "offline")
    assert "pessoa:ana" in md and ANSWER in md and "`operator:ana` (canal console" in md
    assert key not in md  # a chave nunca vai para o arquivo
    assert "| aberto | respondido | retomado |" in md


def test_shared_token_answer_is_not_a_proof(monkeypatch):
    monkeypatch.delenv("OPERATOR_KEYS", raising=False)  # sem chave pessoal, o token compartilhado vale como "admin"
    rec = _run(monkeypatch, "test-operator")
    bad = H.problems(rec, "ana")
    assert any("não pela chave pessoal" in b for b in bad) and any("auditoria" in b for b in bad)


def test_nobody_answers_in_time(monkeypatch):
    monkeypatch.setattr(LIMITER, "allow", lambda key: True)
    monkeypatch.setenv("HITL_SYNC_WAIT_S", "0")
    rec = H.run(TestClient(app), {"Authorization": f"Bearer {issue_token('cliente1988')}"}, H.MESSAGE,
                wait_s=0.2, poll_s=0.05)
    assert H.problems(rec, "ana") == ["ninguém respondeu o caso no prazo"]


def test_question_that_opens_no_case():
    class Answered:  # o /chat respondeu sem abrir caso
        def post(self, *a, **k):
            return type("R", (), {"json": lambda self: {"answer": "ok", "handoff": {"required": False}}})()

    rec = H.run(Answered(), {}, "Quanto vendi ontem?", wait_s=0.2, poll_s=0.05)
    assert H.problems(rec, "ana") == ["a mensagem não abriu caso humano"]


def test_admin_name_is_refused():
    assert H.main(["--nome", "admin"]) == 2
