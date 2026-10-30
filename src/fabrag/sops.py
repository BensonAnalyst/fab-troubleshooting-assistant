"""Renders the fictional SOP library as Markdown documents (the RAG knowledge source)."""

from .knowledge import FAB_NAME, GENERAL_SOP, MODULES, ROOT_CAUSES

EFFECTIVE_DATE = "2025-01-06"

# Sections with little troubleshooting content. They stay in Silver but are not indexed,
# because in Week 2 they took retrieval slots from Checks, Procedure and Acceptance criteria.
LOW_VALUE_SECTION_PREFIXES = ("1. Purpose", "2. Scope", "11. Related documents")


def _header(sop_id, title, module_label, platform, revision="C"):
    return (
        f"# {sop_id}: {title}\n\n"
        f"| Field | Value |\n|---|---|\n"
        f"| Document | {sop_id} |\n"
        f"| Site | {FAB_NAME} (fictional) |\n"
        f"| Module | {module_label} |\n"
        f"| Platform | {platform} |\n"
        f"| Revision | {revision} |\n"
        f"| Effective date | {EFFECTIVE_DATE} |\n"
        f"| Owner | Module process engineering |\n\n"
        "> Synthetic document created for a portfolio project. It does not describe any real company's procedures.\n\n"
    )


def _bullets(items):
    return "\n".join(f"- {i}" for i in items) + "\n"


def _numbered(items):
    return "\n".join(f"{n}. {i}" for n, i in enumerate(items, 1)) + "\n"


def render_rc_sop(rc):
    if rc["module"] == "ANY":
        module_label, platform = "All modules", "All platforms"
    else:
        m = MODULES[rc["module"]]
        module_label, platform = f"{rc['module']} ({m['name']})", m["platform"]
    related = ["SOP-GEN-001 (General OOC Response and Lot Disposition)"]
    if rc["rc_id"] != "RC-MET-01":
        related.append("SOP-MET-001 (Metrology Verification Before Process Tool Action)")
    if rc["rc_id"] != "RC-GEN-01":
        related.append("SOP-GEN-002 (Change Control and Requalification After PM or Recipe Edit)")

    doc = _header(rc["sop_id"], rc["sop_title"], module_label, platform)
    doc += (
        "## 1. Purpose\n\n"
        f"Diagnose and correct the condition: **{rc['name']}**. Use this procedure when the symptoms below "
        "trigger an SPC out-of-control (OOC) event.\n\n"
    )
    doc += f"## 2. Scope\n\nApplies to {module_label} tools on the {platform} platform at {FAB_NAME}.\n\n"
    doc += "## 3. Symptoms (when to use this SOP)\n\n" + _bullets(rc["symptoms"]) + "\n"
    if rc["params"]:
        doc += "Typical SPC parameters affected: " + ", ".join(
            f"`{p}` ({'up' if d > 0 else 'down'})" for p, d in rc["params"]
        ) + ".\n\n"
    doc += "## 4. Safety\n\n" + (_bullets(rc["safety"]) if rc["safety"] else "- No special hazards beyond standard cleanroom practice.\n") + "\n"
    doc += "## 5. Diagnostic checks\n\n" + _numbered(rc["checks"]) + "\n"
    doc += "## 6. Corrective procedure\n\n" + _numbered(rc["fix"]) + "\n"
    doc += "## 7. Acceptance criteria (release the tool only when all are met)\n\n" + _bullets(rc["accept"]) + "\n"
    doc += "## 8. Parts\n\n" + (_bullets(rc["parts"]) if rc["parts"] else "- None.\n") + "\n"
    doc += f"## 9. Escalation\n\n{rc['escalate']}\n\n"
    doc += (
        "## 10. Closure note requirements\n\n"
        f"Close the OOC with root cause code `{rc['rc_id']}` and record: the symptom, the check that confirmed the cause, "
        "the corrective action and the requalification result.\n\n"
    )
    doc += "## 11. Related documents\n\n" + _bullets(related)
    return doc


def render_general_sop():
    doc = _header(GENERAL_SOP["sop_id"], GENERAL_SOP["sop_title"], "All modules", "All platforms", revision="D")
    doc += (
        "## 1. Purpose\n\n"
        "Define the standard response to any SPC out-of-control (OOC) event, from first alarm to closure, "
        "so that lots are protected and every OOC leaves a usable record.\n\n"
        "## 2. Response steps\n\n"
        "1. **Hold** the affected lot and stop further processing on the tool or chamber that produced the OOC point.\n"
        "2. **Verify the measurement first** using SOP-MET-001. Around 1 in 10 OOC events are metrology false alarms; "
        "do not touch the process tool until the reading is confirmed.\n"
        "3. **Check for recent changes** (recipe edits, PMs, part changes in the last 24 hours) using SOP-GEN-002.\n"
        "4. **Use the module troubleshooting SOP** that matches the symptom pattern (see the index below).\n"
        "5. **Requalify** the tool against the acceptance criteria of that SOP.\n"
        "6. **Disposition** held lots: release, rework, or scrap with the module engineer's approval.\n"
        "7. **Close the OOC** with a root cause code and a complete closure note.\n\n"
        "## 3. Response time targets\n\n"
        "- Acknowledge the OOC within 15 minutes.\n"
        "- First diagnosis (cause suspected) within 2 hours.\n"
        "- Tool down longer than 8 hours must be escalated to the module manager.\n\n"
        "## 4. Closure note standard\n\n"
        "A closure note must contain four parts, so that future engineers can search it:\n\n"
        "1. **Symptom**: parameter, value, SPC rule triggered.\n"
        "2. **Root cause**: the confirmed cause and the check that confirmed it, plus the root cause code.\n"
        "3. **Action**: what was done, including part numbers replaced.\n"
        "4. **Verification**: the requalification result.\n\n"
        "Notes such as \"fixed\", \"ok now\" or \"see shift log\" are not acceptable closures.\n\n"
        "## 5. Troubleshooting SOP index\n\n"
        "| Root cause code | SOP | Module | Title |\n|---|---|---|---|\n"
    )
    for rc in ROOT_CAUSES:
        doc += f"| {rc['rc_id']} | {rc['sop_id']} | {rc['module']} | {rc['sop_title']} |\n"
    return doc


def render_all():
    """Return {filename: markdown} for every SOP."""
    docs = {f"{GENERAL_SOP['sop_id']}.md": render_general_sop()}
    for rc in ROOT_CAUSES:
        docs[f"{rc['sop_id']}.md"] = render_rc_sop(rc)
    return docs
