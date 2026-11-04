#!/usr/bin/env python3
"""FILL TEST v2.5 — Path-3 fill on the settled rig v2.5 (iter2 build).

One full strike cycle at 1024x600, 24 fps, built ONLY from:
  - geometry: rig v2.5 mechanism (species package animal_v25.json /
    rig_v25.py, build rig-v25-mechanism-iter2). Poses are heading-profile
    states; intermediate poses interpolate the sampled heading profiles.
  - fill: spike 1's recipe, corrected per the brief —
    * body/legs texture = the approved strike still at identity (the
      v2.5 torso loop and legs were traced from it; the torso is one
      rigid body in every pose, so this is exact by construction),
    * neck texture = donor gold warped TUBE-TO-TUBE (arc fraction x
      cross fraction between donor spine and the v2.5 chain),
    * head texture = donor gold warped by the head-frame similarity
      (donor head_c/bill_tip -> v2.5 skull/bill tip), pasted into the
      head assembly region (skull ellipse + occipital spike + crest
      fan). Head+bill are ONE distal assembly: no separate head
      registration step exists in this build.
    * bill drawn explicitly from the mechanism bill triangle with
      spike 1's extracted (axial x cross) colour profile,
    * eye drawn at the MECHANISM eye anchor on every frame, then
      PIXEL-VERIFIED (spike 3 disclosed spikes 1-2's eye never drew;
      here the anchor region's pixels are sampled and reported),
    * crest + breast-plume strand reinforcement in geometry zones,
    * structural ink: per-region quantile luminance remap (spike 1's
      ink_remap). Neck/head targets = donor regional black rescaled
      by k = 0.262 / donor total black, so the sequence's ink level
      sits at the approved family level on every frame (gate 3).
      Torso/legs carry the approved still's own ink (no remap).
    * a final global trim (<=3 passes, bill/eye protected) keeps the
      whole-frame black fraction inside the gate band.
Deterministic: no RNG anywhere; same inputs -> same bytes.
"""
import hashlib, json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from scipy.interpolate import PchipInterpolator
from scipy.spatial import cKDTree

H_ = os.path.expanduser('~')
for p in (f'{H_}/workspace/heron/art2', f'{H_}/workspace/heron/src13',
          f'{H_}/workspace/heron/art2/finished-art-stills/finish-model-v3',
          f'{H_}/workspace/heron/art2/fill-spike-v1',
          f'{H_}/workspace/heron/art2/fill-spike-v3'):
    sys.path.insert(0, p)
import spike_fill as S1
import build_corpus as bc
import roster_render_v24 as RR
import drawn_landmarks as DL
import importlib.util
_spec = importlib.util.spec_from_file_location(
    'rig25', f'{H_}/workspace/creature-engine/packages/great-blue-heron/rig_v25.py')
R25 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(R25)

W, H = 1024, 600
FS = f'{H_}/workspace/heron/art2/finished-art-stills'
FM3 = f'{FS}/finish-model-v3'
OUT = f'{H_}/workspace/heron/art2/fill-test-v25'
T = R25.T
ANIMAL = R25.ANIMAL
TARGET_BLACK = 0.262
BAND = (0.252, 0.272)

load = S1.load
content_mask, color_fracs, ink_remap = S1.content_mask, S1.color_fracs, S1.ink_remap

REST = load(f'{FS}/audubon_rest.png')
STRIKE = load(f'{FS}/audubon_strike.png')
PAPER = S1.paper_color(REST)

# ---------------------------------------------------------------- donors
tracks24 = json.load(open(f'{FS}/rig-v2/band-pass/pose_tracks_v24.json'))
tracks2 = json.load(open(f'{FS}/rig-v2/work/pose_tracks_v2.json'))
IDLE_POSE = tracks24['idle'][0]

_donor_cache = {}

def donor(pid):
    """-> dict(img, stack, kp, total_black, neck_black, head_black,
    spine_dense, spine_hw, spine_nrm) for a corpus gold pair id."""
    if pid in _donor_cache:
        return _donor_cache[pid]
    img = load(f'{FM3}/corpus/target/{pid}.png')
    if pid.startswith('idle'):
        pose = IDLE_POSE
    else:
        pose = tracks2['strike'][int(pid[-4:])]
    stack = bc.stack_for(pose)
    kp = RR.kp_master(pose)
    cm = content_mask(img)
    lum = img.mean(axis=2)
    neck_m = stack[1] > 0
    head_m = stack[2] > 0
    # densified spine + halfwidths from the neck channel DT
    spine = np.array(kp['spine'], float)
    dense = R25.dense_chain(spine, step=2.0)
    dt = ndimage.distance_transform_edt(neck_m | head_m)
    hw = np.array([dt[min(max(int(round(y)), 0), H - 1),
                      min(max(int(round(x)), 0), W - 1)] for x, y in dense])
    hw = np.maximum(hw, 3.0)
    d = np.gradient(dense, axis=0)
    n = np.hypot(d[:, 0], d[:, 1]); n[n == 0] = 1
    nrm = np.stack([-d[:, 1] / n, d[:, 0] / n], axis=1)
    s_cum = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(dense, axis=0).T))])
    d = dict(img=img, stack=stack, kp=kp,
             total_black=color_fracs(img, cm)['black'],
             neck_black=float((lum[neck_m] < 70).mean()) if neck_m.any() else 0.0,
             head_black=float((lum[head_m] < 70).mean()) if head_m.any() else 0.0,
             spine_dense=dense, spine_hw=hw, spine_nrm=nrm,
             spine_u=s_cum / max(s_cum[-1], 1e-9),
             neck_chan=neck_m, head_chan=head_m)
    _donor_cache[pid] = d
    return d

# bill colour profile (spike 1 extraction; colours only) + iris colour
BILL_PROF = S1.extract_bill_profile()
def extract_iris():
    g = load(f'{FM3}/corpus/target/idle_f0030.png')
    st = bc.stack_for(IDLE_POSE)
    kp = RR.kp_master(IDLE_POSE)
    tri = np.array([kp['bill_poly'][9], kp['bill_poly'][10], kp['bill_poly'][11]])
    ys, xs = np.mgrid[0:H, 0:W]
    _, _, inside = S1.tri_coords(np.stack([ys.ravel(), xs.ravel()], 1), tri)
    head_zone = (st[2] > 0) & ~inside.reshape(H, W)
    comps = DL.comps(DL.iris_mask(g) & head_zone)
    for size, cen, _ in comps:
        if size >= 15:
            m = np.zeros((H, W), bool)
            yy, xx = np.nonzero(DL.iris_mask(g) & head_zone)
            sel = np.hypot(xx - cen[0], yy - cen[1]) < 12
            return np.median(g[yy[sel], xx[sel]], axis=0), int(size), cen
    return np.array([176., 128., 44.]), 0, None
IRIS_COL, IRIS_PX, IRIS_CEN = extract_iris()

# ---------------------------------------------------------------- poses
SGRID = np.linspace(0, 1, 201)
def pose_profile(name):
    spec = ANIMAL['poses'][name]
    k = np.array(spec['knots'], float)
    return PchipInterpolator(k[:, 0], k[:, 1])(SGRID), spec['head_pitch_offset_deg']
PROF = {n: pose_profile(n) for n in ('alert', 'deep_coil', 'strike_peak')}

def blend_profile(terms):
    th = sum(w * PROF[n][0] for n, w in terms)
    pitch = sum(w * PROF[n][1] for n, w in terms)
    return th, pitch

def profile_from_grid(th_grid):
    return PchipInterpolator(SGRID, th_grid)

def build_chain_grid(th_grid, pitch_off):
    """rig_v25.build_chain math on an arbitrary heading-profile grid."""
    prof = profile_from_grid(th_grid)
    SEG, ARC = R25.SEG, R25.ARC
    s_edges = np.concatenate([[0], np.cumsum(SEG) / ARC])
    heads = []
    for i in range(R25.N):
        ss = np.linspace(s_edges[i], s_edges[i + 1], 9)
        heads.append(float(np.trapezoid(prof(ss), ss) / (ss[-1] - ss[0])))
    heads = np.array(heads)
    pts = [R25.ROOT.copy()]
    for i in range(R25.N):
        a = math.radians(heads[i])
        pts.append(pts[-1] + R25.SEG_PX[i] * np.array([math.cos(a), math.sin(a)]))
    return np.array(pts), heads

def frame_geometry(th_grid, pitch_off, slim_f):
    pts, heads = build_chain_grid(th_grid, pitch_off)
    dense = R25.dense_chain(pts)
    s_cum = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(dense, axis=0).T))])
    u = s_cum / max(s_cum[-1], 1e-9)
    widths = R25.width_rest(np.clip(u, 0, 1)) * T
    if slim_f > 0:
        widths = widths * (1 - slim_f + slim_f * R25.slim_mult(np.clip(u, 0, 1)))
    vis, neckbase = R25.visible_chain(pts)
    skull = pts[-1]
    final_head = heads[-1] + pitch_off
    a = math.radians(final_head)
    dvec = np.array([math.cos(a), math.sin(a)])
    perp = np.array([dvec[1], -dvec[0]])
    ha = ANIMAL['head_assembly']
    base_c = skull + dvec * ha['bill_base_offset_from_skull_centre'] * T
    tip = skull + dvec * ha['bill_tip_reach_from_skull_centre'] * T
    bw = 0.0135 * T
    eye = (skull + dvec * ha['eye_anchor_in_head_frame']['along_bill'] * T
           + perp * ha['eye_anchor_in_head_frame']['up'] * T)
    ell = [skull + (dvec * math.cos(t) * ha['skull_semi_major'] * T
                    + np.array([-dvec[1], dvec[0]]) * math.sin(t)
                    * ha['skull_semi_minor'] * T)
           for t in np.linspace(0, 2 * math.pi, 40)]
    plume_tip = skull + (dvec * -0.115 + perp * -0.030) * T
    plume_b = skull + (dvec * -0.01 + perp * 0.018) * T
    plume_c = skull + (dvec * -0.03 + perp * -0.022) * T
    return dict(pts=pts, heads=heads, dense=dense, u=u, widths=widths,
                neckbase=neckbase, skull=skull, dvec=dvec, perp=perp,
                base_c=base_c, tip=tip, bw=bw, eye=eye, ell=ell,
                plume_tri=[plume_b, plume_tip, plume_c],
                bill_tri=[base_c + perp * bw, tip, base_c - perp * bw])

def poly_mask(polys, shape=(H, W)):
    im = Image.new('L', (shape[1], shape[0]), 0)
    dr = ImageDraw.Draw(im)
    for poly in polys:
        dr.polygon([tuple(p) for p in poly], fill=1)
    return np.array(im) > 0

TORSO_M = poly_mask([R25.catmull_rom(R25.TORSO_LOOP, n_per=3, closed=True)])
def legs_mask():
    im = Image.new('L', (W, H), 0)
    dr = ImageDraw.Draw(im)
    for hip, knee, foot in R25.LEGS:
        for a_, b_, w0, w1 in ((hip, knee, 16, 11), (knee, foot, 7, 5)):
            a2, b2 = np.array(a_, float), np.array(b_, float)
            dv = b2 - a2; dv = dv / max(np.hypot(*dv), 1e-9)
            pp = np.array([-dv[1], dv[0]])
            dr.polygon([tuple(a2 + pp * w0 / 2), tuple(b2 + pp * w1 / 2),
                        tuple(b2 - pp * w1 / 2), tuple(a2 - pp * w0 / 2)], fill=1)
        for ang, ln in ((8, 26), (38, 20), (-52, 15)):
            aa = math.radians(ang)
            tip = np.array(foot, float) + np.array([math.cos(aa), math.sin(aa) * 0.45]) * ln
            dr.line([tuple(foot), tuple(tip)], fill=1, width=3)
    return np.array(im) > 0
LEGS_M = legs_mask()
B_TORSO = float((STRIKE.mean(axis=2)[TORSO_M] < 70).mean())
B_LEGS = float((STRIKE.mean(axis=2)[LEGS_M] < 70).mean())

def region_masks(g):
    tube = R25.tube_poly(g['dense'], g['widths'])
    neck_m = poly_mask([tube]) & ~TORSO_M
    fan_c = g['skull']
    rel = np.stack(np.meshgrid(np.arange(W), np.arange(H)), axis=2).astype(float)
    rel = rel - fan_c
    proj = rel @ g['dvec']; perp_d = rel @ g['perp']
    fan = (proj < 0) & (proj > -0.30 * T) & (np.abs(perp_d) < 0.11 * T)
    head_m = poly_mask([g['ell'], g['plume_tri']]) | fan
    head_m &= ~TORSO_M
    neck_m &= ~head_m
    bill_m = poly_mask([g['bill_tri']])
    return neck_m, head_m, bill_m

# ---------------------------------------------------------------- fill
def neck_warp(dnr, g, neck_m):
    """Tube-to-tube donor neck sampling. Returns (rgb, coverage) where
    coverage = fraction of neck pixels whose donor sample lands inside
    the donor neck+head channels."""
    ys, xs = np.nonzero(neck_m)
    P = np.stack([xs, ys], axis=1).astype(float)
    tree = cKDTree(g['dense'])
    _, idx = tree.query(P)
    cen = g['dense'][idx]
    u = g['u'][idx]
    off = P - cen
    gd = np.gradient(g['dense'], axis=0)
    gn = np.hypot(gd[:, 0], gd[:, 1]); gn[gn == 0] = 1
    nrm = np.stack([-gd[:, 1] / gn, gd[:, 0] / gn], axis=1)[idx]
    v = (off * nrm).sum(axis=1) / np.maximum(g['widths'][idx] / 2.0, 1e-6)
    # donor point at same (u, v)
    du = dnr['spine_u']
    dc = np.stack([np.interp(u, du, dnr['spine_dense'][:, 0]),
                   np.interp(u, du, dnr['spine_dense'][:, 1])], axis=1)
    dhw = np.interp(u, du, dnr['spine_hw'])
    dn = np.stack([np.interp(u, du, dnr['spine_nrm'][:, 0]),
                   np.interp(u, du, dnr['spine_nrm'][:, 1])], axis=1)
    src = dc + dn * (v * dhw)[:, None]
    rgb = np.stack([ndimage.map_coordinates(dnr['img'][:, :, c],
                                            [src[:, 1], src[:, 0]],
                                            order=1, mode='nearest')
                    for c in range(3)], axis=1)
    sx = np.clip(src[:, 0].astype(int), 0, W - 1)
    sy = np.clip(src[:, 1].astype(int), 0, H - 1)
    cov = float(((dnr['neck_chan'] | dnr['head_chan'])[sy, sx]).mean())
    return rgb, cov, (ys, xs)

def head_warp(dnr, g):
    hc = np.array(dnr['kp']['head_c'], float)
    tipd = np.array(dnr['kp']['bill_tip'], float)
    axd = tipd - hc; Ld = np.hypot(*axd)
    axt = g['tip'] - g['skull']; Lt = np.hypot(*axt)
    s = Lt / Ld
    th = math.degrees(math.atan2(axt[1], axt[0]) - math.atan2(axd[1], axd[0]))
    R = np.array([[math.cos(math.radians(th)), -math.sin(math.radians(th))],
                  [math.sin(math.radians(th)), math.cos(math.radians(th))]])
    d = g['skull'] - s * (R @ hc)
    return S1.warp_img(dnr['img'], (s, th, d[0], d[1]))

def draw_eye_at(img, xy):
    ys, xs = np.mgrid[0:H, 0:W]
    d = np.hypot(xs - xy[0], ys - xy[1])
    out = img.copy()
    out[d <= 5.0] = IRIS_COL
    out[d <= 2.4] = np.array([18., 15., 12.])
    return out

def eye_pixel_check(img, xy):
    """Verify the drawn eye is actually in the pixels at the anchor."""
    x, y = int(round(xy[0])), int(round(xy[1]))
    c = img[y, x]
    pupil_ok = bool(c.mean() < 45)
    ring = []
    for dx, dy in ((4, 0), (-4, 0), (0, 4), (0, -4), (3, 3), (-3, -3)):
        xx, yy = x + dx, y + dy
        if 0 <= xx < W and 0 <= yy < H:
            ring.append(img[yy, xx])
    ring = np.array(ring)
    amber = ((ring[:, 0] > 90) & (ring[:, 0] < 230) & (ring[:, 2] < 115)
             & ((ring[:, 0] - ring[:, 2]) > 60) & (ring[:, 0] > ring[:, 1]))
    return dict(anchor=[round(float(xy[0]), 1), round(float(xy[1]), 1)],
                centre_rgb=[round(float(v), 1) for v in c],
                pupil_dark=pupil_ok,
                ring_amber=int(amber.sum()), ring_n=int(len(ring)))

def build_frame(g, neck_pid, head_pid):
    neck_m, head_m, bill_m = region_masks(g)
    dnr_n = donor(neck_pid)
    dnr_h = donor(head_pid)
    img = np.zeros((H, W, 3), np.float32)
    img[:] = PAPER
    img[540:600] = STRIKE[540:600]           # waterline band, approved still
    img[TORSO_M] = STRIKE[TORSO_M]           # body: approved still, identity
    img[LEGS_M] = STRIKE[LEGS_M]
    # neck: tube-to-tube donor warp
    rgb, cov_n, (ys, xs) = neck_warp(dnr_n, g, neck_m)
    img[ys, xs] = rgb
    # head: head-frame similarity warp, feathered into the head region
    hw = head_warp(dnr_h, g)
    paste = head_m & ~ndimage.binary_dilation(bill_m, iterations=1)
    dist = ndimage.distance_transform_edt(paste)
    alpha = np.clip(dist / 3.0, 0, 1)[:, :, None]
    img = img * (1 - alpha) + hw * alpha
    cov_h = float((content_mask(hw)[paste]).mean()) if paste.any() else 0.0
    # structural ink: neck + head remapped to rescaled donor targets
    k_n = TARGET_BLACK / max(dnr_n['total_black'], 1e-6)
    k_h = TARGET_BLACK / max(dnr_h['total_black'], 1e-6)
    img = ink_remap(img, neck_m, float(np.clip(dnr_n['neck_black'] * k_n, 0.05, 0.60)))
    img = ink_remap(img, head_m, float(np.clip(dnr_h['head_black'] * k_h, 0.05, 0.60)))
    # crest reinforcement: zone behind the head (spike 1 recipe, v2.5 frame)
    ys2, xs2 = np.mgrid[0:H, 0:W]
    rel = np.stack([xs2 - g['skull'][0], ys2 - g['skull'][1]], axis=2)
    proj = rel @ g['dvec']
    crest_zone = (np.hypot(rel[:, :, 0], rel[:, :, 1]) < 250) & (proj < 25) \
        & ~TORSO_M & ~LEGS_M
    img = S1.reinforce_strands(img, crest_zone)
    # breast plume reinforcement: strands hanging from the neckbase
    nb = g['neckbase'] if g['neckbase'] is not None else g['pts'][0]
    plume_zone = (xs2 > nb[0] - 0.15 * T) & (xs2 < nb[0] + 0.03 * T) \
        & (ys2 > nb[1] - 10) & (ys2 < nb[1] + 0.38 * T) & TORSO_M
    img = S1.reinforce_strands(img, plume_zone, core_lum=115, dark_mul=0.55)
    # bill drawn explicitly from mechanism geometry
    kp_syn = dict(bill_poly=[[0, 0]] * 9 + [list(g['bill_tri'][0]),
                                            list(g['bill_tri'][1]),
                                            list(g['bill_tri'][2])],
                  head_c=list(g['skull']), bill_tip=list(g['tip']))
    img, bill_drawn = S1.draw_bill(img, kp_syn, BILL_PROF)
    # eye at the mechanism anchor, then pixel-verify
    img = draw_eye_at(img, g['eye'])
    chk = eye_pixel_check(img, g['eye'])
    # global trim to the gate band (bill + eye protected), <= 3 passes
    prot = bill_drawn.copy()
    prot |= np.hypot(xs2 - g['eye'][0], ys2 - g['eye'][1]) <= 7
    passes = 0
    for _ in range(3):
        cm = content_mask(img)
        b = color_fracs(img, cm)['black']
        if BAND[0] <= b <= BAND[1]:
            break
        img = ink_remap(img, cm & ~prot, TARGET_BLACK)
        passes += 1
    info = dict(neck_donor=neck_pid, head_donor=head_pid,
                neck_cov=round(cov_n, 3), head_cov=round(cov_h, 3),
                neck_target=round(float(np.clip(dnr_n['neck_black'] * k_n, 0.05, 0.60)), 4),
                head_target=round(float(np.clip(dnr_h['head_black'] * k_h, 0.05, 0.60)), 4),
                trim_passes=passes, eye_check=chk,
                black=round(color_fracs(img, content_mask(img))['black'], 4))
    return img, info

# ---------------------------------------------------------------- timeline
def smooth(t):
    return t * t * (3 - 2 * t)

def timeline():
    F = []  # (theta_grid, pitch, slim, neck_pid, head_pid, phase)
    A, C, P = 'alert', 'deep_coil', 'strike_peak'
    def add(terms, slim, n_pid, h_pid, phase):
        th, pitch = blend_profile(terms)
        F.append((th, pitch, slim, n_pid, h_pid, phase))
    for _ in range(48):
        add([(A, 1.0)], 0.0, 'idle_f0011', 'idle_f0011', 'alert_hold')
    for i in range(28):
        t = smooth((i + 1) / 28)
        idx = 15 + int(round(t * 10))
        pid = f'strike_f{idx:04d}'
        add([(A, 1 - t), (C, t)], 0.0, pid, pid, 'coil_in')
    for _ in range(10):
        add([(C, 1.0)], 0.0, 'strike_f0025', 'strike_f0025', 'coil_hold')
    dip_th = PROF[A][0] + 1.12 * (PROF[C][0] - PROF[A][0])
    dip_pitch = PROF[A][1] + 1.12 * (PROF[C][1] - PROF[A][1])
    for _ in range(2):
        F.append((dip_th, dip_pitch, 0.0, 'strike_f0025', 'strike_f0025', 'dip'))
    # release: 5 frames, quarter-bins cum [0, .03, .15, .75, 1] of dip->peak
    q = [(0.0, 0.0), (0.25, 0.03), (0.5, 0.15), (0.75, 0.75), (1.0, 1.0)]
    rel_pids = ['strike_f0026', 'strike_f0027', 'strike_f0027',
                'strike_f0028', 'strike_f0029']
    for i in range(5):
        tt = (i + 0.5) / 5
        u = float(np.interp(tt, [a for a, _ in q], [b for _, b in q]))
        th = (1 - u) * dip_th + u * PROF[P][0]
        pitch = (1 - u) * dip_pitch + u * PROF[P][1]
        F.append((th, pitch, u, rel_pids[i], rel_pids[i], 'release'))
    for _ in range(6):
        add([(P, 1.0)], 1.0, 'strike_f0027', 'strike_f0027', 'peak_hold')
    for i in range(20):
        t = smooth((i + 1) / 20)
        if i < 12:
            idx = 30 + int(round((i / 11) * 8))
            pid = f'strike_f{idx:04d}'
        else:
            pid = 'idle_f0011'
        th, pitch = blend_profile([(P, 1 - t), (A, t)])
        F.append((th, pitch, 1 - t, pid, pid, 'withdrawal'))
    for _ in range(24):
        add([(A, 1.0)], 0.0, 'idle_f0011', 'idle_f0011', 'settle')
    return F

def render_sequence():
    frames, infos = [], []
    for i, (th, pitch, slim, n_pid, h_pid, phase) in enumerate(timeline()):
        g = frame_geometry(th, pitch, slim)
        img, info = build_frame(g, n_pid, h_pid)
        info['frame'] = i; info['phase'] = phase
        frames.append(np.clip(img, 0, 255).astype(np.uint8))
        infos.append(info)
    return frames, infos

def main():
    os.makedirs(f'{OUT}/frames', exist_ok=True)
    os.makedirs(f'{OUT}/work', exist_ok=True)
    frames, infos = render_sequence()
    hashes = []
    for i, f in enumerate(frames):
        Image.fromarray(f).save(f'{OUT}/frames/f{i:04d}.png')
        hashes.append(hashlib.md5(f.tobytes()).hexdigest())
    # determinism: full second render, byte-compare per frame
    frames2, _ = render_sequence()
    det = all(hashlib.md5(f.tobytes()).hexdigest() == h
              for f, h in zip(frames2, hashes))
    blacks = [inf['black'] for inf in infos]
    json.dump(dict(infos=infos, determinism=det,
                   black_min=min(blacks), black_max=max(blacks),
                   iris_col=[round(float(v), 1) for v in IRIS_COL],
                   iris_px=IRIS_PX, n_frames=len(frames)),
              open(f'{OUT}/work/render_log.json', 'w'), indent=1)
    print(f'rendered {len(frames)} frames; determinism={det}; '
          f'black range {min(blacks):.4f}..{max(blacks):.4f}')

if __name__ == '__main__':
    main()
