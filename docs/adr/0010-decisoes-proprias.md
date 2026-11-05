# ADR 0010 — Quais decisões deste desenho são próprias e quais vieram de ideia pública

Status: aceito no kit v5.8.0 (04/11/2026). Complementa a seção "Ideias de soluções públicas" de
[docs/PROCEDENCIA.md](../PROCEDENCIA.md), que lista o que veio de fora. Aqui fica o outro lado: o que o desenho tem
que não veio de nenhuma solução pública lida, o problema que cada decisão resolveu e onde está a medida que a decidiu.
Nenhum número desta entrega é repetido aqui (eles mudam a cada bateria): cada linha aponta para o lugar gerado.

**Contexto.** Uma avaliação perguntou "quais decisões deste desenho são suas, e quais vieram do skywalker e do
nelsondell?". A resposta curta está na tabela; a origem das ideias externas fica na PROCEDENCIA.

## Vieram de ideia pública (implementação e testes próprios)

| Ideia | De onde | Onde está |
|---|---|---|
| Router como único leitor do histórico; especialistas sem estado | skywalker | ADR 0007, `src/app/router.py` |
| Humano consultado de dentro do turno, com espera curta | skywalker | `src/app/hitl_sync.py` |
| Login com senha; 👍/👎 por resposta; README que explica o porquê | skywalker | `src/app/auth.py`, `src/app/candidates.py` |
| Resposta em três estados (completa, parcial, sem fonte) | nelsondell | `src/app/agents.py` (`AgentResult.status`) |
| Demonstrativos na reescrita; placar de busca no caminho do agente | nelsondell | `src/app/followup.py`, `evals/run_evals.py` |
| Regra de validação do juiz fixada antes de medir | nelsondell | `evals/judge.py` (`VALIDATION_MIN_CASES`) |

## Próprias (o problema, a decisão e a prova)

| Problema medido | Decisão | Prova |
|---|---|---|
| O supervisor ignorava o que a tool achava (terminal offline, venda recusada) e respondia só a pergunta | o achado da tool (`needs`) volta ao modelo como informação, nunca como passo imposto; cada passo grava quem decidiu (`decided_by`) | `docs/RESULTS.md` (quem decide cada passo); ablação com e sem `needs` em `evals/results/ablation_replan*.json` |
| Número e frase sem base saíam na resposta, mesmo com a fonte certa recuperada | conferência no código de cada número e de cada frase contra fonte, tool e pergunta: o que não tem base é reescrito, cortado ou escalado | `src/app/grounding.py`, `src/app/claims.py`; juiz "fundamentada" no §0 do README |
| A resposta ficava "parcial" por item que ninguém pediu | parcial decidido no código pelo item pedido na pergunta, não pelo redator | `src/app/coverage.py`; oficiais "só em parte" no §0 |
| O piso de cosseno respondia sem fonte e recusava com fonte, conforme o idioma | portão "sem fonte" pela nota do cross-encoder, calibrado no gold do domínio | bloco de busca do README (§2.2), `data/retriever.json` |
| Ação de escrita sem controle fora do LLM | confirmação do dono; risco alto com aprovação de operador com chave pessoal; limite de valor; execução única entre réplicas | `src/app/actions.py`, `src/app/risk.py` |
| Fato dito em turno ou conversa anterior se perdia | livro de fatos extraído por código + perfil de longo prazo que entra em conversa nova como dado datado, só para o dono | `src/app/memory.py`; memória ao vivo no §0 |
| A CI não podia chamar o LLM e o eval offline não media o produto ao vivo | cassete de cada resposta ao vivo e replay na CI com o piso da gravação aceita | `evals/run_evals.py` (`--replay`), job `check (replay)` |
| Juiz validado só contra rótulos escritos a partir da SPEC | conferência humana cega numa página congelada, com respostas adulteradas de propósito misturadas às reais, e o juiz julgando o mesmo texto que as pessoas leram | `scripts/label_page.py`, `evals/label.py`, `evals/results/human_review.json` |
| Casos de avaliação escritos por quem escreveu o código | held-out escrito por autores cegos (sem ver código nem casos) e teste que reprova exemplo de treino igual a um caso cego | `evals/heldout_blind.jsonl`, `tests/test_router_contamination.py` |

## Consequência

As ideias de fora entraram como ideia, e o código e os testes foram escritos aqui. O que pesa nas medidas desta
entrega, que são a conferência, o achado da tool, o portão por cross-encoder e a avaliação com rotulagem cega, é
próprio. A ordem em que cada parte sairia, para quem precisar de menos código, está em
[docs/ESSENCIAL.md](../ESSENCIAL.md).
