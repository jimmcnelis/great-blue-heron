#!/usr/bin/env python3
"""Strike-measure core instruments (measurement ONLY — no fill, no edits).

Replicates spike 3's instruments exactly for corpus frames, and adds:
- rig geometry (run, torso hull, neck-footprint widths) from kp/stack
- a uniform torso-hull reference measurable on any bird mask
- perpendicular width scans along a centerline
All points are (x, y) image coords on the 1024x600 canvas.
"""
import os, sys, json
import numpy as np
from scipy import ndimage
from scipy.spatial import ConvexHull

HOME = os.path.expanduser('~')
ART2 = f'{HOME}/workspace/heron/art2'
FS = f'{ART2}/finished-art-stills'
FM3 = f'{FS}/finish-model-v3'
sys.path.insert(0, ART2); sys.path.insert(0, f'{HOME}/workspace/heron/src13')
sys.path.insert(0, FM3); sys.path.insert(0, f'{ART2}/fill-spike-v1')
sys.path.insert(0, f'{ART2}/fill-spike-v2'); sys.path.insert(0, f'{ART2}/fill-spike-v3')
import build_corpus as bc
import roster_render_v24 as RR
import spike_fill as S1
import drawn_landmarks as DL

W, H = 1024, 600
load = S1.load
TRACKS2 = json.load(open(f'{FS}/rig-v2/work/pose_tracks_v2.json'))
TRACKS24 = json.load(open(f'{FS}/rig-v2/band-pass/pose_tracks_v24.json'))
EYE_UV = (54.7, 1.0)   # spike 3: measured from idle_f0030 gold

def pose_of(pair_id):
    fam, fr = pair_id.rsplit('_f', 1)
    if fam == 'idle':
        return TRACKS24['idle'][0]
    return TRACKS2['strike'][int(fr)]

def hull_diameter(pts):
    pts = np.asarray(pts, float)
    if len(pts) < 3:
        return float(np.hypot(*(pts.max(0) - pts.min(0)))) if len(pts) else 0.0
    hull = ConvexHull(pts)
    hp = pts[hull.vertices]
    d = np.hypot(*(hp[:, None, :] - hp[None, :, :]).transpose(2, 0, 1))
    return float(d.max())

def rig_geometry(pose):
    kp = RR.kp_master(pose)
    stack = bc.stack_for(pose)
    spine = [np.array(p, float) for p in kp['spine']]
    head_c = np.array(kp['head_c'], float)
    run_pts = spine[1:] + [head_c]
    arc = float(sum(np.hypot(*(run_pts[i + 1] - run_pts[i]))
                    for i in range(len(run_pts) - 1)))
    return dict(kp=kp, stack=stack, spine=spine, head_c=head_c,
                run_straight=float(np.hypot(*(head_c - spine[1]))),
                run_arc=arc,
                torso_hull=hull_diameter(kp['torso_poly']),
                neck_w_param=float(pose['neck_w']))

def scan_width(mask, pt, direction, max_r=110):
    """Width of the contiguous mask segment containing pt, scanned along
    the line through pt perpendicular to `direction`. 2px gap tolerance.
    Returns (width_px, end_a, end_b) or (0, pt, pt) if pt not on mask."""
    d = np.asarray(direction, float); d /= max(np.hypot(*d), 1e-9)
    perp = np.array([-d[1], d[0]])
    ts = np.arange(-max_r, max_r + 1)
    xs = pt[0] + perp[0] * ts; ys = pt[1] + perp[1] * ts
    xi = np.clip(np.round(xs).astype(int), 0, W - 1)
    yi = np.clip(np.round(ys).astype(int), 0, H - 1)
    on = mask[yi, xi]
    c = max_r  # index of pt
    if not on[c]:
        # snap to nearest on-pixel within 6 px along the scan
        idx = np.nonzero(on)[0]
        if len(idx) == 0 or abs(idx[np.argmin(np.abs(idx - c))] - c) > 6:
            return 0.0, np.array(pt, float), np.array(pt, float)
        c = int(idx[np.argmin(np.abs(idx - c))])
    def grow(i, step):
        gap = 0; last = i
        while 0 <= i + step < len(on):
            i += step
            if on[i]:
                last = i; gap = 0
            else:
                gap += 1
                if gap > 2:
                    break
        return last
    a = grow(c, -1); b = grow(c, +1)
    pa = np.array([xs[a], ys[a]]); pb = np.array([xs[b], ys[b]])
    return float(np.hypot(*(pb - pa))), pa, pb

def centerline_widths(mask, pts, fracs=(0.0, 0.25, 0.5, 0.75)):
    """Widths at arc-length fractions of the polyline pts (base->skull).
    Returns {frac: (width, point, end_a, end_b)}."""
    pts = [np.array(p, float) for p in pts]
    seg = [np.hypot(*(pts[i + 1] - pts[i])) for i in range(len(pts) - 1)]
    total = float(sum(seg))
    out = {}
    for f in fracs:
        target = f * total
        acc = 0.0; done = False
        for i, L in enumerate(seg):
            if acc + L >= target or i == len(seg) - 1:
                t = 0.0 if L == 0 else min(max((target - acc) / L, 0.0), 1.0)
                p = pts[i] + t * (pts[i + 1] - pts[i])
                d = pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]
                w, pa, pb = scan_width(mask, p, d)
                out[f] = (w, p, pa, pb); done = True; break
            acc += L
        if not done:
            out[f] = (0.0, pts[-1], pts[-1], pts[-1])
    return out, total

def torso_hull_from_mask(mask, base_pt, run_dir):
    """Uniform torso reference for ANY bird mask: cut away the neck/head
    side at the line through base_pt perpendicular to run_dir, erode away
    thin structures (legs/plume), take the largest remaining component,
    return its convex-hull diameter and the component mask."""
    ys, xs = np.mgrid[0:H, 0:W]
    d = np.asarray(run_dir, float); d /= max(np.hypot(*d), 1e-9)
    side = (xs - base_pt[0]) * d[0] + (ys - base_pt[1]) * d[1]
    body = mask & (side <= 2)
    er = ndimage.binary_erosion(body, iterations=8)
    lab, n = ndimage.label(er)
    if n == 0:
        return 0.0, er
    sizes = ndimage.sum(er, lab, range(1, n + 1))
    main = lab == (1 + int(np.argmax(sizes)))
    ys2, xs2 = np.nonzero(main)
    pts = np.stack([xs2, ys2], axis=1)
    # hull diameter on the eroded core underestimates the outline; grow the
    # core back inside `body` before measuring (reconstruction by dilation)
    rec = ndimage.binary_dilation(main, iterations=8) & body
    ys3, xs3 = np.nonzero(rec)
    # thin the boundary sample for the hull (every 3rd px is plenty)
    bnd = np.stack([xs3, ys3], axis=1)[::3]
    return hull_diameter(bnd), rec
