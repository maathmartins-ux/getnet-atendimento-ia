"""Rodada 17: busca medida num gold de outra família (rótulos de relevância nos 10 primeiros trechos)."""
from __future__ import annotations

import json
from types import SimpleNamespace

from evals import retrieval_cross as rc


class FakeLLM:
    model, provider = "gpt-5", "openai_compat"

    def __init__(self, answers):
        self.answers = list(answers)

    def complete(self, system, messages, max_tokens=512, schema=None):
        return SimpleNamespace(text=json.dumps({"relevant": self.answers.pop(0)}), model=self.model,
                               input_tokens=1000, output_tokens=10)


class FakeRetriever:
    def search(self, query, k=10):
        return [SimpleNamespace(doc=SimpleNamespace(id=f"d{i}", title=f"t{i}", text="x")) for i in range(k)]


def test_scores_rank_of_first_useful_passage_and_counts_questions_without_any():
    items = [{"id": "real-01", "split": "real", "message": "a"}, {"id": "h-1", "split": "heldout", "message": "b"},
             {"id": "h-2", "split": "heldout", "message": "c"}]
    r = rc.run(FakeLLM([[1, 4], [5], []]), FakeRetriever(), items)
    assert r["status"] == "complete" and r["com_trecho_util"] == 2 and r["sem_trecho_util"] == 1
    assert r["hit@3"] == 0.5 and r["hit@5"] == 1.0 and r["mrr@10"] == round((1 + 1 / 5) / 2, 3)
    assert set(r["por_split"]) == {"real", "heldout"}


def test_out_of_range_positions_are_ignored_and_budget_stops():
    two = [{"id": "a", "split": "real", "message": "a"}, {"id": "b", "split": "real", "message": "b"}]
    r = rc.run(FakeLLM([[0, 11, 2], [1]]), FakeRetriever(), two)
    assert r["linhas"][0]["relevant"] == [2]
    r = rc.run(FakeLLM([[1], [1]]), FakeRetriever(), two, max_usd=0.0)
    assert r["status"] == "aborted_max_usd" and r["perguntas"] == 0


def test_only_knowledge_heldout_and_all_real(tmp_path):
    h = tmp_path / "h.jsonl"
    h.write_text("\n".join(json.dumps(x) for x in [
        {"id": "h1", "message": "x", "expect": {"intent": "knowledge"}},
        {"id": "h2", "message": "y", "expect": {"intent": "support"}}]), encoding="utf-8")
    r = tmp_path / "r.jsonl"
    r.write_text(json.dumps({"id": "real-1", "split": "real", "message": "z"}), encoding="utf-8")
    assert [q["id"] for q in rc.questions(h, r)] == ["real-1", "h1"]


def test_malformed_judge_reply_marks_the_question_unlabeled_and_keeps_going():
    class Broken(FakeLLM):
        def complete(self, system, messages, max_tokens=512, schema=None):
            if self.answers.pop(0) == "bad":
                return SimpleNamespace(text="não é json", model=self.model, input_tokens=10, output_tokens=1)
            ok = json.dumps({"relevant": [2]})
            return SimpleNamespace(text=ok, model=self.model, input_tokens=10, output_tokens=1)

    items = [{"id": "a", "split": "real", "message": "a"}, {"id": "b", "split": "real", "message": "b"}]
    r = rc.run(Broken(["bad", "ok"]), FakeRetriever(), items)
    assert r["status"] == "complete" and r["sem_rotulo"] == ["a"] and r["perguntas"] == 1 and r["hit@3"] == 1.0
