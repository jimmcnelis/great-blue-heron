#!/usr/bin/env python3
"""Corpus v3 for the pose-conditioned finish model (the retrain on the
settled rig v2.4).

Pairs (same 79 gold pairs + roles as the v2 corpus manifest):
  INPUT  = palette canvas rendered from the rig13_r4_v24 mask stack
           (kp_master + maskrender_v2.build_mask_stack, the exact
           geometry-round construction). The canvas bird IS the rig
           silhouette, so input geometry is exact by construction.
  TARGET = the v2 gold finished frame, per-pair similarity-registered
           (uniform scale + translation, fitted from bird-mask
           moments, iterated) onto that frame's rig silhouette, warped
           with paper fill. The v2 failure mode (canvas<->target IoU
           median 0.134) is measured again here on the same pairs.

Audit: registration_audit_v3.csv -- per pair: IoU(target, rig sil)
before warp, after warp (raw + scenery band y>=558 excluded),
centroid distance after, fitted scale/shift.
"""
import copy, csv, json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

HOME = os.path.expanduser('~')
ART2 = f'{HOME}/workspace/heron/art2'
FS = f'{ART2}/finished-art-stills'
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ART2)
sys.path.insert(0, f'{HOME}/workspace/heron/src13')
import roster_render_v24 as RR
import maskrender_v2 as M2

W, H = 1024, 600
SCEN = 558  # scenery band y>=558 excluded for the bird-only surface

# painter order: later channels paint over earlier ones
PALETTE = [  # (channel, rgb)
    (0, (104, 127, 149)),   # torso slate
    (3, (84, 99, 117)),     # wing darker slate
    (6, (70, 82, 98)),      # tail dark slate
    (5, (133, 103, 70)),    # leg far tan dark
    (4, (168, 132, 92)),    # leg near tan
    (1, (146, 167, 189)),   # neck light slate
    (7, (186, 199, 214)),   # plume pale
    (2, (228, 232, 236)),   # head near-white
]

def stack_for(pose):
    pose = copy.deepcopy(pose)
    for leg in ('leg_near', 'leg_far'):
        pose[leg] = dict(pose[leg])
    kpm = RR.kp_master(pose)
    scalars = dict(neck_w=float(pose['neck_w']), bulge_pos=float(pose['bulge_pos']),
                   bulge_amp=float(pose['bulge_amp']), px_per_unit=RR.U)
    return M2.build_mask_stack(kpm, scalars, (W, H))

def palette_canvas(stack):
    img = np.full((H, W, 3), 255, np.uint8)
    for ch, rgb in PALETTE:
        m = stack[ch] > 0
        img[m] = rgb
    return img

# ---- target segmentation (gate.py protocol, verbatim method) --------
def paper_color(a):
    patches = [a[:40, :40], a[:40, -40:], a[-40:, :40], a[-40:, -40:]]
    return np.median(np.concatenate([p.reshape(-1, 3) for p in patches]), axis=0)

def bird_mask(a):
    pc = paper_color(a)
    cm = np.abs(a - pc).sum(axis=2) > 55
    lab, n = ndimage.label(cm)
    if n == 0:
        return cm
    sizes = ndimage.sum(cm, lab, range(1, n + 1))
    main = 1 + int(np.argmax(sizes))
    keep = lab == main
    dil = ndimage.binary_dilation(keep, iterations=5)
    for i in range(1, n + 1):
        if i != main and sizes[i - 1] >= 200 and (dil & (lab == i)).any():
            keep |= lab == i
    keep[594:, :] = False  # clip hairline waterline (gate.py: y<=593)
    return keep

def moments(m):
    ys, xs = np.nonzero(m)
    return (xs.mean(), ys.mean(), xs.max() - xs.min() + 1, ys.max() - ys.min() + 1,
            int(m.sum()))

def iou(a, b):
    return float((a & b).sum() / max((a | b).sum(), 1))

def _Minv(s, th_deg, dx, dy):
    """(row,col) inverse affine for forward map p' = s*R(th)*p + (dx,dy),
    p in (x,y). Calibrated 2026-11-04: reproduces the geometry-round
    protocol score on the approved idle pair (0.684 vs their 0.691)."""
    th = np.deg2rad(th_deg)
    c, sn = np.cos(th), np.sin(th)
    Minv = (1 / s) * np.array([[c, -sn], [sn, c]])
    return Minv, -Minv @ np.array([dy, dx])

def warp_mask(m, s, th, dx, dy, shape=(H, W)):
    Minv, off = _Minv(s, th, dx, dy)
    return ndimage.affine_transform(m.astype(float), Minv, offset=off,
                                    output_shape=shape, order=1,
                                    mode='constant', cval=0) > 0.5

def fit(tm, sil):
    """Similarity fit of target mask onto rig silhouette. Search runs on
    half-res masks; returns (iou_fullres, s, th, dx, dy)."""
    tm2 = tm.reshape(300, 2, 512, 2).mean(axis=(1, 3)) > 0.5
    sil2 = sil.reshape(300, 2, 512, 2).mean(axis=(1, 3)) > 0.5
    def mom(m):
        ys, xs = np.nonzero(m)
        return xs.mean(), ys.mean(), xs.max() - xs.min() + 1, ys.max() - ys.min() + 1, int(m.sum())
    tcx, tcy, tw, th_, ta = mom(tm2)
    scx, scy, sw, sh, sa = mom(sil2)
    def ev(s, th, dx, dy):  # params in full-res px; evaluate at half res
        return iou(warp_mask(tm2, s, th, dx / 2, dy / 2, shape=(300, 512)), sil2)
    best = None
    for s0 in (np.sqrt(sa / ta), sw / tw, sh / th_):
        t = (s0, 0.0, 2 * (scx - s0 * tcx), 2 * (scy - s0 * tcy))
        v = ev(*t)
        if best is None or v > best[0]:
            best = (v, *t)
    steps = [(0.04, 0, 0, 0), (0, 1.5, 0, 0), (0, 0, 16, 0), (0, 0, 0, 16)]
    for _ in range(4):
        improved = True
        while improved:
            improved = False
            _, s, th, dx, dy = best
            for (ds, dt, ddx, ddy) in steps:
                for sgn in (1, -1):
                    t = (s * (1 + sgn * ds), th + sgn * dt, dx + sgn * ddx, dy + sgn * ddy)
                    v = ev(*t)
                    if v > best[0] + 1e-4:
                        best = (v, *t); improved = True
        steps = [(a / 2, b / 2, c / 2, d / 2) for (a, b, c, d) in steps]
    _, s, th, dx, dy = best
    return iou(warp_mask(tm, s, th, dx, dy), sil), s, th, dx, dy

def fit_and_warp(img, tmask, sil):
    pc = paper_color(img)
    v, s, th, dx, dy = fit(tmask, sil)
    Minv, off = _Minv(s, th, dx, dy)
    wimg = np.stack([ndimage.affine_transform(img[:, :, c], Minv, offset=off,
                     output_shape=(H, W), order=1, mode='constant', cval=pc[c])
                     for c in range(3)], axis=2)
    wm = warp_mask(tmask, s, th, dx, dy)
    return wimg, wm, dict(scale=float(s), rot=float(th), dx=float(dx), dy=float(dy))

def main():
    tracks24 = json.load(open(f'{FS}/rig-v2/band-pass/pose_tracks_v24.json'))
    tracks2 = json.load(open(f'{FS}/rig-v2/work/pose_tracks_v2.json'))
    poses = {'idle_hold': tracks24['idle'][0]}
    for i, p in enumerate(tracks2['strike']):
        poses[f'strike_f{i:04d}'] = p
    rows = list(csv.DictReader(open(f'{FS}/finish-model/corpus_manifest.csv')))
    os.makedirs(f'{HERE}/corpus/canvas', exist_ok=True)
    os.makedirs(f'{HERE}/corpus/target', exist_ok=True)
    os.makedirs(f'{HERE}/corpus/silhouette', exist_ok=True)
    audit, out_rows = [], []
    sil_cache = {}
    for r in rows:
        pid = r['pair_id']
        key = 'idle_hold' if r['family'] == 'idle' else f"strike_f{int(r['chart_frame']):04d}"
        if key not in sil_cache:
            stack = stack_for(poses[key])
            sil = np.any(stack > 0, axis=0)
            sil_cache[key] = (stack, sil)
            Image.fromarray(palette_canvas(stack)).save(f'{HERE}/corpus/canvas/{key}.png')
            Image.fromarray((sil * 255).astype(np.uint8)).save(f'{HERE}/corpus/silhouette/{key}.png')
        stack, sil = sil_cache[key]
        tgt = np.asarray(Image.open(f"{FS}/finish-model/corpus/{r['target']}").convert('RGB'), dtype=np.float32)
        tm = bird_mask(tgt)
        band = np.ones_like(sil); band[SCEN:, :] = False
        pre = iou(tm, sil); pre_b = iou(tm & band, sil & band)
        wimg, wm, prm = fit_and_warp(tgt, tm, sil)
        post = iou(wm, sil); post_b = iou(wm & band, sil & band)
        wcx, wcy, *_ = moments(wm); scx, scy, *_ = moments(sil)
        cd = float(np.hypot(wcx - scx, wcy - scy))
        tname = f'{pid}.png'
        Image.fromarray(np.clip(wimg, 0, 255).astype(np.uint8)).save(f'{HERE}/corpus/target/{tname}')
        out_rows.append(dict(pair_id=pid, family=r['family'], chart_frame=r['chart_frame'],
                             canvas=f'canvas/{key}.png', target=f'target/{tname}',
                             role=r['role'], approved_still=r['approved_still']))
        audit.append(dict(pair_id=pid, key=key, iou_pre=round(pre, 4), iou_pre_bird=round(pre_b, 4),
                          iou_post=round(post, 4), iou_post_bird=round(post_b, 4),
                          centroid_dist_post=round(cd, 2), **{k: (round(v, 4) if isinstance(v, float) else v)
                                                              for k, v in prm.items()}))
        print(pid, key, f'pre {pre:.3f} -> post {post:.3f} (bird {post_b:.3f}) cd {cd:.1f}', flush=True)
    with open(f'{HERE}/corpus_manifest.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys())); w.writeheader(); w.writerows(out_rows)
    with open(f'{HERE}/registration_audit_v3.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(audit[0].keys())); w.writeheader(); w.writerows(audit)
    post = np.array([a['iou_post'] for a in audit]); postb = np.array([a['iou_post_bird'] for a in audit])
    pre = np.array([a['iou_pre'] for a in audit])
    print(f'\nREGISTRATION: pre-warp IoU median {np.median(pre):.3f} | post-warp median {np.median(post):.3f} '
          f'min {post.min():.3f} max {post.max():.3f} | bird-only post median {np.median(postb):.3f} min {postb.min():.3f}')
    print(f'pairs post-warp >= 0.80: {(post >= 0.80).sum()}/{len(post)} | >= 0.70: {(post >= 0.70).sum()}')

if __name__ == '__main__':
    main()
