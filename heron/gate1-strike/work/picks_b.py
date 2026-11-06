"""Round 2 recipes: bowed wing mass, shadow-only hatch, fixed plume,
smudge smears. One refined attempt per pick."""
import math, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
sys.path.insert(0, '/home/hatch/workspace/heron/gate1-strike/work')
from pencil import *
import rig_v25 as R
from picks_a import ALERT, COIL, PEAK, neck_chevrons, ankle_rings

WORK = '/home/hatch/workspace/heron/gate1-strike/work'

# Bowed folded-wing mass: lower edge of the wing, sagging with the body.
WING2 = [(532, 98), (472, 152), (392, 204), (312, 246), (244, 278)]
ARCS2 = [
    [(512, 124), (452, 172), (378, 218), (306, 254)],
    [(488, 152), (428, 196), (360, 234), (296, 262)],
]


def wing2(D, seed, alpha=0.5, arcs=True, width=1.5):
    stroke(D, WING2, width=width, alpha=alpha, jitter=0.7, seed=seed)
    if arcs:
        for i, a in enumerate(ARCS2):
            stroke(D, a, width=1.2, alpha=alpha * 0.65, jitter=0.7, seed=seed + 41 + i)


def shadow_region():
    img = Image.new('L', (W, H), 0)
    dr = ImageDraw.Draw(img)
    top = [(128, 264), (250, 252), (380, 245), (500, 242), (606, 254)]
    poly = top + [(606, 300), (500, 292), (380, 295), (250, 300), (128, 308)]
    dr.polygon(poly, fill=1)
    return np.array(img) > 0


SHADOW = shadow_region()


def plume2(D, seed, n=9, alpha=0.5):
    plume_strands(D, (597, 222), seed, n=n, length=(30, 54), alpha=alpha, spread=11.0)


def pick1b(seed):
    g = ALERT
    D = new_D()
    ca = 0.30
    th = np.linspace(0, 2 * math.pi, 72)
    rot = math.radians(-10)
    ell = np.stack([360 + 248 * np.cos(th), 192 + 138 * np.sin(th)], axis=1)
    ell = (ell - [360, 192]) @ np.array([[math.cos(rot), -math.sin(rot)],
                                         [math.sin(rot), math.cos(rot)]]) + [360, 192]
    stroke(D, ell, width=1.2, alpha=ca, jitter=0.5, seed=seed + 1, closed=True, taper=0)
    for i in range(0, 21, 3):
        c = g['chain'][i]
        r = R.width_rest(i / 20) * R.T / 2
        circ = np.stack([c[0] + r * np.cos(th), c[1] + r * np.sin(th)], axis=1)
        stroke(D, circ, width=1.1, alpha=ca, jitter=0.5, seed=seed + i, closed=True, taper=0)
    ges = [g['chain'][0] - (g['chain'][2] - g['chain'][0]) * 1.5] + list(g['chain'][::2]) + \
          [g['skull'] + g['dvec'] * 30]
    stroke(D, ges, width=1.3, alpha=ca + 0.06, jitter=0.4, seed=seed + 7, taper=0)
    r = R.ANIMAL['head_assembly']['skull_semi_major'] * R.T
    circ = np.stack([g['skull'][0] + r * np.cos(th), g['skull'][1] + r * np.sin(th)], axis=1)
    stroke(D, circ, width=1.1, alpha=ca, jitter=0.5, seed=seed + 9, closed=True, taper=0)
    stroke(D, [g['skull'] - g['dvec'] * 46, g['bill_tip'] + g['dvec'] * 55],
           width=1.1, alpha=ca, jitter=0.3, seed=seed + 10, taper=0)
    for (hip, joint, foot) in g['legs']:
        stroke(D, [np.array(hip) - [0, 34], np.array(foot) + [0, 26]], width=1.1,
               alpha=ca, jitter=0.4, seed=seed + int(hip[0]), taper=0)
        circ = np.stack([joint[0] + 8 * np.cos(th), joint[1] + 8 * np.sin(th)], axis=1)
        stroke(D, circ, width=1.1, alpha=ca, jitter=0.4, seed=seed + 3, closed=True, taper=0)
        stroke(D, [[joint[0] - 34, 382], [joint[0] + 34, 382]], width=1.1,
               alpha=ca, jitter=0.3, seed=seed + 4, taper=0)
    stroke(D, g['contour'], width=2.3, alpha=0.62, jitter=1.5, passes=3,
           seed=seed + 20, closed=True)
    hatch_fill(D, g['mask'], angle_deg=104, spacing=8.0, alpha=0.20, margin=4,
               seed=seed + 21, region=SHADOW, dropout=0.25)
    wing2(D, seed + 22, alpha=0.5)
    plume2(D, seed + 23)
    neck_chevrons(D, g, seed + 24, alpha=0.28)
    draw_eye(D, g)
    stroke(D, [g['bill_base'], g['bill_tip']], width=1.2, alpha=0.5, seed=seed + 25)
    ankle_rings(D, g, seed + 26, alpha=0.5)
    return D


def pick2b(seed):
    g = ALERT
    D = new_D()
    stroke(D, g['contour'], width=2.6, alpha=0.16, jitter=0.25, passes=1,
           seed=seed + 1, closed=True, taper=0.15)
    stroke(D, g['contour'], width=1.7, alpha=0.85, jitter=0.35, passes=2,
           seed=seed + 2, closed=True, taper=0.15)
    wing2(D, seed + 3, alpha=0.55)
    plume2(D, seed + 4, n=10, alpha=0.55)
    neck_chevrons(D, g, seed + 5, alpha=0.22, step=5)
    hatch_fill(D, g['mask'], angle_deg=102, spacing=9.5, alpha=0.15, margin=5,
               seed=seed + 6, region=SHADOW, dropout=0.3)
    draw_eye(D, g)
    stroke(D, [g['bill_base'], g['bill_tip']], width=1.1, alpha=0.55, seed=seed + 7)
    ankle_rings(D, g, seed + 8, alpha=0.5, passes=1)
    return D


def pick5b(seed):
    g = ALERT
    D = new_D()
    cont = contour_of(g['mask'], smooth=3.2)
    stroke(D, cont, width=2.1, alpha=0.88, jitter=0.45, passes=1, seed=seed + 1,
           closed=True, taper=0.1)
    stroke(D, WING2, width=1.5, alpha=0.6, jitter=0.5, seed=seed + 2)
    dot(D, g['eye'], 3.4, 0.95)
    for (hip, joint, foot) in g['legs']:
        th = np.linspace(0, 2 * math.pi, 48)
        pts = np.stack([joint[0] + 13 * np.cos(th), joint[1] + 3.4 * np.sin(th)], axis=1)
        stroke(D, pts, width=1.5, alpha=0.55, jitter=0.5, seed=seed + 3, closed=True, taper=0)
    return D


def smear_strokes(D, mask, seed, n=30):
    """Wide soft directional stump strokes, clipped to mask, blurred in."""
    rng = np.random.default_rng(seed)
    layer = Image.new('L', (W * SS, H * SS), 0)
    dr = ImageDraw.Draw(layer)
    ys, xs = np.nonzero(mask)
    for _ in range(n):
        k = rng.integers(len(xs))
        x, y = xs[k] * SS, ys[k] * SS
        ang = math.radians(-18 + rng.normal(0, 10))
        L = rng.uniform(60, 170) * SS / 2
        wdt = rng.uniform(7, 15) * SS / 2
        a = (x - math.cos(ang) * L, y - math.sin(ang) * L)
        b = (x + math.cos(ang) * L, y + math.sin(ang) * L)
        dr.line([a, b], fill=int(rng.uniform(28, 60)), width=int(wdt))
    arr = np.asarray(layer.filter(__import__('PIL.ImageFilter', fromlist=['GaussianBlur']).GaussianBlur(6)), dtype=np.float64) / 255.0
    m = ndimage.zoom(mask.astype(float), SS, order=0)
    arr *= m
    D[:] = 1.0 - (1.0 - D) * (1.0 - arr)


def pick3b(seed):
    g = COIL
    D = new_D()
    chain = g['chain']
    low = chain[np.argmax(chain[:, 1])]
    blobs = [
        (low[0], low[1] + 6, 95, 42, 0.34),
        (400, 292, 210, 46, 0.30),
        (640, 190, 60, 85, 0.20),
        (210, 250, 90, 70, 0.22),
        (585, 130, 80, 60, 0.14),
        (330, 120, 190, 55, 0.12),
    ]
    smudge(D, g['mask'], blobs, base=0.15, blur=8.0, vgrad=0.10)
    smear_strokes(D, g['mask'], seed + 40, n=34)
    stroke(D, g['contour'], width=3.4, alpha=0.30, jitter=0.8, passes=2, seed=seed + 1, closed=True)
    stroke(D, g['contour'], width=1.6, alpha=0.42, jitter=0.7, passes=1, seed=seed + 2, closed=True)
    plume2(D, seed + 30, n=9, alpha=0.42)
    draw_eye(D, g)
    ankle_rings(D, g, seed + 31, alpha=0.45)
    return D


def pick4b(seed):
    g = PEAK
    D = new_D()
    chain = g['chain']

    def angle_fn(x, y):
        d2 = ((chain[:, 0] - x) ** 2 + (chain[:, 1] - y) ** 2)
        i = int(np.argmin(d2))
        if d2[i] < 70 ** 2 and i > 2:
            a, b = chain[max(i - 1, 0)], chain[min(i + 1, len(chain) - 1)]
            return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        return -14 + 10 * math.sin(x / 300.0)

    stroke(D, g['contour'], width=2.6, alpha=0.6, jitter=2.0, passes=2,
           seed=seed + 1, closed=True, taper=0.1)
    scribble_fill(D, g['mask'], angle_fn, density=950, len_lo=22, len_hi=56,
                  alpha=0.28, seed=seed + 2)
    dense = R.dense_chain(chain)
    dvv = np.gradient(dense, axis=0)
    nn = np.hypot(dvv[:, 0], dvv[:, 1]); nn[nn == 0] = 1
    nrm = np.stack([-dvv[:, 1] / nn, dvv[:, 0] / nn], axis=1)
    for k, off in enumerate((16, 30)):
        arc = dense[6::3] + nrm[6::3] * -off
        stroke(D, arc, width=1.5, alpha=0.26 - k * 0.07, jitter=1.2, seed=seed + 5 + k, taper=0)
    back = -g['dvec']
    perp = np.array([-back[1], back[0]])
    for k in range(4):
        c = g['bill_tip'] + back * (14 + k * 9) + perp * (k - 1.5) * 7
        stroke(D, [c + back * -7, c + back * 8], width=1.5, alpha=0.34, jitter=0.6,
               seed=seed + 9 + k, taper=0)
    wing2(D, seed + 15, alpha=0.45)
    draw_eye(D, g)
    ankle_rings(D, g, seed + 16, alpha=0.5)
    return D


if __name__ == '__main__':
    jobs = [(1, pick1b, ALERT, 0.22), (2, pick2b, ALERT, 0.22),
            (5, pick5b, ALERT, 0.22), (3, pick3b, COIL, 0.16),
            (4, pick4b, PEAK, 0.22)]
    for num, fn, g, th in jobs:
        D = fn(404 + num * 1000)
        iou = silhouette_iou(D, g['mask'], thresh=th)
        finish(D, 404 + num * 1000, f'{WORK}/cand_pick{num}_r2.png')
        print(f'pick{num} r2: IoU={iou:.3f}', flush=True)
