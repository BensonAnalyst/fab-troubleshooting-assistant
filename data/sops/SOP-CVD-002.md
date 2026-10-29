# SOP-CVD-002: CVD Particle Excursion Response

| Field | Value |
|---|---|
| Document | SOP-CVD-002 |
| Site | Northbridge Fab 1 (fictional) |
| Module | CVD (Chemical Vapour Deposition) |
| Platform | Halcyon H4 |
| Revision | C |
| Effective date | 2025-01-06 |
| Owner | Module process engineering |

> Synthetic document created for a portfolio project. It does not describe any real company's procedures.

## 1. Purpose

Diagnose and correct the condition: **Particle flaking from chamber walls or lid**. Use this procedure when the symptoms below trigger an SPC out-of-control (OOC) event.

## 2. Scope

Applies to CVD (Chemical Vapour Deposition) tools on the Halcyon H4 platform at Northbridge Fab 1.

## 3. Symptoms (when to use this SOP)

- Sudden jump in particle adders on monitor wafers.
- Random or edge-concentrated particle map; large flakes under SEM review.

Typical SPC parameters affected: `particle_adders` (up).

## 4. Safety

- Vent and LOTO required for wet clean. Handle chamber parts with gloves; deposits may be reactive.

## 5. Diagnostic checks

1. Classify the particle map pattern: random/large flakes (wall flaking), edge-heavy (lift pins or edge ring), cluster (handling).
2. Check the clean interval and whether the last clean or pre-coat was skipped.
3. Check the exhaust and foreline pressure for back-streaming.

## 6. Corrective procedure

1. Run an extended clean plus a thicker pre-coat (seasoning) to bury loose deposits.
2. Run 2 particle monitors. If adders are still high, perform a chamber wet clean.
3. For edge-heavy patterns, inspect and clean the lift pins.

## 7. Acceptance criteria (release the tool only when all are met)

- Particle adders at or below 20 on 2 consecutive monitors.
- No flake-type defects on SEM review.

## 8. Parts

- Chamber lid liner
- Lift pin set

## 9. Escalation

Escalate to the defect engineer if the particle source cannot be identified after a wet clean.

## 10. Closure note requirements

Close the OOC with root cause code `RC-CVD-02` and record: the symptom, the check that confirmed the cause, the corrective action and the requalification result.

## 11. Related documents

- SOP-GEN-001 (General OOC Response and Lot Disposition)
- SOP-MET-001 (Metrology Verification Before Process Tool Action)
- SOP-GEN-002 (Change Control and Requalification After PM or Recipe Edit)
