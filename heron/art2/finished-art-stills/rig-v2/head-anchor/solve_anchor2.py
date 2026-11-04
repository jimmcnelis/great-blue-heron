#!/usr/bin/env python3
"""Stage 2: chord-frame neck fit + finalist re-judging + final pack.

Stage 1 (solve_anchor.py) adopted the anatomical anchor but its
world-frame Bezier neck made the measured length only by bowing
~2x deeper than the approved S (chord RMS 0.202, visible in the
stage-1 overlay). rig13_r4_v21 now places neck controls in the
chord frame; this stage tunes (T1, K1, T2, K2) per candidate anchor
(arc-length law as a hard +-1% constraint, then min chord RMS),
re-judges the stage-1 finalists under the full identical protocol,
regenerates the final verification pack, and bakes the winning
neck constants into rig13_r4_v21.py.
"""
import json, os, re, sys, copy
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HOME = os.path.expanduser('~')
ART2 = f'{HOME}/workspace/heron/art2'
FS = f'{ART2}/finished-art-stills'
RIGV2 = f'{FS}/rig-v2'
OUT = f'{RIGV2}/head-anchor'
sys.path.insert(0, ART2)
sys.path.insert(0, f'{HOME}/workspace/heron/src13')
sys.path.insert(0, f'{FS}/refinish-corpus/work')
sys.path.insert(0, f'{RIGV2}/work')
sys.path.insert(0, OUT)
import measure_v2 as MV
import roster_charts as RC
import roster_render_v21 as RR21
import rig13_r4_v21 as R21
import maskrender_v2 as M2

W, H = 1024, 600
res = {}
meas = json.load(open(f'{OUT}/approved_measurements.json'))
stage1 = json.load(open(f'{OUT}/solve_results.json'))
rest = np.asarray(Image.open(f'{RIGV2}/masks/approved_rest_mask.png')) > 0
base_pose = RC.CHARTS['idle_hunt']().frames[0]
Href = meas['rig_v2']['H_units']
arc_target = meas['neck']['arc_over_H'] * Href
hx0 = stage1['anatomical']['hx']
hy0 = stage1['anatomical']['hy']

app_samples = np.array(meas['centreline_pts'], float)
app_path = np.concatenate([app_samples[::-1], [np.array(meas['anchor']['adopted'])]])
breast_app = np.array(meas['breast_px'], float)
anchor_app = np.array(meas['anchor']['adopted'], float)


def resample_by_arc(pts, n=40):
    pts = np.asarray(pts, float)
    seg = np.hypot(*np.diff(pts, axis=0).T)
    s = np.concatenate([[0], np.cumsum(seg)])
    t = np.linspace(0, s[-1], n)
    return np.stack([np.interp(t, s, pts[:, 0]), np.interp(t, s, pts[:, 1])], axis=1), s[-1]


def chord_frame(pts, B, A):
    d = np.asarray(A, float) - np.asarray(B, float)
    L = np.hypot(*d)
    ua = d / L
    va = np.array([-ua[1], ua[0]])
    rel = np.asarray(pts, float) - np.asarray(B, float)
    return np.stack([rel @ ua / L, rel @ va / L], axis=1)


app_rs, _ = resample_by_arc(app_path)
app_cf = chord_frame(app_rs, breast_app, anchor_app)


def rig_spine(hx, hy):
    pose = copy.deepcopy(base_pose)
    pose['hx'], pose['hy'] = float(hx), float(hy)
    xf, _piv = R21.body_xform(pose)
    st = R21.YAW_STOPS[0]
    breast = np.array(xf((R21.BREAST_LOCAL[0] + st['ndx'], R21.BREAST_LOCAL[1])))
    spine, Hh = R21.neck_spine(pose, breast)
    return spine, breast, Hh


def spine_metrics(spine, breast, anchor):
    rs, arc = resample_by_arc(spine)
    cf = chord_frame(rs, breast, anchor)
    rms = float(np.sqrt((((cf - app_cf) ** 2).sum(axis=1)).mean()))
    tang = np.diff(np.asarray(spine, float), axis=0)
    ang = np.arctan2(tang[:, 1], tang[:, 0])
    dang = np.abs(np.diff(np.unwrap(ang)))
    return arc, rms, float(np.degrees(dang).max())


def set_neck(t1, k1, t2, k2):
    R21.NECK_T1, R21.NECK_K1, R21.NECK_T2, R21.NECK_K2 = t1, k1, t2, k2


def _eval_neck(hx, hy, prm):
    set_neck(*prm)
    sp, br, an = rig_spine(hx, hy)
    arc, rms, mx = spine_metrics(sp, br, an)
    return (abs(arc - arc_target) / arc_target, rms, mx, prm, arc)


def tune_neck2(hx, hy):
    """Coarse grid -> pattern search. Feasibility (arc err <= 1%)
    is a hard gate when reachable; score inside the gate is RMS."""
    cands = []
    for t1 in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6):
        for k1 in (-0.36, -0.28, -0.20, -0.12, -0.04, 0.04):
            for t2 in (0.05, 0.15, 0.25, 0.35, 0.45):
                for k2 in (-0.40, -0.32, -0.24, -0.16, -0.08, 0.0):
                    cands.append(_eval_neck(hx, hy, (t1, k1, t2, k2)))
    ok = [c for c in cands if c[0] <= 0.01]
    if ok:
        best = min(ok, key=lambda c: c[1])
    else:
        best = min(cands, key=lambda c: c[0] * 3 + c[1])

    def better(c, b):
        if c[0] <= 0.01 and b[0] <= 0.01:
            return c[1] < b[1]
        if c[0] <= 0.01 < b[0]:
            return True
        if b[0] <= 0.01 < c[0]:
            return False
        return c[0] * 3 + c[1] < b[0] * 3 + b[1]

    for step_t, step_k in ((0.04, 0.03), (0.02, 0.015), (0.01, 0.008), (0.005, 0.004)):
        improved = True
        while improved:
            improved = False
            t1, k1, t2, k2 = best[3]
            for dt1 in (-step_t, 0, step_t):
                for dk1 in (-step_k, 0, step_k):
                    for dt2 in (-step_t, 0, step_t):
                        for dk2 in (-step_k, 0, step_k):
                            if dt1 == dk1 == dt2 == dk2 == 0:
                                continue
                            c = _eval_neck(hx, hy, (t1 + dt1, k1 + dk1,
                                                    t2 + dt2, k2 + dk2))
                            if better(c, best):
                                best = c
                                improved = True
    set_neck(*best[3])
    return dict(params=dict(zip(('T1', 'K1', 'T2', 'K2'), [round(v, 3) for v in best[3]])),
                arc_units=round(best[4], 2),
                arc_err_pct=round((best[4] - arc_target) / arc_target * 100, 2),
                chord_rms=round(best[1], 4), max_tangent_step_deg=round(best[2], 1))


def sil_for(hx, hy):
    pose = copy.deepcopy(base_pose)
    pose['hx'], pose['hy'] = float(hx), float(hy)
    kpm = RR21.kp_master(pose)
    scalars = dict(neck_w=float(pose['neck_w']), bulge_pos=float(pose['bulge_pos']),
                   bulge_amp=float(pose['bulge_amp']), px_per_unit=RR21.U)
    stack = M2.build_mask_stack(kpm, scalars, (W, H))
    return np.any(stack > 0, axis=0), pose, kpm


# finalists from stage 1 (anatomical + top locals), each with its
# own tuned neck
finalists = [(hx0, hy0, 'anatomical')]
for key in stage1['full_protocol_finalists']:
    fx, fy = (float(v) for v in key.split(','))
    if abs(fx - hx0) > 0.01 or abs(fy - hy0) > 0.01:
        finalists.append((fx, fy, 'local'))
res['finalists'] = {}
tunes = {}
for fx, fy, tag in finalists:
    tunes[(fx, fy)] = tune_neck2(fx, fy)
    s, _, _ = sil_for(fx, fy)
    iou = MV.aligned_iou(rest, s)
    res['finalists'][f'{fx},{fy}'] = dict(tag=tag, iou=iou[0], params=iou[1],
                                          neck=tunes[(fx, fy)])
ana = res['finalists'][f'{hx0},{hy0}']
best_key = max(res['finalists'], key=lambda k: res['finalists'][k]['iou'])
fx, fy = (float(v) for v in best_key.split(','))
adopt_local = ((fx, fy) != (hx0, hy0)
               and res['finalists'][best_key]['iou'] >= ana['iou'] + 0.02
               and abs(tunes[(fx, fy)]['arc_err_pct']) <= 1.5
               and tunes[(fx, fy)]['chord_rms'] <= tunes[(hx0, hy0)]['chord_rms'] * 1.25)
final_hx, final_hy = (fx, fy) if adopt_local else (hx0, hy0)
final_tune = tunes[(final_hx, final_hy)]
set_neck(*[final_tune['params'][k] for k in ('T1', 'K1', 'T2', 'K2')])
res['decision'] = dict(adopted='local_best' if adopt_local else 'anatomical',
                       hx=final_hx, hy=final_hy,
                       mask_iou=res['finalists'][f'{final_hx},{final_hy}']['iou'],
                       stage1_mask_iou_same_anchor=stage1['decision']['mask_iou'],
                       v2_mask_iou_same_protocol=stage1['certification']['mask_iou_v2_reproduced'][0])

# ------------------------------------------------ final pack
sil_f, pose_f, kpm_f = sil_for(final_hx, final_hy)
Image.fromarray((sil_f * 255).astype(np.uint8)).save(f'{OUT}/rig_v2_1_idle_silhouette.png')
res['final_mask_iou_recheck'] = MV.aligned_iou(rest, sil_f)
res['landmarks_v21'] = MV.landmarks(RR21, pose_f)
ys, xs = np.nonzero(sil_f)
res['final_sil_bbox'] = dict(x0=int(xs.min()), x1=int(xs.max()),
                             y0=int(ys.min()), y1=int(ys.max()), area=int(sil_f.sum()))
res['final_clipping'] = [k for k, c in (('left', xs.min() <= 0), ('right', xs.max() >= W - 1),
                                        ('top', ys.min() <= 0), ('bottom', ys.max() >= H - 1)) if c]
spine, breast_r, anchor_r = rig_spine(final_hx, final_hy)
arc_d, rms_f, mx_f = spine_metrics(spine, breast_r, anchor_r)
sp5 = np.array(kpm_f['spine'], float)
arc_poly = float(np.hypot(*np.diff(sp5, axis=0).T).sum()) / RR21.U
crown_u = anchor_r[1] - 3.15 * R21.HEAD_S
Hg_new = 88.0 - crown_u
res['final_neck'] = dict(arc_dense_units=round(arc_d, 2),
                         arc_dense_over_H=round(arc_d / Hg_new, 4),
                         arc_polyline_units=round(arc_poly, 2),
                         arc_polyline_over_H=round(arc_poly / Hg_new, 4),
                         chord_rms=round(rms_f, 4), max_tangent_step_deg=round(mx_f, 1),
                         H_units_new=round(Hg_new, 2), tune=final_tune)
spm = np.array([RR21.mxy(p) for p in spine])
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
            if not (0 <= qi[0] < W and 0 <= qi[1] < H) or not sil_f[qi[1], qi[0]]:
                break
            k += 1
        tot += k
    wid[f't={t}'] = tot
res['final_neck']['silhouette_widths_px'] = wid
res['final_neck']['silhouette_widths_over_H'] = {
    k: round(v / (Hg_new * RR21.U), 4) for k, v in wid.items()}


def placed_mask(target, src, prm):
    Mc = ndimage.center_of_mass(target)
    S0 = ndimage.rotate(src.astype(float), prm['rot'], reshape=False, order=1) > 0.5
    sy, sx = np.nonzero(S0)
    crop = S0[sy.min():sy.max() + 1, sx.min():sx.max() + 1].astype(float)
    z = ndimage.zoom(crop, float(prm['scale']), order=1) > 0.5
    zh, zw = z.shape
    top = int(round(Mc[0] - zh / 2 + prm['dy']))
    left = int(round(Mc[1] - zw / 2 + prm['dx']))
    canvas = np.zeros_like(target)
    ys0, ys1 = max(0, top), min(H, top + zh)
    xs0, xs1 = max(0, left), min(W, left + zw)
    canvas[ys0:ys1, xs0:xs1] = z[ys0 - top:ys1 - top, xs0 - left:xs1 - left]
    return canvas


def overlay(target, placed, path):
    img = np.ones((H, W, 3), np.uint8) * 255
    img[target & placed] = (255, 200, 0)
    img[target & ~placed] = (230, 40, 30)
    img[placed & ~target] = (40, 90, 220)
    Image.fromarray(img).save(path)


prm_f = res['final_mask_iou_recheck'][1]
overlay(rest, placed_mask(rest, sil_f, prm_f), f'{OUT}/overlay_v21_vs_approved.png')

# neck-shape visual: rig spine mapped into the approved frame
# (translate to the approved breast, scale by H ratio; chord angles
# agree by construction of the transplant)
a_img = Image.open(f'{FS}/audubon_rest.png').convert('RGB')
dr = ImageDraw.Draw(a_img)
dr.line([tuple(p) for p in app_path], fill=(255, 0, 0), width=2)
scale = float(meas['approved_H']['H_px']) / (Hg_new * RR21.U)
spm_u = spine                                     # design units
mapped = breast_app + (spm_u - breast_r) * RR21.U * scale
dr.line([tuple(p) for p in mapped], fill=(30, 90, 255), width=2)
a_img.save(f'{OUT}/neck_shape_overlay.png')
res['final_pose'] = {k: pose_f[k] for k in ('root_x', 'root_y', 'body_tilt', 'hx', 'hy',
                                            'coil', 'neck_w', 'head_pitch', 'yaw')}

# bake the winning neck constants into rig13_r4_v21.py
p = final_tune['params']
path_rig = f'{HOME}/workspace/heron/src13/rig13_r4_v21.py'
src = open(path_rig).read()
src = re.sub(r'NECK_T1, NECK_K1 = [^\n]+', f"NECK_T1, NECK_K1 = {p['T1']}, {p['K1']}", src)
src = re.sub(r'NECK_T2, NECK_K2 = [^\n]+', f"NECK_T2, NECK_K2 = {p['T2']}, {p['K2']}", src)
open(path_rig, 'w').write(src)
res['baked_neck_constants'] = p

with open(f'{OUT}/solve_results2.json', 'w') as f:
    json.dump(res, f, indent=1)
print(json.dumps(res, indent=1))
