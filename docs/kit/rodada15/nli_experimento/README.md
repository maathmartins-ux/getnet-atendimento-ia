# 2º juiz sem LLM (NLI local): medido e deixado de fora

Ideia própria aprovada pelo dono (05/11): um modelo pequeno de inferência textual, de outra família (mDeBERTa
multilíngue em XNLI, ONNX int8, ~317 MB, revisão e sha256 fixados no script), conferindo cada frase da resposta contra
os trechos e os dados das tools, como 2ª opinião do juiz LLM. Regra fixada antes de medir: frase com base se algum
trecho a implica com p ≥ 0,5; resposta fundamentada se nenhuma frase é contradita e ≥ 80% têm base.

Medido nas respostas ao vivo da rodada 15 (commit 28f71da), sem API:

| Versão | Respostas | Concordância com o juiz LLM | kappa | NLI fundamentadas | juiz LLM fundamentadas |
|---|---:|---:|---:|---:|---:|
| trecho inteiro (até 512 tokens) | 78 (official + memory) | 0.154 | -0.011 | 0.09 | 0.91 |
| janelas de 2 frases, top-3 por palavras em comum | 30 (official) | 0.133 | 0.008 | 0.033 | 0.9 |

Decisão: fica de fora (regra combinada: se não passar no teste, sai e é declarado). Causa provável: a resposta
parafraseia e resume vários trechos (frase em inglês sobre fonte em português, pronome sem antecedente, número
reescrito), e o NLI de frase isolada dá implicação baixa até para frase certa (0,2–0,45 em frases que o juiz LLM e as
pessoas aceitam). Para tentar de novo: premissa = janela + a frase anterior da resposta (resolve o "It"), tradução da
frase para o idioma do trecho, e limiar calibrado nos rótulos humanos, não no juiz LLM.
