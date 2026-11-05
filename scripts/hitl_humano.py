"""Atendimento humano de verdade: uma PESSOA responde um caso pelo console do operador (`/operator`) com a chave pessoal
dela, e docs/HITL_HUMANO.md guarda a conversa, os horários do caso (aberto, respondido, retomado) e a auditoria.

O eval mede o caminho humano com uma operadora simulada (evals/operator_sim.py); aqui ninguém é simulado. O script sobe
a API numa porta, abre a conversa pelo `POST /chat` como o cliente, espera a pessoa responder pelo console e só grava se
a auditoria registrou a resposta com o nome dela (chave pessoal; o token compartilhado "admin" não vale).

Uso:
    python scripts/hitl_humano.py --nome ana [--host 127.0.0.1] [--porta 8765] [--espera-min 15]
A chave pessoal é gerada nesta execução e aparece só no terminal (o processo guarda só o sha256 em OPERATOR_KEYS);
abra http://<host>:<porta>/operator, cole a chave, carregue a fila e responda o caso.
Saída: 0 = arquivo gravado; 2 = a mensagem não abriu caso, ninguém respondeu no prazo ou a resposta não veio da chave
pessoal (nada gravado).
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import os
import secrets
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "HITL_HUMANO.md"
USER = "cliente1988"
STARTUP_S = 180.0
MESSAGE = "Quero falar com um atendente: tem uma cobrança na minha conta que eu não reconheço."


def personal_key(name: str) -> tuple[str, str]:
    """(chave, entrada "nome:sha256" do OPERATOR_KEYS). A chave nunca vai para arquivo."""
    key = secrets.token_urlsafe(24)
    return key, f"{name}:{hashlib.sha256(key.encode()).hexdigest()}"


def _when(ts: float | None) -> str:
    return datetime.datetime.fromtimestamp(ts, datetime.UTC).strftime("%Y-%m-%d %H:%M:%S UTC") if ts else "—"


def run(client, headers: dict, message: str, wait_s: float, poll_s: float = 2.0, resume_s: float = 60.0) -> dict:
    """Abre a conversa, espera a resposta humana do caso e a mensagem retomada. `client`: qualquer cliente HTTP com
    `post`/`get` (httpx.Client no servidor de verdade; TestClient no teste). Devolve o registro para o arquivo."""
    from app.store import get_store

    first = client.post("/chat", json={"message": message}, headers=headers).json()
    ticket_id = ((first.get("handoff") or {}).get("ticket_id"))
    rec = {"message": message, "first": first, "ticket_id": ticket_id, "error": None}
    if not ticket_id:
        rec["error"] = "a mensagem não abriu caso humano"
        return rec
    print(f"caso {ticket_id} aberto: responda pelo console /operator", file=sys.stderr, flush=True)
    store, deadline = get_store(), time.monotonic() + wait_s
    ticket = store.get_ticket(ticket_id)
    while ticket and ticket.get("status") == "open" and time.monotonic() < deadline:
        time.sleep(poll_s)
        ticket = store.get_ticket(ticket_id)
    rec["ticket"] = ticket
    if not ticket or not ticket.get("answered_at"):
        rec["error"] = "ninguém respondeu o caso no prazo"
        return rec
    conv, resumed, deadline = first.get("conversation_id"), None, time.monotonic() + resume_s
    while resumed is None and time.monotonic() < deadline:
        msgs = client.get(f"/conversations/{conv}", headers=headers).json().get("messages") or []
        resumed = next((m for m in msgs if m["role"] == "assistant" and m["ts"] >= ticket["answered_at"]), None)
        if resumed is None:
            time.sleep(poll_s)
    rec["resumed"] = resumed
    rec["audit"] = store.audit_for(ticket_id, "handoff_reply")
    return rec


def problems(rec: dict, name: str) -> list[str]:
    """O que impede de chamar isto de prova: sem caso, sem resposta, resposta de outra chave ou sem auditoria."""
    if rec.get("error"):
        return [rec["error"]]
    out = []
    ticket = rec.get("ticket") or {}
    if ticket.get("answered_by") != name:
        out.append(f"o caso foi respondido por {ticket.get('answered_by')!r}, não pela chave pessoal de {name!r}")
    if not any(a.get("actor") == f"operator:{name}" for a in rec.get("audit") or []):
        out.append("a auditoria não registrou a resposta com o nome da pessoa")
    if not rec.get("resumed"):
        out.append("o assistente não retomou a conversa depois da resposta")
    return out


def markdown(rec: dict, name: str, sha: str, when: str, provider: str) -> str:
    ticket, first, resumed = rec["ticket"], rec["first"], rec["resumed"]
    audit = ", ".join(f"`{a['actor']}` (canal {(a.get('detail') or {}).get('channel', '?')}, {_when(a.get('ts'))})"
                      for a in rec["audit"])
    took = ticket["answered_at"] - ticket["created_at"]
    return "\n".join([
        "# Atendimento humano de verdade",
        "",
        f"Gerado por `scripts/hitl_humano.py` no commit `{sha}` em {when} (LLM: `{provider}`). A conversa foi "
        "aberta pelo `POST /chat`; quem respondeu o caso foi uma pessoa, pelo console `/operator`, com chave pessoal "
        "gerada nesta execução (o processo guardou só o sha256 dela em `OPERATOR_KEYS`; o token compartilhado não "
        "valia). Nada foi escrito à mão.",
        "",
        f"**Cliente** (`{USER}`): {rec['message']}",
        "",
        f"**Assistente:** {first.get('answer', '').strip()}",
        "",
        f"**Atendente** (`pessoa:{name}`, caso `{ticket['id']}`): {ticket.get('answer', '').strip()}",
        "",
        f"**Assistente, retomando depois do atendente:** {resumed['content'].strip()}",
        "",
        "| caso | aberto | respondido | retomado | tempo até a resposta |",
        "|---|---|---|---|---:|",
        f"| `{ticket['id']}` ({ticket.get('reason')}) | {_when(ticket['created_at'])} | {_when(ticket['answered_at'])} "
        f"| {_when(resumed['ts'])} | {int(took // 60)} min {int(took % 60):02d} s |",
        "",
        f"Auditoria do caso: `handoff_reply` registrado por {audit}.",
        "",
    ])


def _serve(host: str, port: int):
    import uvicorn

    from app.api import app

    server = uvicorn.Server(uvicorn.Config(app, host=host, port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.monotonic() + STARTUP_S  # a subida carrega o índice e os modelos da busca
    while time.monotonic() < deadline and thread.is_alive():
        if server.started:
            return server, thread
        time.sleep(0.2)
    raise SystemExit(f"a API não subiu em {host}:{port} em {STARTUP_S:.0f} s")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nome", required=True, help="nome de quem vai responder (vai na auditoria como pessoa:<nome>)")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--porta", type=int, default=8765)
    ap.add_argument("--espera-min", type=float, default=15.0)
    ap.add_argument("--mensagem", default=MESSAGE)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args(argv)
    name = args.nome.strip()
    if not name or name.lower() == "admin":
        print('escolha o nome da pessoa ("admin" é o nome reservado do token compartilhado)', file=sys.stderr)
        return 2
    key, entry = personal_key(name)
    db = ROOT / "var" / "hitl_humano.db"
    db.parent.mkdir(parents=True, exist_ok=True)
    db.unlink(missing_ok=True)
    os.environ.update(DB_PATH=str(db), OPERATOR_KEYS=",".join(filter(None, [os.getenv("OPERATOR_KEYS"), entry])),
                      OPERATOR_SHARED_TOKEN="off")
    sys.path[:0] = [str(ROOT / "src")]
    import httpx

    from app.auth import issue_token

    server, thread = _serve(args.host, args.porta)
    print(f"console: http://{args.host}:{args.porta}/operator\nchave pessoal de {name} (só nesta execução): {key}",
          file=sys.stderr, flush=True)
    try:
        with httpx.Client(base_url=f"http://{args.host}:{args.porta}", timeout=180) as client:
            rec = run(client, {"Authorization": f"Bearer {issue_token(USER)}"}, args.mensagem, args.espera_min * 60)
    finally:
        server.should_exit = True
        thread.join(timeout=10)
    bad = problems(rec, name)
    if bad:
        print("NADA GRAVADO: " + "; ".join(bad), file=sys.stderr)
        return 2
    sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout
    when = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M UTC")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(markdown(rec, name, sha.strip() or "sem-git", when, os.getenv("LLM_PROVIDER", "offline")),
                        encoding="utf-8")
    print(f"gravado {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
