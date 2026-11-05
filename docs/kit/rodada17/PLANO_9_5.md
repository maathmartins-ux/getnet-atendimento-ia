# Plano para 9,5+ no avaliador real (rodada 17)

Ordem do dono (05/11): ir atrás de 9,5+ independente do custo. Pela diretriz do mesmo dia, a rota sai só do feedback
real (v6 revisado, 9,1) e da régua dele; nossas réguas cegas medem entre rodadas (8,72 na nossa = 9,1 real).

## A meta, critério por critério

9,5 pede ganhar 0,4 dos 0,9 ponto que ainda se perdem. O avaliador diz o que separa 9,1 de 9,5: "a estabilidade dos
oficiais e a validação do juiz"; a faixa 9,5–10 é "desenho de referência completo e evidência de respostas boas nos
cenários". Alvo (ponderada 9,52):

| Critério | Peso | v6 | Alvo | O que o avaliador precisa ver (desconto dele → prova nossa) |
|---|---:|---:|---:|---|
| Orchestration | 15% | 9,0 | 9,5 | "sem ganho do replanejamento fora dos casos escritos para ele" → ablação com × sem `needs` no held-out escrito por pessoas e nas reais, só nos casos em que a tool achou algo, com o ganho medido |
| Evaluation | 14% | 9,0 | 9,6 | "juiz não validado", "plantados não detectados", "mesma família" → juiz validado pela regra (≥ 10 negativos humanos, ≥ 3 reais, TPR e TNR ≥ 0,8), adulteradas pegas pelas pessoas, 2º juiz de outra família concordando |
| Security | 13% | 9,1 | 9,5 | "token de operador compartilhado e /metrics sem token no dev" → já corrigido (chave pessoal, token no /metrics); nada mais escrito |
| RAG | 10% | 9,0 | 9,5 | "gold escrito pelo time; limiares calibrados no mesmo gold" → gold de teste independente (link das perguntas reais e do held-out humano), limiar calibrado num gold e reportado no outro |
| Business | 8% | 9,0 | 9,5 | "official-04 falha 3/3, outro parcial"; "held-out escrito por IA" → oficiais resolvidas com o juiz ≥ 90% em todas as rodadas; held-out escrito por pessoas |
| Tools | 10% | 9,4 | 9,5 | sem desconto escrito → não mexer, não regredir |
| Memory | 8% | 9,2 | 9,6 | "perfil guarda fatos extraídos por código, não preferências em texto livre" → preferência dita em texto livre, extraída e datada, só para o dono, medida ao vivo entre conversas |
| HITL | 7% | 9,4 | 9,7 | "operador do eval simulado"; João é superior em "canal humano operacional" → casos com o dono como operador de verdade, pelo canal real, gravados |
| Observability | 6% | 9,0 | 9,4 | "p95 ~28 s; custo pela tabela de preços" → p95 ≤ 15 s medido; custo conferido com o uso do provedor |
| Production | 5% | 9,1 | 9,5 | "Docker não rodou no ambiente de construção"; "não acessou o Actions" → imagem construída e subida com prova commitada; resumo da CI do commit do gate commitado |
| Judgment | 4% | 9,0 | 9,3 | "complexidade desproporcional" → cortar o que o ESSENCIAL marca como opcional e sem efeito medido, sem perder o que pontua |

## O que só o dono pode dar (pré-requisito)

1. **Chave de um provedor de outra família** (OpenAI, Google ou outro) como segredo do ambiente, para o 2º juiz
   (`JUDGE_PROVIDER=openai_compat`). Sem ela o "mesma família" não sai.
2. **Teto de API ~US$ 120** (estimativa abaixo).
3. **Tempo das pessoas:**
   - held-out humano: o dono e a Bianca escrevem 15 perguntas cada, sem ver código nem casos (~40 min cada, antes do relógio, lacrado com sha);
   - rotulagem com atenção: 2 páginas (ensaio e produção), ~36 itens, ≥ 15 s por item (~12 min por pessoa por página); um 3º rotulador ajuda a chegar aos 10 negativos;
   - operador de verdade: o dono responde 3–4 casos pelo canal do operador durante a bateria do split `hitl` (~15 min).

## Frentes do kit (antes de qualquer ensaio), na ordem dos pontos

| Frente | Ataca | Dona | Prova que fecha |
|---|---|---|---|
| F1 Ausência falsa | Business, Evaluation (official-04, memory-04/11) | A | frase "a fonte não diz X" com X num trecho citado é conferida no código e reescrita; official-04 3/3 resolvida com o juiz |
| F2 Juiz validado | Evaluation | B | 2º juiz de outra família; página com 10 adulteradas, 6 suspeitas, treino com 2 exemplos corrigidos na abertura; relatório da regra |
| F3 Ganho do replanejamento fora dos casos escritos | Orchestration | A | ablação no held-out humano e nas reais, recortada nos casos com achado da tool |
| F4 Gold independente | RAG | B | gold de teste das reais e do held-out humano (pelo link); calibra no do time, reporta nos dois |
| F5 Preferência em texto livre | Memory | A | extração de preferência datada, só para o dono; caso entre conversas ao vivo |
| F6 Operador de verdade | HITL | B | transcrição do caso com o dono como operador, no `docs/DEMO.md` |
| F7 Latência | Observability | A | p50/p95 por split antes × depois, sem perder resolvidas |
| F8 Prova de produção | Production | B | imagem construída e subida no ambiente com o log commitado; resumo da CI do gate commitado |
| F9 Corte de complexidade | Judgment | A, com revisão da B | linhas antes × depois no ESSENCIAL, suíte e bateria iguais |

Cada frente: teste focado → rescore do gravado → split afetado ao vivo (repeat 1) → próxima. Bateria integral só no
fim do lote.

## Portões (nada passa sem os dois)

1. **Checklist do avaliador, medido** (o "Caminho para 9,5" dele, objetivo):
   - oficiais resolvidas com o juiz, pass^k ≥ 0,90;
   - juiz validado pela regra;
   - pessoas pegam ≥ 80% das adulteradas;
   - 2º juiz concorda (κ ≥ 0,6);
   - Recall@3 ≥ 0,85 no gold independente;
   - memória ≥ 90%;
   - p95 ≤ 15 s.
2. **Nossa régua** (média de 2) ≥ 9,1 no ensaio e no cronometrado (≈ 9,5 real pela calibração da rodada 15).

## Sequência

1. Hoje: pré-requisitos do dono; frentes F1–F9 no kit (A e B entrelaçadas, uma dona por arquivo).
2. Ensaio completo sem relógio: domínio montado, bateria integral, juiz das 2 famílias, rotulagem pelas pessoas,
   operador de verdade, régua ×2. Se um portão falhar: corrigir só o que falhou e medir só o split afetado.
3. Ensaio cronometrado de 60 min com o mesmo kit → portões.
4. Produção (60 min) → régua ×2 no commit entregue → envio.

## Custo estimado (API)

| Passo | US$ |
|---|---:|
| loops curtos das frentes | ~20 |
| ensaio: bateria integral + juízes (2 famílias) | ~25 |
| 2ª bateria do ensaio, se um portão falhar | ~20 |
| cronometrado | ~25 |
| produção | ~25 |
| **total** | **~115** |

## Riscos que o plano não controla

- **Rotulagem:** o juiz só valida se as pessoas pegarem as adulteradas.
- **Ressalva de processo:** a "sétima iteração" pesa para a banca, não na nota.
- **Benchmark:** o João continua superior em simplicidade e originalidade.
- **Estimativa:** o alvo por critério é estimativa nossa; a calibração real só vem no próximo feedback.

## Estado em 05/11, 09h00 (kit v5.9.1, ramo r16/candidato)

| Frente | Estado | Prova |
|---|---|---|
| F1 ausência falsa | feita (B) | oficiais com o juiz 0,87 → 0,90; pass^k 0,80 → 0,90 (official + memory ao vivo) |
| F2 juiz validado | código pronto; medida no ensaio | rotulagem número a número, 10 adulteradas; juiz OpenAI (--out, judge_agree) |
| F3 ganho do replanejamento | código pronto; medida no ensaio | ablação no held-out, só nos casos com achado |
| F4 gold independente | código pronto; medida no ensaio | evals.retrieval_cross (juiz OpenAI marca relevância) |
| F5 preferência em texto livre | feita | tests/test_r17_preferencias.py |
| F6 operador de verdade | código pronto (B); medida no ensaio | scripts/hitl_humano.py → docs/HITL_HUMANO.md; roteiro 3b |
| F7 latência | parte feita (17b) | latency_solo.json; portão sem fonte para no 1º trecho que passa (busca −32% no gold, portão igual em 197/197); pensamento desligado medido e rejeitado (claims marcou 36 frases × 1) |
| F8 prova de produção | feita | docker_proof.sh verde aqui (build, sem rede, 2 réplicas); ci_summary.py |
| F9 complexidade | parte feita | −610 linhas de flags/atalhos, comentários limpos, −995 linhas e −56 testes na entrega |
| Held-out humano | página publicada | perguntas de lojista: dono e Bianca, antes do relógio |
| Rotulagem fora do relógio | decidida pelo dono | roteiro passo 3 |

Não feito, de propósito: saída estruturada do redator no lugar das regex (−550 linhas estimadas). Pesa em Judgment (4%,
≈0,02 da nota) e muda o pedido ao LLM de quase todos os splits; o prompt menor da B já levou as oficiais a 0,90. Fica
para depois da produção, com bateria inteira.
