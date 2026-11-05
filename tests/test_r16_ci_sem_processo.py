"""O ci.yml vai para a entrega com o kit: comentário de processo nele é lido pelo avaliador (rodada 15)."""
from scripts.check import workflow_process_words


def test_kit_workflows_have_no_process_words():
    assert workflow_process_words() == []
