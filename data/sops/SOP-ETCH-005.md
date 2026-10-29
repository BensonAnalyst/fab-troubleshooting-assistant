# SOP-ETCH-005: Mass Flow Controller (MFC) Verification and Replacement

| Field | Value |
|---|---|
| Document | SOP-ETCH-005 |
| Site | Northbridge Fab 1 (fictional) |
| Module | ETCH (Plasma Etch) |
| Platform | Kestrel K9 |
| Revision | C |
| Effective date | 2025-01-06 |
| Owner | Module process engineering |

> Synthetic document created for a portfolio project. It does not describe any real company's procedures.

## 1. Purpose

Diagnose and correct the condition: **Process gas MFC drift**. Use this procedure when the symptoms below trigger an SPC out-of-control (OOC) event.

## 2. Scope

Applies to ETCH (Plasma Etch) tools on the Kestrel K9 platform at Northbridge Fab 1.

## 3. Symptoms (when to use this SOP)

- Step change in etch rate or endpoint time without a matching change in chamber hours.
- Selectivity or profile change on product wafers.

Typical SPC parameters affected: `etch_rate` (up), `endpoint_time` (down).

## 4. Safety

- Gas line work requires toxic gas LOTO and a gas detector check before and after.

## 5. Diagnostic checks

1. Run a rate-of-rise (ROR) flow verification on each process gas MFC.
2. Compare MFC readback against setpoint in the gas panel log for the last 7 days.
3. Check for recent gas bottle or gas line work.

## 6. Corrective procedure

1. If an MFC deviates more than 2% on ROR, recalibrate it; if it deviates more than 5%, replace it.
2. Purge the gas line after any MFC replacement.
3. Requalify etch rate on 3 monitor wafers.

## 7. Acceptance criteria (release the tool only when all are met)

- All MFCs within +/-2% of setpoint on rate-of-rise verification.
- Etch rate within +/-3% of baseline.

## 8. Parts

- Mass flow controller (C4F8 / CF4 / O2 / Ar)

## 9. Escalation

Escalate to gas facilities if the drift is on the supply side.

## 10. Closure note requirements

Close the OOC with root cause code `RC-ETCH-05` and record: the symptom, the check that confirmed the cause, the corrective action and the requalification result.

## 11. Related documents

- SOP-GEN-001 (General OOC Response and Lot Disposition)
- SOP-MET-001 (Metrology Verification Before Process Tool Action)
- SOP-GEN-002 (Change Control and Requalification After PM or Recipe Edit)
