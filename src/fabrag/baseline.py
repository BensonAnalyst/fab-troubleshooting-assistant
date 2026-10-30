"""Keyword-only BM25 baseline over the same chunks the AI Search indexes use.

Pure Python, no Databricks needed. It gives a reference point: AI Search (embeddings + keywords)
has to beat this to justify itself. It also lets the tests run the whole assistant offline.
"""

import csv
import math
import re
from collections import Counter
from pathlib import Path

from .knowledge import VAGUE_NOTES
from .sops import LOW_VALUE_SECTION_PREFIXES

_TOKEN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
_STOP = set("a an and are as at be by did do does for from had has have how i in is it its of on or our "
            "should so the this to was we what when where which why with you your my me get getting keeps".split())


def tokenize(text: str) -> list:
    return [t for t in _TOKEN.findall(text.lower()) if t not in _STOP]


class BM25:
    def __init__(self, docs: list, text_key="retrieval_text", k1=1.5, b=0.75):
        self.docs, self.k1, self.b = docs, k1, b
        self.toks = [tokenize(d[text_key]) for d in docs]
        self.avgdl = sum(map(len, self.toks)) / max(1, len(self.toks))
        df = Counter(t for ts in self.toks for t in set(ts))
        n = len(docs)
        self.idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}
        self.tf = [Counter(ts) for ts in self.toks]

    def search(self, query: str, filters=None, k=5) -> list:
        q = tokenize(query)
        scored = []
        for d, tf, ts in zip(self.docs, self.tf, self.toks):
            if filters and not _match(d, filters):
                continue
            s = 0.0
            for t in q:
                if t in tf:
                    f = tf[t]
                    s += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * len(ts) / self.avgdl))
            if s > 0:
                scored.append((s, d))
        scored.sort(key=lambda x: -x[0])
        return [dict(d, score=round(s, 4)) for s, d in scored[:k]]


def _match(doc, filters):
    for col, val in filters.items():
        vals = val if isinstance(val, (list, tuple)) else [val]
        if doc.get(col) not in vals:
            return False
    return True


# ---------------------------------------------------------------------------------------
# Build the same Gold records as gold.py, from the files, without Spark
# ---------------------------------------------------------------------------------------
def load_sop_chunks(sop_dir, include_low_value=False) -> list:
    """Same chunks as gold_sop_chunks. include_low_value=True returns every section."""
    chunks = []
    for path in sorted(Path(sop_dir).glob("*.md")):
        text = path.read_text(encoding="utf-8")
        first, *parts = text.split("\n## ")
        m = re.match(r"^# (SOP-([A-Z]+)-\d{3}): (.*)$", first.split("\n")[0])
        sop_id, mod, title = m.group(1), m.group(2), m.group(3)
        module_code = mod if mod in ("ETCH", "CVD", "CMP", "LITH", "WET") else "ANY"
        for i, part in enumerate(parts, 1):
            section_title, _, body = part.partition("\n")
            body = body.strip()
            if not include_low_value and section_title.strip().startswith(LOW_VALUE_SECTION_PREFIXES):
                continue
            chunks.append({
                "chunk_id": f"{sop_id}#{i:02d}", "sop_id": sop_id, "sop_title": title,
                "section_title": section_title.strip(), "module_code": module_code,
                "retrieval_text": f"{sop_id} {title} - {section_title.strip()}\n{body}",
            })
    return chunks


def load_event_chunks(events_csv, root_causes_csv) -> list:
    with open(root_causes_csv, newline="", encoding="utf-8") as f:
        rc_names = {r["root_cause_code"]: r["root_cause_name"] for r in csv.DictReader(f)}
    vague = {v.lower() for v in VAGUE_NOTES}
    out = []
    with open(events_csv, newline="", encoding="utf-8") as f:
        for e in csv.DictReader(f):
            note = e["closure_note"].strip()
            if note.lower() in vague or len(note) < 30:
                continue
            code = e["root_cause_code"] or None
            rc = f"{code} {rc_names[code]}" if code else "not coded"
            chamber = f" chamber {e['chamber']}" if e["chamber"] else ""
            text = (f"Past OOC event {e['event_id']} on {e['tool_id']}{chamber} ({e['module']}) | Date: {e['event_ts'][:10]} | "
                    f"Symptom: {e['parameter_name']} = {e['value']} {e['unit']}, {e['spc_rule']} | Root cause: {rc} | "
                    f"Closure note: {note} | Downtime: {e['downtime_hours']} h")
            out.append({"event_id": e["event_id"], "tool_id": e["tool_id"], "module": e["module"],
                        "event_date": e["event_ts"][:10], "root_cause_code": code, "retrieval_text": text})
    return out


def baseline_sections_fn(data_dir):
    """sections_fn(sop_id) for Assistant: all indexed sections of one SOP, from the files."""
    by_sop = {}
    for c in load_sop_chunks(Path(data_dir) / "sops"):
        by_sop.setdefault(c["sop_id"], []).append(c)
    return lambda sop_id: by_sop.get(sop_id, [])


def baseline_search_fn(data_dir):
    """Return a search_fn(index, query, filters, k) backed by BM25, for Assistant(...)."""
    data_dir = Path(data_dir)
    indexes = {
        "sop": BM25(load_sop_chunks(data_dir / "sops")),
        "events": BM25(load_event_chunks(data_dir / "raw" / "ooc_events.csv", data_dir / "raw" / "root_causes.csv")),
    }
    return lambda index, query, filters, k: indexes[index].search(query, filters, k)
