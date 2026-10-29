"""Bronze -> Silver transforms (PySpark). Used by the Databricks notebook and by the local tests.

Only built-in Spark functions are used (no Python UDFs), so this runs on Databricks
serverless compute as well as a local SparkSession.
"""

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from .knowledge import VAGUE_NOTES

MIN_NOTE_CHARS = 30  # below this a closure note cannot describe symptom, cause, action and result


# ---------------------------------------------------------------------------------------
# Bronze: land the files as they are, plus lineage columns
# ---------------------------------------------------------------------------------------
def read_bronze_csv(spark: SparkSession, path: str) -> DataFrame:
    """Read a raw CSV with every column as string, so nothing is lost at ingestion."""
    return (
        spark.read.option("header", True).option("multiLine", True).option("escape", '"').csv(path)
        .withColumn("_source_file", F.col("_metadata.file_path"))
        .withColumn("_ingested_at", F.current_timestamp())
    )


def read_bronze_documents(spark: SparkSession, path: str) -> DataFrame:
    """Read SOP Markdown files, one row per document."""
    return (
        spark.read.format("binaryFile").option("pathGlobFilter", "*.md").load(path)
        .select(
            F.col("path").alias("_source_file"),
            F.decode(F.col("content"), "UTF-8").alias("content"),
            F.col("modificationTime").alias("file_modified_at"),
        )
        .withColumn("_ingested_at", F.current_timestamp())
    )


# ---------------------------------------------------------------------------------------
# Silver: typed, de-duplicated, quality-flagged, ready for chunking and indexing
# ---------------------------------------------------------------------------------------
def silver_ooc_events(bronze_events: DataFrame, bronze_root_causes: DataFrame) -> DataFrame:
    note = F.trim(F.col("closure_note"))
    vague = F.lower(note).isin([v.lower() for v in VAGUE_NOTES])
    rc = bronze_root_causes.select(
        F.col("root_cause_code").alias("_rc_code"), "root_cause_name", F.col("sop_id").alias("root_cause_sop_id")
    )
    df = (
        bronze_events
        .dropDuplicates(["event_id"])
        .select(
            "event_id",
            F.to_timestamp("event_ts").alias("event_ts"),
            "tool_id", "module",
            F.when(F.trim(F.col("chamber")) == "", None).otherwise(F.trim(F.col("chamber"))).alias("chamber"),
            "parameter", "parameter_name", "unit",
            F.col("value").cast("double").alias("value"),
            "spc_rule", "lot_id", "engineer",
            F.when(F.trim(F.col("root_cause_code")) == "", None).otherwise(F.trim(F.col("root_cause_code"))).alias("root_cause_code"),
            note.alias("closure_note"),
            F.col("downtime_hours").cast("double").alias("downtime_hours"),
            F.to_timestamp("closed_ts").alias("closed_ts"),
            "_source_file",
        )
        .join(rc, F.col("root_cause_code") == F.col("_rc_code"), "left")
        .drop("_rc_code")
        .withColumn(
            "note_quality",
            F.when(vague | (F.length(F.col("closure_note")) < MIN_NOTE_CHARS), F.lit("low")).otherwise(F.lit("ok")),
        )
        .withColumn("missing_root_cause_code", F.col("root_cause_code").isNull())
        # Only notes that can teach something go into the retrieval index.
        .withColumn("is_indexable", F.col("note_quality") == "ok")
        .withColumn(
            "retrieval_text",
            F.concat_ws(
                " | ",
                F.concat(F.lit("Past OOC event "), F.col("event_id"), F.lit(" on "), F.col("tool_id"),
                         F.coalesce(F.concat(F.lit(" chamber "), F.col("chamber")), F.lit("")),
                         F.lit(" ("), F.col("module"), F.lit(")")),
                F.concat(F.lit("Date: "), F.date_format("event_ts", "yyyy-MM-dd")),
                F.concat(F.lit("Symptom: "), F.col("parameter_name"), F.lit(" = "), F.col("value").cast("string"),
                         F.lit(" "), F.col("unit"), F.lit(", "), F.col("spc_rule")),
                F.concat(F.lit("Root cause: "),
                         F.coalesce(F.concat(F.col("root_cause_code"), F.lit(" "), F.col("root_cause_name")), F.lit("not coded"))),
                F.concat(F.lit("Closure note: "), F.col("closure_note")),
                F.concat(F.lit("Downtime: "), F.col("downtime_hours").cast("string"), F.lit(" h")),
            ),
        )
    )
    return df


def silver_sop_sections(bronze_docs: DataFrame) -> DataFrame:
    """Split each SOP into its '## ' sections: the natural chunk boundary for retrieval."""
    first_line = F.split(F.col("content"), "\n").getItem(0)
    docs = bronze_docs.select(
        F.regexp_extract(first_line, r"^# (SOP-[A-Z]+-\d{3}):", 1).alias("sop_id"),
        F.regexp_extract(first_line, r"^# SOP-[A-Z]+-\d{3}: (.*)$", 1).alias("sop_title"),
        F.regexp_extract(F.col("content"), r"\| Module \| ([^|]+) \|", 1).alias("module"),
        F.regexp_extract(F.col("content"), r"\| Revision \| ([^|]+) \|", 1).alias("revision"),
        F.split(F.col("content"), "\n## ").alias("parts"),
        "_source_file",
    )
    sections = (
        docs.select("sop_id", "sop_title", "module", "revision", "_source_file", F.posexplode("parts").alias("pos", "part"))
        .where(F.col("pos") > 0)  # part 0 is the title and metadata table
        .select(
            "sop_id", "sop_title", F.trim("module").alias("module"), F.trim("revision").alias("revision"),
            F.col("pos").alias("section_no"),
            F.trim(F.split(F.col("part"), "\n").getItem(0)).alias("section_title"),
            F.trim(F.regexp_replace(F.col("part"), r"^[^\n]*\n", "")).alias("section_text"),
            "_source_file",
        )
        .withColumn("chunk_id", F.concat_ws("#", F.col("sop_id"), F.lpad(F.col("section_no").cast("string"), 2, "0")))
        .withColumn("char_len", F.length("section_text"))
        .withColumn(
            "retrieval_text",
            F.concat(F.col("sop_id"), F.lit(" "), F.col("sop_title"), F.lit(" - "), F.col("section_title"),
                     F.lit("\n"), F.col("section_text")),
        )
    )
    return sections


def dq_scorecard(silver_events: DataFrame, sop_sections: DataFrame) -> DataFrame:
    """One-row summary of data quality, written alongside the Silver tables."""
    ev = silver_events.agg(
        F.count("*").alias("ooc_events"),
        F.sum(F.when(F.col("note_quality") == "low", 1).otherwise(0)).alias("low_quality_notes"),
        F.sum(F.when(F.col("missing_root_cause_code"), 1).otherwise(0)).alias("missing_root_cause_code"),
        F.sum(F.when(F.col("is_indexable"), 1).otherwise(0)).alias("indexable_events"),
    )
    sop = sop_sections.agg(
        F.countDistinct("sop_id").alias("sop_documents"),
        F.count("*").alias("sop_sections"),
        F.max("char_len").alias("max_section_chars"),
    )
    return (
        ev.crossJoin(sop)
        .withColumn("pct_low_quality_notes", F.round(F.col("low_quality_notes") / F.col("ooc_events") * 100, 1))
        .withColumn("pct_missing_root_cause_code", F.round(F.col("missing_root_cause_code") / F.col("ooc_events") * 100, 1))
        .withColumn("computed_at", F.current_timestamp())
    )
