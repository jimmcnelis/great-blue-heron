# The Heron

**The goal:** build a great blue heron that *lives* in a small framed screen — standing knee-deep in still water, watching, coiling, striking at fish, stretching, preening, flying out and coming back — generated moment to moment by a tiny model on a cheap chip, entirely offline. Not a video loop: a creature with a measured anatomy and a behavior repertoire, in the pattern of a candle whose flame is computed by a small neural network rather than recorded.

**How we're building it:**

- **Measure the real bird first.** A reference library of heron footage (strikes, swallows, stalks, flights, landings, preening, courtship) is measured frame by frame — neck chords, joint mechanics, wingbeat frequency, timing profiles — into a written canon. Nothing is animated from vibes.
- **Model the animal as a mechanism.** The neck is a ~20-link chain, after the bird's own cervical skeleton, with per-joint limits and a strike hinge in the lower-middle neck. Poses are states of that mechanism, so impossible poses are unreachable by construction.
- **Draw it like Audubon.** The finish is John James Audubon's *Birds of America* (Plate 211) — hand-colored engraving, real field marks. Art is drawn on the mechanism's own poses and approved by a human eye before anything moves.
- **Render it on a chip.** The target is a 7″ 1024×600 screen on an ESP32-P4 board: USB-C powered, no camera, no account, no internet. Training happens on a local GPU box; the finished model is flashed to the device and runs there forever.

**Where it stands (Nov 2026):** the measurement canon is complete; the mechanism (rig v2.5) passed its geometry gate against the approved artwork; the art direction is approved and keyframes are being redrawn on the mechanism's poses; the behavior roster (20 charts, ~2,000 frames of pose tracks) is built. The endgame is a small ambient object — a heron for a shelf — possibly sold locally in Calvert County, Maryland, where the real bird fishes our pier.

**What's in this repo:** the written record and the code — the measurement studies and canon, the project laws and gate reports, the creature-engine (a pluggable engine: species / environment / style / behavior packages; the heron is species #1), the rig and measurement scripts, and the reference-film inventory. The artwork files and reference footage live outside this repo; the inventory (`heron/reference-footage/INVENTORY.md`) lists every source with its origin.

*The heron on our pier is named Harry. The animated one doesn't have a name yet.*
