# SOP-MET-001: Metrology Verification Before Process Tool Action

| Field | Value |
|---|---|
| Document | SOP-MET-001 |
| Site | Northbridge Fab 1 (fictional) |
| Module | All modules |
| Platform | All platforms |
| Revision | C |
| Effective date | 2025-01-06 |
| Owner | Module process engineering |

> Synthetic document created for a portfolio project. It does not describe any real company's procedures.

## 1. Purpose

Diagnose and correct the condition: **Metrology false alarm (measurement tool error)**. Use this procedure when the symptoms below trigger an SPC out-of-control (OOC) event.

## 2. Scope

Applies to All modules tools on the All platforms platform at Northbridge Fab 1.

## 3. Symptoms (when to use this SOP)

- Single OOC point with no supporting trend, often on one metrology tool only.
- Re-measurement gives a normal value.

## 4. Safety

- No special hazards beyond standard cleanroom practice.

## 5. Diagnostic checks

1. Re-measure the wafer on a second metrology tool, or measure the golden reference wafer on the same tool.
2. Check the metrology tool's own calibration status.

## 6. Corrective procedure

1. If the re-measurement is in control, close the OOC as a metrology false alarm: no process tool action.
2. Raise a metrology calibration request for the measuring tool.
3. Release the held lot after the re-measurement.

## 7. Acceptance criteria (release the tool only when all are met)

- Re-measured value in control on a second metrology tool or golden wafer.

## 8. Parts

- None.

## 9. Escalation

Escalate to metrology if the golden wafer reads out of range.

## 10. Closure note requirements

Close the OOC with root cause code `RC-MET-01` and record: the symptom, the check that confirmed the cause, the corrective action and the requalification result.

## 11. Related documents

- SOP-GEN-001 (General OOC Response and Lot Disposition)
- SOP-GEN-002 (Change Control and Requalification After PM or Recipe Edit)
