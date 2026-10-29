# SOP-ETCH-001: Chamber Dry Clean, Seasoning and Wet Clean Decision

| Field | Value |
|---|---|
| Document | SOP-ETCH-001 |
| Site | Northbridge Fab 1 (fictional) |
| Module | ETCH (Plasma Etch) |
| Platform | Kestrel K9 |
| Revision | C |
| Effective date | 2025-01-06 |
| Owner | Module process engineering |

> Synthetic document created for a portfolio project. It does not describe any real company's procedures.

## 1. Purpose

Diagnose and correct the condition: **Chamber wall polymer build-up (clean interval exceeded)**. Use this procedure when the symptoms below trigger an SPC out-of-control (OOC) event.

## 2. Scope

Applies to ETCH (Plasma Etch) tools on the Kestrel K9 platform at Northbridge Fab 1.

## 3. Symptoms (when to use this SOP)

- Etch rate drifting down slowly over several days, often flagged by a trend rule rather than a single point.
- Endpoint time creeping up on the same chamber.
- Particle adders rising on monitor wafers, sometimes with flakes visible on the chamber liner.

Typical SPC parameters affected: `etch_rate` (down), `endpoint_time` (up), `particle_adders` (up).

## 4. Safety

- Wet clean requires chamber vent and lock-out/tag-out (LOTO) of RF and gas.
- Wear chemical gloves and face shield when handling liner deposits; residues can be fluorinated polymer.

## 5. Diagnostic checks

1. Check RF hours since the last chamber wet clean in the tool PM counter. The Kestrel K9 wet clean interval is 1,200 RF hours.
2. Trend etch rate and endpoint time for the last 30 monitor wafers on this chamber only. A gradual slope points to build-up; a step change points elsewhere.
3. Inspect the chamber liner and window through the viewport for visible deposit or flaking.

## 6. Corrective procedure

1. Run the O2 dry clean recipe DC-O2-30 followed by 5 seasoning wafers.
2. Run 3 monitor wafers. If etch rate is back within +/-3% of baseline, release the chamber.
3. If RF hours since wet clean are above 1,100 or the dry clean does not recover etch rate, schedule a chamber wet clean PM (liner and window replacement).

## 7. Acceptance criteria (release the tool only when all are met)

- Etch rate within +/-3% of the chamber baseline on 3 consecutive monitor wafers.
- Particle adders at or below 15 on a bare-silicon particle monitor.
- Endpoint time within +/-2 s of baseline.

## 8. Parts

- Chamber liner kit (wet clean only)
- Viewport window (wet clean only)

## 9. Escalation

Escalate to the etch module owner if etch rate does not recover after a wet clean.

## 10. Closure note requirements

Close the OOC with root cause code `RC-ETCH-01` and record: the symptom, the check that confirmed the cause, the corrective action and the requalification result.

## 11. Related documents

- SOP-GEN-001 (General OOC Response and Lot Disposition)
- SOP-MET-001 (Metrology Verification Before Process Tool Action)
- SOP-GEN-002 (Change Control and Requalification After PM or Recipe Edit)
