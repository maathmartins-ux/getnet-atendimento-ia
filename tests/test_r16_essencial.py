"""docs/ESSENCIAL.md sai das linhas de src/app/: módulo novo fora do mapa ou doc velho reprova."""
from scripts import module_map


def test_essential_map_is_current_and_covers_every_module():
    assert module_map.main(["--check"]) == 0
