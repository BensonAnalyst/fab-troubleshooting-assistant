# SOP-CMP-002: Slurry Delivery and Filter Troubleshooting

| Field | Value |
|---|---|
| Document | SOP-CMP-002 |
| Site | Northbridge Fab 1 (fictional) |
| Module | CMP (Chemical Mechanical Planarization) |
| Platform | Polaris P3 |
| Revision | C |
| Effective date | 2025-01-06 |
| Owner | Module process engineering |

> Synthetic document created for a portfolio project. It does not describe any real company's procedures.

## 1. Purpose

Diagnose and correct the condition: **Slurry delivery problem or agglomeration**. Use this procedure when the symptoms below trigger an SPC out-of-control (OOC) event.

## 2. Scope

Applies to CMP (Chemical Mechanical Planarization) tools on the Polaris P3 platform at Northbridge Fab 1.

## 3. Symptoms (when to use this SOP)

- Scratch defects jumping, often arc-shaped (micro-scratches).
- Removal rate unstable.

Typical SPC parameters affected: `scratch_count` (up), `removal_rate` (down).

## 4. Safety

- Slurry is a chemical: gloves and goggles for filter change.

## 5. Diagnostic checks

1. Check slurry flow rate at the point of use against the recipe.
2. Check POU filter differential pressure and last filter change date.
3. Check slurry lot, age and mixing tank recirculation.

## 6. Corrective procedure

1. Replace the POU filter and flush the slurry line.
2. Verify slurry flow with the flow-check routine.
3. If a new slurry lot was introduced, quarantine the lot and return to the previous lot.

## 7. Acceptance criteria (release the tool only when all are met)

- Scratch defects at or below 5 on 2 defect monitors.
- Slurry flow within +/-5% of setpoint.

## 8. Parts

- POU slurry filter

## 9. Escalation

Escalate to the slurry supplier through the materials engineer for suspected bad lots.

## 10. Closure note requirements

Close the OOC with root cause code `RC-CMP-02` and record: the symptom, the check that confirmed the cause, the corrective action and the requalification result.

## 11. Related documents

- SOP-GEN-001 (General OOC Response and Lot Disposition)
- SOP-MET-001 (Metrology Verification Before Process Tool Action)
- SOP-GEN-002 (Change Control and Requalification After PM or Recipe Edit)
