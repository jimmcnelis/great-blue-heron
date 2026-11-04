#!/usr/bin/env python3
"""Proof (1), canvas surface: aligned silhouette IoU of the Fix-1
decoder canvases vs the approved rest still, plus the decoder's
self-consistency (canvas vs its OWN conditioning silhouette, raw).

Bird mask from a canvas: luminance < T, largest component plus any
>=200 px component touching it (mirrors gate.bird_mask's fragment
rule; no y-clip - canvases have no plate furniture to exclude).
Phase B's canvas protocol (thresholds/house rules) was never saved;
the stage-1 probe on the EXISTING v2 canvas found T=200 -> 0.4669
and T=220 -> 0.4838 under this protocol, bracketing Phase B's
reported 0.465-0.491, so T=200 is primary, T=220 the sensitivity.
Every canvas is measured with the identical code path.
"""
import json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

HOME = os.path.expanduser('~')
FS = f'{HOME}/workspace/heron/art2/finished-art-stills'
RIGV2 = f'{FS}/rig-v2'
OUT = f'{RIGV2}/head-anchor'
sys.path.insert(0, f'{RIGV2}/work')
import measure_v2 as MV

W, Hh = 1024, 600
rest = np.asarray(Image.open(f'{RIGV2}/masks/approved_rest_mask.png')) > 0


def canvas_bird(path, T):
    a = np.asarray(Image.open(path).convert('RGB')).astype(float)
    lum = a @ np.array([0.299, 0.587, 0.114])
    ink = lum < T
    lab, n = ndimage.label(ink)
    sizes = ndimage.sum(ink, lab, range(1, n + 1))
    main_id = int(np.argmax(sizes)) + 1
    keep = lab == main_id
    dil = ndimage.binary_dilation(keep, iterations=2)
    for i, s in enumerate(sizes, start=1):
        if i != main_id and s >= 200 and np.any(dil & (lab == i)):
            keep |= lab == i
    return keep


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
    ys0, ys1 = max(0, top), min(Hh, top + zh)
    xs0, xs1 = max(0, left), min(W, left + zw)
    canvas[ys0:ys1, xs0:xs1] = z[ys0 - top:ys1 - top, xs0 - left:xs1 - left]
    return canvas


def overlay(target, placed, path):
    img = np.ones((Hh, W, 3), np.uint8) * 255
    img[target & placed] = (255, 200, 0)
    img[target & ~placed] = (230, 40, 30)
    img[placed & ~target] = (40, 90, 220)
    Image.fromarray(img).save(path)


res = {}
jobs = {
    'v2': (f'{RIGV2}/canvas/idle_hold.png', f'{RIGV2}/masks/rig_v2_idle_silhouette.png'),
    'v21': (f'{OUT}/idle_hold_v21.png', f'{OUT}/rig_v2_1_idle_silhouette.png'),
}
for tag, (cpath, spath) in jobs.items():
    sil = np.asarray(Image.open(spath)) > 0
    res[tag] = {}
    for T in (200, 220):
        bm = canvas_bird(cpath, T)
        iou, prm = MV.aligned_iou(rest, bm)
        raw = float(np.sum(bm & sil) / np.sum(bm | sil))
        res[tag][f'T{T}'] = dict(canvas_iou_vs_approved=iou, params=prm,
                                 canvas_area=int(bm.sum()),
                                 decoder_self_iou_raw=raw)
        if tag == 'v21' and T == 200:
            overlay(rest, placed_mask(rest, bm, prm),
                    f'{OUT}/overlay_canvas_v21_vs_approved.png')
    res[tag]['silhouette_area'] = int(sil.sum())

with open(f'{OUT}/canvas_measurements.json', 'w') as f:
    json.dump(res, f, indent=1)
print(json.dumps(res, indent=1))
