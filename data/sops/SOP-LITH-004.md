# SOP-LITH-004: Resist Coat Thickness Troubleshooting (Track)

| Field | Value |
|---|---|
| Document | SOP-LITH-004 |
| Site | Northbridge Fab 1 (fictional) |
| Module | LITH (Lithography) |
| Platform | Meridian M7 |
| Revision | C |
| Effective date | 2025-01-06 |
| Owner | Module process engineering |

> Synthetic document created for a portfolio project. It does not describe any real company's procedures.

## 1. Purpose

Diagnose and correct the condition: **Track resist coat problem (nozzle or hotplate)**. Use this procedure when the symptoms below trigger an SPC out-of-control (OOC) event.

## 2. Scope

Applies to LITH (Lithography) tools on the Meridian M7 platform at Northbridge Fab 1.

## 3. Symptoms (when to use this SOP)

- Resist thickness out of range or non-uniform.
- CD shift linked to a specific coat or bake module.

Typical SPC parameters affected: `resist_thickness` (up), `cd_mean` (down).

## 4. Safety

- Resist is flammable: no ignition sources; use solvent-rated gloves.

## 5. Diagnostic checks

1. Check resist thickness monitors by coat module.
2. Inspect the dispense nozzle for dried resist or a drip.
3. Check hotplate temperature uniformity with the calibration wafer.

## 6. Corrective procedure

1. Clean the dispense nozzle and run a dummy dispense.
2. Recalibrate the hotplate if uniformity is out.
3. Run a resist thickness monitor.

## 7. Acceptance criteria (release the tool only when all are met)

- Resist thickness within 1,180 to 1,220 A.
- Hotplate uniformity within +/-0.3 C.

## 8. Parts

- Dispense nozzle

## 9. Escalation

Escalate to the track vendor if the hotplate cannot be calibrated.

## 10. Closure note requirements

Close the OOC with root cause code `RC-LITH-04` and record: the symptom, the check that confirmed the cause, the corrective action and the requalification result.

## 11. Related documents

- SOP-GEN-001 (General OOC Response and Lot Disposition)
- SOP-MET-001 (Metrology Verification Before Process Tool Action)
- SOP-GEN-002 (Change Control and Requalification After PM or Recipe Edit)
