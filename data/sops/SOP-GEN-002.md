# SOP-GEN-002: Change Control and Requalification After PM or Recipe Edit

| Field | Value |
|---|---|
| Document | SOP-GEN-002 |
| Site | Northbridge Fab 1 (fictional) |
| Module | All modules |
| Platform | All platforms |
| Revision | C |
| Effective date | 2025-01-06 |
| Owner | Module process engineering |

> Synthetic document created for a portfolio project. It does not describe any real company's procedures.

## 1. Purpose

Diagnose and correct the condition: **Unqualified change (recipe edit or PM without requalification)**. Use this procedure when the symptoms below trigger an SPC out-of-control (OOC) event.

## 2. Scope

Applies to All modules tools on the All platforms platform at Northbridge Fab 1.

## 3. Symptoms (when to use this SOP)

- Step change right after a recipe edit, a PM or a part change.

## 4. Safety

- No special hazards beyond standard cleanroom practice.

## 5. Diagnostic checks

1. Check the recipe change log and the PM log for changes in the 24 hours before the first OOC point.
2. Confirm whether requalification was completed and signed off after the change.

## 6. Corrective procedure

1. Revert the recipe to the last qualified version, or complete the missed requalification.
2. Hold the tool until requalification passes.
3. Record the change in the change-control log.

## 7. Acceptance criteria (release the tool only when all are met)

- Requalification passed and signed off by the module engineer.

## 8. Parts

- None.

## 9. Escalation

Escalate repeated change-control misses to the module manager.

## 10. Closure note requirements

Close the OOC with root cause code `RC-GEN-01` and record: the symptom, the check that confirmed the cause, the corrective action and the requalification result.

## 11. Related documents

- SOP-GEN-001 (General OOC Response and Lot Disposition)
- SOP-MET-001 (Metrology Verification Before Process Tool Action)
