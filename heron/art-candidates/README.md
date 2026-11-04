# Heron project — art candidates (filed 2026-11-02)

Project: a neural-net simulation in the Skunkflame pattern — a cartoon **great blue heron**
standing in shallow water, living by generation, not loops. Behaviors Jimmy specified
(2026-11-02): idle standing with gentle life; occasionally spear the water and catch a
fish — some tiny, sometimes bigger — then swallow it; occasionally stretch its wings;
occasionally fly off, later return by flying back in and land.

## The pick

**White-background #1 — Flat storybook** (`white-1-flat-storybook-PICK.webp`):
bold flat shapes, slate blue-grey, yellow spear beak. Chosen by Jimmy 2026-11-02.
Rationale: bold regions a tiny model can hold; poses read at a glance at small size.

## Filed for later (all kept — Jimmy: "these are all great")

White-background character options (2026-11-02):
- `white-2-bigeye-cute.webp` — fluffy juvenile, huge expressive eye; most expressive face.
- `white-3-ink-watercolor.webp` — ink outlines + watercolor wash, rust shoulder patch;
  prettiest, but fine detail would melt at tiny-grid scale.
- `white-4-retro-angular.webp` — 1950s UPA geometry, teal; supremely readable at small size.

Scene-style explorations (first round, heron in creek water):
- `scene-1-flat.webp` — flat vector storybook with scenery.
- `scene-2-watercolor.webp` — soft watercolor with scenery.
- `scene-3-screenprint.webp` — retro screenprint poster with scenery.
- `scene-4-pixel.webp` — chunky low-res pixel treatment with scenery.

Original generator filenames are preserved alongside the friendly copies.

## Round 2 — true proportions (2026-11-02)

Jimmy's correction: legs longer, beak longer. Dug against real birds first
(reference photos in ~/workspace/heron/reference/): the real heron stands 45–54 in,
legs ≈ 40% of its height ("comically long" — Jimmy), bill 12.3–15.2 cm ≈ the length
of its shin (tarsus 15.7–21 cm); white face, black brow + head plume, rusty thighs,
black shoulder patch. Four flat options on true proportions: A tall stand, B hunting
coil, C one-leg rest, D alert upright (media-generation-heron-flat2-*).
Jimmy's pick: **A's proportions, D's finish.**
- `heron-blend-AD-SAVED.webp` — the A×D blend. Richer finish than ordered (drifted
  toward illustration). **Saved for later at Jimmy's word, NOT the working character.**
- `heron-storybook-FINAL-DIRECTION.webp` — the blend flattened back to bold flat
  storybook (flat4): big clean shapes, zigzag chest fringe as one shape, black
  shoulder patch, stilt legs, mid-step. **The working character design.**

## Environment law (Jimmy, 2026-11-02 — locked)

- SPARSE. The water is IMPLIED, never drawn: a blank white canvas until disturbed.
- Color belongs to living things only: the bird (always full color) and the fish.
  (A cattail or two was in the first sketch of this law — full color, swaying
  slightly — but Jimmy removed it 2026-11-02: "remove the cat tail for now."
  Parked, not deleted; it may return.)
- Water speaks ONLY when touched, and only in FLAT BLACK INK: ripple rings where
  legs step, the strike splash when the beak spears, drops falling from the wet
  fish in its mouth, (by the same law) takeoff/landing disturbances.
- Stillness is the default state of the world; every mark on the water is CAUSED.
- DEPTH (Jimmy, 2026-11-02): the water is KNEE-DEEP on the heron — the surface
  sits just below the backward-bending knee joint. Lower legs and feet live under
  the blank; a leg visually ends where it pierces the surface, and ripples ring
  THAT point. A stepping leg emerges whole, drips ink, and re-enters elsewhere.
  The cattail is deeper too — it grows up out of the same water, base hidden at
  the same invisible plane. There is no shore anywhere in the frame.
- Proof still: `env-concept-1.webp` (rich saved bird standing in the void, one
  cattail, ink ripples at the standing foot — the flattened bird drops into the
  same emptiness).

## Blocking / stage law (Jimmy, 2026-11-02 — locked)

- The frame is three zones. The bird LIVES in the 1st third or the 3rd third —
  its standing/idling spots are off-center, left or right.
- FISHING TAKES PLACE IN THE MIDDLE. The center third is the fishing ground;
  the strike (and the catch, swallow) plays center-stage.
- Travel connects the zones: the bird may WALK from one side to the other
  (through the middle), or FLY OUT and later fly back in.
- Reading of the grammar: a walk side-to-side is a little journey that passes
  the fishing ground (walk → fish mid-frame → settle is a natural episode);
  flight exits/entries are full-frame crossings.

Status: **v1 BUILD GREENLIT by Jimmy 2026-11-02 ("v1 is a go")** — rig + behavior
corpus + tiny net + simulation preview, building on the Spark (~/heron/).
Architecture ruling from the law: the net generates the bird (+fish) on a
palette-indexed grid; the ink water layer is PROCEDURAL, drawn by the simulation
from its own caused events — never learned.

## Display-treatment studies — FILED FOR LATER (Jimmy, 2026-11-02)
Explorations only; the v1 build stays storybook on the BOX-3. Jimmy on the LED
one: "that led panel drawing is cool. keep for possible stuff in the future."
- media-generation-heron-dots-color-on-black-*.webp — LED dot-matrix treatment
  (color dots on black; the HUB75 face). Hardware notes in ../device-800x480-spec.md.
- media-generation-heron-dots-black-on-white-*.webp — halftone ink dots on white.
- media-generation-heron-oled-whiteonblack-*.webp / -oled-blackonwhite-*.webp —
  monochrome OLED treatments (SSD1322 strip family).
