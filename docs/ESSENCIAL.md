# O essencial e o opcional

Gerado por `scripts/module_map.py` a partir das linhas de `src/app/` (o teste reprova o doc velho).

O motor em `src/app/` (fora o domínio do desafio, `src/app/domain/`, que muda por desafio) tem **14183 linhas**; o que o enunciado pede (núcleo, conferência da resposta e segurança) soma **12338** (87%). O resto é bônus ou operação e sai em blocos, cada um com o que se perde. Configuração por variável de ambiente: **77** nomes no motor, todos com padrão no código (roda sem `.env`).

| Parte | O que entrega | Linhas | Módulos | Se cortar |
|---|---|---:|---|---|
| Núcleo do enunciado | Router, Knowledge com RAG, Customer Support com tools, agente geral, POST /chat | 9751 | `api.py`, `pipeline.py`, `router.py`, `followup.py`, `supervisor.py`, `agents.py`, `rag.py`, `ingest.py`, `tools.py`, `live_data.py`, `schemas.py`, `llm.py`, `config.py`, `store.py`, `memory.py`, `jsonl.py`, `clock.py` | não sem perder o enunciado ou a qualidade medida |
| Conferência da resposta | número e frase sem base saem; parcial só quando falta o que o cliente pediu | 1262 | `grounding.py`, `claims.py`, `coverage.py`, `capabilities.py` | não sem perder o enunciado ou a qualidade medida |
| Segurança e identidade | JWT, guardrails, PII mascarada | 1325 | `auth.py`, `guardrails.py` | não sem perder o enunciado ou a qualidade medida |
| Chaves rotacionáveis | JWKS com HS256, EdDSA e RS256 | 192 | `keys.py` | fica só HS256 com um segredo; sem rotação sem derrubar sessões |
| Humano no laço (bônus) | operador consultado no turno, caso assíncrono com retomada | 488 | `hitl_sync.py`, `resume.py`, `cases.py`, `casestate.py` | o caso vira só ticket: o plano não continua depois da resposta do operador |
| Fila humana avançada | especialidade do operador, SLA que re-roteia, aviso por Telegram | 150 | `routing.py`, `notify.py` | um operador genérico, sem SLA nem Telegram |
| Ações com risco | confirmação do dono, quatro olhos, limite de valor, execução única | 283 | `actions.py`, `risk.py` | as tools ficam só de leitura |
| Operação e escala | métricas, analytics, 👎 → caso de teste, Postgres para vários hosts, MCP | 732 | `observability.py`, `analytics.py`, `candidates.py`, `store_pg.py`, `mcp_server.py` | réplicas só no mesmo host (SQLite); sem MCP nem analytics (o log JSON com custo fica em observability.py) |

Para outro time manter com menos código, a ordem de corte é a de baixo para cima da tabela: operação e escala, ações com risco, fila humana avançada e chaves rotacionáveis saem sem tocar no caminho de uma mensagem (`src/app/pipeline.py`). O humano no laço é bônus do enunciado, mas é o que mais pesa na supervisão humana.
