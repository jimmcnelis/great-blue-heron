#!/usr/bin/env python3
"""Body-placement round: measure the BODY of the idle hold off the
approved rest still and off the rig v2.1 mask stack, in the same
terms both sides (breast-relative, H-normalised), plus a zone
decomposition of the v2.1 aligned proof-(1) placement.

Approved-side instruments mirror Phase A / head-anchor practice:
gate mask (saved, byte-identical area 96,492), DT cores for solid
mass, thin/hanging components for legs and plume strands. Plume law
applied: legs are read from the anatomical structures under the
plume skirt, never from the plume-blended outline.
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
    """Distance from every pixel to segment a->b."""
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]]
    a = np.asarray(a, float); b = np.asarray(b, float)
    d = b - a; L2 = float(d @ d)
    t = ((xx - a[0]) * d[0] + (yy - a[1]) * d[1]) / L2
    t = np.clip(t, 0, 1)
    px = a[0] + t * d[0]; py = a[1] + t * d[1]
    return np.hypot(xx - px, yy - py)

def comp_table(mask, min_area=120):
    lab, n = ndimage.label(mask, np.ones((3, 3)))
    out = []
    for i in range(1, n + 1):
        m = lab == i
        area = int(m.sum())
        if area < min_area:
            continue
        ys, xs = np.nonzero(m)
        out.append(dict(id=i, area=area, x0=int(xs.min()), x1=int(xs.max()),
                        y0=int(ys.min()), y1=int(ys.max()),
                        cx=round(float(xs.mean()), 1), cy=round(float(ys.mean()), 1)))
    return out, lab

def pt_stats(m):
    ys, xs = np.nonzero(m)
    return dict(area=int(m.sum()), cx=round(float(xs.mean()), 1), cy=round(float(ys.mean()), 1),
                x0=int(xs.min()), x1=int(xs.max()), y0=int(ys.min()), y1=int(ys.max()))

# ---------------------------------------------------------------- approved
rest = np.asarray(Image.open(f'{RIGV2}/masks/approved_rest_mask.png')) > 0
Happ = 562.0
B = np.array([565.0, 221.0])      # breast anchor (certified, head-anchor round)
A = np.array([660.8, 53.3])       # head anchor (certified)
TIP = np.array([828.0, 63.0])
dt = ndimage.distance_transform_edt(rest)

neck_zone = seg_dist(rest.shape, B, A) < 42
yy, xx = np.mgrid[0:600, 0:1024]
head_zone = (np.hypot(xx - A[0], yy - A[1]) < 66) | (seg_dist(rest.shape, A, TIP) < 15)
torso_zone = rest & ~neck_zone & ~head_zone
core = torso_zone & (dt >= 13)

res = {'approved': {}}
res['approved']['mask_area'] = int(rest.sum())
res['approved']['torso_zone'] = pt_stats(torso_zone)
res['approved']['torso_core'] = pt_stats(core)
for name, m in (('torso_zone', torso_zone), ('torso_core', core)):
    c = np.array([res['approved'][name]['cx'], res['approved'][name]['cy']])
    res['approved'][name]['centroid_minus_breast_px'] = [round(float(v), 1) for v in (c - B)]
    res['approved'][name]['centroid_minus_breast_over_H'] = [round(float(v) / Happ, 4) for v in (c - B)]

# hanging structures: mask pixels below the torso-core bottom boundary
core_bottom = np.full(W, -1)
for x in range(W):
    col = np.nonzero(core[:, x])[0]
    if len(col):
        core_bottom[x] = col.max()
hang = np.zeros_like(rest)
cols = np.nonzero(core_bottom >= 0)[0]
for x in cols:
    hang[core_bottom[x] + 3:, x] = rest[core_bottom[x] + 3:, x]
hang &= ~neck_zone & ~head_zone
comps, lab = comp_table(hang, min_area=100)
res['approved']['hanging_components'] = comps

# legs = hanging comps reaching the waterline with a high top
legs = [c for c in comps if c['y1'] >= 535 and c['y0'] <= 470 and (c['y1'] - c['y0']) >= 120]
res['approved']['legs_found'] = []
for c in legs:
    m = lab == c['id']
    top = np.nonzero(m[c['y0']:c['y0'] + 6, :])[1]
    bot = np.nonzero(m[c['y1'] - 5:c['y1'] + 1, :])[1]
    mid_y = (c['y0'] + c['y1']) // 2
    mid = np.nonzero(m[mid_y - 2:mid_y + 3, :])[1]
    res['approved']['legs_found'].append(dict(
        area=c['area'], hip_xy=[round(float(top.mean()), 1), c['y0']],
        foot_xy=[round(float(bot.mean()), 1), c['y1']],
        mid_xy=[round(float(mid.mean()), 1) if len(mid) else None, mid_y],
        bbox=[c['x0'], c['x1'], c['y0'], c['y1']]))
if len(legs) >= 2:
    hips = [l['hip_xy'] for l in res['approved']['legs_found']]
    feet = [l['foot_xy'] for l in res['approved']['legs_found']]
    res['approved']['hip_separation_px'] = round(abs(hips[0][0] - hips[1][0]), 1)
    res['approved']['stance_px'] = round(abs(feet[0][0] - feet[1][0]), 1)
    res['approved']['hips_minus_breast_over_H'] = [[round((h[0] - B[0]) / Happ, 4),
                                                    round((h[1] - B[1]) / Happ, 4)] for h in hips]
    res['approved']['feet_minus_breast_over_H'] = [[round((f[0] - B[0]) / Happ, 4),
                                                    round((f[1] - B[1]) / Happ, 4)] for f in feet]

# plume = hanging comps in the front fan (not legs, not rear underside)
leg_ids = {c['id'] for c in legs}
plume = np.zeros_like(rest)
for c in comps:
    if c['id'] in leg_ids:
        continue
    if B[0] - 230 <= c['cx'] <= B[0] + 50 and c['y1'] <= 545:
        plume |= lab == c['id']
if plume.any():
    st = pt_stats(plume)
    st['centroid_minus_breast_over_H'] = [round((st['cx'] - B[0]) / Happ, 4),
                                          round((st['cy'] - B[1]) / Happ, 4)]
    st['drop_max_over_H'] = round((st['y1'] - B[1]) / Happ, 4)
    ys = np.nonzero(plume)[0]
    st['drop_p95_over_H'] = round((float(np.percentile(ys, 95)) - B[1]) / Happ, 4)
    res['approved']['plume'] = st
res['approved']['scenery_y_ge_558'] = int(rest[558:, :].sum())
res['approved']['thin_grass_comps'] = [c for c in comps
                                       if c['id'] not in leg_ids and c['y0'] >= 440 and c['y1'] >= 500]

# ---------------------------------------------------------------- rig v2.1
def hold_pose(rig_tracks_pose=None):
    pose = copy.deepcopy(RC.CHARTS['idle_hunt']().frames[0])
    pose['hx'], pose['hy'] = 36.17, -26.34
    return pose

def stack_of(RR, pose):
    kpm = RR.kp_master(pose)
    scalars = dict(neck_w=float(pose['neck_w']), bulge_pos=float(pose['bulge_pos']),
                   bulge_amp=float(pose['bulge_amp']), px_per_unit=RR.U)
    return M2.build_mask_stack(kpm, scalars, (W, H)), kpm

pose21 = hold_pose()
stack21, kpm21 = stack_of(RR21, pose21)
sil21 = np.any(stack21 > 0, axis=0)
breast_r = np.array(kpm21['spine'][0], float)
anchor_r = np.array(kpm21['head_c'], float)
crown_y = anchor_r[1] - 3.15 * 1.45 * U
foot_y = 88.0 * U
Hrig = foot_y - crown_y
s = Hrig / Happ
res['rig_v21'] = {'H_px': round(Hrig, 1), 'breast_px': [round(float(v), 1) for v in breast_r],
                  'anchor_px': [round(float(v), 1) for v in anchor_r]}
torso_r = (stack21[0] > 0) | (stack21[3] > 0) | (stack21[6] > 0)
dt_r = ndimage.distance_transform_edt(torso_r)
core_r = torso_r & (dt_r >= 13 * s)
for name, m in (('torso_mass', torso_r), ('torso_core', core_r)):
    st = pt_stats(m)
    st['centroid_minus_breast_over_H'] = [round((st['cx'] - breast_r[0]) / Hrig, 4),
                                          round((st['cy'] - breast_r[1]) / Hrig, 4)]
    res['rig_v21'][name] = st
plume_r = stack21[7] > 0
st = pt_stats(plume_r)
st['centroid_minus_breast_over_H'] = [round((st['cx'] - breast_r[0]) / Hrig, 4),
                                      round((st['cy'] - breast_r[1]) / Hrig, 4)]
st['drop_max_over_H'] = round((st['y1'] - breast_r[1]) / Hrig, 4)
ys = np.nonzero(plume_r)[0]
st['drop_p95_over_H'] = round((float(np.percentile(ys, 95)) - breast_r[1]) / Hrig, 4)
res['rig_v21']['plume'] = st
res['rig_v21']['legs_kp'] = {}
for nm in ('n', 'f'):
    hip = np.array(kpm21[f'hip_{nm}'], float); knee = np.array(kpm21[f'knee_{nm}'], float)
    foot = np.array(kpm21[f'foot_{nm}'], float)
    res['rig_v21']['legs_kp'][nm] = dict(
        hip=[round(float(v), 1) for v in hip], knee=[round(float(v), 1) for v in knee],
        foot=[round(float(v), 1) for v in foot],
        hip_minus_breast_over_H=[round(float((hip[0] - breast_r[0]) / Hrig), 4),
                                 round(float((hip[1] - breast_r[1]) / Hrig), 4)],
        foot_minus_breast_over_H=[round(float((foot[0] - breast_r[0]) / Hrig), 4),
                                  round(float((foot[1] - breast_r[1]) / Hrig), 4)])
res['rig_v21']['hip_separation_over_H'] = round(abs(
    res['rig_v21']['legs_kp']['n']['hip'][0] - res['rig_v21']['legs_kp']['f']['hip'][0]) / Hrig, 4)
res['rig_v21']['stance_over_H'] = round(abs(
    res['rig_v21']['legs_kp']['n']['foot'][0] - res['rig_v21']['legs_kp']['f']['foot'][0]) / Hrig, 4)

# ---------------------------------------------------------------- controls
sil2, _, _ = MV.sil_of(MV.RR2, MV.M2, 'idle_hunt', 0)
iou2 = MV.aligned_iou(rest, sil2)
iou21, prm21 = MV.aligned_iou(rest, sil21)
res['controls'] = {'v2_mask_iou': iou2, 'v21_mask_iou': (iou21, prm21)}

# ---------------------------------------------------------------- zone decomposition (v2.1 placement)
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

placed = placed_mask(rest, sil21, prm21)
leg_zone = np.zeros_like(rest)
for c in legs:
    leg_zone |= lab == c['id']
leg_zone = ndimage.binary_dilation(leg_zone, iterations=10)
plume_zone = ndimage.binary_dilation(plume, iterations=10) if plume.any() else plume
scenery = np.zeros_like(rest); scenery[558:, :] = True
zones = {}
zones['head'] = head_zone
zones['neck'] = neck_zone & ~head_zone
zones['legs'] = leg_zone & ~head_zone & ~neck_zone
zones['plume'] = plume_zone & ~zones['legs'] & ~neck_zone & ~head_zone
zones['scenery'] = scenery & ~zones['legs'] & ~zones['plume'] & ~neck_zone & ~head_zone
used = np.zeros_like(rest)
for z in zones.values():
    used |= z
zones['torso_rest'] = ~used
dec = {}
miss = rest & ~placed
extra = placed & ~rest
for name, z in zones.items():
    dec[name] = dict(approved=int((rest & z).sum()), miss=int((miss & z).sum()),
                     extra=int((extra & z).sum()))
dec['TOTAL'] = dict(approved=int(rest.sum()), miss=int(miss.sum()), extra=int(extra.sum()),
                    union=int((rest | placed).sum()), inter=int((rest & placed).sum()))
res['zone_decomposition_v21'] = dec

with open(f'{OUT}/body_measurements.json', 'w') as f:
    json.dump(res, f, indent=1)
print(json.dumps(res, indent=1))
