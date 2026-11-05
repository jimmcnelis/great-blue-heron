#!/usr/bin/env python3
"""WATERLINE DEPTH LADDER — ALERT plate (plate_1) only.
Five variants differing ONLY in waterline seat: the ripple rings' vertical
position relative to the rusty->dark transition on the legs. Leg endings and
rings move together (cut = ring centre + 4, as in the shipped corrections).
D1 (-8) / D2 (0) / D5 (+32) are built from the original master with the same
pipeline as work-knee/knee_correct.py, one fixed seed so ring jitter is
identical across built variants. D3 (+7) and D4 (+19) ARE the shipped
plate_1_knee.png / plate_1_knee2.png (per brief). Every variant is labelled
"D1".."D5" in the bottom-left corner, light grey — selection proofs.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import json, hashlib, os, math

BASE = os.path.expanduser('~/workspace/heron/art2/plates-fresh/eye-first')
CORR = os.path.join(BASE, 'corrected')
OUT = os.path.join(CORR, 'ladder')
WORK = os.path.join(OUT, 'work')
os.makedirs(WORK, exist_ok=True)

SRC = os.path.join(BASE, 'ranked/plate_1.png')
KNEE = os.path.join(CORR, 'plate_1_knee.png')
KNEE2 = os.path.join(CORR, 'plate_1_knee2.png')

# plate_1 geometry, from the shipped knee-correction work
HW, CAP = 17, 5
ERASE_RX, ERASE_RY = 54, 24
RING = (78, 16, 46, 10)  # outer w,h / inner w,h
LEGS = [dict(joint=(363, 411), foot=(343, 537)),
        dict(joint=(404, 415), foot=(404, 537))]
PAPER_REF = np.array([250., 237., 216.])
SEED = 20261104

def sha256(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()

def centreline_x(leg, y):
    jx, jy = leg['joint']; fx, fy = leg['foot']
    return jx + (fx - jx) * (y - jy) / max(1, (fy - jy))

def build_variant(orig, offset):
    """Same pipeline as knee_correct.py, ring centre = transition + offset."""
    W, H = orig.size
    a = np.asarray(orig).astype(np.float64)
    rng = np.random.default_rng(SEED)
    legs = []
    for leg in LEGS:
        jx, jy = leg['joint']
        cy = jy + offset
        cx = int(round(centreline_x(leg, cy)))
        legs.append(dict(joint=leg['joint'], foot=leg['foot'],
                         centre=(cx, cy), cut=cy + 4))

    # ---- erase mask (corridor + foot ellipse), as knee_correct.py
    mask_img = Image.new('L', (W, H), 0)
    md = ImageDraw.Draw(mask_img)
    for leg in legs:
        jx, jy = leg['joint']; cut = leg['cut']; fx, fy = leg['foot']
        dx, dy = fx - jx, 560 - cut
        L = math.hypot(dx, dy); ux, uy = dx / L, dy / L; px_, py_ = -uy, ux
        pts = [(jx + px_ * HW, cut + py_ * 0), (jx - px_ * HW, cut - py_ * 0),
               (fx - px_ * HW, 562 - py_ * 0), (fx + px_ * HW, 562 + py_ * 0)]
        md.polygon(pts, fill=255)
        md.ellipse([fx - ERASE_RX, fy - ERASE_RY, fx + ERASE_RX, fy + ERASE_RY], fill=255)
    mask = np.asarray(mask_img).astype(np.float64) / 255.0
    # sculpt: round off the leg ending (quarter-ellipse cap)
    sculpt = np.zeros((H, W), bool)
    for leg in legs:
        cut = leg['cut']
        for r in range(cut - CAP, cut + 1):
            t = (r - (cut - CAP)) / CAP
            allowed = 8.0 * math.sqrt(max(0.0, 1 - t * t)) + 1.5
            cxr = centreline_x(leg, r)
            for x in range(int(cxr) - 13, int(cxr) + 14):
                if abs(x - cxr) > allowed:
                    sculpt[r, x] = True
    mask[sculpt] = 1.0
    mask = np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).filter(
        ImageFilter.MaxFilter(3))).astype(np.float64) / 255.0
    # protect plume strands (bluish mid-tones stay original)
    lum_a = a.mean(axis=2)
    strand = (lum_a > 100) & (lum_a < 205) & ((a[..., 2] - a[..., 0]) > 6)
    mask[strand] = 0.0

    # ---- donor paper fill (same-plate donor, row-tinted, feathered)
    donor = a[390:585, 35:240].copy()
    strip = a[:, 240:293]
    strip_paper = np.abs(strip - PAPER_REF).sum(axis=2) < 45
    row_target = np.array([strip[y][strip_paper[y]].mean(axis=0) if strip_paper[y].sum() > 8
                           else PAPER_REF for y in range(H)])
    filled = a.copy()
    ys, xs = np.where(mask > 0)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    dh, dw = donor.shape[:2]
    donor_rows = donor.mean(axis=1)
    for y in range(y0, y1 + 1):
        dy_ = (y - y0) % (2 * dh)
        dy_ = dy_ if dy_ < dh else 2 * dh - 1 - dy_
        tint = row_target[y] - donor_rows[dy_]
        for x in range(x0, x1 + 1):
            if mask[y, x] <= 0: continue
            dx_ = (x - x0) % (2 * dw)
            dx_ = dx_ if dx_ < dw else 2 * dw - 1 - dx_
            filled[y, x] = donor[dy_, dx_] + tint
    mask_blur = np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(1.6))).astype(np.float64) / 255.0
    out = a * (1 - mask_blur[..., None]) + filled * mask_blur[..., None]

    # ---- ripple rings in the plates' own hand (supersampled)
    S = 4
    layer = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ow, oh, iw, ih = RING
    for leg in legs:
        cx, cy = leg['centre']
        for (w_, h_, lw, col, al) in [(ow, oh, 1.4, (48, 45, 42), 215),
                                      (iw, ih, 2.1, (33, 31, 29), 242)]:
            pts = []
            n = 90
            ph = rng.uniform(0, 6.28)
            for i in range(n + 1):
                t = 2 * np.pi * i / n
                jr = 1 + 0.012 * np.sin(3 * t + ph) + 0.008 * np.sin(7 * t + ph * 2)
                pts.append(((cx + (w_ / 2) * np.cos(t) * jr) * S,
                            (cy + (h_ / 2) * np.sin(t) * jr) * S))
            ld.line(pts, fill=col + (al,), width=max(1, int(lw * S)), joint='curve')
    layer = layer.resize((W, H), Image.LANCZOS)
    out_im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert('RGBA')
    out_im.alpha_composite(layer)

    # ---- restore original leg-tip pixels over the rings (arcs pass behind)
    out_arr = np.asarray(out_im.convert('RGB')).astype(np.float64)
    dist = np.abs(a - PAPER_REF).sum(axis=2)
    nonpaper = dist > 60
    for leg in legs:
        cy = leg['centre'][1]; cut = leg['cut']
        for r in range(max(0, cy - 16), cut + 1):
            cxr = centreline_x(leg, r)
            c0, c1 = int(round(cxr)) - 13, int(round(cxr)) + 14
            keep = nonpaper[r, c0:c1] & ~sculpt[r, c0:c1]
            out_arr[r, c0:c1][keep] = a[r, c0:c1][keep]
    final = Image.fromarray(np.clip(out_arr, 0, 255).astype(np.uint8))
    return final, legs

# ---------------------------------------------------------------- build all
orig = Image.open(SRC).convert('RGB')
W, H = orig.size
orig_arr = np.asarray(orig).astype(int)

variants = {}   # name -> (image, offset, source_desc, legs_info)
built, legs1 = build_variant(orig, -8)
variants['D1'] = (built, -8, 'built from original master', legs1)
built, legs2 = build_variant(orig, 0)
variants['D2'] = (built, 0, 'built from original master', legs2)
variants['D3'] = (Image.open(KNEE).convert('RGB'), 7, 'plate_1_knee.png as shipped',
                  [dict(centre=(363, 418), cut=422), dict(centre=(404, 422), cut=426)])
variants['D4'] = (Image.open(KNEE2).convert('RGB'), 19, 'plate_1_knee2.png as shipped',
                  [dict(centre=(359, 430), cut=434), dict(centre=(404, 434), cut=438)])
built, legs5 = build_variant(orig, 32)
variants['D5'] = (built, 32, 'built from original master', legs5)

# ---- labels (bottom-left corner, light grey) + save
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 22)
LABEL_BOX = (8, 552, 84, 596)  # excluded zone in diff accounting
saved = {}
for name in ['D1', 'D2', 'D3', 'D4', 'D5']:
    im, off, src_desc, legs = variants[name]
    im = im.copy()
    d = ImageDraw.Draw(im)
    d.text((16, 564), name, font=font, fill=(150, 144, 132))
    p = os.path.join(OUT, f'alert_{name}.png')
    im.save(p)
    saved[name] = p

# ---- verification: confined diff vs the original master
yy, xx = np.indices((H, W))
in_legband = (xx >= 270) & (xx <= 470) & (yy >= 380)
in_label = (xx >= LABEL_BOX[0]) & (xx <= LABEL_BOX[2]) & (yy >= LABEL_BOX[1]) & (yy <= LABEL_BOX[3])
results = {}
for name in ['D1', 'D2', 'D3', 'D4', 'D5']:
    im = Image.open(saved[name]).convert('RGB')
    arr = np.asarray(im).astype(int)
    diff = (np.abs(arr - orig_arr).sum(axis=2) > 24)
    dys, dxs = np.where(diff)
    results[name] = dict(
        offset_spec=variants[name][1], source=variants[name][2],
        centres=[list(l['centre']) for l in variants[name][3]],
        cuts=[l['cut'] for l in variants[name][3]],
        diff_px=int(diff.sum()),
        diff_bbox=[int(dxs.min()), int(dys.min()), int(dxs.max()), int(dys.max())],
        diff_outside_legband_and_label=int((diff & ~in_legband & ~in_label).sum()),
        diff_in_labelbox=int((diff & in_label).sum()))
    # sanity: ring bottom-arc seat measured on the finished PNG
    fa = arr.astype(float)
    lum = fa.mean(axis=2)
    seats = []
    for leg, linfo in zip(LEGS, variants[name][3]):
        cx, cy = linfo['centre']
        cols = list(range(cx - 34, cx - 17)) + list(range(cx + 18, cx + 35))
        bottoms = []
        for c in cols:
            dark_rows = np.where(lum[cy - 14:cy + 15, c] < 120)[0]
            if len(dark_rows):
                bottoms.append(dark_rows.max() + cy - 14)
        bottom = float(np.median(bottoms)) if bottoms else None
        seats.append(dict(drawn_centre=[cx, cy],
                          bottom_arc_y=bottom,
                          implied_centre_y=(bottom - RING[1] / 2) if bottom else None,
                          implied_offset_vs_transition=(
                              (bottom - RING[1] / 2) - leg['joint'][1]) if bottom else None))
    results[name]['seat_measure'] = seats

# D3/D4 must equal their shipped sources outside the label box
for name, srcf in [('D3', KNEE), ('D4', KNEE2)]:
    sarr = np.asarray(Image.open(srcf).convert('RGB')).astype(int)
    varr = np.asarray(Image.open(saved[name]).convert('RGB')).astype(int)
    d = (np.abs(varr - sarr).sum(axis=2) > 24)
    results[name]['diff_vs_shipped_source_px'] = int(d.sum())
    results[name]['diff_vs_source_outside_label'] = int((d & ~in_label).sum())

hashes = {p: sha256(p) for p in [SRC, KNEE, KNEE2]}
results['_hashes'] = hashes
json.dump(results, open(os.path.join(WORK, 'ladder_measure.json'), 'w'), indent=1)
print(json.dumps(results, indent=1))
print('DONE')
