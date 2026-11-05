"""docs/ESSENCIAL.md: o que é essencial para o enunciado e o que é opcional, com as linhas de cada parte.

A pergunta é de quem herda o código: "se tivesse que entregar este sistema para outro time manter, o que cortaria?"
(medido: quem lê ~15 mil linhas para um bot de suporte pergunta isso primeiro). As linhas saem do disco e o
`tests/test_r16_essencial.py` reprova o doc velho; nenhum número aqui é digitado à mão.
Uso: python scripts/module_map.py            (grava docs/ESSENCIAL.md)
     python scripts/module_map.py --check    (sai com 1 se o doc não for o que o código dá hoje)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "src" / "app"
OUT = ROOT / "docs" / "ESSENCIAL.md"

# (grupo, o que entrega, módulos, o que se perde ao cortar; None = não corta sem perder o enunciado)
GROUPS = [
    ("Núcleo do enunciado", "Router, Knowledge com RAG, Customer Support com tools, agente geral, POST /chat",
     ["api.py", "pipeline.py", "router.py", "followup.py", "supervisor.py", "agents.py", "rag.py", "ingest.py",
      "tools.py", "live_data.py", "schemas.py", "llm.py", "config.py", "store.py", "memory.py", "jsonl.py",
      "clock.py"], None),
    ("Conferência da resposta", "número e frase sem base saem; parcial só quando falta o que o cliente pediu",
     ["grounding.py", "claims.py", "coverage.py", "capabilities.py"], None),
    ("Segurança e identidade", "JWT, guardrails, PII mascarada",
     ["auth.py", "guardrails.py"], None),
    ("Chaves rotacionáveis", "JWKS com HS256, EdDSA e RS256",
     ["keys.py"], "fica só HS256 com um segredo; sem rotação sem derrubar sessões"),
    ("Humano no laço (bônus)", "operador consultado no turno, caso assíncrono com retomada",
     ["hitl_sync.py", "resume.py", "cases.py", "casestate.py"], "o caso vira só ticket: o plano não continua depois "
     "da resposta do operador"),
    ("Fila humana avançada", "especialidade do operador, SLA que re-roteia, aviso por Telegram",
     ["routing.py", "notify.py"], "um operador genérico, sem SLA nem Telegram"),
    ("Ações com risco", "confirmação do dono, quatro olhos, limite de valor, execução única",
     ["actions.py", "risk.py"], "as tools ficam só de leitura"),
    ("Operação e escala", "métricas, analytics, 👎 → caso de teste, Postgres para vários hosts, MCP",
     ["observability.py", "analytics.py", "candidates.py", "store_pg.py", "mcp_server.py"],
     "réplicas só no mesmo host (SQLite); sem MCP nem analytics (o log JSON com custo fica em observability.py)"),
]


def lines(path: Path) -> int:
    files = sorted(path.rglob("*.py")) if path.is_dir() else [path]
    return sum(len(f.read_text(encoding="utf-8").splitlines()) for f in files if f.is_file())


def env_vars() -> int:
    rx = re.compile(r"""os\.(?:getenv|environ\.get)\(\s*["']([A-Z][A-Z0-9_]+)["']""")
    return len({m for f in APP.rglob("*.py") if "domain" not in f.relative_to(APP).parts
                for m in rx.findall(f.read_text(encoding="utf-8"))})


def render() -> str:
    # o domínio do desafio (src/app/domain/) fica fora: ele é montado no relógio e muda por desafio; o mapa é do motor
    seen = {str(p.relative_to(APP)) for p in APP.glob("*.py") if p.name != "__init__.py"}
    rows, total, core, missing = [], 0, 0, []
    for name, what, mods, cut in GROUPS:
        n = sum(lines(APP / m) for m in mods)
        total += n
        if cut is None:
            core += n
        missing += [m for m in mods if not (APP / m).exists()]
        seen -= set(mods)
        rows.append(f"| {name} | {what} | {n} | {', '.join(f'`{m}`' for m in mods)} | "
                    f"{'não sem perder o enunciado ou a qualidade medida' if cut is None else cut} |")
    if missing or seen:
        raise SystemExit(f"módulos fora do mapa: {sorted(seen)}; inexistentes: {missing} (atualize GROUPS)")
    return "\n".join([
        "# O essencial e o opcional",
        "",
        "Gerado por `scripts/module_map.py` a partir das linhas de `src/app/` (o teste reprova o doc velho).",
        "",
        f"O motor em `src/app/` (fora o domínio do desafio, `src/app/domain/`, que muda por desafio) tem "
        f"**{total} linhas**; o que o enunciado pede (núcleo, conferência da resposta e segurança) "
        f"soma **{core}** ({round(100 * core / total)}%). O resto é bônus ou operação e sai em blocos, cada um com o "
        "que se perde. Configuração por variável de ambiente: "
        f"**{env_vars()}** nomes no motor, todos com padrão no código (roda sem `.env`).",
        "",
        "| Parte | O que entrega | Linhas | Módulos | Se cortar |",
        "|---|---|---:|---|---|",
        *rows,
        "",
        "Para outro time manter com menos código, a ordem de corte é a de baixo para cima da tabela: "
        "operação e escala, "
        "ações com risco, fila humana avançada e chaves rotacionáveis saem sem tocar no caminho de uma mensagem "
        "(`src/app/pipeline.py`). O humano no laço é bônus do enunciado, mas é o que mais pesa na supervisão humana.",
        "",
    ])


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    text = render()
    if "--check" in argv:
        ok = OUT.exists() and OUT.read_text(encoding="utf-8") == text
        print("docs/ESSENCIAL.md em dia" if ok else "docs/ESSENCIAL.md velho: rode python scripts/module_map.py")
        return 0 if ok else 1
    OUT.write_text(text, encoding="utf-8")
    print(f"gravado {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
