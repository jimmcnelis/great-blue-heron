# RIG v2.5 — GEOMETRY BRIEF (mechanism-first)

Written by Mordecai, 2026-11-04. Basis: the full character + motion study
(~/workspace/heron/art2/real-bird-measure/MOTION_STUDY_REPORT.md) and its addendum
(ADDENDUM_REPORT.md, same folder), plus the strike arbitration
(~/workspace/heron/art2/strike-measure/). Discipline per FARMS: the animal is a
mechanism; poses are states of the mechanism; body / controller / rendering stay
separate under ONE animal definition.

## 1. One animal definition
The creature-engine species package for the great blue heron carries the single
source of truth: segment lengths, joint limits, width profile. Rig v2.5, the pose
tracks, and the Path-3 fill all derive from it. No private copies of the numbers.

## 2. The neck mechanism
- ~20 links (skeleton mounts: ~20 cervical vertebrae, elongated mid-neck), not the
  handful of stations rig v2.4 used.
- Two bend zones, as measured: a forward bend low (throat) and a backward bend high —
  the visible kink behind the head is the strike hinge.
- Per-joint angle limits set so the canon poses are reachable BY CONSTRUCTION:
  - Deep coil: chord_base ≈ 0.27 × torso with arc : chord ≥ 1.9 (the coil stores
    ~twice its chord in arc).
  - Alert stance: chord_base ≈ 0.435; crouch-walk coil ≈ 0.363.
  - Standing strike peak: chord_base 0.62–0.71, chord76 0.49–0.60, arc ≈ 0.70 —
    reached by UNFOLDING, arc conserved in standing work. The v2.4 pathology
    (strike arc 29% SHORTER than its own idle arc; reach factor 0.95 vs the real
    2.4–2.6) is impossible in a fixed-arc chain.
- OUT OF SCOPE for v2.5: the lunge class (chord_base 0.77–0.87, arc at peak up to
  0.87). The product's standard strike is the standing spear; a lunge chart is a
  later decision, not a silent inclusion.

## 3. Release (controller layer)
- Ballistic strike: proximal→distal unfold fitted to the measured profile —
  small DIP first (chord falls 10–20%), then quarter-bins [~3 / ~12 / ~60 / ~25]%
  of reach, total extension 0.10–0.25 s. (Addendum revision of [3/10/78/9]:
  slow start confirmed twice; Q4 carries real weight.)
- Glean-stab is a SEPARATE slow class (~1.6 s extension, DS2) — its own chart,
  never blended into strike timing.
- Withdrawal 3–5× slower than extension when empty (study); with prey, handling
  comes first (bluegill catch→swallow ≈45 s; prey-dipping documented).

## 4. Widths
- Extension slimming target: mid-tube width ratio 0.55–0.65 (study canon; the
  addendum did not test it — carried as a target, flagged untested).
- Idle neck-base width corrected to the drawing: rig v2.4 ran ~40% wide at the
  base station (70 vs 49 units); v2.5 takes the width profile from the approved
  stills + grey-heron diagram (the bone chain runs thin; most tube width is feather).

## 5. Head and bill
- Bill ≈ 0.23 × torso (median of measured 0.20–0.31); head+bill ride the chain's
  distal links as one assembly — no separate head registration (spikes 2–3's
  failure mode is designed out, not patched).
- The eye is DRAWN, placed from the amber-cluster find (spike-3 side finding:
  extract_bill_profile silently returned no eye on corpus golds; the real eye is
  findable and its placement is part of this brief's checks).

## 6. THE GATE (cheap proof, point of use — before any fill or roster work)
Three mechanism poses rendered as BARE MASKS only: alert rest, deep coil,
standing strike peak.
- Auto-check per pose against canon bands: chord76, chord_base, arc, neck-base
  width. All must land in band.
- Visual check: peak-pose overlay against the approved strike still; Mordecai
  views it, then Jimmy judges.
- PASS = numbers in band AND Jimmy's visual pass. FAIL = work stops and reports;
  iterating is Jimmy's fresh decision (failure-discipline rule 2). One method,
  one shot.

## 7. Explicit non-goals for v2.5
- No lunge class. No fill changes (Path-3 fill runs on v2.5 geometry only after
  the gate passes). No wingbeat number — flight frequency is UNRESOLVED (Boga
  renders are rate-corrupted; ~0.44 Hz render value must never be baked).
  Landing/takeoff charts may use the measured phase structure (6 phases; long
  asymmetric balance; takeoff neck extended at liftoff, fold by +0.4–0.5 s;
  stretch = post-landing bilateral wing-spread hold ~3 s, no neck component)
  but flight timing waits for a rate-verified clip.
