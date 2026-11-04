#!/usr/bin/env python3
"""Gate measurement for the fill test v2.5 — run ONCE on the frozen
render in frames/. Instruments: spike 1 / v3 metric definitions
(content_mask, color_fracs), build_corpus.fit for still registration,
spike 3's colour tests for bill/eye landmark extraction."""
import json, math, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

H_ = os.path.expanduser('~')
for p in (f'{H_}/workspace/heron/art2', f'{H_}/workspace/heron/src13',
          f'{H_}/workspace/heron/art2/finished-art-stills/finish-model-v3',
          f'{H_}/workspace/heron/art2/fill-spike-v1',
          f'{H_}/workspace/heron/art2/fill-spike-v3',
          f'{H_}/workspace/heron/art2/fill-test-v25'):
    sys.path.insert(0, p)
import spike_fill as S1
import build_corpus as bc
import drawn_landmarks as DL
import fill25 as F

W, H = 1024, 600
OUT = F.OUT
T = F.T
load = S1.load
res = {}

def frame(i):
    return load(f'{OUT}/frames/f{i:04d}.png')

# ---------------- gate 1: hold fidelity ----------------
hold = frame(10)
hm = S1.content_mask(hold)
res['hold_black'] = round(S1.color_fracs(hold, hm)['black'], 4)
# (a) spike-1 basis: IoU vs registered gold idle_f0030 (the registered
# approved rest still on v2.4 idle geometry)
gold_idle = load(f'{F.FM3}/corpus/target/idle_f0030.png')
gm = S1.content_mask(gold_idle)
res['iou_vs_registered_rest_v24basis'] = round(S1.iou(hm, gm), 4)
# (b) approved rest still re-registered onto the v2.5 alert silhouette
th, pitch = F.blend_profile([('alert', 1.0)])
g = F.frame_geometry(th, pitch, 0.0)
neck_m, head_m, bill_m = F.region_masks(g)
sil = F.TORSO_M | F.LEGS_M | neck_m | head_m | bill_m
rest_mask = bc.bird_mask(F.REST)
iou_fit, s, thd, dx, dy = bc.fit(rest_mask, sil)
warped_rest = S1.warp_img(F.REST, (s, thd, dx, dy))
wmask = bc.warp_mask(rest_mask, s, thd, dx, dy)
res['rest_fit_iou'] = round(iou_fit, 4)
res['iou_vs_rest_reregistered'] = round(S1.iou(hm, wmask), 4)
u = hm | wmask
res['mad_vs_rest_reregistered'] = round(float(np.abs(hold - warped_rest)[u].mean()), 2)
res['hold_fracs'] = {k: round(v, 4) for k, v in S1.color_fracs(hold, hm).items()}
res['rest_fracs_orig'] = {k: round(v, 4) for k, v in
                          S1.color_fracs(F.REST, S1.content_mask(F.REST)).items()}
Image.fromarray(np.clip(hold, 0, 255).astype(np.uint8)).save(f'{OUT}/work/hold.png')
# 3-panel side-by-side: mine | rest registered onto v2.5 alert | original
strip = np.full((630, 1024 * 3, 3), 255, np.uint8)
for i, a in enumerate((hold, warped_rest, F.REST)):
    strip[30:630, i * 1024:(i + 1) * 1024] = np.clip(a, 0, 255).astype(np.uint8)
Image.fromarray(strip).save(f'{OUT}/sidebyside/hold_vs_rest.png')

# ---------------- gate 2: strike truth ----------------
def bill_landmarks(img, g):
    yel = DL.yellow_mask(img)
    comps = DL.comps(yel)
    if not comps:
        return None
    size, cen, pts = comps[0]
    proj = (pts - g['skull']) @ g['dvec']
    tip = pts[int(np.argmax(proj))]
    return dict(yellow_px=int(size), n_comps=len(comps),
                tip=[round(float(tip[0]), 1), round(float(tip[1]), 1)],
                tip_dist_from_skull=round(float(proj.max()), 1),
                geom_tip_dist=round(float(np.hypot(*(g['tip'] - g['skull']))), 1))

def eye_and_skull(img, g):
    # the drawn eye's amber ring itself passes DL.yellow_mask (amber is
    # yellow-class), so do NOT subtract yellow; instead drop clusters
    # that overlap the bill triangle and take the one nearest the anchor
    _, _, bill_m0 = F.region_masks(g)
    iris = DL.iris_mask(img)
    best = None
    for size, cen, pts in DL.comps(iris):
        yy = np.clip(pts[:, 1].astype(int), 0, H - 1)
        xx = np.clip(pts[:, 0].astype(int), 0, W - 1)
        if bill_m0[yy, xx].mean() > 0.5:
            continue
        d = np.hypot(*(cen - g['eye']))
        if best is None or d < best[0]:
            best = (d, cen, size)
    if best is None:
        return None
    d, cen, size = best
    ha = F.ANIMAL['head_assembly']
    skull_est = cen - (g['dvec'] * ha['eye_anchor_in_head_frame']['along_bill'] * T
                       + g['perp'] * ha['eye_anchor_in_head_frame']['up'] * T)
    return dict(cluster_px=int(size), dist_to_anchor=round(float(d), 1),
                centroid=[round(float(cen[0]), 1), round(float(cen[1]), 1)],
                skull_est=skull_est)

def chord76_filled(img, g):
    """Pixel landmarks: bill tip + eye->skull; neck centreline walked
    through the filled corridor (content minus torso/head/bill)."""
    bl = bill_landmarks(img, g)
    es = eye_and_skull(img, g)
    if bl is None or es is None:
        return dict(bill=bl, eye=None if es is None else True)
    skull = es['skull_est']
    neck_m2, head_m2, bill_m2 = F.region_masks(g)
    head_core = F.poly_mask([g['ell'], g['plume_tri']])   # anatomy only, no fan
    corridor = S1.content_mask(img) & ndimage.binary_dilation(neck_m2, iterations=6) \
        & ~F.TORSO_M & ~ndimage.binary_dilation(head_core, iterations=2) \
        & ~ndimage.binary_dilation(bill_m2, iterations=2)
    corridor[535:, :] = False   # waterline band is scenery, not neck
    target = g['neckbase']
    direction = target - skull
    L = np.hypot(*direction); direction = direction / L
    pts = [skull.copy()]
    p = skull.copy()
    for _ in range(200):
        p = p + direction * 6.0
        yy, xx = np.nonzero(corridor[max(0, int(p[1]) - 16):int(p[1]) + 17,
                                     max(0, int(p[0]) - 16):int(p[0]) + 17])
        if len(xx) < 8:
            break
        c = np.array([xx.mean() + max(0, int(p[0]) - 16),
                      yy.mean() + max(0, int(p[1]) - 16)])
        pts.append(c)
        if np.hypot(*(c - target)) < 18:
            break
    pts = np.array(pts)
    if len(pts) < 3:
        return dict(bill=bl, eye_cluster_px=es['cluster_px'],
                    eye_dist_to_anchor=es['dist_to_anchor'],
                    centreline_pts=len(pts), corridor_arc=0.0,
                    chord76=None,
                    chord76_note='centreline walk broke: filled corridor has '
                                 'no continuous content from the skull',
                    tip_reach_over_T=round(float(np.hypot(*(np.array(bl['tip']) - skull))) / T, 3),
                    design_chord76=round(float(np.hypot(*(g['skull'] -
                        F.R25.pt_at_frac(F.R25.visible_chain(g['pts'])[0][::-1], 0.76)))) / T, 3))
    seg = np.hypot(*np.diff(pts, axis=0).T)
    arc = np.concatenate([[0], np.cumsum(seg)])
    total = arc[-1]
    k = int(np.searchsorted(arc, 0.76 * total))
    k = min(max(k, 1), len(pts) - 1)
    frac = (0.76 * total - arc[k - 1]) / max(seg[k - 1], 1e-9)
    p76 = pts[k - 1] + frac * (pts[k] - pts[k - 1])
    return dict(bill=bl, eye_cluster_px=es['cluster_px'],
                eye_dist_to_anchor=es['dist_to_anchor'],
                centreline_pts=len(pts), corridor_arc=round(float(total), 1),
                chord76=round(float(np.hypot(*(skull - p76))) / T, 3),
                design_chord76=round(float(np.hypot(*(g['skull'] -
                    F.R25.pt_at_frac(F.R25.visible_chain(g['pts'])[0][::-1], 0.76)))) / T, 3))

th, pitch = F.blend_profile([('strike_peak', 1.0)])
g_peak = F.frame_geometry(th, pitch, 1.0)
res['peak'] = chord76_filled(frame(95), g_peak)
res['peak_frame94'] = chord76_filled(frame(94), g_peak)
# bill intact through withdrawal: yellow mass + reach per sampled frame
wd = {}
for i in (95, 102, 108, 114, 118):
    thx, px = (F.blend_profile([('strike_peak', 1.0)]) if i == 95 else (None, None))
    img = frame(i)
    yel = DL.yellow_mask(img)
    comps = DL.comps(yel)
    wd[i] = dict(n_comps=len(comps),
                 largest=int(comps[0][0]) if comps else 0,
                 second=int(comps[1][0]) if len(comps) > 1 else 0)
res['withdrawal_bill'] = wd
# region blacks at peak (what the neck/head remaps actually landed)
neck_m, head_m, bill_m = F.region_masks(g_peak)
pk = frame(95)
lum = pk.mean(axis=2)
res['peak_region_black'] = dict(
    neck=round(float((lum[neck_m] < 70).mean()), 4),
    head=round(float((lum[head_m] < 70).mean()), 4),
    torso=round(float((lum[F.TORSO_M] < 70).mean()), 4))
# peak side-by-side: mine | strike still registered onto peak sil | orig
sil_p = F.TORSO_M | F.LEGS_M | neck_m | head_m | bill_m
smask = bc.bird_mask(F.STRIKE)
_, s2, th2, dx2, dy2 = bc.fit(smask, sil_p)
warped_strike = S1.warp_img(F.STRIKE, (s2, th2, dx2, dy2))
strip = np.full((630, 1024 * 3, 3), 255, np.uint8)
for i, a in enumerate((pk, warped_strike, F.STRIKE)):
    strip[30:630, i * 1024:(i + 1) * 1024] = np.clip(a, 0, 255).astype(np.uint8)
Image.fromarray(strip).save(f'{OUT}/sidebyside/peak_vs_strike.png')
res['peak_iou_vs_strike_rereg'] = round(S1.iou(S1.content_mask(pk),
                                        bc.warp_mask(smask, s2, th2, dx2, dy2)), 4)
# crops for visual record
Image.fromarray(np.clip(pk, 0, 255).astype(np.uint8)[180:600, 540:1024]).save(
    f'{OUT}/work/peak_head_neck_crop.png')
Image.fromarray(np.clip(hold, 0, 255).astype(np.uint8)[0:330, 540:1024]).save(
    f'{OUT}/work/hold_head_crop.png')

# ---------------- gates 3+4 from the render log ----------------
log = json.load(open(f'{OUT}/work/render_log.json'))
res['black_all_frames'] = [round(log['black_min'], 4), round(log['black_max'], 4)]
res['determinism'] = log['determinism']
res['eye_checks_sampled'] = {str(i): log['infos'][i]['eye_check']
                             for i in (10, 80, 90, 95, 108, 130)}
res['coverage_sampled'] = {str(i): (log['infos'][i]['neck_cov'],
                                    log['infos'][i]['head_cov'])
                           for i in (10, 60, 80, 90, 95, 108, 130)}
json.dump(res, open(f'{OUT}/work/metrics_fill25.json', 'w'), indent=1)
print(json.dumps(res, indent=1))
