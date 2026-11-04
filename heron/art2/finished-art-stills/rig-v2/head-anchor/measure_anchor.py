#!/usr/bin/env python3
"""Head-anchor measurement: approved rest still vs rig v2 idle hold.

Same instruments as Phase A/B (gate.bird_mask on the still; roster
keypoints on the rig). Definitions (stated once, used everywhere):

  HEAD ANCHOR := the skull centre -- the point the rig's head group
  rotates about (rig H). Primary location method = BILL GEOMETRY:
  anchor = bill_tip - (head->tip length) * bill_axis, because
  head->tip = 0.298 H is a locked proof-2 landmark the transplant
  must preserve, and the bill is the most precisely measurable
  feature on the still (mask extremity + a clean 1,288-px saturated
  component). Cross-checks reported: (a) EYE method (eye centre
  minus the rig's eye offset in H fractions) -- expected to sit
  forward of the bill anchor because Phase A measured the approved
  skull LONGER than the rig's authored skull (0.19-0.22 H vs ~0.17),
  so the rig's eye offset does not transfer; (b) geometric centroid
  of the skull mass (mask region y<110, x>600, DT>=4, bill component
  removed).

  H (approved) := crown -> foot. Crown = topmost main-component
  pixel with DT >= 8 at x > 620 (excludes the 1-2 px plume-strand
  tip that reaches y=18). Foot: the gate clips the mask at y=594,
  so the toes are not measurable from the mask; foot = 588, the
  waterline, Phase A's documented convention. H = 562 (Phase A
  said 561 with crown 27; immaterial).

  NECK CENTRELINE := medial-axis path (largest DT>=9 core component)
  from the skull base to the torso. BREAST ANCHOR := first path
  point from the head side where DT exceeds 1.35x the path's median
  neck DT (the tube has merged into the torso mass) -- mirrors the
  rig, whose breast sits essentially on the torso outline. The
  DT>=40 (deep-torso) variant is reported as a sensitivity bound.
  Neck length = arc from breast to the head anchor (final hop from
  the centreline's head end to the anchor included). Neck width =
  perpendicular cross-sections through the centreline (median of
  the middle reach); the 2xDT inscribed-circle profile is reported
  alongside (it under-reads a curved ribbon).

  BODY CENTROID (for commensurability with the Phase-B report's
  +310 / +102 px figures) := centroid of the mask minus the neck
  tube sweep, torso component selected by the same filter on both
  birds.
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HOME = os.path.expanduser('~')
ART2 = f'{HOME}/workspace/heron/art2'
FS = f'{ART2}/finished-art-stills'
sys.path.insert(0, ART2)
sys.path.insert(0, f'{HOME}/workspace/heron/src13')
sys.path.insert(0, f'{FS}/refinish-corpus/work')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gate
import roster_charts as RC
import roster_render_v2 as RR2
import maskrender_v2 as M2
import rig13_r4_v2 as R2
from necktools import skeleton, centreline_path, arc_len

W, H = 1024, 600
OUT = f'{FS}/rig-v2/head-anchor'
os.makedirs(OUT, exist_ok=True)

res = {}
a = gate.load_norm(f'{FS}/audubon_rest.png')
bm = gate.bird_mask(a)
saved = np.asarray(Image.open(f'{FS}/rig-v2/masks/approved_rest_mask.png')) > 0
res['mask_matches_saved_phaseA'] = bool((bm == saved).all())
res['approved_mask_area'] = int(bm.sum())
dt = ndimage.distance_transform_edt(bm)
lab_all, n_all = ndimage.label(bm, np.ones((3, 3)))
sizes_all = ndimage.sum(bm, lab_all, range(1, n_all + 1))
main = lab_all == (1 + int(np.argmax(sizes_all)))
res['main_component_area'] = int(main.sum())

# H: crown (DT>=8, x>620) -> foot 588 (waterline, gate clips at 594)
top = main & (dt >= 8)
top[:, :620] = False
crown_y = int(np.nonzero(top)[0].min())
foot_y = 588
H_app = foot_y - crown_y
res['approved_H'] = dict(crown_y=crown_y, foot_y=foot_y, H_px=H_app,
                         note='foot = waterline per Phase A; gate clips mask at y=594')

lum = a.mean(axis=2)
r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]

# eye: darkest cluster within r=18 of the grounded point (715, 50)
ex0, ey0 = 715, 50
win = lum[ey0 - 18:ey0 + 18, ex0 - 18:ex0 + 18]
wys, wxs = np.nonzero(win < 60)
eye = (float(wxs.mean() + ex0 - 18), float(wys.mean() + ey0 - 18))
res['eye_px'] = [round(eye[0], 1), round(eye[1], 1)]

# bill: largest saturated-yellow component in the head zone; tip =
# mask extremity in the head band (the pale tip escapes the colour
# class); axis = PCA of the component
ym = bm & (r > 150) & (g > 95) & (b < 120) & ((r - b) > 60)
lab2, n2 = ndimage.label(ym, np.ones((3, 3)))
s2 = ndimage.sum(ym, lab2, range(1, n2 + 1))
cand = [(s2[i], i + 1) for i in range(n2)
        if np.nonzero(lab2 == i + 1)[1].min() > 640]
cand.sort(reverse=True)
bill_lab = cand[0][1]
bys, bxs = np.nonzero(lab2 == bill_lab)
bp = np.stack([bxs, bys], axis=1).astype(float)
cen = bp.mean(axis=0)
evals, evecs = np.linalg.eigh(np.cov((bp - cen).T))
axis = evecs[:, int(np.argmax(evals))]
if axis[0] < 0:
    axis = -axis
band = main.copy()
band[:25, :] = False
band[95:, :] = False
band[:, :700] = False
tys, txs = np.nonzero(band)
tip = (float(txs.max()), float(tys[txs.argmax()]))
res['bill'] = dict(comp_px=int((lab2 == bill_lab).sum()),
                   comp_x=[int(bxs.min()), int(bxs.max())],
                   tip_px=[tip[0], tip[1]],
                   axis_deg=round(float(np.degrees(np.arctan2(axis[1], axis[0]))), 2))

# head anchor: bill method (primary), eye method + skull centroid
RigH_units = 73.57
anchor_bill = (tip[0] - 0.298 * H_app * axis[0], tip[1] - 0.298 * H_app * axis[1])
eye_off = (2.248 / RigH_units, -1.334 / RigH_units)
anchor_eye = (eye[0] - eye_off[0] * H_app, eye[1] - eye_off[1] * H_app)
skull = main & (dt >= 4)
skull[110:, :] = False
skull[:, :600] = False
skull &= ~(ndimage.binary_dilation(lab2 == bill_lab, np.ones((5, 5))))
sys_, sxs = np.nonzero(skull)
skull_c = (float(sxs.mean()), float(sys_.mean()))
anchor = anchor_bill
res['anchor'] = dict(
    bill_method=[round(anchor_bill[0], 1), round(anchor_bill[1], 1)],
    eye_method=[round(anchor_eye[0], 1), round(anchor_eye[1], 1)],
    skull_centroid=[round(skull_c[0], 1), round(skull_c[1], 1)],
    adopted=[round(anchor[0], 1), round(anchor[1], 1)],
    head_to_tip_px=round(float(np.hypot(tip[0] - anchor[0], tip[1] - anchor[1])), 1))

# neck centreline + breast (DT-crossing rule; DT>=40 as sensitivity)
skel = skeleton(bm)
path, sk_start = centreline_path(skel, dt, anchor)
pdts = np.array([dt[p[1], p[0]] for p in path])
mid_slice = pdts[len(pdts) // 4: 3 * len(pdts) // 4]
med_dt = float(np.median(mid_slice))
thr = max(30.0, 1.35 * med_dt)
bi = next(i for i, v in enumerate(pdts) if v > thr)
bi40 = next(i for i, v in enumerate(pdts) if v >= 40.0)
breast = path[bi]
hop = float(np.hypot(*(np.array(path[0], float) - np.array(anchor, float))))
neck_arc = arc_len(path[:bi + 1]) + hop
neck_arc40 = arc_len(path[:bi40 + 1]) + hop
res['centreline'] = dict(skel_start=[int(sk_start[0]), int(sk_start[1])],
                         n_pts=len(path), median_neck_dt=round(med_dt, 1),
                         breast_threshold_dt=round(thr, 1))
res['breast_px'] = [int(breast[0]), int(breast[1])]
res['breast_px_dt40'] = [int(path[bi40][0]), int(path[bi40][1])]
res['neck'] = dict(arc_px=round(neck_arc, 1), arc_over_H=round(neck_arc / H_app, 4),
                   arc_px_dt40=round(neck_arc40, 1),
                   arc_over_H_dt40=round(neck_arc40 / H_app, 4),
                   chord_px=round(float(np.hypot(anchor[0] - breast[0],
                                                 anchor[1] - breast[1])), 1))
# widths: 2xDT profile + perpendicular cross-sections on the neck reach
neck_path = path[:bi + 1]
samp_i = np.linspace(0, len(neck_path) - 1, 21).astype(int)
res['neck_width_profile_2xDT_px'] = [round(float(2 * dt[neck_path[i][1], neck_path[i][0]]), 1)
                                     for i in samp_i]
par = np.asarray(neck_path, float)
perp_w = []
for i in range(len(par)):
    if i < 2 or i > len(par) - 3:
        continue
    tang = par[min(i + 2, len(par) - 1)] - par[max(i - 2, 0)]
    tang = tang / max(np.hypot(*tang), 1e-9)
    nrm = np.array([-tang[1], tang[0]])
    tot = 0.0
    for sgn in (1, -1):
        k = 0
        while True:
            q = par[i] + nrm * sgn * (k + 1)
            qi = (int(round(q[0])), int(round(q[1])))
            if not (0 <= qi[0] < W and 0 <= qi[1] < H) or not bm[qi[1], qi[0]]:
                break
            k += 1
            if k > 90:
                break
        tot += k
    perp_w.append(tot)
midw = perp_w[len(perp_w) // 4: 3 * len(perp_w) // 4]
res['neck']['mid_width_perp_px'] = round(float(np.median(midw)), 1)
res['neck']['mid_width_perp_over_H'] = round(float(np.median(midw)) / H_app, 4)
res['neck']['mid_width_2xDT_px'] = round(float(np.median(
    [2 * dt[p[1], p[0]] for p in neck_path[len(neck_path) // 4: 3 * len(neck_path) // 4]])), 1)
res['centreline_pts'] = [[int(neck_path[i][0]), int(neck_path[i][1])] for i in samp_i]

# body centroid: mask minus sweep of the neck centreline (anchor ->
# breast at local DT radii), torso component by fixed filter
yy, xx = np.mgrid[0:H, 0:W]
tube = np.zeros_like(bm)
sweep_pts = [tuple(np.array(anchor))] + [tuple(p) for p in neck_path]
for p in sweep_pts:
    rr_ = dt[int(round(p[1])), int(round(p[0]))] if bm[int(round(p[1])), int(round(p[0]))] else 12.0
    tube |= ((xx - p[0]) ** 2 + (yy - p[1]) ** 2 <= rr_ ** 2)
body = bm & ~tube
lab, n = ndimage.label(body, np.ones((3, 3)))
sizes = ndimage.sum(body, lab, range(1, n + 1))
order = np.argsort(sizes)[::-1]
keep = np.zeros_like(body)
for i in order[:4]:
    comp = lab == (i + 1)
    cyy, cxx = np.nonzero(comp)
    if sizes[i] > 800 and cyy.mean() > breast[1] - 60 and cxx.mean() < breast[0] + 40:
        keep |= comp
kys, kxs = np.nonzero(keep)
res['body_centroid_px'] = [round(float(kxs.mean()), 1), round(float(kys.mean()), 1)]
res['anchor_fwd_of_body_centroid_px'] = round(anchor[0] - float(kxs.mean()), 1)
ays, axs = np.nonzero(bm)
res['approved_sil_centroid_px'] = [round(float(axs.mean()), 1), round(float(ays.mean()), 1)]

# debug overlay
ov = Image.fromarray(a.astype(np.uint8)).convert('RGB')
dr = ImageDraw.Draw(ov)
dr.line([tuple(p) for p in neck_path], fill=(255, 0, 0), width=2)
for p, col in ((anchor, (255, 0, 255)), (eye, (0, 200, 0)), (tip, (0, 0, 255)),
               (tuple(breast), (255, 165, 0)), (skull_c, (0, 255, 255))):
    dr.ellipse([p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6], outline=col, width=2)
ov.save(f'{OUT}/centreline_overlay.png')

# ---------------------------------------------------------------- rig v2
pose = RC.CHARTS['idle_hunt']().frames[0]
kp = RR2.keypoints_for(pose)
anchor_u = np.array(kp['head_c'], float)
xf, piv = R2.body_xform(pose)
st = R2.YAW_STOPS[0]
breast_design = np.array(xf((R2.BREAST_LOCAL[0] + st['ndx'], R2.BREAST_LOCAL[1])))
spine_dense, _ = R2.neck_spine(pose, breast_design)
arc_rig = float(np.hypot(*np.diff(spine_dense, axis=0).T).sum())
crown_u = anchor_u[1] - 3.15 * R2.HEAD_S
Hg_units = 88.0 - crown_u
res['rig_v2'] = dict(
    pose_hx=float(pose['hx']), pose_hy=float(pose['hy']), coil=float(pose['coil']),
    breast_units=[round(float(breast_design[0]), 2), round(float(breast_design[1]), 2)],
    anchor_units=[round(float(anchor_u[0]), 2), round(float(anchor_u[1]), 2)],
    H_units=round(float(Hg_units), 2),
    neck_arc_units=round(arc_rig, 2), neck_arc_over_H=round(arc_rig / Hg_units, 4),
    neck_chord_units=round(float(np.hypot(*(anchor_u - breast_design))), 2),
    delta_anchor_minus_breast_units=[round(float(anchor_u[0] - breast_design[0]), 2),
                                     round(float(anchor_u[1] - breast_design[1]), 2)],
    delta_over_H=[round(float((anchor_u[0] - breast_design[0]) / Hg_units), 4),
                  round(float((anchor_u[1] - breast_design[1]) / Hg_units), 4)])
res['approved_delta_anchor_minus_breast_over_H'] = [
    round((anchor[0] - breast[0]) / H_app, 4), round((anchor[1] - breast[1]) / H_app, 4)]
res['approved_delta_anchor_minus_breast_px'] = [
    round(anchor[0] - breast[0], 1), round(anchor[1] - breast[1], 1)]

# rig body centroid under the identical rule (sweep of its own dense
# spine at maskrender widths)
kpm = RR2.kp_master(pose)
scalars = dict(neck_w=float(pose['neck_w']), bulge_pos=float(pose['bulge_pos']),
               bulge_amp=float(pose['bulge_amp']), px_per_unit=RR2.U)
stack = M2.build_mask_stack(kpm, scalars, (W, H))
sil = np.any(stack > 0, axis=0)
res['rig_sil_area'] = int(sil.sum())
spine_m = np.array([RR2.mxy(p) for p in spine_dense])
tt = np.linspace(0, 1, len(spine_dense))
wdt = (6.4 - 3.0 * tt) * float(pose['neck_w']) * 1.40 * RR2.U
tube_r = np.zeros_like(sil)
for p, wv in zip(spine_m, wdt):
    tube_r |= ((xx - p[0]) ** 2 + (yy - p[1]) ** 2 <= (wv / 2) ** 2)
body_r = sil & ~tube_r
lab, n = ndimage.label(body_r, np.ones((3, 3)))
sizes = ndimage.sum(body_r, lab, range(1, n + 1))
order = np.argsort(sizes)[::-1]
breast_m = spine_m[0]
keep_r = np.zeros_like(body_r)
for i in order[:4]:
    comp = lab == (i + 1)
    cyy, cxx = np.nonzero(comp)
    if sizes[i] > 800 and cyy.mean() > breast_m[1] - 60 and cxx.mean() < breast_m[0] + 40:
        keep_r |= comp
rys, rxs = np.nonzero(keep_r)
anchor_m = np.array(RR2.mxy(anchor_u))
res['rig_body_centroid_px'] = [round(float(rxs.mean()), 1), round(float(rys.mean()), 1)]
res['rig_anchor_fwd_of_body_centroid_px'] = round(float(anchor_m[0] - rxs.mean()), 1)
res['rig_anchor_px'] = [round(float(anchor_m[0]), 1), round(float(anchor_m[1]), 1)]
res['rig_breast_px'] = [round(float(breast_m[0]), 1), round(float(breast_m[1]), 1)]
sily, silx = np.nonzero(sil)
res['rig_sil_centroid_px'] = [round(float(silx.mean()), 1), round(float(sily.mean()), 1)]

with open(f'{OUT}/approved_measurements.json', 'w') as f:
    json.dump(res, f, indent=1)
print(json.dumps(res, indent=1))
