"""Deterministic metrics over the evaluation set: routing, retrieval and declining.

`predictions` is a list of dicts with: qid, route, retrieved_sop_ids, retrieved_event_ids, declined,
and (from Week 3) retrieved_chunk_ids.
`truth_rc` maps event_id -> true root cause (from ooc_ground_truth, used for scoring only).

Week 2 metrics are computed on the original 49 questions (types below) so runs stay comparable.
The Week 3 paraphrased questions are scored separately with the `paraphrase_` prefix.
"""

ORIGINAL_TYPES = ("troubleshooting", "procedure", "history", "aggregate", "unanswerable")


def _mean(xs):
    xs = list(xs)
    return round(sum(xs) / len(xs), 3) if xs else None


def _sop_scores(pairs):
    hit = [bool(set(q["expected_sop_ids"]) & set(p["retrieved_sop_ids"])) for q, p in pairs]
    top1 = [bool(p["retrieved_sop_ids"]) and p["retrieved_sop_ids"][0] in q["expected_sop_ids"] for q, p in pairs]

    def rr(q, p):
        for rank, s in enumerate(p["retrieved_sop_ids"], 1):
            if s in q["expected_sop_ids"]:
                return 1 / rank
        return 0.0

    return _mean(hit), _mean(top1), _mean(rr(q, p) for q, p in pairs)


def _chunk_hit(pairs):
    scored = [(q, p) for q, p in pairs if q.get("expected_chunk_ids") and p.get("retrieved_chunk_ids") is not None]
    return _mean(bool(set(q["expected_chunk_ids"]) & set(p["retrieved_chunk_ids"])) for q, p in scored)


def _event_precision(pairs, truth_rc):
    scored = [(q, p) for q, p in pairs if p["retrieved_event_ids"]]
    return _mean(sum(truth_rc.get(e) == q["expected_root_cause"] for e in p["retrieved_event_ids"])
                 / len(p["retrieved_event_ids"]) for q, p in scored)


def retrieval_metrics(questions: list, predictions: list, truth_rc: dict) -> dict:
    by_id = {p["qid"]: p for p in predictions}
    all_rows = [(q, by_id[q["qid"]]) for q in questions if q["qid"] in by_id]
    rows = [(q, p) for q, p in all_rows if q["type"] in ORIGINAL_TYPES]
    para = [(q, p) for q, p in all_rows if q["type"] == "paraphrase"]

    route_ok = [(p["route"] == "sql") == (q["expected_behavior"] == "route_to_sql") for q, p in all_rows]
    sop_qs = [(q, p) for q, p in rows if q["expected_sop_ids"] and q["expected_behavior"] == "answer"]
    hit, top1, mrr = _sop_scores(sop_qs)

    ev_qs = [(q, p) for q, p in rows if q["type"] in ("troubleshooting", "history")]
    hist = [(q, p) for q, p in rows if q["type"] == "history" and q["relevant_event_ids"]]
    hist_recall = [len(set(q["relevant_event_ids"]) & set(p["retrieved_event_ids"])) / len(q["relevant_event_ids"])
                   for q, p in hist]

    unans = [p["declined"] for q, p in all_rows if q["expected_behavior"] == "decline"]
    false_decline = [p["declined"] for q, p in rows if q["expected_behavior"] == "answer"]

    p_hit, p_top1, _ = _sop_scores(para)
    return {
        "questions_scored": len(all_rows),
        "routing_accuracy": _mean(route_ok),
        "sop_hit_rate_at_k": hit,
        "sop_top1_accuracy": top1,
        "sop_mrr": mrr,
        "event_root_cause_precision_at_k": _event_precision(ev_qs, truth_rc),
        "history_event_recall": _mean(hist_recall),
        "procedure_section_hit_rate": _chunk_hit([(q, p) for q, p in rows if q["type"] == "procedure"]),
        "acceptance_criteria_retrieved": _chunk_hit([(q, p) for q, p in rows if q["type"] == "troubleshooting"]),
        "decline_rate_unanswerable": _mean(unans),
        "false_decline_rate_answerable": _mean(false_decline),
        "paraphrase_sop_hit_rate_at_k": p_hit,
        "paraphrase_sop_top1_accuracy": p_top1,
        "paraphrase_event_root_cause_precision_at_k": _event_precision(para, truth_rc),
        "paraphrase_acceptance_criteria_retrieved": _chunk_hit(para),
        "paraphrase_false_decline_rate": _mean(p["declined"] for q, p in para) if para else None,
    }


def aggregate_correct(expected: str, answer: str) -> bool:
    """Counting questions: the first token of the expected answer (a number or a root cause code)
    must appear in the answer. A root cause can also be given by its name."""
    import re

    from .knowledge import root_cause_by_id

    answer = answer or ""
    key = expected.split()[0]
    if re.search(rf"(?<![\w.]){re.escape(key)}(?![\w.])", answer):
        return True
    rc = root_cause_by_id().get(key)
    return bool(rc) and rc["name"].lower() in answer.lower()
