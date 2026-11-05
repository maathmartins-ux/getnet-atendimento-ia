# Modos de falha (eval ao vivo)

Gerado por `python -m evals.failure_modes` a partir de `evals/results/live_*.json`. Cada falha conta uma vez, pela primeira checagem que falhou. Para cada modo: o que fazer é decisão humana; o que foi feito fica no commit que cita o modo.

Fora da conta: `heldout` (111 execuções), o conjunto cego: ler as falhas dele para corrigir o motor o contamina. A medida dele fica nos blocos ao vivo, do juiz e humano de `docs/RESULTS.md`.

12 falhas em 210 execuções (5.7%).

| modo | falhas | casos distintos | splits |
|---|---:|---:|---|
| `facts` | 4 | 2 | official (3), parallel (1) |
| `replanned` | 4 | 4 | replan (4) |
| `memory` | 1 | 1 | memory (1) |
| `claims` | 1 | 1 | official (1) |
| `handoff` | 1 | 1 | replan (1) |
| `intent` | 1 | 1 | replan (1) |

## `facts`

Casos que mais falham: `official-04` (3x), `parallel-04` (1x)

- exemplo `official-04`: “Do I need a bank account to receive my sales via Pix?”
- esperado: intent `knowledge`; obtido: `knowledge`; rota ['router', 'faq']; ferramentas []
- números sem base: nenhum
- resposta: Yes. To enable Pix at Getnet, you need a Santander bank domicile (the account where you receive your sales) and an active Pix key [1]. The other eligibility criteria are: - A compatible capture method: terminal, TEF or e-commerce. - A registration with an ind…

## `replanned`

Casos que mais falham: `replan-12` (1x), `replan-13` (1x), `replan-18` (1x), `replan-20` (1x)

- exemplo `replan-12`: “My terminal has no signal, how do I fix it?”
- esperado: intent `troubleshoot`; obtido: `troubleshoot`; rota ['router', 'records', 'faq']; ferramentas ['get_terminals']
- números sem base: nenhum
- resposta: Your terminal T1988B (Get Clássica) is offline on its chip with no signal. It was last in contact on 05/11/2026 at 07:26 and has been offline for 5 hours. T1988A is online with good signal. Try these steps for T1988B: - **Check the chip** [1]: Turn the termin…

## `memory`

Casos que mais falham: `memory-16` (1x)

- exemplo `memory-16`: “Remind me which installment limit we talked about last time?”
- esperado: intent `knowledge`; obtido: `knowledge`; rota ['router', 'faq']; ferramentas []
- números sem base: nenhum
- resposta: - Each card issuer sets its own installment limit under its credit policies [1]. Interest rates can also vary by issuer [2]. - Before the sale, you can check the interest by running a simulation on the card machine (credit > crediário). The simulation is for …

## `claims`

Casos que mais falham: `official-01` (1x)

- exemplo `official-01`: “What's the difference between the Get Clássica and the Get Smart?”
- esperado: intent `knowledge`; obtido: `knowledge`; rota ['router', 'faq']; ferramentas []
- números sem base: nenhum
- resposta: The Get Smart is an Android smart card machine. The sources I found describe the Get Clássica mainly by its plan terms, not by features. **Get Smart** - You can control stock, place orders, close tabs, load a menu and issue invoices on the device [1]. - It ca…

## `handoff`

Casos que mais falham: `replan-07` (1x)

- exemplo `replan-07`: “Qual o telefone do gerente regional da Getnet em Manaus?”
- esperado: intent `knowledge`; obtido: `knowledge`; rota ['router', 'faq']; ferramentas []
- números sem base: nenhum
- resposta: Você pode ligar para a Central de Relacionamento Getnet: 4002-4000 ou 4003-4000 (capitais e regiões metropolitanas) e 0800-648-8000 (demais localidades) [1][2]. Não encontrei nas fontes o telefone de um gerente regional em Manaus. Para clientes atacado, uma f…

## `intent`

Casos que mais falham: `replan-08` (1x)

- exemplo `replan-08`: “What is the name of the Getnet regional manager in Recife?”
- esperado: intent `knowledge`; obtido: `blocked`; rota ['guardrails']; ferramentas []
- números sem base: nenhum
- resposta: I can't help with that request. I can help with product or account questions.
