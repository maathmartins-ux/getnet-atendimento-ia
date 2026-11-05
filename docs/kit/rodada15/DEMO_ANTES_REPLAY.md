# Respostas reais — split `official`

Geradas de `evals/results/live_official.json` (provedor `replay`, status `complete`, gasto US$ 0.00); respostas medidas no commit `28f71da` (2026-11-04T23:20:34Z), página gerada no commit `28f71da` em 04/11/2026 23:25 UTC. Nada aqui foi escrito à mão: é a saída do `POST /chat` com o LLM ligado, 1ª rodada de cada caso.

Estabilidade em 3 rodadas: pass@1 0.7333, pass^3 0.6; instáveis: official-01, official-02, official-05.

Em cada passo, **decidido por** diz quem pôs o agente no turno: o supervisor LLM (tool call); o plano do router (o router LLM, ou a regra que o substitui: seguimento herdado, guarda da própria empresa, queda do LLM), quando o supervisor LLM não foi consultado (rodado pelo atalho de 1 passo ou pelo motor de tabela); o código, com a regra entre parênteses (`supervisor.CODE_WHY`); ou a operadora que respondeu o caso. "não registrado" = passo gravado sem o campo `decided_by`.

| caso | intenção | rota | ferramentas | handoff | veredito automático |
|---|---|---|---|---|---|
| `official-01` | knowledge | router → faq | — | não | OK |
| `official-02` | general | router → general | weather_forecast | não | OK |
| `official-03` | support | router → records | get_settlements | não | OK |
| `official-04` | knowledge | router → faq | — | não | falhou: facts, resolved |
| `official-05` | None |  | — | não | falhou: intent |
| `official-06` | knowledge | router → faq | — | não | OK |
| `official-07` | general | router → general | currency_rate | não | OK |
| `official-08` | troubleshoot | router → records → faq | get_transactions, get_terminals | não | OK |
| `official-09` | knowledge | router → faq | — | não | OK |
| `official-10` | knowledge | router → faq | — | não | OK |

## official-01

**Pergunta:** What's the difference between the Get Clássica and the Get Smart?

**Intenção:** knowledge (esperada knowledge) · **rota:** router → faq · **replanos:** nenhum · **caminho:** supervisor LLM (laço de tool use) · **custo:** US$ 0.0000 · **latência:** 2.2 s

**Resposta:**

> The Get Smart is an Android "smart" card machine that works as a management terminal. The sources describe the Get Clássica mainly through its rates and its free-machine offer.
>
> **Get Smart**
> - You can control stock, place orders, close tabs, load a menu and issue invoices on the device. It can also integrate with your business system [1].
> - It can replace a computer and a fiscal printer at the counter [3].
> - Most apps on it issue NF-e, but confirm with the specific app [4].
> - It can be used as a TEF solution [prod-get-tap-04 is not cited for this; the source is [7]].
> - App subscriptions are charged by the app developers. You pay Getnet rent and administrative fees [10].
>
> **Get Clássica**
> - It comes with a free account and card, receipt in 2 days, and it works for CPF and CNPJ [5].
> - A 2025 page lists a single rate across the main card brands: debit at 1.69% and credit in 1x at 3.79%. That page may be outdated [5].
>
> **Free-machine offer**
> - The 2026 page lists the Get Clássica for monthly sales above R$ 20 thousand. It lists the Get Clássica or Get Smart above R$ 40 thousand and above R$ 80 thousand [8].
> - Voucher (VA/VR) and Crediário sales don't count toward rent exemption [8].
>
> I didn't find Get Smart rates or rent amounts, or Get Clássica management features. A human agent can help with those if you want.

**Passos:**

1. **faq** · ok · 1926 ms · decidido por: supervisor LLM (tool call)

**Fontes:** <https://site.getnet.com.br/duvidas/get-smart/>; <https://site.getnet.com.br/todas-as-maquininhas/>; <https://site.getnet.com.br/duvidas/get-smart/>; <https://site.getnet.com.br/duvidas/get-smart/>; <https://site.getnet.com.br/maquininha/get-classica/>
**Checagens:** 9/9 passam · **desfecho:** completa

## official-02

**Pergunta:** What's the weather forecast in Porto Alegre tomorrow?

**Intenção:** general (esperada general) · **rota:** router → general · **replanos:** nenhum · **caminho:** supervisor LLM (laço de tool use) · **custo:** US$ 0.0000 · **latência:** 4.2 s

**Resposta:**

> Tomorrow (2026-11-05) in Porto Alegre, the forecast is a low of 18 °C, a high of 27 °C, and up to a 39% chance of rain. Source: wttr.in.

**Passos:**

1. **general** · ok · 4153 ms · decidido por: supervisor LLM (tool call)
   - `weather_forecast` {"city": "Porto Alegre", "day": "amanhã"} → ok

**Fontes:** <https://wttr.in/>
**Checagens:** 10/10 passam · **desfecho:** completa

## official-03

**Pergunta:** When will the money from yesterday's sales be deposited?

**Intenção:** support (esperada support) · **rota:** router → records · **replanos:** nenhum · **caminho:** supervisor LLM (laço de tool use) · **custo:** US$ 0.0000 · **latência:** 0.1 s

**Resposta:**

> Yesterday's sales total R$ 695,50, and the deposit date depends on how each sale was paid:
>
> - **Pix:** R$ 120,00, deposited on 03/11/2026.
> - **Debit:** R$ 95,50, deposited on 04/11/2026.
> - **Credit (30-day plan):** R$ 480,00, expected on 03/12/2026.
>
> The records tool says R$ 215,50 has already been deposited and R$ 480,00 is still to be deposited.

**Passos:**

1. **records** · ok · 37 ms · decidido por: supervisor LLM (tool call)
   - `get_settlements` {"period": "yesterday"} → ok · `{"ok": true, "data": {"period": "yesterday", "from": "2026-11-03", "to": "2026-11-03", "today": "2026-11-04", "schedule": [{"method": "pix"…`

**Checagens:** 10/10 passam · **desfecho:** completa

## official-04

**Pergunta:** Do I need a bank account to receive my sales via Pix?

**Intenção:** knowledge (esperada knowledge) · **rota:** router → faq · **replanos:** nenhum · **caminho:** supervisor LLM (laço de tool use) · **custo:** US$ 0.0000 · **latência:** 1.6 s

**Resposta:**

> It depends, and the sources don't say whether an account is required. They do describe ways to receive Pix and the Get Conta option.
>
> - Getnet generates a Pix QR Code on its capture channels: physical terminals, TEF Auttar and e-commerce [5].
> - You can also receive Pix through biometrics, Get Tap on your phone, or a QR Code on the card machine [7].
> - Get Conta is Getnet's free digital business account. You can send and receive money and sell through Pix with it [6].
> - The FAQ describes a Pix received into a Get Conta [4].
> - To open a Get Conta, you choose a rental or purchase machine and pick the option to receive your sales in the account [10]. The sources don't say this is mandatory for Pix.
>
> If you'd like a definite answer, I can hand your case to a human agent.

**Passos:**

1. **faq** · partial · motivo `partial_coverage` · 1522 ms · decidido por: supervisor LLM (tool call)

**Fontes:** <https://site.getnet.com.br/duvidas/>; <https://site.getnet.com.br/duvidas/pix-mais-respostas/>; <https://site.getnet.com.br/pix/>; <https://site.getnet.com.br/duvidas/pix-mais-respostas/>; <https://site.getnet.com.br/duvidas/>
**Checagens:** 7/9 passam; falham: facts, resolved · **desfecho:** não resolvida

## official-05

**Pergunta:** My card machine won't connect to the internet, what should I do?

**Intenção:** None (esperada troubleshoot) · **rota:**  · **replanos:** nenhum · **caminho:** None · **custo:** US$ 0.0000 · **latência:** 1.6 s

**Resposta:**


**Checagens:** 0/1 passam; falham: intent · **desfecho:** não resolvida

## official-06

**Pergunta:** How does receivables advance (antecipação) work with Getnet?

**Intenção:** knowledge (esperada knowledge) · **rota:** router → faq · **replanos:** nenhum · **caminho:** supervisor LLM (laço de tool use) · **custo:** US$ 0.0000 · **latência:** 1.7 s

**Resposta:**

> A sales schedule can be advanced from D+1, which is one business day after the sale. It stays available until D-3, which is three business days before the schedule settles into your account [6].
>
> - **Card brands:** Some brands can't be advanced through Getnet. For those, you have to go through the brand's own operator [6].
> - **Normal receiving options:** Debit sales are available the next day. For credit, you can choose to receive everything in 2 days, in 30 days, or month by month following the card installments [7].
> - **Automatic Advance:** This is a condition for the exemption on the "Receba Conforme suas Vendas" plan.
> - **Collateral (gravame):** If you use your receivables as collateral for a loan, the schedule goes to the lender to guarantee the operation [2]. Sales then go to your Get Conta, up to the outstanding loan balance [1].
>
> I didn't find the advance fee or the steps to request one. I can propose an advance of credit receivables for a specific amount in reais. You would need to confirm it, and a human agent would then have to approve it. I can also hand your case to an agent if you'd like.

**Passos:**

1. **faq** · ok · 1605 ms · decidido por: supervisor LLM (tool call)

**Fontes:** <https://site.getnet.com.br/duvidas/antecipacao-de-vendas/>; <https://site.getnet.com.br/duvidas/antecipacao-de-vendas/>; <https://site.getnet.com.br/duvidas/>; <https://site.getnet.com.br/duvidas/antecipacao-de-vendas/>; <https://site.getnet.com.br/duvidas/link-de-pagamento/>
**Checagens:** 9/9 passam · **desfecho:** completa

## official-07

**Pergunta:** What's the euro exchange rate today?

**Intenção:** general (esperada general) · **rota:** router → general · **replanos:** nenhum · **caminho:** supervisor LLM (laço de tool use) · **custo:** US$ 0.0000 · **latência:** 1.0 s

**Resposta:**

> Today's euro rate (PTAX, 2026-11-04) is R$ 6.1531 to buy and R$ 6.1549 to sell for 1 EUR. Rounded, that is R$ 6.15 for both.
>
> Source: Banco Central do Brasil, https://www.bcb.gov.br/estabilidadefinanceira/historicocotacoes

**Passos:**

1. **general** · ok · 970 ms · decidido por: supervisor LLM (tool call)
   - `currency_rate` {"currency": "EUR", "date": "2026-11-04"} → ok

**Fontes:** <https://www.bcb.gov.br/estabilidadefinanceira/historicocotacoes>
**Checagens:** 10/10 passam · **desfecho:** completa

## official-08

**Pergunta:** My card machine is showing a transaction decline error.

**Intenção:** troubleshoot (esperada troubleshoot) · **rota:** router → records → faq · **replanos:** ['records:need->faq (venda recusada: o que fazer vem do manual de recusas; maquininha offline: se a p)'] · **caminho:** supervisor LLM (laço de tool use) · **custo:** US$ 0.0000 · **latência:** 0.9 s

**Resposta:**

> The declines on your machine came from the card issuer, and the data shows no terminal fault. In the last 30 days there were 2 declined sales, both today on terminal T1988A:
>
> - **TX1007**, 10:05, credit, R$ 210,00. Code 51 means insufficient balance or credit limit. The buyer should contact the card issuer or pay with another card or Pix.
> - **TX1008**, 10:40, debit, R$ 75,00. Code 05 means the issuer did not authorize it. The buyer should contact the card-issuing bank. Retrying will not help.
>
> T1988A is online on Wi-Fi with good signal. Separately, T1988B is offline with no signal and has been for 5 hours. It has no declines.
>
> I can propose a support ticket for T1988B for "no signal". Nothing happens until you confirm, and the proposal expires after 15 minutes. I can also hand you to a human agent if you'd like.

**Passos:**

1. **records** · ok · 3.4 ms · decidido por: supervisor LLM (tool call)
   - `get_transactions` {"period": "last_30_days"} → ok · `{"ok": true, "data": {"period": "last_30_days", "from": "2026-10-06", "to": "2026-11-04", "today": "2026-11-04", "sales": [{"transaction_id…`
   - `get_terminals` {} → ok · `{"ok": true, "data": {"terminals": [{"terminal_id": "T1988A", "model": "Get Smart", "status": "online", "connection": "wi-fi", "signal": "b…`
2. **faq** · insufficient · motivo `no_source` · 839 ms · decidido por: supervisor LLM (tool call)

**Checagens:** 10/10 passam · **desfecho:** completa

## official-09

**Pergunta:** How many installments can I split a sale into with the crediário?

**Intenção:** knowledge (esperada knowledge) · **rota:** router → faq · **replanos:** nenhum · **caminho:** supervisor LLM (laço de tool use) · **custo:** US$ 0.0000 · **latência:** 0.9 s

**Resposta:**

> You can split a sale into up to 48 installments with the Crediário on a credit card [1][5]. Each card issuer sets its own installment limit under its credit policies, and interest rates can also vary by issuer [1][3].
>
> To see the customer's interest, run a simulation on the terminal. Insert the card, enter the amount, and choose credit > crediário. You can also print the simulation receipt. The simulation is for reference only and is subject to credit analysis. The issuer decides whether to approve the transaction [3].

**Passos:**

1. **faq** · ok · 848 ms · decidido por: supervisor LLM (tool call)

**Fontes:** <https://site.getnet.com.br/crediario/>; <https://site.getnet.com.br/crediario/>; <https://site.getnet.com.br/duvidas/crediario/>; <https://site.getnet.com.br/duvidas/parcelado/>; <https://site.getnet.com.br/crediario/>
**Checagens:** 9/9 passam · **desfecho:** completa

## official-10

**Pergunta:** Can I sell through WhatsApp using the Payment Link?

**Intenção:** knowledge (esperada knowledge) · **rota:** router → faq · **replanos:** nenhum · **caminho:** supervisor LLM (laço de tool use) · **custo:** US$ 0.0000 · **latência:** 0.8 s

**Resposta:**

> Yes, you can sell through WhatsApp with the Payment Link. You send the link to your customers by WhatsApp, social media, email or SMS. They click it, choose a payment method and complete the purchase [1].

**Passos:**

1. **faq** · ok · 791 ms · decidido por: supervisor LLM (tool call)

**Fontes:** <https://site.getnet.com.br/duvidas/link-de-pagamento/>; <https://site.getnet.com.br/link-de-pagamento/>; <https://site.getnet.com.br/link-de-pagamento/>; <https://site.getnet.com.br/duvidas/link-de-pagamento/>; <https://site.getnet.com.br/duvidas/link-de-pagamento/>
**Checagens:** 9/9 passam · **desfecho:** completa
