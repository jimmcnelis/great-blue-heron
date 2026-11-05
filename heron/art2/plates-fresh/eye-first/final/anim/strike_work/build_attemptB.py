#!/usr/bin/env python3
"""Attempt B: plate-based morph of the strike cycle.
Pyramidal block-match flow between keyframe plates; warp-blend in-betweens.
Timeline (24fps, 156f): alert hold / slow coil wind-up / coil hold /
5-frame strike on the release profile / peak hold / withdraw / uncoil / settle.
"""
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates, gaussian_filter, zoom
import os, time

W, H = 1024, 600
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, '..', 'strike_attemptB_frames')
os.makedirs(OUT, exist_ok=True)

def load(n):
    return np.asarray(Image.open(os.path.join(BASE, n)).convert('RGB'), dtype=np.float32)

alert, coil, peak = load('alert_1024.png'), load('coil_1024.png'), load('peak_1024.png')

def gray(a): return a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)

def pyr(g, levels=4):
    out = [g]
    for _ in range(levels - 1):
        out.append(gaussian_filter(out[-1], 1.0)[::2, ::2])
    return out

def block_flow(src, dst):
    """Dense flow src->dst at half res via coarse-to-fine block matching."""
    sw, sh = 512, 300
    s = gray(src)[::2, ::2]; d = gray(dst)[::2, ::2]
    ps, pd_ = pyr(s), pyr(d)
    flow = np.zeros((2, 8, 8), dtype=np.float32)  # at coarsest grid below
    # grid strides per level (from coarsest to finest)
    for li in range(len(ps) - 1, -1, -1):
        im_s, im_d = ps[li], pd_[li]
        lh, lw = im_s.shape
        stride = 4
        gy, gx = np.mgrid[stride//2:lh:stride, stride//2:lw:stride]
        pts = np.stack([gy.ravel(), gx.ravel()]).astype(np.float32)  # 2 x N
        scale = (sh / lh)
        # upsample incoming flow to this level's grid
        if li == len(ps) - 1:
            f = np.zeros((2, pts.shape[1]), dtype=np.float32)
        else:
            f = f * 2.0  # vectors scale with resolution
        # expected positions with current flow
        base_y = pts[0] + f[0]; base_x = pts[1] + f[1]
        R = 5 if li > 0 else 3
        PH = 4  # patch half
        offs = [(dy, dx) for dy in range(-R, R + 1) for dx in range(-R, R + 1)]
        # patch sample offsets
        py, px = np.mgrid[-PH:PH + 1, -PH:PH + 1]
        py, px = py.ravel(), px.ravel()
        src_patch = None
        best = np.full(pts.shape[1], np.inf, dtype=np.float32)
        bestf = f.copy()
        # source patches (fixed)
        sy = (pts[0][:, None] + py[None, :]).ravel()
        sx = (pts[1][:, None] + px[None, :]).ravel()
        src_patch = map_coordinates(im_s, [sy, sx], order=1, mode='nearest').reshape(pts.shape[1], -1)
        for dy, dx in offs:
            cy = (base_y[:, None] + dy + py[None, :]).ravel()
            cx = (base_x[:, None] + dx + px[None, :]).ravel()
            cand = map_coordinates(im_d, [cy, cx], order=1, mode='nearest').reshape(pts.shape[1], -1)
            err = np.abs(cand - src_patch).mean(axis=1)
            m = err < best
            if m.any():
                best[m] = err[m]
                bestf[0][m] = f[0][m] + dy
                bestf[1][m] = f[1][m] + dx
        f = bestf
        # densify to grid image for next level upsample
        gh, gw = gy.shape
        fimg = f.reshape(2, gh, gw)
        if li > 0:
            fimg = zoom(fimg, (1, 2, 2), order=1)
            # re-stride handled next level by re-sampling f at new grid pts
            nxt_h, nxt_w = ps[li - 1].shape
            ngy, ngx = np.mgrid[stride//2:nxt_h:stride, stride//2:nxt_w:stride]
            f = np.stack([
                map_coordinates(fimg[0], [ngy.ravel() / 2.0, ngx.ravel() / 2.0], order=1, mode='nearest'),
                map_coordinates(fimg[1], [ngy.ravel() / 2.0, ngx.ravel() / 2.0], order=1, mode='nearest'),
            ]).astype(np.float32)
        else:
            dense = np.stack([
                zoom(fimg[0], (sh / gh, sw / gw), order=1),
                zoom(fimg[1], (sh / gh, sw / gw), order=1),
            ])
    # smooth dense flow (vectors in half-res px)
    dense[0] = gaussian_filter(dense[0], 4)
    dense[1] = gaussian_filter(dense[1], 4)
    # to full res
    full = np.stack([
        zoom(dense[0], (H / sh, W / sw), order=1) * 2.0,
        zoom(dense[1], (H / sh, W / sw), order=1) * 2.0,
    ])
    return full.astype(np.float32)

def warp(img, flow, t):
    """Sample img at coords + flow*t (flow points from img toward target)."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cy = yy + flow[0] * t; cx = xx + flow[1] * t
    out = np.empty_like(img)
    for c in range(3):
        out[..., c] = map_coordinates(img[..., c], [cy, cx], order=1, mode='nearest')
    return out

t0 = time.time()
print('flow alert->coil ...', flush=True)
f_ac = block_flow(alert, coil)
print('flow coil->alert ...', flush=True)
f_ca = block_flow(coil, alert)
print('flow coil->peak ...', flush=True)
f_cp = block_flow(coil, peak)
print('flow peak->coil ...', flush=True)
f_pc = block_flow(peak, coil)
print('flows done in %.0fs' % (time.time() - t0), flush=True)
np.savez(os.path.join(BASE, 'flows.npz'), ac=f_ac, ca=f_ca, cp=f_cp, pc=f_pc)

def morph(A, B, fab, fba, t):
    if t <= 0.0: return A.copy()
    if t >= 1.0: return B.copy()
    wa = warp(A, fab, t)
    wb = warp(B, fba, -(1.0 - t))
    return ((1 - t) * wa + t * wb)

def smooth(t): return t * t * (3 - 2 * t)

frames = []
def add(img, n=1):
    for _ in range(n): frames.append(img)

add(alert, 18)                                            # alert hold 0.75s
for i in range(1, 49):                                    # wind-up 2.0s
    frames.append(morph(alert, coil, f_ac, f_ca, smooth(i / 48)))
add(coil, 18)                                             # coil hold 0.75s
for p in (0.03, 0.15, 0.45, 0.75):                        # strike ~0.17s
    frames.append(morph(coil, peak, f_cp, f_pc, p))
add(peak, 15)                                             # peak hold (incl. strike end frame)
for i in range(1, 9):                                     # withdraw 0.33s, ease-out
    u = 1 - (1 - i / 8) ** 3
    frames.append(morph(coil, peak, f_cp, f_pc, 1 - u))
for i in range(1, 31):                                    # uncoil 1.25s
    frames.append(morph(coil, alert, f_ca, f_ac, 1 - smooth(i / 30)))
add(alert, 15)                                            # settle -> loop
print('total frames:', len(frames), flush=True)

for i, fr in enumerate(frames):
    Image.fromarray(np.clip(fr, 0, 255).astype(np.uint8)).save(os.path.join(BASE, 'allB_%03d.png' % i))
print('frames written in %.0fs' % (time.time() - t0), flush=True)
