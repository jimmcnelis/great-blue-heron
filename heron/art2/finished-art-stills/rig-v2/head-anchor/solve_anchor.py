#!/usr/bin/env python3
"""Head-anchor surgery: solve (hx, hy) + neck-curve offsets for the
idle hold, re-measure proof (1) under Phase B's IDENTICAL protocol
(measure_v2.aligned_iou, unchanged).

Steps:
 0. Certification: aligned_iou(approved_rest, saved rig-v2 idle
    silhouette) must reproduce Phase B's 0.5324. Canvas-threshold
    forensics: find the luminance threshold pair that reproduces
    Phase B's canvas range 0.465-0.491 on the EXISTING v2 canvas.
 1. Anatomical anchor: (hx, hy) placing the rig anchor at the
    approved anchor's breast-relative offset (H fractions x the
    rig's H). Neck offsets tuned so the dense Bezier neck hits the
    approved measured arc length AND traces the approved centreline
    (chord-frame RMS), no kinks.
 2. Local IoU search around the anatomical anchor (fast pre-score,
    full identical protocol on finalists). Adoption rule: local
    best only if it beats anatomical by >= 0.02 on the full
    protocol AND its retuned neck still meets length (+-1.5%) and
    shape (RMS <= 1.25x anatomical's).
 3. Final verification: landmarks (measure_v2.landmarks) + neck arc
    (dense + conditioning polyline), silhouette neck widths,
    clipping, overlays. Writes solve_results.json.
"""
import json, os, sys, copy
import numpy as np
from PIL import Image
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
import gate
import measure_v2 as MV
import roster_charts as RC
import roster_render_v21 as RR21
import rig13_r4_v21 as R21
import maskrender_v2 as M2

W, H = 1024, 600
res = {}
meas = json.load(open(f'{OUT}/approved_measurements.json'))
rest = np.asarray(Image.open(f'{RIGV2}/masks/approved_rest_mask.png')) > 0
base_pose = RC.CHARTS['idle_hunt']().frames[0]


def sil_for(hx, hy, pose_out=None):
    pose = copy.deepcopy(base_pose)
    pose['hx'], pose['hy'] = float(hx), float(hy)
    kpm = RR21.kp_master(pose)
    scalars = dict(neck_w=float(pose['neck_w']), bulge_pos=float(pose['bulge_pos']),
                   bulge_amp=float(pose['bulge_amp']), px_per_unit=RR21.U)
    stack = M2.build_mask_stack(kpm, scalars, (W, H))
    if pose_out is not None:
        pose_out.update(pose=pose, kpm=kpm)
    return np.any(stack > 0, axis=0), pose, kpm


# ---------------------------------------------------------- 0. certify
v2sil = np.asarray(Image.open(f'{RIGV2}/masks/rig_v2_idle_silhouette.png')) > 0
cert = MV.aligned_iou(rest, v2sil)
res['certification'] = dict(mask_iou_v2_reproduced=cert,
                            phaseB_value=0.5324)


def canvas_mask(path, T):
    a = np.asarray(Image.open(path).convert('RGB'), dtype=np.float32)
    m = a.mean(axis=2) < T
    lab, n = ndimage.label(m, np.ones((3, 3)))
    if n == 0:
        return m
    sizes = ndimage.sum(m, lab, range(1, n + 1))
    big = 1 + int(np.argmax(sizes))
    keep = lab == big
    dil = ndimage.binary_dilation(keep, np.ones((11, 11)))
    for i in range(1, n + 1):
        if i != big and sizes[i - 1] >= 200 and np.any((lab == i) & dil):
            keep |= lab == i
    return keep


probe = {}
for T in (220, 200, 180, 160, 128):
    probe[T] = MV.aligned_iou(rest, canvas_mask(f'{RIGV2}/canvas/idle_hold.png', T))[0]
res['canvas_threshold_probe_v2canvas'] = {str(k): round(v, 4) for k, v in probe.items()}
res['phaseB_canvas_range'] = [0.465, 0.491]

# ------------------------------------------------- 1. anatomical anchor
Href = meas['rig_v2']['H_units']                       # 73.57
dApp = meas['approved_delta_anchor_minus_breast_over_H']
breast_u = np.array(meas['rig_v2']['breast_units'])
anchor_t = breast_u + np.array(dApp) * Href
hx0 = float(anchor_t[0] - base_pose['root_x'])
hy0 = float(anchor_t[1] - (R21.HIP_Y + base_pose['root_y']))
arc_target = meas['neck']['arc_over_H'] * Href
res['anatomical'] = dict(hx=round(hx0, 2), hy=round(hy0, 2),
                         anchor_units=[round(float(anchor_t[0]), 2),
                                       round(float(anchor_t[1]), 2)],
                         arc_target_units=round(arc_target, 2))

# approved centreline (breast -> anchor) in its own chord frame
app_samples = np.array(meas['centreline_pts'], float)          # head -> breast
app_path = np.concatenate([app_samples[::-1],
                           [np.array(meas['anchor']['adopted'])]])


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
app_cf = chord_frame(app_rs, app_path[0], app_path[-1])
breast_app = np.array(meas['breast_px'], float)
anchor_app = np.array(meas['anchor']['adopted'], float)
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


def set_neck(p1x, p1c, p1y, p2x, p2y):
    R21.NECK_P1X, R21.NECK_P1C, R21.NECK_P1Y = p1x, p1c, p1y
    R21.NECK_P2X, R21.NECK_P2Y = p2x, p2y


def tune_neck(hx, hy):
    spine0, breast, anchor = rig_spine(hx, hy)
    best = None
    for p1x in (-16, -13, -10, -8, -6, -4):
        for p2x in (-16, -13, -10, -9, -7, -5, -3):
            for p2y in (0, 3, 5, 8, 11):
                set_neck(p1x, -0.5, -1.0, p2x, p2y)
                sp, br, an = rig_spine(hx, hy)
                arc, rms, mx = spine_metrics(sp, br, an)
                score = abs(arc - arc_target) / arc_target * 3 + rms
                if best is None or score < best[0]:
                    best = (score, (p1x, -0.5, -1.0, p2x, p2y), arc, rms, mx)
    # refine around the winner, freeing p1y / p1c
    (p1x, p1c, p1y, p2x, p2y) = best[1]
    for dx in (-1.5, -0.75, 0, 0.75, 1.5):
        for dy in (-1.5, -0.75, 0, 0.75, 1.5):
            for dc, cy in ((-1.5, -2.0), (-0.5, -1.0), (0.5, 0.0), (-0.5, -2.0), (-0.5, 0.0)):
                set_neck(p1x + dx, dc, cy, p2x + dy, p2y)
                sp, br, an = rig_spine(hx, hy)
                arc, rms, mx = spine_metrics(sp, br, an)
                score = abs(arc - arc_target) / arc_target * 3 + rms
                if score < best[0]:
                    best = (score, (p1x + dx, dc, cy, p2x + dy, p2y), arc, rms, mx)
    set_neck(*best[1])
    return best


tb = tune_neck(hx0, hy0)
res['neck_tuning_anatomical'] = dict(
    params=dict(zip(('P1X', 'P1C', 'P1Y', 'P2X', 'P2Y'), tb[1])),
    arc_units=round(tb[2], 2), arc_err_pct=round((tb[2] - arc_target) / arc_target * 100, 2),
    chord_rms=round(tb[3], 4), max_tangent_step_deg=round(tb[4], 1))

# ------------------------------------------------------- 2. IoU search
def fast_iou(target, src):
    Mc = ndimage.center_of_mass(target)
    S0 = src.astype(float) > 0.5
    sy, sx = np.nonzero(S0)
    crop = S0[sy.min():sy.max() + 1, sx.min():sx.max() + 1].astype(float)
    best = 0.0
    for s in np.linspace(0.95, 1.35, 17):
        z = ndimage.zoom(crop, float(s), order=1) > 0.5
        zh, zw = z.shape
        for dy in range(-20, 21, 8):
            for dx in range(-20, 21, 8):
                top = int(round(Mc[0] - zh / 2 + dy))
                left = int(round(Mc[1] - zw / 2 + dx))
                canvas = np.zeros_like(target)
                ys0, ys1 = max(0, top), min(H, top + zh)
                xs0, xs1 = max(0, left), min(W, left + zw)
                if ys1 <= ys0 or xs1 <= xs0:
                    continue
                canvas[ys0:ys1, xs0:xs1] = z[ys0 - top:ys1 - top, xs0 - left:xs1 - left]
                inter = np.logical_and(target, canvas).sum()
                union = np.logical_or(target, canvas).sum()
                v = inter / union if union else 0.0
                if v > best:
                    best = float(v)
    return best


cands = {}
for dhx in range(-4, 5):
    for dhy in range(-3, 4):
        s, _, _ = sil_for(hx0 + dhx, hy0 + dhy)
        cands[(round(hx0 + dhx, 2), round(hy0 + dhy, 2))] = fast_iou(rest, s)
ranked = sorted(cands.items(), key=lambda kv: -kv[1])
res['fast_prescore_top6'] = {f'{k[0]},{k[1]}': round(v, 4) for k, v in ranked[:6]}
res['fast_prescore_anatomical'] = round(cands[(round(hx0, 2), round(hy0, 2))], 4)

finalists = [(hx0, hy0, 'anatomical')]
seen = {(round(hx0, 2), round(hy0, 2))}
for (fx, fy), _v in ranked:
    if (fx, fy) not in seen:
        finalists.append((fx, fy, 'local'))
        seen.add((fx, fy))
    if len(finalists) >= 4:
        break
full = {}
for fx, fy, tag in finalists:
    s, _, _ = sil_for(fx, fy)
    full[(fx, fy)] = (MV.aligned_iou(rest, s), tag)
res['full_protocol_finalists'] = {
    f'{k[0]},{k[1]}': dict(iou=v[0][0], params=v[0][1], tag=v[1]) for k, v in full.items()}

ana_iou = full[(hx0, hy0)][0][0]
best_key = max(full, key=lambda k: full[k][0][0])
fx, fy = best_key
adopt_local = False
if (fx, fy) != (hx0, hy0) and full[best_key][0][0] >= ana_iou + 0.02:
    tb2 = tune_neck(fx, fy)
    arc_ok = abs(tb2[2] - arc_target) / arc_target <= 0.015
    shape_ok = tb2[3] <= tb[3] * 1.25
    res['neck_tuning_localbest'] = dict(
        params=dict(zip(('P1X', 'P1C', 'P1Y', 'P2X', 'P2Y'), tb2[1])),
        arc_units=round(tb2[2], 2), chord_rms=round(tb2[3], 4),
        arc_ok=bool(arc_ok), shape_ok=bool(shape_ok))
    adopt_local = bool(arc_ok and shape_ok)
    if not adopt_local:
        set_neck(*tb[1])
final_hx, final_hy = (fx, fy) if adopt_local else (hx0, hy0)
res['decision'] = dict(adopted='local_best' if adopt_local else 'anatomical',
                       hx=round(final_hx, 2), hy=round(final_hy, 2),
                       mask_iou=full[(final_hx, final_hy)][0][0],
                       mask_iou_params=full[(final_hx, final_hy)][0][1])

# ------------------------------------------- 3. final verification pack
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
                         H_units_new=round(Hg_new, 2),
                         neck_params=dict(zip(('P1X', 'P1C', 'P1Y', 'P2X', 'P2Y'),
                                              (R21.NECK_P1X, R21.NECK_P1C, R21.NECK_P1Y,
                                               R21.NECK_P2X, R21.NECK_P2Y))))
# silhouette neck widths: perpendicular sections at spine quarters
spm = np.array([RR21.mxy(p) for p in spine])
wid = []
for t in (0.3, 0.5, 0.7):
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
    wid.append(tot)
res['final_neck']['silhouette_widths_px'] = wid
res['final_neck']['silhouette_widths_over_H'] = [round(w / (Hg_new * RR21.U), 4) for w in wid]

# overlay under the winning alignment (placement math mirrors
# measure_v2.aligned_iou's inner loop)
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
prm_v2 = cert[1]
overlay(rest, placed_mask(rest, v2sil, prm_v2), f'{OUT}/overlay_v2_recheck.png')
res['final_pose'] = {k: pose_f[k] for k in ('root_x', 'root_y', 'body_tilt', 'hx', 'hy',
                                            'coil', 'neck_w', 'head_pitch', 'yaw')}

with open(f'{OUT}/solve_results.json', 'w') as f:
    json.dump(res, f, indent=1)
print(json.dumps(res, indent=1))
