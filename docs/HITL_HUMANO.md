# Atendimento humano de verdade

Gerado por `scripts/hitl_humano.py` no commit `d89ece1` em 2026-11-05 15:24 UTC (LLM: `anthropic`). A conversa foi aberta pelo `POST /chat`; a resposta do caso foi decidida por uma pessoa (Matheus, dono do projeto), que escolheu o texto entre três alternativas pelo celular; a sessão de apoio o enviou pelo endpoint do console (`POST /handoffs/{id}/reply`, o mesmo do `/operator`), com a chave pessoal dela gerada nesta execução (o processo guardou só o sha256 dela em `OPERATOR_KEYS`; o token compartilhado não valia). Nada foi escrito à mão neste arquivo.

**Cliente** (`cliente1988`): Quero falar com um atendente: tem uma cobrança na minha conta que eu não reconheço.

**Assistente:** Encaminhei seu caso para um atendente humano. O protocolo é **T-c3c50f62**, e a resposta do atendente vai aparecer nesta conversa.

A decisão sobre uma cobrança que você não reconhece é de um atendente, e o assistente não decide esse tipo de caso.

**Atendente** (`pessoa:Matheus`, caso `T-c3c50f62`): Olá, aqui é o Matheus. Para eu localizar, me diga a data e o valor da cobrança que você não reconhece, que eu verifico e já te respondo por aqui.

**Assistente, retomando depois do atendente:** O atendente Matheus já está com o seu caso. Para localizar a cobrança, ele precisa que você informe a **data** e o **valor** que você não reconhece. Assim que você enviar, ele verifica e responde por aqui.

| caso | aberto | respondido | retomado | tempo até a resposta |
|---|---|---|---|---:|
| `T-c3c50f62` (user_request) | 2026-11-05 15:21:30 UTC | 2026-11-05 15:24:46 UTC | 2026-11-05 15:24:48 UTC | 3 min 16 s |

Auditoria do caso: `handoff_reply` registrado por `operator:Matheus` (canal console, 2026-11-05 15:24:46 UTC).
