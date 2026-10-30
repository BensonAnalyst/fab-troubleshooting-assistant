"""Databricks backends for the Assistant: AI Search, model serving and Spark SQL.

Imports of Databricks libraries happen inside the functions, so this module can be imported
(and the rest of the package tested) without them installed.
"""

import time

from .assistant import chat_text, parse_hits

SOP_COLUMNS = ["chunk_id", "sop_id", "sop_title", "section_title", "module_code", "retrieval_text"]
EVENT_COLUMNS = ["event_id", "tool_id", "module", "event_date", "root_cause_code", "retrieval_text"]
# Short, high-signal columns first: the reranker truncates the concatenated text at 2,000 characters.
RERANK_COLUMNS = {"sop": ["section_title", "retrieval_text"], "events": ["retrieval_text"]}


def make_search_fn(client, endpoint: str, index_names: dict, query_type: str = "HYBRID", rerank: bool = False):
    """search_fn(index, query, filters, k) over AI Search. index_names: {"sop": fq_name, "events": fq_name}."""
    columns = {"sop": SOP_COLUMNS, "events": EVENT_COLUMNS}
    cache = {}

    def search(index, query, filters, k):
        if index not in cache:
            cache[index] = client.get_index(endpoint_name=endpoint, index_name=index_names[index])
        kwargs = dict(query_text=query, columns=columns[index], filters=filters, num_results=k,
                      query_type=query_type, disable_notice=True)
        if rerank:
            from databricks.ai_search.reranker import DatabricksReranker
            kwargs["reranker"] = DatabricksReranker(columns_to_rerank=RERANK_COLUMNS[index])
        return parse_hits(cache[index].similarity_search(**kwargs))

    return search


def make_llm_fn(workspace_client, endpoint: str, max_tokens: int = 1500, retries: int = 4):
    """llm_fn(messages) -> text, with retries for rate limits and transient errors."""
    def llm(messages):
        body = {"messages": messages, "max_tokens": max_tokens, "temperature": 0}
        for attempt in range(retries):
            try:
                resp = workspace_client.api_client.do("POST", f"/serving-endpoints/{endpoint}/invocations", body=body)
                return chat_text(resp)
            except Exception:
                if attempt == retries - 1:
                    raise
                time.sleep(2 ** attempt * 3)

    return llm


def make_sections_fn(spark, gold_sop_table: str):
    """sections_fn(sop_id) -> that SOP's indexed sections, loaded once from the Gold table."""
    by_sop = {}
    for r in spark.table(gold_sop_table).select(*SOP_COLUMNS).collect():
        d = r.asDict()
        by_sop.setdefault(d["sop_id"], []).append(d)
    return lambda sop_id: by_sop.get(sop_id, [])


def make_sql_fn(spark, limit: int = 50):
    return lambda sql: [r.asDict() for r in spark.sql(sql).limit(limit).collect()]


def split_search_fn(sop_search_fn, event_search_fn):
    """Use a different retriever per index, e.g. keyword search for SOPs and hybrid search for past events."""
    def search(index, query, filters, k):
        return (sop_search_fn if index == "sop" else event_search_fn)(index, query, filters, k)

    return search
