# Databricks notebook source
# MAGIC %md
# MAGIC # 04 · Evaluate: compare retrieval settings, judge the answers, Before vs After
# MAGIC
# MAGIC 1. **Retrieval settings** (no chat model, fast): keyword-only BM25, vector-only, hybrid, hybrid + reranker,
# MAGIC    each with and without parent-document expansion. Scored on all 61 questions.
# MAGIC 2. **Full run** of the assistant with the chosen setting, every answer graded by an **LLM judge**
# MAGIC    (coverage of the expected points, and groundedness in the sources).
# MAGIC 3. **Before vs After**: the Week 2 run against this one.
# MAGIC
# MAGIC Everything is logged to MLflow (experiment `fab-rag-evaluation` in your user folder) and to `eval_predictions`.
# MAGIC **Run `02_build_index` first** (re-run it once after the Week 3 update, so low-value SOP sections leave the index).

# COMMAND ----------

# MAGIC %pip install --quiet databricks-ai-search mlflow

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("schema", "fab_rag")
dbutils.widgets.text("endpoint", "fab-rag-endpoint")
dbutils.widgets.text("chat_model", "databricks-gpt-oss-120b")
dbutils.widgets.text("judge_model", "databricks-gpt-oss-120b")
dbutils.widgets.text("final_config", "split_expand")  # any name from section 1; the reranker configs need a paid workspace

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
endpoint = dbutils.widgets.get("endpoint")
chat_model = dbutils.widgets.get("chat_model")
judge_model = dbutils.widgets.get("judge_model")
final_config = dbutils.widgets.get("final_config")
fq = lambda name: f"{catalog}.{schema}.{name}"

# COMMAND ----------

import json
import os
import sys
import time

import mlflow

sys.path.append(os.path.abspath("../src"))
data_dir = os.path.abspath("../data")  # the repo's own data folder (Git folder), so no Volume re-upload

from databricks.ai_search.client import AISearchClient
from databricks.sdk import WorkspaceClient

from fabrag.assistant import Assistant, citations, route, sources_text
from fabrag.backends import make_llm_fn, make_search_fn, make_sections_fn, make_sql_fn, split_search_fn
from fabrag.baseline import baseline_search_fn, baseline_sections_fn
from fabrag.evaluate import aggregate_correct, retrieval_metrics
from fabrag.judge import judge_answer, judge_metrics

w = WorkspaceClient()
client = AISearchClient()
INDEXES = {"sop": fq("idx_sop_chunks"), "events": fq("idx_event_chunks")}

questions = [json.loads(l) for l in open(f"{data_dir}/eval/eval_questions.jsonl")]
truth_rc = {r.event_id: r.true_root_cause
            for r in spark.table(fq("ooc_ground_truth")).select("event_id", "true_root_cause").collect()}
print(f"{len(questions)} questions:", {t: sum(q['type'] == t for q in questions) for t in sorted({q['type'] for q in questions})})

user = w.current_user.me().user_name
mlflow.set_experiment(f"/Users/{user}/fab-rag-evaluation")
mlflow_ok = True


def log_mlflow(run_name, params, metrics, table=None):
    """Best effort: an MLflow problem should never stop the evaluation."""
    global mlflow_ok
    if not mlflow_ok:
        return
    try:
        with mlflow.start_run(run_name=run_name):
            mlflow.log_params(params)
            mlflow.log_metrics({k: float(v) for k, v in metrics.items() if isinstance(v, (int, float))})
            if table is not None:
                mlflow.log_table(table, artifact_file="predictions.json")
    except Exception as exc:
        mlflow_ok = False
        print(f"MLflow logging skipped: {exc}")

# COMMAND ----------

# MAGIC %md ## 1. Compare retrieval settings (no chat model needed)
# MAGIC `split` = keyword search (BM25) for SOPs, hybrid AI Search for past events.
# MAGIC `expand` = parent-document retrieval: the top SOP's Checks, Procedure and Acceptance sections are always added.

# COMMAND ----------

ai_sections = make_sections_fn(spark, fq("gold_sop_chunks"))
bm25_search, bm25_sections = baseline_search_fn(data_dir), baseline_sections_fn(data_dir)

CONFIGS = {
    "bm25":                 (bm25_search, None),
    "bm25_expand":          (bm25_search, bm25_sections),
    "vector":               (make_search_fn(client, endpoint, INDEXES, "ANN"), None),
    "hybrid":               (make_search_fn(client, endpoint, INDEXES, "HYBRID"), None),
    "hybrid_expand":        (make_search_fn(client, endpoint, INDEXES, "HYBRID"), ai_sections),
    # Week 3 finding: keyword search ranks SOPs better, hybrid search finds better past events. Use each where it wins.
    "split_expand":         (split_search_fn(bm25_search, make_search_fn(client, endpoint, INDEXES, "HYBRID")), bm25_sections),
    "hybrid_rerank":        (make_search_fn(client, endpoint, INDEXES, "HYBRID", rerank=True), None),
    "hybrid_rerank_expand": (make_search_fn(client, endpoint, INDEXES, "HYBRID", rerank=True), ai_sections),
}


def retrieval_preds(bot):
    out = []
    for q in questions:
        r = route(q["question"])
        sop, ev = ([], []) if r == "sql" else bot.retrieve(q["question"])
        out.append({"qid": q["qid"], "route": r, "declined": False,
                    "retrieved_sop_ids": list(dict.fromkeys(h["sop_id"] for h in sop)),
                    "retrieved_chunk_ids": [h["chunk_id"] for h in sop],
                    "retrieved_event_ids": [h["event_id"] for h in ev]})
    return out


SHOW = ["sop_top1_accuracy", "sop_mrr", "procedure_section_hit_rate", "acceptance_criteria_retrieved",
        "event_root_cause_precision_at_k", "history_event_recall",
        "paraphrase_sop_hit_rate_at_k", "paraphrase_sop_top1_accuracy",
        "paraphrase_event_root_cause_precision_at_k", "paraphrase_acceptance_criteria_retrieved"]
settings = {}
for name, (search_fn, sections_fn) in CONFIGS.items():
    t0 = time.time()
    try:
        m = retrieval_metrics(questions, retrieval_preds(Assistant(search_fn, None, sections_fn=sections_fn)), truth_rc)
        settings[name] = m
        log_mlflow(f"retrieval_{name}", {"stage": "retrieval", "config": name}, m)
        print(f"{name:<22} done in {time.time() - t0:.0f}s")
    except Exception as exc:
        print(f"{name:<22} FAILED: {str(exc)[:200]}")

display(spark.createDataFrame(
    [(k, *[settings[c].get(k) for c in settings]) for k in SHOW],
    "metric string, " + ", ".join(f"{c} double" for c in settings),
))

# COMMAND ----------

# MAGIC %md ## 2. Full run with the chosen setting, graded by the LLM judge (about 10 to 20 minutes)

# COMMAND ----------

if final_config not in settings:
    fallback = next(c for c in ("split_expand", "hybrid_expand", "hybrid", "bm25_expand") if c in settings)
    print(f"'{final_config}' is not available; using '{fallback}'")
    final_config = fallback

search_fn, sections_fn = CONFIGS[final_config]
llm, judge_llm = make_llm_fn(w, chat_model), make_llm_fn(w, judge_model, max_tokens=4000)  # reasoning model: needs room to think before the JSON
bot = Assistant(search_fn, llm, sql_fn=make_sql_fn(spark), sections_fn=sections_fn, table_name=fq("silver_ooc_events"))

run_id = time.strftime("%Y%m%d-%H%M%S")
preds, judged = [], []
for q in questions:
    t0 = time.time()
    rec = {"run_id": run_id, "config": final_config, "qid": q["qid"], "type": q["type"], "question": q["question"],
           "expected_behavior": q["expected_behavior"], "chat_model": chat_model, "error": None,
           "route": None, "answer": None, "declined": False, "retrieved_sop_ids": [], "retrieved_chunk_ids": [],
           "retrieved_event_ids": [], "citations": [], "sql": None, "coverage": None, "grounded": None,
           "judge_reason": None, "aggregate_correct": None}
    try:
        a = bot.ask(q["question"])
        rec.update(route=a.route, answer=a.text, declined=a.declined, retrieved_sop_ids=a.retrieved_sop_ids,
                   retrieved_chunk_ids=a.retrieved_chunk_ids if a.route == "retrieval" else [],
                   retrieved_event_ids=a.retrieved_event_ids, citations=citations(a.text), sql=a.sql)
        if q["type"] == "aggregate":
            rec["aggregate_correct"] = aggregate_correct(q["expected_answer_points"][0], a.text)
        elif q["expected_behavior"] == "answer":
            if a.declined:
                j = {"coverage": 0.0, "grounded": None, "reason": "declined", "judge_error": None}
            else:
                j = judge_answer(judge_llm, q["question"], q["expected_answer_points"],
                                 sources_text(a.sop_hits, a.event_hits), a.text)
            rec.update(coverage=j["coverage"], grounded=j["grounded"], judge_reason=j.get("reason") or j.get("judge_error"))
            judged.append({"type": q["type"], **j})
    except Exception as exc:  # one failed call should not lose the whole run
        rec["error"] = str(exc)[:500]
    rec["latency_s"] = round(time.time() - t0, 2)
    preds.append(rec)
    print(f"{q['qid']} {q['type']:<15} {rec['route'] or 'ERROR':<9} cov={rec['coverage']} grounded={rec['grounded']} {rec['latency_s']}s")

PRED_SCHEMA = ("run_id string, config string, qid string, type string, question string, expected_behavior string, "
               "chat_model string, error string, route string, answer string, declined boolean, "
               "retrieved_sop_ids array<string>, retrieved_chunk_ids array<string>, retrieved_event_ids array<string>, "
               "citations array<string>, sql string, coverage double, grounded boolean, judge_reason string, "
               "aggregate_correct boolean, latency_s double")
pred_df = spark.createDataFrame(preds, PRED_SCHEMA)
pred_df.write.mode("append").option("mergeSchema", "true").saveAsTable(fq("eval_predictions"))

ok = [p for p in preds if p["error"] is None]
final_metrics = {**retrieval_metrics(questions, ok, truth_rc), **judge_metrics(judged)}
aggs = [p["aggregate_correct"] for p in ok if p["aggregate_correct"] is not None]
final_metrics["aggregate_accuracy"] = round(sum(aggs) / len(aggs), 3) if aggs else None
final_metrics["errors"] = len(preds) - len(ok)
final_metrics["median_latency_s"] = sorted(p["latency_s"] for p in preds)[len(preds) // 2]
log_mlflow(f"full_{final_config}", {"stage": "full", "config": final_config, "chat_model": chat_model,
                                     "judge_model": judge_model, "run_id": run_id}, final_metrics, pred_df.toPandas())
print(f"Saved run {run_id}. Errors: {final_metrics['errors']}")
display(spark.createDataFrame([(k, float(v) if v is not None else None) for k, v in final_metrics.items()],
                              "metric string, value double"))

# COMMAND ----------

# MAGIC %md ## 2b. (Optional) Re-grade a saved run with the judge only
# MAGIC Use this if the judge failed on a run: it rebuilds each answer's sources from the saved IDs
# MAGIC and grades again, without generating new answers.

# COMMAND ----------

# Re-grade only the answers the judge failed on (coverage empty). Same saved answers, judge only.
RUN_TO_REGRADE = run_id  # or paste an earlier run_id, e.g. "20261030-083342"
judge_llm = make_llm_fn(w, judge_model, max_tokens=4000)

sop_text = {r.chunk_id: r.asDict() for r in spark.table(fq("gold_sop_chunks")).select("chunk_id", "retrieval_text").collect()}
evt_text = {r.event_id: r.asDict() for r in spark.table(fq("gold_event_chunks")).select("event_id", "retrieval_text").collect()}
qmap = {q["qid"]: q for q in questions}
rows = [r.asDict() for r in spark.table(fq("eval_predictions")).where(
    f"run_id = '{RUN_TO_REGRADE}' AND expected_behavior = 'answer' AND type != 'aggregate' AND error IS NULL AND coverage IS NULL").collect()]
print(f"{len(rows)} answers to re-grade")

updates = []
for r in sorted(rows, key=lambda r: r["qid"]):
    q = qmap[r["qid"]]
    if r["declined"]:
        j = {"coverage": 0.0, "grounded": None, "reason": "declined", "judge_error": None}
    else:
        # Rebuild exactly the sources the assistant saw, from the IDs saved with the answer.
        src = sources_text([sop_text[c] for c in r["retrieved_chunk_ids"] if c in sop_text],
                           [evt_text[e] for e in r["retrieved_event_ids"] if e in evt_text])
        for _ in range(2):  # one retry if the reply is still unusable
            j = judge_answer(judge_llm, q["question"], q["expected_answer_points"], src, r["answer"])
            if not j["judge_error"]:
                break
    updates.append((RUN_TO_REGRADE, r["qid"], j["coverage"], j["grounded"], j.get("reason") or j.get("judge_error")))
    print(f"{r['qid']} {q['type']:<15} cov={j['coverage']} grounded={j['grounded']}")

if updates:
    spark.createDataFrame(updates, "run_id string, qid string, coverage double, grounded boolean, judge_reason string") \
         .createOrReplaceTempView("_regrade")
    spark.sql(f"""
        MERGE INTO {fq('eval_predictions')} t USING _regrade s ON t.run_id = s.run_id AND t.qid = s.qid
        WHEN MATCHED THEN UPDATE SET t.coverage = s.coverage, t.grounded = s.grounded, t.judge_reason = s.judge_reason
    """)

# Judge metrics for the whole run, read back from the table.
judged = [{"type": r.type, "coverage": r.coverage, "grounded": r.grounded,
           "judge_error": (r.judge_reason or "").startswith("unparseable")}
          for r in spark.table(fq("eval_predictions")).where(
              f"run_id = '{RUN_TO_REGRADE}' AND expected_behavior = 'answer' AND type != 'aggregate' AND error IS NULL").collect()]
judge_results = judge_metrics(judged)
log_mlflow(f"regrade_{RUN_TO_REGRADE}", {"stage": "regrade", "run_id": RUN_TO_REGRADE, "judge_model": judge_model}, judge_results)
run_id = RUN_TO_REGRADE  # so section 4 analyses this run
display(spark.createDataFrame([(k, float(v) if v is not None else None) for k, v in judge_results.items()],
                              "metric string, value double"))

# COMMAND ----------

# MAGIC %md ## 3. Before vs After (Week 2 run vs this run)

# COMMAND ----------

from pyspark.sql import functions as F

hist = spark.table(fq("eval_predictions"))
if "config" not in hist.columns:
    hist = hist.withColumn("config", F.lit(None).cast("string"))
week2_ids = [r.run_id for r in hist.where("config IS NULL").select("run_id").distinct().orderBy("run_id").collect()]

def metrics_for(run):
    rows = [r.asDict() for r in hist.where(F.col("run_id") == run).collect()]
    for r in rows:
        r.setdefault("retrieved_chunk_ids", None)
    q49 = [q for q in questions if int(q["qid"][1:]) <= 49]  # Week 2 only had these
    m = retrieval_metrics(q49, [r for r in rows if r["error"] is None], truth_rc)
    exp = {q["qid"]: q["expected_answer_points"][0] for q in q49 if q["type"] == "aggregate"}
    m["aggregate_accuracy"] = round(sum(aggregate_correct(exp[r["qid"]], r["answer"]) for r in rows if r["qid"] in exp) / len(exp), 3)
    return m

if week2_ids:
    before = metrics_for(week2_ids[-1])
    after = metrics_for(run_id)  # same 49 questions, for a fair comparison
    keys = ["routing_accuracy", "sop_top1_accuracy", "sop_mrr", "procedure_section_hit_rate", "acceptance_criteria_retrieved",
            "event_root_cause_precision_at_k", "history_event_recall", "decline_rate_unanswerable",
            "false_decline_rate_answerable", "aggregate_accuracy"]
    display(spark.createDataFrame([(k, before.get(k), after.get(k)) for k in keys],
                                  "metric string, week2_before double, week3_after double"))
    print(f"Week 2 run: {week2_ids[-1]}   Week 3 run: {run_id}   (same 49 questions)")
else:
    print("No Week 2 run found in eval_predictions; showing this run only.")

# COMMAND ----------

# MAGIC %md ## 4. Error analysis: what still goes wrong

# COMMAND ----------

display(spark.sql(f"""
    SELECT qid, type, question, coverage, grounded, judge_reason, declined, answer
    FROM {fq('eval_predictions')}
    WHERE run_id = '{run_id}' AND expected_behavior = 'answer'
      AND (declined OR coverage < 0.6 OR grounded = false)
    ORDER BY coverage
"""))
