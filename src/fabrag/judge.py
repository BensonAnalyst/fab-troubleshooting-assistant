"""LLM judge: scores each written answer for coverage of the expected points and for groundedness.

Coverage: which expected answer points the answer states (correctness against ground truth).
Groundedness: whether every factual claim in the answer is supported by the sources it was given.

The judge returns JSON; parsing is defensive because models sometimes wrap JSON in prose or fences.
"""

import json
import re

from .assistant import FAB_POLICY

JUDGE_PROMPT = """You are grading an answer from a wafer-fab troubleshooting assistant. Be strict and literal.

QUESTION:
{question}

EXPECTED POINTS (the answer should state each of these, in any wording):
{points}

FAB POLICY THE ASSISTANT IS ALLOWED TO STATE WITHOUT A SOURCE (stating these is supported):
{policy}

SOURCES THE ASSISTANT WAS GIVEN:
{sources}

ANSWER TO GRADE:
{answer}

Grade two things.
1. covered: for each expected point, in order, true if the answer states it (equivalent wording counts), else false.
   For a point listing several event IDs, true only if the answer lists all of them.
2. grounded: true if EVERY factual claim in the answer (causes, values, limits, steps, part names, event details) is supported by the sources above. A claim not found in the sources makes it false. Saying that something is "not in the retrieved sources" is not a claim.

Reply with JSON only, no other text:
{{"covered": [true, false, ...], "grounded": true, "unsupported_claims": ["..."], "reason": "one short sentence"}}
Keep the reason under 25 words."""


def build_judge_messages(question: str, points: list, sources_text: str, answer: str) -> list:
    pts = "\n".join(f"{i}. {p}" for i, p in enumerate(points, 1))
    content = JUDGE_PROMPT.format(question=question, points=pts, policy=FAB_POLICY,
                                 sources=sources_text or "(none)", answer=answer)
    return [{"role": "user", "content": content}]


def _salvage(text: str):
    """Recover covered/grounded from a reply cut off before the closing brace (token limit hit)."""
    cov = re.search(r'"covered"\s*:\s*\[([^\]]*)\]', text)
    grd = re.search(r'"grounded"\s*:\s*(true|false)', text)
    if not (cov and grd):
        return None
    return {"covered": [x.strip() == "true" for x in cov.group(1).split(",") if x.strip()],
            "grounded": grd.group(1) == "true", "reason": "(reply truncated; scores recovered)"}


def parse_judgement(raw: str, n_points: int) -> dict:
    """Return {coverage, grounded, unsupported_claims, reason, judge_error}."""
    text = re.sub(r"```(?:json)?", "", raw or "").strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    try:
        data = json.loads(match.group(0)) if match else None
    except json.JSONDecodeError:
        data = None
    if not isinstance(data, dict):
        data = _salvage(text)
    if not isinstance(data, dict):
        return {"coverage": None, "grounded": None, "unsupported_claims": [], "reason": None,
                "judge_error": f"unparseable judge output: {(raw or '')[:200]}"}
    covered = [bool(x) for x in (data.get("covered") or [])][:n_points]
    covered += [False] * (n_points - len(covered))
    grounded = data.get("grounded")
    return {
        "coverage": round(sum(covered) / n_points, 3) if n_points else None,
        "grounded": grounded if isinstance(grounded, bool) else None,
        "unsupported_claims": [str(c) for c in (data.get("unsupported_claims") or [])][:10],
        "reason": data.get("reason"),
        "judge_error": None,
    }


def judge_answer(llm_fn, question: str, points: list, sources_text: str, answer: str) -> dict:
    raw = llm_fn(build_judge_messages(question, points, sources_text, answer))
    return parse_judgement(raw, len(points))


def judge_metrics(judged: list) -> dict:
    """judged: list of dicts with type, coverage, grounded (from parse_judgement), for answered questions."""
    def mean(xs):
        xs = [x for x in xs if x is not None]
        return round(sum(xs) / len(xs), 3) if xs else None

    out = {
        "answer_coverage": mean(j["coverage"] for j in judged),
        "groundedness_rate": mean(float(j["grounded"]) for j in judged if j["grounded"] is not None),
        "judge_errors": sum(1 for j in judged if j.get("judge_error")),
    }
    for t in sorted({j["type"] for j in judged}):
        sub = [j for j in judged if j["type"] == t]
        out[f"answer_coverage_{t}"] = mean(j["coverage"] for j in sub)
    return out
