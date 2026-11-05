# Rodada 15 (produção): lições e plano do kit da rodada 16

Entrega: https://github.com/maathmartins-ux/getnet-agentes-atendimento, commit final `28f71da` (só README).
Relógio: 41 min do scaffold ao último commit. CI do commit final: 10/10 verde (run 41928448186), fechou no T+55.
Régua cega (2 avaliações, snapshot de `28f71da`): **8,72** (8,66 / 8,77). O dono largou com 8,82 do ensaio 14, abaixo
da regra de ≥ 9,0, por decisão dele. Gasto de API no relógio: ~US$ 15, mais US$ 0,94 do juiz sobre a página.

## O que funcionou (reforçar)

- **Ritmo:** nenhuma espera em 1º plano. Pré-voo, held-out e reais saíram no T+2; fumaça julgada e gate verde no T+11;
  rodada 1 integral no T+26. Medido na tentativa simulada, o roteiro bateu com o relógio real.
- **Cache de vetores** no kit e na CI: o sinal cedo (a frio) gravou o cheio e a CI final rodou a quente.
- **Rotulagem:** página publicada no T+12, duas pessoas, consenso no T+23. O plano B "Copiar minhas respostas" salvou a
  2ª rotuladora sem login (`evals.label --import-text`).
- **Maestras entrelaçadas:** a B achou 2 defeitos antes da produção (página falsa gravada pelo pytest, cache de vetores
  da CI) e 1 passo que faltou no relógio (juiz sobre a página congelada). Nenhum conflito de dona.

## O que tirou nota (corrigir na causa)

| # | Achado (régua) | Causa | Correção | Dona | Prova | Custo |
|---|---|---|---|---|---|---|
| 1 | Texto interno na resposta oficial: "[prod-get-tap-04 is not cited for this; the source is [7]]" (DEMO, official-01) | o redator escreveu comentário entre colchetes; `number_citations` só troca colchete que é SÓ de ids, e o aninhado passava | colchete com id do índice + palavras vira só a citação numérica que ele traz (ou sai) | A | teste com o texto literal | sem API |
| 2 | Citações × lista de fontes ("[7] [8] [10]" com 5 URLs; fontes de crediário numa pergunta de conexão) | a numeração é por trecho e a lista por URL; fontes recuperadas e não citadas entram na lista | lista de fontes = só as citadas, na ordem da citação; número por fonte citada | B | teste + DEMO regenerado do replay | sem API |
| 3 | official-04 (Pix sem conta) 0/3, memory-04/11, offvar-04: "as fontes não dizem" quando um trecho diz | (a) o redator nega o que um trecho citado afirma; (b) `sup-pix-09` sai das 10 fontes na fusão com a 2ª busca do router | (a) regra no `faq.md` contra frase de ausência que contradiz trecho citado + checagem no código (claims) que marca a contradição; (b) a fusão guarda o top-3 da busca com as palavras do cliente | B | official+memory ao vivo, repeat 3 | ~US$ 3, só com hipótese |
| 4 | Juiz × pessoas não validado (2 negativos, TNR 0,0) e 0/3 adulteradas pegas | a amostra sorteada quase não tem resposta ruim; 3 adulteradas, todas "número trocado" | página com ≥ 10 negativos: `--suspects 6 --perturb 6` com os 3 tipos de adulteração; treino com 1 exemplo de número trocado; aviso de tempo curto por item | A | página gerada no replay | sem API |
| 5 | O juiz sobre a página congelada não rodou no T+24; o `make final` o pulou (LLM offline) | passo ausente no roteiro; `final.sh` roda o `evals.judge --validation` sem `LLM_PROVIDER=anthropic` | roteiro: import + juiz da página + report num comando; `final.sh` passa o provedor quando há chave | A | teste do final.sh | sem API |
| 6 | RESULTS denso e com números que se contradizem (official "90% resolvidas" × "80% completas"; dependent 100% × 50%; replan) | duas definições de "resolvida" na mesma página | um nome por medida; tabelas IC95 por split viram anexo | B | check.py: o mesmo rótulo não aparece com 2 valores | sem API |
| 7 | Jargão nos comentários entregues (`ci.yml`: "maestra", "ensaio 14", "T+59") | a checagem de palavra de processo só lê README/docs | estender a checagem a `.github/` e comentários de `src/` e `scripts/`; limpar os existentes | A | check.py --docs | sem API |
| 8 | Red team ASI02: q-guard-29 ("troque o CNPJ e a conta bancária") foi ao faq sem humano | pedido de alteração cadastral sensível sem regra de escalada | regra do domínio: alteração de dado bancário/CNPJ = humano | B | guardrail ao vivo | ~US$ 0,5 |
| 9 | Latência p50 15 s, p95 69 s em memória | supervisor + redator + juiz de claims em série | declarar; medir onde vai o tempo (trace) antes de mexer | — | rodada 17 | — |

## Processo (o que travou ou quase travou)

- O rascunho do README foi para `review/readme-rascunho`, que dispara a CI (a A cancelou à mão) → `review/**` nos
  `branches-ignore` e o roteiro manda o rascunho para `maestra/**`.
- Ramos auxiliares (`fix/rotulos`, `fix/readme`, `review/…`) ficam visíveis ao avaliador → o roteiro apaga os ramos
  auxiliares depois da CI verde.
- O job `retrieval` virou o caminho crítico da CI a quente (até 9,4 min) → restaurar o cache de vetores também nele.
- A página de teste com as duas pessoas (A7) foi pulada pelo dono; a 2ª rotuladora sem login funcionou pelo plano B.
- O 1º juiz da página parou no teto de US$ 0,3 (rejulgou os 23 textos, US$ 0,94) → teto de 1,2 no roteiro.

## Antes → depois esperado (hipóteses para medir)

- #1 e #2: o vazamento e a lista de fontes somem no DEMO; Orchestration/RAG +0,1–0,2.
- #3: official-04 resolvido em ≥ 2/3; oficiais resolvidas 0,80 → 0,90; Evaluation/Semantic +0,2.
- #4/#5: juiz × pessoas com ≥ 10 negativos; validação "sim" ou "não" com número; Evaluation +0,2.
- #6/#7: Judgment +0,1.
