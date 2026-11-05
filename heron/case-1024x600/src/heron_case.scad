// =====================================================================
//  Heron 7" creature frame — picture-frame case + LOW dock
//  Board: Waveshare ESP32-P4-WIFI6-Touch-LCD-7B (SKU 32510, BASIC)
//  Jimmy's form call (2026-11-02): stands like the ESP32-S3-BOX-3 in its
//  dock — upright, slight recline — but LOW: frame bottom edge ~5 mm off
//  the desk, not perched up high.
//
//  VERIFIED dims (Waveshare product page + docs, 2026-11-02):
//    panel outline 164.28 x 99.17 mm; active area 154.58 x 86.42 mm.
//
//  PROTOTYPE REVISION 2026-11-04 (board in hand, Rev1.1; see
//  RECONCILIATION-2026-11-04.md + REVISION-2026-11-04.md):
//  the official outline drawing (Waveshare product page, "outline
//  dimensions") gives PCB envelope 164.00 x 97.00 and hole pitch
//  156 x 89 — both now VERIFIED below. ALL USB is on ONE short edge
//  (back-view right = frame LEFT wall): ON/OFF switch, USB-OTG
//  Type-A, Type-C "USB" (power/flashing), Type-C "USB TO UART".
//  Jimmy's prototype rulings: side plug-in is fine; the tray's USB
//  wall gets a full relief window (drop-in/lift-out with zero
//  connector contact + plug/switch access from the side); the JST
//  edge gets a clearance relief too; the back cover gets a matching
//  notch; the enclosed kit speaker does NOT live in the cover
//  (grille deleted); mics are back-facing at the panel corners, so
//  the chin holes are OFF (solid chin, drill later if wanted);
//  dock UNCHANGED. The hidden chin-raceway cable route stays in
//  the geometry for the final version.
//
//  MATERIAL: tolerances below are the PETG-final values. PLA prototype
//  (what's in the printer now) shrinks less — see README "PLA vs PETG".
//  Colour in previews: rose violet, per Jimmy.
// =====================================================================

// ---------- part selector ----------
// "bezel" | "back" | "dock" | "dock_lower" | "dock_upper" |
// "fit_corner" | "hole_plate" | "assembly" | "exploded"
//   (assembly/exploded are preview-only; "dock" is the legacy
//   one-piece dock, kept as the reference solid for the split pair)
part = "assembly";

// ---------- panel (VERIFIED) ----------
panel_w   = 164.28;   // glass/module outline, Waveshare spec table
panel_h   = 99.17;
active_w  = 154.58;   // display area, Waveshare spec table
active_h  = 86.42;
stack_t   = 13.0;     // UNVERIFIED total panel+PCB stack thickness.
                      // Pocket is cut stack_t+0.8 deep; bump if the real
                      // stack (headers etc.) measures thicker.

// ---------- fit / material ----------
fit_clear = 0.6;      // per-side panel pocket clearance — PETG final.
                      // PLA PROTOTYPE: use 0.35 (PLA shrinks ~0.2-0.3%
                      // vs PETG ~0.3-0.6%; on 165 mm that is ~0.3-0.5 mm
                      // total, i.e. the PLA print fits slightly looser
                      // on the panel and slightly tighter on inserts).
hole_clear_d = 3.4;   // M3 clearance hole dia in back cover (PETG).
                      // PLA prototype: 3.3 is fine, 3.4 still works.
insert_pilot_d = 4.3; // M3 brass heat-set insert pilot (insert OD ~4.2-4.6)
wall      = 2.0;      // general wall (>=1.6 mm class for PETG)
slab_t    = 2.4;      // front bezel face thickness

// ---------- frame proportions ----------
side_band = 9;        // frame bar width, left/right of pocket
top_band  = 10;       // frame bar height above pocket
chin      = 21;       // bottom "chin" bar: hosts radar window + mics,
                      // and its hollow back is the USB cable raceway
corner_r  = 4;        // outer corner radius

pocket_w  = panel_w + 2*fit_clear;
pocket_h  = panel_h + 2*fit_clear;
outer_w   = pocket_w + 2*side_band;
outer_h   = pocket_h + top_band + chin;
tray_d    = slab_t + stack_t + 0.8;      // bezel tray depth
cover_t   = 2.2;                          // back cover thickness
frame_d   = tray_d + cover_t;             // total frame thickness

// active area centre in frame coords (origin: frame bottom-left-front;
// active assumed centred on the panel — standard for this module)
act_cx = outer_w/2;
act_cy = chin + fit_clear + panel_h/2;

// ---------- case screws (M3, ours — NOT the board's holes) ----------
boss_d    = 7.5;
boss_inset = 6.5;     // boss centre distance from outer edges
boss_top_z = 13;      // boss pillar height from slab back

// ---------- board standoffs (VERIFIED 2026-11-04) ----------
// Official outline drawing: hole pitch 156.00 x 89.00 on the
// 164.00 x 97.00 PCB envelope (4.0 mm from each edge if symmetric).
// These short locating nubs on the back cover use the verified
// pitch; the design does not depend on them (panel is captured by
// the bezel lip) — delete (h=0) if they land wrong.
hole_pitch_x = 156;   // VERIFIED — Waveshare outline drawing
hole_pitch_y = 89;    // VERIFIED — Waveshare outline drawing
hole_dia     = 3.2;   // hole dia itself not dimensioned in the
                      // drawing; only used by hole_plate (M3-class)
standoff_h   = 0.6;   // locating nub height only — harmless if misplaced

// ---------- USB / cable ----------
usbc_x    = 0;        // legacy chin-notch centre offset. The notch +
                      // chin raceway remain for the FINAL version's
                      // hidden cable route; the prototype plugs in
                      // at the side window instead (see below).
notch_w   = 46;       // cable notch width through frame bottom (rear half)

// ---------- side relief windows (2026-11-04, prototype) ----------
// Frame coords are FRONT view. The board's USB edge (back-view
// right) is the frame's LEFT wall (x-min); the JST/RESET/BOOT edge
// (back-view left) is the frame's RIGHT wall (x-max). Each window
// cuts the tray wall from the slab back (z = slab_t) through the
// tray back, 0.6 mm past the pocket wall line into the pocket air,
// so edge connectors never touch printed material on the way in
// or out, and plugs + the power switch are reachable from the
// side. Spans are board-stack extents (official drawing, chained
// dims 13.57/15.28/11.91/10.68) mapped into frame coords with
// >= 5 mm margin at both ends (PCB-to-panel alignment assumed
// centred; the margin absorbs the +-1.1 mm uncertainty).
usb_win_y0 = 28;  usb_win_y1 = 117;   // USB stack + ON/OFF switch
jst_win_y0 = 36;  jst_win_y1 = 114;   // JST housings + RESET/BOOT
win_clear  = 0.6;                     // cut this far past pocket wall

// ---------- microphones (VERIFIED 2026-11-04 — chin holes OFF) ----------
// The real MIC1/MIC2 sit at the PCB's bottom corners on the BACK
// face (|x| ~ 74 mm from centre, behind the panel's bottom edge) —
// front chin holes at +-58 could never serve them. Prototype:
// solid chin (README's drill-later fallback). A final version
// would port the BACK COVER at the corners instead.
mic_holes = false;
mic_x     = 58;       // legacy — unused while mic_holes = false
mic_d     = 2.2;

// ---------- deferred sensors (provisions only) ----------
// HLK-LD2410C radar: module 16 x 22 mm (Hi-Link datasheet, verified).
// Mounts flat inside the chin (rotated: 22 wide x 16 tall), facing
// forward through a 1.2 mm radar-transparent thin section.
radar_win_w = 30; radar_win_h = 18; radar_thin = 1.2;
radar_x   = -32;      // window centre offset (left of centre; mics right)
// BH1750 light sensor: pocket + up-facing window slot in the top band.
// Sized for the common GY-302 breakout (~32 x 15 mm — TYPICAL, unverified).
bh1750_slot_w = 16; bh1750_slot_d = 6; bh1750_x = 40;

// ---------- dock ----------
tilt        = 10;     // recline, degrees back from vertical
dock_w      = 196;
dock_d      = 76;     // front-to-back footprint
dock_h      = 28;
slot_floor_z = 5;     // frame bottom edge height above desk — the "low"
slot_clear  = 0.8;    // per-side clearance, frame in slot
cable_exit_w = 48;    // rear cable exit width in dock back wall
cable_exit_sill = 9;  // exit sill height above the desk plane —
                      // raised from 2.5 on 2026-11-03 (see the exit
                      // cut in dock_geometry): the cord leaves over
                      // this sill and droops to the desk in free air

// ---------- dock split (2026-11-03, Jimmy's call) ----------
// The dock also builds as TWO snap-together halves (dock_lower /
// dock_upper) so neither print needs supports inside the cable
// cavity. Seam = the horizontal plane dock_split_z, the interior
// cavity's roof line: everything the cable touches (floor, exit,
// frame shelf) is below it; the frame slot and top skin are above.
// Union of the halves = the one-piece dock, plus the snap hardware:
// 4 cantilever fingers (upper) into grooves (lower side walls),
// 2 pry notches (back). (Locating pins/holes removed 2026-11-03 —
// Jimmy's ruling; the snap tabs alone carry the join.)
dock_split_z = 12;
snap_fy = [20, 36];   // snap finger centres (y): clear of the frame
                      // slot (y >= 43 at the seam) and of the frame
                      // shelf (y >= 54) at every height they occupy
// Tongue-and-groove seam (2026-11-03, Jimmy's refinement — replaces
// the deleted locating pins): a continuous tapered rib on the
// LOWER's seam ring seats in a straight channel in the UPPER's.
// It locates the halves along the whole joint and stiffens the
// long walls against mid-span bow; the snap fingers do the holding.
// Rib: 2.0 wide at base tapering to 1.2 at the tip, 1.7 tall.
// Channel: 2.6 wide (0.3 clearance per side), floor 1.9 above the
// seam (0.2 clear of the rib tip), leaving 0.7 of wall stock on
// each side of the channel in the 4 mm walls — a full perimeter
// at Jimmy's 0.42/0.45 line widths, where the old Ø3.6 holes had
// 0.2 and died. Rib and channel run the full seam ring, centred
// on the wall centrelines (back y=2, front y=74, sides x=+-96).
tongue_w = 2.0; tongue_tip_w = 1.2; tongue_h = 1.7;
groove_w = 2.6; groove_depth = 1.9;

// preview colour: rose violet
violet = [0.42, 0.24, 0.72];
violet_dark = [0.30, 0.16, 0.52];

// =====================================================================
// helpers
// =====================================================================
module rrect(w, h, r) {
  hull() for (sx = [-1, 1], sy = [-1, 1])
    translate([sx*(w/2 - r), sy*(h/2 - r)]) circle(r = r);
}
module rbox(w, h, d, r) linear_extrude(d) rrect(w, h, r);
module slot2d(len, w) hull() { translate([-len/2 + w/2, 0]) circle(d = w);
                              translate([ len/2 - w/2, 0]) circle(d = w); }

// frame-space: x 0..outer_w (left->right), y 0..outer_h (bottom->top),
// z 0.. (front face -> back). Parts are modelled centred on x for dock
// maths: cx() shifts to centre-origin where needed.
fx = outer_w/2;  // frame centre x in frame coords

// =====================================================================
// PART 1 — bezel tray
// =====================================================================
module bezel() {
  difference() {
    // outer tray body (rbox is centre-origin: shift to frame coords)
    translate([fx, outer_h/2, 0]) rbox(outer_w, outer_h, tray_d, corner_r);
    // panel pocket (from slab back to tray back)
    translate([fx, chin + pocket_h/2, slab_t])
      rbox(pocket_w, pocket_h, tray_d, 2);
    // display window through the front slab (clears active area + 1 mm)
    translate([act_cx, act_cy, -1])
      rbox(active_w + 1, active_h + 1, slab_t + 2, 3);
    // side relief windows (2026-11-04 prototype): through the tray
    // walls from the slab back to past the tray back. Left (frame
    // x-min) = the board's USB edge: the whole stack + ON/OFF
    // switch pass and stay reachable. Right (x-max) = JST housings
    // + RESET/BOOT clearance. The front slab (z < slab_t) is NOT
    // cut — the frame's face and display border are unchanged.
    translate([-1, usb_win_y0, slab_t])
      cube([side_band + 2*fit_clear + win_clear,
            usb_win_y1 - usb_win_y0, tray_d - slab_t + 0.5]);
    translate([outer_w - side_band - win_clear, jst_win_y0, slab_t])
      cube([side_band + 2*fit_clear + win_clear,
            jst_win_y1 - jst_win_y0, tray_d - slab_t + 0.5]);
    // chin raceway recess (hollow behind chin slab, open at the back,
    // overlapping the pocket floor by 1 mm so a bottom-edge USB-C plug
    // has room and its cable can drop in)
    translate([fx, (2.5 + chin + 1)/2, slab_t + (tray_d - slab_t)/2])
      cube([outer_w - 24, chin + 1 - 2.5, tray_d - slab_t + 0.2],
           center = true);
    // radar thin section: recess deepened toward the slab at the radar
    // window, leaving exactly radar_thin of material at the front
    translate([fx + radar_x, chin/2 + 1, (radar_thin + slab_t + 0.2)/2])
      cube([radar_win_w, radar_win_h, slab_t + 0.2 - radar_thin],
           center = true);
    // cable notch: breaches the tray's bottom face, rear part of depth,
    // so the cable drops out of the raceway into the dock channel.
    // The cut must pass CLEAN through the back face (tray_d = 16.2):
    // z 6.0..16.6. (Bug 2026-11-03: the original z 6.3..15.7 left a
    // 0.5 mm skin at the back of the notch — the flimsy strip Jimmy
    // found in the first print. Front web stays 6.0 mm.)
    translate([fx + usbc_x, 0, 11.3])
      cube([notch_w, 7, 10.6], center = true);
    // heat-set insert pilot holes in the four tray corners (the corner
    // blocks are solid stock; screws come through the back cover)
    for (sx = [boss_inset, outer_w - boss_inset],
         sy = [boss_inset, outer_h - boss_inset])
      translate([sx, sy, tray_d - 6]) cylinder(h = 7, d = insert_pilot_d);
    // BH1750 window slot through the top band (faces up)
    translate([fx + bh1750_x, outer_h - top_band/2, tray_d/2])
      cube([bh1750_slot_w, top_band + 2, bh1750_slot_d], center = true);
    // top chimney vents through the top band
    for (i = [-2.5 : 1 : 2.5])
      translate([fx + i*22, outer_h - top_band/2, tray_d/2])
        rotate([90, 0, 0]) linear_extrude(top_band + 2, center = true)
          slot2d(15, 3);
    // mic holes through the chin slab
    if (mic_holes) for (s = [-1, 1])
      translate([fx + s*mic_x, chin/2 + 1, -1])
        cylinder(h = slab_t + 2, d = mic_d);
  }
  // BH1750 ledge inside the pocket top (module lies flat under the slot)
  translate([fx + bh1750_x, chin + pocket_h - 2.9, tray_d/2])
    cube([36, 1.6, tray_d - slab_t - 2], center = true);
  // radar locating ribs inside the chin raceway
  for (s = [-1, 1])
    translate([fx + radar_x + s*(radar_win_w/2 + 1), chin/2 + 1, slab_t + 1.5])
      cube([1.6, radar_win_h + 2, 3], center = true);
}

// =====================================================================
// PART 2 — back cover
// =====================================================================
module back_cover() {
  z0 = tray_d;  // sits on the tray back face
  difference() {
    union() {
      translate([fx, outer_h/2, z0]) rbox(outer_w, outer_h, cover_t, corner_r);
      // shallow locating rim into the pocket (behind the panel)
      translate([fx, chin + pocket_h/2, z0 - 0.7])
        difference() {
          rbox(pocket_w - 0.8, pocket_h - 0.8, 0.7, 2);
          translate([0, 0, -0.1])
            rbox(pocket_w - 0.8 - 3, pocket_h - 0.8 - 3, 0.9, 2);
        }
      // board standoff nubs (placeholder pitch — see header)
      for (sx = [-1, 1], sy = [-1, 1])
        translate([fx + sx*hole_pitch_x/2,
                   chin + fit_clear + panel_h/2 + sy*hole_pitch_y/2,
                   z0 - standoff_h])
          cylinder(h = standoff_h, d = 8);
    }
    // case screw clearance holes
    for (sx = [boss_inset, outer_w - boss_inset],
         sy = [boss_inset, outer_h - boss_inset])
      translate([sx, sy, z0 - 1]) cylinder(h = cover_t + 2, d = hole_clear_d);
    // vent slot field (over the SoC / PCB area — broad field, exact SoC
    // position unverified; chimney slots in the bezel top band help too)
    for (r = [0 : 4], c = [0 : 5])
      translate([fx - 55 + c*22, chin + 34 + r*11, z0 - 1])
        linear_extrude(cover_t + 2) slot2d(15, 3.2);
    // top vent row on the cover
    for (i = [-2.5 : 1 : 2.5])
      translate([fx + i*22, outer_h - 7, z0 - 1])
        linear_extrude(cover_t + 2) slot2d(14, 3);
    // (Speaker grille REMOVED 2026-11-04: the kit speaker is an
    // enclosed dual-driver box, not the loose driver this grille
    // was cut for, and it cannot live inside the closed frame —
    // see RECONCILIATION-2026-11-04.md. It stays external for the
    // prototype; a final version gives it a measured home.)
    // USB-edge notch (2026-11-04 prototype): the cover's left edge
    // (frame x-min = the board's USB edge) is opened over the tray
    // window's span, through the cover AND its locating rim, so
    // nothing presses on the USB-A socket's height and the plugs
    // + power switch stay reachable with the cover on.
    translate([-1, usb_win_y0, z0 - 1])
      cube([13, usb_win_y1 - usb_win_y0, cover_t + 2]);
    // cable notch continuation in cover bottom edge
    translate([fx + usbc_x, 2, z0 + cover_t/2])
      cube([notch_w, 7, cover_t + 2], center = true);
  }
}

// =====================================================================
// PART 3 — low dock
// Dock coords: x centred 0, y 0..dock_d (0 = BACK, dock_d = FRONT),
// z 0.. up. Frame local -> dock: rotate about X by (90 - tilt) around
// the pivot at the slot floor, so the frame reclines `tilt` degrees.
// =====================================================================
dock_pivot = [0, dock_d - 10, slot_floor_z];
module frame_in_dock() {
  translate(dock_pivot) rotate([90 + tilt, 0, 0])
    translate([-fx, 0, 0]) children();
}
module dock_geometry() {
  difference() {
    // blank
    translate([-dock_w/2, 0, 0]) cube([dock_w, dock_d, dock_h]);
    // interior cavity (low hollow under the slot floor: cable space)
    translate([-dock_w/2 + 4, 4, 2.5])
      cube([dock_w - 8, dock_d - 8, 9.5]);
    // upper lightening cavity (keeps 3 mm top skin, solid cheeks)
    translate([-dock_w/2 + 6, 10, 12])
      cube([dock_w - 12, dock_d - 20, dock_h - 15]);
    // slot for the frame (frame volume + clearance, tilted)
    frame_in_dock()
      translate([0, -slot_clear, -slot_clear - 2])
        cube([outer_w + 2*slot_clear, outer_h + 30,
              frame_d + 2*slot_clear + 4]);
    // rear cable exit — must span the full back wall (y 0..4) AND bite
    // into the interior cavity (starts y=4): y -4..8. (Bug 2026-11-03:
    // the original cut spanned y -5..3 and left a 1 mm membrane at
    // y 3..4 sealing the cavity — found in Jimmy's first print.)
    // RAISED 2026-11-03 (defect #3, Jimmy): the original slot spanned
    // z 2.5..10.5 — its sill flush with the cavity floor, 2.5 mm above
    // the desk, so the exiting cord was pinched between the sill edge
    // and the desk ("how is a cord supposed to come out of that slot
    // if it sits at the bottom of the stand?"). The slot now spans
    // z 9..17 — sill cable_exit_sill = 9 mm above the desk plane —
    // and the cable ramp (below, with the shelf) walks the interior
    // channel floor up to meet it. The cord leaves horizontally and
    // droops to the desk in free air over its own bend radius. The
    // slot now crosses the z=12 seam: each half prints its share of
    // the opening, both support-free, and the seam tongue/groove
    // interrupts across it.
    translate([0, 2, cable_exit_sill + 4])
      cube([cable_exit_w, 12, 8], center = true);
    // rubber pad recesses
    for (sx = [-1, 1], sy = [10, dock_d - 10])
      translate([sx*(dock_w/2 - 14), sy, -0.6]) cylinder(h = 1.2, d = 11);
  }
  // slot floor shelf (frame rests here; rear gap lets the cable drop
  // from the frame's bottom notch into the cavity and out the back)
  frame_in_dock()
    translate([0, -slot_clear - 0.5, -slot_clear])
      cube([outer_w + 2*slot_clear, 1.6, frame_d - 6]);
  // shelf support ribs down to the floor
  for (s = [-1, 1])
    translate([s*(dock_w/2 - 20), dock_d - 16, 2.5])
      cube([6, 10, slot_floor_z - 2.5 + 1.6]);
  // cable ramp (2026-11-03, with the raised exit): a wedge in the
  // rear of the cavity that walks the channel floor (z 2.5) up to
  // the exit sill (z 9) at the back wall — a ~14 deg slope the cord
  // lies on, instead of a 6.5 mm step up to the sill. Hull of the
  // toe plate on the floor and a sliver at the wall just under the
  // sill. Entirely inside the lower half (top at z 9 < seam 12),
  // clear of the frame shelf at the front and of the snap fingers
  // at the sides; 60 wide, so the cord is never funnelled.
  hull() {
    translate([-30, 4, 2.5]) cube([60, 26, 0.2]);
    translate([-30, 4, cable_exit_sill - 0.2]) cube([60, 0.2, 0.2]);
  }
  // ribs under the lightening-cavity roof (behind the slot, clear of
  // the frame's reclined back face by >= 5 mm)
  for (s = [-1, 1])
    translate([s*45 - 1.2, 10, 12]) cube([2.4, 30, dock_h - 15]);
}

// the legacy one-piece dock — unchanged reference solid
module dock() { dock_geometry(); }

// =====================================================================
// PART 3b — the dock as two snap-together halves (2026-11-03)
// Lower half prints as-is (bottom on the bed): an open-top tub.
// Upper half prints TOP-FACE DOWN (seam face up): the lightening
// pocket opens upward, the roof ribs stand on the top skin, and the
// snap fingers point up off the seam face — no bridging anywhere.
// =====================================================================
module dock_pry_notches() {
  // two shallow notches across the seam on the BACK face, so a
  // fingernail or spudger can start the separation. 0.8 mm deep —
  // the one deliberate deviation from the one-piece exterior.
  for (sx = [-70, 70])
    translate([sx, 0, dock_split_z]) cube([10, 1.6, 2.0], center = true);
}
module dock_snap_finger(s, fy) {
  // Cantilever snap finger in profile (x, z), extruded 12 mm in y
  // and centred on fy. Hangs from the upper half's cheek (root
  // embedded to z 12.5) down the lower cavity's side wall: finger
  // 1.6 thick (x 92.1..93.7, 0.3 running clearance to the wall face
  // at 94), barb 0.9 proud (tip x 94.6) with ~38 deg lead-in and
  // ~38 deg cam-out ramps, so assembly deflects it 0.6 mm and a
  // firm straight pull cams it back out — hand-separable, no tools.
  // Free length root->barb ~6.3 mm at 0.6 mm deflection and 1.6 mm
  // thickness gives ~3.6% peak strain: inside PETG's repeated-snap
  // comfort zone. Barb z-band 5.5..6.0 sits in the wall groove.
  pts = [[s*92.1, 4.6], [s*93.7, 4.6], [s*93.7, 4.8],
         [s*94.6, 5.5], [s*94.6, 6.0], [s*93.7, 6.7],
         [s*93.7, 12.5], [s*92.1, 12.5]];
  translate([0, fy + 6, 0]) rotate([90, 0, 0])
    linear_extrude(12) polygon(pts);
}
module seam_tongue_x(len, yc, xc = 0) {
  // tapered rib running along x, centred on wall centreline yc:
  // hull of a base box (tongue_w wide, z seam..seam+1.2) and a tip
  // box (tongue_tip_w wide, top at seam+tongue_h) — the hull tapers
  // the flanks ~13 deg per side over the full height, so the rib
  // self-seats into the channel on assembly.
  hull() {
    translate([xc, yc, dock_split_z + 0.6])
      cube([len, tongue_w, 1.2], center = true);
    translate([xc, yc, dock_split_z + tongue_h - 0.25])
      cube([len, tongue_tip_w, 0.5], center = true);
  }
}
module seam_tongue_y(len, xc) {
  hull() {
    translate([xc, dock_d/2, dock_split_z + 0.6])
      cube([tongue_w, len, 1.2], center = true);
    translate([xc, dock_d/2, dock_split_z + tongue_h - 0.25])
      cube([tongue_tip_w, len, 0.5], center = true);
  }
}
module seam_groove_x(len, yc, xc = 0) {
  // straight channel cut, floor at seam+groove_depth, sunk 0.2
  // below the seam plane for a clean boolean
  translate([xc, yc, dock_split_z + groove_depth/2 - 0.1])
    cube([len, groove_w, groove_depth + 0.2], center = true);
}
module seam_groove_y(len, xc) {
  translate([xc, dock_d/2, dock_split_z + groove_depth/2 - 0.1])
    cube([groove_w, len, groove_depth + 0.2], center = true);
}
module dock_lower() {
  difference() {
    union() {
      // the one-piece solid, clipped at the seam (keeps the tub,
      // cable exit, pad recesses, frame shelf + its support ribs).
      // The locating pins that used to stand on this seam ring were
      // REMOVED 2026-11-03 (Jimmy's ruling): at his slicer settings
      // the mating holes in the upper never materialised in the
      // print, and the snap tabs alone carry the join — verified by
      // him on the printed pair. In their place, the seam tongue
      // below locates the halves along the whole ring.
      intersection() {
        dock_geometry();
        translate([-dock_w/2 - 2, -2, -2])
          cube([dock_w + 4, dock_d + 4, dock_split_z + 2]);
      }
      // seam tongue: full ring — front rib (along x), side ribs
      // (along y), overlapping at the corners. The BACK rib is in
      // two segments: it interrupts at the cable exit (|x| < 26)
      // so the rib never crosses the opening.
      seam_tongue_x(71, 2, -61.5);
      seam_tongue_x(71, 2, 61.5);
      seam_tongue_x(194, dock_d - 2);
      seam_tongue_y(74, -(dock_w/2 - 2));
      seam_tongue_y(74, dock_w/2 - 2);
    }
    // snap grooves in the cavity side walls: 1.3 deep into the 4 mm
    // wall (2.7 mm of wall remains), 14 long (finger 12 + 1 a side),
    // z 4.7..6.9 around the barb band
    for (s = [-1, 1], fy = snap_fy)
      translate([s*94.55, fy, 5.8]) cube([1.5, 14, 2.2], center = true);
    // seam shave: the roof ribs' bottom faces sit exactly ON the
    // seam plane in the one-piece solid, so clipping leaves
    // zero-thickness slivers of them in the lower half — remove a
    // 0.4 mm band over each rib footprint (void below, ribs above,
    // so nothing real is touched)
    for (s = [-1, 1])
      translate([s*45, 25, dock_split_z]) cube([4, 34, 0.4], center = true);
    dock_pry_notches();
  }
}
module dock_upper() {
  difference() {
    union() {
      // the one-piece solid above the seam (slot, lightening
      // pocket, top skin, roof ribs)
      intersection() {
        dock_geometry();
        translate([-dock_w/2 - 2, -2, dock_split_z])
          cube([dock_w + 4, dock_d + 4, dock_h - dock_split_z + 4]);
      }
      // snap fingers, two per side, in the cavity's side margins
      for (s = [-1, 1], fy = snap_fy) dock_snap_finger(s, fy);
    }
    // (The Ø3.6 locating-pin holes that used to pierce this seam
    // face were REMOVED 2026-11-03, with the pins — see dock_lower.)
    // Seam groove: the matching channel for the lower's tongue,
    // same ring, same centrelines. Cuts run slightly long so the
    // channel is clean through the corners — except at the back,
    // where the channel interrupts at the cable exit (|x| < 26),
    // matching the tongue.
    seam_groove_x(71, 2, -61.5);
    seam_groove_x(71, 2, 61.5);
    seam_groove_x(196, dock_d - 2);
    seam_groove_y(76, -(dock_w/2 - 2));
    seam_groove_y(76, dock_w/2 - 2);
    dock_pry_notches();
  }
}

// =====================================================================
// fit-check parts
// =====================================================================
module fit_corner() {
  // one bezel corner (bottom-left, 80 x 80 mm of it): verifies pocket
  // clearance on the real panel corner, boss + insert fit, chin depth.
  intersection() {
    bezel();
    translate([-2, -2, -2]) cube([82, 82, tray_d + 4]);
  }
}
module hole_plate() {
  // 1.6 mm plate with the 4 placeholder board holes at 1:1 pitch,
  // plus a 50 mm calibration window. Lay it on the real PCB: if the
  // holes line up, hole_pitch_x/y in this file are right.
  difference() {
    translate([fx, chin + fit_clear + panel_h/2, 0])
      rbox(hole_pitch_x + 24, hole_pitch_y + 24, 1.6, 3);
    for (sx = [-1, 1], sy = [-1, 1])
      translate([fx + sx*hole_pitch_x/2,
                 chin + fit_clear + panel_h/2 + sy*hole_pitch_y/2, -1])
        cylinder(h = 3.6, d = hole_dia);
    // calibration square 50 x 50 (cut) — check your slicer scaling
    translate([fx - 25, chin + fit_clear + panel_h/2 - 25, -1])
      cube([50, 50, 3.6]);
  }
}

// =====================================================================
// preview-only panel dummy
// =====================================================================
module panel_dummy() {
  color([0.08, 0.08, 0.11])
    translate([fx, chin + fit_clear + panel_h/2, slab_t + stack_t/2])
      cube([panel_w, panel_h, stack_t], center = true);
  color([0.16, 0.13, 0.24])  // dark violet "screen on" face
    translate([act_cx, act_cy, slab_t - 0.15])
      cube([active_w, active_h, 0.3], center = true);
}

// =====================================================================
module exploded() {
  color(violet) translate([0, 0, 46]) bezel();
  translate([0, 0, 26]) panel_dummy();
  color(violet_dark) translate([0, 0, 0]) back_cover();
  color(violet_dark)
    translate([fx, -70, -120]) dock();
}
module assembly() {
  frame_in_dock() {
    color(violet) bezel();
    panel_dummy();
    color(violet) back_cover();
  }
  color(violet_dark) dock();
}

// (colors are preview-only; STL/3MF exports ignore them)
if (part == "bezel")      color(violet) bezel();
if (part == "back")       color(violet) back_cover();
if (part == "dock")       color(violet_dark) dock();
if (part == "dock_lower") color(violet_dark) dock_lower();
if (part == "dock_upper") color(violet) dock_upper();
if (part == "fit_corner") color(violet) fit_corner();
if (part == "hole_plate") color(violet) hole_plate();
if (part == "assembly")   assembly();
if (part == "exploded")   exploded();

echo(str("outer frame: ", outer_w, " x ", outer_h, " x ", frame_d, " mm"));
echo(str("glass bottom above desk: ",
         slot_floor_z + chin + fit_clear + (panel_h - active_h)/2, " mm"));
echo(str("dock footprint: ", dock_w, " x ", dock_d, " mm"));
