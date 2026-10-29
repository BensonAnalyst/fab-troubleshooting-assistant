"""Generate the synthetic fab troubleshooting dataset.

Outputs (under --out, default ./data):
    raw/tools.csv               tool master
    raw/root_causes.csv         root cause taxonomy (code -> name -> SOP)
    raw/ooc_events.csv          SPC out-of-control events with engineer closure notes
    raw/maintenance_logs.csv    scheduled PMs and unscheduled repairs linked to OOC events
    sops/*.md                   SOP library (the documents the assistant retrieves from)
    eval/eval_questions.jsonl   evaluation set with ground truth

Usage:
    python -m fabrag.generate --out data --seed 42 --n-events 450

Uses only the Python standard library, so it runs anywhere (laptop, Databricks, CI).
"""

import argparse
import csv
import json
import random
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

from . import eval_spec
from .knowledge import (ENGINEERS, MODULES, PARAMETERS, ROOT_CAUSES, SPC_RULES,
                        TECHNICIANS, VAGUE_NOTES)
from .sops import render_all

START = datetime(2025, 1, 1)
END = datetime(2026, 9, 30, 23, 59)

SHORTHAND = [("wafers", "wfrs"), ("wafer", "wfr"), ("replaced", "repl"), ("checked", "chk"),
             ("chamber", "chmbr"), ("monitors", "mons"), ("requalified", "requal'd"), ("with", "w/")]


# ---------------------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------------------
def build_tools(rng):
    tools = []
    for module, m in MODULES.items():
        for i in range(1, m["tools"] + 1):
            tools.append({
                "tool_id": f"{module}-{i:02d}",
                "module": module,
                "module_name": m["name"],
                "platform": m["platform"],
                "chambers": "|".join(c for c in m["chambers"] if c),
                "install_year": rng.choice([2017, 2018, 2019, 2020, 2021, 2022]),
            })
    return tools


# ---------------------------------------------------------------------------------------
# OOC events
# ---------------------------------------------------------------------------------------
def _candidates(module):
    rcs = [rc for rc in ROOT_CAUSES if rc["module"] in (module, "ANY")]
    return rcs, [rc["weight"] for rc in rcs]


def _fmt(value, sigma):
    if sigma < 0.01:
        return f"{value:.3f}"
    if sigma < 1:
        return f"{value:.2f}"
    return f"{value:.0f}"


def _slot_values(rng, rc, value_str):
    rfh = {"RC-ETCH-01": (1150, 1380), "RC-ETCH-02": (770, 880), "RC-CVD-01": (590, 700)}.get(rc["rc_id"], (300, 900))
    pct = (5, 14) if rc["rc_id"] == "RC-CVD-04" else (2, 7)
    return {"rfh": rng.randint(*rfh), "n": rng.randint(3, 8), "pct": rng.randint(*pct), "val": value_str}


def _shorthand(rng, text):
    if rng.random() < 0.35:
        for full, short in SHORTHAND:
            text = text.replace(full, short)
    if rng.random() < 0.25:
        text = text.lower()
    return text


def _closure_note(rng, rc, tool_id, chamber, param, value_str, unit, rule, lot_id):
    where = f"{tool_id}{('-' + chamber) if chamber else ''}"
    rule_short = rule.split(":")[0]
    openers = [
        f"{param['name']} OOC on {where} ({rule_short}), value {value_str} {unit}.".replace("  ", " "),
        f"{where}: {param['id']} out at {value_str} {unit}, {rule_short}.".replace("  ", " "),
        f"OOC {param['id']} {where} lot {lot_id}.",
    ]
    slots = _slot_values(rng, rc, value_str)
    # Findings and actions are index-aligned so each note tells one consistent story.
    i = rng.randrange(len(rc["findings"]))
    finding = rc["findings"][i].format(**slots)
    action = rc["actions"][i].format(**slots)
    closer = rng.choice(["", f" Lot {lot_id} released.", " Held lots dispositioned.", " Will monitor next 3 days.", ""])
    note = f"{rng.choice(openers)} {finding[0].upper() + finding[1:]}. {action[0].upper() + action[1:]}.{closer}"
    return _shorthand(rng, note)


def build_events(rng, tools, n_events):
    tool_weights = [1.0 for _ in tools]
    params_by_module = {m: [{"id": p[0], "name": p[1], "unit": p[2], "base": p[3], "sigma": p[4]} for p in ps]
                        for m, ps in PARAMETERS.items()}
    span = (END - START).total_seconds()
    events = []
    for _ in range(n_events):
        tool = rng.choices(tools, weights=tool_weights)[0]
        module = tool["module"]
        rcs, weights = _candidates(module)
        rc = rng.choices(rcs, weights=weights)[0]
        chamber = rng.choice(tool["chambers"].split("|")) if tool["chambers"] else ""

        module_params = params_by_module[module]
        if rc["params"]:
            pid, direction = rng.choice(rc["params"])
            param = next(p for p in module_params if p["id"] == pid)
        else:
            param, direction = rng.choice(module_params), rng.choice([-1, 1])
        if param["id"] in ("particle_adders", "scratch_count", "watermark_defects", "reflected_power", "focus_error"):
            direction = 1  # these only go out of control upwards
        # A metrology false alarm is a single bad reading, so it only ever trips Rule 1.
        rule = SPC_RULES[0] if rc["rc_id"] == "RC-MET-01" else rng.choices(SPC_RULES, weights=[4, 2, 2, 2])[0]
        k = rng.uniform(3.1, 5.5) if rule.startswith("Rule 1") else rng.uniform(2.1, 3.0)
        value = param["base"] + direction * k * param["sigma"]
        if param["id"] in ("particle_adders", "scratch_count", "watermark_defects"):
            value = round(value + rng.uniform(2, 20))
        value_str = str(int(round(value))) if param["unit"] == "count" else _fmt(value, param["sigma"])

        event_ts = START + timedelta(seconds=rng.uniform(0, span))
        lot_id = f"L{event_ts:%y}{rng.randint(10000, 99999)}"
        engineer = rng.choice(ENGINEERS)
        low_quality = rng.random() < 0.09
        if low_quality:
            note = rng.choice(VAGUE_NOTES)
            rc_code = rc["rc_id"] if rng.random() < 0.3 else ""
        else:
            note = _closure_note(rng, rc, tool["tool_id"], chamber, param, value_str, param["unit"], rule, lot_id)
            rc_code = rc["rc_id"] if rng.random() < 0.9 else ""
        lo, hi = rc["downtime"]
        downtime = round(rng.uniform(lo, hi), 1)
        closed_ts = event_ts + timedelta(hours=downtime + rng.uniform(0.3, 2.0))
        events.append({
            "event_id": "",  # assigned after sorting
            "event_ts": event_ts.strftime("%Y-%m-%d %H:%M:%S"),
            "tool_id": tool["tool_id"],
            "module": module,
            "chamber": chamber,
            "parameter": param["id"],
            "parameter_name": param["name"],
            "unit": param["unit"],
            "value": value_str,
            "spc_rule": rule,
            "lot_id": lot_id,
            "engineer": engineer,
            "root_cause_code": rc_code,
            "closure_note": note,
            "downtime_hours": downtime,
            "closed_ts": closed_ts.strftime("%Y-%m-%d %H:%M:%S"),
            "_true_rc": rc["rc_id"],  # ground truth, written to a separate file
            "_low_quality": low_quality,
        })
    events.sort(key=lambda e: e["event_ts"])
    for i, e in enumerate(events, 1):
        e["event_id"] = f"OOC-{i:05d}"
    return events


# ---------------------------------------------------------------------------------------
# Maintenance logs
# ---------------------------------------------------------------------------------------
def build_maintenance(rng, tools, events, rc_by_id):
    logs = []
    for e in events:
        rc = rc_by_id[e["_true_rc"]]
        if rc["rc_id"] == "RC-MET-01" or rng.random() > 0.75:
            continue
        start = datetime.strptime(e["event_ts"], "%Y-%m-%d %H:%M:%S") + timedelta(minutes=rng.randint(20, 120))
        parts = rng.sample(rc["parts"], k=min(len(rc["parts"]), rng.choice([0, 1, 1, 2]))) if rc["parts"] else []
        step = rng.choice(rc["fix"][:2])
        logs.append({
            "maint_id": "",
            "tool_id": e["tool_id"],
            "chamber": e["chamber"],
            "start_ts": start.strftime("%Y-%m-%d %H:%M:%S"),
            "maint_type": "Unscheduled repair",
            "description": f"OOC response for {e['parameter']}. {step}",
            "parts_replaced": "; ".join(parts),
            "linked_event_id": e["event_id"],
            "technician": rng.choice(TECHNICIANS),
            "duration_hours": round(max(0.5, e["downtime_hours"] * rng.uniform(0.6, 0.95)), 1),
        })
    pm_items = {
        "ETCH": "Monthly PM: chamber inspection, He leak-up test, RF connector check, MFC verification.",
        "CVD": "Monthly PM: showerhead inspection, thermocouple check, ampoule level check, particle monitor.",
        "CMP": "Monthly PM: conditioner disk check, POU filter change, head life counter review, endpoint cal check.",
        "LITH": "Monthly PM: stage and alignment calibration, chuck inspection, dose calibration, track nozzle clean.",
        "WET": "Monthly PM: recirc filter dP check, pump inspection, dryer IPA/N2 flow check, DI resistivity check.",
    }
    for t in tools:
        day = START + timedelta(days=rng.randint(0, 25))
        while day < END:
            logs.append({
                "maint_id": "",
                "tool_id": t["tool_id"],
                "chamber": "",
                "start_ts": day.replace(hour=rng.choice([8, 9, 13, 20])).strftime("%Y-%m-%d %H:%M:%S"),
                "maint_type": "Scheduled PM",
                "description": pm_items[t["module"]],
                "parts_replaced": "",
                "linked_event_id": "",
                "technician": rng.choice(TECHNICIANS),
                "duration_hours": round(rng.uniform(3, 6), 1),
            })
            day += timedelta(days=rng.randint(27, 33))
    logs.sort(key=lambda r: r["start_ts"])
    for i, r in enumerate(logs, 1):
        r["maint_id"] = f"MNT-{i:05d}"
    return logs


# ---------------------------------------------------------------------------------------
# Evaluation set
# ---------------------------------------------------------------------------------------
def build_eval(rng, tools, events, rc_by_id):
    tools_by_module = defaultdict(list)
    for t in tools:
        tools_by_module[t["module"]].append(t["tool_id"])
    good = [e for e in events if not e["_low_quality"]]
    questions = []

    for rc_id, (template, points) in eval_spec.TROUBLESHOOTING.items():
        rc = rc_by_id[rc_id]
        module = rc["module"] if rc["module"] != "ANY" else eval_spec.CROSS_MODULE_TOOL[rc_id]
        tool = rng.choice(tools_by_module[module])
        examples = [e["event_id"] for e in good if e["_true_rc"] == rc_id][:5]
        questions.append({
            "qid": "", "type": "troubleshooting", "question": template.format(tool=tool),
            "expected_behavior": "answer", "expected_root_cause": rc_id, "expected_sop_ids": [rc["sop_id"]],
            "relevant_event_ids": examples, "expected_answer_points": points,
        })

    for question, sop_id, points in eval_spec.PROCEDURE:
        questions.append({
            "qid": "", "type": "procedure", "question": question, "expected_behavior": "answer",
            "expected_root_cause": None, "expected_sop_ids": [sop_id], "relevant_event_ids": [],
            "expected_answer_points": points,
        })

    pairs = Counter((e["tool_id"], e["_true_rc"]) for e in good if e["_true_rc"] in eval_spec.RC_SHORT)
    eligible = sorted(p for p, n in pairs.items() if n >= 2)
    for tool_id, rc_id in rng.sample(eligible, k=min(6, len(eligible))):
        ids = [e["event_id"] for e in good if e["tool_id"] == tool_id and e["_true_rc"] == rc_id]
        questions.append({
            "qid": "", "type": "history",
            "question": f"Has {tool_id} had {eval_spec.RC_SHORT[rc_id]} before, and what fixed it?",
            "expected_behavior": "answer", "expected_root_cause": rc_id, "expected_sop_ids": [rc_by_id[rc_id]["sop_id"]],
            "relevant_event_ids": ids,
            "expected_answer_points": [f"Yes: {len(ids)} past events ({', '.join(ids)})",
                                       "Summarise the corrective actions from those closure notes"],
        })

    # Aggregate questions: retrieval is the wrong tool, a SQL query over the events table is right.
    # Answers use only what the assistant can see (engineer-entered codes in silver_ooc_events),
    # never the hidden ground truth.
    q2 = [e for e in events if e["tool_id"] == "CMP-02" and "2025-04-01" <= e["event_ts"] < "2025-07-01"]
    etch02 = [e["downtime_hours"] for e in events if e["root_cause_code"] == "RC-ETCH-02"]
    cmp25 = Counter(e["root_cause_code"] for e in events
                    if e["module"] == "CMP" and e["event_ts"].startswith("2025") and e["root_cause_code"])
    top_rc, top_n = cmp25.most_common(1)[0]
    aggregates = [
        ("How many OOC events did CMP-02 have in Q2 2025?", str(len(q2)),
         "SELECT COUNT(*) FROM silver_ooc_events WHERE tool_id = 'CMP-02' "
         "AND event_ts >= '2025-04-01' AND event_ts < '2025-07-01'"),
        ("What is the average downtime for focus ring erosion events?", f"{sum(etch02) / len(etch02):.1f} hours",
         "SELECT ROUND(AVG(downtime_hours), 1) FROM silver_ooc_events WHERE root_cause_code = 'RC-ETCH-02'"),
        ("What was the most common root cause on CMP tools in 2025?", f"{top_rc} ({top_n} events)",
         "SELECT root_cause_code, COUNT(*) AS n FROM silver_ooc_events WHERE module = 'CMP' "
         "AND year(event_ts) = 2025 AND root_cause_code IS NOT NULL GROUP BY 1 ORDER BY n DESC LIMIT 1"),
    ]
    for question, answer, sql in aggregates:
        questions.append({
            "qid": "", "type": "aggregate", "question": question, "expected_behavior": "route_to_sql",
            "expected_root_cause": None, "expected_sop_ids": [], "relevant_event_ids": [],
            "expected_answer_points": [answer], "reference_sql": sql,
        })

    for question, reason in eval_spec.UNANSWERABLE:
        questions.append({
            "qid": "", "type": "unanswerable", "question": question, "expected_behavior": "decline",
            "expected_root_cause": None, "expected_sop_ids": [], "relevant_event_ids": [],
            "expected_answer_points": ["Says it cannot answer from the knowledge base and does not invent an answer"],
            "decline_reason": reason,
        })

    for i, q in enumerate(questions, 1):
        q["qid"] = f"Q{i:03d}"
    return questions


# ---------------------------------------------------------------------------------------
# Writers
# ---------------------------------------------------------------------------------------
def _write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def generate(out_dir, seed=42, n_events=450):
    rng = random.Random(seed)
    out = Path(out_dir)
    rc_by_id = {rc["rc_id"]: rc for rc in ROOT_CAUSES}

    tools = build_tools(rng)
    events = build_events(rng, tools, n_events)
    maint = build_maintenance(rng, tools, events, rc_by_id)
    questions = build_eval(rng, tools, events, rc_by_id)

    _write_csv(out / "raw" / "tools.csv", tools, list(tools[0].keys()))
    _write_csv(out / "raw" / "root_causes.csv",
               [{"root_cause_code": rc["rc_id"], "module": rc["module"], "root_cause_name": rc["name"], "sop_id": rc["sop_id"]}
                for rc in ROOT_CAUSES], ["root_cause_code", "module", "root_cause_name", "sop_id"])
    event_fields = [k for k in events[0] if not k.startswith("_")]
    _write_csv(out / "raw" / "ooc_events.csv", events, event_fields)
    _write_csv(out / "raw" / "maintenance_logs.csv", maint, list(maint[0].keys()))
    # Ground truth is kept apart from the raw events, as it would be in a real labelling exercise.
    _write_csv(out / "ground_truth" / "ooc_ground_truth.csv",
               [{"event_id": e["event_id"], "module": e["module"], "event_ts": e["event_ts"], "true_root_cause": e["_true_rc"],
                 "downtime_hours": e["downtime_hours"], "low_quality_note": e["_low_quality"]} for e in events],
               ["event_id", "module", "event_ts", "true_root_cause", "downtime_hours", "low_quality_note"])

    sop_dir = out / "sops"
    sop_dir.mkdir(parents=True, exist_ok=True)
    for name, text in render_all().items():
        (sop_dir / name).write_text(text, encoding="utf-8")

    eval_path = out / "eval" / "eval_questions.jsonl"
    eval_path.parent.mkdir(parents=True, exist_ok=True)
    with eval_path.open("w", encoding="utf-8") as f:
        for q in questions:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")

    return {"tools": len(tools), "ooc_events": len(events), "maintenance_logs": len(maint),
            "sops": len(render_all()), "eval_questions": len(questions)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="data")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--n-events", type=int, default=450)
    args = ap.parse_args()
    summary = generate(args.out, args.seed, args.n_events)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
