import csv
import json

import pytest

from fabrag import assistant as A
from fabrag.baseline import baseline_search_fn, baseline_sections_fn, load_sop_chunks
from fabrag.evaluate import aggregate_correct, retrieval_metrics
from fabrag.generate import generate
from fabrag.judge import build_judge_messages, judge_metrics, parse_judgement


@pytest.fixture(scope="module")
def data(tmp_path_factory):
    out = tmp_path_factory.mktemp("data")
    generate(out, seed=42, n_events=450)
    questions = [json.loads(line) for line in (out / "eval" / "eval_questions.jsonl").read_text().splitlines()]
    with open(out / "ground_truth" / "ooc_ground_truth.csv", newline="") as f:
        truth = {r["event_id"]: r["true_root_cause"] for r in csv.DictReader(f)}
    return out, questions, truth


def _preds(bot, questions):
    out = []
    for q in questions:
        if A.route(q["question"]) == "sql":
            out.append({"qid": q["qid"], "route": "sql", "retrieved_sop_ids": [], "retrieved_chunk_ids": [],
                        "retrieved_event_ids": [], "declined": False})
            continue
        sop, ev = bot.retrieve(q["question"])
        out.append({"qid": q["qid"], "route": "retrieval", "retrieved_sop_ids": list(dict.fromkeys(h["sop_id"] for h in sop)),
                    "retrieved_chunk_ids": [h["chunk_id"] for h in sop],
                    "retrieved_event_ids": [h["event_id"] for h in ev], "declined": False})
    return out


# ------------------------------------------------------------------ eval set
def test_eval_set_week3(data):
    out, questions, _ = data
    assert len(questions) == 61
    assert [q["qid"] for q in questions[:49]] == [f"Q{i:03d}" for i in range(1, 50)]  # Week 2 IDs unchanged
    para = [q for q in questions if q["type"] == "paraphrase"]
    assert len(para) == 12
    all_chunks = {c["chunk_id"] for c in load_sop_chunks(out / "sops", include_low_value=True)}
    for q in questions:
        assert set(q["expected_chunk_ids"]) <= all_chunks, q["qid"]
        if q["type"] in ("troubleshooting", "paraphrase", "procedure"):
            assert q["expected_chunk_ids"], q["qid"]
    for q in para:  # paraphrases must not reuse the SOP title words
        title = next(c["sop_title"] for c in load_sop_chunks(out / "sops") if c["sop_id"] == q["expected_sop_ids"][0])
        generic = {"wafer", "wafers"}  # every fab question mentions wafers
        shared = {w for w in title.lower().split() if len(w) > 4} & set(q["question"].lower().split()) - generic
        assert not shared, (q["qid"], shared)
        assert A.route(q["question"]) == "retrieval", q["qid"]


def test_low_value_sections_not_indexed(data):
    out, _, _ = data
    chunks = load_sop_chunks(out / "sops")
    assert not any(c["section_title"].startswith(("1. Purpose", "2. Scope", "11. Related")) for c in chunks)
    assert len(chunks) == 22 * 8 + 4


# ------------------------------------------------------------------ parent-document expansion
def test_expand_top_sop_adds_key_sections_in_order():
    def c(cid, title):
        return {"chunk_id": cid, "sop_id": cid.split("#")[0], "section_title": title, "retrieval_text": cid}
    hits = [c("SOP-LITH-003#03", "3. Symptoms"), c("SOP-LITH-004#05", "5. Diagnostic checks")]
    sections = [c("SOP-LITH-003#03", "3. Symptoms"), c("SOP-LITH-003#05", "5. Diagnostic checks"),
                c("SOP-LITH-003#06", "6. Corrective procedure"), c("SOP-LITH-003#07", "7. Acceptance criteria"),
                c("SOP-LITH-003#08", "8. Parts")]
    out = [h["chunk_id"] for h in A.expand_top_sop(hits, sections)]
    assert out == ["SOP-LITH-003#03", "SOP-LITH-003#05", "SOP-LITH-003#06", "SOP-LITH-003#07", "SOP-LITH-004#05"]
    assert A.expand_top_sop(hits, []) == hits


def test_expansion_always_retrieves_acceptance_criteria(data):
    out, questions, truth = data
    plain = A.Assistant(baseline_search_fn(out), lambda m: "")
    expanded = A.Assistant(baseline_search_fn(out), lambda m: "", sections_fn=baseline_sections_fn(out))
    m0 = retrieval_metrics(questions, _preds(plain, questions), truth)
    m1 = retrieval_metrics(questions, _preds(expanded, questions), truth)
    assert m1["acceptance_criteria_retrieved"] >= m0["acceptance_criteria_retrieved"]
    assert m1["acceptance_criteria_retrieved"] >= 0.9
    print("\nBM25 plain:", json.dumps(m0), "\nBM25 + expansion:", json.dumps(m1))


# ------------------------------------------------------------------ citations and prompt
def test_citation_normalising():
    assert A.normalise_citations("cause 【S1】 and （E2） and [S3]") == "cause [S1] and [E2] and [S3]"
    assert A.citations("a 【S2】 b [E1] c (S10)") == ["E1", "S2", "S10"]


def test_prompt_allows_partial_answers():
    assert "not in the retrieved sources" in A.SYSTEM_PROMPT
    assert "ONLY when the sources do not address the main question" in A.SYSTEM_PROMPT


# ------------------------------------------------------------------ aggregate grading
def test_aggregate_correct_accepts_code_or_name():
    assert aggregate_correct("RC-CMP-01 (17 events)", "root_cause_name: Pad glazing or worn conditioner disk, cnt: 17")
    assert aggregate_correct("RC-CMP-01 (17 events)", "RC-CMP-01, 17")
    assert aggregate_correct("5", "5")
    assert aggregate_correct("5.4 hours", "avg_downtime_hours: 5.4")
    assert not aggregate_correct("5", "15")
    assert not aggregate_correct("RC-CMP-01 (17 events)", "RC-CMP-02")


# ------------------------------------------------------------------ judge
def test_judge_parsing():
    j = parse_judgement('```json\n{"covered": [true, false, true], "grounded": true, "unsupported_claims": [], "reason": "ok"}\n```', 3)
    assert j["coverage"] == 0.667 and j["grounded"] is True and j["judge_error"] is None
    short = parse_judgement('Here: {"covered": [true], "grounded": false, "unsupported_claims": ["x"]}', 2)
    assert short["coverage"] == 0.5 and short["grounded"] is False
    bad = parse_judgement("I think it is fine", 2)
    assert bad["coverage"] is None and bad["judge_error"]


def test_judge_messages_and_metrics():
    msgs = build_judge_messages("q?", ["point a", "point b"], "[S1] text", "answer [S1]")
    assert "1. point a" in msgs[0]["content"] and "[S1] text" in msgs[0]["content"]
    m = judge_metrics([
        {"type": "procedure", "coverage": 1.0, "grounded": True},
        {"type": "troubleshooting", "coverage": 0.5, "grounded": False},
        {"type": "troubleshooting", "coverage": None, "grounded": None, "judge_error": "x"},
    ])
    assert m == {"answer_coverage": 0.75, "groundedness_rate": 0.5, "judge_errors": 1,
                 "answer_coverage_procedure": 1.0, "answer_coverage_troubleshooting": 0.5}


# ------------------------------------------------------------------ Databricks backends with fakes
def test_backends_with_fakes(monkeypatch):
    from fabrag.backends import make_llm_fn, make_search_fn

    calls = []

    class FakeIndex:
        def similarity_search(self, **kw):
            calls.append(kw)
            return {"manifest": {"columns": [{"name": "chunk_id"}, {"name": "score"}]},
                    "result": {"data_array": [["SOP-ETCH-003#07", 0.9]]}}

    class FakeClient:
        def get_index(self, endpoint_name, index_name):
            return FakeIndex()

    search = make_search_fn(FakeClient(), "ep", {"sop": "c.s.idx_sop", "events": "c.s.idx_ev"}, "HYBRID")
    assert search("sop", "q", {"module_code": ["ETCH", "ANY"]}, 4) == [{"chunk_id": "SOP-ETCH-003#07", "score": 0.9}]
    assert calls[0]["query_type"] == "HYBRID" and calls[0]["num_results"] == 4 and "reranker" not in calls[0]

    class FakeApi:
        n = 0

        def do(self, method, path, body):
            FakeApi.n += 1
            if FakeApi.n == 1:
                raise RuntimeError("429 rate limited")
            return {"choices": [{"message": {"content": "ok [S1]"}}]}

    class FakeW:
        api_client = FakeApi()

    import fabrag.backends as B
    monkeypatch.setattr(B.time, "sleep", lambda s: None)  # no real waiting in tests
    assert make_llm_fn(FakeW(), "m")([{"role": "user", "content": "hi"}]) == "ok [S1]"


def test_full_run_logic_offline(data):
    """Mirror of notebook 04 section 2 with BM25 and fake models: catches bugs before Databricks."""
    from fabrag.judge import judge_answer, judge_metrics

    out, questions, truth = data

    def fake_llm(messages):
        if messages[0]["content"].startswith("You translate"):
            return "SELECT COUNT(*) FROM silver_ooc_events"
        if "ion implanter" in messages[-1]["content"]:
            return A.DECLINE_PREFIX + ": no implant SOP."
        return "**Likely cause** x 【S1】 **Similar past events** (E1)"

    fake_judge = lambda m: '{"covered": [true, false], "grounded": true, "unsupported_claims": []}'
    bot = A.Assistant(baseline_search_fn(out), fake_llm, sql_fn=lambda s: [{"n": 5}], sections_fn=baseline_sections_fn(out))
    preds, judged = [], []
    for q in questions:
        a = bot.ask(q["question"])
        if q["expected_behavior"] == "answer" and q["type"] != "aggregate" and not a.declined:
            j = judge_answer(fake_judge, q["question"], q["expected_answer_points"],
                             A.sources_text(a.sop_hits, a.event_hits), a.text)
            judged.append({"type": q["type"], **j})
        preds.append({"qid": q["qid"], "route": a.route, "declined": a.declined,
                      "retrieved_sop_ids": a.retrieved_sop_ids, "retrieved_event_ids": a.retrieved_event_ids,
                      "retrieved_chunk_ids": a.retrieved_chunk_ids if a.route == "retrieval" else []})
        if a.route == "retrieval" and not a.declined:
            assert A.citations(a.text) == ["E1", "S1"] and "[S1]" in a.text  # normalised
    m = {**retrieval_metrics(questions, preds, truth), **judge_metrics(judged)}
    assert m["questions_scored"] == 61 and m["routing_accuracy"] == 1.0
    assert m["acceptance_criteria_retrieved"] == 1.0
    assert m["groundedness_rate"] == 1.0 and m["judge_errors"] == 0


def test_judge_salvages_truncated_reply():
    from fabrag.judge import parse_judgement
    j = parse_judgement('{"covered": [true, true, false], "grounded": true', 3)
    assert j["coverage"] == 0.667 and j["grounded"] is True and j["judge_error"] is None
    assert parse_judgement("", 3)["judge_error"].startswith("unparseable")


def test_history_questions_get_deeper_event_search():
    from fabrag.assistant import Assistant
    calls = []
    def search(index, q, f, k):
        calls.append((index, k))
        return []
    bot = Assistant(search, lambda m: "x")
    bot.retrieve("Has CMP-01 had pad glazing before, and what fixed it?")
    bot.retrieve("Dishing is going up on CMP-03. Why?")
    assert ("events", 10) in calls and ("events", 5) in calls


def test_judge_sees_fab_policy():
    from fabrag.assistant import FAB_POLICY, SYSTEM_PROMPT
    from fabrag.judge import build_judge_messages
    msg = build_judge_messages("q", ["p"], "src", "a")[0]["content"]
    assert FAB_POLICY in msg and FAB_POLICY in SYSTEM_PROMPT
