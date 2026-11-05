"""Rodada 16 (#16, avaliação real da rodada 15: "dev com token de operador compartilhado"): o compose do dev diz como
gerar a chave pessoal e não liga o token compartilhado junto dela; o console avisa quando o acesso é o compartilhado."""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_dev_compose_keeps_the_shared_token_off_next_to_personal_keys():
    raw = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    env = yaml.safe_load(raw)["services"]["api"]["environment"]
    assert "OPERATOR_SHARED_TOKEN" not in env  # o padrão (off) vale: com chave pessoal, o compartilhado sai
    assert "python -m app.auth operator-key" in raw and "OPERATOR_KEYS" in raw


def test_operator_console_warns_on_the_shared_token(monkeypatch):
    from fastapi.testclient import TestClient

    from app.api import app

    html = (ROOT / "src" / "app" / "static" / "operator.html").read_text(encoding="utf-8")
    assert 'id="shared"' in html and 'h.operator_auth !== "shared"' in html and "operator-key" in html
    c = TestClient(app)
    monkeypatch.delenv("OPERATOR_KEYS", raising=False)
    assert c.get("/health").json()["operator_auth"] == "shared"
    monkeypatch.setenv("OPERATOR_KEYS", "ana:" + "0" * 64)
    assert c.get("/health").json()["operator_auth"] == "personal"
