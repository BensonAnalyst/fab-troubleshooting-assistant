# SOP-WET-003: Dryer (IPA/N2) Troubleshooting for Watermarks

| Field | Value |
|---|---|
| Document | SOP-WET-003 |
| Site | Northbridge Fab 1 (fictional) |
| Module | WET (Wet Clean) |
| Platform | Cascade C2 |
| Revision | C |
| Effective date | 2025-01-06 |
| Owner | Module process engineering |

> Synthetic document created for a portfolio project. It does not describe any real company's procedures.

## 1. Purpose

Diagnose and correct the condition: **Dryer problem causing watermarks**. Use this procedure when the symptoms below trigger an SPC out-of-control (OOC) event.

## 2. Scope

Applies to WET (Wet Clean) tools on the Cascade C2 platform at Northbridge Fab 1.

## 3. Symptoms (when to use this SOP)

- Watermark defects after the rinse/dry step.

Typical SPC parameters affected: `watermark_defects` (up).

## 4. Safety

- IPA is flammable.

## 5. Diagnostic checks

1. Check DI water resistivity (should be above 17.5 MOhm-cm).
2. Check dryer IPA flow and N2 flow against setpoints.

## 6. Corrective procedure

1. Restore IPA and N2 flow to setpoint (clean or replace the IPA nozzle).
2. If DI resistivity is low, raise a facilities request.
3. Run a defect monitor.

## 7. Acceptance criteria (release the tool only when all are met)

- Watermark defects at or below 3.

## 8. Parts

- IPA nozzle

## 9. Escalation

Escalate DI water issues to facilities.

## 10. Closure note requirements

Close the OOC with root cause code `RC-WET-03` and record: the symptom, the check that confirmed the cause, the corrective action and the requalification result.

## 11. Related documents

- SOP-GEN-001 (General OOC Response and Lot Disposition)
- SOP-MET-001 (Metrology Verification Before Process Tool Action)
- SOP-GEN-002 (Change Control and Requalification After PM or Recipe Edit)
