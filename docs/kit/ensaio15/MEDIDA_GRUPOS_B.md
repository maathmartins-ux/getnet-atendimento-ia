# Reprovações da fumaça do ensaio geral final: causa, correção e medida (Maestra B, rodada 15)

Base: getnet-ensaio-geral-3@66851ec, a fumaça julgada (official + memory, 1 rodada). Tinha 22/26 na regra e 23/26 no
juiz. Cada correção mexe só no domínio montado (`docs/kit/dominio/files/`) ou no juiz do kit, com teste.
Scripts das medidas: `route_probe.py` (só o router), `live_subset.py` (ao vivo com um subconjunto de casos e o juiz
reaproveitando a confiança) e `compare_live.py` (antes × depois, caso a caso).

## O que entrou

| grupo | causa | correção | teste |
|---|---|---|---|
| memory-13, memory-14 (rota) | a reescrita do seguimento perdia o histórico ("code 51" sem a recusa, "do débito" sem o "de ontem") | `router.md`: o seguimento traz de volta o dia e o problema; um código de recusa é troubleshoot, e "por que a venda X foi recusada" continua support; "quando cai o dinheiro das vendas de ontem" é support | `test_router_prompt_follow_up_keeps_the_day_and_the_problem` |
| memory-06 (stale_source) | `get_terminals` calculava o último contato com o relógio de cada chamada: 10:45 no 1º turno, 10:46 no 2º, e a resposta trocou consulta por memória | `contact_anchor()`: hora de referência fixa por até 1 h | `test_last_contact_is_stable_within_a_conversation` |
| memory-03 (recursos) | "como é a Get Clássica?" respondido com preço; o recurso só estava no título da página ("POS 3G + Wi-Fi") | `faq.md`: pergunta sobre aparelho responde primeiro o que ele é e faz; o título do trecho também é fonte | `test_faq_prompt_device_features_title_as_source_and_no_borrowed_features` |
| official-01 (unsupported_claim) | recurso da página de TEF atribuído à Get Smart; "máquina básica" sem fonte | `faq.md`: recurso de outra solução não é do produto perguntado; nenhum adjetivo de juízo sem trecho | o mesmo |
| juiz (custo) | 1 item de calibração recusado (q-cal-44, 45 de 46) desligava o reaproveitamento de canários e calibração: cada split pagaria ~US$ 0,5 de novo | o item recusado conta como tratado e segue declarado | `test_resume_reuses_trust_even_with_a_refused_calibration_item` |

## Medida

Router só, ao vivo (official + memory, 3 rodadas): 72/78 → **78/78**. No controle dos outros 8 splits gated (2
rodadas): 151 → 154/206, e só 2 casos mudaram, os dois para melhor. Detalhe em `MEDIDA_ROUTER_SEGUIMENTO.md`.

Alvo (4 casos × 3, com juiz): memory-06 passou no juiz 3/3 (antes 0/1). official-01 passou 2/2 dos julgados. memory-03
ainda reprovava (preço primeiro e "não achei a conexão"), e isso levou à regra do título.

Regressão obrigatória, official + memory inteiros, 1 rodada com juiz, todos os prompts finais. A comparação é com a
fumaça do ensaio (mesmos casos e o mesmo código, fora as mudanças acima):

| | regra | juiz |
|---|---:|---:|
| fumaça do ensaio geral | 22/26 | 23/26 |
| com as correções | **25/26** | **26/26** |

Melhoraram memory-03, memory-06, memory-13, memory-14 e official-01. **Nenhum caso piorou.** Sobra o official-04, que
reprova no fato (abaixo); o juiz agora aprova a resposta dele.

Gasto desta frente: US$ 3,38 (router US$ 0,10, alvo US$ 1,34, regressão US$ 1,94). O alvo pagou canários e
calibração por causa do defeito do juiz acima. A verba aprovada era de US$ 3,5.

Limite da medida: a regressão é de 1 rodada (ruído de uma resposta pode virar um caso para qualquer lado).

official-var A/B ao vivo (20 casos, 1 rodada; braço A = faq.md de 4e633ba, braço B = faq.md de eb92531, o resto
igual; verba extra de US$ 1,5, gasto US$ 1,44):

| | regra | juiz |
|---|---:|---:|
| A (faq.md antigo) | 18/20 | — (não julgado: verba) |
| B (faq.md novo) | 18/20 | 16/16 julgados (os 4 últimos sem juiz, verba) |

Caso a caso, a regra é igual nos dois braços: só q-offvar-04-pt/en reprovam, a variante do official-04, pela mesma
falta de busca. Nenhum caso piorou, e o faq.md fica.

## O que não entrou (declarado para a rodada 16)

- **official-04, o fato do requisito (chave Pix / domicílio):** o único trecho que o traz (`sup-pix-09`) não entra no
  top-k.
  - Offline, uma 2ª busca "requisitos para habilitar o Pix" o põe em 3º. "Requisitos para receber vendas com Pix" e
    "o que é preciso para receber Pix" não o trazem.
  - Com a regra no router, o Haiku escreveu "receber" em 5 de 6 consultas. A regra seria frágil e quase sob medida:
    revertida.
  - Caminhos já medidos e descartados: `MEDIDA_BUSCA_PIX.md` e `MEDIDA_PIX_CTX.md`.
