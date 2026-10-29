# SOP-LITH-003: Dose Calibration and Laser Energy Check

| Field | Value |
|---|---|
| Document | SOP-LITH-003 |
| Site | Northbridge Fab 1 (fictional) |
| Module | LITH (Lithography) |
| Platform | Meridian M7 |
| Revision | C |
| Effective date | 2025-01-06 |
| Owner | Module process engineering |

> Synthetic document created for a portfolio project. It does not describe any real company's procedures.

## 1. Purpose

Diagnose and correct the condition: **Exposure dose drift**. Use this procedure when the symptoms below trigger an SPC out-of-control (OOC) event.

## 2. Scope

Applies to LITH (Lithography) tools on the Meridian M7 platform at Northbridge Fab 1.

## 3. Symptoms (when to use this SOP)

- Resist CD mean shifting across all fields while focus is normal.

Typical SPC parameters affected: `cd_mean` (up).

## 4. Safety

- Laser service only by the vendor.

## 5. Diagnostic checks

1. Check the dose monitor and the laser energy log for drift.
2. Confirm the resist lot did not change.

## 6. Corrective procedure

1. Run dose calibration.
2. If laser energy is unstable, raise a laser service request.
3. Expose a CD monitor wafer.

## 7. Acceptance criteria (release the tool only when all are met)

- Resist CD mean within 44.0 to 46.0 nm.

## 8. Parts

- None.

## 9. Escalation

Escalate to the vendor for laser energy instability.

## 10. Closure note requirements

Close the OOC with root cause code `RC-LITH-03` and record: the symptom, the check that confirmed the cause, the corrective action and the requalification result.

## 11. Related documents

- SOP-GEN-001 (General OOC Response and Lot Disposition)
- SOP-MET-001 (Metrology Verification Before Process Tool Action)
- SOP-GEN-002 (Change Control and Requalification After PM or Recipe Edit)
