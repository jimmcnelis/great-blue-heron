# Model sheet — Thomas Point Shoal Lighthouse (object)

The canonical form. A proportion or silhouette change is a model-sheet
change: edit here first, then the rig, then re-check the canonical renders
(day / night) in the object plug test.

## The real thing (facts the drawing must keep)

- Thomas Point Shoal Lighthouse, Chesapeake Bay off Annapolis, MD —
  built 1875, the last screwpile lighthouse still on its original site
  in the Bay, and the Bay's most recognized landmark.
- Form: a **hexagonal white wooden cottage** (the keeper's house) standing
  on **iron screwpiles** in open water — no land, no shore. A **red roof**;
  centred on the roof, a short **black lantern room** with a gallery
  (railed deck) around it.
- The light is a fixed white light in life. The rig's sweeping beam wedge
  is a *cartoon convention for night scenes*, declared in state
  (`beam_angle`) — it is not a claim about the real light, and it never
  appears unless a scene sets `lamp: 1`.

## Cartoon scale (a deliberate lie, recorded)

- Real proportions: the structure is ~43 ft above the water; a great blue
  heron stands ~4 ft. True scale would put the heron out of frame.
- Authored scale: **~54 design units above the waterline** — roughly one
  heron tall — so the landmark can share a frame as a backdrop presence.
  Scenes shrink it (`scale` placement) to push it into the distance.
  Nobody may "fix" this to true scale without a scene-level decision.

## Canonical marks (may never change shape)

1. White hexagonal cottage, red roof, black lantern — in that stack.
2. Screwpiles visible above the waterline, rusty iron, cross-braced.
3. Gallery rail around the lantern (it is the perch anchor — ospreys sit
   on the real one).
4. Two shuttered windows + centre door on the front face.

## Palette discipline

Object colors are the object's own (see object.schema.json): a landmark
is a thing in the world, drawn in full color. The environment's ink law
(marks only when caused) does not apply to it — but the *beam and glow*
are light, and light is only drawn when the lamp is lit.
