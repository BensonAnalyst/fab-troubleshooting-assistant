# SOP-CVD-004: Liquid Precursor Delivery Troubleshooting

| Field | Value |
|---|---|
| Document | SOP-CVD-004 |
| Site | Northbridge Fab 1 (fictional) |
| Module | CVD (Chemical Vapour Deposition) |
| Platform | Halcyon H4 |
| Revision | C |
| Effective date | 2025-01-06 |
| Owner | Module process engineering |

> Synthetic document created for a portfolio project. It does not describe any real company's procedures.

## 1. Purpose

Diagnose and correct the condition: **Precursor delivery problem (ampoule low or line heater)**. Use this procedure when the symptoms below trigger an SPC out-of-control (OOC) event.

## 2. Scope

Applies to CVD (Chemical Vapour Deposition) tools on the Halcyon H4 platform at Northbridge Fab 1.

## 3. Symptoms (when to use this SOP)

- Sudden drop in deposition rate (thin film) on consecutive runs.
- Precursor flow readback noisy or below setpoint.

Typical SPC parameters affected: `film_thickness` (down), `thickness_uniformity` (up).

## 4. Safety

- Ampoule change follows the chemical handling procedure: PPE and two-person verification.

## 5. Diagnostic checks

1. Check the precursor ampoule level and the last ampoule change date.
2. Check vaporizer and line heater temperatures against setpoint.
3. Check the precursor flow readback for noise or drop-outs.

## 6. Corrective procedure

1. Replace the ampoule if the level is below 15%.
2. Repair or replace any line heater below setpoint; cold spots cause condensation.
3. Purge the delivery line and run 2 thickness monitors.

## 7. Acceptance criteria (release the tool only when all are met)

- Thickness within +/-2% of target on 2 monitors.
- Precursor flow stable within +/-3% of setpoint.

## 8. Parts

- Precursor ampoule
- Line heater jacket

## 9. Escalation

Escalate to chemical facilities for supply issues.

## 10. Closure note requirements

Close the OOC with root cause code `RC-CVD-04` and record: the symptom, the check that confirmed the cause, the corrective action and the requalification result.

## 11. Related documents

- SOP-GEN-001 (General OOC Response and Lot Disposition)
- SOP-MET-001 (Metrology Verification Before Process Tool Action)
- SOP-GEN-002 (Change Control and Requalification After PM or Recipe Edit)
