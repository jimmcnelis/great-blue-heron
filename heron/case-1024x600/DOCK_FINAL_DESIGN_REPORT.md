# Dock final design pass — pegs out, tongue-and-groove in, exit raised (2026-11-03)

One pass, three of Jimmy's rulings from the printed pair, all final.
Supersedes the peg/hole sections of DOCK_SPLIT_REPORT.md. The seam
stays at **z = 12**; the snap fingers, cable channel's job, bezel,
back cover, and every earlier fix are unchanged.

## Ruling 1 — locating pegs + holes DELETED

The 4 pins (Ø3.2, lower seam ring) and 4 holes (Ø3.6, upper seam
face) are gone from `src/heron_case.scad`; both seam faces are
clean. One line of cause, for the record: the holes sat in the
4 mm front/back wall tops with **0.2 mm of stock per side** — under
half of one 0.42 mm perimeter at Jimmy's settings (2 wall loops,
0.42/0.45 line widths, 15% grid infill, 1 mm top skin) — so no
loop could form around them and the slicer swallowed them; the
pins printed fine (both facts photo-proven on the printed pair).

## Ruling 2 — join = end tabs + tongue-and-groove

The 4 cantilever snap fingers and their grooves are **exactly as
designed** (Jimmy verified they hold the assembled dock). No new
tabs. Added around the seam ring:

- **Tongue (lower):** continuous tapered rib centred on the wall
  centrelines (back y=2, front y=74, sides x=±96) — 2.0 mm wide at
  the base tapering to 1.2 mm at the tip (the taper is the lead-in
  chamfer), **1.7 mm tall**. Runs the full perimeter, corners
  overlapped — with ONE interruption: across the cable exit on the
  back wall (|x| < 26), where there is no wall top to carry it.
- **Groove (upper):** matching straight channel, **2.6 mm wide**
  (0.30 mm clearance per side), floor 1.9 mm above the seam
  (0.2 mm clear of the tongue tip), same ring, same interruption.
  Stock beside the channel: **0.7 mm per side** in the 4 mm walls,
  and in the upper the front/back walls widen to 10 mm above the
  seam, so the channel is backed by solid wall, not infill.

**Why this channel survives slicing where the Ø3.6 blind holes
didn't** (Jimmy's project settings, pulled from the .3mf:
wall_loops 2, outer/inner line width 0.42/0.45, sparse infill 15%
grid, top shell 5 layers = 1 mm, layer height 0.2):

1. **Width vs perimeters.** The hole left 0.2 mm per side — no
   perimeter fits, so its contour merged into the wall face. The
   channel leaves 0.7 mm per side: a full perimeter on each lip,
   plus the wall's second loop behind it.
2. **Open channel vs closed pocket.** The hole was a closed
   recess whose floor printed as a skin over sparse infill — the
   skin simply closed it. The groove is open along its whole run;
   there is no pocket to bridge shut, and its floor is an ordinary
   recessed surface printed as inner layers.
3. **Orientation.** The upper prints top-face down (seam face up),
   so the channel is formed by the final layers' long continuous
   perimeter loops — the most reliable geometry a slicer makes.
   The tongue is pure addition on the lower's up-facing seam.

## Ruling 3 — cable exit RAISED

As designed, the exit slot spanned **z 2.5..10.5** in the back
wall — sill flush with the cavity floor, **2.5 mm above the desk
plane** — so the cord exited straight into the 2.5 mm gap between
sill and desk and was pinched there (Jimmy: *"how is a cord
supposed to come out of that slot if it sits at the bottom of the
stand?"*).

The fix, in the shared `dock_geometry()`:

- **Exit slot now spans z 9..17** (48 mm wide, as before) — sill
  **9.0 mm above the desk plane (z=0)**, top at 17.0. The cord
  leaves horizontally and droops to the desk in free air; the only
  contact is the sill's top corner as a gentle fulcrum, with air
  below the cord until it touches down behind the dock. Nothing
  sits on it.
- **Interior ramp:** a wedge in the rear of the cavity walks the
  channel floor (z 2.5) up to the sill over y 30 → 4 (a ~14°
  slope, 60 mm wide), so the cord's path — chin raceway → frame
  notch → cavity floor → ramp → out the back — has no step and
  no knife-edge turn. The ramp lives entirely in the lower half
  (top at z 9 < seam 12), clear of the frame shelf (front) and
  the snap fingers (sides).
- The slot now crosses the seam: the lower prints its z 9..12
  share as a wall notch, the upper its z 12..17 share — both
  support-free in the established orientations. The tongue and
  groove interrupt across the slot (|x| < 26, 2 mm lands at the
  jambs); the cable path is never narrowed by the seam hardware.

Deliberate side effect, stated plainly: the legacy one-piece
`dock` in the SCAD shares `dock_geometry()`, so it inherits the
raised exit + ramp (516 → 544 facets) and `stl-fixed/dock.stl`
was re-exported to match. It is not part of the print project.

## Verification — measured on the tessellated meshes

**Pegs/holes absent.** Lower's max z: 15.400 (pin tips) → 13.700
(tongue tip). Upper probed at all four former hole axes
(±60, y 2/74) at z 14.5 and 15.5: solid at all 8 points.

**End tabs unchanged.** Snap-finger facet sets are identical
between the shipped and final upper meshes (96/96 facets,
vertex-for-vertex). Lower body facets below the seam (z ≤ 11.79)
identical 478/478; upper unchanged bands identical 104/104. The
only re-triangulation anywhere is 2 coplanar floor triangles
re-split where the ramp's toe lands (same z=2.5 surface).

**Tongue + groove dimensions** (sampled on the final meshes,
front wall): tongue base width **2.0**, tip width **1.2**, height
**1.7** (tip at z 13.700); groove width **2.6**, floor at
**z 13.9 → depth 1.9**; clearances 0.30/side and 0.2 at the tip,
as designed. Ring continuity: tongue present at 58/58 sampled
stations (the designed exit gap excluded); back-wall segments
present and matched on both halves.

**Cable path sweep.** A Ø4.0 mm tube swept along the dock-side
path (cavity behind the frame shelf → floor → ramp → exit →
outside), 33 stations, surface-sampled: penetration < 0.05 mm
everywhere — a Ø3.9 tube clears all 33 stations with zero
interference, so the Ø4.0 contacts are exactly the designed
resting contacts (floor, ramp, sill). **Narrowest point: the
exit slot itself, 48 wide × 8.0 tall (z 9..17)** — a Ø4 cable
keeps ≥2 mm clearance on every side except its resting line on
the sill. **Exit sill height above the desk plane: 9.0 mm**
(top 17.0). Straight rays at cable height (z=11) from inside the
cavity out the back cross **0** mesh facets at x = −20/0/+20 —
the path is open; the old floor-level rays (z=6.5) now hit the
ramp and wall (2 crossings), i.e. the bottom slot is closed by
design.

**Meshes.** Lower: 688 facets, 64.756 cm³, watertight (0
non-manifold edges). Upper: 392 facets, 87.265 cm³, watertight.
Assembled pair 152.02 cm³. Print orientations unchanged: lower
bottom-down, upper top-face down (seam up).

**Archives.** `dock-split.3mf` rebuilt with the same packaging
(non-mesh entries byte-identical; mesh volumes match the STLs to
≤0.4 mm³, the format's 4-decimal rounding). `heron-case-bambu-
project.3mf` rebuilt from a fresh backup: the **only** changed
entries are `3D/Objects/object_3.model` (dock_lower),
`3D/Objects/object_4.model` (dock_upper) and
`Metadata/model_settings.config` (dock face counts now 688/392)
— bezel, back cover, all print settings, plates and thumbnails
are byte-identical to the backup, and the embedded dock meshes
match the STLs (float32 storage rounding ≤4×10⁻⁶ mm, the same
class as Bambu's own files). Backup:
`heron-case-bambu-project.bak-20261103-pegremoval.3mf`
(md5 cedc1d9d786cdd51b98e219f5726733e — verified identical to
the pre-pass project).

## Salvage — the pair already printed

- **Pegs: snip them flush** (side cutters + a lick of a file).
  The printed upper has no holes, so with the pegs gone the
  halves mate on the tabs alone — the joint Jimmy already
  assembled and approved.
- **Exit notch: yes** — file or Dremel a notch **up** the back
  wall from the existing slot: from the slot's top edge up ~6 mm
  (to ≈z 16–17), over a ~15–20 mm width centred on the slot.
  The printed interior has no ramp (floor stays at z 2.5), so
  the cord makes one step up inside and out the notch — a
  workable field version of the raise. The wall is 4 mm PETG;
  go slow so it doesn't melt.

## Checksums (md5)

| File | md5 |
|---|---|
| src/heron_case.scad | 9c34f493ff4f6fc1c96ebf8473de181e |
| stl-fixed/dock_lower.stl | 5fe1ad207a907afadde8024f635329ce |
| stl-fixed/dock_upper.stl | 859bfe39c99e0e0c9b6371e5937aea49 |
| stl-fixed/dock.stl (one-piece reference) | 520be7de7ee95bca99fd16034ef34ba8 |
| dock-split.3mf | 5916493af86a87075c47ba94071f46bc |
| heron-case-bambu-project.3mf | 2b34a9ee1e913aed1909e56e9d00c522 |
