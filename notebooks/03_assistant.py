# Databricks notebook source
# MAGIC %md
# MAGIC # 03 · The assistant: ask questions, then run the evaluation set
# MAGIC
# MAGIC 1. Connects the assistant (`src/fabrag/assistant.py`) to AI Search, a chat model and Spark SQL.
# MAGIC 2. Answers a few sample questions with citations.
# MAGIC 3. Runs all 49 evaluation questions, scores **routing, retrieval and declining**, compares
# MAGIC    AI Search with a keyword-only (BM25) baseline, and saves everything to `eval_predictions`.
# MAGIC
# MAGIC Answer correctness and groundedness are scored with an LLM judge in Week 3.
# MAGIC **Run `02_build_index` first.**

# COMMAND ----------

# MAGIC %pip install --quiet databricks-ai-search

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("schema", "fab_rag")
dbutils.widgets.text("volume", "raw")
dbutils.widgets.text("endpoint", "fab-rag-endpoint")
dbutils.widgets.text("chat_model", "databricks-gpt-oss-120b")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
volume = dbutils.widgets.get("volume")
endpoint = dbutils.widgets.get("endpoint")
chat_model = dbutils.widgets.get("chat_model")
fq = lambda name: f"{catalog}.{schema}.{name}"
data_dir = f"/Volumes/{catalog}/{schema}/{volume}/data"

# COMMAND ----------

import json
import os
import re
import sys
import time

sys.path.append(os.path.abspath("../src"))

from databricks.ai_search.client import AISearchClient
from databricks.sdk import WorkspaceClient

from fabrag.assistant import Assistant, chat_text, citations, parse_hits
from fabrag.baseline import baseline_search_fn
from fabrag.evaluate import retrieval_metrics

w = WorkspaceClient()
client = AISearchClient()

# COMMAND ----------

# MAGIC %md ## 1. Connect the backends

# COMMAND ----------

INDEX = {"sop": fq("idx_sop_chunks"), "events": fq("idx_event_chunks")}
COLUMNS = {
    "sop": ["chunk_id", "sop_id", "sop_title", "section_title", "module_code", "retrieval_text"],
    "events": ["event_id", "tool_id", "module", "event_date", "root_cause_code", "retrieval_text"],
}
_index_cache = {}


def ai_search(index, query, filters, k):
    if index not in _index_cache:
        _index_cache[index] = client.get_index(endpoint_name=endpoint, index_name=INDEX[index])
    res = _index_cache[index].similarity_search(
        query_text=query, columns=COLUMNS[index], filters=filters, num_results=k,
        query_type="HYBRID", disable_notice=True,
    )
    return parse_hits(res)


def llm(messages, max_tokens=1200):
    body = {"messages": messages, "max_tokens": max_tokens, "temperature": 0}
    resp = w.api_client.do("POST", f"/serving-endpoints/{chat_model}/invocations", body=body)
    return chat_text(resp)


def run_sql(sql):
    return [r.asDict() for r in spark.sql(sql).limit(50).collect()]


# Quick check that the chat model answers; if not, list the names this workspace uses.
try:
    print("Chat model says:", llm([{"role": "user", "content": "Reply with the single word: ready"}], max_tokens=50))
except Exception as exc:
    names = sorted(e.name for e in w.serving_endpoints.list())
    raise RuntimeError(f"Chat endpoint '{chat_model}' failed ({exc}). Available endpoints: {names}")

bot = Assistant(ai_search, llm, sql_fn=run_sql, sop_index="sop", event_index="events",
                table_name=fq("silver_ooc_events"))

# COMMAND ----------

# MAGIC %md ## 2. Ask it something

# COMMAND ----------

def show(answer):
    used = set(citations(answer.text))
    lines = [f"### {answer.question}", f"*Route: {answer.route}*", "", answer.text, ""]
    if answer.sql:
        lines += ["**SQL run:**", f"`{answer.sql}`"]
    if answer.sop_hits or answer.event_hits:
        lines += ["| Ref | Source | Cited |", "|---|---|---|"]
        lines += [f"| S{i} | {h['chunk_id']} ({h['section_title']}) | {'✅' if f'S{i}' in used else ''} |"
                  for i, h in enumerate(answer.sop_hits, 1)]
        lines += [f"| E{i} | {h['event_id']} on {h['tool_id']}, {h['event_date']}, {h['root_cause_code'] or 'not coded'} | "
                  f"{'✅' if f'E{i}' in used else ''} |" for i, h in enumerate(answer.event_hits, 1)]
    try:
        import markdown as _md
        displayHTML(_md.markdown("\n".join(lines), extensions=["tables"]))
    except ImportError:  # plain text if the markdown package is not installed
        print("\n".join(lines))


def ask(question):
    a = bot.ask(question)
    show(a)
    return a


_ = ask("Getting helium flow alarms on ETCH-04 and a few de-chuck errors. What should I check first?")

# COMMAND ----------

_ = ask("Has ETCH-03 had a helium backside leak before, and what fixed it?")

# COMMAND ----------

_ = ask("How many OOC events did CMP-02 have in Q2 2025?")

# COMMAND ----------

_ = ask("How do I tune beam current on the ion implanter?")

# COMMAND ----------

# MAGIC %md ## 3. Run the evaluation set (49 questions, about 3 to 6 minutes)

# COMMAND ----------

questions = [json.loads(l) for l in open(f"{data_dir}/eval/eval_questions.jsonl")]
truth_rc = {r.event_id: r.true_root_cause for r in spark.table(fq("ooc_ground_truth")).select("event_id", "true_root_cause").collect()}

run_id = time.strftime("%Y%m%d-%H%M%S")
preds = []
for q in questions:
    t0 = time.time()
    try:
        a = bot.ask(q["question"])
        err = None
    except Exception as exc:  # keep going: one failed call should not lose the whole run
        a, err = None, str(exc)[:500]
    preds.append({
        "run_id": run_id, "qid": q["qid"], "type": q["type"], "question": q["question"],
        "expected_behavior": q["expected_behavior"],
        "route": a.route if a else None,
        "answer": a.text if a else None,
        "declined": a.declined if a else False,
        "retrieved_sop_ids": a.retrieved_sop_ids if a else [],
        "retrieved_event_ids": a.retrieved_event_ids if a else [],
        "citations": citations(a.text) if a else [],
        "sql": a.sql if a else None,
        "latency_s": round(time.time() - t0, 2),
        "error": err,
        "chat_model": chat_model,
    })
    print(f"{q['qid']} {q['type']:<15} {preds[-1]['route'] or 'ERROR':<9} {preds[-1]['latency_s']:>5}s")

PRED_SCHEMA = ("run_id string, qid string, type string, question string, expected_behavior string, route string, "
               "answer string, declined boolean, retrieved_sop_ids array<string>, retrieved_event_ids array<string>, "
               "citations array<string>, sql string, latency_s double, error string, chat_model string")
spark.createDataFrame(preds, PRED_SCHEMA).write.mode("append").option("mergeSchema", "true").saveAsTable(fq("eval_predictions"))
print(f"Saved run {run_id} to {fq('eval_predictions')}")

# COMMAND ----------

# MAGIC %md ## 4. Score it, and compare with the keyword-only baseline

# COMMAND ----------

ok = [p for p in preds if p["error"] is None]
ai = retrieval_metrics(questions, ok, truth_rc)

# Same assistant, same filters, but BM25 keyword search instead of AI Search. No LLM needed for retrieval scoring.
base_bot = Assistant(baseline_search_fn(data_dir), lambda m: "", sql_fn=lambda s: [])
base_preds = []
for q in questions:
    b = base_bot.ask(q["question"])
    base_preds.append({"qid": q["qid"], "route": b.route, "retrieved_sop_ids": b.retrieved_sop_ids,
                       "retrieved_event_ids": b.retrieved_event_ids, "declined": False})
bm25 = retrieval_metrics(questions, base_preds, truth_rc)

rows = [(k, bm25[k], ai[k]) for k in ai if k not in ("decline_rate_unanswerable", "false_decline_rate_answerable")]
rows += [("decline_rate_unanswerable", None, ai["decline_rate_unanswerable"]),
         ("false_decline_rate_answerable", None, ai["false_decline_rate_answerable"])]
scores = spark.createDataFrame(rows, "metric string, bm25_keyword_baseline double, ai_search_hybrid double")
display(scores)

errors = [p for p in preds if p["error"]]
print(f"Errors: {len(errors)}", *[f"{p['qid']}: {p['error'][:150]}" for p in errors], sep="\n")

# COMMAND ----------

# MAGIC %md ## 5. Aggregate questions: did the SQL route give the right number?

# COMMAND ----------

for q in (q for q in questions if q["type"] == "aggregate"):
    p = next(p for p in preds if p["qid"] == q["qid"])
    expected = q["expected_answer_points"][0]
    hit = re.search(rf"(?<![\w.]){re.escape(expected.split()[0])}(?![\w.])", p["answer"] or "") is not None
    print(f"{'✅' if hit else '❌'} {q['question']}\n   expected: {expected}\n   got:      {p['answer']}\n   sql:      {p['sql']}\n")
