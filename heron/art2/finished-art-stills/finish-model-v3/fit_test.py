#!/usr/bin/env python3
"""Calibrate the similarity fitter on the idle approved pair:
v2.4 idle silhouette vs approved rest still mask. Geometry-round
protocol scores this pair raw 0.6907 / bird-only 0.7402 (aligned fit).
"""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

HOME = os.path.expanduser('~')
FS = f'{HOME}/workspace/heron/art2/finished-art-stills'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_corpus import bird_mask, iou, SCEN

W, H = 1024, 600

def warp_mask(m, s, th_deg, dx, dy):
    th = np.deg2rad(th_deg)
    c, sn = np.cos(th), np.sin(th)
    Minv = (1 / s) * np.array([[c, -sn], [sn, c]])  # (row,col) space
    off = -Minv @ np.array([dy, dx])
    return ndimage.affine_transform(m.astype(float), Minv, offset=off,
                                    output_shape=(H, W), order=1,
                                    mode='constant', cval=0) > 0.5

def moments(m):
    ys, xs = np.nonzero(m)
    return xs.mean(), ys.mean(), xs.max() - xs.min() + 1, ys.max() - ys.min() + 1, int(m.sum())

def fit(tm, sil):
    tcx, tcy, tw, th_, ta = moments(tm)
    scx, scy, sw, sh, sa = moments(sil)
    cands = []
    for s0 in (np.sqrt(sa / ta), sw / tw, sh / th_):
        cands.append((s0, 0.0, scx - s0 * tcx, scy - s0 * tcy))
    best = None
    for (s, th, dx, dy) in cands:
        v = iou(warp_mask(tm, s, th, dx, dy), sil)
        if best is None or v > best[0]:
            best = (v, s, th, dx, dy)
    # hill climb
    steps = [(0.04, 0, 0, 0), (0, 1.5, 0, 0), (0, 0, 8, 0), (0, 0, 0, 8)]
    for shrink in range(4):
        improved = True
        while improved:
            improved = False
            v0, s, th, dx, dy = best
            for (ds, dt, ddx, ddy) in steps:
                for sgn in (1, -1):
                    t = (s * (1 + sgn * ds), th + sgn * dt, dx + sgn * ddx, dy + sgn * ddy)
                    v = iou(warp_mask(tm, *t), sil)
                    if v > best[0] + 1e-4:
                        best = (v, *t); improved = True
        steps = [(ds / 2, dt / 2, ddx / 2, ddy / 2) for (ds, dt, ddx, ddy) in steps]
    return best

sil = np.asarray(Image.open(f'{FS}/finish-model-v3/corpus/silhouette/idle_hold.png')) > 0
appr = np.asarray(Image.open(f'{FS}/../audubon_rest.png').convert('RGB'), dtype=np.float32) \
    if os.path.exists(f'{FS}/../audubon_rest.png') else None
still = np.asarray(Image.open(f'{FS}/audubon_rest.png').convert('RGB'), dtype=np.float32)
tm = bird_mask(still)
print('unaligned IoU:', round(iou(tm, sil), 4))
v, s, th, dx, dy = fit(tm, sil)
wm = warp_mask(tm, s, th, dx, dy)
band = np.ones_like(sil); band[SCEN:, :] = False
print(f'fitted: IoU {v:.4f} bird-only {iou(wm & band, sil & band):.4f} scale {s:.3f} rot {th:.2f} d ({dx:.1f},{dy:.1f})')
their = np.asarray(Image.open(f'{FS}/rig-v2/masks/approved_rest_mask.png')) > 0
print('my mask vs their approved mask IoU:', round(iou(tm, their), 4))
print('fitted vs their mask:', round(iou(wm, their), 4))
