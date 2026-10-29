import csv

import pytest

pyspark = pytest.importorskip("pyspark")
from pyspark.sql import SparkSession  # noqa: E402

from fabrag.generate import generate  # noqa: E402
from fabrag.knowledge import ROOT_CAUSES  # noqa: E402
from fabrag.silver import (dq_scorecard, read_bronze_csv, read_bronze_documents,  # noqa: E402
                           silver_ooc_events, silver_sop_sections)


@pytest.fixture(scope="module")
def spark():
    s = (SparkSession.builder.master("local[2]").appName("fabrag-tests")
         .config("spark.sql.shuffle.partitions", "2").config("spark.ui.enabled", "false").getOrCreate())
    yield s
    s.stop()


@pytest.fixture(scope="module")
def built(spark, tmp_path_factory):
    out = tmp_path_factory.mktemp("data")
    generate(out, seed=42, n_events=450)
    events = silver_ooc_events(read_bronze_csv(spark, str(out / "raw" / "ooc_events.csv")),
                               read_bronze_csv(spark, str(out / "raw" / "root_causes.csv"))).cache()
    sections = silver_sop_sections(read_bronze_documents(spark, str(out / "sops"))).cache()
    return out, events, sections


def test_events_typed_and_unique(built):
    _, events, _ = built
    assert events.count() == 450
    assert events.select("event_id").distinct().count() == 450
    assert dict(events.dtypes)["event_ts"] == "timestamp"
    assert dict(events.dtypes)["value"] == "double"
    assert events.where("value IS NULL OR event_ts IS NULL").count() == 0


def test_note_quality_matches_ground_truth(built):
    out, events, _ = built
    with open(out / "ground_truth" / "ooc_ground_truth.csv", newline="") as f:
        truth = {r["event_id"]: r["low_quality_note"] == "True" for r in csv.DictReader(f)}
    flagged = {r["event_id"]: r["note_quality"] == "low" for r in events.select("event_id", "note_quality").collect()}
    assert flagged == truth  # the DQ rule catches every vague note and nothing else


def test_retrieval_text_never_null(built):
    _, events, _ = built
    assert events.where("retrieval_text IS NULL OR retrieval_text = ''").count() == 0
    sample = events.where("is_indexable").first()["retrieval_text"]
    assert sample.startswith("Past OOC event OOC-") and "Closure note:" in sample


def test_sop_sections(built):
    _, _, sections = built
    assert sections.select("sop_id").distinct().count() == len(ROOT_CAUSES) + 1
    assert sections.where("sop_id = '' OR section_title = '' OR section_text = ''").count() == 0
    assert sections.select("chunk_id").distinct().count() == sections.count()
    # 11 sections per troubleshooting SOP, 5 in the general SOP
    assert sections.count() == len(ROOT_CAUSES) * 11 + 5
    row = sections.where("sop_id = 'SOP-ETCH-002' AND section_no = 7").first()
    assert row["section_title"].startswith("7. Acceptance criteria")
    assert "2 mTorr/min" in row["section_text"]


def test_dq_scorecard(built):
    _, events, sections = built
    row = dq_scorecard(events, sections).first()
    assert row["ooc_events"] == 450
    assert row["indexable_events"] == 450 - row["low_quality_notes"]
    assert row["sop_documents"] == len(ROOT_CAUSES) + 1
