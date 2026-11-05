"""Rodada 16: título de página repetido pelo site em páginas diferentes não é característica do produto. No corpus do
desafio, o <title> "Maquininha POS 3G + Wi-Fi" vinha nas páginas de duas maquininhas."""
from __future__ import annotations

from types import SimpleNamespace

from app import agents


def _doc(i, title, url, text="t"):
    return SimpleNamespace(id=i, title=title, url=url, text=text)


def test_shared_title_is_marked_and_unique_title_is_not(monkeypatch):
    docs = [_doc("a1", "Site | POS", "https://x/a/"), _doc("a2", "Site | POS", "https://x/a/"),
            _doc("b1", "Site | POS", "https://x/b/"), _doc("c1", "Site | Pix", "https://x/c/")]
    index = SimpleNamespace(docs=docs)
    monkeypatch.setattr("app.rag.get_index", lambda: index)
    agents._shared_titles.cache_clear()
    assert agents.shown_title(docs[0]) == "Site | POS [título comum a 2 páginas do site: o produto é o do endereço]"
    assert agents.shown_title(docs[3]) == "Site | Pix"
    listing = agents._listing([SimpleNamespace(doc=docs[2]), SimpleNamespace(doc=docs[3])])
    first = listing.splitlines()[0]
    assert first.startswith("[1] Site | POS [título comum a 2 páginas") and "(https://x/b/)" in first
    assert listing.splitlines()[1].startswith("[2] Site | Pix (https://x/c/)")
    agents._shared_titles.cache_clear()
