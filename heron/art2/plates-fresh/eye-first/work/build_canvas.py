"""Batch 3 — structural CANVAS for the ALERT pose, computed fresh from the
corrected mechanism (rig_v25.py + animal_v25.json). No image of any kind is
an input: every shape below is mechanism geometry (torso loop, neck chain +
rest width profile, head assembly at canon proportions, corrected leg
traces) drawn flat in species-palette roles so a generator can paint inside
the geometry instead of freehanding proportions.

Canvas facts (mechanism, alert): neckbase (601.2, 219.4), skull centre
(740.8, 42.5), eye anchor (754.7, 35.7), design chord_base 0.456,
T = 493.85 px, corrected legs end AT the waterline y = 382 (joints at
(406, 382) near / (358, 382) far; below the line: paper only).
"""
import sys, math, json
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/creature-engine/packages/great-blue-heron')
import rig_v25 as R
from PIL import Image, ImageDraw

W, H = 1024, 600
T = R.T
POSE = 'alert'

# palette (species.yaml roles)
PAPER    = (240, 233, 216)
INK      = (0, 0, 0)
OUTLINE  = (30, 48, 74)
SLATE    = (105, 130, 155)
DARKSLATE= (66, 93, 122)
PALE     = (176, 203, 224)
ORANGE   = (240, 133, 36)
RUSTY    = (154, 82, 60)
LEGCOL   = (74, 48, 36)
AMBER    = (232, 164, 32)
PLUME_BG = (229, 235, 242)
PLUME_LN = (133, 155, 180)
TICK     = (141, 171, 201)
WING_SEAM= (48, 70, 98)

img = Image.new('RGB', (W, H), PAPER)
dr = ImageDraw.Draw(img)

dv = R.design_values(POSE)
pts, heads, spec = dv['pts'], dv['heads'], R.ANIMAL['poses'][POSE]
neckbase, skull = dv['neckbase'], dv['skull']
mask_img, _, eye = R.render(POSE)
eye = np.array(eye, float)

# ---------------------------------------------------------------- torso
loop = R.catmull_rom(R.TORSO_LOOP, n_per=3, closed=True)
dr.polygon([tuple(p) for p in loop], fill=SLATE)
# folded wing: band along the back line, pulled toward the torso centroid
centroid = np.array(R.TORSO_LOOP, float).mean(axis=0)
back_idx = list(range(0, 26))                      # tail -> over the back -> chest
wing = [np.array(R.TORSO_LOOP[i], float) for i in back_idx]
wing_in = [p + (centroid - p) * 0.16 + np.array([0, 20]) for p in wing]
dr.polygon([tuple(p) for p in wing] + [tuple(p) for p in wing_in[::-1]], fill=DARKSLATE)
for f in (0.3, 0.52, 0.74):                        # scallop seam suggestion
    a = wing[int(f * (len(wing) - 1))]
    b = wing_in[int(f * (len(wing_in) - 1))]
    dr.line([tuple(a), tuple(b)], fill=WING_SEAM, width=2)
dr.line([tuple(p) for p in loop] + [tuple(loop[0])], fill=OUTLINE, width=2)

# ---------------------------------------------------------------- legs (corrected traces; END at the joint / waterline)
for hip, joint, foot in R.LEGS_BY_POSE[POSE]:
    hip, joint = np.array(hip, float), np.array(joint, float)
    d = joint - hip; L = np.hypot(*d); d /= L
    pp = np.array([-d[1], d[0]])
    mid = hip + (joint - hip) * 0.58               # rusty thigh -> dark shin
    def taper(a, b, w0, w1, fill):
        dr.polygon([tuple(a + pp * w0 / 2), tuple(b + pp * w1 / 2),
                    tuple(b - pp * w1 / 2), tuple(a - pp * w0 / 2)], fill=fill)
    taper(hip, mid, 17, 12, RUSTY)
    taper(mid, joint, 12, 9, LEGCOL)
    dr.ellipse([joint[0] - 7, joint[1] - 5, joint[0] + 7, joint[1] + 5], fill=LEGCOL)

# ---------------------------------------------------------------- neck tube (station-mapped sheet)
dense = R.dense_chain(pts)
s_cum = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(dense, axis=0).T))])
u_full = s_cum / s_cum[-1]
widths = R.width_rest(np.clip(u_full, 0, 1)) * T
if spec.get('slimming'):
    widths = widths * R.slim_mult(np.clip(u_full, 0, 1))
tube = R.tube_poly(dense, widths)
dr.polygon([tuple(p) for p in tube], fill=PALE)
# back-of-neck overlay: centreline shifted to the back, narrower band in slate
grad = np.gradient(dense, axis=0)
gn = np.hypot(grad[:, 0], grad[:, 1]); gn[gn == 0] = 1
nrm = np.stack([-grad[:, 1] / gn, grad[:, 0] / gn], axis=1)
away = np.sign(((dense - centroid) * nrm).sum(axis=1)); away[away == 0] = 1
front_n = nrm * away[:, None]                      # normal pointing away from body centre = throat side
back_c = dense - front_n * (widths[:, None] * 0.22)
back_tube = R.tube_poly(back_c, widths * 0.58)
dr.polygon([tuple(p) for p in back_tube], fill=SLATE)
dr.line([tuple(p) for p in tube] + [tuple(tube[0])], fill=OUTLINE, width=2)
# station ticks across the visible tube (u = arc fraction, the (u,v) sheet made visible)
vis, nb = R.visible_chain(pts)
vis_len = float(np.hypot(*np.diff(vis, axis=0).T).sum())
u0 = 1 - (vis_len / T) / R.ANIMAL['neck_chain']['arc_total']
for f in np.arange(0.1, 0.95, 0.1):
    c = R.pt_at_frac(vis, f)
    i2 = min(max(int(f * (len(vis) - 1)), 1), len(vis) - 2)
    gd = vis[i2 + 1] - vis[i2 - 1]; gl = np.hypot(*gd); gd = gd / max(gl, 1e-9)
    nn = np.array([-gd[1], gd[0]])
    hw = R.width_rest(np.clip(u0 + f * (1 - u0), 0, 1)) * T / 2
    dr.line([tuple(c - nn * hw), tuple(c + nn * hw)], fill=TICK, width=1)

# ---------------------------------------------------------------- shoulder patch (caps the neck root)
dr.ellipse([neckbase[0] - 24, neckbase[1] - 9, neckbase[0] + 14, neckbase[1] + 15],
           fill=INK)

# ---------------------------------------------------------------- breast plume: fixed roots, countable strands
seam_top = np.array([600, 228], float); seam_bot = np.array([548, 298], float)
roots = [seam_top + (seam_bot - seam_top) * (i / 13) for i in range(14)]
tips = []
for i, r0 in enumerate(roots):
    ln = 100 + 42 * math.sin(i * 1.7) ** 2 + i * 1.5
    ln = min(ln, 372 - r0[1])          # strands end above the waterline (y=382)
    tips.append(r0 + np.array([14 - i * 0.7, ln]))
wedge = roots + tips[::-1]
dr.polygon([tuple(p) for p in wedge], fill=PLUME_BG)
for r0, tp in zip(roots, tips):
    ctrl = r0 + np.array([8, (tp[1] - r0[1]) * 0.5])
    seg = []
    for t in np.linspace(0, 1, 16):
        seg.append((1 - t) ** 2 * r0 + 2 * (1 - t) * t * ctrl + t ** 2 * tp)
    dr.line([tuple(p) for p in seg], fill=PLUME_LN, width=2)

# ---------------------------------------------------------------- head assembly (canon proportions)
ha = R.ANIMAL['head_assembly']
final_head = heads[-1] + spec['head_pitch_offset_deg']
a = math.radians(final_head)
dvec = np.array([math.cos(a), math.sin(a)])
perp = np.array([dvec[1], -dvec[0]])               # 'up' side of the bill line (rig convention)
minor_axis = np.array([-dvec[1], dvec[0]])
sma, smi = ha['skull_semi_major'] * T, ha['skull_semi_minor'] * T
ell = [skull + dvec * math.cos(th) * sma + minor_axis * math.sin(th) * smi
       for th in np.linspace(0, 2 * math.pi, 48)]
dr.polygon([tuple(p) for p in ell], fill=(252, 252, 250))
dr.line([tuple(p) for p in ell] + [tuple(ell[0])], fill=OUTLINE, width=2)
# occipital plume strands (2, trailing behind the skull)
occ = skull - dvec * sma * 0.92 + perp * 2
for k, (back, drop) in enumerate(((0.115, -0.030), (0.09, -0.052))):
    tip = skull + (dvec * -back + perp * drop) * T
    ctrl = occ + (dvec * -back * T * 0.5) + np.array([0, 6 + 4 * k])
    seg = []
    for t in np.linspace(0, 1, 16):
        seg.append((1 - t) ** 2 * occ + 2 * (1 - t) * t * ctrl + t ** 2 * tip)
    dr.line([tuple(p) for p in seg], fill=INK, width=2)
# black brow band across the top of the skull
band = []
for s in np.linspace(-0.85, 0.8, 14):
    off = smi * math.sqrt(max(1 - s ** 2, 0.0)) * 0.94
    band.append(skull + dvec * (s * sma) + perp * off)
dr.line([tuple(p) for p in band], fill=INK, width=6)
# bill: tapered dagger from the skull
base_c = skull + dvec * ha['bill_base_offset_from_skull_centre'] * T
tip = skull + dvec * ha['bill_tip_reach_from_skull_centre'] * T
bw = 0.0135 * T
dr.polygon([tuple(base_c + perp * bw), tuple(tip), tuple(base_c - perp * bw)], fill=ORANGE)
dr.line([tuple(base_c + perp * bw), tuple(tip), tuple(base_c - perp * bw),
         tuple(base_c + perp * bw)], fill=OUTLINE, width=1)
# eye: PLACED at the mechanism anchor — ring + amber iris + pupil
dr.ellipse([eye[0] - 7, eye[1] - 7, eye[0] + 7, eye[1] + 7], outline=INK, width=2)
dr.ellipse([eye[0] - 5, eye[1] - 5, eye[0] + 5, eye[1] + 5], fill=AMBER)
dr.ellipse([eye[0] - 2.2, eye[1] - 2.2, eye[0] + 2.2, eye[1] + 2.2], fill=INK)

# ---------------------------------------------------------------- water: RIPPLES ONLY (Jimmy, 2026-11-04 12:37)
# No line, no band, no blue may survive into a painted plate — the ripple
# rings ARE the waterline: each ring's centre sits at the intertarsal
# joint's height (y = 382). Canvas v1 carried a full-width construction
# line at this height; candidate 1 inherited it as a drawn line and died
# on the environment law, so the line was removed — the rings alone mark
# the height now.
WL = 382
for hip, joint, foot in R.LEGS_BY_POSE[POSE]:
    jx = joint[0]
    for wdt, hgt, lw in ((40, 9, 2), (64, 15, 1)):
        dr.ellipse([jx - wdt / 2, WL - hgt / 2, jx + wdt / 2, WL + hgt / 2],
                   outline=INK, width=lw)
# (nothing below the waterline but paper — the feet are underwater, undrawn)

img.save('/home/hatch/workspace/heron/art2/plates-fresh/eye-first/work/alert_canvas.png')

# ---------------------------------------------------------------- framing extents (Jimmy's framing gate, on the canvas itself)
crown_y = min(p[1] for p in ell) - 3
ext = dict(
    T_px=round(float(T), 2), neckbase=[round(float(x), 1) for x in neckbase],
    skull_centre=[round(float(x), 1) for x in skull],
    eye_anchor=[round(float(x), 1) for x in eye],
    bill_tip=[round(float(x), 1) for x in tip],
    bill_dir_deg=round(float(final_head), 2),
    chord_base_design=round(dv['chord_base'], 3),
    crown_top_y=round(float(crown_y), 1),
    margin_top_px=round(float(crown_y), 1),
    margin_right_px=round(float(W - tip[0]), 1),
    margin_left_px=round(float(min(p[0] for p in loop)), 1),
    waterline_y=WL,
    joints=[[int(j[0]), int(j[1])] for _, j, _ in R.LEGS_BY_POSE[POSE]],
)
print(json.dumps(ext, indent=1))
