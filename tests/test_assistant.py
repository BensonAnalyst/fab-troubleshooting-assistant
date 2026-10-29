import csv
import json

import pytest

from fabrag import assistant as A
from fabrag.baseline import baseline_search_fn, load_event_chunks, load_sop_chunks
from fabrag.evaluate import retrieval_metrics
from fabrag.generate import generate


@pytest.fixture(scope="module")
def data(tmp_path_factory):
    out = tmp_path_factory.mktemp("data")
    generate(out, seed=42, n_events=450)
    questions = [json.loads(line) for line in (out / "eval" / "eval_questions.jsonl").read_text().splitlines()]
    with open(out / "ground_truth" / "ooc_ground_truth.csv", newline="") as f:
        truth = {r["event_id"]: r["true_root_cause"] for r in csv.DictReader(f)}
    return out, questions, truth


# ------------------------------------------------------------------ routing and filters
def test_routing_matches_eval_set(data):
    _, questions, _ = data
    for q in questions:
        expected = "sql" if q["expected_behavior"] == "route_to_sql" else "retrieval"
        assert A.route(q["question"]) == expected, q["question"]


def test_filters():
    sop_f, ev_f = A.search_filters("Has ETCH-03 had a helium backside leak before, and what fixed it?")
    assert sop_f == {"module_code": ["ETCH", "ANY"]} and ev_f == {"tool_id": "ETCH-03"}
    sop_f, ev_f = A.search_filters("Removal rate on cmp-02 keeps falling and the pad looks shiny.")
    assert sop_f == {"module_code": ["CMP", "ANY"]} and ev_f == {"module": "CMP"}
    assert A.search_filters("What PPE do I need for a wet bench bath change?") == (None, None)


# ------------------------------------------------------------------ SQL guard
@pytest.mark.parametrize("sql", [
    "SELECT COUNT(*) FROM silver_ooc_events WHERE tool_id = 'CMP-02'",
    "select root_cause_code, count(*) n from workspace.fab_rag.silver_ooc_events group by 1",
    "SELECT COUNT(*) FROM silver_ooc_events WHERE EXTRACT(YEAR FROM event_ts) = 2025",
    "WITH x AS (SELECT * FROM silver_ooc_events) SELECT COUNT(*) FROM x WHERE 1=1".replace("FROM x", "FROM silver_ooc_events"),
])
def test_sql_guard_allows_reads(sql):
    assert A.check_sql(sql) == sql


@pytest.mark.parametrize("sql", [
    "DROP TABLE silver_ooc_events",
    "SELECT * FROM silver_ooc_events; DELETE FROM silver_ooc_events",
    "SELECT * FROM ooc_ground_truth",
    "SELECT * FROM silver_ooc_events JOIN ooc_ground_truth USING (event_id)",
    "UPDATE silver_ooc_events SET downtime_hours = 0",
])
def test_sql_guard_rejects(sql):
    with pytest.raises(ValueError):
        A.check_sql(sql)


def test_clean_sql_strips_fences():
    assert A.clean_sql("```sql\nSELECT 1 FROM silver_ooc_events;\n```") == "SELECT 1 FROM silver_ooc_events"


# ------------------------------------------------------------------ parsing and prompting
def test_parse_hits():
    resp = {"manifest": {"columns": [{"name": "chunk_id"}, {"name": "sop_id"}, {"name": "score"}]},
            "result": {"data_array": [["SOP-ETCH-002#07", "SOP-ETCH-002", 0.91]]}}
    assert A.parse_hits(resp) == [{"chunk_id": "SOP-ETCH-002#07", "sop_id": "SOP-ETCH-002", "score": 0.91}]
    assert A.parse_hits({"manifest": {"columns": []}, "result": {}}) == []


def test_messages_number_sources_and_state_rules():
    sop = [{"chunk_id": "SOP-ETCH-002#07", "sop_id": "SOP-ETCH-002", "retrieval_text": "leak-up below 2 mTorr/min"}]
    ev = [{"event_id": "OOC-00004", "retrieval_text": "Past OOC event OOC-00004 ..."}]
    msgs = A.build_messages("q?", sop, ev)
    assert msgs[0]["role"] == "system" and A.DECLINE_PREFIX in msgs[0]["content"]
    assert "[S1] SOP-ETCH-002#07" in msgs[1]["content"] and "[E1] Past OOC event OOC-00004" in msgs[1]["content"]
    assert A.citations("Replace the ring [S1][S2]. Seen before [E1], [S1].") == ["E1", "S1", "S2"]


# ------------------------------------------------------------------ end to end with fakes
def _fake_llm(messages):
    if messages[0]["content"].startswith("You translate a question"):
        return "```sql\nSELECT COUNT(*) AS n FROM silver_ooc_events WHERE tool_id = 'CMP-02';\n```"
    if "ion implanter" in messages[1]["content"]:
        return A.DECLINE_PREFIX + ": there is no implant SOP."
    return "**Likely cause** Focus ring erosion [S1]. **Similar past events** [E1]."


def test_assistant_end_to_end(data):
    out, _, _ = data
    seen_sql = []
    bot = A.Assistant(baseline_search_fn(out), _fake_llm, sql_fn=lambda s: seen_sql.append(s) or [{"n": 5}],
                      table_name="workspace.fab_rag.silver_ooc_events")

    a = bot.ask("The 49-point map on ETCH-05 shows the edge etching faster than the centre. Likely cause?")
    assert a.route == "retrieval" and not a.declined
    assert a.sop_hits and all(h["module_code"] in ("ETCH", "ANY") for h in a.sop_hits)
    assert all(h["module"] == "ETCH" for h in a.event_hits)
    assert A.citations(a.text) == ["E1", "S1"]

    s = bot.ask("How many OOC events did CMP-02 have in Q2 2025?")
    assert s.route == "sql" and s.text == "5"
    assert seen_sql == ["SELECT COUNT(*) AS n FROM workspace.fab_rag.silver_ooc_events WHERE tool_id = 'CMP-02'"]

    d = bot.ask("How do I tune beam current on the ion implanter?")
    assert d.declined


def test_rejected_sql_declines(data):
    out, _, _ = data
    bot = A.Assistant(baseline_search_fn(out), lambda m: "DELETE FROM silver_ooc_events", sql_fn=lambda s: [])
    a = bot.ask("How many OOC events were there in total?")
    assert a.declined and a.sql_rows is None


# ------------------------------------------------------------------ baseline metrics
def test_bm25_baseline_metrics(data):
    out, questions, truth = data
    bot = A.Assistant(baseline_search_fn(out), _fake_llm, sql_fn=lambda s: [{"n": 0}])
    preds = []
    for q in questions:
        a = bot.ask(q["question"])
        preds.append({"qid": q["qid"], "route": a.route, "retrieved_sop_ids": a.retrieved_sop_ids,
                      "retrieved_event_ids": a.retrieved_event_ids, "declined": a.declined})
    m = retrieval_metrics(questions, preds, truth)
    assert m["questions_scored"] == len(questions)
    assert m["routing_accuracy"] == 1.0
    # A keyword baseline should already find the right SOP for most questions; AI Search must beat it.
    assert m["sop_hit_rate_at_k"] >= 0.6
    print("\nBM25 baseline:", json.dumps(m))


def test_baseline_chunks_match_gold_counts(data):
    out, _, _ = data
    assert len(load_sop_chunks(out / "sops")) == 22 * 11 + 5
    events = load_event_chunks(out / "raw" / "ooc_events.csv", out / "raw" / "root_causes.csv")
    with open(out / "ground_truth" / "ooc_ground_truth.csv", newline="") as f:
        assert len(events) == sum(r["low_quality_note"] == "False" for r in csv.DictReader(f))


def test_chat_text_handles_reasoning_blocks():
    plain = {"choices": [{"message": {"content": "Answer [S1]"}}]}
    blocks = {"choices": [{"message": {"content": [
        {"type": "reasoning", "summary": [{"type": "summary_text", "text": "thinking..."}]},
        {"type": "text", "text": "Answer [S1]"}]}}]}
    assert A.chat_text(plain) == A.chat_text(blocks) == "Answer [S1]"
