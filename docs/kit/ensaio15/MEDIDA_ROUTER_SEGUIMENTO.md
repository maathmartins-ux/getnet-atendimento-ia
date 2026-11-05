# Rota do seguimento: memory-13 e memory-14 (ensaio geral final, rodada 15)

## Causa (lida nas respostas gravadas do router, `evals/cassettes/memory.jsonl` do getnet-ensaio-geral-3@66851ec)

O router reescreve o seguimento numa pergunta autônoma (`standalone`) e classifica essa pergunta. No seguimento curto, a
reescrita perdia o que o histórico dizia, e a intenção mudava junto:

| caso | turno anterior | seguimento | standalone gravado | intenção (esperada) |
|---|---|---|---|---|
| memory-13 | My card machine shows a decline error | What does code 51 mean? | "What does code 51 mean?" | knowledge (troubleshoot) |
| memory-14 | Quanto vendi ontem? | E quando cai o dinheiro do débito? | "Quando cai o dinheiro das vendas no débito?" | knowledge (support) |

As respostas dos dois passaram no juiz; a reprovação era só de rota (intenção do memory ao vivo 87,5%, abaixo dos 90%).

## Mudança (só `src/app/domain/challenge_prompts/router.md` do domínio montado)

1. Reescrita: o seguimento curto traz de volta o dia ou o período das vendas e o problema em curso (exemplos
   genéricos, sem frase de caso de avaliação).
2. troubleshoot: o que significa um código de recusa ou de erro da máquina/venda; "por que a venda X foi recusada?"
   continua support (dado de uma transação).
3. support: quando cai o dinheiro de vendas de um dia ou período do cliente; sem dia nem venda, o prazo em geral
   continua knowledge.

## Medida (router só, ao vivo, Haiku; `docs/kit/ensaio15/route_probe.py`; histórico tirado do cassete)

| conjunto | antes | depois |
|---|---:|---:|
| official + memory, 3 rodadas | 72/78 | **78/78** |
| memory-13 | 0/3 | 3/3 |
| memory-14 | 0/3 | 3/3 |
| official-var, replan, dependent, parallel, approval, hitl, partial, guardrail (2 rodadas; histórico só do cliente nos dois braços) | 151/206 | 154/206 |

Nos 8 splits do controle, só mudaram 2 casos, os dois para melhor: q-offvar-03-en (0/2 → 2/2) e q-offvar-03-pt (1/2 →
2/2), a mesma pergunta "quando cai o dinheiro das vendas de ontem". O guardrail tem a mesma contagem baixa nos dois
braços: lá a "intenção esperada" é a do bloqueio, que vem depois do router. Held-out e perguntas reais ficaram fora da
medida porque são cegos.

Variante intermediária, medida e descartada: só a regra 2 sem a ressalva do "por que a venda X foi recusada?" fez o
memory-09 virar troubleshoot em 1 de 3 rodadas. Com a ressalva, 3/3 support.

Custo de toda a medida: US$ 0,10 (cerca de 700 chamadas do router a ~US$ 0,0001). Suíte da tentativa com a mudança:
tudo verde nos testes do domínio e do roteador (contaminação com o held-out novo do ensaio inclusive). Teste novo:
`test_router_prompt_follow_up_keeps_the_day_and_the_problem`.

## Os outros grupos

official-01, memory-03, memory-06 e official-04, com a regressão ao vivo de official + memory: `MEDIDA_GRUPOS_B.md`.
