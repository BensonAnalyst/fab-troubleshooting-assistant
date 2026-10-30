"""Hand-written evaluation questions. Ground truth comes from the fictional knowledge base.

Questions are deliberately phrased the way an engineer on shift would ask them, not with the
SOP's own wording, so retrieval has to match on meaning rather than copied keywords.
"""

# rc_id -> (question template, expected answer points). {tool} is filled with a real tool ID.
TROUBLESHOOTING = {
    "RC-ETCH-01": (
        "{tool} chamber B etch rate has been sliding for about a week and endpoint keeps getting longer. "
        "Nothing was changed. What's going on and how do I fix it?",
        ["Chamber polymer build-up / clean interval exceeded", "Check RF hours since last wet clean (interval 1,200 RF hours)",
         "Run O2 dry clean DC-O2-30 plus 5 seasoning wafers", "Wet clean PM if dry clean does not recover",
         "Release when etch rate is within +/-3% on 3 monitors"],
    ),
    "RC-ETCH-02": (
        "The 49-point map on {tool} shows the edge of the wafer etching much faster than the centre, "
        "and CD range keeps creeping up. Likely cause?",
        ["Focus ring erosion", "Check ring RF hours against the 800 RF hour life limit", "Replace the focus ring",
         "Leak-up rate below 2 mTorr/min, then season", "CD uniformity at or below 2.4 nm on 3 monitors"],
    ),
    "RC-ETCH-03": (
        "Getting helium flow alarms on {tool} and a few de-chuck errors. What should I check first?",
        ["ESC helium backside leak", "Run the He leak-up test (above 1.5 sccm indicates a leak)",
         "Clean ESC with IPA wipe and replace the He seal o-ring", "Vendor ESC replacement if still leaking",
         "Pass at or below 1.0 sccm"],
    ),
    "RC-ETCH-04": (
        "Reflected power on {tool} keeps spiking and I can see the plasma flickering. What do I do?",
        ["RF match or connector issue", "Check RF connectors for discolouration and torque, and match capacitor positions",
         "Run match auto-tune calibration", "Replace match capacitor if at travel limit",
         "Reflected power at or below 10 W, capacitors between 20% and 80%"],
    ),
    "RC-ETCH-05": (
        "Etch rate on {tool} jumped up suddenly after the weekend but chamber hours look normal. Could it be the gas side?",
        ["Process gas MFC drift", "Run rate-of-rise flow verification", "Recalibrate above 2% deviation, replace above 5%",
         "Purge the line after replacement", "All MFCs within +/-2%"],
    ),
    "RC-CVD-01": (
        "Film on {tool} is coming out thin in the middle of the wafer and uniformity gets worse every day.",
        ["Showerhead deposition / clogging", "Check RF hours since showerhead clean (interval 600)",
         "Extended NF3 clean (2x) and pre-coat", "Showerhead swap if not recovered", "Uniformity at or below 1.5%"],
    ),
    "RC-CVD-02": (
        "Particle counts on {tool} suddenly jumped and SEM shows big flakes. Where do I start?",
        ["Particle flaking from chamber walls", "Classify the particle map pattern",
         "Check whether the pre-coat was skipped after the last clean", "Extended clean plus thicker pre-coat, wet clean if still high",
         "Adders at or below 20 on 2 monitors"],
    ),
    "RC-CVD-03": (
        "On {tool}, refractive index and stress moved out but thickness is fine. What's the likely cause?",
        ["Heater or thermocouple temperature drift", "Check with the reference thermocouple wafer",
         "Replace or recalibrate TC if more than 3 C off", "Heater assembly replacement if zone power unstable",
         "TC within +/-2 C of reference"],
    ),
    "RC-CVD-04": (
        "Deposition rate on {tool} dropped sharply on the last two runs and the precursor flow reading is noisy.",
        ["Precursor delivery problem", "Check ampoule level (replace below 15%)", "Check vaporizer and line heater temperatures",
         "Purge line and run 2 thickness monitors", "Thickness within +/-2%"],
    ),
    "RC-CMP-01": (
        "Removal rate on {tool} keeps falling and the pad looks shiny.",
        ["Pad glazing or worn conditioner disk", "Disk life limit 40 hours, pad 1,500 wafers",
         "Replace conditioner disk; new pad with break-in if near life", "Removal rate within +/-5% on 2 monitors"],
    ),
    "RC-CMP-02": (
        "We're seeing arc-shaped micro-scratches on {tool} wafers since yesterday.",
        ["Slurry delivery problem or agglomeration", "Check POU filter differential pressure and slurry flow",
         "Replace POU filter and flush", "Quarantine a new slurry lot if one was introduced", "Scratches at or below 5"],
    ),
    "RC-CMP-03": (
        "Uniformity on {tool} is bad near the wafer edge and the head is throwing a leak alarm.",
        ["Carrier head membrane or retaining ring wear", "Membrane 3,000 wafers, retaining ring 6,000 wafers",
         "Rebuild the head and run zone pressure calibration", "WIWNU at or below 4.5%"],
    ),
    "RC-CMP-04": (
        "Dishing is going up on {tool} and the endpoint trace looks flat. Why?",
        ["Optical endpoint drift or clouded pad window", "Compare trace with golden reference; inspect window",
         "Clean window or replace pad, recalibrate endpoint", "Dishing at or below 420 A"],
    ),
    "RC-LITH-01": (
        "Daily overlay on {tool} is creeping up and the error looks like a rotation, not random. What should we run?",
        ["Overlay drift from stage or alignment calibration", "Decompose overlay into translation, rotation, magnification",
         "Run stage grid and alignment calibration, update APC corrections", "Overlay at or below 5.0 nm"],
    ),
    "RC-LITH-02": (
        "There's a focus hot spot at exactly the same place on every wafer from {tool}.",
        ["Wafer chuck contamination", "Check whether the spot is fixed to the chuck or moves with the wafer",
         "Clean the chuck with the approved stone", "Focus error at or below 30 nm, no repeating spot"],
    ),
    "RC-LITH-03": (
        "CD is off across every field on {tool} but focus looks fine. What's the next step?",
        ["Exposure dose drift", "Check dose monitor and laser energy log", "Run dose calibration; vendor laser service if unstable",
         "CD mean within 44.0 to 46.0 nm"],
    ),
    "RC-LITH-04": (
        "Resist thickness on coat module 2 of {tool} is out of range and CD is shifting on wafers coated there.",
        ["Track resist coat problem", "Inspect dispense nozzle; check hotplate uniformity",
         "Clean nozzle and dummy dispense; recalibrate hotplate", "Resist thickness 1,180 to 1,220 A"],
    ),
    "RC-WET-01": (
        "Oxide etch rate on {tool} is dropping toward the end of the day. The bath is about two days old.",
        ["Aged bath / concentration out of range", "Bath life 2,000 wafers or 48 hours", "Change the bath",
         "Wait 30 minutes then run etch rate monitor", "Within +/-4% of baseline"],
    ),
    "RC-WET-02": (
        "Particles are up after clean on {tool} and the filter pressure drop reading is high.",
        ["Recirculation filter or pump shedding", "Replace filter and flush loop", "Replace pump seal if worn",
         "Adders at or below 15 on 2 monitors"],
    ),
    "RC-WET-03": (
        "Seeing watermark defects on {tool} after drying.",
        ["Dryer problem", "Check DI resistivity (above 17.5 MOhm-cm) and IPA/N2 flows",
         "Clean or replace IPA nozzle", "Watermarks at or below 3"],
    ),
    "RC-MET-01": (
        "Got a single OOC point on etch rate from {tool}, with no trend before it. Should I take the chamber down?",
        ["Verify the measurement first (possible metrology false alarm)", "Re-measure on a second metrology tool or golden wafer",
         "If in control, close as false alarm with no tool action", "Release the lot and raise a metrology calibration request"],
    ),
    "RC-GEN-01": (
        "Thickness on {tool} stepped out right after yesterday's recipe edit. What's the procedure?",
        ["Unqualified change", "Check recipe change log and PM log", "Revert to last qualified recipe or complete requalification",
         "Hold the tool until requal passes and record in change-control log"],
    ),
}

# Which module's tool to put in the question for cross-module root causes
CROSS_MODULE_TOOL = {"RC-MET-01": "ETCH", "RC-GEN-01": "CVD"}

# (question, expected SOP, answer points, SOP sections that contain the answer)
PROCEDURE = [
    ("What's the wet clean interval for Kestrel K9 etch chambers?", "SOP-ETCH-001", ["1,200 RF hours"], ["05"]),
    ("What leak-up rate is acceptable after replacing a focus ring?", "SOP-ETCH-002", ["Below 2 mTorr/min"], ["07"]),
    ("What PPE do I need for a wet bench bath change?", "SOP-WET-001", ["Full chemical PPE", "Buddy system (HF)"], ["04"]),
    ("When should an MFC be replaced instead of just recalibrated?", "SOP-ETCH-005",
     ["Replace above 5% deviation on rate-of-rise", "Recalibrate above 2%"], ["06"]),
    ("What are the life limits for the CMP carrier head membrane and retaining ring?", "SOP-CMP-003",
     ["Membrane 3,000 wafers", "Retaining ring 6,000 wafers"], ["05"]),
    ("What must an OOC closure note contain?", "SOP-GEN-001",
     ["Symptom", "Root cause with code and confirming check", "Action including parts", "Verification result"], ["04"]),
    ("How fast must an OOC be acknowledged, and when does a down tool have to be escalated?", "SOP-GEN-001",
     ["Acknowledge within 15 minutes", "Escalate if down longer than 8 hours"], ["03"]),
    ("What DI water resistivity is needed for the wet bench dryer?", "SOP-WET-003", ["Above 17.5 MOhm-cm"], ["05"]),
    ("Who is allowed to replace the ESC on a Kestrel K9?", "SOP-ETCH-003", ["Vendor replacement only"], ["06", "08", "09"]),
    ("How cool does a CVD chamber need to be before a heater replacement?", "SOP-CVD-003", ["Below 50 C"], ["04"]),
    ("What overlay value do we need after a stage calibration?", "SOP-LITH-001", ["At or below 5.0 nm"], ["07"]),
    ("How long should I wait after a bath change before running the etch rate monitor?", "SOP-WET-001", ["30 minutes"], ["06"]),
]

# Harder versions of troubleshooting questions (added in Week 3). They describe the symptom in plain
# words that avoid the SOP's own vocabulary, so keyword search cannot match on shared terms.
PARAPHRASE = {
    "RC-ETCH-01": "The tool {tool} is getting slower and slower at clearing the film over the past week, "
                  "and each run needs longer to finish. Nothing was changed. What's wrong?",
    "RC-ETCH-02": "Wafers from {tool} come out over-processed in a ring at the rim, a bit worse every day. Which worn part should I suspect?",
    "RC-ETCH-03": "On {tool} the wafer doesn't stay clamped properly and the backside cooling keeps alarming. Where do I start?",
    "RC-ETCH-04": "Energy bouncing back toward the generator keeps jumping on {tool} and the glow looks unstable. What should I check?",
    "RC-CVD-01": "Film from {tool} is thinner in the middle of the wafer than at the rim, and it's worse each day. Why?",
    "RC-CVD-03": "Films from {tool} have the wrong optical constant and the strain is off, yet the film is as thick as normal. Likely cause?",
    "RC-CMP-01": "Polishing on {tool} takes longer and longer to take off the same amount, and the polishing surface looks glossy.",
    "RC-CMP-02": "Wafers off {tool} show fine curved marks under inspection, starting right after yesterday's chemistry delivery.",
    "RC-LITH-02": "Every wafer from {tool} is blurry at exactly the same spot. What do I do?",
    "RC-WET-01": "The oxide strip on {tool} gets weaker as the day goes on; the chemistry was last replaced two days ago.",
    "RC-WET-03": "Spots shaped like dried droplets show up on wafers after the final drying step on {tool}.",
    "RC-MET-01": "One reading from {tool} jumped outside the limits, but every earlier reading was normal. Do I stop the tool?",
}

# Questions the knowledge base cannot answer. The assistant should say so, not guess.
UNANSWERABLE = [
    ("How do I tune beam current on the ion implanter?", "There is no implant module in the knowledge base."),
    ("What was the dollar cost of ETCH-02 downtime in March 2025?", "Downtime hours exist, but no cost data does."),
    ("What is the base pressure specification for a Kestrel K9 chamber?", "No SOP states a base pressure specification."),
    ("Which engineer is the best at fixing CMP tools?",
     "Closure notes carry engineer initials, but ranking people from them is not a troubleshooting question and should be declined."),
    ("Give me the full step parameters of the DC-O2-30 dry clean recipe.", "The SOP names the recipe but does not document its steps."),
    ("What is the PM schedule for our EUV scanners?", "The lithography tools in the knowledge base are not EUV scanners."),
]

# Short names used in history questions
RC_SHORT = {
    "RC-ETCH-01": "chamber polymer build-up", "RC-ETCH-02": "focus ring erosion", "RC-ETCH-03": "a helium backside leak",
    "RC-ETCH-04": "RF match problems", "RC-ETCH-05": "MFC drift", "RC-CVD-01": "showerhead clogging",
    "RC-CVD-02": "particle flaking", "RC-CVD-03": "heater temperature drift", "RC-CVD-04": "precursor delivery problems",
    "RC-CMP-01": "pad glazing", "RC-CMP-02": "slurry scratches", "RC-CMP-03": "carrier head wear",
    "RC-CMP-04": "endpoint problems", "RC-LITH-01": "overlay drift", "RC-LITH-02": "focus hot spots",
    "RC-LITH-03": "dose drift", "RC-LITH-04": "resist coat problems", "RC-WET-01": "aged bath issues",
    "RC-WET-02": "filter particle issues", "RC-WET-03": "watermark defects",
}
