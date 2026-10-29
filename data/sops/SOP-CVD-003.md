# SOP-CVD-003: Pedestal Heater and Thermocouple Verification

| Field | Value |
|---|---|
| Document | SOP-CVD-003 |
| Site | Northbridge Fab 1 (fictional) |
| Module | CVD (Chemical Vapour Deposition) |
| Platform | Halcyon H4 |
| Revision | C |
| Effective date | 2025-01-06 |
| Owner | Module process engineering |

> Synthetic document created for a portfolio project. It does not describe any real company's procedures.

## 1. Purpose

Diagnose and correct the condition: **Heater or thermocouple temperature drift**. Use this procedure when the symptoms below trigger an SPC out-of-control (OOC) event.

## 2. Scope

Applies to CVD (Chemical Vapour Deposition) tools on the Halcyon H4 platform at Northbridge Fab 1.

## 3. Symptoms (when to use this SOP)

- Refractive index or film stress shifting while thickness is roughly normal.
- Heater zone power output changing to hold the same setpoint.

Typical SPC parameters affected: `refractive_index` (up), `film_stress` (up), `film_thickness` (up).

## 4. Safety

- Heater replacement requires full cool-down (below 50 C) and electrical LOTO.

## 5. Diagnostic checks

1. Compare thermocouple reading against setpoint and against the heater zone power trend.
2. Run a temperature calibration check with the calibrated reference thermocouple wafer.
3. Check thermocouple connector and wiring for damage.

## 6. Corrective procedure

1. If the thermocouple reads more than 3 C off the reference, recalibrate or replace the thermocouple.
2. If heater zone power is unstable or a zone has failed, replace the heater (pedestal) assembly.
3. Requalify refractive index, stress and thickness.

## 7. Acceptance criteria (release the tool only when all are met)

- Thermocouple within +/-2 C of the reference wafer.
- Refractive index within 1.456 to 1.464.
- Film stress within -200 to -160 MPa.

## 8. Parts

- Thermocouple
- Pedestal heater assembly

## 9. Escalation

Heater assembly replacement needs vendor support for levelling.

## 10. Closure note requirements

Close the OOC with root cause code `RC-CVD-03` and record: the symptom, the check that confirmed the cause, the corrective action and the requalification result.

## 11. Related documents

- SOP-GEN-001 (General OOC Response and Lot Disposition)
- SOP-MET-001 (Metrology Verification Before Process Tool Action)
- SOP-GEN-002 (Change Control and Requalification After PM or Recipe Edit)
