# SOP-GEN-001: General OOC Response and Lot Disposition

| Field | Value |
|---|---|
| Document | SOP-GEN-001 |
| Site | Northbridge Fab 1 (fictional) |
| Module | All modules |
| Platform | All platforms |
| Revision | D |
| Effective date | 2025-01-06 |
| Owner | Module process engineering |

> Synthetic document created for a portfolio project. It does not describe any real company's procedures.

## 1. Purpose

Define the standard response to any SPC out-of-control (OOC) event, from first alarm to closure, so that lots are protected and every OOC leaves a usable record.

## 2. Response steps

1. **Hold** the affected lot and stop further processing on the tool or chamber that produced the OOC point.
2. **Verify the measurement first** using SOP-MET-001. Around 1 in 10 OOC events are metrology false alarms; do not touch the process tool until the reading is confirmed.
3. **Check for recent changes** (recipe edits, PMs, part changes in the last 24 hours) using SOP-GEN-002.
4. **Use the module troubleshooting SOP** that matches the symptom pattern (see the index below).
5. **Requalify** the tool against the acceptance criteria of that SOP.
6. **Disposition** held lots: release, rework, or scrap with the module engineer's approval.
7. **Close the OOC** with a root cause code and a complete closure note.

## 3. Response time targets

- Acknowledge the OOC within 15 minutes.
- First diagnosis (cause suspected) within 2 hours.
- Tool down longer than 8 hours must be escalated to the module manager.

## 4. Closure note standard

A closure note must contain four parts, so that future engineers can search it:

1. **Symptom**: parameter, value, SPC rule triggered.
2. **Root cause**: the confirmed cause and the check that confirmed it, plus the root cause code.
3. **Action**: what was done, including part numbers replaced.
4. **Verification**: the requalification result.

Notes such as "fixed", "ok now" or "see shift log" are not acceptable closures.

## 5. Troubleshooting SOP index

| Root cause code | SOP | Module | Title |
|---|---|---|---|
| RC-ETCH-01 | SOP-ETCH-001 | ETCH | Chamber Dry Clean, Seasoning and Wet Clean Decision |
| RC-ETCH-02 | SOP-ETCH-002 | ETCH | Focus Ring Inspection and Replacement |
| RC-ETCH-03 | SOP-ETCH-003 | ETCH | Electrostatic Chuck (ESC) Helium Leak Troubleshooting |
| RC-ETCH-04 | SOP-ETCH-004 | ETCH | RF Match and Reflected Power Troubleshooting |
| RC-ETCH-05 | SOP-ETCH-005 | ETCH | Mass Flow Controller (MFC) Verification and Replacement |
| RC-CVD-01 | SOP-CVD-001 | CVD | Showerhead Clean and Replacement |
| RC-CVD-02 | SOP-CVD-002 | CVD | CVD Particle Excursion Response |
| RC-CVD-03 | SOP-CVD-003 | CVD | Pedestal Heater and Thermocouple Verification |
| RC-CVD-04 | SOP-CVD-004 | CVD | Liquid Precursor Delivery Troubleshooting |
| RC-CMP-01 | SOP-CMP-001 | CMP | Pad Conditioning and Conditioner Disk Replacement |
| RC-CMP-02 | SOP-CMP-002 | CMP | Slurry Delivery and Filter Troubleshooting |
| RC-CMP-03 | SOP-CMP-003 | CMP | Carrier Head Rebuild |
| RC-CMP-04 | SOP-CMP-004 | CMP | Optical Endpoint Verification |
| RC-LITH-01 | SOP-LITH-001 | LITH | Overlay Excursion Response and Stage Calibration |
| RC-LITH-02 | SOP-LITH-002 | LITH | Wafer Chuck Cleaning for Focus Hot Spots |
| RC-LITH-03 | SOP-LITH-003 | LITH | Dose Calibration and Laser Energy Check |
| RC-LITH-04 | SOP-LITH-004 | LITH | Resist Coat Thickness Troubleshooting (Track) |
| RC-WET-01 | SOP-WET-001 | WET | Wet Bench Bath Change and Concentration Check |
| RC-WET-02 | SOP-WET-002 | WET | Wet Bench Filter Change and Particle Response |
| RC-WET-03 | SOP-WET-003 | WET | Dryer (IPA/N2) Troubleshooting for Watermarks |
| RC-MET-01 | SOP-MET-001 | ANY | Metrology Verification Before Process Tool Action |
| RC-GEN-01 | SOP-GEN-002 | ANY | Change Control and Requalification After PM or Recipe Edit |
