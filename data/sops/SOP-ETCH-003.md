# SOP-ETCH-003: Electrostatic Chuck (ESC) Helium Leak Troubleshooting

| Field | Value |
|---|---|
| Document | SOP-ETCH-003 |
| Site | Northbridge Fab 1 (fictional) |
| Module | ETCH (Plasma Etch) |
| Platform | Kestrel K9 |
| Revision | C |
| Effective date | 2025-01-06 |
| Owner | Module process engineering |

> Synthetic document created for a portfolio project. It does not describe any real company's procedures.

## 1. Purpose

Diagnose and correct the condition: **ESC helium backside leak**. Use this procedure when the symptoms below trigger an SPC out-of-control (OOC) event.

## 2. Scope

Applies to ETCH (Plasma Etch) tools on the Kestrel K9 platform at Northbridge Fab 1.

## 3. Symptoms (when to use this SOP)

- He backside flow higher than normal or hitting the flow alarm while pressure is held.
- Local CD non-uniformity (hot spots) because wafer temperature control is poor.
- Occasional wafer de-chuck errors.

Typical SPC parameters affected: `he_backside_flow` (up), `cd_uniformity` (up).

## 4. Safety

- Chamber vent and LOTO required for ESC access. ESC has high-voltage connections: confirm HV discharge.

## 5. Diagnostic checks

1. Run the He leak-up test with a bare wafer chucked. A leak rate above 1.5 sccm points to an ESC or seal issue.
2. Inspect the ESC surface for particles, scratches or arcing marks.
3. Check recent wafers for chipped edges or backside particles that stop the wafer sealing.
4. Check the He seal o-ring for compression set or damage.

## 6. Corrective procedure

1. Clean the ESC surface with an approved lint-free wipe and IPA. Do not use abrasives.
2. Replace the He seal o-ring and re-run the leak-up test.
3. If leak rate is still above 1.5 sccm, the ESC surface is damaged: escalate for ESC replacement with the vendor.

## 7. Acceptance criteria (release the tool only when all are met)

- He leak rate at or below 1.0 sccm on the leak-up test.
- He backside flow within 3.6 to 4.8 sccm during process.
- No de-chuck errors over 25 wafers.

## 8. Parts

- He seal o-ring
- ESC assembly (vendor replacement only)

## 9. Escalation

ESC replacement is a vendor job: raise a vendor service request and keep the chamber down.

## 10. Closure note requirements

Close the OOC with root cause code `RC-ETCH-03` and record: the symptom, the check that confirmed the cause, the corrective action and the requalification result.

## 11. Related documents

- SOP-GEN-001 (General OOC Response and Lot Disposition)
- SOP-MET-001 (Metrology Verification Before Process Tool Action)
- SOP-GEN-002 (Change Control and Requalification After PM or Recipe Edit)
