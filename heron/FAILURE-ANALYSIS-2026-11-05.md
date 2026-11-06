# Heron drawing failures — root-cause analysis (requested by Jimmy, 2026-11-05)

Jimmy: "i dont want to do this again with the heron today where you keep getting it wrong. identify the issues causing this to happen repeatedly and tell me what they are and how we correct them."

The failure trail this analysis must explain: v1.2 "blue oval" (2026-11-02) · finish-model v2 unregistered pairs (2026-11-03) · rig-vs-art 0.406 discovery (2026-11-03) · motion test v3 ink + strike failures (2026-11-04) · Stage B registration + content-budget surprises (2026-11-04) · the pencil picks (2026-11-05).

## The issues

**1. We draw from our own artifacts, never from the bird.**
Every pipeline starts from an internal representation — rig trace, pose canvas, prior art — and optimizes against it. The reference library is mined for NUMBERS (chords, rates) but never opened as the visual source for what the bird LOOKS like. Each generation of work inherits the previous generation's shape errors, which is how one traced torso loop poisoned three separate projects.
→ Correction: the reference library is the only visual source. Any drawing work begins with real-bird images as direct input, and likeness is judged against photos — never against our own earlier outputs.

**2. Metrics certify the wrong thing.**
IoU, overlap, ink density — every gate measured agreement with OUR OWN canvases. A perfect score against a wrong reference certifies the wrongness, and "geometry closed" got declared while the drawn shape was never once compared to a photograph.
→ Correction: numbers are diagnostics, never gates for art. The art gate is a side-by-side against a real heron photo, Mordecai's eye first, Jimmy's eye final.

**3. Two sources of truth, reconciled at the end.**
Rig proportions vs approved art (discovered at 0.406, after both were "done"), charts vs canon timing (v3's strike fired early and short), canvas vs finish scale (0.134). Subsystems are built to separate specs and integrated at packaging time — the same failure shape as Stage B's 59 MB meeting a 32 MB chip at the end.
→ Correction: one canonical bird definition, derived from the real bird, that rig + charts + art all consume; a reconciliation check runs BEFORE building, not after.

**4. Style is decided in words and tested last.**
The "hand" was specified verbally, then a whole pipeline was built before one finished frame was judged (v3's watercolor-vs-engraving miss; today's silhouette-fill "pencil"). 
→ Correction: style proof is ONE finished drawing, gated before any system exists around it. No pipeline before the single frame passes.

**5. The briefs encode the failure, and crews iterate inside a dead method.**
Today's crew executed Mordecai's brief faithfully — canvas-first, procedural recipes, IoU gates. The method was wrong at the brief level: no step required looking at a heron or using a tool that can draw. Worse, crews run internal fix-rounds (round 1 → round 2), so the one-method-one-shot gate never fires; polish accumulates on a failed approach.
→ Correction: visual briefs must name the visual inputs (specific reference files), a drawing route capable of the ask, and a stop rule owned by Mordecai's eye-check. A failed eye-gate ends the METHOD; internal fix-rounds are not new evidence.

**6. The tool chosen cannot do the job asked of it.**
Procedural stroke code cannot produce artist-level drawing. We kept choosing the programmable route because it is controllable and chip-friendly, and smuggled the art requirement through it. The 2026-11-02 pose-space decision already separated these problems; execution kept collapsing them.
→ Correction: art is made with the best drawing tool available, reference-conditioned. The device problem (how a small net conducts/renders finished art on a chip) is engineered AFTER art exists and passes — never as a constraint on how the art is drawn.

**7. Mordecai relays instead of stopping.**
Today I saw the flaws, named three of them in the delivery message — and delivered anyway, making Jimmy the quality filter. "Jimmy is the judge" means he judges art direction among real candidates; it does not mean unfiltered output reaches him with caveats attached.
→ Correction: the eye-gate has stop authority. If it doesn't read as the bird against the photos, it doesn't ship; the report is "the method failed," not a menu of failures.

## Standing effect
**RATIFIED BY JIMMY 2026-11-05 11:55 — "yes to all proposed changes."** All seven corrections are in force as working law: items 1, 2, 4, 5, 7 immediately for all visual work; item 3's canonical-bird rebuild and item 6's art-first route define the shape of any future heron attempt — which begins only on Jimmy's word, with one drawing. The law is recorded where the work reads it: ~/AGENTS.md (Lessons) and ~/workspace/heron/CREW_MEMORY.md (binding on every crew).
