# Ablação do achado `needs` no código entregue na rodada 15 (28f71da), 04/11/2026

Braço sem `needs` medido ao vivo depois da entrega (repeat 1, workers 8; exceção do gate declarada, cópia sem git),
contra o braço com `needs` gravado na rodada 1 da entrega (mesmo código).

| Split | Medida | Com `needs` | Sem `needs` | Custo do braço |
|---|---|---:|---:|---:|
| dependent (10 casos: a tool acha algo que pede outro passo) | passo dependente concluído | **100%** | **60%** | US$ 0,40 |
| official (10 casos) | intent / tools / fatos / handoff | 100 / 100 / 90 / 100 | 100 / 100 / 90 / 100 | US$ 0,28 |
| real (40 perguntas, rodada 15) | resolvidas | 100% | 100% | US$ 1,21 |

Leitura: o achado só muda o resultado quando a tool encontra algo (terminal offline, venda recusada) que exige um 2º
passo; nas perguntas reais quase nenhuma dispara achado, por isso a ablação nelas não discrimina. O roteiro da rodada
16 roda a ablação no split `dependent`.
