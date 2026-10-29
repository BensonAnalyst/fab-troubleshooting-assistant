# SOP-LITH-002: Wafer Chuck Cleaning for Focus Hot Spots

| Field | Value |
|---|---|
| Document | SOP-LITH-002 |
| Site | Northbridge Fab 1 (fictional) |
| Module | LITH (Lithography) |
| Platform | Meridian M7 |
| Revision | C |
| Effective date | 2025-01-06 |
| Owner | Module process engineering |

> Synthetic document created for a portfolio project. It does not describe any real company's procedures.

## 1. Purpose

Diagnose and correct the condition: **Wafer chuck contamination (focus hot spot)**. Use this procedure when the symptoms below trigger an SPC out-of-control (OOC) event.

## 2. Scope

Applies to LITH (Lithography) tools on the Meridian M7 platform at Northbridge Fab 1.

## 3. Symptoms (when to use this SOP)

- Focus error spikes at the same location on every wafer (repeating hot spot).
- Local CD defects at that location.

Typical SPC parameters affected: `focus_error` (up).

## 4. Safety

- Chuck cleaning only by certified technicians; scanner in maintenance mode.

## 5. Diagnostic checks

1. Overlay several wafers' focus maps: a hot spot at a fixed chuck position indicates chuck contamination.
2. Check if the hot spot moves with the wafer (wafer backside particle) or stays fixed (chuck).

## 6. Corrective procedure

1. Clean the wafer chuck with the approved chuck cleaning stone and wipe procedure.
2. Run a focus monitor wafer to confirm the hot spot is gone.
3. If the hot spot moved with the wafer, trace the upstream tool for backside contamination instead.

## 7. Acceptance criteria (release the tool only when all are met)

- Focus error (max) at or below 30 nm with no repeating hot spot.

## 8. Parts

- Chuck cleaning stone

## 9. Escalation

Escalate if the hot spot persists after 2 chuck cleans.

## 10. Closure note requirements

Close the OOC with root cause code `RC-LITH-02` and record: the symptom, the check that confirmed the cause, the corrective action and the requalification result.

## 11. Related documents

- SOP-GEN-001 (General OOC Response and Lot Disposition)
- SOP-MET-001 (Metrology Verification Before Process Tool Action)
- SOP-GEN-002 (Change Control and Requalification After PM or Recipe Edit)
