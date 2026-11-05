# ALERT PLATE — DRAW REPORT, BATCH 2 (post-reset, fresh art)

**Date:** 2026-11-04 · **Governing brief:** Jimmy sent batch 1 back 2026-11-04 12:17 ("fresh batch, tighter brief"). Standing memory: `~/workspace/heron/RESET-2026-11-04.md` + `~/workspace/heron/CREW_MEMORY.md`; design: `art2/art-design/ART_DESIGN.md` + `LEG_CANON.md`; batch 1's record: `art2/plates-fresh/ALERT_DRAW_REPORT.md`. The leg fix is in the mechanism (batch 1, step 1, verified). **No pre-reset image was used as an input anywhere in this run; batch 1's c3 is a failed candidate, not a donor — text/design conditioning only.** (Naming note: this batch's candidates are again numbered c1–c6; "c3" below is THIS batch's candidate 3, a different image from batch 1's c3.)

---

## VERDICT — READ FIRST

**NO candidate passes the full gate. The cap of 6 candidates is spent; no band was lowered; no seventh candidate was generated.** The best candidate — **candidate 3, delivered as `alert_plate.png`** — is presented for Jimmy's gate WITH its gaps named:

- **Chord (a): PASSES mid-band** — chord_base **0.414** vs band 0.40–0.47, aim 0.42–0.45. The only in-band chord of the batch (the rest split 0.315–0.346 deep-S and one 0.517 over-extended — the generator's bimodality from batch 1 persists).
- **Eye (hard gate): FAILS** — drawn eye **~38 px** from the mechanism anchor vs the ≤10 px gate. This is the batch's best-by-design result and it is still a fail: across all 12 candidates of batches 1–2, **no generated candidate has met the eye gate** (batch 1 best ~24 px; batch 2: 31 / 63 / 38 / 46 / 45 / 33 px). The cause is consistent and measured: the bill is drawn at canon length (c3: 0.231 vs ~0.23) but the feathered skull is drawn ~2× canon length (occiput→eye along-bill 0.094 vs spec 0.028; occiput→bill-base ≈0.19 vs ≈0.104), so the eye rides far forward of the anchor no matter how the prompt phrases the proportions. Every proportion lever in the tightened brief was pulled — head-frame numbers in prose, "mostly bill," the 1:3 eye-ratio, the narrow lore slit, the dainty-knob framing — and the skull stretch moved only from 0.121 (worst) to 0.074 (best) along-bill, never to 0.028.
- **Waterline: structure FIXED, placement still off** — the batch-1 defect (rings at two levels, lower legs drawn to the feet) is gone in c3: one pale band, one straight waterline, one ripple ellipse per leg at its entry, nothing drawn below the surface. But the waterline crosses each leg **~39 px (0.068 × torso) BELOW the intertarsal joint** — the knuckles sit dry above the surface with a length of lower shin in the water (see the crop: both joints fully above the line, shins piercing it). Canon is the line AT the joint. c5 came closer (0.054) with the same structure; no candidate put the joint in the line.
- **Plume: PASSES Jimmy's tell, outright** — a curtain of individually separated strands with free tips, layered over the scalloped wing (crop filed). The best plume of the batch, on the selected plate.
- **Identity / field marks: PASS** — unmistakable GBH, all marks present (one blemish: a pale flash at the top of each shin, where thigh meets dark scale).
- **Ink: at the family edge** — black/content **0.256** vs batch 1's proposed family 0.260–0.300 (0.004 under the floor — inside protocol noise, outside the band as written); black/frame 0.0562, inside the proposed 0.021–0.061.

**What Jimmy is being asked to rule on:** the same shape of question as batch 1, one defect fewer — batch 2 fixed the chord (mid-band) and the waterline's structure, and the plate is the right bird with the right stance and a plume that passes his tell; it still carries a long face (eye 38 px off anchor) and a waterline that meets the leg below the joint instead of at it. The missing piece is now precisely named: **text conditioning alone has not produced a canon-proportioned skull in 12 tries, nor seated the joint in the waterline.** What settles it is a decision above this run — another batch under a different conditioning strategy, acceptance of this plate with the two defects named, or a different drawing method for the head/waterline regions. Nothing downstream (coil, peak, ink-band lock) should proceed until he rules. **Nothing else was drawn in this run.**

---

## 1. HOW THE BATCH WAS RUN — the tightened points, and what each bought

Six candidates, text/design conditioning ONLY (written Audubon-manner style rules + the design's numbers in prose; no image attached to any generation). Prompts iterated on measured failures, one measured variable at a time:

1. **Waterline drawn once** (band-occlusion framing from c3 on: a flat pale opaque band whose top edge is the water; legs pass into it and are hidden). *Bought:* the two-level ring defect never recurred after c2; c3/c5/c6 all draw ONE surface with entry ripples and nothing below it. *Not bought:* the joint's seat in the line — the generator consistently draws the knuckle above the surface and a shin-length in the water (offsets 0.068 / 0.054 × torso on the two structured candidates), or ends the leg in a foot-like clump at the surface (c4), or fades the lower legs through the wash (c1).
2. **Head built to the mechanism's head frame** (bill ≈0.23 torso, skull compact, eye at the anchor's ratios, weighted first). *Bought:* the bill is at canon on the selected plate (0.231); the worst faces improved (along-bill eye offset 0.074–0.094 on the better candidates vs batch 1's 0.176 on its selected plate). *Not bought:* the gate — the skull itself is the stretched part, and prose ratios do not shrink it to canon.
3. **Chord aimed mid-band** (0.44 stated in prose from c2 on). *Bought:* c3 at 0.414 — the batch's one in-band landing, vs batch 1's single edge pass at 0.400. The generator's chord remains bimodal around the aim; the aim moved the upper family down (0.517 max vs batch 1's 0.491 over-read is the exception, c4).
4. **Conventions** — legs reported under BOTH conventions for the selected plate (§3); selection used the mechanism convention, flagged here for Jimmy's ratification, as the brief ordered.

**Measurement protocol:** identical to batch 1 (4 torso landmarks grounded on the finished PNG → T_p = max pairwise distance; fractions by projection onto the tail→chest axis and, for legs, also as x-extent fractions; skull = grounded occiput + 0.052·T_p along the bill direction; eye anchor = skull + 0.028·T_p along-bill + 0.014·T_p perpendicular; ink by the v3 protocol) — **with one hygiene change, disclosed:** batch 1 normalized its 1920×1280 originals to 1024×600 by anisotropic resize (+13.8% horizontal stretch, disclosed in its report, and baked into its numbers). Batch 2 normalizes by **crop-to-aspect + uniform resize — no stretch** — so batch-2 fractions describe undistorted drawings. Cross-batch comparisons of horizontal fractions carry that caveat; the eye misses (Euclidean, plate scale) are comparable.

## 2. GATE TABLE — SELECTED PLATE (candidate 3, `alert_plate.png`)

T_p = 576.7 px. Body pitch ≈ 15°.

| gate | spec | measured | verdict |
|---|---|---|---|
| (a) chord_base | 0.40–0.47 (aim 0.42–0.45) | **0.414** | PASS — mid-band |
| (c) eye vs mechanism anchor | ≤ ~10 px (HARD) | **~38 px** (along-bill 0.094 vs spec 0.028) | FAIL |
| head assembly (context) | occiput→tip 0.322; bill ~0.23 | 0.424 total; skull ≈0.19; **bill 0.231** | skull ~2× canon; bill at canon |
| waterline drawn once | one surface, entry rings, nothing below | one band, one ring set at the entries, band empty below | PASS (structure) |
| waterline AT the joint | line crosses leg at the intertarsal joint | line crosses **39 px (0.068·T_p) below** the joint; lower shin in the water | FAIL (placement) |
| upper segment (emergence→joint) | 0.21–0.25 | near **0.265** / far **0.245** | near +0.015 over; far in band |
| emergence — near / far (mechanism x-extent) | 0.53–0.61 | **0.530 / 0.641** | near at floor ✓; far over |
| emergence — near / far (LEG_CANON §2 projection) | 0.53–0.61 | **0.497 / 0.599** | near under; far in band |
| feet-centre | 0.50–0.55 | **0.521 BY CONSTRUCTION** (mechanism alert pose — the feet are not drawn; the joint pair's drawn centre reads 0.551 x-extent / 0.377 projection, the projection figure reflecting that a joint is not a foot: it sits up-back of where the planted foot lands along the pitched axis) | by construction, as the brief specifies |
| plume | countable strands, fixed roots, free tips | dozens of separated strands, tips free (crop) | PASS — Jimmy's tell |
| identity / field marks | exact GBH marks | all present; pale flash atop each shin noted | PASS |
| ink — black / frame | family 0.021–0.061 (batch-1 proposal) | **0.0562** | in family |
| ink — black / content | family 0.260–0.300 (batch-1 proposal) | **0.256** | 0.004 under the floor — marginal |

## 3. ALL SIX CANDIDATES — SUMMARY

| cand | chord (a) | eye miss | ink black/content | waterline / legs | why not selected |
|---|---|---|---|---|---|
| c1 | 0.324 ✗ | ~31 px ✗ | 0.308 | lower legs drawn below the joints, fading, running off the frame's bottom edge | deep-S chord; waterline failed the old way |
| c2 | 0.346 ✗ | ~63 px ✗ | 0.280 | batch-1 defect verbatim: rings at the joints AND at the feet, full legs drawn; white shin bands | chord + waterline + worst eye of the batch |
| **c3** | **0.414 ✓** | ~38 px ✗ | 0.256 | one band, entry rings, nothing below; joint 0.068·T_p above the line; upper segs 0.265/0.245 | **SELECTED — best of six; gaps in §2** |
| c4 | 0.517 ✗ (over) | ~46 px ✗ | 0.283 | legs end AT the surface but in foot-like clumps — reads as feet standing on the water; joint not seated/ringed | over-extended chord; feet at the surface |
| c5 | 0.315 ✗ | ~45 px ✗ | 0.209 | one band; joint 0.054·T_p above the line (closest seat); faint leg ghosts inside the wash | deep-S chord; emergence near 0.465/0.434 ✗ |
| c6 | 0.331 ✗ | ~33 px ✗ | 0.157 | **ONE leg only**, ending in a foot clump in its ripple | one leg — anatomy fail regardless of other numbers |

Why c3: it is the only candidate inside the chord band at all, its waterline is the correct structure (shared only with c5, whose chord and emergence fail), its plume is the batch's best, and its eye miss (38 px) is mid-family rather than worst. Under the brief's weighting (eye first among equals) no candidate qualifies — c1 and c6 beat c3 on the eye (31 / 33 px) while failing chord, waterline, and (c6) basic anatomy; the eye gate is a pass/fail at ≤10 px and all six fail it, so selection fell to the remaining gates, where c3 stands alone.

## 4. THE PLATE IN PLAIN WORDS (viewed, not inferred)

**The bird:** tall and statuesque in the left two-thirds of the frame on flat cream paper, body pitched gently up toward the chest. The neck rises in a long diagonal sweep — nearly straight below, bowing softly back near the top — to a head carried high and forward, bill level, pointing right. It reads as the alert watch the sheet specifies.

**The waterline:** the bottom of the plate is a flat pale blue-grey band with a ruler-straight top edge, empty and clean. The legs pierce that edge inside neat concentric ripple ellipses — and that is the honest success: there is one surface, drawn once, and nothing exists below it. The failure is equally visible once you look at the crop: both knuckle joints stand dry ABOVE the surface, and a finger's width of dark scaly lower shin runs from each knuckle down into the water. The bird reads as standing shin-deep, not knee-deep with the water at the joint.

**The face:** correct marks on a long face. The bill is the right dagger at the right length; behind it the skull stretches — the amber eye, large and round, sits visibly far forward of where the mechanism's head frame puts it, roughly a third of the way along a head that should carry it at a quarter. At a glance it is a heron; measured against the mechanism, the head is a caricature by ~2× on the skull alone.

**The plume:** the plate's glory — a layered curtain of fine separated strands over the scalloped slate wing, every strand with its own free tip, countable at a glance. It passes Jimmy's frill tell without argument.

## 5. DISCLOSURES

1. **No pre-reset image was used anywhere in this run** — no input, donor, target, or reference; generation was conditioned on text (written style rules + design numbers) only. Batch 1's plates were read only as a failure record (its report), never fed to a generation.
2. **The eye-anchor protocol measures the drawn skull's stretch, by design:** the anchor is derived from the grounded occiput at the mechanism's canon skull proportions (skull centre at +0.052·T_p, eye at +0.028 along-bill). A canon-proportioned drawing lands its eye on the anchor; this generator's drawings systematically place the skull at ~0.19–0.22 × torso (canon 0.104) while holding the bill at canon — the miss is a skull measurement, not an artifact of the protocol. Grounding noise on the method is ±0.03–0.04 in fraction terms; the misses (31–63 px) exceed it severalfold.
3. **Alert-stance legs GAP (carried from the design, still open):** alert-specific leg placement has never been measured off real alert frames; the standing band governs, flagged in the design and inherited here.
4. **Convention choice flagged for ratification (per the brief):** selection used the mechanism (x-extent) convention, consistent with the verified mechanism masks. On this plate the two conventions split the emergence verdicts (near: 0.530 x-extent vs 0.497 projection; far: 0.641 vs 0.599) because the drawn body pitches ~15°. Which convention governs drawn plates remains Jimmy's call; both are tabled in §2.
5. **Feet-centre is stated by construction, not grounded** — the feet are underwater and undrawn, exactly as the tightened brief specifies; the figure 0.521 is the corrected mechanism's alert pose, the pose this plate was conditioned on. The drawn joints' centre is reported alongside it for transparency, with its caveat.
6. **Generator traits measured across this batch (for the record):** (i) skull ~2× canon on all six, bill at canon on the better ones — the eye gate was unreachable by prose proportioning in 6 tries here and 6 in batch 1; (ii) the waterline's STRUCTURE is now reliable under the band-occlusion framing (3 of the last 4 candidates), but the joint seats above the line by 0.05–0.07 × torso whenever the joint is drawn at all; (iii) chord stays bimodal (deep-S ~0.32–0.35 / over ~0.52) with in-band landings occasional (1 of 6 here, 1 of 6 in batch 1); (iv) new in c6: a one-legged draw — anatomy variance is not exhausted by the known traits.
7. **Deliverables:** `alert_plate.png` (candidate 3, 1024×600, delivered as best-of-batch WITH the gaps above — it does not pass the gate), `candidates/` (all six at 1024×600), `work/` (generation originals 1920×1280 + normalization script), `sidebyside/alert_plate_vs_mechanism_mask.png` (plate beside the corrected mechanism alert mask), `crops/` (`waterline_joint.png`, `head_eye.png`, `plume.png`, all ×2 from the delivered plate).
8. **Nothing else was drawn.** Coil and peak wait for Jimmy's ruling on this plate.
