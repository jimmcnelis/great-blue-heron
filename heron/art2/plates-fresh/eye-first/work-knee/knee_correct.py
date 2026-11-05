#!/usr/bin/env python3
"""Knee-deep leg correction for the three approved heron plates.
Originals are only read. Corrected copies go to corrected/.
Method: corridor+ellipse erase mask per leg -> donor-paper fill (row-tinted,
feathered) -> hand-style ripple rings drawn at the joints (supersampled) ->
original thigh/knuckle tip pixels restored over the rings (arcs pass BEHIND
the leg, as in the plates' own foot rings).
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import json, hashlib, os

BASE = os.path.expanduser('~/workspace/heron/art2/plates-fresh/eye-first')
OUT = os.path.join(BASE, 'corrected')
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(20261104)

# v2: ring centre sits ~7px below the rusty->dark transition on plate_1/coil_2
# (the dark knuckle nub is kept and enters the ring, as peak_3's knuckle does);
# cut = centre + 4 (alert/coil) ; peak keeps its whole knuckle, cut = centre + 12.
PLATES = {
    'plate_1': dict(
        src='ranked/plate_1.png', out='plate_1_knee.png', belly_y=348, hw=17, cap=5,
        erase_rx=54, erase_ry=24, ring=(78, 16, 46, 10),
        legs=[dict(joint=(363, 411), centre=(363, 418), cut=422, foot=(343, 537)),
              dict(joint=(404, 415), centre=(404, 422), cut=426, foot=(404, 537))]),
    'coil_2': dict(
        src='coil/ranked/coil_2.png', out='coil_2_knee.png', belly_y=348, hw=17, cap=5,
        erase_rx=54, erase_ry=24, ring=(78, 16, 46, 10),
        legs=[dict(joint=(362, 412), centre=(362, 419), cut=423, foot=(342, 538)),
              dict(joint=(401, 420), centre=(401, 427), cut=431, foot=(403, 538))]),
    'peak_3': dict(
        src='peak/ranked/peak_3.png', out='peak_3_knee.png', belly_y=345, hw=19, cap=9,
        erase_rx=56, erase_ry=24, ring=(86, 17, 50, 10),
        legs=[dict(joint=(334, 418), centre=(334, 419), cut=434, foot=(338, 536)),
              dict(joint=(383, 423), centre=(383, 424), cut=439, foot=(394, 536))]),
}

def sha256(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()

def foot_ring_bbox(im, fx):
    """dark-pixel bbox of the foot ring nearest foot centre fx, y 512..562."""
    a = np.asarray(im).astype(int)
    lum = a.mean(axis=2)
    dark = (lum < 95)
    sub = dark[512:562, max(0, fx-70):fx+70]
    ys, xs = np.where(sub)
    if len(xs) == 0: return None
    return (xs.min()+max(0, fx-70), xs.max()+max(0, fx-70), ys.min()+512, ys.max()+512)

results = {}
for name, cfg in PLATES.items():
    src_path = os.path.join(BASE, cfg['src'])
    h_before = sha256(src_path)
    orig = Image.open(src_path).convert('RGB')
    W, H = orig.size
    a = np.asarray(orig).astype(np.float64)

    # ---- measure foot rings (for style + erase sizing)
    fb = [foot_ring_bbox(orig, leg['foot'][0]) for leg in cfg['legs']]
    foot_w = int(max(b[1]-b[0]+1 for b in fb))
    foot_h = int(max(b[3]-b[2]+1 for b in fb))

    # ---- build erase mask
    mask_img = Image.new('L', (W, H), 0)
    md = ImageDraw.Draw(mask_img)
    for leg in cfg['legs']:
        jx, jy = leg['joint']; cut = leg['cut']; fx, fy = leg['foot']
        hw = cfg['hw']  # corridor half width
        # corridor polygon along centreline joint->foot
        import math
        dx, dy = fx-jx, 560-cut
        L = math.hypot(dx, dy); ux, uy = dx/L, dy/L; px_, py_ = -uy, ux
        pts = [(jx+px_*hw, cut+py_*0), (jx-px_*hw, cut-py_*0),
               (fx-px_*hw, 562-py_*0), (fx+px_*hw, 562+py_*0)]
        md.polygon(pts, fill=255)
        # foot ellipse erase (fixed, sized from the plates' actual foot rings)
        md.ellipse([fx-cfg['erase_rx'], fy-cfg['erase_ry'], fx+cfg['erase_rx'], fy+cfg['erase_ry']], fill=255)
    mask = np.asarray(mask_img).astype(np.float64) / 255.0
    # sculpt: round off the leg ending (quarter-ellipse cap over the last rows)
    import math as _m
    sculpt = np.zeros((H, W), bool)
    for leg in cfg['legs']:
        jx, jy = leg['joint']; cut = leg['cut']; fx, fy = leg['foot']; cap = cfg['cap']
        for r in range(cut-cap, cut+1):
            t = (r - (cut-cap)) / cap            # 0 at cap top, 1 at cut row
            allowed = 8.0 * _m.sqrt(max(0.0, 1 - t*t)) + 1.5
            cxr = jx + (fx - jx) * (r - jy) / max(1, (fy - jy))
            for x in range(int(cxr)-13, int(cxr)+14):
                if abs(x - cxr) > allowed:
                    sculpt[r, x] = True
    mask[sculpt] = 1.0
    # dilate 1px to eat antialias fringe of the shins
    mask = np.asarray(Image.fromarray((mask*255).astype(np.uint8)).filter(
        ImageFilter.MaxFilter(3))).astype(np.float64)/255.0
    # protect plume strands: bluish mid-tone pixels inside the mask stay original
    lum_a = a.mean(axis=2)
    strand = (lum_a > 100) & (lum_a < 205) & ((a[..., 2] - a[..., 0]) > 6)
    mask[strand] = 0.0

    # ---- donor paper (bottom-left clean region), verify cleanliness
    paper_ref = np.array([250., 237., 216.])
    donor = a[390:585, 35:240].copy()
    donor_nonpaper = (np.abs(donor - paper_ref).sum(axis=2) > 60).mean()
    # target row tint from clean left strip x 240..292 (outside mask)
    strip = a[:, 240:293]
    strip_paper = np.abs(strip - paper_ref).sum(axis=2) < 45
    row_target = np.array([strip[y][strip_paper[y]].mean(axis=0) if strip_paper[y].sum() > 8
                           else paper_ref for y in range(H)])

    filled = a.copy()
    ys, xs = np.where(mask > 0)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    dh, dw = donor.shape[:2]
    # donor row profile (for tint delta)
    donor_rows = donor.mean(axis=1)
    for y in range(y0, y1+1):
        # mirror-tile donor rows/cols
        dy_ = (y - y0) % (2*dh)
        dy_ = dy_ if dy_ < dh else 2*dh-1-dy_
        tint = row_target[y] - donor_rows[dy_]
        for x in range(x0, x1+1):
            if mask[y, x] <= 0: continue
            dx_ = (x - x0) % (2*dw)
            dx_ = dx_ if dx_ < dw else 2*dw-1-dx_
            filled[y, x] = donor[dy_, dx_] + tint
    # feathered composite
    mask_blur = np.asarray(Image.fromarray((mask*255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(1.6))).astype(np.float64)/255.0
    out = a*(1-mask_blur[..., None]) + filled*mask_blur[..., None]

    # ---- draw ripple rings at joints (supersampled layer)
    S = 4
    layer = Image.new('RGBA', (W*S, H*S), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ring_info = []
    ow, oh, iw, ih = cfg['ring']                       # outer / inner ellipse
    for leg in cfg['legs']:
        jx, cy = leg['centre']
        for (w_, h_, lw, col, al) in [(ow, oh, 1.4, (48, 45, 42), 215),
                                     (iw, ih, 2.1, (33, 31, 29), 242)]:
            # jittered ellipse path
            pts = []
            n = 90
            ph = rng.uniform(0, 6.28)
            for i in range(n+1):
                t = 2*np.pi*i/n
                jr = 1 + 0.012*np.sin(3*t+ph) + 0.008*np.sin(7*t+ph*2)
                pts.append(((jx + (w_/2)*np.cos(t)*jr)*S, (cy + (h_/2)*np.sin(t)*jr)*S))
            ld.line(pts, fill=col+(al,), width=max(1, int(lw*S)), joint='curve')
        ring_info.append(dict(joint=list(leg['joint']), ring_centre=[jx, cy],
                              outer=[ow, oh], inner=[iw, ih]))
    layer = layer.resize((W, H), Image.LANCZOS)
    out_im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert('RGBA')
    out_im.alpha_composite(layer)

    # ---- restore original thigh/knuckle tip pixels over the rings
    out_arr = np.asarray(out_im.convert('RGB')).astype(np.float64)
    dist = np.abs(a - paper_ref).sum(axis=2)
    nonpaper = dist > 60
    for leg in cfg['legs']:
        jx, jy = leg['joint']; cut = leg['cut']; cy = leg['centre'][1]
        zone = np.zeros((H, W), bool)
        zone[max(0, cy-16):cut+1, jx-13:jx+14] = True
        keep = zone & nonpaper & ~sculpt
        out_arr[keep] = a[keep]
    final = Image.fromarray(np.clip(out_arr, 0, 255).astype(np.uint8))
    out_path = os.path.join(OUT, cfg['out'])
    final.save(out_path)

    Image.fromarray((sculpt*255).astype(np.uint8)).save(
        os.path.join(BASE, 'work-knee', f'{name}_sculpt.png'))
    # ---- verification: confined diff
    diff = (np.abs(np.asarray(final).astype(int) - a.astype(int)).sum(axis=2) > 24)
    dys, dxs = np.where(diff)
    bbox = [int(dxs.min()), int(dys.min()), int(dxs.max()), int(dys.max())] if len(dxs) else None
    n_changed = int(diff.sum())
    # outside-leg-zone check: allowed region = x in [290,460], y >= min joint y - 12
    ymin_allowed = min(l['joint'][1] for l in cfg['legs']) - 12
    outside = int((diff & ~((np.indices((H, W))[1] >= 278) & (np.indices((H, W))[1] <= 468)
                            & (np.indices((H, W))[0] >= ymin_allowed))).sum())
    # ring centroid check: dark ring pixels near each joint (excluding leg silhouette cols)
    ring_meas = []
    fa = np.asarray(final).astype(int)
    for leg, ri in zip(cfg['legs'], ring_info):
        jx, jy = leg['centre']
        win = fa[jy-11:jy+12, jx-44:jx+45]
        lum = win.mean(axis=2)
        dark = lum < 110
        # exclude the leg silhouette column band and the NEIGHBOUR ring:
        dark[:, 44-8:44+9] = False
        ring_meas_cx = jx
        ys2, xs2 = np.where(dark)
        if len(xs2):
            ring_meas.append([round(float(xs2.mean()+jx-44), 1), round(float(ys2.mean()+jy-11), 1),
                              int(dark.sum())])
        else:
            ring_meas.append(None)
    h_after = sha256(src_path)
    results[name] = dict(
        src=cfg['src'], out=cfg['out'], sha_before=h_before, sha_after=h_after,
        hash_unchanged=(h_before == h_after),
        foot_ring_measured_wh=[foot_w, foot_h],
        donor_nonpaper_frac=round(float(donor_nonpaper), 4),
        diff_bbox=bbox, diff_px=n_changed, diff_outside_legzone=outside,
        rings=ring_info, ring_centroid_measured=ring_meas)
    print(name, json.dumps(results[name], indent=1))

json.dump(results, open(os.path.join(BASE, 'work-knee/measure_fix_out_knee.json'), 'w'), indent=1)
print('DONE')
