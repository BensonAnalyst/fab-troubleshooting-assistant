# SOP-ETCH-002: Focus Ring Inspection and Replacement

| Field | Value |
|---|---|
| Document | SOP-ETCH-002 |
| Site | Northbridge Fab 1 (fictional) |
| Module | ETCH (Plasma Etch) |
| Platform | Kestrel K9 |
| Revision | C |
| Effective date | 2025-01-06 |
| Owner | Module process engineering |

> Synthetic document created for a portfolio project. It does not describe any real company's procedures.

## 1. Purpose

Diagnose and correct the condition: **Focus (edge) ring erosion**. Use this procedure when the symptoms below trigger an SPC out-of-control (OOC) event.

## 2. Scope

Applies to ETCH (Plasma Etch) tools on the Kestrel K9 platform at Northbridge Fab 1.

## 3. Symptoms (when to use this SOP)

- CD uniformity getting worse, with the wafer edge etching faster than the centre.
- 49-point map shows an edge-fast ring pattern; centre values normal.
- Usually gradual and correlated with focus ring RF hours approaching the life limit.

Typical SPC parameters affected: `cd_uniformity` (up), `etch_rate` (up).

## 4. Safety

- Chamber vent and LOTO required. Allow the chamber to cool below 40 C before opening.

## 5. Diagnostic checks

1. Check focus ring RF hours. The life limit is 800 RF hours on Kestrel K9.
2. Review the 49-point etch rate or CD map: an edge-fast pattern with a normal centre points to ring erosion.
3. Measure ring thickness at 4 points after venting, if the map is inconclusive.

## 6. Corrective procedure

1. Vent the chamber under LOTO and replace the focus ring.
2. Pump down, run a leak-up rate check, then run 5 seasoning wafers.
3. Requalify CD uniformity and etch rate on 3 monitor wafers.

## 7. Acceptance criteria (release the tool only when all are met)

- Leak-up rate below 2 mTorr/min.
- CD uniformity (3-sigma) at or below 2.4 nm on 3 monitor wafers.
- Edge-to-centre etch rate ratio between 0.97 and 1.03.

## 8. Parts

- Focus ring (silicon)
- Ring screws kit

## 9. Escalation

Escalate if a new ring does not restore uniformity: check the ESC and RF return path.

## 10. Closure note requirements

Close the OOC with root cause code `RC-ETCH-02` and record: the symptom, the check that confirmed the cause, the corrective action and the requalification result.

## 11. Related documents

- SOP-GEN-001 (General OOC Response and Lot Disposition)
- SOP-MET-001 (Metrology Verification Before Process Tool Action)
- SOP-GEN-002 (Change Control and Requalification After PM or Recipe Edit)
