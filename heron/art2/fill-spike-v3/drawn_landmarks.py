#!/usr/bin/env python3
"""Drawn-landmark extraction + part re-registration (spike 3 instruments).

For an image (a registered gold drawing) and its rig pose, locate the
DRAWN head's own landmarks and fit the similarity that carries them
onto the rig's landmarks. Deterministic; every fallback is logged.

Detectors (validated on annotated overlays, both gate golds):
- bill: yellow-class pixels near the part/bill wedge; tip = extreme
  along the rig bill axis, base = cluster at the axis-near end.
- eye: iris-colour clusters (the bill itself also passes the iris
  test, so yellow pixels are excluded first) in a wide part zone.
- skull: largest content component in a wide head zone with the
  neck-channel region cut away.
- crest root: boundary of the head mass along the back-of-bill axis.
- neck joints: content centroids in windows on the rig spine stations.
"""
import os, sys
import numpy as np
from scipy import ndimage

HOME = os.path.expanduser('~')
ART2 = f'{HOME}/workspace/heron/art2'
FS = f'{ART2}/finished-art-stills'
FM3 = f'{FS}/finish-model-v3'
sys.path.insert(0, ART2); sys.path.insert(0, f'{HOME}/workspace/heron/src13')
sys.path.insert(0, FM3); sys.path.insert(0, f'{ART2}/fill-spike-v1')
sys.path.insert(0, f'{ART2}/fill-spike-v2')
import build_corpus as bc
import roster_render_v24 as RR
import spike_fill as S1
from spike2_fill import umeyama

W, H = 1024, 600

def yellow_mask(a):
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    return (r > 150) & (g > 95) & (b < 120) & (r - b > 60)

def iris_mask(a):
    # amber iris, measured off both gate golds' eyes (the strict test
    # tuned on the original Audubon scan misses the generated irises)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    return (r > 90) & (r < 230) & (g > 40) & (g < 200) & (b < 115) \
        & ((r - b) > 60) & (r > g)

def comps(mask):
    lab, n = ndimage.label(mask)
    if n == 0:
        return []
    sizes = ndimage.sum(mask, lab, range(1, n + 1))
    out = []
    for k in range(n):
        ys, xs = np.nonzero(lab == k + 1)
        out.append((int(sizes[k]), np.array([xs.mean(), ys.mean()]),
                    np.stack([xs, ys], axis=1).astype(float)))
    return sorted(out, key=lambda t: -t[0])

def march_exit(inside, start, direction, max_t=160):
    """Boundary point from start along direction through `inside`
    (start snapped to the nearest inside pixel within 12 px)."""
    ys, xs = np.nonzero(inside)
    if len(xs) == 0:
        return np.array(start, float)
    d = np.hypot(xs - start[0], ys - start[1])
    k = int(np.argmin(d))
    if d[k] > 12:
        return np.array(start, float)
    p0 = np.array([xs[k], ys[k]], float)
    last = p0.copy()
    for t in range(1, max_t + 1):
        p = p0 + direction * t
        x, y = int(round(p[0])), int(round(p[1]))
        if not (0 <= x < W and 0 <= y < H) or not inside[y, x]:
            break
        last = p
    return last

def bill_triangle_mask(kp):
    bp = kp['bill_poly']
    ys, xs = np.mgrid[0:H, 0:W]
    _, _, tri_in = S1.tri_coords(np.stack([ys.ravel(), xs.ravel()], 1),
                                 np.array([bp[9], bp[10], bp[11]]))
    return tri_in.reshape(H, W)

def drawn_landmarks(img, pose, eye_uv=None):
    """Returns (pts_drawn, pts_rig, names, notes). Points are (x, y).
    eye_uv: the eye's offset in the rig head frame (u along bill axis,
    v along perp), measured once from the idle gold; None drops the eye."""
    stack = bc.stack_for(pose)
    kp = RR.kp_master(pose)
    lab = S1.labelmap(stack)
    part = (lab == 1) | (lab == 2)
    cm = S1.content_mask(img)
    hc = np.array(kp['head_c'], float); tip_r = np.array(kp['bill_tip'], float)
    axis = tip_r - hc; axis = axis / np.hypot(*axis)
    perp = np.array([-axis[1], axis[0]])
    notes = {}
    bp = [np.array(p, float) for p in kp['bill_poly']]
    tri_m = bill_triangle_mask(kp)
    yel_all = yellow_mask(img)
    # --- bill (drawn) ---
    zone_b = ndimage.binary_dilation(part, iterations=25) | \
        ndimage.binary_dilation(tri_m, iterations=30)
    yel = yel_all & zone_b
    notes['yellow_px'] = int(yel.sum())
    if yel.sum() >= 40:
        yy, xx = np.nonzero(yel)
        P = np.stack([xx, yy], axis=1).astype(float)
        proj = (P - hc) @ axis
        tip_d = P[int(np.argmax(proj))]
        base_anchor = P[int(np.argmin(proj))]
        near = np.hypot(*(P - base_anchor).T) <= 14
        base_d = P[near].mean(axis=0)
        if tip_d[1] >= H - 4 or tip_d[0] >= W - 4:
            notes['bill_tip'] = 'frame-clipped (true tip off-frame)'
    else:
        tip_d = tip_r.copy(); base_d = (bp[9] + bp[11]) / 2.0
        notes['bill'] = 'FALLBACK rig (yellow<40)'
    dax = tip_d - base_d
    dax = dax / max(np.hypot(*dax), 1e-9)
    # --- head component (drawn): the content mass the bill base sits on ---
    headz = ndimage.binary_dilation(part, iterations=45)
    cand_m = cm & headz & ~ndimage.binary_dilation(lab == 1, iterations=4) \
        & ~ndimage.binary_dilation(yel_all, iterations=2)
    head_comp = None
    best = None
    for size, cen, P in comps(cand_m):
        if size < 200:
            continue
        d = np.hypot(*(P - base_d).T).min()
        if best is None or d < best:
            best = d; head_comp = P
    if head_comp is None:
        notes['head'] = 'FALLBACK rig (no component)'
        head_comp_m = stack[2] > 0
        skull_d = hc.copy()
    else:
        head_comp_m = np.zeros((H, W), bool)
        head_comp_m[head_comp[:, 1].astype(int), head_comp[:, 0].astype(int)] = True
        notes['head_px'] = int(len(head_comp))
        skull_d = None
    # --- eye (drawn): largest amber cluster on the head mass ---
    eye_d = None
    if head_comp is not None:
        on_head = ndimage.binary_dilation(head_comp_m, iterations=6)
        for size, cen, _ in comps(iris_mask(img) & on_head):
            if 3 <= size <= 150:
                eye_d = cen; notes['eye_px'] = size; break
    if eye_d is None:
        notes['eye'] = 'NOT FOUND (dropped from fit)'
    else:
        notes['eye_xy'] = [round(float(eye_d[0]), 1), round(float(eye_d[1]), 1)]
    eye_r = None
    if eye_uv is not None:
        eye_r = hc + eye_uv[0] * axis + eye_uv[1] * perp
    # --- skull (drawn): head-mass centroid near the eye / bill base ---
    if head_comp is not None:
        anchor = eye_d if eye_d is not None else base_d
        near = np.hypot(*(head_comp - anchor).T) <= 55
        skull_d = head_comp[near].mean(axis=0) if near.sum() >= 60 \
            else head_comp.mean(axis=0)
    # --- crest root / back of skull ---
    root_d = march_exit(ndimage.binary_dilation(head_comp_m, iterations=2),
                        skull_d, -dax)
    back_r = march_exit(stack[2] > 0, hc, -axis)
    # --- neck stations (drawn) ---
    neck_zone = ndimage.binary_dilation(stack[1] > 0, iterations=10)
    ys, xs = np.mgrid[0:H, 0:W]
    st_d, st_r = [], []
    for i in (1, 2, 3):
        sp = np.array(kp['spine'][i], float)
        win = (xs - sp[0]) ** 2 + (ys - sp[1]) ** 2 <= 30 ** 2
        m = cm & neck_zone & win
        if m.sum() >= 40:
            yy, xx = np.nonzero(m)
            st_d.append(np.array([xx.mean(), yy.mean()])); st_r.append(sp)
        else:
            st_d.append(sp.copy()); st_r.append(sp)
            notes[f'station{i}'] = 'FALLBACK rig (identity)'
    names = ['skull', 'bill_tip', 'bill_base', 'crest_root',
             'neck_s1', 'neck_s2', 'neck_s3']
    pts_d = [skull_d, tip_d, base_d, root_d] + st_d
    pts_r = [hc, tip_r, (bp[9] + bp[11]) / 2.0, back_r] + st_r
    if eye_d is not None and eye_r is not None:
        names.insert(1, 'eye')
        pts_d.insert(1, eye_d); pts_r.insert(1, eye_r)
    return np.stack(pts_d), np.stack(pts_r), names, notes

def reregister_part(img, pose, eye_uv=None):
    """Warp the part zone by the drawn->rig similarity; composite back
    with a feathered zone. Returns (out_img, info)."""
    stack = bc.stack_for(pose)
    kp = RR.kp_master(pose)
    lab = S1.labelmap(stack)
    part = (lab == 1) | (lab == 2)
    pts_d, pts_r, names, notes = drawn_landmarks(img, pose, eye_uv)
    prm, rms = umeyama(pts_d, pts_r)
    s, th, dx, dy = prm
    thr = np.deg2rad(th)
    R = np.array([[np.cos(thr), -np.sin(thr)], [np.sin(thr), np.cos(thr)]])
    pred = (s * (R @ pts_d.T)).T + np.array([dx, dy])
    resid = np.hypot(*(pred - pts_r).T)
    warped = S1.warp_img(img, prm)
    hc = np.array(kp['head_c'], float); tip = np.array(kp['bill_tip'], float)
    ax = tip - hc; ax = ax / np.hypot(*ax)
    ys, xs = np.mgrid[0:H, 0:W]
    rel = np.stack([xs - hc[0], ys - hc[1]], axis=2)
    proj = rel @ ax
    crest_zone = (np.hypot(rel[:, :, 0], rel[:, :, 1]) < 250) & (proj < 25) \
        & ~((stack[0] > 0) | (stack[3] > 0) | (stack[6] > 0))
    tri_m = bill_triangle_mask(kp)
    zone = ndimage.binary_dilation(part, iterations=24) | \
        ndimage.binary_dilation(tri_m, iterations=16) | \
        (crest_zone & ndimage.binary_dilation(part, iterations=90))
    dist = ndimage.distance_transform_edt(zone)
    alpha = np.clip(dist / 10.0, 0, 1)[:, :, None]
    out = img * (1 - alpha) + warped * alpha
    info = dict(names=names, notes=notes,
                drawn=[[round(float(v), 1) for v in p] for p in pts_d],
                rig=[[round(float(v), 1) for v in p] for p in pts_r],
                warp=[round(float(v), 4) for v in prm],
                rms=round(rms, 2),
                resid={n: round(float(r), 1) for n, r in zip(names, resid)})
    return out, info
