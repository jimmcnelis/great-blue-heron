#!/usr/bin/env python3
"""Strike-still anchor offset — MEASUREMENT ONLY (no re-posing).

Applies the rest-still instrument set to audubon_strike.png: bill
geometry anchor (tip - 0.298 H along the bill axis), centreline
breast (DT-crossing rule), breast-relative anchor offset in H
fractions. H = 562 px, the same bird's standing height from the
rest still (the lunge pose has no standing height of its own).
Chart side: identical quantities for strike frames via the v2
keypoints (breast = spine[0], anchor = head_c, H = 73.57 units).
The offset table lets Jimmy price a future strike re-pose; nothing
here changes any chart.
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HOME = os.path.expanduser('~')
ART2 = f'{HOME}/workspace/heron/art2'
FS = f'{ART2}/finished-art-stills'
OUT = f'{FS}/rig-v2/head-anchor'
sys.path.insert(0, ART2)
sys.path.insert(0, f'{HOME}/workspace/heron/src13')
sys.path.insert(0, f'{FS}/refinish-corpus/work')
sys.path.insert(0, OUT)
import gate
import roster_charts as RC
import roster_render_v2 as RR2
import rig13_r4_v2 as R2
from necktools import skeleton, centreline_path, arc_len

W, H = 1024, 600
H_REF = 562.0
res = {}
a = gate.load_norm(f'{FS}/audubon_strike.png')
bm = gate.bird_mask(a)
saved = np.asarray(Image.open(f'{FS}/rig-v2/masks/approved_strike_mask.png')) > 0
res['mask_matches_saved_phaseA'] = bool((bm == saved).all())
dt = ndimage.distance_transform_edt(bm)
lab_all, n_all = ndimage.label(bm, np.ones((3, 3)))
sizes_all = ndimage.sum(bm, lab_all, range(1, n_all + 1))
main = lab_all == (1 + int(np.argmax(sizes_all)))
lum = a.mean(axis=2)
r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]

# eye: darkest cluster near the grounded seed (761, 448)
ex0, ey0 = 761, 448
win = lum[ey0 - 18:ey0 + 18, ex0 - 18:ex0 + 18]
wys, wxs = np.nonzero(win < 60)
eye = (float(wxs.mean() + ex0 - 18), float(wys.mean() + ey0 - 18))
res['eye_px'] = [round(eye[0], 1), round(eye[1], 1)]

# bill: largest yellow component in the lower-right head zone
ym = bm & (r > 150) & (g > 95) & (b < 120) & ((r - b) > 60)
lab2, n2 = ndimage.label(ym, np.ones((3, 3)))
s2 = ndimage.sum(ym, lab2, range(1, n2 + 1))
cand = []
for i in range(n2):
    yy, xx = np.nonzero(lab2 == i + 1)
    if xx.mean() > 640 and yy.mean() > 320:
        cand.append((s2[i], i + 1))
cand.sort(reverse=True)
bill_lab = cand[0][1]
bys, bxs = np.nonzero(lab2 == bill_lab)
bp = np.stack([bxs, bys], axis=1).astype(float)
cen = bp.mean(axis=0)
evals, evecs = np.linalg.eigh(np.cov((bp - cen).T))
axis = evecs[:, int(np.argmax(evals))]
if axis[1] < 0:
    axis = -axis                       # bill points DOWN-forward here
res['bill'] = dict(comp_px=int((lab2 == bill_lab).sum()),
                   comp_x=[int(bxs.min()), int(bxs.max())],
                   comp_y=[int(bys.min()), int(bys.max())],
                   axis_deg=round(float(np.degrees(np.arctan2(axis[1], axis[0]))), 2))
# tip: walk from the saturated component's max-projection point
# along the axis, at most +12 px, while mask continues (the pale
# tip extension was 5 px on the rest still). A free projection
# search gets captured by the waterline wash, which the tip
# nearly touches.
comp_proj = (bp - cen) @ axis
p_tip = bp[int(np.argmax(comp_proj))]
tip = p_tip.copy()
miss = 0
for s in range(1, 13):
    q = p_tip + axis * s
    hit = False
    for dx in (-2, -1, 0, 1, 2):
        for dy in (-2, -1, 0, 1, 2):
            qi = (int(round(q[0] + dx)), int(round(q[1] + dy)))
            if 0 <= qi[0] < W and 0 <= qi[1] < H and bm[qi[1], qi[0]]:
                hit = True
    if hit:
        tip = q
        miss = 0
    else:
        miss += 1
        if miss >= 2:
            break
res['bill']['tip_px'] = [round(float(tip[0]), 1), round(float(tip[1]), 1)]

anchor = (tip[0] - 0.298 * H_REF * axis[0], tip[1] - 0.298 * H_REF * axis[1])
res['anchor_px'] = [round(float(anchor[0]), 1), round(float(anchor[1]), 1)]
res['head_to_tip_px'] = round(float(np.hypot(*(tip - anchor))), 1)

# centreline breast + neck arc (same rules as the rest still)
skel = skeleton(bm)
path, sk_start = centreline_path(skel, dt, anchor)
pdts = np.array([dt[p[1], p[0]] for p in path])
med_dt = float(np.median(pdts[len(pdts) // 4: 3 * len(pdts) // 4]))
thr = max(30.0, 1.35 * med_dt)
bi = next(i for i, v in enumerate(pdts) if v > thr)
breast = np.array(path[bi], float)
hop = float(np.hypot(*(np.array(path[0], float) - anchor)))
neck_arc = arc_len(path[:bi + 1]) + hop
res['breast_px'] = [int(breast[0]), int(breast[1])]
res['neck'] = dict(arc_px=round(neck_arc, 1), arc_over_H=round(neck_arc / H_REF, 4),
                   median_neck_dt=round(med_dt, 1), breast_threshold_dt=round(thr, 1))
delta = anchor - breast
res['delta_anchor_minus_breast_px'] = [round(float(delta[0]), 1), round(float(delta[1]), 1)]
res['delta_over_H'] = [round(float(delta[0] / H_REF), 4), round(float(delta[1] / H_REF), 4)]

ov = Image.fromarray(a.astype(np.uint8)).convert('RGB')
dr = ImageDraw.Draw(ov)
dr.line([tuple(p) for p in path[:bi + 1]], fill=(255, 0, 0), width=2)
for p, col in ((tuple(anchor), (255, 0, 255)), (tuple(eye), (0, 200, 0)),
               (tuple(tip), (0, 0, 255)), (tuple(breast), (255, 165, 0))):
    dr.ellipse([p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6], outline=col, width=2)
ov.save(f'{OUT}/centreline_overlay_strike.png')

# chart side: identical quantities per frame (v2 keypoints, exact)
tab = {}
for fi in (0, 12, 24, 26, 27, 28, 30, 36, 44):
    pose = RC.CHARTS['strike']().frames[fi]
    kp = RR2.keypoints_for(pose)
    br = np.array(kp['spine'][0], float)
    an = np.array(kp['head_c'], float)
    xf, _p = R2.body_xform(pose)
    st = R2.YAW_STOPS[0]
    brd = np.array(xf((R2.BREAST_LOCAL[0] + st['ndx'], R2.BREAST_LOCAL[1])))
    spine, _ = R2.neck_spine(pose, brd)
    arc = float(np.hypot(*np.diff(spine, axis=0).T).sum())
    d = an - br
    tab[f'f{fi:04d}'] = dict(
        hx=float(pose['hx']), hy=float(pose['hy']), coil=float(pose['coil']),
        delta_units=[round(float(d[0]), 2), round(float(d[1]), 2)],
        delta_over_H=[round(float(d[0] / 73.57), 4), round(float(d[1] / 73.57), 4)],
        neck_arc_over_H=round(arc / 73.57, 4),
        offset_vs_still_over_H=[round(float(d[0] / 73.57 - delta[0] / H_REF), 4),
                                round(float(d[1] / 73.57 - delta[1] / H_REF), 4)])
res['chart_frames'] = tab

with open(f'{OUT}/strike_measurements.json', 'w') as f:
    json.dump(res, f, indent=1)
print(json.dumps(res, indent=1))
