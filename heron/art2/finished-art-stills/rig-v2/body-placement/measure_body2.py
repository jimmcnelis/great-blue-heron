#!/usr/bin/env python3
"""Body-placement round, refined instruments (supersedes the zone
decomposition in measure_body.py; controls there already certified:
v2 = 0.5257, v2.1 = 0.5501).

Legs: bottom-up run tracking on each bird's union silhouette — the
two persistent narrow runs are the legs (plume law: read the sticks
under the skirt, never the blended outline). Plume: approved side =
thin hanging strands in the front fan minus the leg tracks, plus a
morphologically closed ENVELOPE; rig side = channel 7 (exact) with
the same envelope op. Torso: DT>=13s core with tightened head/neck
exclusions, cross-checked on the rig side against the exact-channel
core. All quantities breast-relative, H-normalised, both frames.
"""
import copy, json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

HOME = os.path.expanduser('~')
ART2 = f'{HOME}/workspace/heron/art2'
FS = f'{ART2}/finished-art-stills'
RIGV2 = f'{FS}/rig-v2'
OUT = f'{RIGV2}/body-placement'
sys.path.insert(0, ART2)
sys.path.insert(0, f'{HOME}/workspace/heron/src13')
sys.path.insert(0, f'{FS}/refinish-corpus/work')
sys.path.insert(0, f'{RIGV2}/work')
import measure_v2 as MV
import roster_charts as RC
import roster_render_v21 as RR21
import maskrender_v2 as M2

W, H = 1024, 600
U = RR21.U

def seg_dist(shape, a, b):
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]]
    a = np.asarray(a, float); b = np.asarray(b, float)
    d = b - a; L2 = float(d @ d)
    t = np.clip(((xx - a[0]) * d[0] + (yy - a[1]) * d[1]) / L2, 0, 1)
    return np.hypot(xx - (a[0] + t * d[0]), yy - (a[1] + t * d[1]))

def runs_at(mask, y, xwin, maxw=30):
    row = mask[y, xwin[0]:xwin[1]]
    out, x = [], 0
    while x < len(row):
        if row[x]:
            x0 = x
            while x < len(row) and row[x]:
                x += 1
            if x - x0 <= maxw:
                out.append((x0 + xwin[0] + (x - 1 + xwin[0])) / 2.0)
        else:
            x += 1
    return out

def track_legs(mask, y_start, y_stop, xwin):
    """Track narrow runs upward from y_start. Returns tracks that
    persist >= 110 rows: list of dicts of per-y centroid x."""
    tracks = [dict(pts={y_start: cx}, alive=True) for cx in runs_at(mask, y_start, xwin)]
    for y in range(y_start - 1, y_stop - 1, -1):
        runs = runs_at(mask, y, xwin)
        for tr in tracks:
            if not tr['alive']:
                continue
            last = tr['pts'][min(tr['pts'])]
            cand = [r for r in runs if abs(r - last) <= 7]
            if cand:
                tr['pts'][y] = min(cand, key=lambda r: abs(r - last))
            else:
                tr['alive'] = False
    out = []
    for tr in tracks:
        ys = sorted(tr['pts'])
        if len(ys) >= 110:
            out.append(tr['pts'])
    return out

def leg_summary(pts, Href, B):
    ys = sorted(pts)
    top_y, bot_y = min(ys), max(ys)
    hip = np.array([pts[top_y], float(top_y)])
    foot = np.array([pts[bot_y], float(bot_y)])
    mid_y = ys[len(ys) // 2]
    return dict(hip_xy=[round(float(hip[0]), 1), int(top_y)],
                foot_xy=[round(float(foot[0]), 1), int(bot_y)],
                mid_xy=[round(float(pts[mid_y]), 1), int(mid_y)],
                hip_minus_breast_over_H=[round(float((hip[0] - B[0]) / Href), 4),
                                         round(float((hip[1] - B[1]) / Href), 4)],
                foot_minus_breast_over_H=[round(float((foot[0] - B[0]) / Href), 4),
                                          round(float((foot[1] - B[1]) / Href), 4)],
                lean_deg=round(float(np.degrees(np.arctan2(foot[0] - hip[0], bot_y - top_y))), 2))

res = {}
# ---------------------------------------------------------------- approved
rest = np.asarray(Image.open(f'{RIGV2}/masks/approved_rest_mask.png')) > 0
Happ = 562.0
B = np.array([565.0, 221.0]); A = np.array([660.8, 53.3]); TIP = np.array([828.0, 63.0])
dt = ndimage.distance_transform_edt(rest)
yy, xx = np.mgrid[0:600, 0:1024]

tracks = track_legs(rest, 548, 330, (100, 680))
res['approved_legs'] = [leg_summary(t, Happ, B) for t in tracks]

# torso core, tightened exclusions
neck_zone = seg_dist(rest.shape, B, A) < 50
head_zone = (np.hypot(xx - A[0], yy - A[1]) < 0.20 * Happ) | (seg_dist(rest.shape, A, TIP) < 15)
core_a = rest & ~neck_zone & ~head_zone & (dt >= 13)
ys, xs = np.nonzero(core_a)
res['approved_torso_core'] = dict(
    area=int(core_a.sum()), cx=round(float(xs.mean()), 1), cy=round(float(ys.mean()), 1),
    centroid_minus_breast_over_H=[round(float((xs.mean() - B[0]) / Happ), 4),
                                  round(float((ys.mean() - B[1]) / Happ), 4)],
    bbox=[int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())])
# row-band masses of the core (upper/mid/lower thirds of its bbox)
y0, y1 = ys.min(), ys.max()
bands = {}
for i, (lo, hi) in enumerate(((0.0, 1 / 3), (1 / 3, 2 / 3), (2 / 3, 1.0))):
    m = core_a[int(y0 + lo * (y1 - y0)):int(y0 + hi * (y1 - y0)) + 1, :]
    bands[f'band{i}'] = round(float(m.sum() / core_a.sum()), 4)
res['approved_torso_core']['row_bands'] = bands

# plume strands: thin hanging pixels below core bottom, front fan, minus legs
core_bottom = np.full(W, -1)
for x in range(W):
    col = np.nonzero(core_a[:, x])[0]
    if len(col):
        core_bottom[x] = col.max()
leg_mask = np.zeros_like(rest)
for t in tracks:
    for y, cx in t.items():
        leg_mask[y, max(0, int(cx) - 9):int(cx) + 10] = True
res['plume_variants'] = {}
for ymax in (500, 530):
    pl = np.zeros_like(rest)
    for x in range(W):
        if core_bottom[x] >= 0:
            pl[core_bottom[x] + 3:ymax, x] = rest[core_bottom[x] + 3:ymax, x]
    pl &= ~leg_mask & ~head_zone & (dt < 10)
    pl[:, :int(B[0] - 235)] = False
    pl[:, int(B[0] + 55):] = False
    pl[:int(B[1]) - 5, :] = False
    if pl.sum() < 50:
        res['plume_variants'][f'ymax{ymax}'] = None
        continue
    env = ndimage.binary_closing(pl, np.ones((17, 17))) & ndimage.binary_dilation(pl, iterations=8)
    pys, pxs = np.nonzero(pl); eys, exs = np.nonzero(env)
    res['plume_variants'][f'ymax{ymax}'] = dict(
        strand_area=int(pl.sum()),
        strand_centroid_minus_breast_over_H=[round(float((pxs.mean() - B[0]) / Happ), 4),
                                             round(float((pys.mean() - B[1]) / Happ), 4)],
        envelope_area=int(env.sum()),
        envelope_centroid_minus_breast_over_H=[round(float((exs.mean() - B[0]) / Happ), 4),
                                               round(float((eys.mean() - B[1]) / Happ), 4)],
        fill=round(float(pl.sum() / max(env.sum(), 1)), 3),
        drop_strand_p95_over_H=round(float((np.percentile(pys, 95) - B[1]) / Happ), 4),
        drop_env_over_H=round(float((eys.max() - B[1]) / Happ), 4))
    if ymax == 500:
        np.save(f'{OUT}/approved_plume_strands.npy', pl)
        np.save(f'{OUT}/approved_leg_mask.npy', leg_mask)
        res['_plume_main'] = res['plume_variants']['ymax500']

# ---------------------------------------------------------------- rig v2.1
pose = copy.deepcopy(RC.CHARTS['idle_hunt']().frames[0])
pose['hx'], pose['hy'] = 36.17, -26.34
kpm = RR21.kp_master(pose)
scalars = dict(neck_w=float(pose['neck_w']), bulge_pos=float(pose['bulge_pos']),
               bulge_amp=float(pose['bulge_amp']), px_per_unit=U)
stack = M2.build_mask_stack(kpm, scalars, (W, H))
sil = np.any(stack > 0, axis=0)
Br = np.array(kpm['spine'][0], float); Ar = np.array(kpm['head_c'], float)
Hrig = 88.0 * U - (Ar[1] - 3.15 * 1.45 * U)
s = Hrig / Happ
res['rig'] = {'H_px': round(Hrig, 1), 'breast_px': [round(float(v), 1) for v in Br]}

tracks_r = track_legs(sil, 548, 280, (40, 560))
res['rig_legs_silhouette'] = [leg_summary(t, Hrig, Br) for t in tracks_r]
res['rig_legs_kp'] = {}
for nm in ('n', 'f'):
    hip = np.array(kpm[f'hip_{nm}'], float); foot = np.array(kpm[f'foot_{nm}'], float)
    res['rig_legs_kp'][nm] = dict(
        hip_minus_breast_over_H=[round(float((hip[0] - Br[0]) / Hrig), 4),
                                 round(float((hip[1] - Br[1]) / Hrig), 4)],
        foot_minus_breast_over_H=[round(float((foot[0] - Br[0]) / Hrig), 4),
                                  round(float((foot[1] - Br[1]) / Hrig), 4)])

torso_ch = (stack[0] > 0) | (stack[3] > 0) | (stack[6] > 0)
dt_r = ndimage.distance_transform_edt(torso_ch)
core_r = torso_ch & (dt_r >= 13 * s)
ys, xs = np.nonzero(core_r)
res['rig_torso_core_channels'] = dict(
    area=int(core_r.sum()),
    centroid_minus_breast_over_H=[round(float((xs.mean() - Br[0]) / Hrig), 4),
                                  round(float((ys.mean() - Br[1]) / Hrig), 4)])
# geometric method on the rig union, same exclusions (symmetry check)
neck_r = seg_dist(sil.shape, Br, Ar) < 50 * s
head_r = np.hypot(xx - Ar[0], yy - Ar[1]) < 0.20 * Hrig
core_g = sil & ~neck_r & ~head_r & ~((stack[7] > 0)) & ~((stack[4] > 0) | (stack[5] > 0)) \
    & (ndimage.distance_transform_edt(sil) >= 13 * s)
ys, xs = np.nonzero(core_g)
res['rig_torso_core_geometric'] = dict(
    area=int(core_g.sum()),
    centroid_minus_breast_over_H=[round(float((xs.mean() - Br[0]) / Hrig), 4),
                                  round(float((ys.mean() - Br[1]) / Hrig), 4)])
y0, y1 = np.nonzero(core_r)[0].min(), np.nonzero(core_r)[0].max()
bands = {}
for i, (lo, hi) in enumerate(((0.0, 1 / 3), (1 / 3, 2 / 3), (2 / 3, 1.0))):
    m = core_r[int(y0 + lo * (y1 - y0)):int(y0 + hi * (y1 - y0)) + 1, :]
    bands[f'band{i}'] = round(float(m.sum() / core_r.sum()), 4)
res['rig_torso_core_channels']['row_bands'] = bands

plume_r = stack[7] > 0
env_r = ndimage.binary_closing(plume_r, np.ones((15, 15))) & ndimage.binary_dilation(plume_r, iterations=7)
pys, pxs = np.nonzero(plume_r); eys, exs = np.nonzero(env_r)
res['rig_plume'] = dict(
    area=int(plume_r.sum()),
    centroid_minus_breast_over_H=[round(float((pxs.mean() - Br[0]) / Hrig), 4),
                                  round(float((pys.mean() - Br[1]) / Hrig), 4)],
    envelope_area=int(env_r.sum()),
    envelope_centroid_minus_breast_over_H=[round(float((exs.mean() - Br[0]) / Hrig), 4),
                                           round(float((eys.mean() - Br[1]) / Hrig), 4)],
    drop_max_over_H=round(float((pys.max() - Br[1]) / Hrig), 4),
    drop_p95_over_H=round(float((np.percentile(pys, 95) - Br[1]) / Hrig), 4))

# ---------------------------------------------------------------- fixed zone decomposition (v2.1)
iou21, prm21 = MV.aligned_iou(rest, sil)

def placed_mask(target, src, prm):
    Mc = ndimage.center_of_mass(target)
    S0 = ndimage.rotate(src.astype(float), prm['rot'], reshape=False, order=1) > 0.5
    sy, sx = np.nonzero(S0)
    crop = S0[sy.min():sy.max() + 1, sx.min():sx.max() + 1].astype(float)
    z = ndimage.zoom(crop, float(prm['scale']), order=1) > 0.5
    zh, zw = z.shape
    top = int(round(Mc[0] - zh / 2 + prm['dy'])); left = int(round(Mc[1] - zw / 2 + prm['dx']))
    canvas = np.zeros_like(target)
    ys0, ys1 = max(0, top), min(H, top + zh); xs0, xs1 = max(0, left), min(W, left + zw)
    canvas[ys0:ys1, xs0:xs1] = z[ys0 - top:ys1 - top, xs0 - left:xs1 - left]
    return canvas

placed = placed_mask(rest, sil, prm21)
plume_a = np.load(f'{OUT}/approved_plume_strands.npy')
leg_a = np.load(f'{OUT}/approved_leg_mask.npy')
zones = {}
zones['head'] = head_zone
zones['neck'] = neck_zone & ~head_zone
zones['legs'] = ndimage.binary_dilation(leg_a, iterations=8) & ~zones['head'] & ~zones['neck']
zones['plume'] = ndimage.binary_dilation(plume_a, iterations=8) & ~zones['legs'] & ~zones['neck'] & ~zones['head']
scen = np.zeros_like(rest); scen[558:, :] = True
zones['scenery'] = scen & ~zones['legs'] & ~zones['plume'] & ~zones['neck'] & ~zones['head']
used = np.zeros_like(rest)
for z in zones.values():
    used |= z
zones['torso_rest'] = ~used
dec = {}
miss = rest & ~placed; extra = placed & ~rest
for name, z in zones.items():
    dec[name] = dict(approved=int((rest & z).sum()), miss=int((miss & z).sum()),
                     extra=int((extra & z).sum()))
dec['TOTAL'] = dict(approved=int(rest.sum()), miss=int(miss.sum()), extra=int(extra.sum()))
res['zone_decomposition_v21_fixed'] = dec
res['v21_iou'] = (iou21, prm21)

with open(f'{OUT}/body_measurements2.json', 'w') as f:
    json.dump(res, f, indent=1)
print(json.dumps(res, indent=1))
