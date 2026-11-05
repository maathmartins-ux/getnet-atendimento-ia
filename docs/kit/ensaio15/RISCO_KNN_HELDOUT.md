# Risco de colisão: exemplos do k-NN do roteador × held-out cego

Medida sem gasto (Maestra B, 04/11, depois do ensaio geral final). Decisão da rodada 15: **não reescrever** (muda o
k-NN do roteador sem medida ao vivo a ~1 h da produção). A rede que fica: o teste de contaminação logo depois do
commit do held-out, a mensagem com `arquivo:linha` e o remédio (tirar o EXEMPLO, nunca o caso cego). Fica para a
rodada 16 decidir.

## O que aconteceu

- Ensaio 14: um exemplo de `data/intent_examples.d/r.jsonl` colidiu com um held-out cego; reescrito em 123aeda.
- Ensaio geral final (rodada 15): a reescrita, `r.jsonl:3` "Is there a monthly fee for the Get Smart?", saiu
  **idêntica** no caso cego novo heldout-H1-03. O pré-voo reprovou no T+6
  (`test_knn_examples_do_not_copy_heldout`: 5 palavras seguidas em comum = cópia).

## Medida

Maior sequência de palavras em comum (texto normalizado) entre cada um dos 22 exemplos e os 120 textos cegos do r14
(H1 + H2 + perguntas reais, com os turnos anteriores): **todos ≤ 3 palavras**, inclusive o `r.jsonl:3` (só
"is there a" no r14). O histórico não prevê a colisão: o risco é o exemplo ser a forma CANÔNICA da pergunta, a
primeira que um autor cego escreve.

| linha | exemplo | maior trecho em comum no r14 | risco |
|---|---|---|---|
| 1 | Como funciona o aluguel da maquininha? | 3 ("como funciona o") | ALTO |
| 2 | Quais bandeiras de cartão a Get Mini aceita? | 2 | ALTO |
| 3 | Is there a monthly fee for the Get Smart? | 3 ("is there a"); colidiu inteiro no ensaio geral | ALTO |
| 4 | Qual o prazo padrão do crédito à vista? | 2 | ALTO |
| 5 | Can I issue a payment link without a website? | 3 ("a payment link") | ALTO |
| 6 | O Pix da maquininha tem tarifa? | 2 | ALTO |
| 17 | Quero conversar com uma pessoa da equipe | 1 | ALTO |
| 7 | Quanto recebi de vendas no débito nesta semana? | 2 | MÉDIO |
| 10 | List my receivables for the next days | 3 ("for the next") | MÉDIO |
| 12 | The terminal keeps showing a communication failure | 3 ("keeps showing a") | MÉDIO |
| 14 | My POS keeps rebooting by itself | 3 ("my pos keeps") | MÉDIO |
| 15 | Como vai estar o tempo em Recife no sábado? | 1 | MÉDIO |
| 18 | Connect me with someone from support staff | 2 | MÉDIO |
| 8, 9, 11, 13, 16, 19–22 | situação específica ou fraseado incomum | ≤ 2 | BAIXO |

ALTO = pergunta curta e genérica de produto (6–9 palavras), na forma óbvia. MÉDIO = fraseado natural, mas com
detalhe que um autor cego nem sempre escreve. BAIXO = situação composta ou ordem incomum.

## Proposta para a rodada 16 (com medida antes × depois)

Reescrever os de risco ALTO com contexto de lojista e ordem menos óbvia, mantendo a intenção (ex.: `r.jsonl:3` →
"Tenho uma Get Smart: cobra alguma mensalidade?"). Depois: os 35 testes do roteador, o gate offline e o split
`real` ao vivo, antes × depois.
