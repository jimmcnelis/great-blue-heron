# ALERT PLATE — DRAW REPORT (post-reset, fresh art)

**Date:** 2026-11-04 · **Governing brief:** `~/workspace/heron/RESET-2026-11-04.md` + `~/workspace/heron/CREW_MEMORY.md`; design: `art2/art-design/ART_DESIGN.md` + `LEG_CANON.md` (approved by Jimmy 2026-11-04 11:52).
**Scope of this run:** Step 1 (apply the leg correction to the species package) + Step 2 (draw the ALERT plate only). No coil, no peak, no animation — nothing else was drawn.

---

## VERDICT — READ FIRST

**Step 1 (leg fix): DONE and verified.** The corrected legs are in the species package; the neck geometry gates are untouched (integrals identical before/after); the corrected legs sit inside their bands on all three pose masks.

**Step 2 (alert plate): NO candidate passes the selection gate (a)+(b) as specified. The cap of 6 candidates is spent.** Per the brief's stop rule, no band was lowered. The best candidate — **candidate 3, delivered as `alert_plate.png`** — is presented for Jimmy's gate WITH its gaps named:

- **(a) Neck chord: PASSES, at the very edge of the band** — chord_base **0.400** vs band 0.40–0.47 (grounding noise on this method is ±0.03–0.04, so this is a coin-flip pass, not a comfortable one).
- **(b) Legs: FAILS as specified, on three counts** — (i) **waterline:** the plate draws ripple rings at TWO levels: one correctly AT the intertarsal joint, and a second, spurious one at the feet, with the lower legs drawn between them; the design draws NO lower leg below the joint ring. (ii) **feet-centre under the study convention** (projection onto the tail→chest axis, the LEG_CANON §2 measurement method): **0.333** vs band 0.50–0.55 — FAIL. Under the mechanism's own trace convention (x-extent fractions, LEG_CANON §2.3, the convention the corrected masks are built and read by): **0.507** — PASS. The two conventions diverge because this plate's body pitches ~19° while the study frames LEG_CANON measured were near-horizontal; the report surfaces the ambiguity rather than resolving it silently (see §4). (iii) **far-leg emergence 0.495** (projection) vs the 0.53 floor — marginal miss; its offset behind the near leg (0.042) is inside the real-bird pattern family.
- **(c) Eye anchor: FAILS** — the drawn eye sits ~95 px (plate scale) from the mechanism anchor. This is a generator-wide trait, not a c3 accident: all six candidates draw an elongated face with the eye far forward (misses: 69–95 px; best was c6 at ~24 px). The bill itself is right (0.245 of torso vs canon ~0.23); the skull is stretched.
- **(d) Identity / field marks: PASS, strongly.** Unmistakable GBH; every field mark present and correctly placed (see §5).

**What Jimmy is being asked to rule on:** whether candidate 3's stance-and-chord pass (under the mechanism convention) is close enough to proceed from, knowing the waterline carries a drawn lower leg and the head is long-faced — or whether the plate goes back. Nothing downstream (coil, peak, ink-band lock) should proceed until he rules.

---

## 1. STEP 1 — THE LEG FIX, AS APPLIED

**Package edited:** `~/workspace/creature-engine/packages/great-blue-heron/`
- `animal_v25.json` — gained a full `"legs"` section: status line ("CORRECTED 2026-11-04… traces computed from LEG_CANON bands — not traced from any image"), the convention, the segment bands, and per-pose fractions. The `"definition"` string is unchanged.
- `rig_v25.py` — new `LEGS_BY_POSE`, **computed** from the LEG_CANON bands (never traced): one waterline y=382 crossing both legs exactly at the intertarsal joints, one ground line y=486, both segments 104.2 px = 0.210 torso, feather-skirt exits 0–16.2 px, hips buried 42 px. The rig is now self-contained (loads its own package, writes to `$HERON_V25_OUT`); the old banned-still overlay block was removed and the removal is commented in the file. Pre-change snapshots kept in `plates-fresh/work/before/`.

**What the old traces had wrong (quantified):** one pose-invariant leg pair, traced off a pre-reset still: feet-centre **0.284** vs the real birds' **0.50–0.55** (a quarter-body too far toward the tail); emergence **0.217/0.359** (window reads) vs real **0.53–0.61**; segment totals near-right (the error was placement and invariance, not length). The identical leg read on all three pose masks is the invariance made visible — at peak the real bird's feet stay planted while the body pitches over them; the old traces never moved at all.

**Corrected traces (hip, joint, foot) px, and mask reads AFTER:**

| pose | near leg | far leg | feet-centre | stagger | emergence (near/far) |
|---|---|---|---|---|---|
| alert | (409,236)(406,382)(399,486) | (389,239)(358,382)(351,486) | **0.520** ✓ | 0.100 | 0.585/0.498 read (construction 0.590/0.531) |
| coil | (412,236)(416,382)(423,486) | (366,236)(362,382)(355,486) | **0.549** ✓ | 0.141 | 0.604/0.494 |
| peak | (418,236)(418,382)(411,486) | (378,243)(332,382)(325,486) | **0.506** ✓ | 0.179 | 0.610/0.451 read (far construction exit 0.500 — the far peak leg slants hard back, so its row-band read lands behind the exit) |

All placement inside the LEG_CANON bands (feet-centre 0.50–0.55; emergence 0.53–0.61 at construction). Eyeball check of the after-mask: legs under the body's middle, staggered, stilt-thin, both joints on one level — the waterline.

**Neck gates untouched — proof:** pose-solve design integrals AFTER are identical to BEFORE (alert chord_base 0.456, coil 0.269, peak 0.666 / chord76 0.516); neckbases, skulls, eye anchors identical (alert eye anchor (754.7, 35.7)); no neck joint over its cap. The leg edit moved nothing above the belly line.

---

## 2. STEP 2 — HOW THE PLATE WAS DRAWN

Six candidates, text/design conditioning ONLY — written Audubon-manner style rules and the design's numbers in prose; **no image of any kind was attached to any generation, pre-reset or otherwise.** Prompts iterated on measured failures (neck extension %, head compactness, leg emergence window, joint-ring waterline). All six originals (1920×1280) are in `candidates/` as `alert_c1..c6.png`. Gates were measured on the 1024×600 normalization of each candidate (the deliverable size); the delivered `alert_plate.png` is candidate 3 at exactly 1024×600. Note: the resize from 1920×1280 to 1024×600 is anisotropic (+13.8% horizontal); every number below was measured on the 1024×600 file, so the numbers describe the plate as delivered.

**Measurement protocol (same for all candidates):** 4 torso landmarks grounded on the normalized PNG → plate torso T_p = max pairwise distance; fractions = projection onto the tail→chest axis (and, for legs, also as x-extent fractions — both reported); skull = grounded occiput + 0.052·T_p along the bill direction; eye anchor = skull + 0.028·T_p along-bill + 0.014·T_p perpendicular (the mechanism's head-frame spec); ink by the v3 protocol (paper = corner median; content = summed RGB diff > 55; black = content with mean RGB < 70).

## 3. GATE TABLE — SELECTED PLATE (candidate 3, `alert_plate.png`)

T_p = 540.6 px. Body pitch ≈ 19°.

| gate | spec | measured | verdict |
|---|---|---|---|
| (a) chord_base | 0.40–0.47 | **0.400** | PASS — at the band's lower edge (noise ±0.03–0.04) |
| (b) feet-centre — projection convention | 0.50–0.55 | **0.333** | FAIL |
| (b) feet-centre — mechanism x-extent convention | 0.50–0.55 | **0.507** | PASS |
| (b) emergence — near leg | 0.53–0.61 | 0.537 proj / 0.577 x | PASS (low edge) |
| (b) emergence — far leg | 0.53–0.61 | 0.495 proj / 0.521 x | marginal FAIL (−0.035/−0.009); near–far offset 0.042 is in the real pattern family |
| (b) waterline at the intertarsal joint | ring at joint, nothing below | ring IS at the joint — and a second ring at the feet, lower legs drawn | FAIL (partial: the joint ring exists, unique to this candidate family) |
| (b) leg segments (context) | upper 0.21–0.25 / lower 0.17–0.22 / total 0.42–0.44 | front 0.221/0.246/0.467; rear 0.277/0.233/0.510 | long — the drawn legs run ~10–16% over the exposed-total band |
| (b) stagger | alert 0.10–0.14 | 0.154 proj / 0.168 x | slightly wide |
| (c) eye vs mechanism anchor | within ~10 px | **~95 px off** (along-bill 0.176 torso vs 0.028 spec) | FAIL — elongated drawn face (occiput→bill tip 0.544 vs assembly 0.322; bill alone 0.245 ✓) |
| (d) identity / field marks | exact GBH marks | all present (§5) | PASS |
| ink — black / frame | — (proposes the band) | **0.0408** | proposes **0.021–0.061** (±0.02) |
| ink — black / content | — (proposes the band) | **0.280** | proposes **0.260–0.300** (±0.02) |

**Ink-band proposal for Jimmy's approval:** if this plate (or its family) is accepted, lock the ink band at **black/content 0.260–0.300** (black/frame 0.021–0.061), measured off this plate ±0.02 as the design specifies. Nothing inherited from pre-reset work.

## 4. ALL SIX CANDIDATES — SUMMARY

| cand | chord (a) | feet-centre proj / x | emergence near (proj) | eye miss | ink black/frame | why not selected |
|---|---|---|---|---|---|---|
| c1 | 0.318 ✗ | 0.279 / 0.456 ✗ | 0.569 ✓ | ~69 px | 0.0392 | neck drawn as a deep coil-leaning S; legs slant back, waterline at feet |
| c2 | 0.491 ✗ (over) | 0.340 / 0.501 | 0.543 ✓ | ~53 px | 0.0497 | neck over-extended; legs short (total 0.269) and pale flamingo-grey |
| **c3** | **0.400 ✓ edge** | **0.333 / 0.507 ✓x** | **0.537 ✓** | ~95 px | 0.0408 | **SELECTED — best of six; gaps in §3** |
| c4 | 0.295 ✗ | 0.384 / 0.477 ✗ | 0.521 | ~78 px | 0.0696 | deep S neck; stance shifted back; much darker ink |
| c5 | 0.304 ✗ | 0.295 / 0.437 ✗ | 0.421 ✗ | ~79 px | 0.0652 | deep S; legs pale and short (total 0.29–0.32) |
| c6 | 0.325 ✗ | 0.376 / 0.520 ✓x | 0.551 ✓ | **~24 px (best)** | 0.0438 | head carried over the shoulders, not forward — chord fails outside noise; rear-leg segments were perfect (0.217/0.217/0.434) |

Why c3 over c6: the brief's selection order puts the chord first — c3 is the only candidate inside (a) at all; it ties c6 on the x-convention feet-centre and is the only candidate carrying a ripple ring at the joint itself. c6 wins only on the eye (still a fail) and one leg's segments.

## 5. THE PLATE IN PLAIN WORDS (viewed, not inferred)

**Stance:** the bird stands tall in the left half of the frame on flat cream paper, body pitched gently up toward the chest, tail low at the left edge. The neck leaves the chest, dips in a moderate open S, and rises to a head carried high with the bill level and pointing right. The legs drop from under the middle of the belly — rusty-brown thighs, then dark scaly shins running near-vertical to a knobby joint; at each joint a flat ripple ring encircles the leg, and — the flaw — the drawing continues below the rings with a second length of leg ending in a second pair of rings at the feet. Nothing else is in the frame: no shore, no reeds, no water surface.

**Plume:** the breast plume is the best the generator has produced in this project — a curtain of dozens of individually separated pale strands hanging from the chest seam, every strand with its own free tip, countable at a glance. It reads as feather, not as a filled mass — it passes Jimmy's frill tell. The folded wing carries the same discipline: scalloped slate coverts with white plume strands laid over them, each distinct.

**Head:** correct marks, wrong proportions — the face is elongated, the amber eye set far forward in it, the black brow band sweeping back into two thin crest strands. It reads as a heron instantly; it does not match the mechanism's compact head assembly, and the eye cannot serve as the rig's anchor as drawn.

## 6. DISCLOSURES

1. **No pre-reset image was used anywhere in this run** — no input, donor, target, or reference. Generation was conditioned on text (written style rules + design numbers) only. The leg traces in the mechanism were computed from LEG_CANON's bands, not traced.
2. **Alert-stance legs GAP (carried from the approved design, still open):** alert-specific leg placement has never been measured off real alert frames; the design applies the standing band (0.53–0.61 emergence) to alert and flags it. The mechanism's alert traces and this report's alert gate both inherit that flag.
3. **Convention ambiguity surfaced, not resolved:** LEG_CANON §2 measures leg fractions by projection (on near-horizontal study frames); §2.3 builds traces by x-extent fractions. On a plate whose body pitches ~19° the two disagree by up to 0.17 on feet-centre. Which convention governs drawn plates is Jimmy's call; the gate table reports both.
4. **Generator traits measured across all six candidates:** (i) the head is always drawn long-faced — the (c) eye-anchor gate was not reachable by any candidate (best 24 px vs the ~10 px band); (ii) the lower legs are always drawn — the "waterline at the joint, nothing below" clause was fully obeyed by zero candidates (c3 came closest, drawing the joint ring and then the lower leg anyway); (iii) neck chord is bimodal — deep-S (~0.30) or over-extended (~0.49) families, with c3 the single landing inside the band.
5. **Deliverables:** `alert_plate.png` (candidate 3, 1024×600), `candidates/` (all six originals + normalization working copies in `work/`), `sidebyside/alert_plate_vs_mechanism_mask.png` (plate beside the corrected mechanism alert mask), `crops/` (`legs_waterline.png`, `plume.png`, `head_eye.png`, all ×2 from the delivered plate). Step-1 working records in `work/` (`solve_legs.py`, `before/`, `masks-after/`).
6. **Nothing else was drawn.** Coil and peak wait for Jimmy's ruling on this plate.
