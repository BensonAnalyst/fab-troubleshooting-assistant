# SOP-LITH-001: Overlay Excursion Response and Stage Calibration

| Field | Value |
|---|---|
| Document | SOP-LITH-001 |
| Site | Northbridge Fab 1 (fictional) |
| Module | LITH (Lithography) |
| Platform | Meridian M7 |
| Revision | C |
| Effective date | 2025-01-06 |
| Owner | Module process engineering |

> Synthetic document created for a portfolio project. It does not describe any real company's procedures.

## 1. Purpose

Diagnose and correct the condition: **Overlay drift from stage or alignment calibration**. Use this procedure when the symptoms below trigger an SPC out-of-control (OOC) event.

## 2. Scope

Applies to LITH (Lithography) tools on the Meridian M7 platform at Northbridge Fab 1.

## 3. Symptoms (when to use this SOP)

- Overlay (mean+3s) creeping up on the daily monitor.
- Systematic overlay signature (translation, rotation or scaling) rather than random scatter.

Typical SPC parameters affected: `overlay_x` (up), `overlay_y` (up).

## 4. Safety

- No hardware access needed; follow scanner software access controls.

## 5. Diagnostic checks

1. Check the daily overlay monitor trend and decompose into translation, rotation and magnification terms.
2. Check alignment mark quality on the affected layer.
3. Check when the stage and alignment calibrations last ran.

## 6. Corrective procedure

1. Run the stage grid and alignment calibration routines.
2. Update the overlay correction (APC) parameters after calibration.
3. Expose and measure 1 overlay monitor wafer.

## 7. Acceptance criteria (release the tool only when all are met)

- Overlay (mean+3s) at or below 5.0 nm in X and Y.

## 8. Parts

- None.

## 9. Escalation

Escalate to the scanner vendor if the stage calibration fails.

## 10. Closure note requirements

Close the OOC with root cause code `RC-LITH-01` and record: the symptom, the check that confirmed the cause, the corrective action and the requalification result.

## 11. Related documents

- SOP-GEN-001 (General OOC Response and Lot Disposition)
- SOP-MET-001 (Metrology Verification Before Process Tool Action)
- SOP-GEN-002 (Change Control and Requalification After PM or Recipe Edit)
