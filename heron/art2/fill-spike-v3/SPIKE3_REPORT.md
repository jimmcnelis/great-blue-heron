# SPIKE 3 REPORT — re-register the heads (drawn-keypoint part registration)

**VERDICT: PRE-GATE FAIL — STOP. No fill run was made and none is owed.**
Gates A and B are moot under the brief's stop rule. One change, one shot, measured first.

---

## 1. PRE-GATE MEASUREMENTS (first, as ordered)

Pre-gate quantity: how much of the rig head∪neck footprint (mask channels 1∪2 of
the target pose's rig mask stack) is covered by the gold drawing's own content —
`|content(gold) ∩ footprint| / |footprint|`, spike-1 instruments
(`content_mask`, `labelmap`) unmodified.

*Note on the baseline: the brief cites 0.316 as the pre-gate baseline. In spike
2's record, 0.316 is the spike-2 FILL's part IoU vs gold (`part_metrics`).
Measured directly as gold-vs-footprint coverage, the same frame's baseline is
**0.3687**. Both are far below the 0.60 bar; the verdict is identical under
either reading.*

| quantity | value |
|---|---|
| gold strike_f0027 footprint coverage, as registered (baseline) | **0.3687** |
| gold strike_f0027 footprint coverage, after drawn-landmark re-registration | **0.1600** |
| pre-gate bar | ≥ 0.60 |
| **result** | **FAIL — coverage fell; the warp moves content OFF the footprint** |

The re-registration warp (Umeyama similarity, drawn→rig, all 8 prescribed
landmarks): scale **0.714**, rotation −11.9°, fit RMS **41.8 px**; per-point
residuals 27–61 px — *no* landmark is seated. The part zone of the re-registered
gold is visibly torn (broken neck, doubled head) — see
`pregate_rereg_sidebyside.png`, viewed by the crew.

## 2. THE LANDMARKS (extraction validated by eye)

Drawn landmarks were extracted from the gold frame itself (bill = yellow-class
pixels on the bill wedge; eye = amber iris cluster on the head mass; skull =
head-component centroid near the eye; crest root = head-mass boundary along the
back-of-bill axis; neck joints = content centroids at the rig spine stations).
Control check on **idle_f0030**: drawn↔rig deltas are 3–23 px at every landmark
(the idle registration was already good) — the detector finds the right
features. On strike_f0027 every green dot sits on the true drawn feature
(`landmarks_strike_f0027.png`, viewed).

**Drawn→rig deltas, strike_f0027 (px):**

| landmark | drawn (x, y) | rig (x, y) | delta |
|---|---|---|---|
| neck_s1 | (556.1, 363.8) | (569.2, 357.6) | 14.5 |
| neck_s2 | (574.4, 397.6) | (583.7, 390.5) | 11.7 |
| neck_s3 | (593.0, 426.1) | (596.6, 423.9) | **4.2** |
| crest_root | (658.0, 474.5) | (589.7, 444.9) | 74.5 |
| eye | (689.4, 533.7) | (626.2, 510.7) | 67.3 |
| skull | (677.2, 523.9) | (598.7, 463.3) | 99.2 |
| bill_base | (687.1, 557.0) | (614.7, 487.2) | 100.6 |
| bill_tip | (702.0, 596.0) | (674.3, 588.4) | 28.7 * |

\* the drawn bill tip is frame-clipped (the drawn bill exits the frame's bottom
edge); the true delta is larger.

## 3. THE STRUCTURAL FINDING — the residual is not rigid

The drawing disagrees with the rig **along the neck's own length**, not as a
rigid offset:

- The drawn neck joints sit essentially **on** the rig stations (4–15 px) —
  the drawn neck tube is registered along its whole run.
- The drawn head sits **67–101 px beyond** the rig head, displaced along the
  neck's continuation. Neck-run length: drawn station-1→skull = **200.8 px**
  vs rig station-1→head_c = **109.7 px** — the drawing's neck run is **1.83×**
  the rig's (station-3→head: 129.1 vs 39.5 px, 3.27×).

A similarity has one scale. Seating the head requires stretching the neck
segment ~1.8×; the already-registered neck joints forbid it. Least squares
compromises at scale 0.714 and seats nothing — hence coverage *falling* to 0.16.

Diagnostic only (not a registration run): even the five head points alone,
with the neck excluded, fit a similarity at RMS 32.5 px — the in-frame points
skull / bill_base / crest_root carry 26–37 px residuals. The drawn head's own
proportions (longer, steeper bill; skull-to-base geometry) also differ from
the rig head's, on top of the displacement. This was measured to size the
missing piece, not used toward any gate.

**Missing piece (for Mordecai's and Jimmy's decision, not attempted here):**
a non-rigid part warp — e.g. a landmark-driven thin-plate / piecewise warp
that can stretch along the neck axis while holding the neck stations — or a
re-examination of why the generated strike drawings' necks run ~1.8× long
against the rig at full extension. Settled by: the same pre-gate — coverage
of gold f0027's footprint ≥ 0.60 under the candidate registration, measured
before any fill verdicts.

Side observation, recorded because it affects every spike so far:
`spike_fill.extract_bill_profile` returns `eye_uv = None` on the corpus golds
(its iris test, tuned on the original Audubon scan, finds no cluster in the
generated drawings) — so spikes 1–2's `draw_eye` silently never drew an eye.
The eye the brief lists as a landmark exists in the drawings (amber cluster,
28 px at f0027, 72 px at idle_f0030) and is findable with an evidence-based
colour test; the rig-side eye counterpart
...[truncated 1837 chars]