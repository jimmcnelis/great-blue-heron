# FILL SPIKE v1 — mask-conditioned fill, two-frame gate

**Date:** 2026-11-04 · **Method under test:** path 3 as approved by
Jimmy (06:47) — replace ONLY the fill: donor gold texture warped into
rig v2.4 geometry and pasted region-by-region over the mask stack,
per-region structural ink targets (quantile luminance remap), and
thin structures drawn explicitly from rig geometry (bill from the
`bill_poly` wedge with the approved still's (axial × cross) colour
profile, eye at its head-frame offset, crest/plume strand
reinforcement in geometry-defined zones). Rig, corpus, pose
machinery and determinism kept. Gate frames' own pairs were EXCLUDED
from donors; ink *statistics* come from the approved stills, per the
method's design. One method, one shot, per the stop rules.

## Verdict

| Gate | Criteria | Result |
|---|---|---|
| A · Standing hold | black ∈ [0.252, 0.272]; IoU ≥ 0.813; MAD ≤ 32.1; reads as the engraving | **FAIL** — black **0.2599 ✓**, IoU **0.8586 ✓**, MAD **38.49 ✗** |
| B · Strike f0027 | bill present & intact; black ∈ [0.361, 0.381] (gold 0.3709 ± 0.01); head holds together | **FAIL** — bill **present ✓**, black **0.3605 ✗** (0.0004 below the band), head **fragmented ✗** |

**The spike fails. No rebuild is authorised by this run, and none
was attempted.** What follows is the full measurement record,
including the two mechanisms that demonstrably worked — they are
the salvageable content of the night.

## Gate A — the standing hold (`hold_fill.png`)

Measured with the v3 instrument, verbatim, against the registered
approved still (`idle_f0030`):

| measure | spike | v3 model | gate |
|---|---|---|---|
| black fraction | **0.2599** | 0.1255 | [0.252, 0.272] — PASS |
| slate fraction | 0.4682 | 0.6135 | (approved original 0.4646) |
| yellow fraction | 0.0236 | 0.0163 | (approved band 0.016–0.018 — spike runs hot) |
| IoU vs registered still | **0.8586** | 0.8125 | ≥ 0.813 — PASS |
| MAD inside bird | **38.49** | 32.11 | ≤ 32.1 — **FAIL** |
| bill centroid y | 175.6 | — | gold 175.9 |

Visual read (frames pulled and viewed, `sidebyside_hold.png`): it
*is* an engraving — hard hatch on the wing, black cap and brow, long
crest strands, strand plume, rusty thighs, the drawn bill intact and
golden with the eye placed. It is not a wash, and the geometry is
the approved bird's. Two visible defects: the neck's front carries a
heavy solid-black column where the gold has a slate neck and white
throat (donor texture + reinforcement darkening landed there), and
the yellow runs hot (0.0236) — the drawn bill plus remap stretch
pushed extra pixels into the yellow class.

Why MAD fails while IoU and black pass: MAD is a per-pixel measure
against *this specific drawing*. Each donor frame is a distinct
registration of the pose (donor MADs vs the gate frame run
21.9–45.4), and pasting eight regions from eight different donors
multiplies line-position jitter — every hatch line a few pixels off
its gate-frame position pays full per-pixel price. The v3 net's
blur, which the fidelity law rejects on sight, is exactly what MAD
rewards. Recorded as measured: the criterion is part of the gate as
briefed, and the spike does not meet it.

## Gate B — full-extension strike (`strike_f0027_fill.png`)

Same instrument, against the registered gold `strike_f0027`:

| measure | spike | v3 model | gold |
|---|---|---|---|
| black fraction | **0.3605** | 0.0701 | 0.3709 |
| IoU vs gold | 0.4837 | 0.6007 | — |
| MAD inside bird | 91.42 | — | — |
| bill centroid y | 525.9 | 509.1 | 562.7 |

- **Black 0.3605 vs band [0.361, 0.381] — FAIL, by 0.0004.** The
  structural-ink mechanism did the heavy lifting it was designed
  for (donor neighbours sit at 0.23–0.25; the v3 net managed
  0.070), but the final global trim had not converged when its
  iteration cap (3) ran out: each remap darkens pixels into the
  content mask, growing the denominator the fraction is measured
  against (recorded creep ≈ 0.30 → 0.36 across the three passes).
  Stated as a fact of this run; per the stop rules it was not
  chased.
- **Bill: PRESENT and intact** — a clean golden dagger, drawn from
  the rig wedge, where the v3 net's bill dissolved entirely. It
  sits ~37 px short in centroid terms (525.9 vs gold 562.7): the
  gold drawing's bill extends past the rig's bill tip, a property
  of that drawing the locked geometry does not carry.
- **Head: FAIL — it does not hold together.** The head/neck
  junction is broken into black-and-white shards with crest
  fragments floating detached (`sidebyside_strike_f0027.png`,
  left panel). Causes, named: whole-silhouette similarity warps
  align the body's mass, not a fast-moving head — donor head texture
  landed offset at the extension pose; the crest-zone reinforcement
  then inked the misplaced donor crest strands into hard black
  shards. The neck tube also pinches where the donors' S-curved
  necks were stretched across the target's straight extension tube.
- The saddle: gold's black saddle spans the torso∪wing footprint;
  regional targets split it (wing 0.4259 / torso 0.2764), so it
  formed only at the shoulder. And the overhang calibration,
  targeted at gold f27's overhang black (0.386 — which in gold
  lives in the crest fan), darkened the base donor's waterline
  into a heavy black band gold does not have.

## What the spike proved (the salvage)

- **Structural ink works as a mechanism.** Black fraction is now a
  carried, specified property: 0.126 → 0.260 on the hold (in band),
  0.070 → 0.361 at the strike (nearest miss in the programme's
  history), from donors that natively sit at 0.23–0.25. The v3
  report's diagnosis — "the remaining failure is ink" — has a
  working counter for the ink *level*, on both frames.
- **Drawn structures survive where generation dissolved them.**
  The bill, redrawn from rig geometry, is present and intact at
  the exact frame where Jimmy caught the net's beak disappearing.
  The eye placement transfers across poses by head-frame offset.
- **Donor texture keeps the engraving's hand.** On the hold, hard
  line, correct slate (0.468 vs approved 0.465), IoU above both
  the gate and the net — at poses the donors cover well, the
  composite reads as the plate, not a painting of it.
- **Determinism kept:** the hold built twice produced identical
  md5 hashes — the temporal gate's precondition survives the
  method change.

## What it did not prove / where it broke

- Pixel-exactness against a *specific* drawing (MAD) is worse
  than the net's blur whenever donor drawings disagree by a few
  pixels — i.e., everywhere except near-static poses.
- At the fastest, rarest pose, silhouette-level warps cannot
  place the head; reinforcement amplifies the misplacement
  instead of repairing it. The strike's head needs placement
  machinery this method does not have (per-part warps anchored
  on the head's own keypoints are the obvious untested shape —
  noted, not attempted, per the stop rules).
- Two gold properties live outside the locked geometry: the
  drawn bill's extra length at extension, and the saddle as a
  single cross-region feature. Regional decomposition splits
  both.

## Files

- `spike_fill.py` — the method, as run (single shot; unmodified
  after the run).
- `hold_fill.png`, `strike_f0027_fill.png` — the two gate frames.
- `sidebyside_hold.png`, `sidebyside_strike_f0027.png` — spike |
  registered gold | original approved still.
- `work/metrics_spike.json` — all measurements, regional ink
  targets, and the per-region donor log (base donors: hold
  `idle_f0011`; strike `strike_f0029`).

Standing orders honoured: rig v2.4 untouched (neck channel,
anchors as baked), no second method, no tuning after the run, no
roster bake, no device work. **The fill is not approved for
production. The next step is Jimmy's call.**
