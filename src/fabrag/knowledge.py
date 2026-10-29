"""Fictional fab knowledge base used to generate the synthetic dataset.

Everything here is invented for this project: the fab ("Northbridge Fab 1"), the tool
platforms, tool IDs, parameter baselines, life limits and procedures. It follows how
front-end wafer fabs generally run SPC and troubleshooting, but it does not reproduce any
real company's documents, recipes, limits or data.
"""

FAB_NAME = "Northbridge Fab 1"

# --------------------------------------------------------------------------------------
# Modules, tool platforms and tools
# --------------------------------------------------------------------------------------
MODULES = {
    "ETCH": {"name": "Plasma Etch", "platform": "Kestrel K9", "tools": 6, "chambers": ["A", "B", "C"]},
    "CVD": {"name": "Chemical Vapour Deposition", "platform": "Halcyon H4", "tools": 4, "chambers": ["A", "B"]},
    "CMP": {"name": "Chemical Mechanical Planarization", "platform": "Polaris P3", "tools": 4, "chambers": ["P1", "P2"]},
    "LITH": {"name": "Lithography", "platform": "Meridian M7", "tools": 3, "chambers": [""]},
    "WET": {"name": "Wet Clean", "platform": "Cascade C2", "tools": 3, "chambers": ["B1", "B2"]},
}

# SPC parameters per module: (parameter_id, display name, unit, baseline, sigma)
PARAMETERS = {
    "ETCH": [
        ("etch_rate", "Etch rate", "A/min", 2450.0, 35.0),
        ("cd_uniformity", "CD uniformity (3-sigma)", "nm", 2.10, 0.15),
        ("endpoint_time", "Endpoint time", "s", 58.0, 1.2),
        ("reflected_power", "RF reflected power", "W", 6.0, 1.5),
        ("he_backside_flow", "He backside flow", "sccm", 4.2, 0.3),
        ("particle_adders", "Particle adders (>0.06um)", "count", 8.0, 3.0),
    ],
    "CVD": [
        ("film_thickness", "Film thickness", "A", 5000.0, 30.0),
        ("thickness_uniformity", "Thickness uniformity (1-sigma)", "%", 1.20, 0.10),
        ("particle_adders", "Particle adders (>0.08um)", "count", 10.0, 4.0),
        ("refractive_index", "Refractive index", "", 1.460, 0.002),
        ("film_stress", "Film stress", "MPa", -180.0, 8.0),
    ],
    "CMP": [
        ("removal_rate", "Removal rate", "A/min", 3200.0, 60.0),
        ("wiwnu", "Within-wafer non-uniformity", "%", 3.5, 0.3),
        ("scratch_count", "Scratch defects", "count", 2.0, 1.0),
        ("dishing", "Dishing (100um pad)", "A", 350.0, 25.0),
    ],
    "LITH": [
        ("overlay_x", "Overlay X (mean+3s)", "nm", 4.0, 0.4),
        ("overlay_y", "Overlay Y (mean+3s)", "nm", 4.0, 0.4),
        ("cd_mean", "Resist CD mean", "nm", 45.0, 0.6),
        ("focus_error", "Focus error (max)", "nm", 20.0, 4.0),
        ("resist_thickness", "Resist thickness", "A", 1200.0, 8.0),
    ],
    "WET": [
        ("oxide_etch_rate", "Oxide etch rate", "A/min", 60.0, 1.5),
        ("particle_adders", "Particle adders (>0.08um)", "count", 6.0, 2.5),
        ("watermark_defects", "Watermark defects", "count", 1.0, 0.8),
    ],
}

# Western Electric style SPC rules used in OOC triggers
SPC_RULES = [
    "Rule 1: 1 point beyond 3-sigma",
    "Rule 2: 2 of 3 points beyond 2-sigma",
    "Rule 4: 8 consecutive points on one side of centre",
    "Rule 5: 6 points trending",
]

ENGINEERS = ["KL", "RT", "SM", "AN", "JW", "PC", "HY", "DF", "MS", "TB"]
TECHNICIANS = ["T-Ahmad", "T-Lim", "T-Raj", "T-Wong", "T-Siti", "T-Kumar", "T-Chen", "T-Nora"]

# --------------------------------------------------------------------------------------
# Root causes. Each maps to one SOP. `params` lists (parameter_id, direction) that the
# root cause typically pushes out of control. `findings` and `actions` are phrase variants
# used to write varied engineer closure notes.
# --------------------------------------------------------------------------------------
ROOT_CAUSES = [
    # ---------------------------------- ETCH ----------------------------------
    {
        "rc_id": "RC-ETCH-01", "module": "ETCH", "sop_id": "SOP-ETCH-001",
        "name": "Chamber wall polymer build-up (clean interval exceeded)",
        "sop_title": "Chamber Dry Clean, Seasoning and Wet Clean Decision",
        "params": [("etch_rate", -1), ("endpoint_time", 1), ("particle_adders", 1)],
        "weight": 1.4, "downtime": (2, 10),
        "symptoms": [
            "Etch rate drifting down slowly over several days, often flagged by a trend rule rather than a single point.",
            "Endpoint time creeping up on the same chamber.",
            "Particle adders rising on monitor wafers, sometimes with flakes visible on the chamber liner.",
        ],
        "checks": [
            "Check RF hours since the last chamber wet clean in the tool PM counter. The Kestrel K9 wet clean interval is 1,200 RF hours.",
            "Trend etch rate and endpoint time for the last 30 monitor wafers on this chamber only. A gradual slope points to build-up; a step change points elsewhere.",
            "Inspect the chamber liner and window through the viewport for visible deposit or flaking.",
        ],
        "fix": [
            "Run the O2 dry clean recipe DC-O2-30 followed by 5 seasoning wafers.",
            "Run 3 monitor wafers. If etch rate is back within +/-3% of baseline, release the chamber.",
            "If RF hours since wet clean are above 1,100 or the dry clean does not recover etch rate, schedule a chamber wet clean PM (liner and window replacement).",
        ],
        "accept": [
            "Etch rate within +/-3% of the chamber baseline on 3 consecutive monitor wafers.",
            "Particle adders at or below 15 on a bare-silicon particle monitor.",
            "Endpoint time within +/-2 s of baseline.",
        ],
        "parts": ["Chamber liner kit (wet clean only)", "Viewport window (wet clean only)"],
        "safety": [
            "Wet clean requires chamber vent and lock-out/tag-out (LOTO) of RF and gas.",
            "Wear chemical gloves and face shield when handling liner deposits; residues can be fluorinated polymer.",
        ],
        "escalate": "Escalate to the etch module owner if etch rate does not recover after a wet clean.",
        "findings": [
            "RF hrs since last wet clean at {rfh}, over interval, liner showing heavy polymer",
            "etch rate trending down past {n} lots, endpoint time up, consistent with chamber build-up",
            "chamber dirty - polymer on liner and window, clean interval exceeded ({rfh} RFh)",
        ],
        "actions": [
            "dry clean did not recover ER, did full wet clean PM, replaced liner kit and window, requal ok",
            "ran DC-O2-30 dry clean + 5 seasoning wfrs, ER recovered on 3 monitors",
            "performed O2 dry clean and seasoning, scheduled wet clean PM for next week",
        ],
    },
    {
        "rc_id": "RC-ETCH-02", "module": "ETCH", "sop_id": "SOP-ETCH-002",
        "name": "Focus (edge) ring erosion",
        "sop_title": "Focus Ring Inspection and Replacement",
        "params": [("cd_uniformity", 1), ("etch_rate", 1)],
        "weight": 1.2, "downtime": (3, 8),
        "symptoms": [
            "CD uniformity getting worse, with the wafer edge etching faster than the centre.",
            "49-point map shows an edge-fast ring pattern; centre values normal.",
            "Usually gradual and correlated with focus ring RF hours approaching the life limit.",
        ],
        "checks": [
            "Check focus ring RF hours. The life limit is 800 RF hours on Kestrel K9.",
            "Review the 49-point etch rate or CD map: an edge-fast pattern with a normal centre points to ring erosion.",
            "Measure ring thickness at 4 points after venting, if the map is inconclusive.",
        ],
        "fix": [
            "Vent the chamber under LOTO and replace the focus ring.",
            "Pump down, run a leak-up rate check, then run 5 seasoning wafers.",
            "Requalify CD uniformity and etch rate on 3 monitor wafers.",
        ],
        "accept": [
            "Leak-up rate below 2 mTorr/min.",
            "CD uniformity (3-sigma) at or below 2.4 nm on 3 monitor wafers.",
            "Edge-to-centre etch rate ratio between 0.97 and 1.03.",
        ],
        "parts": ["Focus ring (silicon)", "Ring screws kit"],
        "safety": ["Chamber vent and LOTO required. Allow the chamber to cool below 40 C before opening."],
        "escalate": "Escalate if a new ring does not restore uniformity: check the ESC and RF return path.",
        "findings": [
            "focus ring at {rfh} RFh (limit 800), edge fast on 49pt map",
            "CDU degrading, edge ER high vs centre, ring eroded on inspection",
            "edge-fast pattern on map, focus ring near EOL",
        ],
        "actions": [
            "replaced focus ring, leak check ok, seasoned 5 wfrs, CDU back in spec",
            "repl edge ring + screws, requal'd CDU and ER on 3 monitors",
            "changed focus ring, CDU recovered to 2.2 nm",
        ],
    },
    {
        "rc_id": "RC-ETCH-03", "module": "ETCH", "sop_id": "SOP-ETCH-003",
        "name": "ESC helium backside leak",
        "sop_title": "Electrostatic Chuck (ESC) Helium Leak Troubleshooting",
        "params": [("he_backside_flow", 1), ("cd_uniformity", 1)],
        "weight": 1.0, "downtime": (2, 24),
        "symptoms": [
            "He backside flow higher than normal or hitting the flow alarm while pressure is held.",
            "Local CD non-uniformity (hot spots) because wafer temperature control is poor.",
            "Occasional wafer de-chuck errors.",
        ],
        "checks": [
            "Run the He leak-up test with a bare wafer chucked. A leak rate above 1.5 sccm points to an ESC or seal issue.",
            "Inspect the ESC surface for particles, scratches or arcing marks.",
            "Check recent wafers for chipped edges or backside particles that stop the wafer sealing.",
            "Check the He seal o-ring for compression set or damage.",
        ],
        "fix": [
            "Clean the ESC surface with an approved lint-free wipe and IPA. Do not use abrasives.",
            "Replace the He seal o-ring and re-run the leak-up test.",
            "If leak rate is still above 1.5 sccm, the ESC surface is damaged: escalate for ESC replacement with the vendor.",
        ],
        "accept": [
            "He leak rate at or below 1.0 sccm on the leak-up test.",
            "He backside flow within 3.6 to 4.8 sccm during process.",
            "No de-chuck errors over 25 wafers.",
        ],
        "parts": ["He seal o-ring", "ESC assembly (vendor replacement only)"],
        "safety": ["Chamber vent and LOTO required for ESC access. ESC has high-voltage connections: confirm HV discharge."],
        "escalate": "ESC replacement is a vendor job: raise a vendor service request and keep the chamber down.",
        "findings": [
            "He flow high, leak-up test failed at 2.3 sccm",
            "He leak found, o-ring compressed, ESC surface ok",
            "He leak-up test out, ESC surface scratched with arc marks",
        ],
        "actions": [
            "cleaned ESC with IPA wipe, removed particles, repl He o-ring, leak-up 0.7 sccm, released",
            "repl He o-ring, leak-up 0.8 sccm, released",
            "o-ring replaced, leak still 1.9 sccm, ESC swap by vendor, requal ok",
        ],
    },
    {
        "rc_id": "RC-ETCH-04", "module": "ETCH", "sop_id": "SOP-ETCH-004",
        "name": "RF match network or connector issue",
        "sop_title": "RF Match and Reflected Power Troubleshooting",
        "params": [("reflected_power", 1), ("etch_rate", -1)],
        "weight": 1.0, "downtime": (1, 12),
        "symptoms": [
            "RF reflected power spiking or trending up.",
            "Etch rate unstable or dropping, sometimes with plasma flicker.",
            "Match capacitor positions running close to their travel limit.",
        ],
        "checks": [
            "Trend reflected power and match tune/load capacitor positions over the last 100 wafers.",
            "Check RF cable connectors for heat discolouration and confirm connector torque.",
            "Check the RF generator fault log for arcing or foldback events.",
        ],
        "fix": [
            "Under LOTO, reseat and torque RF connectors to specification. Replace any discoloured connector.",
            "Run the match auto-tune calibration routine.",
            "If a capacitor is at its travel limit or noisy, replace the match capacitor (or the match unit).",
            "Requalify etch rate on 3 monitor wafers.",
        ],
        "accept": [
            "Reflected power at or below 10 W in steady state.",
            "Match capacitor positions between 20% and 80% of travel.",
            "Etch rate within +/-3% of baseline.",
        ],
        "parts": ["RF connector (N-type)", "Match vacuum capacitor", "RF match unit"],
        "safety": ["RF LOTO required. Never open the match enclosure with RF enabled."],
        "escalate": "Escalate to facilities if the RF generator itself logs faults.",
        "findings": [
            "reflected pwr spiking, load cap at 92% travel",
            "RF connector at match output discoloured / loose",
            "plasma flicker, refl power high, match tuning hunting",
        ],
        "actions": [
            "replaced load vacuum cap, requal ER ok",
            "reseated and torqued RF connectors, auto-tune cal, refl power normal",
            "swapped RF match unit, ran cal, ER back in spec",
        ],
    },
    {
        "rc_id": "RC-ETCH-05", "module": "ETCH", "sop_id": "SOP-ETCH-005",
        "name": "Process gas MFC drift",
        "sop_title": "Mass Flow Controller (MFC) Verification and Replacement",
        "params": [("etch_rate", 1), ("endpoint_time", -1)],
        "weight": 0.8, "downtime": (2, 8),
        "symptoms": [
            "Step change in etch rate or endpoint time without a matching change in chamber hours.",
            "Selectivity or profile change on product wafers.",
        ],
        "checks": [
            "Run a rate-of-rise (ROR) flow verification on each process gas MFC.",
            "Compare MFC readback against setpoint in the gas panel log for the last 7 days.",
            "Check for recent gas bottle or gas line work.",
        ],
        "fix": [
            "If an MFC deviates more than 2% on ROR, recalibrate it; if it deviates more than 5%, replace it.",
            "Purge the gas line after any MFC replacement.",
            "Requalify etch rate on 3 monitor wafers.",
        ],
        "accept": [
            "All MFCs within +/-2% of setpoint on rate-of-rise verification.",
            "Etch rate within +/-3% of baseline.",
        ],
        "parts": ["Mass flow controller (C4F8 / CF4 / O2 / Ar)"],
        "safety": ["Gas line work requires toxic gas LOTO and a gas detector check before and after."],
        "escalate": "Escalate to gas facilities if the drift is on the supply side.",
        "findings": [
            "C4F8 MFC off by {pct}% on ROR check",
            "step change in ER, MFC readback vs setpoint mismatch on CF4 line",
            "O2 MFC drifted, ROR failed",
        ],
        "actions": [
            "recalibrated MFC, ROR within 1%, ER back",
            "replaced MFC, purged line, requal'd 3 monitors ok",
            "MFC swap + purge, ER normal",
        ],
    },
    # ---------------------------------- CVD ----------------------------------
    {
        "rc_id": "RC-CVD-01", "module": "CVD", "sop_id": "SOP-CVD-001",
        "name": "Showerhead deposition / clogging",
        "sop_title": "Showerhead Clean and Replacement",
        "params": [("thickness_uniformity", 1), ("film_thickness", -1)],
        "weight": 1.2, "downtime": (2, 16),
        "symptoms": [
            "Thickness uniformity getting worse with a centre-thin pattern.",
            "Deposition rate slowly dropping.",
        ],
        "checks": [
            "Review the 49-point thickness map for a centre-thin or ring pattern.",
            "Check RF hours since the last showerhead clean (interval 600 RF hours on Halcyon H4).",
            "Check that the in-situ NF3 clean completed without faults on recent runs.",
        ],
        "fix": [
            "Run an extended in-situ NF3 clean (2x standard time) and a pre-coat.",
            "Run 2 thickness monitor wafers. If uniformity has not recovered, perform a showerhead swap PM.",
            "After a swap, run the full requalification (thickness, uniformity, particles).",
        ],
        "accept": [
            "Thickness within +/-2% of target.",
            "Uniformity (1-sigma) at or below 1.5%.",
            "Particle adders at or below 20.",
        ],
        "parts": ["Showerhead (faceplate)", "Showerhead o-ring kit"],
        "safety": ["Chamber must be cooled and purged before a showerhead swap. NF3 residues: wear PPE."],
        "escalate": "Escalate if uniformity is still out after a new showerhead: check the heater.",
        "findings": [
            "centre-thin pattern on 49pt map, showerhead at {rfh} RFh",
            "uniformity worsening and dep rate dropping, showerhead holes partially clogged",
            "NF3 clean incomplete last 3 runs, showerhead deposit",
        ],
        "actions": [
            "extended NF3 clean + precoat, uniformity recovered",
            "showerhead swap PM, full requal passed",
            "ran 2x clean, still marginal, swapped faceplate, ok",
        ],
    },
    {
        "rc_id": "RC-CVD-02", "module": "CVD", "sop_id": "SOP-CVD-002",
        "name": "Particle flaking from chamber walls or lid",
        "sop_title": "CVD Particle Excursion Response",
        "params": [("particle_adders", 1)],
        "weight": 1.3, "downtime": (2, 12),
        "symptoms": [
            "Sudden jump in particle adders on monitor wafers.",
            "Random or edge-concentrated particle map; large flakes under SEM review.",
        ],
        "checks": [
            "Classify the particle map pattern: random/large flakes (wall flaking), edge-heavy (lift pins or edge ring), cluster (handling).",
            "Check the clean interval and whether the last clean or pre-coat was skipped.",
            "Check the exhaust and foreline pressure for back-streaming.",
        ],
        "fix": [
            "Run an extended clean plus a thicker pre-coat (seasoning) to bury loose deposits.",
            "Run 2 particle monitors. If adders are still high, perform a chamber wet clean.",
            "For edge-heavy patterns, inspect and clean the lift pins.",
        ],
        "accept": [
            "Particle adders at or below 20 on 2 consecutive monitors.",
            "No flake-type defects on SEM review.",
        ],
        "parts": ["Chamber lid liner", "Lift pin set"],
        "safety": ["Vent and LOTO required for wet clean. Handle chamber parts with gloves; deposits may be reactive."],
        "escalate": "Escalate to the defect engineer if the particle source cannot be identified after a wet clean.",
        "findings": [
            "adders jumped, random large flakes on SEM",
            "pre-coat skipped after last clean, wall flaking",
            "edge-heavy particles, lift pins dirty",
        ],
        "actions": [
            "wet clean chamber, replaced lid liner, adders <10",
            "extended clean + thick precoat, 2 monitors pass",
            "cleaned lift pins, reran monitors ok",
        ],
    },
    {
        "rc_id": "RC-CVD-03", "module": "CVD", "sop_id": "SOP-CVD-003",
        "name": "Heater or thermocouple temperature drift",
        "sop_title": "Pedestal Heater and Thermocouple Verification",
        "params": [("refractive_index", 1), ("film_stress", 1), ("film_thickness", 1)],
        "weight": 0.9, "downtime": (3, 20),
        "symptoms": [
            "Refractive index or film stress shifting while thickness is roughly normal.",
            "Heater zone power output changing to hold the same setpoint.",
        ],
        "checks": [
            "Compare thermocouple reading against setpoint and against the heater zone power trend.",
            "Run a temperature calibration check with the calibrated reference thermocouple wafer.",
            "Check thermocouple connector and wiring for damage.",
        ],
        "fix": [
            "If the thermocouple reads more than 3 C off the reference, recalibrate or replace the thermocouple.",
            "If heater zone power is unstable or a zone has failed, replace the heater (pedestal) assembly.",
            "Requalify refractive index, stress and thickness.",
        ],
        "accept": [
            "Thermocouple within +/-2 C of the reference wafer.",
            "Refractive index within 1.456 to 1.464.",
            "Film stress within -200 to -160 MPa.",
        ],
        "parts": ["Thermocouple", "Pedestal heater assembly"],
        "safety": ["Heater replacement requires full cool-down (below 50 C) and electrical LOTO."],
        "escalate": "Heater assembly replacement needs vendor support for levelling.",
        "findings": [
            "RI shifted, TC reading 5C off vs reference wafer",
            "heater zone 2 power unstable, stress out",
            "thermocouple connector damaged, temp reading erratic",
        ],
        "actions": [
            "recalibrated TC offset, monitors ok",
            "heater assembly swap with vendor, requal passed",
            "replaced TC and connector, recal, RI and stress back in spec",
        ],
    },
    {
        "rc_id": "RC-CVD-04", "module": "CVD", "sop_id": "SOP-CVD-004",
        "name": "Precursor delivery problem (ampoule low or line heater)",
        "sop_title": "Liquid Precursor Delivery Troubleshooting",
        "params": [("film_thickness", -1), ("thickness_uniformity", 1)],
        "weight": 0.8, "downtime": (1, 6),
        "symptoms": [
            "Sudden drop in deposition rate (thin film) on consecutive runs.",
            "Precursor flow readback noisy or below setpoint.",
        ],
        "checks": [
            "Check the precursor ampoule level and the last ampoule change date.",
            "Check vaporizer and line heater temperatures against setpoint.",
            "Check the precursor flow readback for noise or drop-outs.",
        ],
        "fix": [
            "Replace the ampoule if the level is below 15%.",
            "Repair or replace any line heater below setpoint; cold spots cause condensation.",
            "Purge the delivery line and run 2 thickness monitors.",
        ],
        "accept": [
            "Thickness within +/-2% of target on 2 monitors.",
            "Precursor flow stable within +/-3% of setpoint.",
        ],
        "parts": ["Precursor ampoule", "Line heater jacket"],
        "safety": ["Ampoule change follows the chemical handling procedure: PPE and two-person verification."],
        "escalate": "Escalate to chemical facilities for supply issues.",
        "findings": [
            "ampoule level at {pct}%, dep rate dropped",
            "line heater zone 3 reading low, condensation suspected",
            "precursor flow noisy, vaporizer temp low",
        ],
        "actions": [
            "changed ampoule, purged line, thickness ok",
            "replaced line heater jacket, flow stable, monitors pass",
            "vaporizer heater fixed, thickness recovered",
        ],
    },
    # ---------------------------------- CMP ----------------------------------
    {
        "rc_id": "RC-CMP-01", "module": "CMP", "sop_id": "SOP-CMP-001",
        "name": "Pad glazing or worn conditioner disk",
        "sop_title": "Pad Conditioning and Conditioner Disk Replacement",
        "params": [("removal_rate", -1)],
        "weight": 1.4, "downtime": (1, 4),
        "symptoms": [
            "Removal rate dropping gradually over pad life.",
            "Shiny (glazed) pad surface on inspection.",
        ],
        "checks": [
            "Check conditioner disk life (limit 40 hours on Polaris P3) and pad life (limit 1,500 wafers).",
            "Check conditioner downforce and sweep settings against the recipe.",
            "Inspect the pad for glazing.",
        ],
        "fix": [
            "Replace the conditioner disk if at or near its life limit.",
            "If the pad is near its life limit, replace the pad and run the pad break-in recipe.",
            "Run 2 removal rate monitors.",
        ],
        "accept": ["Removal rate within +/-5% of baseline on 2 monitors."],
        "parts": ["Conditioner disk", "Polishing pad"],
        "safety": ["Platen LOTO before touching the pad or conditioner."],
        "escalate": "Escalate if a new disk and pad do not recover removal rate: check slurry.",
        "findings": [
            "RR down, conditioner disk at 38 hrs",
            "pad glazed, disk worn",
            "RR trending down, pad at end of life",
        ],
        "actions": [
            "replaced conditioner disk, RR recovered",
            "disk change + extra break-in conditioning, RR back within 5%",
            "new pad + break-in, new disk, 2 monitors ok",
        ],
    },
    {
        "rc_id": "RC-CMP-02", "module": "CMP", "sop_id": "SOP-CMP-002",
        "name": "Slurry delivery problem or agglomeration",
        "sop_title": "Slurry Delivery and Filter Troubleshooting",
        "params": [("scratch_count", 1), ("removal_rate", -1)],
        "weight": 1.2, "downtime": (1, 6),
        "symptoms": [
            "Scratch defects jumping, often arc-shaped (micro-scratches).",
            "Removal rate unstable.",
        ],
        "checks": [
            "Check slurry flow rate at the point of use against the recipe.",
            "Check POU filter differential pressure and last filter change date.",
            "Check slurry lot, age and mixing tank recirculation.",
        ],
        "fix": [
            "Replace the POU filter and flush the slurry line.",
            "Verify slurry flow with the flow-check routine.",
            "If a new slurry lot was introduced, quarantine the lot and return to the previous lot.",
        ],
        "accept": [
            "Scratch defects at or below 5 on 2 defect monitors.",
            "Slurry flow within +/-5% of setpoint.",
        ],
        "parts": ["POU slurry filter"],
        "safety": ["Slurry is a chemical: gloves and goggles for filter change."],
        "escalate": "Escalate to the slurry supplier through the materials engineer for suspected bad lots.",
        "findings": [
            "scratches up on monitor, POU filter dP high",
            "slurry flow low, filter clogged",
            "arc scratches after new slurry lot",
        ],
        "actions": [
            "changed POU filter, flushed line, defects ok",
            "verified flow after filter change, scratches <3",
            "quarantined slurry lot, back to previous lot, ok",
        ],
    },
    {
        "rc_id": "RC-CMP-03", "module": "CMP", "sop_id": "SOP-CMP-003",
        "name": "Carrier head membrane or retaining ring wear",
        "sop_title": "Carrier Head Rebuild",
        "params": [("wiwnu", 1), ("removal_rate", 1)],
        "weight": 1.0, "downtime": (3, 8),
        "symptoms": [
            "Within-wafer non-uniformity rising with an edge-fast or edge-slow profile.",
            "Membrane leak alarm, or retaining ring near wear limit.",
        ],
        "checks": [
            "Check carrier head life counters (membrane 3,000 wafers, retaining ring 6,000 wafers).",
            "Run the membrane leak test.",
            "Measure retaining ring thickness.",
        ],
        "fix": [
            "Rebuild the carrier head: replace the membrane and retaining ring.",
            "Run head calibration (zone pressure) after rebuild.",
            "Run 2 removal rate and uniformity monitors.",
        ],
        "accept": ["WIWNU at or below 4.5%.", "Removal rate within +/-5% of baseline."],
        "parts": ["Carrier membrane", "Retaining ring"],
        "safety": ["Polisher LOTO for head removal; heads are heavy, use the lift fixture."],
        "escalate": "Escalate if WIWNU stays high after rebuild: check zone pressure controllers.",
        "findings": [
            "WIWNU high, edge fast, retaining ring worn",
            "membrane leak test failed",
            "head at 3,100 wafers, membrane due",
        ],
        "actions": [
            "head rebuild (membrane + RR), cal, monitors ok",
            "replaced membrane, leak test pass, WIWNU back",
            "rebuilt carrier head, uniformity recovered",
        ],
    },
    {
        "rc_id": "RC-CMP-04", "module": "CMP", "sop_id": "SOP-CMP-004",
        "name": "Optical endpoint sensor drift or clouded pad window",
        "sop_title": "Optical Endpoint Verification",
        "params": [("dishing", 1)],
        "weight": 0.8, "downtime": (1, 4),
        "symptoms": [
            "Dishing increasing because wafers are over-polished.",
            "Endpoint trace looks noisy or flat compared with the reference trace.",
        ],
        "checks": [
            "Compare recent endpoint traces against the golden reference trace.",
            "Inspect the pad window for clouding or slurry residue.",
            "Check endpoint light source intensity.",
        ],
        "fix": [
            "Clean the pad window; replace the pad if the window is permanently clouded.",
            "Recalibrate the endpoint system with the calibration wafer.",
            "Run 2 dishing monitors.",
        ],
        "accept": ["Dishing at or below 420 A.", "Endpoint signal-to-noise within reference limits."],
        "parts": ["Endpoint light source", "Polishing pad (window)"],
        "safety": ["Platen LOTO before window inspection."],
        "escalate": "Escalate to the CMP process owner if traces still deviate after calibration.",
        "findings": [
            "EP trace flat, window clouded",
            "endpoint light source intensity low",
            "over-polish, EP not triggering",
        ],
        "actions": [
            "cleaned window, recal endpoint, dishing ok",
            "replaced EP light source, cal, monitors ok",
            "replaced pad (window clouded), EP cal passed",
        ],
    },
    # ---------------------------------- LITH ----------------------------------
    {
        "rc_id": "RC-LITH-01", "module": "LITH", "sop_id": "SOP-LITH-001",
        "name": "Overlay drift from stage or alignment calibration",
        "sop_title": "Overlay Excursion Response and Stage Calibration",
        "params": [("overlay_x", 1), ("overlay_y", 1)],
        "weight": 1.3, "downtime": (2, 8),
        "symptoms": [
            "Overlay (mean+3s) creeping up on the daily monitor.",
            "Systematic overlay signature (translation, rotation or scaling) rather than random scatter.",
        ],
        "checks": [
            "Check the daily overlay monitor trend and decompose into translation, rotation and magnification terms.",
            "Check alignment mark quality on the affected layer.",
            "Check when the stage and alignment calibrations last ran.",
        ],
        "fix": [
            "Run the stage grid and alignment calibration routines.",
            "Update the overlay correction (APC) parameters after calibration.",
            "Expose and measure 1 overlay monitor wafer.",
        ],
        "accept": ["Overlay (mean+3s) at or below 5.0 nm in X and Y."],
        "parts": [],
        "safety": ["No hardware access needed; follow scanner software access controls."],
        "escalate": "Escalate to the scanner vendor if the stage calibration fails.",
        "findings": [
            "overlay X high, rotation term dominant",
            "stage cal overdue, translation drift",
            "alignment mark contrast low on layer M1",
        ],
        "actions": [
            "ran stage grid + alignment cal, updated APC, OVL ok",
            "calibrations done, overlay monitor passed",
            "updated overlay corrections after cal, back in spec",
        ],
    },
    {
        "rc_id": "RC-LITH-02", "module": "LITH", "sop_id": "SOP-LITH-002",
        "name": "Wafer chuck contamination (focus hot spot)",
        "sop_title": "Wafer Chuck Cleaning for Focus Hot Spots",
        "params": [("focus_error", 1)],
        "weight": 1.0, "downtime": (1, 4),
        "symptoms": [
            "Focus error spikes at the same location on every wafer (repeating hot spot).",
            "Local CD defects at that location.",
        ],
        "checks": [
            "Overlay several wafers' focus maps: a hot spot at a fixed chuck position indicates chuck contamination.",
            "Check if the hot spot moves with the wafer (wafer backside particle) or stays fixed (chuck).",
        ],
        "fix": [
            "Clean the wafer chuck with the approved chuck cleaning stone and wipe procedure.",
            "Run a focus monitor wafer to confirm the hot spot is gone.",
            "If the hot spot moved with the wafer, trace the upstream tool for backside contamination instead.",
        ],
        "accept": ["Focus error (max) at or below 30 nm with no repeating hot spot."],
        "parts": ["Chuck cleaning stone"],
        "safety": ["Chuck cleaning only by certified technicians; scanner in maintenance mode."],
        "escalate": "Escalate if the hot spot persists after 2 chuck cleans.",
        "findings": [
            "focus hot spot at fixed chuck position",
            "repeating focus error same xy on all wfrs",
            "chuck particle found",
        ],
        "actions": [
            "chuck clean with stone, focus monitor ok",
            "cleaned chuck x2, hot spot gone",
            "chuck clean done, monitor passed",
        ],
    },
    {
        "rc_id": "RC-LITH-03", "module": "LITH", "sop_id": "SOP-LITH-003",
        "name": "Exposure dose drift",
        "sop_title": "Dose Calibration and Laser Energy Check",
        "params": [("cd_mean", 1)],
        "weight": 0.9, "downtime": (1, 6),
        "symptoms": ["Resist CD mean shifting across all fields while focus is normal."],
        "checks": [
            "Check the dose monitor and the laser energy log for drift.",
            "Confirm the resist lot did not change.",
        ],
        "fix": [
            "Run dose calibration.",
            "If laser energy is unstable, raise a laser service request.",
            "Expose a CD monitor wafer.",
        ],
        "accept": ["Resist CD mean within 44.0 to 46.0 nm."],
        "parts": [],
        "safety": ["Laser service only by the vendor."],
        "escalate": "Escalate to the vendor for laser energy instability.",
        "findings": [
            "CD mean shifted across all fields, dose monitor drifted",
            "laser energy log shows drift",
            "CD shift, focus normal, dose suspect",
        ],
        "actions": [
            "dose cal run, CD back to target",
            "laser service by vendor, dose cal, CD ok",
            "recalibrated dose, CD monitor pass",
        ],
    },
    {
        "rc_id": "RC-LITH-04", "module": "LITH", "sop_id": "SOP-LITH-004",
        "name": "Track resist coat problem (nozzle or hotplate)",
        "sop_title": "Resist Coat Thickness Troubleshooting (Track)",
        "params": [("resist_thickness", 1), ("cd_mean", -1)],
        "weight": 0.9, "downtime": (1, 6),
        "symptoms": [
            "Resist thickness out of range or non-uniform.",
            "CD shift linked to a specific coat or bake module.",
        ],
        "checks": [
            "Check resist thickness monitors by coat module.",
            "Inspect the dispense nozzle for dried resist or a drip.",
            "Check hotplate temperature uniformity with the calibration wafer.",
        ],
        "fix": [
            "Clean the dispense nozzle and run a dummy dispense.",
            "Recalibrate the hotplate if uniformity is out.",
            "Run a resist thickness monitor.",
        ],
        "accept": ["Resist thickness within 1,180 to 1,220 A.", "Hotplate uniformity within +/-0.3 C."],
        "parts": ["Dispense nozzle"],
        "safety": ["Resist is flammable: no ignition sources; use solvent-rated gloves."],
        "escalate": "Escalate to the track vendor if the hotplate cannot be calibrated.",
        "findings": [
            "resist thickness high on coat module 2, nozzle dried resist",
            "hotplate 3 non-uniform",
            "coat thickness high, nozzle drip",
        ],
        "actions": [
            "cleaned nozzle + dummy dispense, thickness ok",
            "hotplate recal, CD back",
            "nozzle replaced, monitor passed",
        ],
    },
    # ---------------------------------- WET ----------------------------------
    {
        "rc_id": "RC-WET-01", "module": "WET", "sop_id": "SOP-WET-001",
        "name": "Bath chemical concentration out of range (aged bath)",
        "sop_title": "Wet Bench Bath Change and Concentration Check",
        "params": [("oxide_etch_rate", -1)],
        "weight": 1.3, "downtime": (1, 4),
        "symptoms": ["Oxide etch rate drifting down as the bath ages."],
        "checks": [
            "Check bath age (wafer count and hours since change). Bath life is 2,000 wafers or 48 hours.",
            "Check the concentration monitor or run a titration.",
        ],
        "fix": [
            "Change the bath.",
            "Run 1 etch rate monitor after the bath stabilises (30 minutes).",
        ],
        "accept": ["Oxide etch rate within +/-4% of baseline."],
        "parts": [],
        "safety": ["Bath change uses HF: full chemical PPE and buddy system."],
        "escalate": "Escalate to chemical facilities for supply concentration issues.",
        "findings": [
            "ox ER down, bath at 2,150 wfrs",
            "titration low, bath aged",
            "bath past life, ER down",
        ],
        "actions": [
            "bath change, ER monitor ok",
            "changed bath, waited 30 min, ER back",
            "new bath, requal passed",
        ],
    },
    {
        "rc_id": "RC-WET-02", "module": "WET", "sop_id": "SOP-WET-002",
        "name": "Recirculation filter or pump shedding particles",
        "sop_title": "Wet Bench Filter Change and Particle Response",
        "params": [("particle_adders", 1)],
        "weight": 1.0, "downtime": (1, 6),
        "symptoms": ["Particle adders rising after wet clean; filter differential pressure high."],
        "checks": [
            "Check recirculation filter differential pressure and change date.",
            "Check recirculation pump for noise or seal wear.",
        ],
        "fix": [
            "Replace the recirculation filter and flush the loop.",
            "Replace the pump seal if worn.",
            "Run 2 particle monitors.",
        ],
        "accept": ["Particle adders at or below 15 on 2 monitors."],
        "parts": ["Recirculation filter", "Pump seal kit"],
        "safety": ["Drain and rinse the bath before opening the recirculation loop."],
        "escalate": "Escalate to the defect engineer if adders persist.",
        "findings": [
            "adders up, filter dP high",
            "recirc pump noisy, particles up",
            "filter overdue for change",
        ],
        "actions": [
            "replaced recirc filter, flushed, monitors ok",
            "pump seal replaced + new filter, adders down",
            "filter change, particles back to normal",
        ],
    },
    {
        "rc_id": "RC-WET-03", "module": "WET", "sop_id": "SOP-WET-003",
        "name": "Dryer problem causing watermarks",
        "sop_title": "Dryer (IPA/N2) Troubleshooting for Watermarks",
        "params": [("watermark_defects", 1)],
        "weight": 0.8, "downtime": (1, 6),
        "symptoms": ["Watermark defects after the rinse/dry step."],
        "checks": [
            "Check DI water resistivity (should be above 17.5 MOhm-cm).",
            "Check dryer IPA flow and N2 flow against setpoints.",
        ],
        "fix": [
            "Restore IPA and N2 flow to setpoint (clean or replace the IPA nozzle).",
            "If DI resistivity is low, raise a facilities request.",
            "Run a defect monitor.",
        ],
        "accept": ["Watermark defects at or below 3."],
        "parts": ["IPA nozzle"],
        "safety": ["IPA is flammable."],
        "escalate": "Escalate DI water issues to facilities.",
        "findings": [
            "watermarks up, IPA flow low",
            "N2 flow low on dryer",
            "DI resistivity 15 MOhm",
        ],
        "actions": [
            "cleaned IPA nozzle, flow ok, defects down",
            "fixed N2 regulator, watermarks gone",
            "facilities restored DI, monitor ok",
        ],
    },
    # ---------------------------------- CROSS-MODULE ----------------------------------
    {
        "rc_id": "RC-MET-01", "module": "ANY", "sop_id": "SOP-MET-001",
        "name": "Metrology false alarm (measurement tool error)",
        "sop_title": "Metrology Verification Before Process Tool Action",
        "params": [],
        "weight": 0.6, "downtime": (0, 2),
        "symptoms": [
            "Single OOC point with no supporting trend, often on one metrology tool only.",
            "Re-measurement gives a normal value.",
        ],
        "checks": [
            "Re-measure the wafer on a second metrology tool, or measure the golden reference wafer on the same tool.",
            "Check the metrology tool's own calibration status.",
        ],
        "fix": [
            "If the re-measurement is in control, close the OOC as a metrology false alarm: no process tool action.",
            "Raise a metrology calibration request for the measuring tool.",
            "Release the held lot after the re-measurement.",
        ],
        "accept": ["Re-measured value in control on a second metrology tool or golden wafer."],
        "parts": [],
        "safety": [],
        "escalate": "Escalate to metrology if the golden wafer reads out of range.",
        "findings": [
            "single point OOC, re-measured on second metrology tool in control",
            "golden wafer reading off on metrology tool, measurement error",
            "no trend, remeasure ok",
        ],
        "actions": [
            "closed as metrology false alarm, no tool action, lot released",
            "raised metrology cal request, lot released after remeasure",
            "remeasure in spec, released",
        ],
    },
    {
        "rc_id": "RC-GEN-01", "module": "ANY", "sop_id": "SOP-GEN-002",
        "name": "Unqualified change (recipe edit or PM without requalification)",
        "sop_title": "Change Control and Requalification After PM or Recipe Edit",
        "params": [],
        "weight": 0.4, "downtime": (1, 6),
        "symptoms": ["Step change right after a recipe edit, a PM or a part change."],
        "checks": [
            "Check the recipe change log and the PM log for changes in the 24 hours before the first OOC point.",
            "Confirm whether requalification was completed and signed off after the change.",
        ],
        "fix": [
            "Revert the recipe to the last qualified version, or complete the missed requalification.",
            "Hold the tool until requalification passes.",
            "Record the change in the change-control log.",
        ],
        "accept": ["Requalification passed and signed off by the module engineer."],
        "parts": [],
        "safety": [],
        "escalate": "Escalate repeated change-control misses to the module manager.",
        "findings": [
            "recipe edited yesterday without requal",
            "PM done but requal not completed",
            "step change right after part replacement, no requal record",
        ],
        "actions": [
            "reverted recipe to last qualified version, monitors ok",
            "requal done after PM, released",
            "completed requal for the new part, signed off",
        ],
    },
]

GENERAL_SOP = {
    "sop_id": "SOP-GEN-001",
    "sop_title": "General OOC Response and Lot Disposition",
}

# Notes that carry no troubleshooting value: used to model poor-quality closure notes.
VAGUE_NOTES = [
    "fixed",
    "tool back up",
    "PM done, ok",
    "see shift log",
    "ok now",
    "released per engr",
    "issue resolved",
]


def root_cause_by_id():
    return {rc["rc_id"]: rc for rc in ROOT_CAUSES}
