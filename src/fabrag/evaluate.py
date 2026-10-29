"""Deterministic metrics over the evaluation set: routing, retrieval and declining.

Answer correctness and groundedness need an LLM judge (Week 3, MLflow); these metrics do not.

`predictions` is a list of dicts with: qid, route, retrieved_sop_ids, retrieved_event_ids, declined.
`truth_rc` maps event_id -> true root cause (from ooc_ground_truth, used for scoring only).
"""


def _mean(xs):
    xs = list(xs)
    return round(sum(xs) / len(xs), 3) if xs else None


def retrieval_metrics(questions: list, predictions: list, truth_rc: dict) -> dict:
    by_id = {p["qid"]: p for p in predictions}
    rows = [(q, by_id[q["qid"]]) for q in questions if q["qid"] in by_id]

    route_ok = [(p["route"] == "sql") == (q["expected_behavior"] == "route_to_sql") for q, p in rows]

    sop_qs = [(q, p) for q, p in rows if q["expected_sop_ids"] and q["expected_behavior"] == "answer"]
    sop_hit = [bool(set(q["expected_sop_ids"]) & set(p["retrieved_sop_ids"])) for q, p in sop_qs]
    sop_top1 = [bool(p["retrieved_sop_ids"]) and p["retrieved_sop_ids"][0] in q["expected_sop_ids"] for q, p in sop_qs]

    def rr(q, p):
        for rank, s in enumerate(p["retrieved_sop_ids"], 1):
            if s in q["expected_sop_ids"]:
                return 1 / rank
        return 0.0

    ev_qs = [(q, p) for q, p in rows if q["type"] in ("troubleshooting", "history") and p["retrieved_event_ids"]]
    ev_precision = [
        sum(truth_rc.get(e) == q["expected_root_cause"] for e in p["retrieved_event_ids"]) / len(p["retrieved_event_ids"])
        for q, p in ev_qs
    ]
    hist = [(q, p) for q, p in rows if q["type"] == "history"]
    hist_recall = [len(set(q["relevant_event_ids"]) & set(p["retrieved_event_ids"])) / len(q["relevant_event_ids"])
                   for q, p in hist if q["relevant_event_ids"]]

    unans = [p["declined"] for q, p in rows if q["expected_behavior"] == "decline"]
    false_decline = [p["declined"] for q, p in rows if q["expected_behavior"] == "answer"]

    return {
        "questions_scored": len(rows),
        "routing_accuracy": _mean(route_ok),
        "sop_hit_rate_at_k": _mean(sop_hit),
        "sop_top1_accuracy": _mean(sop_top1),
        "sop_mrr": _mean(rr(q, p) for q, p in sop_qs),
        "event_root_cause_precision_at_k": _mean(ev_precision),
        "history_event_recall": _mean(hist_recall),
        "decline_rate_unanswerable": _mean(unans),
        "false_decline_rate_answerable": _mean(false_decline),
    }
