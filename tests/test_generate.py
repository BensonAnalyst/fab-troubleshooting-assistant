import csv
import hashlib
import json
import re
from pathlib import Path

import pytest

from fabrag.generate import generate
from fabrag.knowledge import ROOT_CAUSES

# Real company and product names that must never appear in the synthetic data.
FORBIDDEN = ["micron", "stmicro", "hewlett", "applied materials", "lam research", "tokyo electron",
             "asml", "kla", "ebara", "screen semiconductor", "kokusai"]


@pytest.fixture(scope="module")
def data(tmp_path_factory):
    out = tmp_path_factory.mktemp("data")
    summary = generate(out, seed=42, n_events=450)
    return out, summary


def _rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _digest(folder):
    h = hashlib.sha256()
    for p in sorted(Path(folder).rglob("*")):
        if p.is_file():
            h.update(p.relative_to(folder).as_posix().encode())
            h.update(p.read_bytes())
    return h.hexdigest()


def test_summary_counts(data):
    _, s = data
    assert s["ooc_events"] == 450
    assert s["sops"] == len(ROOT_CAUSES) + 1
    assert s["eval_questions"] >= 45


def test_deterministic(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    generate(a, seed=7, n_events=100)
    generate(b, seed=7, n_events=100)
    assert _digest(a) == _digest(b)


def test_referential_integrity(data):
    out, _ = data
    tools = {r["tool_id"] for r in _rows(out / "raw" / "tools.csv")}
    codes = {r["root_cause_code"] for r in _rows(out / "raw" / "root_causes.csv")}
    events = _rows(out / "raw" / "ooc_events.csv")
    event_ids = {e["event_id"] for e in events}
    assert len(event_ids) == len(events)
    assert {e["tool_id"] for e in events} <= tools
    assert {e["root_cause_code"] for e in events if e["root_cause_code"]} <= codes
    for m in _rows(out / "raw" / "maintenance_logs.csv"):
        assert m["tool_id"] in tools
        assert not m["linked_event_id"] or m["linked_event_id"] in event_ids


def test_eval_references_exist(data):
    out, _ = data
    sops = {p.stem for p in (out / "sops").glob("*.md")}
    event_ids = {e["event_id"] for e in _rows(out / "raw" / "ooc_events.csv")}
    truth = {r["event_id"]: r["true_root_cause"] for r in _rows(out / "ground_truth" / "ooc_ground_truth.csv")}
    questions = [json.loads(line) for line in (out / "eval" / "eval_questions.jsonl").read_text().splitlines()]
    assert {q["type"] for q in questions} == {"troubleshooting", "procedure", "history", "aggregate", "unanswerable"}
    for q in questions:
        assert set(q["expected_sop_ids"]) <= sops, q["qid"]
        assert set(q["relevant_event_ids"]) <= event_ids, q["qid"]
        if q["type"] in ("troubleshooting", "history"):
            assert q["relevant_event_ids"], q["qid"]
            assert all(truth[e] == q["expected_root_cause"] for e in q["relevant_event_ids"]), q["qid"]


def test_realistic_mix(data):
    out, _ = data
    truth = _rows(out / "ground_truth" / "ooc_ground_truth.csv")
    met = sum(r["true_root_cause"] == "RC-MET-01" for r in truth) / len(truth)
    low = sum(r["low_quality_note"] == "True" for r in truth) / len(truth)
    assert 0.06 <= met <= 0.14  # SOP-GEN-001 says "around 1 in 10" are metrology false alarms
    assert 0.05 <= low <= 0.14
    assert {r["true_root_cause"] for r in truth} == {rc["rc_id"] for rc in ROOT_CAUSES}


def test_no_template_leftovers_or_real_names(data):
    out, _ = data
    for p in list((out / "raw").glob("*.csv")) + list((out / "sops").glob("*.md")):
        text = p.read_text(encoding="utf-8")
        assert not re.search(r"\{[a-z_]+\}", text), p.name
        lower = text.lower()
        for name in FORBIDDEN:
            assert not re.search(rf"\b{re.escape(name)}\b", lower), f"{name} in {p.name}"
