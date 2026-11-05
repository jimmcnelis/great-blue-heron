# WATERLINE DEPTH LADDER — ALERT plate, five seats for Jimmy's eye (2026-11-04)

**Why this exists:** the depth has been corrected twice in words and the direction
inverted once in translation. So: no more words into pixels. Five variants of the
same approved alert plate differing **only** in waterline seat — the ripple rings'
vertical position relative to the rusty→dark transition on the legs. Leg endings
and rings move together (leg cut = ring centre + 4, the shipped corrections'
geometry). **No recommendation is made and nothing is ranked — Jimmy's eye picks.**

Jimmy's framing, verbatim: *"he is standing a little too deep. he would be at
knee depth. the whole scene is knee depth."*

Files: `alert_D1.png` … `alert_D5.png` (1024×600, each labelled D1–D5 in light
grey in the bottom-left corner — these are selection proofs, not plates) and
`contact_sheet.png` (all five in a row, captioned). Build script + full
measurements: `work/ladder_build.py`, `work/ladder_measure.json`.

## Seat table — ring-centre offset from the rusty→dark transition

Transitions on this plate: left leg y=411, right leg y=415. Offsets are the ring
centres' distance from each leg's own transition (negative = above it).

| variant | offset | ring centres L / R (x, y) | leg cuts L / R | source |
|---|---|---|---|---|
| **D1** | **−8 px** (above; waterline crosses the rusty segment) | (364, 403) / (404, 407) | 407 / 411 | built from the original master |
| **D2** | **0 px** (exactly at the transition) | (363, 411) / (404, 415) | 415 / 419 | built from the original master |
| **D3** | **+7 px** below | (363, 418) / (404, 422) | 422 / 426 | = `plate_1_knee.png` (v1) as shipped |
| **D4** | **+19 px** below | (359, 430) / (404, 434) | 434 / 438 | = `plate_1_knee2.png` as shipped |
| **D5** | **+32 px** below (a clearly deeper stance) | (358, 443) / (404, 447) | 447 / 451 | built from the original master |

Ring x-centres sit on each leg's centreline at the ring's height (the left leg
slants, so its centre steps 363 → 359 → 358 as the seat deepens — the same
recentring the shipped knee2 used).

## Method (built variants)

Same pipeline as the shipped knee correction (`work-knee/knee_correct.py`), local
pixel work only: corridor + foot-ellipse erase below the new cut, the plate's own
donor paper restored (row-tinted, feathered, plume strands protected), paired-
ellipse ripple rings redrawn in the plates' own hand (78×16 outer / 46×10 inner),
leg endings sculpted round, original leg pixels restored over the rings so the
arcs pass behind the legs. One fixed seed for all three built variants, so the
rings' jitter character is identical across D1/D2/D5 — the seat is the only
difference. D3 and D4 are the shipped v1 / knee2 files themselves (plus the
corner label), per the brief.

## Verification

- **Confined diff vs the original master** (ranked/plate_1.png): **0 changed
  pixels outside the leg/ring band** (x 270–470, y ≥ 380) on every variant,
  excluding the declared label box (bottom-left, x 8–84, y 552–596; 199–223 px
  per file — the "Dn" label itself). Total changed px: D1 6,615 · D2 6,352 ·
  D3 6,201 · D4 6,212 · D5 5,522.
- **D3 / D4 fidelity:** diffed against their shipped sources, they differ by
  exactly the label pixels (223 / 216 px) and **0 px anywhere else** — the leg
  zones are the shipped work, bit for bit.
- **Seat sanity check:** the outer rings' bottom arcs, measured on the finished
  PNGs, imply centre offsets of D1 −9/−11, D2 −1/−3, D3 +6/+4, D4 +17/+16,
  D5 +30/+29 (L/R) — tracking the drawn seats with the estimator's known
  ~1–3 px bias (it reads to the antialiased lower edge of the line). The drawn
  centres in the table above are the rendered positions.
- **Eye check (mine, 3× leg-zone crops + full plates):** all five read as one
  untouched plate each — rounded leg endings entering the rings, arcs behind the
  legs, blank paper below, no ghost of the original shins or foot rings at any
  seat. The progression is monotone and visible at contact-sheet size: D1's
  legs end inside the rusty feathering; D5 carries a clear length of dark shin.
- **Sources untouched:** ranked/plate_1.png `9da53949…`,
  corrected/plate_1_knee.png `54d6bb20…`, corrected/plate_1_knee2.png
  `a3c02028…` — sha256 identical before and after this build.

## Disclosures

- D4 (knee2 as shipped) carries small horizontal tick marks flanking the shins
  at the old ring seat — they are part of the shipped knee2 file and were left
  exactly as they are; the other four variants do not have them.
- The 0 px / +7 px rungs bracket the colour transition itself; the drawn
  anatomy there is a gradient, not a line, so ±2 px around "the transition"
  is the honest precision of the reference row (transitions were located on
  the artifact in the original correction work: L y=411, R y=415).
