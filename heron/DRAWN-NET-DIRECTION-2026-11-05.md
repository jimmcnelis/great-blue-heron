# Drawn-net heron — direction note (Jimmy, 2026-11-05)

**Trigger:** Jimmy shared an Aaron Blaise pencil-test walk cycle (hand-drawn lion) and asked whether a neural net can be an animal *drawn like that* that *moves like the animal*. Answer given: yes, via (1) a net conducting a drawn rig (pose space — his 2026-11-02 decision) or (2) a pose-conditioned finish model; freehand video diffusion cannot hold a drawing or live on a chip.

**Jimmy's ruling (2026-11-05 11:26): "oh the heron will be the subject. we already have all the posture and movement studies."**

**STYLE RULING (Jimmy, 2026-11-05 11:31, supersedes the Audubon manner FOR THIS BUILD): "the audobon manner is out for this one. i want something more in the style of the lion animation video i just provided."** Target hand = animator's pencil test, Blaise-style: graphite line on paper, loose construction marks welcome, smudge shading, monochrome — no engraving ink, no color bands, no plate finish. The written Audubon style rules in CREW_MEMORY.md do NOT govern this build's finish; the motion canon, mechanism, geometry, and reset discipline DO. Gate shape revised: the crew first produces 2–3 pencil-style ANCHOR frames (alert, coil, peak strike) for Jimmy's eye-gate before any full finish round — style is proven on three drawings, not eighty. Finish gates become: geometry IoU vs canvas (unchanged) + pencil-weight/density judged against the anchors Jimmy approves (the old ink-density-vs-plate gate is retired for this build). Status: gate 1 remains HELD (Jimmy, 11:30) — this ruling amends the plan; it does not lift the hold.

**KEYFRAME VERDICT (Jimmy, 2026-11-05 12:03): poses PASS — "the poses for each is acceptable and passes." CONSISTENCY FLAGGED: "these 3 are similar drawings but not the same — color is deeper in the 2nd and the 3rd is lighter than the first."** Read plainly: (1) tonal depth/paper register drifts across the set (alert = the reference tone; coil deeper; peak lighter); (2) the three are not recognizably ONE individual bird. Both are exactly what the canonical-bird reconciliation exists to fix — it is now the live next step, offered to Jimmy 2026-11-05: one canonical bird definition (identity anchored on the approved alert drawing + the library photos), keyframes unified to it, tone matched across the set, each result verified against photo + anchor before delivery.

**STYLE PROOF — APPROVED (Jimmy, 2026-11-05 11:58): "yes this looks great. i appreciate seeing the reference photo."** The corrected method produced it: image model conditioned on a REAL library photo (the eel-swallow profile frame, gate1-strike/corrected/prof_d.png) + the lion pencil band; four candidates drawn, Mordecai verified each against the photo, ONE delivered (candidate 2) alongside the reference photo for Jimmy's own side-by-side — a delivery practice he explicitly appreciated; use it again. The approved drawing: ~/workspace/heron/gate1-strike/corrected/heron_pencil_verified_20261105-1201.png. Status: it is the STYLE ANCHOR for this build (the hand); likeness truth remains the library's photos, per the visual work law. Known nit (accepted as-is): faint warm tint on the bill. Next gated step (not started): coil + peak-strike keyframes in this hand, drawn from library strike frames and verified the same way, THEN the canonical-bird reconciliation before any animation system is built.

**PICKS ROUND 1 — REJECTED (Jimmy, 2026-11-05 11:45): "oh no, lets start over."** The six candidates were rendered PROCEDURALLY — graphite-textured fills inside the rig's silhouette. Verdict by the only judge: no. Mordecai's own eye concurs with the diagnosis: they read as stiff outlined silhouettes with texture fills (humped-loaf torso inherited from the rig trace, stick legs, programmatic scribble), where the lion reference is volumetric, organic, drawn. **That drawing method is a failed method — do not re-run it.** The rig/canon/geometry remain valid as MEASUREMENT and motion truth; the failure is in using the rig silhouette as the drawing itself. Next round's method is Jimmy's call (asked 11:45): free generative drawing in the pencil hand (poses from the charts, no silhouette underneath, likeness by his eye, geometry measured after) vs a different direction entirely.

## What the studies buy us (already in hand)
- Motion-study canon (2026-11-04): strike chords (coil 0.27 / peak 0.70 chord_base), dip-first release profile [3/10/78/9]%, extension 0.10–0.25 s, withdrawal 3–5× slower, coil hold ≥4.15 s, wingbeat canon, swallow distension 1.2–1.25×.
- Rig v2.5: geometry CLOSED against the approved art (reach factor 2.53) — the upstream canvas fault that poisoned finish-model v2 (approved bird vs old rig overlap 0.406) is fixed.
- Behavior roster: 20 charts / 2,004 frames. Reference library CLOSED by Jimmy.

## Where the frontier actually is (last attempts, measured)
- Finish model v2 (2026-11-03): consistency perfect (repeat-hold pixel diff 0.0); fidelity failed — training pairs unregistered (overlap 0.134).
- Finish model v3 (2026-11-04): geometry/registration closed (hold IoU 0.813), consistency passed; FAILED on ink density (0.126 rendered vs 0.259 approved — watercolor instead of engraving) and strike execution (fired in the first beat, ~54 px short of full reach).

## Proposed gate 1 (cheap proof, Jimmy judges by eye)
ONE sequence only — the strike (the money behavior, and the one v3 got wrong):
1. Render its pose canvases from rig v2.5 with the canon timing (dip-first, middle-loaded release, full 0.70 chord reach, ≥4.15 s coil hold).
2. Finish ~40–60 frames ON those canvases in the approved plate hand; per-frame gates: geometry overlap + ink density vs the approved plate (~0.259).
3. Train the small finish model on the gated pairs; render the sequence; Jimmy judges the clip.
Pass → scale to the roster. Fail → stop; iterating is Jimmy's fresh decision (failure-discipline rules).

**Device note:** the P4 in its case stays on Stage A (Dawn's preference) — this thread is Spark-side research until a build earns the swap.
