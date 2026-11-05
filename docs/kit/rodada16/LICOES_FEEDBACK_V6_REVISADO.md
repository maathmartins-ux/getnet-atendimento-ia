# O que o feedback v6 revisado ensina aos nossos processos

Fonte: feedback v6 revisado do avaliador real (mesma nota, 9,1; guardado no arquivo privado). O que mudou da 1ª versão:
a adoção declarada de ideias do skywalker e do nelsondell saiu de Engineering Judgment (8,5 → 9,0); a ponderada foi
de 9,08 para 9,10. A cópia declarada fica só como ressalva de processo para a banca.

## 1. Reforçar (o que o avaliador premia e não pode regredir)

| Ponto | Por que segurar | Como já está protegido |
|---|---|---|
| Procedência declarada com origem e autor | foi o que tirou a cópia da nota: "declarado pelo próprio candidato, não é inferência" | `docs/PROCEDENCIA.md` + ADR 0010 (decisões próprias × ideias públicas) |
| Código aprovando cada transição do LLM | descrito como "orchestrator-workers com controle em código, bem documentado" | `ALLOWED`, `MAX_STEPS`, orçamento, `decided_by`; testes do supervisor |
| Humano no laço e plano que continua | "o HITL mais completo do conjunto ao lado do João" (9,4) | split `hitl` ao vivo |
| Método de avaliação | "o mais completo do conjunto" | pass^k, held-out cego, reais com link, adulteradas, ablação |

## 2. Nossa régua cega × a régua real (calibração)

- As 2 réguas da rodada 16 deram Judgment 8,7 e 8,5; o real deu 9,0 sem o desconto da cópia. Uma delas também tratou
  o controle em código (corte de oferta, escalada garantida) como atalho; o real o elogia. A régua
  (`conhecimento/regua_cega.md` no arquivo) ganhou as duas regras: controle em código que APROVA o LLM conta a favor;
  ideia pública atribuída não desconta em critério nenhum.
- A constante da calibração não muda: 8,72 na régua = 9,10 real (+0,38).
- A régua só avalia entrega gerada pelo pipeline inteiro: `demo_md`, `failure_modes`, `fill_readme`, um commit só e
  árvore limpa. Na cópia da rodada 16 (entrega 15 + código novo) as réguas descontaram DEMO velha, commits misturados
  e árvore suja, coisas que uma produção não teria: a nota da cópia subestima o kit.

## 3. A rota: só os descontos do feedback, pelos pontos que cada critério perde

Ordem = peso × (10 − nota real) (diretriz do dono de 05/11, `MELHORIA_CONTINUA.md`). Cada linha cita o desconto do
avaliador; o que não está no feedback não entra. "Caminho para 9,5" do avaliador: oficiais estáveis ≥ 90% e juiz
validado contra humanos são as duas metas que faltaram.

| # | Critério (peso, nota) | Perde | Desconto escrito pelo avaliador | Estado na rodada 16 | Próximo passo |
|---|---|---:|---|---|---|
| 1 | Orchestration (15%, 9,0) | 0,150 | "ablações não mostram ganho do replanejamento fora dos casos escritos para ele" | ablação no `dependent` (casos escritos para ele): 100% × 60% | medir a ablação nas reais e no held-out com achado `needs` (casos que ninguém escreveu para o replanejamento); só mostrar onde a tool acha algo |
| 2 | Evaluation (14%, 9,0) | 0,140 | "validação humana não discrimina", "defeitos plantados não detectados", "juiz da mesma família", "regra de validação própria não atendida" | página com 10 adulteradas, 6 suspeitas e aviso de ritmo | rodar a página nova com as 2 pessoas e medir quantas adulteradas pegam; juiz de outra família pede chave do dono |
| 3 | Security (13%, 9,1) | 0,117 | "no dev, token de operador compartilhado e /metrics sem token" | corrigido pela B (#16: /metrics com token no dev, chave pessoal do operador) | conferir no próximo feedback real |
| 4 | RAG (10%, 9,0) | 0,100 | "gold de busca escrito pelo time; limiares calibrados no mesmo gold" | igual | gold de teste independente: o link das 40 perguntas reais; calibra no gold do time, reporta nos reais |
| 5 | Business (8%, 9,0) | 0,080 | "official-04 falha 3/3, outro parcial"; "held-out escrito por agentes de IA, não por pessoas" | official-04 parcial 3/3 (ausência falsa, segundo o juiz); official-05 2/3 completa | consertar a ausência falsa da official-04; held-out escrito por pessoas (o dono e a Bianca, cegos, antes do relógio) |
| 6 | Memory (8%, 9,2) | 0,064 | "perfil guarda fatos extraídos por código, não preferências em texto livre" | igual | preferência dita em texto livre, extraída e datada, só para o dono |
| 7 | Observability (6%, 9,0) | 0,060 | "p95 ~28 s por turno; custo pela tabela de preços" | igual | latência do turno |
| 8 | Tools (10%, 9,4) | 0,060 | sem desconto escrito | — | nada (não inventar) |
| 9 | Production (5%, 9,1) | 0,045 | "Docker não rodou no ambiente de construção (só na CI)"; "avaliador não acessou o Actions" | igual | commitar o resumo da CI do commit do gate (jobs, duração, link) |
| 10 | HITL (7%, 9,4) | 0,042 | "operador do eval simulado" | igual | um caso com operador humano de verdade (o dono), gravado |
| 11 | Judgment (4%, 9,0) | 0,040 | "complexidade desproporcional (~15 mil linhas, 1.533 testes)" | `docs/ESSENCIAL.md` e código morto cortado | decisão do dono: entregar sem blocos opcionais |

Fora da rota (eram ideias nossas, sem desconto no feedback): nada novo entra sem uma linha acima.

## 4. Perguntas da entrevista com resposta pronta

As 5 perguntas do feedback têm linha na §7 do README do domínio, cada uma com a prova gerada: adulteradas
(`human_review.json`), replanejamento (ablação no `dependent`), o cenário que mais falha (`FAILURE_MODES.md`), o que
cortar (`ESSENCIAL.md`) e autoria (ADR 0010). Linha sem prova sai sozinha (`fill_readme`).
