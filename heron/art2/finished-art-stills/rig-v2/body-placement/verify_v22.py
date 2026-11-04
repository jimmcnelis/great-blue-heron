#!/usr/bin/env python3
"""Body-placement round: verification pack for rig v2.2.

Controls first (v2 must read 0.5257, v2.1 0.5501 under the certified
protocol or nothing here is trusted), then the baked v2.2 files are
scored fresh, invariants asserted (neck/head channels pixel-identical
to v2.1; breast + anchor unmoved; neck arc/widths unchanged), the
full landmark re-check runs, body measurements are repeated with the
measure_body2 instruments, and the residual is decomposed two ways:
miss by approved-side zone, extra by rig channel.
"""
import copy, json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

HOME = os.path.expanduser('~')
ART2 = f'{HOME}/workspace/heron/art2'
FS = f'{ART2}/finished-art-stills'
RIGV2 = f'{FS}/rig-v2'
OUT = f'{RIGV2}/body-placement'
HA = f'{RIGV2}/head-anchor'
sys.path.insert(0, ART2)
sys.path.insert(0, f'{HOME}/workspace/heron/src13')
sys.path.insert(0, f'{FS}/refinish-corpus/work')
sys.path.insert(0, f'{RIGV2}/work')
import measure_v2 as MV
import roster_charts as RC
import roster_render_v21 as RR21
import roster_render_v22 as RR22
import maskrender_v2 as M2

W, H = 1024, 600
U = RR22.U
rest = np.asarray(Image.open(f'{RIGV2}/masks/approved_rest_mask.png')) > 0
res = {}

def sil_stack(RR, pose):
    kpm = RR.kp_master(pose)
    scalars = dict(neck_w=float(pose['neck_w']), bulge_pos=float(pose['bulge_pos']),
                   bulge_amp=float(pose['bulge_amp']), px_per_unit=RR.U)
    stack = M2.build_mask_stack(kpm, scalars, (W, H))
    return np.any(stack > 0, axis=0), stack, kpm

def hold_pose(hxhy=(36.17, -26.34)):
    pose = copy.deepcopy(RC.CHARTS['idle_hunt']().frames[0])
    pose['hx'], pose['hy'] = hxhy
    return pose

# ---- controls
sil2, _, _ = MV.sil_of(MV.RR2, MV.M2, 'idle_hunt', 0)
res['control_v2'] = MV.aligned_iou(rest, sil2)
pose21 = hold_pose()
sil21, stack21, kpm21 = sil_stack(RR21, pose21)
res['control_v21'] = MV.aligned_iou(rest, sil21)

# ---- v2.2 from the baked files + track
tracks = json.load(open(f'{OUT}/pose_tracks_v22.json'))
pose22 = tracks['idle'][0]
sil22, stack22, kpm22 = sil_stack(RR22, pose22)
iou22, prm22 = MV.aligned_iou(rest, sil22)
res['v22_mask_iou'] = (iou22, prm22)
Image.fromarray((sil22 * 255).astype(np.uint8)).save(f'{OUT}/rig_v2_2_idle_silhouette.png')

# ---- invariants
res['channel_identity_vs_v21'] = {
    'neck_ch1_identical': bool(np.array_equal(stack22[1], stack21[1])),
    'head_ch2_identical': bool(np.array_equal(stack22[2], stack21[2]))}
b21 = np.array(kpm21['spine'][0], float); b22 = np.array(kpm22['spine'][0], float)
a21 = np.array(kpm21['head_c'], float); a22 = np.array(kpm22['head_c'], float)
res['endpoints'] = {'breast_v21': b21.tolist(), 'breast_v22': b22.tolist(),
                    'anchor_v21': a21.tolist(), 'anchor_v22': a22.tolist(),
                    'delta_anchor_minus_breast_v21': (a21 - b21).tolist(),
                    'delta_anchor_minus_breast_v22': (a22 - b22).tolist()}

def neck_metrics(RR, R, pose, sil):
    xf, _ = R.body_xform(pose)
    st = R.YAW_STOPS[0]
    breast = np.array(xf((R.BREAST_LOCAL[0] + st['ndx'], R.BREAST_LOCAL[1])))
    spine, Hh = R.neck_spine(pose, breast)
    arc = float(np.hypot(*np.diff(spine, axis=0).T).sum())
    spm = np.array([RR.mxy(p) for p in spine])
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
    return dict(arc_units=round(arc, 2), widths_px=wid)

import rig13_r4_v21 as R21
import rig13_r4_v22 as R22
res['neck_v21'] = neck_metrics(RR21, R21, pose21, sil21)
res['neck_v22'] = neck_metrics(RR22, R22, pose22, sil22)

# ---- landmarks
res['landmarks_v21'] = MV.landmarks(RR21, pose21)
res['landmarks_v22'] = MV.landmarks(RR22, pose22)
for tag, sil in (('v21', sil21), ('v22', sil22)):
    ys, xs = np.nonzero(sil)
    res[f'bbox_{tag}'] = dict(x0=int(xs.min()), x1=int(xs.max()), y0=int(ys.min()),
                              y1=int(ys.max()), area=int(sil.sum()))
    res[f'clipping_{tag}'] = [k for k, c in (('left', xs.min() <= 0), ('right', xs.max() >= W - 1),
                                             ('top', ys.min() <= 0), ('bottom', ys.max() >= H - 1)) if c]

# ---- body measurements (measure_body2 instruments)
def seg_dist(shape, a, b):
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]]
    a = np.asarray(a, float); b = np.asarray(b, float)
    d = b - a; L2 = float(d @ d)
    t = np.clip(((xx - a[0]) * d[0] + (yy - a[1]) * d[1]) / L2, 0, 1)
    return np.hypot(xx - (a[0] + t * d[0]), yy - (a[1] + t * d[1]))

def runs_at(mask, y, xwin, maxw=30):
    row = mask[y, xwin[0]:xwin[1]]
    out, x = [], 0
    while x < len(row):
        if row[x]:
            x0 = x
            while x < len(row) and row[x]:
                x += 1
            if x - x0 <= maxw:
                out.append((x0 + xwin[0] + (x - 1 + xwin[0])) / 2.0)
        else:
            x += 1
    return out

def track_legs(mask, y_start, y_stop, xwin):
    tracks = [dict(pts={y_start: cx}) for cx in runs_at(mask, y_start, xwin)]
    for tr in tracks:
        tr['alive'] = True
    for y in range(y_start - 1, y_stop - 1, -1):
        runs = runs_at(mask, y, xwin)
        for tr in tracks:
            if not tr['alive']:
                continue
            last = tr['pts'][min(tr['pts'])]
            cand = [r for r in runs if abs(r - last) <= 7]
            if cand:
                tr['pts'][y] = min(cand, key=lambda r: abs(r - last))
            else:
                tr['alive'] = False
    return [tr['pts'] for tr in tracks if len(tr['pts']) >= 110]

def leg_summary(pts, Href, B):
    ys = sorted(pts)
    top_y, bot_y = min(ys), max(ys)
    return dict(hip_minus_breast_over_H=[round(float((pts[top_y] - B[0]) / Href), 4),
                                         round(float((top_y - B[1]) / Href), 4)],
                foot_minus_breast_over_H=[round(float((pts[bot_y] - B[0]) / Href), 4),
                                          round(float((bot_y - B[1]) / Href), 4)])

def body_measures(stack, sil, kpm, Href):
    Br = np.array(kpm['spine'][0], float)
    torso_ch = (stack[0] > 0) | (stack[3] > 0) | (stack[6] > 0)
    s = Href / 562.0
    core = torso_ch & (ndimage.distance_transform_edt(torso_ch) >= 13 * s)
    ys, xs = np.nonzero(core)
    out = {'torso_core_centroid_minus_breast_over_H':
           [round(float((xs.mean() - Br[0]) / Href), 4), round(float((ys.mean() - Br[1]) / Href), 4)]}
    y0, y1 = ys.min(), ys.max()
    bands = {}
    for i, (lo, hi) in enumerate(((0.0, 1 / 3), (1 / 3, 2 / 3), (2 / 3, 1.0))):
        m = core[int(y0 + lo * (y1 - y0)):int(y0 + hi * (y1 - y0)) + 1, :]
        bands[f'band{i}'] = round(float(m.sum() / core.sum()), 4)
    out['torso_core_row_bands'] = bands
    plume = stack[7] > 0
    pys, pxs = np.nonzero(plume)
    out['plume'] = dict(
        centroid_minus_breast_over_H=[round(float((pxs.mean() - Br[0]) / Href), 4),
                                      round(float((pys.mean() - Br[1]) / Href), 4)],
        drop_max_over_H=round(float((pys.max() - Br[1]) / Href), 4),
        drop_p95_over_H=round(float((np.percentile(pys, 95) - Br[1]) / Href), 4))
    tracks = track_legs(sil, 548, 280, (40, 560))
    out['legs_silhouette'] = [leg_summary(t, Href, Br) for t in tracks]
    out['legs_kp'] = {}
    for nm in ('n', 'f'):
        hip = np.array(kpm[f'hip_{nm}'], float); foot = np.array(kpm[f'foot_{nm}'], float)
        out['legs_kp'][nm] = dict(
            hip_minus_breast_over_H=[round(float((hip[0] - Br[0]) / Href), 4),
                                     round(float((hip[1] - Br[1]) / Href), 4)],
            foot_minus_breast_over_H=[round(float((foot[0] - Br[0]) / Href), 4),
                                      round(float((foot[1] - Br[1]) / Href), 4)])
    return out

Hrig = 88.0 * U - (a21[1] - 3.15 * 1.45 * U)
res['body_v21'] = body_measures(stack21, sil21, kpm21, Hrig)
res['body_v22'] = body_measures(stack22, sil22, kpm22, Hrig)

# ---- decomposition: miss by approved zone, extra by rig channel
def placed_mask(target, src, prm):
    Mc = ndimage.center_of_mass(target)
    S0 = ndimage.rotate(src.astype(float), prm['rot'], reshape=False, order=1) > 0.5
    sy, sx = np.nonzero(S0)
    crop = S0[sy.min():sy.max() + 1, sx.min():sx.max() + 1].astype(float)
    z = ndimage.zoom(crop, float(prm['scale']), order=1) > 0.5
    zh, zw = z.shape
    top = int(round(Mc[0] - zh / 2 + prm['dy'])); left = int(round(Mc[1] - zw / 2 + prm['dx']))
    canvas = np.zeros_like(target)
    ys0, ys1 = max(0, top), min(H, top + zh); xs0, xs1 = max(0, left), min(W, left + zw)
    canvas[ys0:ys1, xs0:xs1] = z[ys0 - top:ys1 - top, xs0 - left:xs1 - left]
    return canvas

def placed_stack(stack, prm):
    return np.stack([placed_mask(rest, stack[i] > 0, prm) for i in range(8)])

B = np.array([565.0, 221.0]); A = np.array([660.8, 53.3]); TIP = np.array([828.0, 63.0])
yy, xx = np.mgrid[0:600, 0:1024]
neck_zone = seg_dist(rest.shape, B, A) < 50
head_zone = (np.hypot(xx - A[0], yy - A[1]) < 0.20 * 562.0) | (seg_dist(rest.shape, A, TIP) < 15)
plume_a = np.load(f'{OUT}/approved_plume_strands.npy')
leg_a = np.load(f'{OUT}/approved_leg_mask.npy')
zones = {}
zones['head'] = head_zone
zones['neck'] = neck_zone & ~head_zone
zones['legs'] = ndimage.binary_dilation(leg_a, iterations=8) & ~zones['head'] & ~zones['neck']
zones['plume'] = ndimage.binary_dilation(plume_a, iterations=8) & ~zones['legs'] & ~zones['neck'] & ~zones['head']
scen = np.zeros_like(rest); scen[558:, :] = True
zones['scenery'] = scen & ~zones['legs'] & ~zones['plume'] & ~zones['neck'] & ~zones['head']
used = np.zeros_like(rest)
for z in zones.values():
    used |= z
zones['torso_rest'] = ~used
CH = ['torso', 'neck', 'head', 'wing', 'leg_near', 'leg_far', 'tail', 'plume']

def decompose(sil, stack, prm):
    placed = placed_mask(rest, sil, prm)
    pstack = placed_stack(stack, prm)
    miss = rest & ~placed; extra = placed & ~rest
    dz = {}
    for name, z in zones.items():
        dz[name] = dict(approved=int((rest & z).sum()), miss=int((miss & z).sum()),
                        extra=int((extra & z).sum()))
    dch = {}
    for i, nm in enumerate(CH):
        pm = pstack[i] > 0
        dch[nm] = dict(placed=int(pm.sum()), extra=int((pm & ~rest).sum()))
    bird = np.ones_like(rest); bird[558:, :] = False
    iou_bird = float(((rest & placed & bird).sum()) / max(((rest | placed) & bird).sum(), 1))
    return dict(total=dict(miss=int(miss.sum()), extra=int(extra.sum()),
                           inter=int((rest & placed).sum()), union=int((rest | placed).sum())),
                by_zone=dz, by_channel=dch, iou_excluding_scenery_band=round(iou_bird, 4),
                placed=placed)

dec21 = decompose(sil21, stack21, res['control_v21'][1])
dec22 = decompose(sil22, stack22, prm22)
res['decomp_v21'] = {k: v for k, v in dec21.items() if k != 'placed'}
res['decomp_v22'] = {k: v for k, v in dec22.items() if k != 'placed'}

def overlay(target, placed, path):
    img = np.ones((H, W, 3), np.uint8) * 255
    img[target & placed] = (255, 200, 0)
    img[target & ~placed] = (230, 40, 30)
    img[placed & ~target] = (40, 90, 220)
    Image.fromarray(img).save(path)

overlay(rest, dec22['placed'], f'{OUT}/overlay_v22_vs_approved.png')

with open(f'{OUT}/verify_results.json', 'w') as f:
    json.dump(res, f, indent=1)
print(json.dumps(res, indent=1))
