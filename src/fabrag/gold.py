"""Silver -> Gold: the exact tables the AI Search indexes sync from.

Each Gold table holds only what retrieval needs: a primary key, the text to embed, and the
columns used as search filters. Low-quality closure notes are dropped here.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def gold_sop_chunks(silver_sections: DataFrame) -> DataFrame:
    module_code = F.regexp_extract("sop_id", r"^SOP-([A-Z]+)-", 1)
    return silver_sections.select(
        "chunk_id", "sop_id", "sop_title", "section_title",
        # General and metrology SOPs apply to every module.
        F.when(module_code.isin("ETCH", "CVD", "CMP", "LITH", "WET"), module_code).otherwise(F.lit("ANY")).alias("module_code"),
        "retrieval_text",
    )


def gold_event_chunks(silver_events: DataFrame) -> DataFrame:
    return (
        silver_events.where("is_indexable")
        .select(
            "event_id", "tool_id", "module",
            F.date_format("event_ts", "yyyy-MM-dd").alias("event_date"),
            "root_cause_code", "retrieval_text",
        )
    )
