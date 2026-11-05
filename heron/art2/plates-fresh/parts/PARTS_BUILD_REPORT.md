# PARTS-BUILD REPORT — ALERT plate (parts route, 2026-11-04)

Built under RESET-2026-11-04.md + CREW_MEMORY.md, per ART_DESIGN.md §3
(the six-part decomposition) and LEG_CANON.md. Geometry imported from the
mechanism (`rig_v25.py` / `animal_v25.json`) — never re-derived, never
traced from any image. No pre-reset image and no prior-batch plate was an
input or donor anywhere in this build. One build, measured once.

## RESEMBLANCE VERDICT — FAIL (gate 0, judged first, in plain words)

**This plate does not read as a heron. It reads as a labeled diagram of
one** — six parts stuck together, each speaking a different clip-art
dialect:

- The **torso is a polka-dot dome**: the folded wing's scallops were built
  as filled ellipses in alternating shades, and at plate scale they read
  as bubble-wrap dots across a big rounded mass — the same dome family
  Jimmy rejected in batch 3, now with spots.
- The **neck is a pale pipe**: flat color-zone bands + constant-v hatch +
  cross-ticks add up to a visible windowpane grid with ladder rungs, and
  the dorsal stipple reads as foam. It is the "rigid tube" failure drawn
  — smooth, plastic, segmented like a hose.
- The **plume fails Jimmy's tell**: the strands *are* countable (13), but
  they are stiff, evenly spaced icicle daggers hanging into open paper —
  not a shaggy breast curtain. Countable was necessary; it was never
  sufficient.
- The **legs are banded sticks**: placement is right, but the thigh
  scallop arcs render as even barber-pole stripes, and the emergence
  skirt strokes stand up like hairs.
- The **tail hangs as three melted drips** (the torso loop's rear-bottom
  lobes, filled with the light belly tone).
- The **head is the only part that reads as drawn from nature** — compact
  skull, eye seated, dagger bill — and even it is let down by its
  occipital plumes, which follow the mechanism spike yet read as stiff
  antennae/whiskers at face height, and by the black shoulder patch below
  it, which reads as a floating hole.

**Root cause, named:** the structural layer of the parts method WORKED —
every anchor landed (see the gate table). What failed is the
*mark-making* layer. This build's textures are procedural pattern-fills
(PIL polygons, ellipse stamps, regular hatch), and pattern-fill does not
become engraving by being clipped to a silhouette. The missing piece is a
**per-part texture language that reads as engraved line at device scale**
— fine directional marks following form, gated by eye per part — and the
test that settles it is a **one-part texture spike** (the neck sheet, or
one wing patch) judged against the resemblance gate *before* any
reassembly. Per one-shot discipline, whether that spike runs is Jimmy's
decision; this crew does not rebuild.

## GATE TABLE (measured off the finished PNG)

| Gate | Result | Read |
|---|---|---|
| 0. Resemblance / plume tell | **FAIL** | see verdict above — judged first, decides the plate |
| chord_base (band 0.40–0.47) | **0.463** grounded (neckbase grounded (598, 221); skull derived from the placed eye via the exact head-frame offset) · 0.456 by construction | PASS |
| Eye at anchor | **0.29 px** — amber centroid (754.8, 35.4) vs anchor (754.7, 35.7) | PASS (by construction, verified on the artifact) |
| Ripple rings at the joints | rings centred exactly on (406, 382) and (358, 382) = the intertarsal joints; **offset 0**; nothing drawn below the rings; no band, no line, no wash | PASS (by construction, verified on the crop) |
| Leg emergence (band 0.53–0.61) | near **0.590**, far **0.536** (design alert 0.59 / 0.531) | PASS |
| Upper segment, visible (band 0.21–0.25) | near **0.214**, far **0.231** (exit→joint on the finished plate) | PASS |
| Feet-centre | 0.521 by construction from the corrected traces (feet are underwater, undrawn — stated as construction, per the batch-2 brief's convention) | as designed |
| Ink, black/content (band 0.260–0.300) | **0.2436** — under the floor by 0.016 (black/frame 0.0416; content 0.1708) | **FAIL** — consistent with the flat-fill look: not enough dark line work |
| Framing | content bbox x 124–874, y 27–389; margins L 124 / R 149 / T 27 / B 210 — whole bird in frame, nothing clipped | PASS |

## SEAM INVENTORY (every seam, and how it was handled)

1. **Neck root × torso** — tube drawn first, torso silhouette clipped it
   at the chest edge, ink shoulder patch laid over the junction. The
   patch reads as a floating black oval — a hole, not a cap. **VISIBLE.**
2. **Head × neck tip** — head layer overlaps the tube end; geometrically
   clean, but the occipital strands (built to the mechanism spike, tip
   local (−57, −13)) are stiff straight tapers and read as antennae.
   **READ VISIBLE.**
3. **Plume roots × chest/neck front** — roots distributed along the
   chest edge + lower neck front as designed; the strands fall past the
   belly line into open paper and read as detached icicles. **VISIBLE.**
4. **Legs × torso** — legs drawn under the torso; emergence computed as
   the trace's exit from the smoothed silhouette; rusty skirt tufts laid
   over the edge. Geometry clean; the tufts read as upright hairs.
   **MINOR.**
5. **Ripples × shins** — rings centred on the joints, shins end inside
   the rings. The one junction that works exactly as designed. **NONE.**
6. **Wing × belly** — the scallop field stops at a hard dividing curve;
   reads as two fabrics sewn together. **VISIBLE.**
7. **Torso rear (tail)** — rigid with the torso per design §3.6; the
   loop's rear-bottom lobes in light belly tone read as melted drips at
   alert. **VISIBLE.**

## CANON NOTE (Jimmy, 2026-11-04 12:54 — "the skin can stretch")

Recorded and complied with: arc conservation is treated as a
**standing-posture budget**, not an absolute. This build is the alert
(standing) plate — visible arc 0.707 against the 0.72 budget, no stretch
invoked, so the note does not change it. The (u, v) neck sheet built here
already carries the design's v-stretch headroom (§3.2 swallow provision);
nothing in the sheet or the traces hard-locks arc length for future
poses, where the addendum's pooled peak arc (0.70–0.87) and local swallow
distension will need that give.

## WHAT THE PARTS THEMSELVES ARE (deliverables)

The part sheets in `parts/` are structurally sound as the rig's future
art source — silhouettes, anchors, strand roots, and traces are all exact
— but their current texture rendering is the failed layer described
above and should be re-skinned, not reused as finished art.

- `alert_parts_plate.png` — the assembled plate (1024×600)
- `parts/torso.png` · `parts/neck.png` · `parts/neck_uv_sheet.png` (the
  flat (u, v) station sheet) · `parts/head.png` · `parts/plume.png` ·
  `parts/legs.png` (legs + ripple rings)
- `sidebyside/plate_vs_mask.png` — plate beside the mechanism mask
- `crops/` — head, legs/ripples, plume/neck, torso
- `work/build_parts.py` — the build (deterministic, seeded);
  `work/build_info.json` — construction bookkeeping

## DISCLOSURES

- Texture shades are palette colours blended toward ink/white for
  engraved shading (DEEPWING = darkslate→ink 0.35, etc.); base colours
  are the species palette exactly. The eye's iris uses an amber
  (240, 170, 40) in the orange family — the palette has no separate eye
  entry.
- Authored at 3× supersample, downscaled with LANCZOS to 1024×600.
- Plume strand count is 13 (4 neck-front roots + 9 chest roots) — both
  too few and wrong in character; named in the verdict, not hidden.
- The torso silhouette is the mechanism's fixed loop (strike-derived
  trace, rigid across poses per the mechanism's own renders); its
  rear-bottom lobes are a silhouette fact the color fill exposed.
