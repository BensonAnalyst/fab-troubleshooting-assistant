"""The troubleshooting assistant: routing, retrieval, prompt, answer and citations.

The search, LLM and SQL backends are passed in as plain functions, so the same logic runs
against Databricks AI Search and model serving in a notebook, and against fakes in the tests.

    search_fn(index: str, query: str, filters: dict | None, k: int) -> list[dict]
    llm_fn(messages: list[dict]) -> str
    sql_fn(sql: str) -> list[dict]
"""

import re
from dataclasses import dataclass, field

TOOL_RE = re.compile(r"\b(ETCH|CVD|CMP|LITH|WET)-\d{2}\b", re.IGNORECASE)
MODULES = ("ETCH", "CVD", "CMP", "LITH", "WET")

# Questions that need counting or averaging over many events. Retrieval returns a handful of
# chunks, so it cannot answer these correctly: they go to SQL instead.
AGGREGATE_RE = re.compile(
    r"\bhow many\b|\baverage\b|\bmean\b|\bmost common\b|\bmost frequent\b|\bcount\b|\btotal\b"
    r"|\bper (day|week|month|quarter|year)\b|\btrend (of|in)\b|\bover time\b|\bpercentage\b|\bwhat share\b",
    re.IGNORECASE,
)
HISTORY_RE = re.compile(r"\b(before|previously|history|last time|in the past|has \w+-\d{2} had)\b", re.IGNORECASE)

DECLINE_PREFIX = "I can't answer that from the knowledge base"

SYSTEM_PROMPT = f"""You are the troubleshooting assistant for Northbridge Fab 1, a fictional wafer fab used for a portfolio project.
You help process and equipment engineers respond to SPC out-of-control (OOC) events.

Rules:
1. Use ONLY the numbered sources provided. Every factual statement must cite its source, like [S1] or [E2].
2. Never invent limits, values, part names, recipe steps or procedures that are not in the sources.
3. If the sources do not contain what is needed to answer, start your reply with "{DECLINE_PREFIX}" and say in one sentence what is missing. Do not guess.
4. Do not rank, rate or judge individual people.
5. Recommend verifying the measurement first (SOP-MET-001) when the symptom is a single point with no trend.
6. Tool release always requires the acceptance criteria in the SOP and an engineer's sign-off.

For a troubleshooting question, answer in this structure, keeping only the parts the sources support:
**Likely cause**, **Checks**, **Fix**, **Release criteria**, **Similar past events**.
For a procedure question, answer in one to three sentences with the citation.
Be concise."""

SQL_SYSTEM_PROMPT = """You translate a question into ONE Spark SQL SELECT statement over a single table named silver_ooc_events.
Columns: event_id STRING, event_ts TIMESTAMP, tool_id STRING (e.g. 'CMP-02'), module STRING (ETCH, CVD, CMP, LITH, WET),
chamber STRING, parameter STRING, parameter_name STRING, unit STRING, value DOUBLE, spc_rule STRING, lot_id STRING,
engineer STRING, root_cause_code STRING (e.g. 'RC-ETCH-02', NULL when not entered), root_cause_name STRING,
closure_note STRING, downtime_hours DOUBLE, closed_ts TIMESTAMP, note_quality STRING ('ok' or 'low').
Root cause names: RC-ETCH-01 chamber polymer build-up, RC-ETCH-02 focus ring erosion, RC-ETCH-03 ESC helium leak,
RC-ETCH-04 RF match issue, RC-ETCH-05 MFC drift, RC-CVD-01 showerhead clogging, RC-CVD-02 particle flaking,
RC-CVD-03 heater/thermocouple drift, RC-CVD-04 precursor delivery, RC-CMP-01 pad glazing / conditioner disk,
RC-CMP-02 slurry/filter scratches, RC-CMP-03 carrier head wear, RC-CMP-04 endpoint drift, RC-LITH-01 overlay drift,
RC-LITH-02 chuck focus hot spot, RC-LITH-03 dose drift, RC-LITH-04 resist coat, RC-WET-01 aged bath,
RC-WET-02 filter/pump particles, RC-WET-03 dryer watermarks, RC-MET-01 metrology false alarm, RC-GEN-01 unqualified change.
Return only the SQL, with no explanation and no code fences. Round averages to 1 decimal place."""

_FORBIDDEN_SQL = re.compile(
    r"\b(insert|update|delete|merge|drop|create|alter|truncate|grant|revoke|call|copy|optimize|vacuum|refresh|set|use)\b",
    re.IGNORECASE,
)


@dataclass
class Answer:
    question: str
    route: str                      # "retrieval" or "sql"
    text: str
    sop_hits: list = field(default_factory=list)
    event_hits: list = field(default_factory=list)
    sql: str | None = None
    sql_rows: list | None = None
    declined: bool = False

    @property
    def retrieved_sop_ids(self):
        return list(dict.fromkeys(h["sop_id"] for h in self.sop_hits))

    @property
    def retrieved_event_ids(self):
        return [h["event_id"] for h in self.event_hits]


# ---------------------------------------------------------------------------------------
# Routing and filters
# ---------------------------------------------------------------------------------------
def route(question: str) -> str:
    return "sql" if AGGREGATE_RE.search(question) else "retrieval"


def tool_ids(question: str) -> list:
    return [m.group(0).upper() for m in TOOL_RE.finditer(question)]


def module_of(question: str):
    tools = tool_ids(question)
    if tools:
        return tools[0].split("-")[0]
    return None


def is_history(question: str) -> bool:
    return bool(HISTORY_RE.search(question)) and bool(tool_ids(question))


def search_filters(question: str):
    """Filters for (SOP index, event index). Module filters keep etch questions on etch documents."""
    module = module_of(question)
    sop_f = {"module_code": [module, "ANY"]} if module else None
    if is_history(question):
        ev_f = {"tool_id": tool_ids(question)[0]}
    elif module:
        ev_f = {"module": module}
    else:
        ev_f = None
    return sop_f, ev_f


# ---------------------------------------------------------------------------------------
# AI Search result parsing
# ---------------------------------------------------------------------------------------
def parse_hits(response: dict) -> list:
    """Turn an AI Search similarity_search response into a list of dicts with a `score` key."""
    cols = [c["name"] for c in response.get("manifest", {}).get("columns", [])]
    rows = response.get("result", {}).get("data_array", []) or []
    hits = []
    for row in rows:
        d = dict(zip(cols, row))
        if "score" not in d and len(row) == len(cols) + 1:
            d["score"] = row[-1]
        hits.append(d)
    return hits


# ---------------------------------------------------------------------------------------
# Prompting
# ---------------------------------------------------------------------------------------
def build_messages(question: str, sop_hits: list, event_hits: list) -> list:
    blocks = []
    for i, h in enumerate(sop_hits, 1):
        blocks.append(f"[S{i}] {h['chunk_id']}\n{h['retrieval_text']}")
    for i, h in enumerate(event_hits, 1):
        blocks.append(f"[E{i}] {h['retrieval_text']}")
    sources = "\n\n".join(blocks) if blocks else "(no sources found)"
    user = f"Question: {question}\n\nSources:\n\n{sources}"
    return [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}]


def citations(text: str) -> list:
    return sorted(set(re.findall(r"\[(S\d+|E\d+)\]", text)), key=lambda c: (c[0], int(c[1:])))


# ---------------------------------------------------------------------------------------
# SQL route
# ---------------------------------------------------------------------------------------
def clean_sql(raw: str) -> str:
    sql = raw.strip()
    sql = re.sub(r"^```(?:sql)?\s*|\s*```$", "", sql, flags=re.IGNORECASE).strip()
    return sql.rstrip(";").strip()


def check_sql(sql: str) -> str:
    """Allow only a single read-only SELECT over silver_ooc_events. Raises ValueError otherwise."""
    if ";" in sql:
        raise ValueError("Only one statement is allowed")
    if not re.match(r"^\s*(select|with)\b", sql, re.IGNORECASE):
        raise ValueError("Only SELECT queries are allowed")
    if _FORBIDDEN_SQL.search(sql):
        raise ValueError("Query contains a forbidden keyword")
    # EXTRACT(YEAR FROM col) uses FROM without a table: drop it before looking for table names.
    scan = re.sub(r"\bextract\s*\([^)]*\)", "", sql, flags=re.IGNORECASE)
    tables = re.findall(r"\b(?:from|join)\s+([\w.`]+)", scan, re.IGNORECASE)
    if not tables or any(t.strip("`").split(".")[-1].lower() != "silver_ooc_events" for t in tables):
        raise ValueError("Only the silver_ooc_events table may be queried")
    return sql


# ---------------------------------------------------------------------------------------
# The assistant
# ---------------------------------------------------------------------------------------
class Assistant:
    def __init__(self, search_fn, llm_fn, sql_fn=None, sop_index="sop", event_index="events",
                 k_sops=4, k_events=5, table_name="silver_ooc_events"):
        self.search_fn, self.llm_fn, self.sql_fn = search_fn, llm_fn, sql_fn
        self.sop_index, self.event_index = sop_index, event_index
        self.k_sops, self.k_events = k_sops, k_events
        self.table_name = table_name

    def ask(self, question: str) -> Answer:
        if route(question) == "sql":
            return self._ask_sql(question)
        sop_f, ev_f = search_filters(question)
        sop_hits = self.search_fn(self.sop_index, question, sop_f, self.k_sops)
        event_hits = self.search_fn(self.event_index, question, ev_f, self.k_events)
        text = self.llm_fn(build_messages(question, sop_hits, event_hits)).strip()
        return Answer(question, "retrieval", text, sop_hits, event_hits,
                      declined=text.startswith(DECLINE_PREFIX))

    def _ask_sql(self, question: str) -> Answer:
        if self.sql_fn is None:
            return Answer(question, "sql", f"{DECLINE_PREFIX}: counting questions need the SQL tool, which is not connected.",
                          declined=True)
        raw = self.llm_fn([{"role": "system", "content": SQL_SYSTEM_PROMPT}, {"role": "user", "content": question}])
        try:
            sql = check_sql(clean_sql(raw))
        except ValueError as exc:
            return Answer(question, "sql", f"{DECLINE_PREFIX}: the generated query was rejected ({exc}).",
                          sql=clean_sql(raw), declined=True)
        rows = self.sql_fn(sql.replace("silver_ooc_events", self.table_name))
        return Answer(question, "sql", _format_rows(rows), sql=sql, sql_rows=rows)


def _format_rows(rows: list) -> str:
    if not rows:
        return "No matching events."
    if len(rows) == 1 and len(rows[0]) == 1:
        return f"{next(iter(rows[0].values()))}"
    lines = [", ".join(f"{k}: {v}" for k, v in r.items()) for r in rows[:20]]
    return "\n".join(lines)


def chat_text(response: dict) -> str:
    """Extract the answer text from a chat-completions response.

    Reasoning models (for example gpt-oss) return `content` as a list of blocks, with the
    reasoning separate from the final text; only the text blocks are the answer.
    """
    content = response["choices"][0]["message"]["content"]
    if isinstance(content, str):
        return content
    parts = []
    for block in content or []:
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
        elif isinstance(block, str):
            parts.append(block)
    return "".join(parts)
