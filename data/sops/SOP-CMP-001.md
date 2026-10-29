# SOP-CMP-001: Pad Conditioning and Conditioner Disk Replacement

| Field | Value |
|---|---|
| Document | SOP-CMP-001 |
| Site | Northbridge Fab 1 (fictional) |
| Module | CMP (Chemical Mechanical Planarization) |
| Platform | Polaris P3 |
| Revision | C |
| Effective date | 2025-01-06 |
| Owner | Module process engineering |

> Synthetic document created for a portfolio project. It does not describe any real company's procedures.

## 1. Purpose

Diagnose and correct the condition: **Pad glazing or worn conditioner disk**. Use this procedure when the symptoms below trigger an SPC out-of-control (OOC) event.

## 2. Scope

Applies to CMP (Chemical Mechanical Planarization) tools on the Polaris P3 platform at Northbridge Fab 1.

## 3. Symptoms (when to use this SOP)

- Removal rate dropping gradually over pad life.
- Shiny (glazed) pad surface on inspection.

Typical SPC parameters affected: `removal_rate` (down).

## 4. Safety

- Platen LOTO before touching the pad or conditioner.

## 5. Diagnostic checks

1. Check conditioner disk life (limit 40 hours on Polaris P3) and pad life (limit 1,500 wafers).
2. Check conditioner downforce and sweep settings against the recipe.
3. Inspect the pad for glazing.

## 6. Corrective procedure

1. Replace the conditioner disk if at or near its life limit.
2. If the pad is near its life limit, replace the pad and run the pad break-in recipe.
3. Run 2 removal rate monitors.

## 7. Acceptance criteria (release the tool only when all are met)

- Removal rate within +/-5% of baseline on 2 monitors.

## 8. Parts

- Conditioner disk
- Polishing pad

## 9. Escalation

Escalate if a new disk and pad do not recover removal rate: check slurry.

## 10. Closure note requirements

Close the OOC with root cause code `RC-CMP-01` and record: the symptom, the check that confirmed the cause, the corrective action and the requalification result.

## 11. Related documents

- SOP-GEN-001 (General OOC Response and Lot Disposition)
- SOP-MET-001 (Metrology Verification Before Process Tool Action)
- SOP-GEN-002 (Change Control and Requalification After PM or Recipe Edit)
