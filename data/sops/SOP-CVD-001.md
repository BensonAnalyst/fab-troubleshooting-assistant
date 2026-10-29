# SOP-CVD-001: Showerhead Clean and Replacement

| Field | Value |
|---|---|
| Document | SOP-CVD-001 |
| Site | Northbridge Fab 1 (fictional) |
| Module | CVD (Chemical Vapour Deposition) |
| Platform | Halcyon H4 |
| Revision | C |
| Effective date | 2025-01-06 |
| Owner | Module process engineering |

> Synthetic document created for a portfolio project. It does not describe any real company's procedures.

## 1. Purpose

Diagnose and correct the condition: **Showerhead deposition / clogging**. Use this procedure when the symptoms below trigger an SPC out-of-control (OOC) event.

## 2. Scope

Applies to CVD (Chemical Vapour Deposition) tools on the Halcyon H4 platform at Northbridge Fab 1.

## 3. Symptoms (when to use this SOP)

- Thickness uniformity getting worse with a centre-thin pattern.
- Deposition rate slowly dropping.

Typical SPC parameters affected: `thickness_uniformity` (up), `film_thickness` (down).

## 4. Safety

- Chamber must be cooled and purged before a showerhead swap. NF3 residues: wear PPE.

## 5. Diagnostic checks

1. Review the 49-point thickness map for a centre-thin or ring pattern.
2. Check RF hours since the last showerhead clean (interval 600 RF hours on Halcyon H4).
3. Check that the in-situ NF3 clean completed without faults on recent runs.

## 6. Corrective procedure

1. Run an extended in-situ NF3 clean (2x standard time) and a pre-coat.
2. Run 2 thickness monitor wafers. If uniformity has not recovered, perform a showerhead swap PM.
3. After a swap, run the full requalification (thickness, uniformity, particles).

## 7. Acceptance criteria (release the tool only when all are met)

- Thickness within +/-2% of target.
- Uniformity (1-sigma) at or below 1.5%.
- Particle adders at or below 20.

## 8. Parts

- Showerhead (faceplate)
- Showerhead o-ring kit

## 9. Escalation

Escalate if uniformity is still out after a new showerhead: check the heater.

## 10. Closure note requirements

Close the OOC with root cause code `RC-CVD-01` and record: the symptom, the check that confirmed the cause, the corrective action and the requalification result.

## 11. Related documents

- SOP-GEN-001 (General OOC Response and Lot Disposition)
- SOP-MET-001 (Metrology Verification Before Process Tool Action)
- SOP-GEN-002 (Change Control and Requalification After PM or Recipe Edit)
