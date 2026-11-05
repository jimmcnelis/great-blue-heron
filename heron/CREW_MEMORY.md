# CREW MEMORY — the heron project (post-reset, 2026-11-04)

*The standing memory for any crew working on the heron. This file + `RESET-2026-11-04.md` are given to every crew before work. If anything you remember or find elsewhere conflicts with these two files, these files win — the older record is history, not instruction.*

## The mission

A generative great blue heron that lives in a small framed screen — standing knee-deep in still water, watching, coiling, striking, preening, flying out and back — generated moment to moment by a tiny model on a cheap chip, entirely offline. Not a video loop: a measured animal with a behavior repertoire. Target device: 7″ 1024×600, Waveshare ESP32-P4 board, USB-C powered, **no camera ever** (a scoped mic exception exists for this kit only). Endgame: an ambient object for a shelf, possibly sold locally in Calvert County, MD. The real heron on Jimmy's pier is named Harry; the animated one has no name yet (Jimmy's to give).

## The reset law (Jimmy, 2026-11-04 11:31–11:34)

- Truth = **the studies + the mechanism**. Nothing else.
- **No pre-reset image is an input to anything** — no donors, no targets, no image-conditioning, no inherited bands. All earlier art (approved stills, keyframes, warps, corpus art) is archived history.
- What carries forward: **learnings and methods only**. The Audubon manner survives as the written style rules below — never as pictures.
- Order: **design → Jimmy gates → draw → Jimmy gates → animate**. Never invert it.

## The canon (measured from real birds; source: art2/real-bird-measure/)

All lengths × torso length unless noted.

- **Neck**: it UNFOLDS rather than lengthens — but the skin CAN stretch; it is not a rigid tube (Jimmy, 2026-11-04). Arc ≈0.72 is a STANDING-posture budget (coil and alert alike); at strike peak the pooled arc runs 0.70–0.87 (ramrod lunge 0.874) — extension buys some real length. Model: unfold first, stretch as the allowance at the extremes, local distension when swallowing. Coil chord_base ≈0.27 (deep 0.268–0.271; alert 0.355 drawn / 0.432–0.458 mechanism). Peak: standing spears chord_base 0.62–0.71, chord76 0.49–0.60; lunges chord76 0.60–0.66, chord_base 0.77–0.87 (57Y plunge 0.662/0.870, reach factor 2.40). Reach factor (peak ÷ coil chord) canon 2.3–2.7; mechanism measures 2.53.
- **Slimming**: neck width at extension ≈0.55–0.65 of coiled width (stretch + slim are coupled). Width profile from the mechanism: base 0.117 torso.
- **Bill** ≈0.23 torso (median). At peak the head is a continuation of the spear: eye→billbase axis within ~2° of the neck axis in real frames; the bill never flattens away from the spear line.
- **Strike timing**: extension 0.10–0.25 s; a separate slow glean-stab class ≈1.6 s exists — never blend the classes. Release profile (dip → [~3/~12/~60/~25] across the unfold quarters, n=2, wide bars).
- **Legs**: the waterline sits AT THE ANKLE — legs end at the intertarsal joint, ripple rings centred exactly on it (Jimmy's ruling, 2026-11-04 14:20: "do it at the ankle"). Vocabulary, per Jimmy's question the same day: the visible mid-leg joint IS the ankle (intertarsal); the true knee is hidden inside the body; the scaly segment below the ankle is the bird's foot. "Knee-deep" survives as the scene's name (the whole scene is knee depth; it gives room to strike in the water — the spear works below the line, where the fish are), but the SEAT is measured at the ankle: ring centre offset 0 px from the rusty→dark transition. (Depth history: v1 correction sat +7 and read "a little too deep"; +19 read deeper; a 5-step ladder D1–D5 was built and Jimmy settled it anatomically — at the ankle.) (History: the approved alert plate 1 was drawn with full legs/rings at feet; Jimmy ruled full-legs at 13:49 on 2026-11-04 and REVERSED to knee-deep one minute later — the latest word governs, and plate 1's legs are owed a correction to match.) Leg segment ratios + stance placement per LEG_CANON / the corrected mechanism.
- **Swallow distension**: neck swells 1.20–1.25× lengthwise, up to ~1.8× crosswise (grey-heron sourced; no clean GBH ratio yet — treat as provisional).
- **Gait**: stalk 0.15–0.30 steps/s with 3–6 s freezes, head STABILIZED (no bob); strut ~1.6 steps/s WITH head bob. Night-stalk still-fraction 0.73.
- **Flight**: wingbeat cruise 2.7 ± 0.2 Hz, takeoff 2.85 ± 0.2 Hz. Slow-motion renders from the Boga source run ≈6× slow (divide by 6.0; the 5.0 hypothesis was tested and rejected). Takeoff: neck EXTENDED at liftoff, fold complete by +0.4–0.5 s. Landing has 6 phases; the balance phase is LONG (seconds), asymmetric, stepped, surface-dependent.
- **Stretch ≠ courtship**: the wing stretch is a bilateral wing spread (~0.5 s hold, a flash) with NO neck component. The courtship display is a separate NECK behavior: bill-snap → rise → bill-skyward stretch → sway, in nuptial plumage.
- **Species discipline**: 2 of the 8 original library videos are GREY heron — excluded from GBH pooling. One Jimmy-sent flight clip was a wood stork — excluded. Cousin data is labeled cousin data, never pooled silently.
- **Behavior roster**: 20 charts / 2,004 frames of pose tracks exist (creature-engine species package). Strike success rate in the roster draw: 0.368 (canon target 0.56 — accepted as an honest low draw, not re-seeded).

## The mechanism (rig v2.5 — geometry gate PASSED 2026-11-04)

- One animal definition in the species package; **20-link neck chain** modeled on the bird's ~20 cervical vertebrae; per-joint caps in two bend zones (throat 26° / mid 20° / hinge 30° / distal 22°, frozen); the strike hinge sits in the lower-middle neck, per the skeleton mounts; mid-neck segments elongated.
- Arc budget 0.72 torso conserved by construction in standing postures — impossible poses are unreachable.
- Head + bill are ONE distal assembly; the **eye anchor lives in the head frame** and is known exactly for every pose.
- Torso trace: 57 points, column-extracted from structure with the plume envelope EXCLUDED (the plume is not body).
- Layers stay separate: body (mechanism) / controller (behavior) / rendering — one animal definition feeds all three (FARMS discipline).
- **Leg traces are the known-bad part**: stance placement is a carryover error (see Lessons). Corrected leg canon comes out of the design pass; until Jimmy gates it, treat every leg number in the package as provisional.

## The medium (design for it, don't retrofit)

- Plates are 1024×600, drawn WHOLE per pose — compositing donors across poses is a failed method here (see Lessons), whole-plate drawing deletes the entire erase/ghost problem class.
- The art must decompose into the parts the rig moves: torso / neck / head / plume / legs / tail, with overlaps designed, not discovered.
- Deterministic, offline, tiny-model future: prefer structure that a small generator can hold (named parts, exact anchors) over painterly improvisation that only exists in one frame.
- **Environment law (locked)**: water is IMPLIED, never drawn — blank canvas until touched, then only FLAT BLACK INK. Color only for living things. Stillness is the default; every mark is caused. No shore in frame.
- **Blocking (locked)**: the bird lives in the 1st or 3rd third; fishing happens in the MIDDLE third; on the first landing the heron FILLS the screen.

## Style rules (written, because images may not be fed forward)

- Audubon manner: hand-colored engraving after *Birds of America* Plate 211 — engraved line and stipple, exact field marks, rich natural color on the bird, muted paper ground.
- **The plume law**: the shaggy breast plume is its OWN layer/part, drawn as FINE SEPARATED STRANDS with tips free. Jimmy's tell, verbatim in spirit: strands you can count = real; a filled shaggy mass = cartoon, and it fails regardless of numbers.
- **The neck law**: the neck keeps its full long length as the canon measures it — never compressed, tucked, or foreshortened for composition. It reads long because it IS long.
- Ink family: defined from the work's own plates as they are drawn under this design (the pre-reset strike band is retired — it came from a demoted source).
- Animation philosophy (Jimmy, binding): "mostly static is fine — good but repetitive beats janky but random." One polished signature cycle per behavior. Turns drawn progressively, never a card flip. Line boil OFF unless Jimmy asks.

## Methods that work (keep) / failure lessons (don't repeat)

**Works:**
- The mechanism itself — pose truth from measured joints, verified against canon bands.
- Centreline correspondence as a TEXTURE TRANSPORT (warping along a drawn centreline held corridor 1.00, eyes exact) — as a method note only; the fresh-art plan draws whole plates, so transport matters for the animation stage, not for rescuing old art.
- Gates measured OFF THE FINISHED ARTIFACT (grounded landmarks on the final PNG), never off build bookkeeping alone.
- One method, one shot: a failed gate stops the work and reports; iterating is Jimmy's fresh decision.
- Jimmy's eye outranks every metric: when his read and a number disagree, the number gets investigated, not defended.

**Failed — do not repeat:**
- *Stills-as-truth*: art approved before the canon existed has a painter's geometry (strike reach 0.45 vs the bird's 0.67). Any single image promoted to truth poisons everything downstream.
- *Donor-warp fill from rig-registered donors*: the drawings sit 67–101 px off their rig poses; warps inherited the gap (fill test: neck a black cord in a pale tube, head coverage 0.31).
- *Image-model generation for extreme poses*: the deep coil fold and the true spear sit outside the model's heron prior (best coil arc:chord 1.40 vs ≥1.9 needed; peak kept collapsing to the drawing's shorter strike).
- *Tube-warping the fold*: fold inner radius ≈8.6 px < tube halfwidth ≈26 px — geometrically impossible; the fold is layered feather compression and must be DRAWN as such.
- *Global-threshold erasing on tonal wash*: leaves ghosts. (Whole-plate drawing makes erasing unnecessary.)
- *The leg carryover*: the mechanism's leg stance was drawn once, early, and inherited unverified through every study and frame — Jimmy spotted it in the red overlays and again in the peak frame (feet-centre ~26–28% along the torso in EVERY pose; the stance never changed when the bird pitched). **Verify placement of every part against the studies, especially the parts nobody is looking at.**
- *The resemblance gate (Jimmy, 2026-11-04, batch-3 c3)*: a plate can pass every landmark gate — eye 5 px, ripple seat 0.009, chord, ink, framing — and still be an abomination that "doesn't resemble a heron" (dome-balloon torso, tassel plume, bullseye eye). **Resemblance is the first gate: if the plate doesn't read as a heron at a glance, it fails before any number is read, and the crew must say so itself.** Landmark gates are necessary, never sufficient. Jimmy's eye outranks the table — a crew "pass" on a part (e.g. the plume) that Jimmy reads as wrong is a wrong pass.
- *EYE-FIRST SELECTION (Jimmy, 2026-11-04 13:04 — the standing selection law)*: "please just get the most basic part of this right" — the most basic part is that it LOOKS LIKE A HERON. Candidates are **ranked by resemblance first** (a real visual read at device scale: natural body, lush strand plume, natural head, believable stance) and the top pictures go to Jimmy as pictures. **Numbers are diagnostics — reported after the ranking to explain trade-offs, never used to discard a candidate before the eye ranking, never the selection mechanism.** A numeric filter choosing which art Jimmy sees is the exact disconnect he named: he judges pictures; the pipeline was judging measurements and showing him the winner.

## The people and the gates

- **Jimmy** approves art and design at gates; his agreements mid-build are PROCESS assents, never style approvals of things he hasn't seen. Present plates, not numbers, when it's an eye question.
- **Mordecai** (the main agent) verifies decisive claims himself before relaying them to Jimmy. Crews never talk to Jimmy.
- Reporting: verdict first, numbers off the artifact, failures named with the missing piece and the test that would settle it. "Not yet achieved — missing X — settled by Y" replaces every "can't."

## LEG STRUCTURE LAW (Jimmy, 2026-11-04 16:52-16:56 — supersedes every earlier seat/transition note)
The approved plates' legs are drawn WRONG: thigh running into one straight scaly pole, no joint. A real GBH leg (Jimmy's photo, saved reference-footage/jimmy-gbh-legs-flight-photo.jpg; countless library frames): (1) rusty feathered thigh/drumstick → (2) short PALE bare band → (3) ANKLE = a visible knuckle at ~the MIDDLE of the leg (~49%), bending like a reversed knee → (4) long scaly foot segment to the toes. The waterline goes BELOW the joint — joint fully out of the water, legs roughly 60% out. Any plate whose legs lack the drawn joint fails regardless of ring placement. The day's five failed deliveries all seated rings on jointless legs; the crews' "rusty→dark transition" landmark was the thigh boundary, never the ankle. When Jimmy says a part is wrong, STUDY THE LIBRARY FRAMES OF THAT PART before touching the plate.

## JIMMY IS THE ONLY JUDGE (2026-11-04 17:01 — supersedes all gating language)
"you're not a good judge to gate the work against. just show me each time with or without it passing your tests." Mordecai does NOT withhold visual work for failing his own eye/tests. EVERY attempt reaches Jimmy, labeled with its status; he rules. Gates still govern whether Mordecai silently iterates/spends — never whether Jimmy sees the output.

## STRIDE PLATE APPROVED (Jimmy, 2026-11-04 17:02)
The legfix attempt-1 candidate — a STRIDING heron with correct four-part legs, full-length legs to rings at the feet, small reflection marks under the rings — was shown labeled "failed" and Jimmy approved it as a plate in its own right (👍 then "yes"). It stands approved AS IS (final/stride_approved.png); do not "correct" its waterline or reflections. Lesson: Jimmy's eye over crew verdicts, again — generation freedom produced the plate he wanted.
