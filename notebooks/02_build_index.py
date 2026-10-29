# Databricks notebook source
# MAGIC %md
# MAGIC # 02 · Gold tables and AI Search indexes
# MAGIC
# MAGIC Builds the two Gold tables the assistant retrieves from, and an AI Search (formerly Vector Search)
# MAGIC Delta Sync index on each. Embeddings are computed by Databricks from `retrieval_text`
# MAGIC (managed embeddings), so there is no embedding code to maintain.
# MAGIC
# MAGIC | Gold table | Rows | Index |
# MAGIC |---|---|---|
# MAGIC | `gold_sop_chunks` | 1 per SOP section (247) | `idx_sop_chunks` |
# MAGIC | `gold_event_chunks` | 1 per OOC event with a usable closure note (404) | `idx_event_chunks` |
# MAGIC
# MAGIC **Run `01_bronze_silver` first.** Creating the indexes takes about 5 to 15 minutes the first time.

# COMMAND ----------

# MAGIC %pip install --quiet databricks-ai-search

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("schema", "fab_rag")
dbutils.widgets.text("endpoint", "fab-rag-endpoint")
dbutils.widgets.text("embedding_model", "databricks-gte-large-en")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
endpoint = dbutils.widgets.get("endpoint")
embedding_model = dbutils.widgets.get("embedding_model")
fq = lambda name: f"{catalog}.{schema}.{name}"

# COMMAND ----------

import os
import sys

sys.path.append(os.path.abspath("../src"))
from fabrag.gold import gold_event_chunks, gold_sop_chunks

# COMMAND ----------

# MAGIC %md ## 1. Check the embedding model endpoint
# MAGIC If this fails, the cell prints the endpoint names your workspace has: copy the embedding one
# MAGIC (it contains `gte`, `bge` or `embedding`) into the `embedding_model` widget and re-run.

# COMMAND ----------

from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
try:
    resp = w.api_client.do("POST", f"/serving-endpoints/{embedding_model}/invocations", body={"input": ["focus ring erosion"]})
    print(f"OK: {embedding_model} returns vectors of length {len(resp['data'][0]['embedding'])}")
except Exception as exc:
    names = sorted(e.name for e in w.serving_endpoints.list())
    raise RuntimeError(
        f"Embedding endpoint '{embedding_model}' did not respond ({exc}).\n"
        f"Endpoints in this workspace: {[n for n in names if any(k in n for k in ('gte', 'bge', 'embed'))] or names}"
    )

# COMMAND ----------

# MAGIC %md ## 2. Gold tables (Change Data Feed on, which Delta Sync needs)

# COMMAND ----------

def write_gold(df, name, pk, comment):
    """Create on first run; afterwards MERGE, so the index only re-embeds rows that changed."""
    df.createOrReplaceTempView(f"_{name}")
    if not spark.catalog.tableExists(fq(name)):
        spark.sql(f"""
            CREATE TABLE {fq(name)}
            COMMENT '{comment}'
            TBLPROPERTIES (delta.enableChangeDataFeed = true)
            AS SELECT * FROM _{name}
        """)
    else:
        spark.sql(f"""
            MERGE INTO {fq(name)} t USING _{name} s ON t.{pk} = s.{pk}
            WHEN MATCHED AND to_json(struct(t.*)) <> to_json(struct(s.*)) THEN UPDATE SET *
            WHEN NOT MATCHED THEN INSERT *
            WHEN NOT MATCHED BY SOURCE THEN DELETE
        """)
    print(f"{fq(name)}: {spark.table(fq(name)).count()} rows")


write_gold(gold_sop_chunks(spark.table(fq("silver_sop_sections"))), "gold_sop_chunks", "chunk_id",
           "One row per SOP section, the retrieval unit for procedures")
write_gold(gold_event_chunks(spark.table(fq("silver_ooc_events"))), "gold_event_chunks", "event_id",
           "One row per past OOC event with a usable closure note")

# COMMAND ----------

# MAGIC %md ## 3. AI Search indexes

# COMMAND ----------

from databricks.ai_search.client import AISearchClient

client = AISearchClient()

INDEXES = {
    fq("idx_sop_chunks"): ("gold_sop_chunks", "chunk_id"),
    fq("idx_event_chunks"): ("gold_event_chunks", "event_id"),
}


def get_or_create(index_name, table, pk):
    try:
        idx = client.get_index(endpoint_name=endpoint, index_name=index_name)
        print(f"{index_name}: exists, syncing with the latest Gold table")
        idx.sync()
    except Exception:
        print(f"{index_name}: creating (embeddings from retrieval_text via {embedding_model})")
        idx = client.create_delta_sync_index(
            endpoint_name=endpoint,
            index_name=index_name,
            source_table_name=fq(table),
            primary_key=pk,
            pipeline_type="TRIGGERED",
            embedding_source_column="retrieval_text",
            embedding_model_endpoint_name=embedding_model,
        )
    return idx


indexes = {name: get_or_create(name, table, pk) for name, (table, pk) in INDEXES.items()}

# COMMAND ----------

from datetime import timedelta

for name, idx in indexes.items():
    idx.wait_until_ready(verbose=True, timeout=timedelta(minutes=30), wait_for_updates=True)
    status = idx.describe().get("status", {})
    print(f"{name}: {status.get('detailed_state')} | rows indexed: {status.get('indexed_row_count')}")

# COMMAND ----------

# MAGIC %md ## 4. Smoke test: hybrid search (meaning + keywords)

# COMMAND ----------

q = "helium flow alarm and de-chuck errors"
for name, cols in [(fq("idx_sop_chunks"), ["chunk_id", "section_title"]),
                   (fq("idx_event_chunks"), ["event_id", "tool_id", "root_cause_code"])]:
    res = indexes[name].similarity_search(query_text=q, columns=cols, num_results=3, query_type="HYBRID", disable_notice=True)
    print(name)
    for row in res["result"]["data_array"]:
        print("   ", row)
