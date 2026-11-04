#!/usr/bin/env python3
"""FILL SPIKE v1 — one method, one honest shot (Jimmy's path-3 go, 2026-11-04).

Method (the approved design, nothing else):
  1. Donor texture transfer, mask-conditioned: registered gold frames
     (EXCLUDING the gate frame's own pair) are warped into the target
     frame's rig geometry (similarity fit on silhouettes), then pasted
     REGION BY REGION over the target's visible-region label map
     (rig v2.4 mask stack, painter order). One donor per region,
     chosen by a corpus-side rule: the donor whose regional black
     fraction (in target geometry) is closest to the regional ink
     TARGET. Residual per-region translation aligns each pasted
     region to the donor-family consensus centroid.
  2. Structural ink: per-region quantile luminance remap so each
     region's black fraction (lum<70, the v3 metric's definition)
     equals its target. Regional targets are the APPROVED STILL's
     regional black fractions (idle: scaled by original/registered
     0.2593/0.2389 — the registration softening correction; strike:
     as registered, the gate's own basis). A final global trim to
     band centre runs only if the overall fraction is outside the
     gate band, and never touches the drawn bill/eye.
  3. Explicit structures from rig geometry: the BILL is redrawn from
     the bill_poly wedge (appearance profile = (axial, cross) median
     colours extracted from the approved rest still, plus its mouth
     line and outline); the EYE is drawn at its approved-still offset
     in the head frame; crest and breast-plume strands are reinforced
     in geometry-defined zones (darken line cores, reconnect breaks)
     — no new lines are invented.

Deterministic throughout: fixed donor rules, no RNG, integer shifts,
exact quantile remaps. Same canvas in -> same frame out.
"""
import copy, csv, hashlib, json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

HOME = os.path.expanduser('~')
ART2 = f'{HOME}/workspace/heron/art2'
FS = f'{ART2}/finished-art-stills'
FM3 = f'{FS}/finish-model-v3'
SPIKE = f'{ART2}/fill-spike-v1'
sys.path.insert(0, ART2)
sys.path.insert(0, f'{HOME}/workspace/heron/src13')
sys.path.insert(0, FM3)
import build_corpus as bc          # stack_for, fit, _Minv (v3 corpus machinery)
import roster_render_v24 as RR

W, H = 1024, 600
ORDER = [0, 3, 6, 5, 4, 1, 7, 2]   # painter order (build_corpus.PALETTE)
NAMES = {0: 'torso', 1: 'neck', 2: 'head', 3: 'wing', 4: 'leg_near',
         5: 'leg_far', 6: 'tail', 7: 'plume'}

# ---------- metric instrument (measure_v3.py, verbatim) ----------
def load(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.float32)

def paper_color(a):
    patches = [a[:40, :40], a[:40, -40:], a[-40:, :40], a[-40:, -40:]]
    return np.median(np.concatenate([p.reshape(-1, 3) for p in patches]), axis=0)

def content_mask(a):
    pc = paper_color(a)
    return np.abs(a - pc).sum(axis=2) > 55

def color_fracs(a, mask):
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    n = max(mask.sum(), 1)
    black = mask & (a.mean(axis=2) < 70)
    rust = mask & (r > 95) & (r - g > 22) & (r - b > 40)
    yellow = mask & (r > 150) & (g > 95) & (b < 120) & (r - b > 60)
    slate = mask & (b > r + 4) & (a.mean(axis=2) > 60) & (a.mean(axis=2) < 190)
    return dict(black=float(black.sum() / n), rust=float(rust.sum() / n),
                yellow=float(yellow.sum() / n), slate=float(slate.sum() / n))

def iou(m0, m1):
    u = (m0 | m1).sum()
    return float((m0 & m1).sum() / u) if u else 1.0

# ---------- geometry helpers ----------
def labelmap(stack):
    lab = np.full((H, W), -1, int)
    for ch in ORDER:
        lab[stack[ch] > 0] = ch
    return lab

def warp_img(img, prm):
    s, th, dx, dy = prm
    Minv, off = bc._Minv(s, th, dx, dy)
    pc = paper_color(img)
    return np.stack([ndimage.affine_transform(img[:, :, c], Minv, offset=off,
                     output_shape=(H, W), order=1, mode='constant', cval=pc[c])
                     for c in range(3)], axis=2)

def warp_mask(m, prm):
    s, th, dx, dy = prm
    Minv, off = bc._Minv(s, th, dx, dy)
    return ndimage.affine_transform(m.astype(float), Minv, offset=off,
                                    output_shape=(H, W), order=1,
                                    mode='constant', cval=0) > 0.5

def centroid(m):
    ys, xs = np.nonzero(m)
    return np.array([xs.mean(), ys.mean()]) if len(xs) else None

# ---------- structural ink ----------
def ink_remap(img, setmask, target_black):
    """Quantile-anchored luminance remap: after the remap, the fraction
    of set pixels with lum<70 equals target_black (up to ties). Hue is
    preserved (RGB scaled by lum'/lum)."""
    lum = img.mean(axis=2)
    vals = lum[setmask]
    if len(vals) < 50 or target_black <= 0:
        return img
    v_q = np.quantile(vals, target_black)
    if v_q <= 1:
        return img
    new = img.copy()
    scale = np.ones_like(lum)
    dark = lum <= v_q
    scale[dark] = 70.0 / v_q
    if v_q < 254:
        bright = ~dark
        scale[bright] = (70.0 + (lum[bright] - v_q) * (255.0 - 70.0) / (255.0 - v_q)) \
                        / np.maximum(lum[bright], 1e-6)
    new = img * scale[:, :, None]
    out = img.copy()
    out[setmask] = new[setmask]
    return np.clip(out, 0, 255)

# ---------- bill profile (from the approved rest still) ----------
def bill_triangle(kp):
    bp = [tuple(map(float, p)) for p in kp['bill_poly']]
    return np.array([bp[9], bp[10], bp[11]])   # top-base, tip, bottom-base

def tri_coords(pts_yx, tri):
    """Barycentric (s, cross) for pixels: s = a+b (0 at base segment,
    1 at tip), cross = (a-b)/max(s,0.15) in [-1,1]. pts as (y,x)."""
    A = np.array([tri[0][1], tri[0][0]])  # (y,x) of top-base
    B = np.array([tri[1][1], tri[1][0]])
    C = np.array([tri[2][1], tri[2][0]])
    P = pts_yx.astype(float)
    M = np.stack([B - A, C - A], axis=1)
    ab = np.einsum('ij,nj->ni', np.linalg.inv(M), P - A)
    a_, b_ = ab[:, 0], ab[:, 1]
    s = a_ + b_
    cross = (a_ - b_) / np.maximum(s, 0.15)
    inside = (a_ >= -0.02) & (b_ >= -0.02) & (s <= 1.02)
    return s, cross, inside

def extract_bill_profile():
    gold = load(f'{FM3}/corpus/target/idle_f0030.png')
    tracks24 = json.load(open(f'{FS}/rig-v2/band-pass/pose_tracks_v24.json'))
    kp = RR.kp_master(tracks24['idle'][0])
    tri = bill_triangle(kp)
    ys, xs = np.mgrid[0:H, 0:W]
    s, cross, inside = tri_coords(np.stack([ys.ravel(), xs.ravel()], 1),
                                  tri)
    s = s.reshape(H, W); cross = cross.reshape(H, W); inside = inside.reshape(H, W)
    sb = np.clip((s * 12).astype(int), 0, 11)
    cb = np.clip(((cross + 1) / 2 * 5).astype(int), 0, 4)
    prof = np.zeros((12, 5, 3))
    for i in range(12):
        for j in range(5):
            m = inside & (sb == i) & (cb == j)
            prof[i, j] = np.median(gold[m], axis=0) if m.sum() >= 8 else np.nan
    # fill empty bins from nearest filled bin
    for i in range(12):
        for j in range(5):
            if np.isnan(prof[i, j, 0]):
                d2 = [(abs(i - a) + abs(j - b), a, b) for a in range(12)
                      for b in range(5) if not np.isnan(prof[a, b, 0])]
                _, a, b = min(d2)
                prof[i, j] = prof[a, b]
    # mouth line: darkest cross bin per mid-t bin of the gold bill
    lum = gold.mean(axis=2)
    line = []
    for i in range(2, 10):
        mids = []
        for j in range(5):
            m = inside & (sb == i) & (cb == j)
            if m.sum() >= 8:
                mids.append((float(np.median(lum[m])), (j + 0.5) / 5 * 2 - 1))
        line.append((i / 12, min(mids)[1]))
    lt = np.array([p[0] for p in line]); lc = np.array([p[1] for p in line])
    coef = np.polyfit(lt, lc, 1)
    linepix = inside & (np.abs(cross - np.polyval(coef, s)) < 0.10) & (s > 0.1) & (s < 0.95)
    line_col = np.median(gold[linepix], axis=0)
    # outline colour: gold pixels within 1.5 px of the triangle boundary
    tri_m = inside.copy()
    er = ndimage.binary_erosion(tri_m, iterations=1)
    outline_col = np.median(gold[tri_m & ~er], axis=0)
    # eye: iris cluster in the skull (head channel minus bill triangle)
    stack = bc.stack_for(tracks24['idle'][0])
    skull = (stack[2] > 0) & ~ndimage.binary_dilation(tri_m, iterations=2)
    r, g, b = gold[:, :, 0], gold[:, :, 1], gold[:, :, 2]
    iris = skull & (r > 100) & (r < 215) & (g > 55) & (g < 145) & (b < 85) & ((r - b) > 70)
    lab, n = ndimage.label(iris)
    sizes = ndimage.sum(iris, lab, range(1, n + 1)) if n else []
    eye_c = None; iris_col = np.array([176., 128., 44.])
    if n:
        k = 1 + int(np.argmax(sizes))
        ys2, xs2 = np.nonzero(lab == k)
        eye_c = np.array([xs2.mean(), ys2.mean()])
        iris_col = np.median(gold[lab == k], axis=0)
    hc = np.array(kp['head_c'], float); tip = np.array(kp['bill_tip'], float)
    ax = tip - hc; ax = ax / np.hypot(*ax)
    perp = np.array([-ax[1], ax[0]])
    uv = np.array([(eye_c - hc) @ ax, (eye_c - hc) @ perp]) if eye_c is not None else None
    return dict(profile=prof, line_coef=coef, line_col=line_col,
                outline_col=outline_col, eye_uv=uv, iris_col=iris_col,
                eye_xy=eye_c)

def draw_bill(img, kp, prof):
    tri = bill_triangle(kp)
    ys, xs = np.mgrid[0:H, 0:W]
    s, cross, inside = tri_coords(np.stack([ys.ravel(), xs.ravel()], 1), tri)
    s = s.reshape(H, W); cross = cross.reshape(H, W); inside = inside.reshape(H, W)
    sf = np.clip(s * 12 - 0.5, 0, 11); cf = np.clip((cross + 1) / 2 * 5 - 0.5, 0, 4)
    s0 = np.floor(sf).astype(int); c0 = np.floor(cf).astype(int)
    s1 = np.minimum(s0 + 1, 11); c1 = np.minimum(c0 + 1, 4)
    fs = (sf - s0)[:, :, None]; fc = (cf - c0)[:, :, None]
    P = prof['profile']
    col = (P[s0, c0] * (1 - fs) * (1 - fc) + P[s1, c0] * fs * (1 - fc) +
           P[s0, c1] * (1 - fs) * fc + P[s1, c1] * fs * fc)
    out = img.copy()
    out[inside] = col[inside]
    # mouth line
    lc = np.polyval(prof['line_coef'], s)
    line_m = inside & (np.abs(cross - lc) < 0.09) & (s > 0.08) & (s < 0.97)
    out[line_m] = out[line_m] * 0.35 + prof['line_col'] * 0.65
    # outline
    er = ndimage.binary_erosion(inside, iterations=1)
    out[inside & ~er] = prof['outline_col']
    return out, inside

def draw_eye(img, kp, prof):
    if prof['eye_uv'] is None:
        return img
    hc = np.array(kp['head_c'], float); tip = np.array(kp['bill_tip'], float)
    ax = tip - hc; ax = ax / np.hypot(*ax)
    perp = np.array([-ax[1], ax[0]])
    c = hc + prof['eye_uv'][0] * ax + prof['eye_uv'][1] * perp
    ys, xs = np.mgrid[0:H, 0:W]
    d = np.hypot(xs - c[0], ys - c[1])
    out = img.copy()
    out[d <= 5.0] = prof['iris_col']
    out[d <= 2.4] = np.array([18., 15., 12.])
    return out

def reinforce_strands(img, zone, core_lum=105, dark_mul=0.5):
    lum = img.mean(axis=2)
    core = zone & (lum < core_lum)
    near = ndimage.binary_dilation(core, iterations=2) & zone & (lum < 175)
    out = img.copy()
    out[near] = out[near] * 0.72
    out[core] = out[core] * dark_mul
    grow = ndimage.binary_dilation(core, iterations=1) & zone
    out[grow] = out[grow] * 0.55 + np.array([30., 27., 24.]) * 0.45
    return out

# ---------- frame builder ----------
def build(target_key, pose, donors, gate_pair, region_targets, band,
          band_centre, kp):
    tstack = bc.stack_for(pose)
    tlab = labelmap(tstack)
    tsil = np.any(tstack > 0, axis=0)
    # --- warp donors into target geometry ---
    D = []
    for pid, img, stack in donors:
        dsil = np.any(stack > 0, axis=0)
        if np.array_equal(dsil, tsil):
            prm = (1.0, 0.0, 0.0, 0.0); wimg = img; wstack = stack
            sil_iou = 1.0
        else:
            _, s, th, dx, dy = bc.fit(dsil, tsil)
            prm = (s, th, dx, dy)
            wimg = warp_img(img, prm)
            wstack = np.stack([warp_mask(stack[c] > 0, prm) for c in range(8)])
            sil_iou = iou(np.any(wstack > 0, axis=0), tsil)
        D.append(dict(pid=pid, img=wimg, stack=wstack, sil_iou=sil_iou, prm=prm))
    # base donor: idle -> median overall black; strike -> best silhouette IoU
    if target_key == 'idle':
        vals = [color_fracs(d['img'], content_mask(d['img']))['black'] for d in D]
        med = float(np.median(vals))
        base = min(D, key=lambda d: (abs(color_fracs(d['img'], content_mask(d['img']))['black'] - med), d['pid']))
    else:
        base = max(D, key=lambda d: (d['sil_iou'], d['pid']))
    img = base['img'].copy()
    log = dict(base_donor=base['pid'], regions={})
    # --- per-region composite ---
    # consensus centroids per region (median of warped donors' centroids)
    for ch in ORDER:
        tm = tlab == ch
        if tm.sum() == 0:
            continue
        cents = [centroid(d['stack'][ch] > 0) for d in D]
        cents = [c for c in cents if c is not None]
        cons = np.median(np.stack(cents), axis=0) if cents else None
        tgt = region_targets[ch]
        def regblack(d):
            return float((d['img'].mean(axis=2)[tm] < 70).mean())
        pick = min(D, key=lambda d: (abs(regblack(d) - tgt), d['pid']))
        src = pick['img']
        cen = centroid(pick['stack'][ch] > 0)
        if cons is not None and cen is not None:
            shift = np.round(cons - cen).astype(int)
            shift = np.clip(shift, -10, 10)
            if shift.any():
                src = ndimage.shift(src, (shift[1], shift[0], 0), order=1,
                                    mode='nearest')
        dist = ndimage.distance_transform_edt(tm)
        alpha = np.clip(dist / 3.0, 0, 1)[:, :, None]
        img = img * (1 - alpha) + src * alpha
        log['regions'][NAMES[ch]] = dict(donor=pick['pid'],
                                         donor_black=round(regblack(pick), 4),
                                         target=round(tgt, 4))
    # --- structural ink: per-region remap ---
    lum = img.mean(axis=2)
    for ch in ORDER:
        img = ink_remap(img, tlab == ch, region_targets[ch])
    over = (tlab < 0) & content_mask(img)
    img = ink_remap(img, over, region_targets['overhang'])
    # --- explicit structures ---
    prof = extract_bill_profile()
    img, bill_m = draw_bill(img, kp, prof)
    img = draw_eye(img, kp, prof)
    # crest zone: behind the head, off the body channels
    hc = np.array(kp['head_c'], float); tip = np.array(kp['bill_tip'], float)
    ax = tip - hc; ax = ax / np.hypot(*ax)
    ys, xs = np.mgrid[0:H, 0:W]
    rel = np.stack([xs - hc[0], ys - hc[1]], axis=2)
    proj = rel @ ax
    crest_zone = (np.hypot(rel[:, :, 0], rel[:, :, 1]) < 250) & (proj < 25) \
        & ~((tstack[0] > 0) | (tstack[3] > 0) | (tstack[6] > 0))
    img = reinforce_strands(img, crest_zone)
    # plume zone: plume channel extended downward (hanging strands)
    plume = tstack[7] > 0
    zone = plume.copy()
    for k in range(1, 41):
        zone[k:] |= plume[:-k]
    zone = ndimage.binary_dilation(zone, iterations=2)
    img = reinforce_strands(img, zone, core_lum=115, dark_mul=0.55)
    # --- global trim to band centre (bill/eye protected) ---
    prot = bill_m.copy()
    if prof['eye_uv'] is not None:
        perp = np.array([-ax[1], ax[0]])
        c = hc + prof['eye_uv'][0] * ax + prof['eye_uv'][1] * perp
        prot |= np.hypot(xs - c[0], ys - c[1]) <= 7
    for _ in range(3):
        cm = content_mask(img)
        b = color_fracs(img, cm)['black']
        if band[0] <= b <= band[1]:
            break
        img = ink_remap(img, cm & ~prot, band_centre)
    return img, log

def bill_centroid_y(a, mask):
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    yel = mask & (r > 150) & (g > 95) & (b < 120) & (r - b > 60)
    ys, _ = np.nonzero(yel)
    return round(float(ys.mean()), 1) if len(ys) else None

def measure(img, gold_path):
    g = load(gold_path); gm = content_mask(g)
    m = content_mask(img)
    u = m | gm
    return dict(fracs={k: round(v, 4) for k, v in color_fracs(img, m).items()},
                gold_fracs={k: round(v, 4) for k, v in color_fracs(g, gm).items()},
                iou_vs_gold=round(iou(m, gm), 4),
                mad_bird=round(float(np.abs(img - g)[u].mean()), 2),
                bill_y=bill_centroid_y(img, m),
                bill_y_gold=bill_centroid_y(g, gm))

def sidebyside(mine, gold_reg, gold_orig, path, labels):
    imgs = [mine, gold_reg, gold_orig]
    strip = np.full((630, 1024 * 3, 3), 255, np.uint8)
    for i, a in enumerate(imgs):
        strip[30:630, i * 1024:(i + 1) * 1024] = np.clip(a, 0, 255).astype(np.uint8)
    Image.fromarray(strip).save(path)

def main():
    os.makedirs(f'{SPIKE}/work', exist_ok=True)
    man = {r['pair_id']: r for r in csv.DictReader(open(f'{FM3}/corpus_manifest.csv'))}
    tracks24 = json.load(open(f'{FS}/rig-v2/band-pass/pose_tracks_v24.json'))
    tracks2 = json.load(open(f'{FS}/rig-v2/work/pose_tracks_v2.json'))

    # ---------- GATE A: the standing hold ----------
    idle_pose = tracks24['idle'][0]
    istack = bc.stack_for(idle_pose)
    donorsA = []
    for pid, r in man.items():
        if r['family'] == 'idle' and pid != 'idle_f0030':
            donorsA.append((pid, load(f'{FM3}/corpus/target/{pid}.png'), istack))
    goldA = load(f'{FM3}/corpus/target/idle_f0030.png')
    labA = labelmap(istack)
    lumA = goldA.mean(axis=2); cmA = content_mask(goldA)
    corr = 0.2593 / 0.2389
    tgtA = {}
    for ch in ORDER:
        m = labA == ch
        tgtA[ch] = float((m & (lumA < 70)).sum() / m.sum()) * corr
    tgtA['overhang'] = float(((labA < 0) & cmA & (lumA < 70)).sum() /
                             max(((labA < 0) & cmA).sum(), 1)) * corr
    kpA = RR.kp_master(idle_pose)
    imgA, logA = build('idle', idle_pose, donorsA, 'idle_f0030', tgtA,
                       (0.252, 0.272), 0.262, kpA)
    Image.fromarray(np.clip(imgA, 0, 255).astype(np.uint8)).save(f'{SPIKE}/hold_fill.png')
    mA = measure(imgA, f'{FM3}/corpus/target/idle_f0030.png')
    sidebyside(imgA, goldA, load(f'{FS}/audubon_rest.png'),
               f'{SPIKE}/sidebyside_hold.png', None)
    print('GATE A log:', json.dumps(logA))
    print('GATE A measure:', json.dumps(mA))

    # ---------- GATE B: full-extension strike f0027 ----------
    poseB = tracks2['strike'][27]
    donorsB = []
    for i in list(range(18, 27)) + list(range(28, 37)):
        pid = f'strike_f{i:04d}'
        donorsB.append((pid, load(f'{FM3}/corpus/target/{pid}.png'),
                        bc.stack_for(tracks2['strike'][i])))
    goldB = load(f'{FM3}/corpus/target/strike_f0027.png')
    stackB = bc.stack_for(poseB)
    labB = labelmap(stackB)
    lumB = goldB.mean(axis=2); cmB = content_mask(goldB)
    tgtB = {}
    for ch in ORDER:
        m = labB == ch
        tgtB[ch] = float((m & (lumB < 70)).sum() / max(m.sum(), 1))
    tgtB['overhang'] = float(((labB < 0) & cmB & (lumB < 70)).sum() /
                             max(((labB < 0) & cmB).sum(), 1))
    kpB = RR.kp_master(poseB)
    imgB, logB = build('strike', poseB, donorsB, 'strike_f0027', tgtB,
                       (0.361, 0.381), 0.371, kpB)
    Image.fromarray(np.clip(imgB, 0, 255).astype(np.uint8)).save(f'{SPIKE}/strike_f0027_fill.png')
    mB = measure(imgB, f'{FM3}/corpus/target/strike_f0027.png')
    sidebyside(imgB, goldB, load(f'{FS}/audubon_strike.png'),
               f'{SPIKE}/sidebyside_strike_f0027.png', None)
    print('GATE B log:', json.dumps(logB))
    print('GATE B measure:', json.dumps(mB))

    # determinism: rebuild the hold and compare hashes
    imgA2, _ = build('idle', idle_pose, donorsA, 'idle_f0030', tgtA,
                     (0.252, 0.272), 0.262, kpA)
    h1 = hashlib.md5(np.clip(imgA, 0, 255).astype(np.uint8).tobytes()).hexdigest()
    h2 = hashlib.md5(np.clip(imgA2, 0, 255).astype(np.uint8).tobytes()).hexdigest()
    print('determinism hold:', h1 == h2, h1[:12], h2[:12])
    json.dump(dict(gateA=mA, gateB=mB, logA=logA, logB=logB,
                   targetsA={NAMES[k]: round(v, 4) for k, v in tgtA.items() if k != 'overhang'} | {'overhang': round(tgtA['overhang'], 4)},
                   targetsB={NAMES[k]: round(v, 4) for k, v in tgtB.items() if k != 'overhang'} | {'overhang': round(tgtB['overhang'], 4)},
                   determinism_hold=(h1 == h2)),
              open(f'{SPIKE}/work/metrics_spike.json', 'w'), indent=1)
    print('WROTE metrics_spike.json')

if __name__ == '__main__':
    main()
