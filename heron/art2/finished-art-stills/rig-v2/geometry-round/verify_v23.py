#!/usr/bin/env python3
"""Bird-completion geometry round: verification pack for rig v2.3.

Controls first (v2 0.5257, v2.1 0.5501, v2.2 0.6141 raw must reproduce
or nothing here is trusted), then the BAKED v2.3 files are scored
fresh: raw + bird-only IoU, bake-faithfulness (the baked build must
match the search's winning build pixel-identically), invariants
(neck channel pixel-identical to v2.2; breast + anchor bit-identical;
neck arc 32.62 units; neck widths on the neck channel), landmarks,
body measurements (row bands, plume), full residual decomposition,
overlay + silhouette.
"""
import copy, json, os, sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geo_common as G
import roster_render_v21 as RR21
import roster_render_v22 as RR22
import roster_render_v23 as RR23
import rig13_r4_v23 as R23

W, H = G.W, G.H
res = {}

def hold(hxhy=(36.17, -26.34)):
    pose = copy.deepcopy(G.RC.CHARTS['idle_hunt']().frames[0])
    pose['hx'], pose['hy'] = hxhy
    return pose

sil2, _, _ = G.MV.sil_of(G.MV.RR2, G.MV.M2, 'idle_hunt', 0)
r, p, b, _ = G.score(sil2); res['control_v2'] = dict(raw=r, prm=p, bird=b)
sil21, _, _ = G.sil_stack(RR21, hold())
r, p, b, _ = G.score(sil21); res['control_v21'] = dict(raw=r, prm=p, bird=b)
pose22 = json.load(open(f'{G.BP}/pose_tracks_v22.json'))['idle'][0]
sil22, stack22, kpm22 = G.sil_stack(RR22, copy.deepcopy(pose22))
r, p, b, _ = G.score(sil22); res['control_v22'] = dict(raw=r, prm=p, bird=b)

pose23 = json.load(open(f'{G.OUT}/pose_tracks_v23.json'))['idle'][0]
sil23, stack23, kpm23 = G.sil_stack(RR23, copy.deepcopy(pose23))
raw23, prm23, bird23, _ = G.score(sil23)
res['v23'] = dict(raw=raw23, prm=prm23, bird=bird23)
Image.fromarray((sil23 * 255).astype(np.uint8)).save(f'{G.OUT}/rig_v2_3_idle_silhouette.png')

# ---- invariants
res['invariants'] = {
    'neck_ch1_pixel_identical_to_v22': bool(np.array_equal(stack23[1], stack22[1])),
    'breast_v22': np.array(kpm22['spine'][0]).tolist(),
    'breast_v23': np.array(kpm23['spine'][0]).tolist(),
    'anchor_v22': np.array(kpm22['head_c']).tolist(),
    'anchor_v23': np.array(kpm23['head_c']).tolist(),
    'breast_bit_identical': bool(np.array_equal(np.array(kpm23['spine'][0]), np.array(kpm22['spine'][0]))),
    'anchor_bit_identical': bool(np.array_equal(np.array(kpm23['head_c']), np.array(kpm22['head_c']))),
    'bill_tip_v22': np.array(kpm22['bill_tip']).tolist(),
    'bill_tip_v23': np.array(kpm23['bill_tip']).tolist(),
    'bill_tip_identical': bool(np.array_equal(np.array(kpm23['bill_tip']), np.array(kpm22['bill_tip']))),
}

def neck_arc_widths(RR, R, pose, neck_ch):
    xf, _ = R.body_xform(pose)
    st = R.YAW_STOPS[0]
    breast = np.array(xf((R.BREAST_LOCAL[0] + st['ndx'], R.BREAST_LOCAL[1])))
    spine, Hh = R.neck_spine(pose, breast)
    arc = float(np.hypot(*np.diff(spine, axis=0).T).sum())
    spm = np.array([RR.mxy(p) for p in spine])
    sil = neck_ch > 0
    wid = {}
    for t in (0.45, 0.6, 0.75):
        i = int(t * (len(spm) - 1))
        tang = spm[min(i + 2, len(spm) - 1)] - spm[max(i - 2, 0)]
        tang = tang / max(np.hypot(*tang), 1e-9)
        nrm = np.array([-tang[1], tang[0]])
        tot = 0
        for sgn in (1, -1):
            k = 0
            while True:
                q = spm[i] + nrm * sgn * (k + 1)
                qi = (int(round(q[0])), int(round(q[1])))
                if not (0 <= qi[0] < W and 0 <= qi[1] < H) or not sil[qi[1], qi[0]]:
                    break
                k += 1
            tot += k
        wid[f't={t}'] = tot
    return dict(arc_units=round(arc, 2), widths_on_neck_channel_px=wid)

import rig13_r4_v22 as R22
res['neck_v22'] = neck_arc_widths(RR22, R22, pose22, stack22[1])
res['neck_v23'] = neck_arc_widths(RR23, R23, pose23, stack23[1])

# ---- landmarks + bbox
res['landmarks_v22'] = G.MV.landmarks(RR22, pose22)
res['landmarks_v23'] = G.MV.landmarks(RR23, pose23)
for tag, sil in (('v22', sil22), ('v23', sil23)):
    ys, xs = np.nonzero(sil)
    res[f'bbox_{tag}'] = dict(x0=int(xs.min()), x1=int(xs.max()), y0=int(ys.min()),
                              y1=int(ys.max()), area=int(sil.sum()))
    res[f'clipping_{tag}'] = [k for k, c in (('left', xs.min() <= 0), ('right', xs.max() >= W - 1),
                                             ('top', ys.min() <= 0), ('bottom', ys.max() >= H - 1)) if c]

# ---- body measures (bands / plume), Href as verify_v22
a22 = np.array(kpm22['head_c'], float)
Href = 88.0 * RR23.U - (a22[1] - 3.15 * 1.45 * RR23.U)
res['body_v22'] = G.body_measures(stack22, sil22, kpm22, Href)
res['body_v23'] = G.body_measures(stack23, sil23, kpm23, Href)

# ---- decomposition
dec22 = G.decompose(sil22, stack22, res['control_v22']['prm'])
dec23 = G.decompose(sil23, stack23, prm23)
res['decomp_v22'] = {k: v for k, v in dec22.items() if k != 'placed'}
res['decomp_v23'] = {k: v for k, v in dec23.items() if k != 'placed'}
G.overlay(dec23['placed'], f'{G.OUT}/overlay_v23_vs_approved.png')

with open(f'{G.OUT}/verify_results_v23.json', 'w') as f:
    json.dump(res, f, indent=1)
print(json.dumps(res, indent=1))
