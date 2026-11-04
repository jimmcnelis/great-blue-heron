# FILL SPIKE v2 — per-part head warps, two-frame gate

**Date:** 2026-11-04 · **Method under test:** spike 1's fill with ONE
change (Jimmy's go, 06:57): head+neck treated as one part, warped
and inked anchored on the head's own rig keypoints; the part carries
its own ink target, protected from the global trim; the torso∪wing
saddle inked as one union set; the trim iterates to convergence.
Everything else — donor fill, structural-ink mechanism, drawn
bill/eye, crest/plume reinforcement, rig v2.4, corpus, determinism —
carried over from spike 1 verbatim (instruments imported unmodified
from `fill-spike-v1/spike_fill.py`).

## Verdict

| Gate | Criteria | Result |
|---|---|---|
| A · Standing hold | black ∈ [0.252, 0.272]; IoU ≥ 0.85; neck-front column GONE (visual); MAD reported | **FAIL** — black **0.2656 ✓**, IoU **0.8591 ✓**, MAD 38.31 (context below), **column still present ✗** |
| B · Strike f0027 | bill intact (visual); black ∈ [0.361, 0.381]; head/neck junction INTACT (visual); IoU ≥ 0.60 | **FAIL** — bill **present ✓**, black **0.3714 ✓**, **junction shattered ✗**, IoU **0.4844 ✗** |

**The spike fails both gates. Per the stop rules, nothing further
was run: no second variation, no rebuild.** What follows is the
full measurement record, including the one mechanism that did land
(trim convergence with part-owned ink) and the structural finding
that explains why per-part warps could not bite at these frames.

## Gate A — the standing hold (`hold_fill.png`)

Measured with the v3 instrument, verbatim, against the registered
approved still (`idle_f0030`):

| measure | spike 2 | spike 1 | gate / gold |
|---|---|---|---|
| black fraction | **0.2656** | 0.2599 | [0.252, 0.272] — PASS |
| slate fraction | 0.4635 | 0.4682 | gold registered 0.4740 |
| yellow fraction | 0.0234 | 0.0236 | gold ~0.017 (runs hot, as spike 1) |
| IoU vs registered still | **0.8591** | 0.8586 | ≥ 0.85 — PASS |
| MAD inside bird | 38.31 | 38.49 | reported, not tuned to |
| bill centroid y | 174.3 | 175.6 | gold 175.9 |
| head∪neck part IoU vs gold | 0.8933 | — | best-aligned region of the frame |
| head∪neck part MAD | 25.43 | — | vs 38.31 frame-wide |
| neck-front black | **0.0710** | 0.0710 | gold **0.0131** — column gate FAIL |
| neck-back black | 0.0742 | 0.0936 | gold 0.0654 |

Visual read (`sidebyside_hold.png`, viewed): the frame again reads
as the engraving — hard hatch, crest strands, drawn bill intact —
and the neck front again carries the solid black column where the
gold has slate neck and white throat. The column is unchanged to
the third decimal (0.0710 both spikes).

**Why the change could not fix Gate A, stated plainly:** the idle
family lives on a single canvas and a single pose, so every donor's
head anchors are the target's. The part warp for Gate A is the
identity (logged: warp (1, 0, 0, 0), anchor RMS 0.0) — correctly,
not as a bug. Gate A therefore exercised only the ink half of the
change (union target, trim protection), and the column is not an
ink-level defect: it is a *placement* defect. The donor texture's
dark neck stripe sits front-of-channel after silhouette
registration, the union remap darkens the union's darkest pixels
first — which are that misplaced stripe — and no ink-set change
relocates texture. The part-owned ink did hold its level (part
black final 0.1616 vs union target 0.1466, the +0.015 drift being
the drawn bill outline and pupil painted into the footprint after
the remap), but level was never the column's problem.

## Gate B — full-extension strike (`strike_f0027_fill.png`)

Same instrument, against the registered gold `strike_f0027`:

| measure | spike 2 | spike 1 | gold / gate |
|---|---|---|---|
| black fraction | **0.3714** | 0.3605 | band [0.361, 0.381] — PASS |
| IoU vs gold | **0.4844** | 0.4837 | ≥ 0.60 — **FAIL** (v3 net: 0.6007) |
| MAD inside bird | 91.57 | 91.42 | — |
| bill centroid y | 526.2 | 525.9 | gold 562.7 (rig-tip shortfall, known) |
| head∪neck part black, final | 0.0994 | neck alone 0.2542 | part target 0.0888 (gold union) |
| head∪neck part IoU vs gold | 0.316 | — | see finding below |
| head∪neck part MAD | 100.39 | — | see finding below |

- **Bill: PRESENT and intact** — the drawn golden dagger reaches
  the water, as in spike 1. Drawn structures surviving motion
  remains proven; the centroid shortfall is the locked geometry's
  (gold's drawn bill extends past the rig tip), unchanged.
- **Black 0.3714, mid-band — the trim converged.** First measured
  pass 0.4224 (over band: the part-owned remap sets plus the
  saddle-union remap overshot), one solved trim pass → 0.3714,
  inside [0.361, 0.381]. And the part *kept* its ink: part black
  final 0.0994 against its 0.0888 target (drift = drawn bill/eye),
  where spike 1's unprotected trim blew the strike neck out to
  0.2542 against a 0.0881 gold. Part-owned ink targets are now
  honoured end-to-end, on both frames.
- **Head/neck junction: FAIL — still broken.** Viewed at native
  resolution: the neck is kinked and two-toned with a hard black
  triangular shard embedded at the junction; the crest is a burst
  of long black spikes standing off the head, several detached;
  the black cap mass smears down the face. Different debris than
  spike 1's, same verdict: the junction does not hold together.
- **IoU 0.4844 — FAIL**, unchanged from spike 1 (0.4837). The v3
  net's 0.6007 comes from a content mask trained onto the drawing;
  donor compositing fills the rig footprint, and at this frame the
  drawing does not fill its own rig footprint (next section).
- The saddle, inked as one torso∪wing set (union target 0.3233),
  reads as one continuous feature across the shoulder in the
  frame — the spike-1 split (wing forced to 0.4259, torso to
  0.2764, saddle forming only at the shoulder) does not recur.

## The structural finding — why the warps had no purchase

The change assumed the head's misplacement is a *pose* difference
that keypoint anchoring can correct. At the gate frame it is not:

1. **Plateau donors share the gate frame's head exactly.** Strike
   frames 26–29 carry identical head parameters (hx 30.0, hy 20.0,
   coil 0.15, head_pitch 56.0 — identical to float dust). Their
   anchor sets are the target's; their warps are the identity
   (RMS 0.00), correctly. The ink-closeness pick chose f0026
   (|Δ| 0.0032) — an identity-warp donor. There was nothing for
   the warp to correct *with*.
2. **Every other donor is a non-similarity configuration.**
   Anchor-fit RMS for frames 18–25 and 30–36 runs 16–128 px:
   a coiled or withdrawing neck cannot be similarity-warped onto
   the extended neck, so the mechanism has no valid traction at
   distance either.
3. **The defect lives between each drawing and its own rig.**
   Gold f0027's drawn head∪neck content overlaps the rig part
   footprint at IoU **0.316** (part MAD 100.39): the drawn neck
   is narrower than the rig's neck channel and runs along one
   side of it. Rig keypoints are functions of the rig; they are
   blind by construction to where a *drawing's* head sits inside
   its rig. Warping donors by rig anchors aligns rig to rig —
   the residual that shatters the junction is drawing-to-rig,
   and it rides through untouched.

In one sentence: per-part warps anchored on rig keypoints correct
pose differences; the strike's head failure is a registration
residual, and at the one frame where it matters most, the donor
pool offers either identical geometry (no correction available)
or unreachable geometry (no valid warp).

## What the spike proved (the salvage)

- **Part-owned ink targets hold end-to-end.** With the part
  protected and the trim solving for the overall band, Gate B
  landed mid-band (0.3714 vs gold 0.3709 — the closest black
  reading of the programme) while the part stayed at its own
  target instead of being re-inked to 0.254. The ink half of
  the part design works and is worth keeping in any successor.
- **The saddle as one ink set works**: union remap over torso∪wing
  forms the cross-region feature whole.
- **Determinism kept**: the hold built twice produced identical
  md5 hashes.
- **Gate A's head∪neck is the best-aligned region on the hold**
  (part IoU 0.8933, part MAD 25.43 vs 38.31 frame-wide) — at
  covered, near-static poses the part composite is sound; its
  remaining defect is the donor stripe's placement inside the
  neck channel, a sub-channel registration residual of the same
  family as the strike's, at smaller amplitude.

## Files

- `spike2_fill.py` — the method, as run (single shot; unmodified
  after the run).
- `hold_fill.png`, `strike_f0027_fill.png` — the two gate frames.
- `sidebyside_hold.png`, `sidebyside_strike_f0027.png` — spike |
  registered gold | original approved still.
- `work/metrics_spike2.json` — all measurements, per-region donor
  log, part warp + anchor RMS, trim trace (base donors: hold
  `idle_f0011` with part donor `idle_f0013`; strike base
  `strike_f0029` with part donor `strike_f0026`).

Standing orders honoured: rig v2.4 untouched (neck channel,
anchors as baked), one change, one shot, no tuning after the run,
no roster bake, no device work. **The fill is not approved for
production. The next step is Jimmy's call.**
