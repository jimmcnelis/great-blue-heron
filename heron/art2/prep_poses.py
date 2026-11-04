"""Derive the four art2 target poses from the KEPT animation data
(sheet13_r4.py pose definitions + cycles13_r4 episode frame 415) and their
keypoints in master pixel coords (1024x600). Writes poses_art2.json,
target mask stacks (full-frame + canonical 512 crop), and a debug sheet.
"""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.expanduser('~/workspace/heron/src13'))
sys.path.insert(0, HERE)
import rig13_r4 as R
import cycles13_r4 as C
import maskrender as M

U = R.U            # 6.6667 px per design unit at master
XOFF = R.XOFF      # 112.0

def mxy(p):
    p = np.asarray(p, float)
    return [float(XOFF + p[0] * U), float(p[1] * U)]

def rot(p, deg):
    th = np.deg2rad(deg)
    c, s = np.cos(th), np.sin(th)
    p = np.asarray(p, float)
    return np.array([c * p[0] - s * p[1], s * p[0] + c * p[1]])

def sheet_pose(**kw):
    p = R.default_pose(); p['root_x'] = 58.0
    for k, v in kw.items():
        if k in ('leg_near', 'leg_far'):
            p[k].update(v)
        else:
            p[k] = v
    return p

COIL = dict(body_tilt=24, coil=1.0, hx=25, hy=-15, head_pitch=16, root_y=1.5)
FLIGHT = dict(wing_mode='flight', body_tilt=2, coil=0.9, hx=24, hy=-14,
              head_pitch=-2, flap=-42, flap_tip=10,
              leg_near=dict(fx=-37, fy=53, toe=-55), leg_far=dict(fx=-34, fy=50, toe=-55))
FRONT = dict(yaw=90, hx=-2, hy=-27, body_tilt=4, coil=0.3)

_frames, _ink = C.build_episode()
SWAL = _frames[415]

POSES = {
    'rest': sheet_pose(),
    'front': sheet_pose(**FRONT),
    'flight': sheet_pose(**FLIGHT),
    'swallow': SWAL,
}

def keypoints_for(pose):
    xf, piv = R.body_xform(pose)
    st = R.YAW_STOPS.get(int(round(pose['yaw'])), R.YAW_STOPS[0])
    if int(round(pose['yaw'])) == 90:
        breast = np.array(xf((0.0, -5.0)))
    else:
        breast = np.array(xf((R.BREAST_LOCAL[0] + st['ndx'], R.BREAST_LOCAL[1])))
    spine, H = R.neck_spine(pose, breast)
    spine5 = [spine[i] for i in (0, 7, 14, 22, 29)]
    pitch = pose['head_pitch']
    xs = 0.74 if st['head'] == 'tq' else 1.0

    def W(p, front=False):
        q = np.asarray(p, float)
        if not front:
            q = np.array([q[0] * xs * R.HEAD_S, q[1] * R.HEAD_S])
        return rot(q, pitch) + H

    if st['head'] == 'front':
        skull = [(-3.4, -2.2), (0, -3.3), (3.4, -2.2), (3.9, 0.4),
                 (2.3, 2.7), (-2.3, 2.7), (-3.9, 0.4)]
        g = pose['gape'] * 1.1
        bill = [(-1.05, 0.7), (1.05, 0.7), (0.5 + g, 5.4), (-0.5 - g, 5.4)]
        bill_poly = [W(p, front=True) for p in skull] + [W(p, front=True) for p in bill]
    else:
        skull = [(-4.6, -1.1), (-3.5, -2.8), (-0.6, -3.15), (2.1, -2.3),
                 (3.6, -0.9), (3.9, 0.5), (2.1, 1.9), (-0.8, 2.45), (-3.7, 1.5)]
        bill = [(2.5, -1.55), (R.HINGE[0] + R.BILL_LEN, 0.5), (3.45, 1.55)]
        bill_poly = [W(p) for p in skull] + [W(p) for p in bill]

    kp = {}
    kp['torso_poly'] = [xf(p) for p in R.TORSO]
    kp['spine'] = spine5
    kp['head_c'] = H
    kp['bill_tip'] = R.bill_tip(pose)
    kp['bill_poly'] = bill_poly
    kp['tail_poly'] = [xf(R.TORSO[0]), xf((-16.5, -4.6)), xf((-17.0, 4.4))]
    # PLUME skirt (Jimmy 2026-11-02 22:45): its own region, hanging from the
    # breast over the upper legs — never part of torso/leg masks.
    if int(round(pose['yaw'])) == 90:
        offs = [(-3.6, -2.0), (3.6, -2.0), (3.2, 7.0), (1.2, 11.5),
                (-1.2, 11.5), (-3.2, 7.0)]
    elif pose['wing_mode'] == 'flight':
        offs = [(-2.0, -2.5), (3.5, -2.0), (4.5, 3.0), (1.0, 6.5),
                (-2.5, 3.5)]
    else:
        offs = [(-2.5, -3.0), (2.0, -4.0), (5.0, -0.5), (4.6, 6.0),
                (2.6, 11.5), (0.2, 13.0), (-2.2, 8.0), (-3.2, 2.0)]
    kp['plume_poly'] = [np.asarray(breast, float) + np.array(o) for o in offs]
    if pose['wing_mode'] == 'flight':
        root = np.array(xf((5.0, -6.0)))
        pts, _w = R._wing_outline(pose['flap'], pose['flap_tip'], 1.0, 0.0)
        kp['wing_poly'] = [root + np.asarray(q, float) for q in pts]
    else:
        kp['wing_poly'] = [xf(p) for p in R.WING]
    for name, leg, hip_local in (('n', pose['leg_near'], R.HIP_NEAR),
                                 ('f', pose['leg_far'], R.HIP_FAR)):
        hip = np.array(xf(hip_local))
        foot = np.array([pose['root_x'] + leg['fx'] * st['spread'], leg['fy']])
        if leg['fx'] < -18:
            d = foot - hip; L = max(np.hypot(*d), 1e-9); d = d / L
            perp = np.array([-d[1], d[0]])
            knee = hip + d * L * 0.52 + perp * 0.8
        else:
            knee = R.leg_ik(hip, foot)
        kp[f'hip_{name}'] = hip; kp[f'knee_{name}'] = knee; kp[f'foot_{name}'] = foot
    return kp

POSE_SCALARS = ['coil', 'neck_w', 'head_pitch', 'body_tilt', 'yaw',
                'bulge_pos', 'bulge_amp', 'flap', 'flap_tip', 'gape',
                'plume_sway']

def pose_vector(pose):
    return [float(pose['coil']), float(pose['neck_w']),
            float(pose['head_pitch']) / 60.0, float(pose['body_tilt']) / 40.0,
            float(pose['yaw']) / 180.0, float(pose['bulge_pos']),
            float(pose['bulge_amp']), float(pose['flap']) / 60.0,
            float(pose['flap_tip']) / 30.0,
            1.0 if pose['wing_mode'] == 'flight' else 0.0,
            float(pose['gape']), float(pose['plume_sway']) / 3.0]

def jsonsafe_pose(pose):
    out = {}
    for k, v in pose.items():
        if isinstance(v, dict):
            out[k] = {kk: float(vv) for kk, vv in v.items()}
        elif isinstance(v, tuple):
            out[k] = [float(x) for x in v]
        elif isinstance(v, (int, float)):
            out[k] = float(v)
        else:
            out[k] = v
    return out

os.makedirs(os.path.join(HERE, 'targets'), exist_ok=True)
data = {'master': [1024, 600], 'px_per_unit': U, 'poses': {}}
debug = Image.new('RGB', (1024 * 2, 600 * 2), 'white')
dd = ImageDraw.Draw(debug)
CH_COLORS = [(200, 60, 60), (60, 160, 60), (60, 60, 220), (220, 160, 40),
             (160, 60, 200), (60, 180, 200), (120, 120, 120), (240, 110, 180)]
for i, (name, pose) in enumerate(POSES.items()):
    kp_d = keypoints_for(pose)
    kp_m = {k: ([mxy(p) for p in v] if k in ('torso_poly', 'spine', 'bill_poly',
                                             'wing_poly', 'tail_poly', 'plume_poly')
                else mxy(v)) for k, v in kp_d.items()}
    scalars = dict(neck_w=float(pose['neck_w']), bulge_pos=float(pose['bulge_pos']),
                   bulge_amp=float(pose['bulge_amp']), px_per_unit=U)
    stack = M.build_mask_stack(kp_m, scalars, (1024, 600))
    np.savez_compressed(os.path.join(HERE, 'targets', f'mask_{name}.npz'),
                        mask=stack, pose=np.array(pose_vector(pose), np.float32))
    pts = M.all_points(kp_m)
    crop = M.crop_spec(pts)
    data['poses'][name] = dict(pose=jsonsafe_pose(pose), keypoints_master=kp_m,
                               scalars=scalars, crop_master=crop,
                               pose_vector=pose_vector(pose))
    # debug render
    ox, oy = (i % 2) * 1024, (i // 2) * 600
    comp = np.zeros((600, 1024, 3), np.uint8)
    for ci in range(8):
        comp[stack[ci] > 0] = CH_COLORS[ci]
    debug.paste(Image.fromarray(comp), (ox, oy))
    dd.text((ox + 12, oy + 10), name.upper(), fill=(0, 0, 0))
    x0, y0, side = crop
    dd.rectangle([ox + x0, oy + y0, ox + x0 + side, oy + y0 + side],
                 outline=(255, 0, 255), width=3)
with open(os.path.join(HERE, 'poses_art2.json'), 'w') as f:
    json.dump(data, f, indent=1)
debug.save(os.path.join(HERE, 'targets', 'debug_masks.png'))
print('poses written:', list(data['poses'].keys()))
for n, d in data['poses'].items():
    print(n, 'crop', [round(v, 1) for v in d['crop_master']],
          'bulge', d['pose']['bulge_pos'], d['pose']['bulge_amp'], 'yaw', d['pose']['yaw'])
