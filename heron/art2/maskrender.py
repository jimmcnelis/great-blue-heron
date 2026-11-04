"""Shared conditioning-mask renderer for the art2 route proofs.

Turns a keypoint set (any pixel coordinate frame) into a 7-channel part-mask
stack. The SAME construction rules are used for rig-derived target poses and
for annotated training frames, so train/test conditioning match.

Keypoint schema (all [x, y] in the working pixel frame):
  torso_poly : list of >=5 pts, the torso outline loop
  spine      : list of 5 pts, neck centerline breast -> head
  head_c     : skull center (rig H anchor)
  bill_tip   : bill tip
  bill_poly  : list of pts, full head+bill outline (skull + bill merged ok)
  wing_poly  : list of pts, wing outline (folded quad or flight outline)
  hip_n, knee_n, foot_n : near leg joints
  hip_f, knee_f, foot_f : far leg joints
  tail_poly  : list of 3+ pts
Scalars (pose dict subset): neck_w, bulge_pos, bulge_amp, px_per_unit
  (pixel size of one design unit in the working frame, for tube widths).

Channels: 0 torso, 1 neck, 2 head, 3 wing, 4 leg_near, 5 leg_far, 6 tail,
7 PLUME — the shaggy breast-plume skirt is its OWN region (Jimmy, binding
2026-11-02 22:45): it must never be merged into torso or leg masks. Torso
outlines follow the true anatomical body line; legs are the thin sticks
under the skirt. The plume may overlap leg/torso channels spatially (it
hangs over them) but lives only in channel 7.
"""
import numpy as np
from PIL import Image, ImageDraw


def fish_profile(ds):
    """Mirror of rig13_r4._fish_profile (the kept r4 swallow deformation)."""
    ds = np.asarray(ds, float)
    out = np.zeros_like(ds)
    head = ds >= 0
    x = np.clip(ds[head] / 0.20, 0, 1)
    out[head] = (1 - x * x) ** 0.55
    x = np.clip(-ds[~head] / 0.36, 0, 1)
    out[~head] = (1 - x) ** 1.35
    return out


def _tube_poly(spine, widths):
    """Closed polygon around a centerline with per-point full widths."""
    sp = np.asarray(spine, float)
    w = np.asarray(widths, float) / 2.0
    d = np.gradient(sp, axis=0)
    n = np.hypot(d[:, 0], d[:, 1]); n[n == 0] = 1
    nrm = np.stack([-d[:, 1] / n, d[:, 0] / n], axis=1)
    left = sp + nrm * w[:, None]
    right = sp - nrm * w[:, None]
    return [tuple(p) for p in left] + [tuple(p) for p in right[::-1]]


def _seg_poly(a, b, w0, w1):
    a = np.asarray(a, float); b = np.asarray(b, float)
    d = b - a; L = max(np.hypot(*d), 1e-9); d = d / L
    p = np.array([-d[1], d[0]])
    return [tuple(a + p * w0 / 2), tuple(b + p * w1 / 2),
            tuple(b - p * w1 / 2), tuple(a - p * w0 / 2)]


def build_mask_stack(kp, scalars, size):
    """kp: keypoint dict as above. scalars: dict(neck_w, bulge_pos,
    bulge_amp, px_per_unit). size: (W, H) of output. Returns uint8 (7,H,W)."""
    W, H = size
    u = float(scalars.get('px_per_unit', 6.6667))
    chans = [Image.new('L', (W, H), 0) for _ in range(8)]
    dr = [ImageDraw.Draw(c) for c in chans]

    def poly(idx, pts):
        if pts and len(pts) >= 3:
            dr[idx].polygon([tuple(map(float, p)) for p in pts], fill=255)

    poly(0, kp['torso_poly'])
    # neck: dense spine via catmull-ish subdivision of the 5 samples
    sp5 = np.asarray(kp['spine'], float)
    tt = np.linspace(0, 1, 25)
    idx = tt * (len(sp5) - 1)
    i0 = np.floor(idx).astype(int); i0 = np.minimum(i0, len(sp5) - 2)
    fr = (idx - i0)[:, None]
    spine = sp5[i0] * (1 - fr) + sp5[i0 + 1] * fr
    t = np.linspace(0, 1, len(spine))
    widths = (6.4 - 3.0 * t) * float(scalars.get('neck_w', 1.0))
    amp = float(scalars.get('bulge_amp', 0.0))
    if amp > 0.01:
        s = 1.0 - t
        widths = widths * (1.0 + amp * 0.95 * fish_profile(s - float(scalars.get('bulge_pos', 0.0))))
    poly(1, _tube_poly(spine, widths * u))
    poly(2, kp['bill_poly'])
    poly(3, kp['wing_poly'])
    # legs: thigh (wide) + shin (narrow)
    for idx, pre in ((4, 'n'), (5, 'f')):
        hip = kp[f'hip_{pre}']; knee = kp[f'knee_{pre}']; foot = kp[f'foot_{pre}']
        poly(idx, _seg_poly(hip, knee, 2.9 * u, 1.65 * u))
        poly(idx, _seg_poly(knee, foot, 0.95 * u, 0.6 * u))
    poly(6, kp['tail_poly'])
    if kp.get('plume_poly'):
        poly(7, kp['plume_poly'])
    return np.stack([np.asarray(c) for c in chans], axis=0)


def crop_spec(points, pad=0.18, min_side=64):
    """Square crop around a point set. points: (N,2) array in source px.
    Returns (x0, y0, side) floats; crop may extend beyond the image
    (renderers must pad). Same rule for training frames and targets."""
    pts = np.asarray(points, float)
    lo = pts.min(axis=0); hi = pts.max(axis=0)
    cx, cy = (lo + hi) / 2.0
    side = max(hi[0] - lo[0], hi[1] - lo[1]) * (1.0 + 2 * pad)
    side = max(side, min_side)
    return float(cx - side / 2), float(cy - side / 2), float(side)


def all_points(kp):
    pts = []
    for k in ('torso_poly', 'spine', 'bill_poly', 'wing_poly', 'tail_poly',
              'plume_poly'):
        pts.extend([list(p) for p in kp[k]])
    for k in ('head_c', 'bill_tip', 'hip_n', 'knee_n', 'foot_n',
              'hip_f', 'knee_f', 'foot_f'):
        pts.append(list(kp[k]))
    return np.array(pts, float)


def xform_points(kp, fn):
    """Apply fn(xy)->xy to every point in a keypoint dict; returns new dict."""
    out = {}
    for k, v in kp.items():
        if k in ('torso_poly', 'spine', 'bill_poly', 'wing_poly', 'tail_poly',
                 'plume_poly'):
            out[k] = [list(fn(np.asarray(p, float))) for p in v]
        else:
            out[k] = list(fn(np.asarray(v, float)))
    return out
