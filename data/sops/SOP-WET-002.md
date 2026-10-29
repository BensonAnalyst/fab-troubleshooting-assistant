# SOP-WET-002: Wet Bench Filter Change and Particle Response

| Field | Value |
|---|---|
| Document | SOP-WET-002 |
| Site | Northbridge Fab 1 (fictional) |
| Module | WET (Wet Clean) |
| Platform | Cascade C2 |
| Revision | C |
| Effective date | 2025-01-06 |
| Owner | Module process engineering |

> Synthetic document created for a portfolio project. It does not describe any real company's procedures.

## 1. Purpose

Diagnose and correct the condition: **Recirculation filter or pump shedding particles**. Use this procedure when the symptoms below trigger an SPC out-of-control (OOC) event.

## 2. Scope

Applies to WET (Wet Clean) tools on the Cascade C2 platform at Northbridge Fab 1.

## 3. Symptoms (when to use this SOP)

- Particle adders rising after wet clean; filter differential pressure high.

Typical SPC parameters affected: `particle_adders` (up).

## 4. Safety

- Drain and rinse the bath before opening the recirculation loop.

## 5. Diagnostic checks

1. Check recirculation filter differential pressure and change date.
2. Check recirculation pump for noise or seal wear.

## 6. Corrective procedure

1. Replace the recirculation filter and flush the loop.
2. Replace the pump seal if worn.
3. Run 2 particle monitors.

## 7. Acceptance criteria (release the tool only when all are met)

- Particle adders at or below 15 on 2 monitors.

## 8. Parts

- Recirculation filter
- Pump seal kit

## 9. Escalation

Escalate to the defect engineer if adders persist.

## 10. Closure note requirements

Close the OOC with root cause code `RC-WET-02` and record: the symptom, the check that confirmed the cause, the corrective action and the requalification result.

## 11. Related documents

- SOP-GEN-001 (General OOC Response and Lot Disposition)
- SOP-MET-001 (Metrology Verification Before Process Tool Action)
- SOP-GEN-002 (Change Control and Requalification After PM or Recipe Edit)
