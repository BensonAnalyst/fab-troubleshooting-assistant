# Databricks notebook source
# MAGIC %md
# MAGIC # 01 · Bronze and Silver: fab troubleshooting knowledge base
# MAGIC
# MAGIC Lands the synthetic OOC events, maintenance logs and SOP documents into Unity Catalog, then builds
# MAGIC the Silver tables that Week 2 will chunk, embed and index:
# MAGIC
# MAGIC | Table | Grain | Purpose |
# MAGIC |---|---|---|
# MAGIC | `bronze_ooc_events`, `bronze_maintenance_logs`, `bronze_tools`, `bronze_root_causes` | 1 row per source row | Raw landing, all strings, with lineage |
# MAGIC | `bronze_sop_documents` | 1 row per SOP file | Raw Markdown |
# MAGIC | `silver_ooc_events` | 1 row per OOC event | Typed, de-duplicated, note quality flagged, `retrieval_text` built |
# MAGIC | `silver_sop_sections` | 1 row per SOP section | Section-level chunks with `chunk_id` |
# MAGIC | `dq_scorecard` | 1 row per run | Data quality summary |
# MAGIC
# MAGIC **Before running:** create a Volume and upload the repo's `data/` folder into it (see README, "Run it").

# COMMAND ----------

dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("schema", "fab_rag")
dbutils.widgets.text("volume", "raw")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
volume = dbutils.widgets.get("volume")
base = f"/Volumes/{catalog}/{schema}/{volume}/data"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")
spark.sql(f"CREATE VOLUME IF NOT EXISTS {catalog}.{schema}.{volume}")
print(f"Reading from {base}")

# COMMAND ----------

import os
import sys

# The notebook lives in notebooks/; the package lives in src/ of the same Git folder.
sys.path.append(os.path.abspath("../src"))

from fabrag.silver import (dq_scorecard, read_bronze_csv, read_bronze_documents,
                           silver_ooc_events, silver_sop_sections)


def save(df, name):
    full = f"{catalog}.{schema}.{name}"
    df.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(full)
    print(f"{full}: {spark.table(full).count()} rows")


# COMMAND ----------

# MAGIC %md ## Bronze

# COMMAND ----------

bronze = {
    "bronze_ooc_events": read_bronze_csv(spark, f"{base}/raw/ooc_events.csv"),
    "bronze_maintenance_logs": read_bronze_csv(spark, f"{base}/raw/maintenance_logs.csv"),
    "bronze_tools": read_bronze_csv(spark, f"{base}/raw/tools.csv"),
    "bronze_root_causes": read_bronze_csv(spark, f"{base}/raw/root_causes.csv"),
    "bronze_sop_documents": read_bronze_documents(spark, f"{base}/sops"),
}
for name, df in bronze.items():
    save(df, name)

# Ground truth is for evaluation only: it is never indexed or shown to the assistant.
save(read_bronze_csv(spark, f"{base}/ground_truth/ooc_ground_truth.csv"), "ooc_ground_truth")

# COMMAND ----------

# MAGIC %md ## Silver

# COMMAND ----------

events = silver_ooc_events(spark.table(f"{catalog}.{schema}.bronze_ooc_events"),
                           spark.table(f"{catalog}.{schema}.bronze_root_causes"))
sections = silver_sop_sections(spark.table(f"{catalog}.{schema}.bronze_sop_documents"))
save(events, "silver_ooc_events")
save(sections, "silver_sop_sections")
save(dq_scorecard(spark.table(f"{catalog}.{schema}.silver_ooc_events"),
                  spark.table(f"{catalog}.{schema}.silver_sop_sections")), "dq_scorecard")

# COMMAND ----------

# MAGIC %md ## Data quality check
# MAGIC About 1 in 10 closure notes is too vague to help anyone ("fixed", "see shift log"). They stay in Silver for
# MAGIC reporting but are excluded from the retrieval index (`is_indexable = false`).

# COMMAND ----------

display(spark.table(f"{catalog}.{schema}.dq_scorecard"))

# COMMAND ----------

display(spark.sql(f"""
    SELECT module, note_quality, COUNT(*) AS events
    FROM {catalog}.{schema}.silver_ooc_events
    GROUP BY ALL ORDER BY module, note_quality
"""))

# COMMAND ----------

# Enable Change Data Feed: Databricks Vector Search (Week 2) syncs Delta Sync indexes from it.
for t in ("silver_ooc_events", "silver_sop_sections"):
    spark.sql(f"ALTER TABLE {catalog}.{schema}.{t} SET TBLPROPERTIES (delta.enableChangeDataFeed = true)")
print("Change Data Feed enabled")
