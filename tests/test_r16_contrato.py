"""Contrato de resposta: a falta que, tirado o que a resposta já cobriu, não tem termo em comum com a pergunta não
deixa a resposta parcial (a frase honesta fica no texto). Frases medidas na bateria da rodada 16."""
from app.coverage import is_refinement

Q05 = ["My card machine won't connect to the internet, what should I do?"]
B05 = ("Your offline machine is T1988B, on a chip connection. Steps: check the chip, then run a communication test "
       "(press the function key, 2, then 1). If the signal fluctuates (error ADQ 1-84), press Function and 25.")
QD = ["Minha maquininha não conecta: qual delas está com problema e como eu resolvo?",
      "Qual maquininha está offline e como resolvo a conexão da Get Clássica T1988B?"]
BD = ("A maquininha com problema é a T1988B (Get Clássica), offline e sem sinal. Como resolver: desligue a máquina, "
      "confira o chip e faça o teste de comunicação; na oscilação de sinal, aperte Função e 25.")


def test_sub_case_the_customer_did_not_ask_is_not_missing():
    assert is_refinement("what to do if the communication test fails", B05, Q05)
    assert is_refinement("passo a passo específico da Get Clássica para ficar sem sinal", BD, QD)


def test_what_the_customer_asked_and_was_not_answered_stays_missing():
    q = ["Quanto custa o aluguel da Get Smart?"]
    assert not is_refinement("preço do aluguel da Get Smart", "A Get Smart roda apps de gestão.", q)
    q2 = ["Quais as taxas da Get Clássica e da Get Smart?"]
    assert not is_refinement("taxas da Get Smart", "A Get Clássica cobra 1,69% no débito.", q2)


def test_neighbor_rate_in_a_difference_question_is_not_missing():
    # lição do ensaio 14: a tabela de taxas numa pergunta de diferença é item vizinho
    q = ["What's the difference between the Get Clássica and the Get Smart?"]
    assert is_refinement("Get Smart rates", "The Get Smart runs management apps. The Get Clássica costs less.", q)
