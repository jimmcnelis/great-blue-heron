#!/usr/bin/env python3
"""Geometry + identity gate for the round-3 refinish corpus.

GEOMETRY (the judged dimension = the silhouette):
- Canvas bird = the filled rig silhouette the stipple canvas encodes,
  rebuilt from the chart pose via roster_charts -> kp_master ->
  maskrender.build_mask_stack (union of all 8 part channels). The raw
  stipple mask is also recorded as a cross-check (it is a sparse point
  render of the same silhouette, so a raw-pixel IoU against a solid
  finished bird is not a meaningful gate; the filled silhouette is).
- Finished bird = bird-only mask segmented from the finished frame:
  v1 content mask (colour distance from the frame's own paper estimate
  > 55), largest connected component plus any component >= 200 px that
  touches its 5 px dilation (detached plume strands), clipped to
  y <= 593 so the hairline waterline below the feet is not bird.
- PASS: silhouette IoU >= 0.90 AND centroid distance <= 10.0 px.
  No marginal passes: 0.899 is a reject.

IDENTITY (v1 protocol verbatim): colour-class fractions computed on
the FULL v1 content mask of the finished frame (same denominator the
v1 bands were measured with):
- idle/hold canvas: black 0.252-0.272, rust 0.035-0.037,
  yellow 0.016-0.018 (approved rest bands; task-stated + v1 report).
- strike canvases: black 0.2501-0.2653, rust 0.0335-0.0373,
  yellow 0.0155-0.0188 (min/max over the 40 standing-family frames
  f00-23 + f40-51 in motion-test/work/metrics.json).

Usage:
  gate.py measure <pair_id> <image_path>   -> one JSON line
  pair_id: idle_hold | strike_f0000 .. strike_f0051
"""
import json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

ART2 = os.path.expanduser('~/workspace/heron/art2')
sys.path.insert(0, ART2)
import roster_charts as RC
import roster_render as RR
import maskrender as M

W, H = 1024, 600
BANDS = {
    'idle':   dict(black=(0.252, 0.272), rust=(0.035, 0.037), yellow=(0.016, 0.018)),
    'strike': dict(black=(0.2501, 0.2653), rust=(0.0335, 0.0373), yellow=(0.0155, 0.0188)),
}

_rig_cache = {}

def rig_silhouette(pair_id):
    if pair_id in _rig_cache:
        return _rig_cache[pair_id]
    if pair_id == 'idle_hold':
        chart, idx = 'idle_hunt', 0
    else:
        chart, idx = 'strike', int(pair_id[-4:])
    pose = RC.CHARTS[chart]().frames[idx]
    kpm = RR.kp_master(pose)
    scalars = dict(neck_w=float(pose['neck_w']), bulge_pos=float(pose['bulge_pos']),
                   bulge_amp=float(pose['bulge_amp']), px_per_unit=RR.U)
    stack = M.build_mask_stack(kpm, scalars, (W, H))
    sil = np.any(stack > 0, axis=0)
    _rig_cache[pair_id] = sil
    return sil

def load_norm(path):
    im = Image.open(path).convert('RGB')
    if im.size != (W, H):
        im = im.resize((W, H), Image.LANCZOS)
    return np.asarray(im, dtype=np.float32)

def paper_color(a):
    patches = [a[:40, :40], a[:40, -40:], a[-40:, :40], a[-40:, -40:]]
    return np.median(np.concatenate([p.reshape(-1, 3) for p in patches]), axis=0)

def content_mask(a):
    pc = paper_color(a)
    return np.abs(a - pc).sum(axis=2) > 55

def bird_mask(a):
    m = content_mask(a)
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
    keep[594:, :] = False
    return keep

def stipple_mask(pair_id):
    p = os.path.expanduser(
        f'~/workspace/heron/art2/finished-art-stills/refinish-corpus/canvas/{pair_id}.png')
    a = np.asarray(Image.open(p).convert('RGB'), dtype=np.float32)
    return a.mean(axis=2) < 200

def color_fracs(a, mask):
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    n = max(int(mask.sum()), 1)
    black = mask & (a.mean(axis=2) < 70)
    rust = mask & (r > 95) & (r - g > 22) & (r - b > 40)
    yellow = mask & (r > 150) & (g > 95) & (b < 120) & (r - b > 60)
    slate = mask & (b > r + 4) & (a.mean(axis=2) > 60) & (a.mean(axis=2) < 190)
    return dict(black=float(black.sum() / n), rust=float(rust.sum() / n),
                yellow=float(yellow.sum() / n), slate=float(slate.sum() / n))

def centroid(m):
    ys, xs = np.nonzero(m)
    if len(xs) == 0:
        return None
    return float(xs.mean()), float(ys.mean())

def measure(pair_id, path):
    fam = 'idle' if pair_id == 'idle_hold' else 'strike'
    a = load_norm(path)
    sil = rig_silhouette(pair_id)
    bm = bird_mask(a)
    inter = int((bm & sil).sum()); union = int((bm | sil).sum())
    iou = inter / union if union else 0.0
    bc, sc = centroid(bm), centroid(sil)
    if bc and sc:
        dcx, dcy = bc[0] - sc[0], bc[1] - sc[1]
        cdist = float(np.hypot(dcx, dcy))
    else:
        dcx = dcy = cdist = None
    fr = color_fracs(a, content_mask(a))
    bands = BANDS[fam]
    ident = all(bands[k][0] <= fr[k] <= bands[k][1] for k in ('black', 'rust', 'yellow'))
    geo = bool(iou >= 0.90 and cdist is not None and cdist <= 10.0)
    st = stipple_mask(pair_id)
    stc = centroid(st)
    return dict(pair_id=pair_id, image=path,
                iou=round(float(iou), 4), d_cx=None if dcx is None else round(dcx, 2),
                d_cy=None if dcy is None else round(dcy, 2),
                centroid_dist=None if cdist is None else round(cdist, 2),
                bird_area=int(bm.sum()), sil_area=int(sil.sum()),
                stipple_area=int(st.sum()),
                stipple_centroid=None if not stc else [round(stc[0], 1), round(stc[1], 1)],
                sil_centroid=[round(sc[0], 1), round(sc[1], 1)] if sc else None,
                fracs={k: round(v, 4) for k, v in fr.items()},
                identity_pass=bool(ident), geometry_pass=geo,
                accepted=bool(ident and geo))

if __name__ == '__main__':
    if len(sys.argv) == 4 and sys.argv[1] == 'measure':
        print(json.dumps(measure(sys.argv[2], sys.argv[3])))
    else:
        print(__doc__)
        sys.exit(2)
