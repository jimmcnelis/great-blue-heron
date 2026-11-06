"""Pick 6 — FLIGHT, full pencil. Rig v2.5 has no flight pose, so the canvas
is composed from canon dimensions: TORSO_LOOP rotated level (length
preserved), neck folded at the standing arc budget, bill 0.23 torso,
legs trailing. Fit is measured against this composed canvas."""
import math, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, '/home/hatch/workspace/heron/gate1-strike/work')
from pencil import *
import rig_v25 as R

WORK = '/home/hatch/workspace/heron/gate1-strike/work'


def rot(pts, deg, c):
    th = math.radians(deg)
    M = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
    return (np.asarray(pts, float) - c) @ M.T + c


def build_flight():
    loop = np.array(R.TORSO_LOOP, dtype=float)
    c0 = loop.mean(axis=0)
    # level the long axis: tail->chest vector angle
    tail = np.array(R.LM['tail']); chest = np.array(R.LM['chest'])
    ang = math.degrees(math.atan2(chest[1] - tail[1], chest[0] - tail[0]))
    best = None
    for sgn in (1, -1):
        cand = rot(loop, sgn * -ang, c0)
        lm = {k: rot([v], sgn * -ang, c0)[0] for k, v in R.LM.items()}
        if lm['backtop'][1] < lm['belly'][1] and lm['tail'][0] < lm['chest'][0]:
            best = (cand, lm)
            break
    loop_r, lm = best
    centre = np.array([430.0, 298.0])
    shift = centre - loop_r.mean(axis=0)
    loop_f = loop_r + shift
    lm = {k: v + shift for k, v in lm.items()}

    img = Image.new('L', (W, H), 255)
    dr = ImageDraw.Draw(img)
    smooth = R.catmull_rom([tuple(p) for p in loop_f], n_per=3, closed=True)
    dr.polygon([tuple(p) for p in smooth], fill=0)

    chest_f = lm['chest']
    # folded neck centreline (profile: up-back from the breast, head forward)
    centre_line = np.array([
        chest_f + [6, 14],
        chest_f + [-18, -34],
        chest_f + [-52, -58],
        chest_f + [-84, -62],
        chest_f + [-92, -44],
    ])
    dense = R.dense_chain(centre_line, step=2.0)
    s = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(dense, axis=0).T))])
    u = s / s[-1]
    widths = R.width_rest(np.clip(u, 0, 1)) * R.T * 0.92
    dr.polygon([tuple(p) for p in R.tube_poly(dense, widths)], fill=0)
    skull = centre_line[-1] + np.array([16, -6])
    ha = R.ANIMAL['head_assembly']
    dvec = np.array([1.0, 0.10]); dvec /= np.hypot(*dvec)
    perp = np.array([dvec[1], -dvec[0]])
    ell = []
    for th in np.linspace(0, 2 * math.pi, 40):
        ell.append(skull + (dvec * math.cos(th) * ha['skull_semi_major'] * R.T
                            + np.array([-dvec[1], dvec[0]]) * math.sin(th)
                            * ha['skull_semi_minor'] * R.T))
    dr.polygon([tuple(p) for p in ell], fill=0)
    base_c = skull + dvec * ha['bill_base_offset_from_skull_centre'] * R.T
    tip = skull + dvec * ha['bill_tip_reach_from_skull_centre'] * R.T
    bw = 0.0135 * R.T
    dr.polygon([tuple(base_c + perp * bw), tuple(tip), tuple(base_c - perp * bw)], fill=0)
    eye = (skull + dvec * ha['eye_anchor_in_head_frame']['along_bill'] * R.T
           + perp * ha['eye_anchor_in_head_frame']['up'] * R.T)
    # trailing legs
    belly = lm['belly']
    for off, foot in ((0, np.array([228.0, 318.0])), (1, np.array([238.0, 340.0]))):
        hip = belly + np.array([-38 - off * 6, -6 + off * 13])
        d = foot - hip; d = d / np.hypot(*d)
        pp = np.array([-d[1], d[0]])
        dr.polygon([tuple(hip + pp * 4.5), tuple(foot + pp * 2.0),
                    tuple(foot - pp * 2.0), tuple(hip - pp * 4.5)], fill=0)
    # wings
    near = [(522, 238), (420, 168), (300, 122), (188, 102), (108, 122),
            (128, 158), (186, 190), (258, 220), (336, 246), (420, 264), (500, 272)]
    far = [(548, 240), (636, 172), (728, 132), (822, 128), (852, 150),
           (786, 186), (700, 218), (616, 242), (560, 256)]
    for wing in (far, near):
        sm = R.catmull_rom(wing, n_per=4, closed=True)
        dr.polygon([tuple(p) for p in sm], fill=0)
    mask = np.array(img) < 128
    geom = dict(mask=mask, contour=contour_of(mask), eye=eye, skull=skull,
                dvec=dvec, bill_tip=tip, bill_base=base_c, chest=chest_f,
                centre_line=centre_line, near_wing=near, far_wing=far)
    return geom


def pick6(seed, g):
    D = new_D()
    stroke(D, g['contour'], width=2.2, alpha=0.6, jitter=1.1, passes=2,
           seed=seed + 1, closed=True)
    # primary feather fans: lines from trailing-edge scallops toward the wing root
    root_n = np.array([455.0, 240.0])
    trail_n = [(128, 158), (186, 190), (258, 220), (336, 246), (420, 264)]
    for i, p in enumerate(trail_n):
        p = np.array(p, float)
        q = root_n + (p - root_n) * 0.18
        stroke(D, [q, p - (p - q) * 0.04], width=1.3, alpha=0.5, jitter=0.6,
               seed=seed + 10 + i)
    root_f = np.array([560.0, 242.0])
    trail_f = [(786, 186), (700, 218), (616, 242)]
    for i, p in enumerate(trail_f):
        p = np.array(p, float)
        q = root_f + (p - root_f) * 0.2
        stroke(D, [q, p], width=1.2, alpha=0.42, jitter=0.6, seed=seed + 20 + i)
    # secondary arcs inside the near wing, roughly parallel to trailing edge
    for k, off in enumerate((26, 52)):
        arc = [(x, y - off * (0.5 + 0.5 * math.sin((x - 100) / 780 * math.pi)))
               for (x, y) in [(150, 168), (230, 204), (320, 234), (410, 256)]]
        arc = [(x, y - off * 0.55) for (x, y) in [(150, 168), (230, 204), (320, 234), (410, 256)]]
        stroke(D, arc, width=1.2, alpha=0.4, jitter=0.7, seed=seed + 30 + k)
    # body shading + folded-wing hint on the torso
    hatch_fill(D, g['mask'], angle_deg=88, spacing=9.0, alpha=0.13, margin=5,
               seed=seed + 40, dropout=0.35)
    stroke(D, [(520, 262), (440, 292), (340, 306), (252, 300)], width=1.4,
           alpha=0.45, jitter=0.7, seed=seed + 41)
    # neck fold shading chevrons
    cl = g['centre_line']
    for i in range(1, len(cl) - 1):
        a, b = cl[i - 1], cl[i + 1]
        d = b - a; d /= max(np.hypot(*d), 1e-9)
        n = np.array([-d[1], d[0]])
        stroke(D, [cl[i] - n * 15, cl[i] + n * 11], width=1.1, alpha=0.3,
               jitter=0.5, seed=seed + 50 + i)
    dot(D, g['eye'], 3.4, 0.92)
    stroke(D, [g['bill_base'], g['bill_tip']], width=1.1, alpha=0.5, seed=seed + 60)
    return D


if __name__ == '__main__':
    g = build_flight()
    Image.fromarray((~g['mask'] * 255).astype(np.uint8)).save(f'{WORK}/canvas_flight.png')
    for s in (101, 202):
        D = pick6(s + 6000, g)
        iou = silhouette_iou(D, g['mask'], thresh=0.22)
        finish(D, s + 6000, f'{WORK}/cand_pick6_s{s}.png')
        print(f'pick6 seed{s}: IoU={iou:.3f}', flush=True)
