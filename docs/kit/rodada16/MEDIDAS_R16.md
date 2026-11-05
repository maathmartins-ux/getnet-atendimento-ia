# Rodada 16 — correções do feedback v6 aplicadas e medidas (kit v5.8.0)

Sem produção nesta rodada (ordem do dono: aplicar e medir, teto de US$ 10 na API, depois parar). Medido numa tentativa
montada do `r16/candidato` (domínio da rodada 15, provedor real, `--live`). Antes = bateria 1 (r16/candidato com as
entregas da B, antes do contrato de resposta); depois = remedida com o contrato (4ef3cda).

## Antes → depois (ao vivo)

| Medida | Rodada 15 (produção) | Bateria 1 | Com o contrato | O que mudou |
|---|---|---|---|---|
| Oficiais: checagens passando (pass^k, x3) | 0,70 | 0,90 | **1,00** (30/30) | official-04 deixou de falhar a checagem |
| Oficiais resolvidas (sem parcial, x3) | — | 0,80 | **0,87** | official-05 0/3 → 2/3 completa |
| official-04 | falha 3/3 | parcial | parcial 3/3 | falta honesta: a fonte não diz se banco fora do Santander recebe Pix |
| Dependentes parciais | — | 60% | **20%** | o item vizinho que ninguém pediu não deixa parcial |
| Dependentes resolvidas | — | 40% | **80%** | idem |
| Juiz (rodada 0) | — | oficiais 9/10, memória 14/16 | — | não re-rodado (texto das oficiais mudou pouco) |
| Guardrail: intenção | 96,9% | 100% | — | |
| Guardrail: handoff certo | — | 33% (1/3) | **100%** (3/3), com `must_escalate` | pedido sem tool só OFERECIA atendente |
| Guardrail: seguras (red team) | — | 100% de 32 | 100% de 32 | intenção 100% nas duas |
| Ablação do `needs` no split dependent | — | completed 100% × 60% | — | o replanejamento ganha onde a tool acha algo |
| Juiz NLI local (2º juiz sem LLM) | — | κ −0,011 em 78 | — | descartado pela regra combinada antes |

Ruído: dependent-10 errou intenção/rota no router uma vez (antes do especialista; o contrato não age ali). Na bateria 1
o mesmo caso passou.

## Escalada de pedido sem ferramenta

Achado: "troque o CNPJ e a conta bancária" e "pague o boleto do fornecedor" saíam com a recusa certa e só a oferta de
atendente; o supervisor LLM às vezes nem chamava especialista. Correção na raiz, no código: `pipeline.must_escalate`
lê o hook opcional do domínio `must_escalate(text)`; com motivo, abre o caso e tira a oferta do texto
(`tests/test_r16_must_escalate.py`). A parte do domínio, da Maestra B (`flow.py`, 13da113): `must_escalate` devolve
`account_change` ou `unsupported_action` (pagar boleto); pergunta de como se faz, chamado e antecipação com valor não
escalam (`docs/kit/dominio/files/tests/test_domain_must_escalate.py`). Ao vivo, montado do 7bff148: handoff 3/3,
a oferta saiu do texto e o protocolo entrou.

Achado da B no mesmo commit: o `dominio.py mount` só copia o que o `MANIFEST.json` lista, e três testes do domínio
estavam fora dele (nunca rodariam na tentativa). Entraram, e `tests/test_dominio_montado.py` reprova o próximo.

## Gasto

Bateria 1 US$ 4,59; remedida US$ 1,19; guardrail US$ 0,15; ablação e experimentos ~US$ 0,7. Total ~US$ 6,6 de
US$ 10.

## Régua cega (2 avaliações, média)

Avaliada a cópia `grade_snap16`: a entrega da rodada 15 com o código do kit v5.8.0 por cima, os splits official,
memory, dependent e guardrail e o juiz regravados no código novo (os outros 9 splits e a DEMO ficaram da rodada 15).

| Critério | Rodada 15 (8,66 / 8,77) | Rodada 16 (8,86 / 8,78) |
|---|---|---|
| Ponderada | 8,72 | **8,82** |
| Orchestration | 8,8 / 9,0 | 9,0 / 9,0 |
| Evaluation | 8,3 / 8,3 | 8,5 / 8,4 |
| Security | 9,0 / 8,9 | 9,0 / 9,0 |
| RAG | 8,5 / 8,7 | 8,6 / 8,4 |
| HITL | 8,8 / 9,0 | 9,1 / 9,0 |

Pela calibração da rodada 15 (8,72 na régua = 9,1 real), 8,82 ≈ 9,2 real. Abaixo da meta de 9,0 na régua.

O que segurou, nas duas réguas: juiz não validado contra pessoas (TNR 0,0 em 2 negativos, mesma família) e
adulteradas que os rotuladores não pegaram; official-04 parcial 3/3, que o juiz chama de falsa ausência (o critério do
domicílio Santander responde a pergunta); latência p50 ~15 s; RESULTS denso; muita decisão por regex no código.
Artefatos da cópia (somem numa produção com o kit): DEMO velha com o texto interno que vazou, evidência de commits
misturados e de árvore suja, gravação depois do relógio.

Próximo, do maior peso: official-04 (falsa ausência: o redator diz que a fonte não cobre o que o trecho do domicílio
cobre); validação do juiz com mais negativos humanos (a página já planta 8 adulteradas e 4 suspeitas); latência.
