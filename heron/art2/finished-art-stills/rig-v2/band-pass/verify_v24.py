#!/usr/bin/env python3
"""Band pass: verification pack for the BAKED rig v2.4.

Controls anchor (v2.3 baked must still read 0.7121 / 0.7656), then
the baked v2.4 files scored fresh: raw + bird-only IoU, band surface,
invariants (neck channel pixel-identical to v2.2; breast + anchor +
bill tip bit-identical; neck arc + widths), landmarks, full residual
decomposition, overlay + silhouette.
"""
import copy, json, os, sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import band_core as B
import geo_common as G
import roster_render_v22 as RR22
import roster_render_v23 as RR23
import roster_render_v24 as RR24
import rig13_r4_v22 as R22
import rig13_r4_v24 as R24

W, H = G.W, G.H
res = {}

pose22 = json.load(open(f'{G.BP}/pose_tracks_v22.json'))['idle'][0]
sil22, stack22, kpm22 = G.sil_stack(RR22, copy.deepcopy(pose22))
pose23 = json.load(open(f'{B.GEO}/pose_tracks_v23.json'))['idle'][0]
sil23, stack23, kpm23 = G.sil_stack(RR23, copy.deepcopy(pose23))
r, p, b, _ = G.score(sil23)
res['control_v23'] = dict(raw=r, prm=p, bird=b)
assert abs(r - 0.7121) < 0.001 and abs(b - 0.7656) < 0.001, 'v2.3 anchor moved'

pose24 = json.load(open(f'{B.OUT}/pose_tracks_v24.json'))['idle'][0]
sil24, stack24, kpm24 = G.sil_stack(RR24, copy.deepcopy(pose24))
raw24, prm24, bird24, _ = G.score(sil24)
res['v24'] = dict(raw=raw24, prm=prm24, bird=bird24)
Image.fromarray((sil24 * 255).astype(np.uint8)).save(f'{B.OUT}/rig_v2_4_idle_silhouette.png')

res['invariants'] = {
    'neck_ch1_pixel_identical_to_v22': bool(np.array_equal(stack24[1], stack22[1])),
    'neck_ch1_pixel_identical_to_v23': bool(np.array_equal(stack24[1], stack23[1])),
    'head_ch2_pixel_identical_to_v23': bool(np.array_equal(stack24[2], stack23[2])),
    'plume_ch7_pixel_identical_to_v23': bool(np.array_equal(stack24[7], stack23[7])),
    'breast_bit_identical': bool(np.array_equal(np.array(kpm24['spine'][0]), np.array(kpm22['spine'][0]))),
    'anchor_bit_identical': bool(np.array_equal(np.array(kpm24['head_c']), np.array(kpm22['head_c']))),
    'bill_tip_identical': bool(np.array_equal(np.array(kpm24['bill_tip']), np.array(kpm22['bill_tip']))),
    'breast_v24': np.array(kpm24['spine'][0]).tolist(),
    'anchor_v24': np.array(kpm24['head_c']).tolist(),
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

res['neck_v24'] = neck_arc_widths(RR24, R24, pose24, stack24[1])
res['landmarks_v23'] = G.MV.landmarks(RR23, pose23)
res['landmarks_v24'] = G.MV.landmarks(RR24, pose24)
res['body_v23'] = B.band_metrics(stack23, sil23, kpm23, pose23)
res['body_v24'] = B.band_metrics(stack24, sil24, kpm24, pose24)
for tag, sil in (('v23', sil23), ('v24', sil24)):
    ys, xs = np.nonzero(sil)
    res[f'bbox_{tag}'] = dict(x0=int(xs.min()), x1=int(xs.max()), y0=int(ys.min()),
                              y1=int(ys.max()), area=int(sil.sum()))
dec23 = G.decompose(sil23, stack23, res['control_v23']['prm'])
dec24 = G.decompose(sil24, stack24, prm24)
res['decomp_v23'] = {k: v for k, v in dec23.items() if k != 'placed'}
res['decomp_v24'] = {k: v for k, v in dec24.items() if k != 'placed'}
G.overlay(dec24['placed'], f'{B.OUT}/overlay_v24_vs_approved.png')

def _np_default(o):
    if isinstance(o, (np.bool_,)): return bool(o)
    if isinstance(o, (np.floating,)): return float(o)
    if isinstance(o, (np.integer,)): return int(o)
    raise TypeError(str(type(o)))
with open(f'{B.OUT}/verify_results_v24.json', 'w') as f:
    json.dump(res, f, indent=1, default=_np_default)
print(json.dumps(res, indent=1, default=_np_default))
