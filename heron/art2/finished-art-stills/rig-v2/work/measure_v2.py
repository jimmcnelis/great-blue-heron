#!/usr/bin/env python3
"""Rig-v2 measurement: v2 mask silhouettes vs approved stills + landmarks.

Surfaces: local VM, files in this workspace. Silhouettes are the mask-stack
union from roster_render_v2.kp_master + maskrender_v2.build_mask_stack —
the exact conditioning geometry the Fix-1 decoder will be fed, and the
same canvas-side silhouette definition gate.py uses.
"""
import json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

HOME = os.path.expanduser('~')
ART2 = f'{HOME}/workspace/heron/art2'
sys.path.insert(0, ART2)
sys.path.insert(0, f'{HOME}/workspace/heron/src13')
sys.path.insert(0, f'{ART2}/finished-art-stills/refinish-corpus/work')
import gate
import roster_charts as RC
import roster_render as RR1
import roster_render_v2 as RR2
import maskrender as M1
import maskrender_v2 as M2

W, H = 1024, 600
OUT = f'{ART2}/finished-art-stills/rig-v2'

def sil_of(RR, M, chart, idx):
    pose = RC.CHARTS[chart]().frames[idx]
    kpm = RR.kp_master(pose)
    scalars = dict(neck_w=float(pose['neck_w']), bulge_pos=float(pose['bulge_pos']),
                   bulge_amp=float(pose['bulge_amp']), px_per_unit=RR.U)
    stack = M.build_mask_stack(kpm, scalars, (W, H))
    return np.any(stack > 0, axis=0), pose, kpm

def bbox(m):
    ys, xs = np.nonzero(m)
    return dict(x0=int(xs.min()), x1=int(xs.max()), y0=int(ys.min()), y1=int(ys.max()),
                area=int(m.sum()))

def aligned_iou(target, src, rots=(0, -6, -3, 3, 6), scales=None, step=6):
    """Best IoU of src rigid-aligned (rot + uniform scale + translation)
    onto target. Search identical in spirit to the old-baseline run."""
    if scales is None:
        scales = np.linspace(0.8, 1.35, 23)
    Mc = ndimage.center_of_mass(target)
    best = (0.0, None)
    for rot in rots:
        S0 = ndimage.rotate(src.astype(float), rot, reshape=False, order=1) > 0.5
        sy, sx = np.nonzero(S0)
        crop = S0[sy.min():sy.max() + 1, sx.min():sx.max() + 1].astype(float)
        for s in scales:
            z = ndimage.zoom(crop, float(s), order=1) > 0.5
            zh, zw = z.shape
            for dy in range(-24, 25, step):
                for dx in range(-24, 25, step):
                    top = int(round(Mc[0] - zh / 2 + dy)); left = int(round(Mc[1] - zw / 2 + dx))
                    canvas = np.zeros_like(target)
                    ys0, ys1 = max(0, top), min(H, top + zh); xs0, xs1 = max(0, left), min(W, left + zw)
                    if ys1 <= ys0 or xs1 <= xs0:
                        continue
                    canvas[ys0:ys1, xs0:xs1] = z[ys0 - top:ys1 - top, xs0 - left:xs1 - left]
                    inter = np.logical_and(target, canvas).sum(); union = np.logical_or(target, canvas).sum()
                    v = inter / union if union else 0.0
                    if v > best[0]:
                        best = (float(v), dict(rot=rot, scale=round(float(s), 3), dx=dx, dy=dy))
    return best

def dist(a, b):
    return float(np.hypot(*(np.array(a, float) - np.array(b, float))))

def landmarks(RR, pose):
    kp = RR.keypoints_for(pose)
    Hc = np.array(kp['head_c'])
    skull_top = 3.15 * RR.R.HEAD_S
    crown_y = Hc[1] - skull_top
    foot_y = 88.0
    Hgt = foot_y - crown_y
    torso = np.array(kp['torso_poly'])
    plume = np.array(kp['plume_poly'])
    breast = np.array(kp['spine'][0])
    return dict(
        height_units=round(Hgt, 1),
        torso_w_over_H=round(float(torso[:, 0].max() - torso[:, 0].min()) / Hgt, 3),
        torso_d_over_H=round(float(torso[:, 1].max() - torso[:, 1].min()) / Hgt, 3),
        head_tip_over_H=round(dist(Hc, kp['bill_tip']) / Hgt, 3),
        plume_drop_over_H=round(float(plume[:, 1].max() - breast[1]) / Hgt, 3),
        leg_n=[round(dist(kp['hip_n'], kp['knee_n']), 1), round(dist(kp['knee_n'], kp['foot_n']), 1)],
        torso_bbox_units=[round(float(torso[:, 0].max() - torso[:, 0].min()), 1),
                          round(float(torso[:, 1].max() - torso[:, 1].min()), 1)])

if __name__ == '__main__':
    os.makedirs(f'{OUT}/masks', exist_ok=True)
    res = {}
    for name in ('rest', 'strike'):
        a = gate.load_norm(f'{ART2}/finished-art-stills/audubon_{name}.png')
        bm = gate.bird_mask(a)
        Image.fromarray((bm * 255).astype(np.uint8)).save(f'{OUT}/masks/approved_{name}_mask.png')
        res[f'approved_{name}'] = bbox(bm)
    rest = np.asarray(Image.open(f'{OUT}/masks/approved_rest_mask.png')) > 0

    sil1, pose1, _ = sil_of(RR1, M1, 'idle_hunt', 0)
    sil2, pose2, _ = sil_of(RR2, M2, 'idle_hunt', 0)
    Image.fromarray((sil1 * 255).astype(np.uint8)).save(f'{OUT}/masks/rig_v1_idle_silhouette.png')
    Image.fromarray((sil2 * 255).astype(np.uint8)).save(f'{OUT}/masks/rig_v2_idle_silhouette.png')
    res['rig_v1_idle_sil'] = bbox(sil1)
    res['rig_v2_idle_sil'] = bbox(sil2)
    res['iou_v1_idle_vs_approved_rest'] = aligned_iou(rest, sil1)
    res['iou_v2_idle_vs_approved_rest'] = aligned_iou(rest, sil2)
    res['landmarks_v1_idle'] = landmarks(RR1, pose1)
    res['landmarks_v2_idle'] = landmarks(RR2, pose2)

    clip = []
    for chart, idx, tag in [('idle_hunt', 0, 'idle_hold')] + [('strike', i, f'strike_f{i:04d}') for i in range(52)]:
        s, _, _ = sil_of(RR2, M2, chart, idx)
        b = bbox(s)
        edges = [k for k, cond in (('left', b['x0'] <= 0), ('right', b['x1'] >= W - 1),
                                   ('top', b['y0'] <= 0), ('bottom', b['y1'] >= H - 1)) if cond]
        if edges:
            clip.append(dict(pair=tag, edges=edges, bbox=b))
    res['v2_clipping'] = clip
    print(json.dumps(res, indent=1))
    with open(f'{OUT}/work/measure_v2_out.json', 'w') as f:
        json.dump(res, f, indent=1)
