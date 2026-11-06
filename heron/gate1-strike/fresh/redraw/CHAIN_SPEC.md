# SEQUENCE 1 (STRIKE) — FULL REDRAW SPEC (crew order 2026-11-05 14:35-14:37)

Replaces the v2 chain. v1/v2 drawings are BANNED as inputs. Only this spec,
the references, and the MEASURED GEOMETRY (tip targets below, from
fresh/DENSIFY_STATUS.md + fresh/REPORT_DENSIFIED_20261105-1920.md) carry over.

## The anchor
- HOME = fresh/home_frame_approval.png — LOCKED. Stream index 0, shown t0-9 and
  t58-59, byte-identical. NOT redrawn. Its raw artwork is
  fresh/K_coil_color_redo.png (use as edit canvas only for RX_1).
- HOME is attached to EVERY generation call as color + identity authority.
  Every drawing is BORN in its register: slate-blue body/neck, warm orange
  dagger bill, yellow ringed eye, rusty thigh + bend-of-wing accents, shaggy
  chest-frill cascade, two black head plumes, one black shoulder patch, warm
  off-white paper. NO post-hoc color normalization anywhere.

## COLOR GATE (per drawing, measured on the raw 2048x1152 PNG)
bird_sat = mean HSV saturation over pixels with luminance < 210 (same function
as fresh/normalize_color_v2.py). HOME raw = 46.9.
GATE (coordinator-amended 2026-11-05, aligning the metric with the crew order's
own words - a drawing FAILS if it reads PALER or BLUER than home): FAIL if
bird_sat < 42.9 (paler than home -4) or if the view gate finds a blue/grey
shift vs home. Richer-than-home saturation is NOT the named failure (the v2
defect Jimmy rejected was a PALER chain); sats are tabulated for every drawing
in the report either way. Never gain a drawing up in post. A drawing that reads
grey/pale next to the home frame fails even if the number passes.

## Geometry (raw canvas 2048x1152; tips in 0-1000 normalized coords)
- Legs PLANTED, home stance in every drawing: front foot raw x ~16.5% width,
  rear foot ~23%, waterline y ~96.5% height, small ripple rings at each foot.
  (Registered check at assembly: feet 15.2% / 20.3% +/- 0.8.)
- Registration (assembly): uniform scale 0.80, offset (+48,+204); whole bird
  inside the frame always.
- Anti-clone gate (breakdowns): measured bill tip strictly between its two
  neighbours' tips, >=15% of the interval from either end.
- Attempts: TWO per pose. A breakdown that fails twice escalates to ONE fresh
  full drawing (label it ESCALATED in results). A key that fails twice is
  reported to the coordinator with measurements.

## Water (feet rings constant in EVERY drawing, incl. extension)
- Extension: no touch rings (bill above water). RK_PEAK: bill tip touches the
  surface; first small rings born at the touch point (under the tip).
- Withdrawal fraction f by tick: f = (t-17)/40.
  f 0-0.1: droplets falling from the bill + tight strong rings at touch point.
  f 0.1-0.3: rings spreading, clear. f 0.3-0.6: wide, medium-faint.
  f 0.6-0.85: widest, faint. f 0.85-1: ghost, nearly calm. HOME: calm.
- Blank paper only. No scenery, no text, no marsh (runtime composite).

## The chain (42 unique drawings incl. HOME; 60 ticks @ 12 fps = 5.0 s)

| name | type | tip target | ticks | notes |
|---|---|---|---|---|
| HOME | locked | (472,848) | t0-9, t58-59 | calm + feet rings |
| RX_1 | bd of HOME | (537,817) | t10 | extension launch, neck starting to unfold |
| RX_2 | bd | (577,814) | t11 | unfolding |
| RK_EMID | KEY | (643,840) | t12 | extension halfway; head rides right on the unfolding arc |
| RX_4 | bd | (629,906) measured | t14 | COORDINATOR RE-SLOT: drawn as an EMID->RX_5 halfway attempt, it landed past RX_5 toward PEAK (629,906) - so it plays AFTER RX_5 in the chain (order ...EMID, RX_5, RX_4, PEAK), one step before the peak. Nominal target (607,922) superseded by measured geometry (PEAK itself measured (621,931), not (596,954)). |
| RX_5 | bd | (632,883) measured | t13 | spear nearly straight, bill above water; plays before RX_4 per the re-slot above. |
| RK_PEAK | KEY | (596,954) | t15-16 | full extension, one straight spear line, bill tip TOUCHES water, rings born |
| RK_EXIT | KEY | (602,810) | t17 | head just clear of water, droplets falling, tight rings below |
| RW_A1 | bd | (600,817) | t18 | droplets, tight rings |
| RW_A2 | bd | (598,823) | t19 | droplets end, rings spreading |
| RW_A3 | bd | (601,808) | t20 | neck beginning to kink |
| RW_A4 | bd | (603,797) | t21 | rings spreading clear (f~0.1) |
| RW_A5 | bd | (602,778) | t22 | |
| RW_A6 | bd | (601,761) | t23 | |
| RW_A7 | bd | (601,738) | t24 | |
| RW_A8 | bd | (600,715) | t25 | rings wide, medium-faint (f~0.2-0.3) |
| RW_A9 | bd | (595,716) | t26-27 | head near-still, neck settling (2-tick hold) |
| RW_MIDW | bd (ex-KEY) | (596,734) | t28 | withdrawal halfway, neck re-coiling into S, rings wide medium-faint. COORDINATOR CHANGE: standalone key production failed across 5 attempts (fresh draws collapsed to upright-alert; edits produced a swan-S); produced in the B pass as an edit of RW_A9 (deepen the S, tip to target). Anti-clone note: the measured v1 path wiggles here (716 -> 734 -> 703), so the tip is not strictly between neighbours in y - documented exception, pose itself must be a genuinely deepened S, not a clone. |
| RW_B1 | bd | (600,703) | t29 | head rising |
| RW_B2 | bd | (604,672) | t30 | head at highest rise |
| RW_B3 | bd | (596,719) | t31 | head turning down into the re-coil dip |
| RW_B4 | bd | (587,766) | t32 | the dip |
| RW_B5 | bd | (579,775) | t33 | |
| RW_B6 | bd | (571,784) | t34 | rings widest, faint (f~0.45) |
| RW_B7 | bd | (562,807) | t35 | swinging toward the tuck |
| RW_B8 | bd | (554,830) | t36 | |
| RW_B9 | bd | (520,828) | t37 | entering the tuck swing |
| RW_C1 | bd | (485,826) | t38 | |
| RK_TUCK | KEY | (449,823) | t39-41 | deep tuck hold, head folded down-left to chest, bill pointing down; 3-tick hold (bird truly still) |
| RW_D0 | bd | (466,800) | t42 | first stir out of the tuck |
| RK_RISEA | KEY | (485,779) | t43 | head mid-rise out of the tuck, first third |
| RK_RISEB | KEY | (524,738) | t44 | head two-thirds risen, neck half-recoiled |
| RW_D1 | bd | (562,696) | t45 | re-coiled S nearly restored; rings widest faint (f~0.7) |
| RW_E1 | bd | (558,735) | t46 | settle begins, head lowering toward home |
| RW_E2 | bd | (555,775) | t47 | |
| RW_E3 | bd | (556,807) | t48 | |
| RW_E4 | bd | (553,796) | t49 | |
| RW_E5 | bd | (552,810) | t50 | rings ghost (f~0.83) |
| RW_E6 | bd | (551,822) | t51-52 | micro-settle (2-tick hold) |
| RW_E7 | bd | (550,824) | t53-54 | micro-settle (2-tick hold) |
| RW_E8 | bd | (550,823) | t55-56 | micro-settle (2-tick hold) |
| RK_SETTLE | KEY | (510,836) | t57 | settle-approach: nearly the home coil, head slightly higher/forward of home; ghost rings |

Timing vs v2 (disclosed changes): freeze t0-9, peak beat t15-16 and HOME at
t58-59 unchanged. Withdrawal re-spaced to one drawing per tick where the bird
moves; the tuck is a single-drawing 3-tick hold (v2 used two near-identical
drawings x2 ticks each); segment E compressed by the D-segment's extra
interpolation drawing (RW_D0); no other phase boundaries moved.

## Outputs
- Raw drawings: redraw/poses/<NAME>.png at 2048x1152 (generation returns
  2096x1184 - resize to exactly 2048x1152, PIL LANCZOS, then measure).
- Per-worker results: redraw/work/<SEGMENT>_results.md - per pose: attempts,
  measured tip, bird_sat, verdict (PASS / ESCALATED / FAILED + why).
