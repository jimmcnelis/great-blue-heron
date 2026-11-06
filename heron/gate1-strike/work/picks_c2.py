"""Pick 6 v2 — FLIGHT canvas composed explicitly at canon scale:
torso hull = T (494 px), bill 0.23 torso, neck folded in front of the
breast with the head clear of the body, legs trailing past the tail,
wings in a shallow glide V. (v1's rotated standing torso buried the
head and pitched the body; discarded on the eye read.)"""
import math, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, '/home/hatch/workspace/heron/gate1-strike/work')
from pencil import *
import rig_v25 as R

WORK = '/home/hatch/workspace/heron/gate1-strike/work'

BODY = [(215, 300), (300, 268), (420, 252), (540, 256), (628, 274),
        (668, 294), (640, 318), (540, 336), (420, 342), (300, 334),
        (232, 318)]
TAIL = [(222, 296), (164, 280), (170, 326), (224, 316)]
NECK_LINE = [(636, 302), (622, 262), (630, 232), (656, 218), (682, 226)]
NEAR_WING = [(520, 258), (428, 196), (318, 152), (206, 128), (122, 136),
             (168, 168), (244, 196), (330, 222), (420, 244), (496, 256)]
FAR_WING = [(560, 252), (650, 182), (748, 142), (840, 130), (906, 142),
            (832, 176), (746, 204), (656, 230), (586, 246)]


def build_flight2():
    img = Image.new('L', (W, H), 255)
    dr = ImageDraw.Draw(img)
    for poly in (FAR_WING, BODY, TAIL, NEAR_WING):
        sm = R.catmull_rom(poly, n_per=4, closed=True)
        dr.polygon([tuple(p) for p in sm], fill=0)
    # folded neck tube
    cl = np.array(NECK_LINE, dtype=float)
    dense = R.dense_chain(cl, step=2.0)
    s = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(dense, axis=0).T))])
    u = s / s[-1]
    widths = R.width_rest(np.clip(u, 0, 1)) * R.T * 0.88
    dr.polygon([tuple(p) for p in R.tube_poly(dense, widths)], fill=0)
    # head + bill
    ha = R.ANIMAL['head_assembly']
    skull = np.array([694.0, 228.0])
    dvec = np.array([1.0, 0.06]); dvec /= np.hypot(*dvec)
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
    # trailing legs (hips buried in the body)
    for hip, foot in ((np.array([302.0, 320.0]), np.array([126.0, 330.0])),
                      (np.array([294.0, 330.0]), np.array([120.0, 348.0]))):
        d = foot - hip; d /= np.hypot(*d)
        pp = np.array([-d[1], d[0]])
        dr.polygon([tuple(hip + pp * 4.5), tuple(foot + pp * 2.0),
                    tuple(foot - pp * 2.0), tuple(hip - pp * 4.5)], fill=0)
    mask = np.array(img) < 128
    return dict(mask=mask, contour=contour_of(mask), eye=eye, skull=skull,
                dvec=dvec, bill_tip=tip, bill_base=base_c,
                centre_line=cl)


def pick6b(seed, g):
    D = new_D()
    stroke(D, g['contour'], width=2.2, alpha=0.62, jitter=1.1, passes=2,
           seed=seed + 1, closed=True)
    # primary fans
    for root, trail, a0 in ((np.array([462.0, 238.0]),
                             [(168, 168), (244, 196), (330, 222), (420, 244)], 0.5),
                            (np.array([586.0, 236.0]),
                             [(832, 176), (746, 204), (656, 230)], 0.42)):
        for i, p in enumerate(trail):
            p = np.array(p, float)
            q = root + (p - root) * 0.16
            stroke(D, [q, p], width=1.3, alpha=a0, jitter=0.6, seed=seed + 10 + i)
    # secondary arcs inside wings
    for pts, sd in (([(180, 178), (262, 208), (352, 232), (436, 250)], 30),
                    ([(812, 186), (730, 212), (648, 234)], 33)):
        stroke(D, pts, width=1.2, alpha=0.38, jitter=0.7, seed=seed + sd)
    # body shading: soft hatch in the belly band only
    yy, xx = np.mgrid[0:H, 0:W]
    region = (yy > 296) & (yy < 344) & (xx > 210) & (xx < 672)
    hatch_fill(D, g['mask'], angle_deg=84, spacing=8.5, alpha=0.13, margin=4,
               seed=seed + 40, region=region, dropout=0.4)
    # wing underside shading arcs
    stroke(D, [(150, 150), (250, 182), (360, 210), (460, 232)], width=2.6,
           alpha=0.16, jitter=0.9, seed=seed + 44)
    stroke(D, [(872, 158), (780, 190), (682, 216)], width=2.6,
           alpha=0.14, jitter=0.9, seed=seed + 45)
    # neck fold chevrons
    cl = g['centre_line']
    for i in range(1, len(cl) - 1):
        a, b = cl[i - 1], cl[i + 1]
        d = b - a; d /= max(np.hypot(*d), 1e-9)
        n = np.array([-d[1], d[0]])
        stroke(D, [cl[i] - n * 14, cl[i] + n * 10], width=1.1, alpha=0.3,
               jitter=0.5, seed=seed + 50 + i)
    dot(D, g['eye'], 3.4, 0.92)
    stroke(D, [g['bill_base'], g['bill_tip']], width=1.1, alpha=0.5, seed=seed + 60)
    return D


if __name__ == '__main__':
    g = build_flight2()
    Image.fromarray((~g['mask'] * 255).astype(np.uint8)).save(f'{WORK}/canvas_flight2.png')
    for s in (101, 202):
        D = pick6b(s + 6000, g)
        iou = silhouette_iou(D, g['mask'], thresh=0.22)
        finish(D, s + 6000, f'{WORK}/cand_pick6b_s{s}.png')
        print(f'pick6b seed{s}: IoU={iou:.3f}', flush=True)
