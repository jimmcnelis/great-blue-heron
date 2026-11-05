# EYE-FIRST REPORT — Alert plate, eye-first batch (2026-11-04)

**Verdict first: this batch reads as herons.** All eight candidates read as a real
great blue heron at a glance — the first batch all day where that is true of every
single candidate. The change that did it is Jimmy's 13:05 correction: for the
first time, the drawing was conditioned on REAL birds from the reference library,
not on the generator's prior plus our numbers. The top 3 below go to Jimmy as
pictures. His eye is the gate; this ranking is the filter.

Selection was by eye, per the EYE-FIRST law (CREW_MEMORY): resemblance first,
numbers after, as diagnostics only. No candidate was discarded by a measurement.

## What conditioned what (the reference library enters the drawing)

Every candidate was conditioned on the fresh mechanism canvas (alert pose,
corrected legs; rebuilt this run from rig_v25 — T = 493.85, identical geometry
to batch 3's canvas) **plus real great blue heron frames**:

| Ref | Source (library) | What it teaches |
|---|---|---|
| R1 `ref_ur_alert_t75.jpg` | UR4n4gYX2T4 @ 75 s (the atlas_01 standing bird, clean raw frame — the annotated atlas image itself was NOT used) | standing alert profile: compact head, modest eye, the lush strand curtain, lean body |
| R2 `ref_ur_stand_f0530.jpg` | UR4n4gYX2T4 frame f0530 (real-bird-measure frame set) | second standing bird, head up, bill closed |
| R3 `ref_alvarez_t20.jpg` | fb-alvarez-standing @ 20 s | standing bird, head in profile, neck/body mass |
| R4 `ref_underlegs_t9.jpg` | fb-underwater-legs @ 9 s | true legs: stilt-thin, dark, near-vertical |

| Candidate | Canvas | Real frames | Prompt lever |
|---|---|---|---|
| c1 | ✓ | R1 + R4 | base |
| c2 | ✓ | R1 + R3 | plume pushed hardest |
| c3 | ✓ | R2 + R4 | torso leanness pushed hardest |
| c4 | ✓ | R1 + R2 | head/eye pushed hardest |
| c5 | ✓ | R2 + R3 | freer: "study only for pose, bird from the photographs" |
| c6 | ✓ | R1 | finer stipple / softer hand-color |
| c7 | ✓ | R4 + R3 | stance/legs pushed hardest |
| c8 | ✓ | R1 + R2 | "if it starts to look generic, pull it back to the photographs" |

All prompts carried the written style rules and hygiene laws: Audubon manner;
water = ink ripple rings at the legs only, blank paper otherwise; whole bird in
frame with margin; plume a lush curtain of separated strands; compact head,
modest eye; lean body, no dome.

## Ranking (by resemblance, Jimmy's criteria in order)

1. **c3 → plate_1** — The leanest, most level-backed body of the eight — a long
   horizontal oval like the real bird, no dome. Full lush strand curtain, compact
   head with a modest amber bead eye, long stilt legs balanced under the middle.
   Costs: neck is slate-dark down the front (less pale than the photographs),
   thighs heavily scale-textured.
2. **c1 → plate_2** — Immediately a heron: fine wispy curtain, natural compact
   head, the longest stilt legs of the batch. Costs: the back is rounded and
   deep (a mild dome), and pale wing filaments spill across the back.
3. **c5 → plate_3** — Elongated, fairly level body and a lush curtain; calm,
   balanced stance. Costs: a slight shoulder dome, shins banded pale above the
   dark, and a faint smudge on the paper at the left edge.
4. **c2** — The lushest plume of the batch and a fine S-neck, but the body is a
   high rounded mass and the legs are stunted — the bird sits low and heavy.
5. **c7** — Long body, rich dark slate, lush plume; but a moderate dome and the
   strongest ringed, staring eye of the engraved plates.
6. **c6** — Handsome engraving, elegant pale neck; the back is one big dome and
   the body reads heavy throughout.
7. **c4** — The roundest balloon torso of the batch. Lovely neck and plume
   cannot rescue the body mass.
8. **c8** — Reads as a heron, but in a flatter modern-illustration register
   rather than engraving; the neck is compressed and stocky, and the eye is a
   ringed bullseye — least like the real bird of the eight.

## Diagnostics for the top 3 — DIAGNOSTICS, NOT GATES

Measured after the ranking, same protocol as batches 1–3 (visual-grounding
landmarks; torso T_p = max pairwise over tail/chest/back-top/belly; ink by the
v3 protocol). These numbers describe what each picture costs; they did not
select it.

| | plate_1 (c3) | plate_2 (c1) | plate_3 (c5) |
|---|---|---|---|
| Torso T_p (mechanism: 494 px) | 628 px | 549 px | 593 px |
| chord_base (design 0.456) | 0.323 | 0.399 | 0.318 |
| Eye offset from computed anchor | 29.9 px | 10.2 px | 12.9 px |
| Bill (× torso; canon ≈0.23) | 0.317 | 0.239 | 0.281 |
| Ripple seat, near/far (× torso) | 0.173 / 0.184 | 0.214 / 0.196 | 0.131 / 0.121 |
| Leg emergence, near/far (tail→chest fraction) | 0.587 / 0.511 | 0.542 / 0.467 | 0.510 / 0.564 |
| Ink, content-black fraction | 0.269 | 0.223 | 0.237 |
| Framing | in frame; tightest margins (tail 26 px, bill 47 px) | comfortable | comfortable |

**The shared cost, named plainly:** in all three (and all eight), the generator
followed the photographs over the canvas on the legs — it drew full-length legs
standing in water, so the ripple rings sit at the *feet*, ~0.12–0.21 torso below
the knuckle joints, instead of legs ending at the joint with the rings ringing
the joint. The water law's intent still holds in every plate — ripples only, no
band, no wash, nothing drawn below the rings — but the ring placement is the
photographs' truth, not the mechanism's convention. Also shared: the birds are
drawn bigger than the mechanism (T_p 549–628 vs 494), which compresses the
chord readings. Plate_1's eye offset (29.9 px) is the worst number in the table;
its eye nonetheless reads modest and natural in the picture — which is exactly
the trade the eye-first law exists to surface for Jimmy's judgment rather than
decide by table.

## Disclosures

- No pre-reset art, no prior plates, no approved stills were used as inputs —
  only the fresh mechanism canvas and real-bird library frames (the studies,
  which the reset law names as the source of truth).
- The annotated atlas_01 image was NOT an input; the same bird was extracted
  clean from the source video at t = 75 s.
- Raws were 2048×1184; normalization is batch 3's crop-to-aspect (a few px) +
  uniform resize to 1024×600. No retouching, no compositing.
- All eight candidates were viewed at 1024×600 before ranking. All eight are
  filed in `candidates/`; the top 3 are copied to `ranked/plate_1..3.png`.
- The joint landmarks for the ripple-seat diagnostic are the visible mid-shin
  knuckle bends as read by visual grounding — the plates draw the joint softly,
  so the seat numbers carry read uncertainty; the qualitative fact (rings at
  the feet, legs full-length) is plain to the eye in all three.
