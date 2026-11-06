"""Pencil-test drawing toolkit: graphite strokes on warm paper, driven by
rig-v2.5 geometry. Works on a 'darkness' field D (0..1) at SS supersample,
composited over paper at the end."""
import math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, '/home/hatch/workspace/creature-engine/packages/great-blue-heron')
import rig_v25 as R

W, H = 1024, 600
SS = 2
GRAPHITE = np.array([52.0, 50.0, 58.0])      # blue-black graphite
PAPER_RGB = np.array([243.0, 238.0, 226.0])  # warm off-white


def make_paper(seed):
    rng = np.random.default_rng(seed)
    base = np.ones((H * SS, W * SS, 3)) * PAPER_RGB
    # low-frequency blotches
    blotch = rng.normal(0, 1, (15, 26))
    blotch = ndimage.zoom(blotch, (H * SS / 15, W * SS / 26), order=3)
    blotch = blotch / (np.abs(blotch).max() + 1e-9)
    base += (blotch * 5.0)[..., None]
    # fine grain
    base += rng.normal(0, 2.2, base.shape[:2])[..., None]
    return base


def new_D():
    return np.zeros((H * SS, W * SS), dtype=np.float64)


def _seg_draw(img, a, b, width, val):
    dr = ImageDraw.Draw(img)
    dr.line([tuple(a), tuple(b)], fill=val, width=max(int(round(width)), 1))
    r = width / 2.0
    for p in (a, b):
        dr.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=val)


def stroke(D, pts, width=2.0, alpha=0.6, jitter=0.0, passes=1, seed=0,
           taper=0.35, closed=False):
    """Sketchy polyline stroke into darkness field D (SS coords in, given in
    IMAGE coords — scaled here)."""
    rng = np.random.default_rng(seed)
    pts = np.asarray(pts, dtype=float) * SS
    if closed:
        pts = np.vstack([pts, pts[:1]])
    n = len(pts)
    for p in range(passes):
        layer = Image.new('L', (W * SS, H * SS), 0)
        if jitter > 0 and n > 2:
            # smooth random-walk offset perpendicular-ish
            off = rng.normal(0, jitter * SS, (n, 2))
            k = np.array([0.25, 0.5, 0.25])
            for c in range(2):
                off[:, c] = np.convolve(off[:, c], k, mode='same')
            q = pts + off
        else:
            q = pts
        # arc-length param for taper
        seg = np.hypot(*np.diff(q, axis=0).T)
        total = seg.sum() if seg.sum() > 0 else 1.0
        acc = 0.0
        for i in range(n - 1):
            mid = (acc + seg[i] / 2) / total
            wfac = 1.0 - taper * (abs(mid - 0.5) * 2) ** 2 if taper else 1.0
            _seg_draw(layer, q[i], q[i + 1], width * SS * max(wfac, 0.45), 255)
            acc += seg[i]
        a = np.asarray(layer, dtype=np.float64) / 255.0 * alpha
        D[:] = 1.0 - (1.0 - D) * (1.0 - a)


def dot(D, centre, r, alpha=0.9):
    layer = Image.new('L', (W * SS, H * SS), 0)
    dr = ImageDraw.Draw(layer)
    cx, cy = centre[0] * SS, centre[1] * SS
    dr.ellipse([cx - r * SS, cy - r * SS, cx + r * SS, cy + r * SS], fill=255)
    a = np.asarray(layer, dtype=np.float64) / 255.0 * alpha
    D[:] = 1.0 - (1.0 - D) * (1.0 - a)


def hatch_fill(D, mask, angle_deg=0.0, spacing=7.0, alpha=0.25, width=1.3,
               jitter=1.0, margin=3, seed=0, len_jitter=0.0, region=None,
               dropout=0.0):
    """Parallel hatch lines clipped to mask (mask at IMAGE res).
    region: optional bool mask to further restrict where hatch lands.
    dropout: probability of skipping a run segment (breaks mechanical feel)."""
    rng = np.random.default_rng(seed)
    m = ndimage.binary_erosion(mask, iterations=margin)
    if region is not None:
        m = m & region
    th = math.radians(angle_deg)
    d = np.array([math.cos(th), math.sin(th)])
    nrm = np.array([-d[1], d[0]])
    diag = math.hypot(W, H)
    offs = np.arange(-diag, diag, spacing)
    for o in offs:
        c = np.array([W / 2, H / 2]) + nrm * o
        ts = np.arange(-diag, diag, 3.0)
        pts = c[None, :] + ts[:, None] * d[None, :]
        xi = np.clip(pts[:, 0].astype(int), 0, W - 1)
        yi = np.clip(pts[:, 1].astype(int), 0, H - 1)
        inside = m[yi, xi]
        # runs
        i = 0
        while i < len(ts):
            if inside[i]:
                j = i
                while j < len(ts) and inside[j]:
                    j += 1
                run = pts[i:j]
                if len(run) >= 3 and rng.random() > dropout:
                    stroke(D, run, width=width, alpha=alpha * rng.uniform(0.75, 1.1),
                           jitter=jitter, seed=int(rng.integers(1e9)))
                i = j
            else:
                i += 1


def scribble_fill(D, mask, angle_fn, density=900, len_lo=16, len_hi=42,
                  alpha=0.3, width=1.6, margin=3, seed=0):
    """Short energetic strokes; angle_fn(x,y)->degrees gives local direction."""
    rng = np.random.default_rng(seed)
    m = ndimage.binary_erosion(mask, iterations=margin)
    ys, xs = np.nonzero(m)
    idx = rng.choice(len(xs), size=min(density, len(xs)), replace=False)
    for k in idx:
        x, y = float(xs[k]), float(ys[k])
        a = math.radians(angle_fn(x, y) + rng.normal(0, 9))
        L = rng.uniform(len_lo, len_hi)
        d = np.array([math.cos(a), math.sin(a)])
        p0, p1 = np.array([x, y]) - d * L / 2, np.array([x, y]) + d * L / 2
        if not (0 <= p0[0] < W and 0 <= p0[1] < H and 0 <= p1[0] < W and 0 <= p1[1] < H):
            continue
        if not m[int(p0[1]), int(p0[0])] or not m[int(p1[1]), int(p1[0])]:
            continue
        mid = np.array([x, y]) + np.array([-d[1], d[0]]) * rng.normal(0, 2.5)
        stroke(D, [p0, mid, p1], width=width, alpha=alpha * rng.uniform(0.7, 1.15),
               jitter=0.4, seed=int(rng.integers(1e9)))


def smudge(D, mask, blobs, base=0.16, blur=7.0, vgrad=0.10):
    """Tonal smudge fill. blobs: list of (x, y, rx, ry, strength) image coords."""
    layer = np.zeros((H, W), dtype=np.float64)
    yy, xx = np.mgrid[0:H, 0:W]
    layer += base + vgrad * (yy / H)
    for (x, y, rx, ry, s) in blobs:
        layer += s * np.exp(-(((xx - x) / rx) ** 2 + ((yy - y) / ry) ** 2))
    layer = ndimage.gaussian_filter(layer, blur / 2)
    layer = np.clip(layer, 0, 0.85) * mask
    big = ndimage.zoom(layer, SS, order=1)
    D[:] = 1.0 - (1.0 - D) * (1.0 - big)


def contour_of(mask, smooth=1.2):
    """Longest ordered boundary loop of a binary mask (image coords)."""
    fig = plt.figure()
    cs = plt.contour(mask.astype(float), levels=[0.5])
    plt.close(fig)
    best = None
    paths = []
    if hasattr(cs, 'get_paths'):
        paths = cs.get_paths()
    else:
        for coll in cs.collections:
            paths.extend(coll.get_paths())
    for path in paths:
        v = path.vertices
        if best is None or len(v) > len(best):
            best = v
    pts = best.astype(float)  # contour vertices are (x=col, y=row) = image coords
    if smooth > 0:
        k = max(int(smooth * 4) | 1, 3)
        ker = np.hanning(k); ker /= ker.sum()
        for c in range(2):
            ext = np.concatenate([pts[-k:, c], pts[:, c], pts[:k, c]])
            pts[:, c] = np.convolve(ext, ker, mode='same')[k:-k]
    return pts


def finish(D, seed, out_path):
    """Composite darkness over paper with pencil grain; save PNG 1024x600."""
    rng = np.random.default_rng(seed + 777)
    grain = 0.82 + 0.36 * rng.random(D.shape)
    grain = ndimage.gaussian_filter(grain, 0.7)
    d = np.clip(D * grain, 0, 1)
    img = Image.fromarray((d * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    d = np.asarray(img, dtype=np.float64) / 255.0
    paper = make_paper(seed)
    paper = np.asarray(Image.fromarray(paper.astype(np.uint8)).resize((W, H)), dtype=np.float64)
    out = paper * (1 - d[..., None]) + GRAPHITE * d[..., None]
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(out_path)
    return out_path


def silhouette_iou(D, mask, thresh=0.22):
    small = np.asarray(Image.fromarray((np.clip(D, 0, 1) * 255).astype(np.uint8)).resize((W, H)))
    ink = small > thresh * 255
    ink = ndimage.binary_closing(ink, iterations=2)
    filled = ndimage.binary_fill_holes(ink)
    inter = (filled & mask).sum()
    union = (filled | mask).sum()
    return float(inter / union) if union else 0.0


def rings(D, cx, cy, seed, alpha=0.55, passes=2, rx0=15.0):
    """Pencil ripple ellipses centred on the ankle joint (cx, cy)."""
    for i, rx in enumerate((rx0, rx0 * 1.55, rx0 * 2.2)):
        th = np.linspace(0, 2 * math.pi, 60)
        pts = np.stack([cx + rx * np.cos(th), cy + rx * 0.26 * np.sin(th)], axis=1)
        stroke(D, pts, width=1.5, alpha=alpha * (1 - i * 0.25), jitter=0.8,
               passes=passes, seed=seed + i * 13, closed=True, taper=0.0)


# ---------------------------------------------------------------- pose data
def pose_geom(name):
    img, dv, eye = R.render(name)
    mask = np.array(img) < 128
    spec = R.ANIMAL['poses'][name]
    skull = dv['skull']
    fh = math.radians(dv['heads'][-1] + spec['head_pitch_offset_deg'])
    dvec = np.array([math.cos(fh), math.sin(fh)])
    ha = R.ANIMAL['head_assembly']
    bill_tip = skull + dvec * ha['bill_tip_reach_from_skull_centre'] * R.T
    bill_base = skull + dvec * ha['bill_base_offset_from_skull_centre'] * R.T
    return dict(mask=mask, dv=dv, eye=np.array(eye, dtype=float), skull=skull,
                dvec=dvec, bill_tip=bill_tip, bill_base=bill_base,
                chain=dv['pts'], neckbase=dv['neckbase'],
                legs=R.LEGS_BY_POSE[name], contour=contour_of(mask))


def draw_eye(D, g, r=3.6, alpha=0.92):
    dot(D, g['eye'], r, alpha)
    # brow line
    d = g['dvec']; p = np.array([-d[1], d[0]])
    a = g['eye'] - d * 7 + p * 3.5
    b = g['eye'] + d * 8 + p * 4.5
    stroke(D, [a, b], width=1.4, alpha=0.6, seed=5)


def plume_strands(D, root, seed, n=9, length=(46, 78), alpha=0.5, spread=16.0):
    rng = np.random.default_rng(seed)
    for i in range(n):
        x0 = root[0] + rng.uniform(-spread, spread * 0.4)
        y0 = root[1] + rng.uniform(-6, 10)
        L = rng.uniform(*length)
        bend = rng.uniform(-7, 7)
        pts = [(x0, y0), (x0 + bend * 0.4, y0 + L * 0.55), (x0 + bend, y0 + L)]
        stroke(D, pts, width=1.15, alpha=alpha * rng.uniform(0.7, 1.1),
               jitter=0.7, seed=int(rng.integers(1e9)))
