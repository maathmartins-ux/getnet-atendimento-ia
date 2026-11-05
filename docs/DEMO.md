# Respostas reais — split `official`

Geradas de `evals/results/live_official.json` (provedor `anthropic`, status `complete`, gasto US$ 0.62); respostas medidas no commit `f21ce9f` (2026-11-05T15:33:24Z), página gerada no commit `c03261c` em 05/11/2026 15:44 UTC. Nada aqui foi escrito à mão: é a saída do `POST /chat` com o LLM ligado, 1ª rodada de cada caso.

Estabilidade em 3 rodadas: pass@1 0.8667, pass^3 0.8; instáveis: official-01.

Em cada passo, **decidido por** diz quem pôs o agente no turno: o supervisor LLM (tool call); o plano do router (o router LLM, ou a regra que o substitui: seguimento herdado, guarda da própria empresa, queda do LLM), quando o supervisor LLM não foi consultado (rodado pelo atalho de 1 passo ou pelo motor de tabela); o código, com a regra entre parênteses (`supervisor.CODE_WHY`); ou a operadora que respondeu o caso. "não registrado" = passo gravado sem o campo `decided_by`.

| caso | intenção | rota | ferramentas | handoff | veredito automático |
|---|---|---|---|---|---|
| `official-01` | knowledge | router → faq | — | não | OK |
| `official-02` | general | router → general | weather_forecast | não | OK |
| `official-03` | support | router → records | get_settlements | não | OK |
| `official-04` | knowledge | router → faq | — | não | falhou: facts, resolved |
| `official-05` | troubleshoot | router → records → faq | get_terminals | não | OK |
| `official-06` | knowledge | router → faq | — | não | OK |
| `official-07` | general | router → general | currency_rate | não | OK |
| `official-08` | troubleshoot | router → records → faq | get_transactions, get_terminals | não | OK |
| `official-09` | knowledge | router → faq | — | não | OK |
| `official-10` | knowledge | router → faq | — | não | OK |

## official-01

**Pergunta:** What's the difference between the Get Clássica and the Get Smart?

**Intenção:** knowledge (esperada knowledge) · **rota:** router → faq · **replanos:** nenhum · **caminho:** supervisor LLM (laço de tool use) · **custo:** US$ 0.0462 · **latência:** 26.1 s

**Resposta:**

> The main difference is that the Get Smart is an Android smart terminal with built-in management features. The sources describe the Get Clássica only as a 3G + Wi-Fi POS with a single rate across the main card brands.
>
> **Get Smart**
> - You can control stock, place orders, close tabs, load a menu and issue invoices on the device [1].
> - Because it runs Android, it also supports menus and messages between kitchen and floor. Getnet processes all sales on it [1].
> - It can replace a computer and a fiscal printer at the counter [1].
> - Whether it prints the NF-e depends on the app. Most apps on it issue NF-e, but check with the app [1].
> - Getnet charges rental and administrative fees. The app developers charge the app subscriptions [1].
>
> **Get Clássica** (2025 page) [2]
> - The page lists a free machine*, a free account and card, receipt in 2 days, and a single rate across the main brands. It is valid for CPF and CNPJ.
> - The free machine depends on sales of R$10,000 or more.
> - Rates listed: debit 1,69%, credit 1x 3,79%, 2x 7,98%, 3x 8,47%, 4x 8,96% and 5x 9,45%.
>
> **Free machine by monthly sales**
> - 2025 page: R$10 thousand per month gets a Get Mini or Get Clássica. R$60 thousand per month gets a Get Mini, Get Clássica or Get Smart [2].
> - 2026 page: above R$20 thousand gets a Get Clássica. Above R$40 thousand gets a Get Clássica or Get Smart. The same choice is listed above R$80 thousand [3].
>
> The sources don't list Get Smart rates, so I can't compare rates between the two. I can pass your question to a human agent if you'd like.

**Passos:**

1. **faq** · ok · 14579 ms · decidido por: supervisor LLM (tool call)

**Fontes citadas:** [1] <https://site.getnet.com.br/duvidas/get-smart/>; [2] <https://site.getnet.com.br/maquininha/get-classica/>; [3] <https://site.getnet.com.br/todas-as-maquininhas/>
**Checagens:** 9/9 passam · **desfecho:** completa

## official-02

**Pergunta:** What's the weather forecast in Porto Alegre tomorrow?

**Intenção:** general (esperada general) · **rota:** router → general · **replanos:** nenhum · **caminho:** supervisor LLM (laço de tool use) · **custo:** US$ 0.0132 · **latência:** 7.3 s

**Resposta:**

> Tomorrow (2026-11-06) in Porto Alegre, wttr.in forecasts a low of 16 °C, a high of 27 °C, and a chance of rain of up to 10%. Source: https://wttr.in/

**Passos:**

1. **general** · ok · 3759 ms · decidido por: supervisor LLM (tool call)
   - `weather_forecast` {"city": "Porto Alegre", "day": "amanhã"} → ok

**Dados ao vivo de:** <https://wttr.in/>
**Checagens:** 10/10 passam · **desfecho:** completa

## official-03

**Pergunta:** When will the money from yesterday's sales be deposited?

**Intenção:** support (esperada support) · **rota:** router → records · **replanos:** nenhum · **caminho:** supervisor LLM (laço de tool use) · **custo:** US$ 0.0143 · **latência:** 9.3 s

**Resposta:**

> Yesterday's sales (04/11/2026) total R$ 695,50. Of that, R$ 215,50 has already been deposited and R$ 480,00 is still to come:
>
> - **Pix:** R$ 120,00, deposited on 04/11/2026.
> - **Debit:** R$ 95,50, deposited on 05/11/2026.
> - **Credit (30-day plan):** R$ 480,00, expected on 04/12/2026.

**Passos:**

1. **records** · ok · 3671 ms · decidido por: supervisor LLM (tool call)
   - `get_settlements` {"period": "yesterday"} → ok · `{"ok": true, "data": {"period": "yesterday", "from": "2026-11-04", "to": "2026-11-04", "today": "2026-11-05", "schedule": [{"method": "pix"…`

**Checagens:** 10/10 passam · **desfecho:** completa

## official-04

**Pergunta:** Do I need a bank account to receive my sales via Pix?

**Intenção:** knowledge (esperada knowledge) · **rota:** router → faq · **replanos:** nenhum · **caminho:** supervisor LLM (laço de tool use) · **custo:** US$ 0.0149 · **latência:** 8.3 s

**Resposta:**

> Yes. To enable Pix at Getnet, you need a Santander bank domicile (the account where you receive your sales) and an active Pix key [1].
>
> The other eligibility criteria are:
> - A compatible capture method: terminal, TEF or e-commerce.
> - A registration with an individual (PF) legal representative.
>
> If the Pix button is still unavailable after you meet these criteria, the Central de Atendimento can help [1].

**Passos:**

1. **faq** · ok · 2493 ms · decidido por: supervisor LLM (tool call)

**Fontes citadas:** [1] <https://site.getnet.com.br/duvidas/pix/>
**Checagens:** 7/9 passam; falham: facts, resolved · **desfecho:** não resolvida

## official-05

**Pergunta:** My card machine won't connect to the internet, what should I do?

**Intenção:** troubleshoot (esperada troubleshoot) · **rota:** router → records → faq · **replanos:** ['records:need->faq (maquininha offline: se a pergunta é sobre conexão ou sinal, o passo a passo vem )'] · **caminho:** supervisor LLM (laço de tool use) · **custo:** US$ 0.0368 · **latência:** 18.5 s

**Resposta:**

> Your machine T1988B (Get Clássica) is offline on chip with no signal. It has been offline for 5 hours, since 05/11/2026 07:26. Your other machine, T1988A (Get Smart), is online.
>
> 1. Turn the machine off and open the back cover. [1]
> 2. Insert the chip in the slot marked SIM1 or SIM2, with the metal side facing down. [1]
> 3. Close the cover and turn the machine on. Wait for it to connect to the data network. [1]
> 4. When the display shows the network as connected (2G or 3G), the machine is ready to use. [1]
> 5. Run a communication test. Press the function button (F, # or the one on your machine), choose option 2 (maintenance), then option 1 (communication test). [1]
>
> If it still doesn't connect, I can propose a support ticket for T1988B with the reason "no signal". Nothing runs until you confirm, and the proposal expires after 15 minutes. Do you want me to propose it?

**Passos:**

1. **records** · ok · 4494 ms · decidido por: supervisor LLM (tool call)
   - `get_terminals` {} → ok · `{"ok": true, "data": {"terminals": [{"terminal_id": "T1988A", "model": "Get Smart", "status": "online", "connection": "wi-fi", "signal": "b…`
2. **faq** · ok · 5036 ms · decidido por: supervisor LLM (tool call)

**Fontes citadas:** [1] <https://site.getnet.com.br/duvidas/>
**Checagens:** 10/10 passam · **desfecho:** completa

## official-06

**Pergunta:** How does receivables advance (antecipação) work with Getnet?

**Intenção:** knowledge (esperada knowledge) · **rota:** router → faq · **replanos:** nenhum · **caminho:** supervisor LLM (laço de tool use) · **custo:** US$ 0.0300 · **latência:** 15.6 s

**Resposta:**

> You can advance your sales through the Getnet Brasil app, which is always available for this. The app adds no extra fees [1].
>
> - **Timing:** Sales can be advanced from D+1, which is one business day after the sale. They stay available until D-3, which is three business days before the amount would be paid to you [2].
> - **Consent:** Under the new rules, you must authorize Getnet to consult your receivables schedule at the Registradora (the registry). The Registradora confirms the authorization and the operation [2].
> - **Costs:** There are no new charges. You pay only the existing ones, such as rental, MDR and the advance fee [2].
> - **Card brands:** If you enabled some brands, those sales can't be advanced through Getnet. You can only advance them with the brand's own operator [2].
> - **Automatic Advance:** This is a condition for the exemption on the "Receba Conforme suas Vendas" plan. Getnet assesses each contract individually before granting it [1].
> - **Gravame:** If you use your receivables as collateral for a loan, a gravame applies. Your sales are then paid into your Get Conta up to the loan's outstanding balance [2].
>
> I didn't find the percentage for the advance fee. A human agent can confirm it if you want.
>
> You can also ask me to propose an advance of credit receivables for a given amount in reais. You would need to confirm it, and then a human agent would have to approve it before it runs.

**Passos:**

1. **faq** · ok · 6466 ms · decidido por: supervisor LLM (tool call)

**Fontes citadas:** [1] <https://site.getnet.com.br/duvidas/>; [2] <https://site.getnet.com.br/duvidas/antecipacao-de-vendas/>
**Checagens:** 9/9 passam · **desfecho:** completa

## official-07

**Pergunta:** What's the euro exchange rate today?

**Intenção:** general (esperada general) · **rota:** router → general · **replanos:** nenhum · **caminho:** supervisor LLM (laço de tool use) · **custo:** US$ 0.0147 · **latência:** 9.2 s

**Resposta:**

> Today (2026-11-05), the euro is R$ 6,1327 for buying and R$ 6,1339 for selling, according to Banco Central do Brasil (PTAX). That comes from the intermediate bulletin published at 12:06.
>
> Source: https://www.bcb.gov.br/estabilidadefinanceira/historicocotacoes

**Passos:**

1. **general** · ok · 3067 ms · decidido por: supervisor LLM (tool call)
   - `currency_rate` {"currency": "EUR", "date": "2026-11-05"} → ok

**Dados ao vivo de:** <https://www.bcb.gov.br/estabilidadefinanceira/historicocotacoes>
**Checagens:** 10/10 passam · **desfecho:** completa

## official-08

**Pergunta:** My card machine is showing a transaction decline error.

**Intenção:** troubleshoot (esperada troubleshoot) · **rota:** router → records → faq · **replanos:** ['records:need->faq (venda recusada: o que fazer vem do manual de recusas; maquininha offline: se a p)'] · **caminho:** supervisor LLM (laço de tool use) · **custo:** US$ 0.0271 · **latência:** 24.8 s

**Resposta:**

> The declines on your machine came from the card issuers, not from a machine fault. There were 2 declines in the last 7 days, both today on terminal T1988A. That terminal is online on Wi-Fi with good signal.
>
> - **TX1007** (05/11, 10:05, credit, R$ 210,00): code 51, insufficient balance or credit limit. The buyer should contact the card issuer or pay with another card or Pix.
> - **TX1008** (05/11, 10:40, debit, R$ 75,00): code 05, not authorized by the issuer. The buyer should contact their bank. Retrying will not help.
>
> In the same period there were 6 approved sales, totaling R$ 995,40.
>
> Separately, terminal T1988B has been offline with no signal for 5 hours. It has no declines. I can propose a support ticket for it, but nothing runs until you confirm.
>
> If you need more help, I can hand your case to a human agent.

**Passos:**

1. **records** · ok · 4740 ms · decidido por: supervisor LLM (tool call)
   - `get_transactions` {"period": "last_7_days"} → ok · `{"ok": true, "data": {"period": "last_7_days", "from": "2026-10-30", "to": "2026-11-05", "today": "2026-11-05", "sales": [{"transaction_id"…`
   - `get_terminals` {} → ok · `{"ok": true, "data": {"terminals": [{"terminal_id": "T1988A", "model": "Get Smart", "status": "online", "connection": "wi-fi", "signal": "b…`
2. **faq** · insufficient · motivo `no_source` · 8802 ms · decidido por: supervisor LLM (tool call)

**Checagens:** 10/10 passam · **desfecho:** completa

## official-09

**Pergunta:** How many installments can I split a sale into with the crediário?

**Intenção:** knowledge (esperada knowledge) · **rota:** router → faq · **replanos:** nenhum · **caminho:** supervisor LLM (laço de tool use) · **custo:** US$ 0.0148 · **latência:** 9.7 s

**Resposta:**

> Up to 48 installments. The Crediário lets your customer split a credit card purchase in up to 48 times [1].
>
> - Each card issuer sets its own installment limit under its credit policies [2].
> - Interest rates may vary by issuer [1].
> - On the card machine, you can run a simulation (credit > crediário). It shows the customer the interest and the final amount.
> - The issuer still has to approve the transaction [2].

**Passos:**

1. **faq** · ok · 4285 ms · decidido por: supervisor LLM (tool call)

**Fontes citadas:** [1] <https://site.getnet.com.br/crediario/>; [2] <https://site.getnet.com.br/duvidas/crediario/>
**Checagens:** 9/9 passam · **desfecho:** completa

## official-10

**Pergunta:** Can I sell through WhatsApp using the Payment Link?

**Intenção:** knowledge (esperada knowledge) · **rota:** router → faq · **replanos:** nenhum · **caminho:** supervisor LLM (laço de tool use) · **custo:** US$ 0.0143 · **latência:** 9.7 s

**Resposta:**

> Yes, you can sell through WhatsApp with the Payment Link. You send the link to your customers on WhatsApp, social networks, email or SMS. They click it, choose a payment method and complete the purchase [1]. The Getnet Payment Link page also lists selling through WhatsApp or a social network as a benefit [2].

**Passos:**

1. **faq** · ok · 3974 ms · decidido por: supervisor LLM (tool call)

**Fontes citadas:** [1] <https://site.getnet.com.br/duvidas/link-de-pagamento/>; [2] <https://site.getnet.com.br/link-de-pagamento/>
**Checagens:** 9/9 passam · **desfecho:** completa
