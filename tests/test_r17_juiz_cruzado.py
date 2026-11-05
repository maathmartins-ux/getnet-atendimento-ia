"""Rodada 17: 2º juiz de outra família nas mesmas linhas, com teto de gasto que vale, e a concordância dos dois."""
from __future__ import annotations

import json

from app import observability
from evals import judge, judge_agree


def _v(i, run, grounded, split="official"):
    return {"id": i, "run": run, "split": split, "grounded": grounded, "failure_type": "none", "reason": "r"}


def test_agreement_counts_only_rows_both_judged_and_lists_divergences():
    a = {"model": "claude-opus-5-5", "judge_family": "anthropic",
         "verdicts": [_v("o-1", 0, True), _v("o-2", 0, False), _v("o-3", 0, True), _v("m-1", 0, True, "memory")]}
    b = {"model": "gpt-5", "judge_family": "openai_compat",
         "verdicts": [_v("o-1", 0, True), _v("o-2", 0, True), _v("o-3", 0, True), _v("x-9", 0, False)]}
    r = judge_agree.compare(a, b)
    assert r["familias_diferentes"] and r["linhas_em_comum"] == 3 and r["so_em_a"] == 1 and r["so_em_b"] == 1
    assert r["fundamentada"]["concordancia"] == round(2 / 3, 3)
    assert [d["id"] for d in r["divergencias"]] == ["o-2"]


def test_other_family_judge_without_price_still_has_a_cost(monkeypatch):
    """Modelo fora da tabela contava US$ 0 e o --max-usd do juiz nunca parava."""
    monkeypatch.setenv("JUDGE_PROVIDER", "openai_compat")
    monkeypatch.setenv("JUDGE_MODEL", "gpt-5")
    monkeypatch.delenv("JUDGE_PRICE_PER_MTOK", raising=False)
    assert observability.llm_cost("gpt-5", 1_000_000, 0) == observability.JUDGE_PRICE_FALLBACK[0]
    monkeypatch.setenv("JUDGE_PRICE_PER_MTOK", "1.25,10")
    assert observability.llm_cost("gpt-5", 1_000_000, 1_000_000) == 11.25
    monkeypatch.delenv("JUDGE_PROVIDER")
    assert observability.llm_cost("gpt-5", 1_000_000, 0) == 0.0  # fora do juiz cruzado, nada muda


def test_out_writes_elsewhere_and_keeps_judge_json(tmp_path, monkeypatch):
    main_out = tmp_path / "judge.json"
    main_out.write_text(json.dumps({"verdicts": [_v("o-1", 0, True)]}), encoding="utf-8")
    monkeypatch.setattr(judge, "OUT", main_out)
    cross = tmp_path / "judge_cross.json"
    cross.write_text(json.dumps({"verdicts": [_v("o-1", 0, True)]}), encoding="utf-8")
    seen = {}
    monkeypatch.setattr(judge, "sync_live_summaries", lambda head, files, cmd: seen.update(head) or [])
    assert judge.main(["--out", str(cross), "--sync"]) == 0  # --sync lê o relatório do --out (nada é reescrito aqui)
    assert seen["verdicts"][0]["id"] == "o-1" and judge.OUT == cross
    assert json.loads(main_out.read_text(encoding="utf-8"))["verdicts"][0]["id"] == "o-1"


def test_openai_api_gets_max_completion_tokens(monkeypatch):
    """Os modelos de raciocínio da OpenAI recusam `max_tokens` (400): o juiz cruzado cairia na 1ª chamada."""
    from app.llm import OpenAICompatLLM

    seen = []

    def post(url, body, headers):
        seen.append(body)
        return 200, {"choices": [{"message": {"content": '{"ok": true}'}, "finish_reason": "stop"}],
                     "usage": {"prompt_tokens": 10, "completion_tokens": 5}}

    monkeypatch.delenv("JUDGE_TOKENS_FIELD", raising=False)
    msg = [{"role": "user", "content": "q"}]
    OpenAICompatLLM("https://api.openai.com/v1", "gpt-5", "k", post=post).complete("s", msg)
    OpenAICompatLLM("http://localhost:8080/v1", "outro", None, post=post).complete("s", msg)
    assert "max_completion_tokens" in seen[0] and "max_tokens" not in seen[0]
    assert seen[1]["max_tokens"] == 4096 and "max_completion_tokens" not in seen[1]


def test_same_row_with_another_text_is_left_out_and_counted():
    a = {"verdicts": [{**_v("o-1", 0, True), "answer_sha": "aaa"}, {**_v("o-2", 0, True), "answer_sha": "bbb"}]}
    b = {"verdicts": [{**_v("o-1", 0, False), "answer_sha": "zzz"}, {**_v("o-2", 0, True), "answer_sha": "bbb"}]}
    r = judge_agree.compare(a, b)
    assert r["linhas_em_comum"] == 1 and r["mesma_linha_outro_texto"] == 1 and r["divergencias"] == []
