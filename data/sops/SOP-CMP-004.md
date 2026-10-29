# SOP-CMP-004: Optical Endpoint Verification

| Field | Value |
|---|---|
| Document | SOP-CMP-004 |
| Site | Northbridge Fab 1 (fictional) |
| Module | CMP (Chemical Mechanical Planarization) |
| Platform | Polaris P3 |
| Revision | C |
| Effective date | 2025-01-06 |
| Owner | Module process engineering |

> Synthetic document created for a portfolio project. It does not describe any real company's procedures.

## 1. Purpose

Diagnose and correct the condition: **Optical endpoint sensor drift or clouded pad window**. Use this procedure when the symptoms below trigger an SPC out-of-control (OOC) event.

## 2. Scope

Applies to CMP (Chemical Mechanical Planarization) tools on the Polaris P3 platform at Northbridge Fab 1.

## 3. Symptoms (when to use this SOP)

- Dishing increasing because wafers are over-polished.
- Endpoint trace looks noisy or flat compared with the reference trace.

Typical SPC parameters affected: `dishing` (up).

## 4. Safety

- Platen LOTO before window inspection.

## 5. Diagnostic checks

1. Compare recent endpoint traces against the golden reference trace.
2. Inspect the pad window for clouding or slurry residue.
3. Check endpoint light source intensity.

## 6. Corrective procedure

1. Clean the pad window; replace the pad if the window is permanently clouded.
2. Recalibrate the endpoint system with the calibration wafer.
3. Run 2 dishing monitors.

## 7. Acceptance criteria (release the tool only when all are met)

- Dishing at or below 420 A.
- Endpoint signal-to-noise within reference limits.

## 8. Parts

- Endpoint light source
- Polishing pad (window)

## 9. Escalation

Escalate to the CMP process owner if traces still deviate after calibration.

## 10. Closure note requirements

Close the OOC with root cause code `RC-CMP-04` and record: the symptom, the check that confirmed the cause, the corrective action and the requalification result.

## 11. Related documents

- SOP-GEN-001 (General OOC Response and Lot Disposition)
- SOP-MET-001 (Metrology Verification Before Process Tool Action)
- SOP-GEN-002 (Change Control and Requalification After PM or Recipe Edit)
