# Databricks notebook source
# MAGIC %md
# MAGIC # 03 · The assistant: ask it questions
# MAGIC
# MAGIC Connects the assistant (`src/fabrag/assistant.py`) to AI Search, a chat model and Spark SQL, with the
# MAGIC Week 3 retrieval: **hybrid search + reranker + parent-document expansion**. Change the question in the
# MAGIC last cell to try your own. The full evaluation is in `04_evaluate`.
# MAGIC **Run `02_build_index` first.**

# COMMAND ----------

# MAGIC %pip install --quiet databricks-ai-search

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("schema", "fab_rag")
dbutils.widgets.text("endpoint", "fab-rag-endpoint")
dbutils.widgets.text("chat_model", "databricks-gpt-oss-120b")
dbutils.widgets.dropdown("rerank", "true", ["true", "false"])

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
endpoint = dbutils.widgets.get("endpoint")
chat_model = dbutils.widgets.get("chat_model")
rerank = dbutils.widgets.get("rerank") == "true"
fq = lambda name: f"{catalog}.{schema}.{name}"

# COMMAND ----------

import os
import sys

sys.path.append(os.path.abspath("../src"))

from databricks.ai_search.client import AISearchClient
from databricks.sdk import WorkspaceClient

from fabrag.assistant import Assistant, citations
from fabrag.backends import make_llm_fn, make_search_fn, make_sections_fn, make_sql_fn

w = WorkspaceClient()
llm = make_llm_fn(w, chat_model)
try:
    print("Chat model says:", llm([{"role": "user", "content": "Reply with the single word: ready"}]))
except Exception as exc:
    names = sorted(e.name for e in w.serving_endpoints.list())
    raise RuntimeError(f"Chat endpoint '{chat_model}' failed ({exc}). Available endpoints: {names}")

bot = Assistant(
    make_search_fn(AISearchClient(), endpoint, {"sop": fq("idx_sop_chunks"), "events": fq("idx_event_chunks")},
                   "HYBRID", rerank=rerank),
    llm,
    sql_fn=make_sql_fn(spark),
    sections_fn=make_sections_fn(spark, fq("gold_sop_chunks")),
    table_name=fq("silver_ooc_events"),
)

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
    except ImportError:
        print("\n".join(lines))


def ask(question):
    a = bot.ask(question)
    show(a)
    return a

# COMMAND ----------

# Week 2 declined this one because the release criteria were not retrieved. Parent-document expansion fixes it.
_ = ask("CD is off across every field on LITH-03 but focus looks fine. What's the next step?")

# COMMAND ----------

# A paraphrase with no SOP keywords: "doesn't stay clamped" + "backside cooling" = ESC helium leak.
_ = ask("On ETCH-01 the wafer doesn't stay clamped properly and the backside cooling keeps alarming. Where do I start?")

# COMMAND ----------

_ = ask("What was the most common root cause on CMP tools in 2025?")

# COMMAND ----------

_ = ask("How do I tune beam current on the ion implanter?")

# COMMAND ----------

# Try your own question here.
_ = ask("Has ETCH-03 had a helium backside leak before, and what fixed it?")
