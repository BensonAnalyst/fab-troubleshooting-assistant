# SOP-CMP-003: Carrier Head Rebuild

| Field | Value |
|---|---|
| Document | SOP-CMP-003 |
| Site | Northbridge Fab 1 (fictional) |
| Module | CMP (Chemical Mechanical Planarization) |
| Platform | Polaris P3 |
| Revision | C |
| Effective date | 2025-01-06 |
| Owner | Module process engineering |

> Synthetic document created for a portfolio project. It does not describe any real company's procedures.

## 1. Purpose

Diagnose and correct the condition: **Carrier head membrane or retaining ring wear**. Use this procedure when the symptoms below trigger an SPC out-of-control (OOC) event.

## 2. Scope

Applies to CMP (Chemical Mechanical Planarization) tools on the Polaris P3 platform at Northbridge Fab 1.

## 3. Symptoms (when to use this SOP)

- Within-wafer non-uniformity rising with an edge-fast or edge-slow profile.
- Membrane leak alarm, or retaining ring near wear limit.

Typical SPC parameters affected: `wiwnu` (up), `removal_rate` (up).

## 4. Safety

- Polisher LOTO for head removal; heads are heavy, use the lift fixture.

## 5. Diagnostic checks

1. Check carrier head life counters (membrane 3,000 wafers, retaining ring 6,000 wafers).
2. Run the membrane leak test.
3. Measure retaining ring thickness.

## 6. Corrective procedure

1. Rebuild the carrier head: replace the membrane and retaining ring.
2. Run head calibration (zone pressure) after rebuild.
3. Run 2 removal rate and uniformity monitors.

## 7. Acceptance criteria (release the tool only when all are met)

- WIWNU at or below 4.5%.
- Removal rate within +/-5% of baseline.

## 8. Parts

- Carrier membrane
- Retaining ring

## 9. Escalation

Escalate if WIWNU stays high after rebuild: check zone pressure controllers.

## 10. Closure note requirements

Close the OOC with root cause code `RC-CMP-03` and record: the symptom, the check that confirmed the cause, the corrective action and the requalification result.

## 11. Related documents

- SOP-GEN-001 (General OOC Response and Lot Disposition)
- SOP-MET-001 (Metrology Verification Before Process Tool Action)
- SOP-GEN-002 (Change Control and Requalification After PM or Recipe Edit)
