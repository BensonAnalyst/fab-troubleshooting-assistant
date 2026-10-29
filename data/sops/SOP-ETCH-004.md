# SOP-ETCH-004: RF Match and Reflected Power Troubleshooting

| Field | Value |
|---|---|
| Document | SOP-ETCH-004 |
| Site | Northbridge Fab 1 (fictional) |
| Module | ETCH (Plasma Etch) |
| Platform | Kestrel K9 |
| Revision | C |
| Effective date | 2025-01-06 |
| Owner | Module process engineering |

> Synthetic document created for a portfolio project. It does not describe any real company's procedures.

## 1. Purpose

Diagnose and correct the condition: **RF match network or connector issue**. Use this procedure when the symptoms below trigger an SPC out-of-control (OOC) event.

## 2. Scope

Applies to ETCH (Plasma Etch) tools on the Kestrel K9 platform at Northbridge Fab 1.

## 3. Symptoms (when to use this SOP)

- RF reflected power spiking or trending up.
- Etch rate unstable or dropping, sometimes with plasma flicker.
- Match capacitor positions running close to their travel limit.

Typical SPC parameters affected: `reflected_power` (up), `etch_rate` (down).

## 4. Safety

- RF LOTO required. Never open the match enclosure with RF enabled.

## 5. Diagnostic checks

1. Trend reflected power and match tune/load capacitor positions over the last 100 wafers.
2. Check RF cable connectors for heat discolouration and confirm connector torque.
3. Check the RF generator fault log for arcing or foldback events.

## 6. Corrective procedure

1. Under LOTO, reseat and torque RF connectors to specification. Replace any discoloured connector.
2. Run the match auto-tune calibration routine.
3. If a capacitor is at its travel limit or noisy, replace the match capacitor (or the match unit).
4. Requalify etch rate on 3 monitor wafers.

## 7. Acceptance criteria (release the tool only when all are met)

- Reflected power at or below 10 W in steady state.
- Match capacitor positions between 20% and 80% of travel.
- Etch rate within +/-3% of baseline.

## 8. Parts

- RF connector (N-type)
- Match vacuum capacitor
- RF match unit

## 9. Escalation

Escalate to facilities if the RF generator itself logs faults.

## 10. Closure note requirements

Close the OOC with root cause code `RC-ETCH-04` and record: the symptom, the check that confirmed the cause, the corrective action and the requalification result.

## 11. Related documents

- SOP-GEN-001 (General OOC Response and Lot Disposition)
- SOP-MET-001 (Metrology Verification Before Process Tool Action)
- SOP-GEN-002 (Change Control and Requalification After PM or Recipe Edit)
