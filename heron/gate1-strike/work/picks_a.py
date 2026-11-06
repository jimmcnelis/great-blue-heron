"""Picks 1-5 (rig poses). Each pick rendered with several seeds; IoU measured."""
import math, sys
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/heron/gate1-strike/work')
from pencil import *
import rig_v25 as R

WORK = '/home/hatch/workspace/heron/gate1-strike/work'
ALERT = pose_geom('alert')
COIL = pose_geom('deep_coil')
PEAK = pose_geom('strike_peak')

WING = [(528, 88), (455, 128), (368, 182), (292, 232), (238, 272)]
FEATHER_ARCS = [
    [(505, 112), (430, 152), (350, 200), (282, 244)],
    [(478, 140), (402, 180), (330, 222), (270, 258)],
]


def wing_lines(D, seed, alpha=0.45, arcs=True):
    stroke(D, WING, width=1.5, alpha=alpha, jitter=0.7, seed=seed)
    if arcs:
        for i, a in enumerate(FEATHER_ARCS):
            stroke(D, a, width=1.2, alpha=alpha * 0.7, jitter=0.7, seed=seed + 31 + i)


def neck_chevrons(D, g, seed, alpha=0.3, step=4):
    pts = g['chain']
    for i in range(3, len(pts) - 1, step):
        a, b = pts[i - 1], pts[i + 1]
        d = b - a; d = d / max(np.hypot(*d), 1e-9)
        n = np.array([-d[1], d[0]])
        w = R.width_rest(i / (len(pts) - 1)) * R.T * 0.36
        stroke(D, [pts[i] - n * w, pts[i] + n * w * 0.6], width=1.1,
               alpha=alpha, jitter=0.5, seed=seed + i)


def ankle_rings(D, g, seed, **kw):
    for (hip, joint, foot) in g['legs']:
        rings(D, joint[0], joint[1], seed + int(joint[0]), **kw)


# ------------------------------------------------------------------ pick 1
def pick1(seed):
    g = ALERT
    D = new_D()
    rng = np.random.default_rng(seed)
    # --- construction layer (light graphite, left in)
    ca = 0.34
    th = np.linspace(0, 2 * math.pi, 72)
    rot = math.radians(-10)
    ell = np.stack([360 + 248 * np.cos(th), 192 + 138 * np.sin(th)], axis=1)
    ell = (ell - [360, 192]) @ np.array([[math.cos(rot), -math.sin(rot)],
                                         [math.sin(rot), math.cos(rot)]]) + [360, 192]
    stroke(D, ell, width=1.2, alpha=ca, jitter=0.5, seed=seed + 1, closed=True, taper=0)
    # neck joint circles
    for i in range(0, 21, 3):
        c = g['chain'][i]
        r = R.width_rest(i / 20) * R.T / 2
        circ = np.stack([c[0] + r * np.cos(th), c[1] + r * np.sin(th)], axis=1)
        stroke(D, circ, width=1.1, alpha=ca, jitter=0.5, seed=seed + i, closed=True, taper=0)
    # gesture line through the neck, overshooting both ends
    ges = [g['chain'][0] - (g['chain'][2] - g['chain'][0]) * 1.5] + list(g['chain'][::2]) + \
          [g['skull'] + g['dvec'] * 30]
    stroke(D, ges, width=1.3, alpha=ca + 0.06, jitter=0.4, seed=seed + 7, taper=0)
    # head circle + bill guide
    r = R.ANIMAL['head_assembly']['skull_semi_major'] * R.T
    circ = np.stack([g['skull'][0] + r * np.cos(th), g['skull'][1] + r * np.sin(th)], axis=1)
    stroke(D, circ, width=1.1, alpha=ca, jitter=0.5, seed=seed + 9, closed=True, taper=0)
    stroke(D, [g['skull'] - g['dvec'] * 46, g['bill_tip'] + g['dvec'] * 55],
           width=1.1, alpha=ca, jitter=0.3, seed=seed + 10, taper=0)
    # leg guides + joint circles
    for (hip, joint, foot) in g['legs']:
        stroke(D, [np.array(hip) - [0, 34], np.array(foot) + [0, 26]], width=1.1,
               alpha=ca, jitter=0.4, seed=seed + int(hip[0]), taper=0)
        circ = np.stack([joint[0] + 8 * np.cos(th), joint[1] + 8 * np.sin(th)], axis=1)
        stroke(D, circ, width=1.1, alpha=ca, jitter=0.4, seed=seed + 3, closed=True, taper=0)
    # waterline ticks at ankles
    for (hip, joint, foot) in g['legs']:
        stroke(D, [[joint[0] - 34, 382], [joint[0] + 34, 382]], width=1.1,
               alpha=ca, jitter=0.3, seed=seed + 4, taper=0)
    # --- main contour, rough multi-pass
    stroke(D, g['contour'], width=2.3, alpha=0.62, jitter=1.5, passes=3,
           seed=seed + 20, closed=True)
    # --- interior life
    hatch_fill(D, g['mask'], angle_deg=100, spacing=8.5, alpha=0.16, margin=4, seed=seed + 21)
    wing_lines(D, seed + 22, alpha=0.5)
    plume_strands(D, (600, 228), seed + 23, n=10, alpha=0.5)
    neck_chevrons(D, g, seed + 24, alpha=0.28)
    draw_eye(D, g)
    stroke(D, [g['bill_base'], g['bill_tip']], width=1.2, alpha=0.5, seed=seed + 25)
    ankle_rings(D, g, seed + 26, alpha=0.5)
    return D


# ------------------------------------------------------------------ pick 2
def pick2(seed):
    g = ALERT
    D = new_D()
    stroke(D, g['contour'], width=2.6, alpha=0.16, jitter=0.25, passes=1,
           seed=seed + 1, closed=True, taper=0.15)
    stroke(D, g['contour'], width=1.7, alpha=0.85, jitter=0.35, passes=2,
           seed=seed + 2, closed=True, taper=0.15)
    wing_lines(D, seed + 3, alpha=0.55)
    plume_strands(D, (600, 228), seed + 4, n=11, length=(40, 66), alpha=0.55)
    neck_chevrons(D, g, seed + 5, alpha=0.22, step=5)
    hatch_fill(D, g['mask'], angle_deg=96, spacing=11, alpha=0.10, margin=6, seed=seed + 6)
    draw_eye(D, g)
    stroke(D, [g['bill_base'], g['bill_tip']], width=1.1, alpha=0.55, seed=seed + 7)
    ankle_rings(D, g, seed + 8, alpha=0.5, passes=1)
    return D


# ------------------------------------------------------------------ pick 5
def pick5(seed):
    g = ALERT
    D = new_D()
    cont = contour_of(g['mask'], smooth=3.2)
    stroke(D, cont, width=2.1, alpha=0.88, jitter=0.45, passes=1, seed=seed + 1,
           closed=True, taper=0.1)
    stroke(D, WING, width=1.5, alpha=0.6, jitter=0.5, seed=seed + 2)
    dot(D, g['eye'], 3.4, 0.95)
    for (hip, joint, foot) in g['legs']:
        th = np.linspace(0, 2 * math.pi, 48)
        pts = np.stack([joint[0] + 13 * np.cos(th), joint[1] + 3.4 * np.sin(th)], axis=1)
        stroke(D, pts, width=1.5, alpha=0.55, jitter=0.5, seed=seed + 3, closed=True, taper=0)
    return D


# ------------------------------------------------------------------ pick 3
def pick3(seed):
    g = COIL
    D = new_D()
    chain = g['chain']
    low = chain[np.argmax(chain[:, 1])]
    blobs = [
        (low[0], low[1] + 6, 95, 42, 0.34),          # under the coil fold
        (400, 292, 210, 46, 0.30),                    # belly shadow
        (640, 190, 60, 85, 0.20),                     # neck front shade
        (210, 250, 90, 70, 0.22),                     # tail mass
        (585, 130, 80, 60, 0.14),                     # upper neck light shade
        (330, 120, 190, 55, 0.12),                    # back top soft
    ]
    smudge(D, g['mask'], blobs, base=0.15, blur=8.0, vgrad=0.10)
    # soft contour
    stroke(D, g['contour'], width=3.4, alpha=0.30, jitter=0.8, passes=2, seed=seed + 1, closed=True)
    stroke(D, g['contour'], width=1.6, alpha=0.42, jitter=0.7, passes=1, seed=seed + 2, closed=True)
    # soft wing arcs (blurred by drawing wide + faint, twice)
    for i, a in enumerate(FEATHER_ARCS + [WING]):
        stroke(D, a, width=3.0, alpha=0.13, jitter=1.0, seed=seed + 10 + i)
        stroke(D, a, width=1.4, alpha=0.22, jitter=0.8, seed=seed + 20 + i)
    plume_strands(D, (598, 232), seed + 30, n=10, alpha=0.4)
    draw_eye(D, g)
    ankle_rings(D, g, seed + 31, alpha=0.45)
    return D


# ------------------------------------------------------------------ pick 4
def pick4(seed):
    g = PEAK
    D = new_D()
    chain = g['chain']

    def angle_fn(x, y):
        # near the neck: follow the spear; else follow the back's flow
        d2 = ((chain[:, 0] - x) ** 2 + (chain[:, 1] - y) ** 2)
        i = int(np.argmin(d2))
        if d2[i] < 70 ** 2 and i > 2:
            a, b = chain[max(i - 1, 0)], chain[min(i + 1, len(chain) - 1)]
            return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        return -14 + 10 * math.sin(x / 300.0)

    stroke(D, g['contour'], width=2.6, alpha=0.6, jitter=2.0, passes=2,
           seed=seed + 1, closed=True, taper=0.1)
    scribble_fill(D, g['mask'], angle_fn, density=1200, alpha=0.30, seed=seed + 2)
    # trailing motion arcs above the neck path
    dense = R.dense_chain(chain)
    dv = np.gradient(dense, axis=0)
    nn = np.hypot(dv[:, 0], dv[:, 1]); nn[nn == 0] = 1
    nrm = np.stack([-dv[:, 1] / nn, dv[:, 0] / nn], axis=1)
    for k, off in enumerate((16, 30)):
        arc = dense[6::3] + nrm[6::3] * -off
        stroke(D, arc, width=1.5, alpha=0.20 - k * 0.06, jitter=1.2, seed=seed + 5 + k, taper=0)
    # speed ticks behind the bill tip
    back = -g['dvec']
    perp = np.array([-back[1], back[0]])
    for k in range(4):
        c = g['bill_tip'] + back * (14 + k * 9) + perp * (k - 1.5) * 7
        stroke(D, [c + back * -7, c + back * 8], width=1.5, alpha=0.34, jitter=0.6,
               seed=seed + 9 + k, taper=0)
    wing_lines(D, seed + 15, alpha=0.45)
    draw_eye(D, g)
    ankle_rings(D, g, seed + 16, alpha=0.5)
    return D


if __name__ == '__main__':
    jobs = [(1, 'alert', pick1, ALERT), (2, 'alert', pick2, ALERT),
            (5, 'alert', pick5, ALERT), (3, 'deep_coil', pick3, COIL),
            (4, 'strike_peak', pick4, PEAK)]
    for num, pose, fn, g in jobs:
        for s in (101, 202, 303):
            D = fn(s + num * 1000)
            iou = silhouette_iou(D, g['mask'], thresh=0.16 if num == 3 else 0.22)
            finish(D, s + num * 1000, f'{WORK}/cand_pick{num}_s{s}.png')
            print(f'pick{num} seed{s}: IoU={iou:.3f}', flush=True)
