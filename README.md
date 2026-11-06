# The Heron

**The goal:** build a great blue heron that *lives* in a small framed screen — standing knee-deep in still water, watching, coiling, striking at fish, stretching, preening, flying out and coming back — generated moment to moment by a tiny model on a cheap chip, entirely offline. Not a video loop: a creature with a measured anatomy and a behavior repertoire, in the pattern of a candle whose flame is computed by a small neural network rather than recorded.

**How we're building it:**

- **Measure the real bird first.** A reference library of heron footage (strikes, swallows, stalks, flights, landings, preening, courtship) is measured frame by frame — neck chords, joint mechanics, wingbeat frequency, timing profiles — into a written canon. Nothing is animated from vibes.
- **Model the animal as a mechanism.** The neck is a ~20-link chain, after the bird's own cervical skeleton, with per-joint limits and a strike hinge in the lower-middle neck. Poses are states of that mechanism, so impossible poses are unreachable by construction.
- **Draw it like Audubon.** The finish is John James Audubon's *Birds of America* (Plate 211) — hand-colored engraving, real field marks. Art is drawn on the mechanism's own poses and approved by a human eye before anything moves.
- **Render it on a chip.** The target is a 7″ 1024×600 screen on an ESP32-P4 board: USB-C powered, no camera, no account, no internet. Training happens on a local GPU box; the finished model is flashed to the device and runs there forever.

**Where it stands (Nov 2026):** the heron is alive on the device. All seven behaviors — strike, idle, stretch, preen, flight, listening, and the stride that carries it across the screen — are drawn frame by frame in graphite pencil over the marsh plate and composited on the chip at 12 fps, entirely from native flash. It walks to the far side, turns through drawn views, and everything afterward plays mirrored until it strides back. The stride was rebuilt on 2026-11-06 to the measured step cycle (planted feet stay pinned, the head stays world-locked while the body passes) after the first version read as dragging its feet. The measurement canon and the rig remain the foundation every drawing answers to.

**What's in this repo:** the written record and the code — the measurement studies and canon, the project laws and gate reports, the creature-engine (a pluggable engine: species / environment / style / behavior packages; the heron is species #1), the rig and measurement scripts, and the reference-film inventory. The artwork files and reference footage live outside this repo; the inventory (`heron/reference-footage/INVENTORY.md`) lists every source with its origin.

*The heron on our pier is named Harry. The animated one doesn't have a name yet.*
