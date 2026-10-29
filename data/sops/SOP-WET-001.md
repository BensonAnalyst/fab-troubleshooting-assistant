# SOP-WET-001: Wet Bench Bath Change and Concentration Check

| Field | Value |
|---|---|
| Document | SOP-WET-001 |
| Site | Northbridge Fab 1 (fictional) |
| Module | WET (Wet Clean) |
| Platform | Cascade C2 |
| Revision | C |
| Effective date | 2025-01-06 |
| Owner | Module process engineering |

> Synthetic document created for a portfolio project. It does not describe any real company's procedures.

## 1. Purpose

Diagnose and correct the condition: **Bath chemical concentration out of range (aged bath)**. Use this procedure when the symptoms below trigger an SPC out-of-control (OOC) event.

## 2. Scope

Applies to WET (Wet Clean) tools on the Cascade C2 platform at Northbridge Fab 1.

## 3. Symptoms (when to use this SOP)

- Oxide etch rate drifting down as the bath ages.

Typical SPC parameters affected: `oxide_etch_rate` (down).

## 4. Safety

- Bath change uses HF: full chemical PPE and buddy system.

## 5. Diagnostic checks

1. Check bath age (wafer count and hours since change). Bath life is 2,000 wafers or 48 hours.
2. Check the concentration monitor or run a titration.

## 6. Corrective procedure

1. Change the bath.
2. Run 1 etch rate monitor after the bath stabilises (30 minutes).

## 7. Acceptance criteria (release the tool only when all are met)

- Oxide etch rate within +/-4% of baseline.

## 8. Parts

- None.

## 9. Escalation

Escalate to chemical facilities for supply concentration issues.

## 10. Closure note requirements

Close the OOC with root cause code `RC-WET-01` and record: the symptom, the check that confirmed the cause, the corrective action and the requalification result.

## 11. Related documents

- SOP-GEN-001 (General OOC Response and Lot Disposition)
- SOP-MET-001 (Metrology Verification Before Process Tool Action)
- SOP-GEN-002 (Change Control and Requalification After PM or Recipe Edit)
