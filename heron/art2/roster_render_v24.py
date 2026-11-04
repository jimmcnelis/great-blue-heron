"""Roster renderer — pose tracks -> Route-2 Fix-1 decoder -> frames + QA.

Runs on the Spark (GPU). For each frame pose: keypoints via the KEPT
prep_poses.keypoints_for construction (copied verbatim below), mask
stack via maskrender at master scale, decoder input crop built with
the exact block from train_decoder_fix.infer, batched UNet forward
with ckpt/last.pt (the shipped step-6000 Fix-1 checkpoint), composited
on white at 1024x600.

QA per frame (measure_fix.py code, same as the Fix-1 sheet):
  texture_energy / checker_index from the raw 512 crop + body mask
  head_alpha_occupancy: decoder alpha > 0.5 inside the frame's own
    head channel (crop coords)
  leg widths at master scale via measure_fix.leg_widths

Usage:
  roster_render.py --tracks pose_tracks.json --ckpt last.pt \
      --outdir OUT [--charts strike,swallow] [--batch 16]
  roster_render.py --smoke --art2 ART2DIR --ckpt last.pt --outdir OUT
      (renders the 4 kept target poses through this batch path so the
      caller can pixel-diff against route2/out_last masters)
"""
import argparse, copy, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'src13'))
import rig13_r4_v24 as R
import maskrender_v2 as M
import measure_fix as MF

# ---- keypoints_for / pose_vector: verbatim from prep_poses.py ----------
def rot(p, deg):
    th = np.deg2rad(deg)
    c, s = np.cos(th), np.sin(th)
    p = np.asarray(p, float)
    return np.array([c * p[0] - s * p[1], s * p[0] + c * p[1]])

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
        skull = SKULL_PROFILE
        bill = [(2.5, -1.55), (R.HINGE[0] + R.BILL_LEN, 0.5), (3.45, 1.55)]
        bill_poly = [W(p) for p in skull] + [W(p) for p in bill]

    kp = {}
    kp['torso_poly'] = [xf(p) for p in R.TORSO]
    kp['spine'] = spine5
    kp['head_c'] = H
    kp['bill_tip'] = R.bill_tip(pose)
    kp['bill_poly'] = bill_poly
    kp['tail_poly'] = [xf(R.TORSO[0]), xf((-16.5, -4.6)), xf((-17.0, 4.4))]
    if int(round(pose['yaw'])) == 90:
        offs = [(-3.6, -2.0), (3.6, -2.0), (3.2, 7.0), (1.2, 11.5),
                (-1.2, 11.5), (-3.2, 7.0)]
    elif pose['wing_mode'] == 'flight':
        offs = [(-2.0, -2.5), (3.5, -2.0), (4.5, 3.0), (1.0, 6.5),
                (-2.5, 3.5)]
    else:
        # rig-v2: plume skirt offsets x1.80 (approved plume drop ~0.33 H
        # vs the old rig's ~0.18 H); anchors unchanged (breast point).
        # rig-v2.2 (body-placement round): the whole offset set may be
        # TRANSLATED by (PLUME_DX, PLUME_DY) -- placement of the hang,
        # internal geometry (shape/size) untouched.
        # rig-v2.3 (geometry round): PLUME_OFFS_BASE is the offset set
        # itself, module-level so the geometry search can reshape the
        # fan; PLUME_DX/PLUME_DY still translate it.
        offs = [(x + PLUME_DX, y + PLUME_DY) for (x, y) in PLUME_OFFS_BASE]
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

def pose_vector(pose):
    return [float(pose['coil']), float(pose['neck_w']),
            float(pose['head_pitch']) / 60.0, float(pose['body_tilt']) / 40.0,
            float(pose['yaw']) / 180.0, float(pose['bulge_pos']),
            float(pose['bulge_amp']), float(pose['flap']) / 60.0,
            float(pose['flap_tip']) / 30.0,
            1.0 if pose['wing_mode'] == 'flight' else 0.0,
            float(pose['gape']), float(pose['plume_sway']) / 3.0]

# rig-v2.3 (geometry round): profile skull outline as a module
# constant (values = the v2.2 outline at zero delta) so the head-bulk
# geometry search can tune it; the anchor H and bill are untouched.
SKULL_PROFILE = [
                 (-4, -1.1), (-3.5, -1.15), (-0.6, -2.7), (2.1, -2.3),
                 (3.6, -0.9), (3.9, 0.5), (2.1, 2.35), (-0.8, 2.9),
                 (-3.1, 1.5)]
# rig-v2.3: plume fan offsets (breast-relative, design units) at zero
# delta = the rig-v2 set; reshaping them is this round's plume lever.
PLUME_OFFS_BASE = [
                    (-3.15, -4.32), (2.52, -5.76), (6.3, -0.72), (5.796, 12.04),
                    (3.276, 17.96), (0.252, 22.12), (-2.772, 24.92), (-4.032, 2.88)]

PLUME_DX, PLUME_DY = 6, -18.5   # rig-v2.2 plume placement (design units),
# baked from the body-placement search: the solid skirt belongs on the
# DENSE fan under the breast (+6 fwd, -17 up), NOT on the wispy strand
# envelope (translating toward the envelope centroid cost IoU at every
# grid point -- the strands' paper gaps tax a solid polygon).

U, XOFF = R.U, R.XOFF

def mxy(p):
    p = np.asarray(p, float)
    return [float(XOFF + p[0] * U), float(p[1] * U)]

def kp_master(pose):
    kp_d = keypoints_for(pose)
    return {k: ([mxy(p) for p in v] if k in ('torso_poly', 'spine', 'bill_poly',
                                             'wing_poly', 'tail_poly', 'plume_poly')
                else mxy(v)) for k, v in kp_d.items()}

# ---- decoder plumbing (crop block verbatim from train_decoder_fix) -----
def build_input(full_mask, pose_vec, crop_master):
    import torch
    import torch.nn.functional as F
    x0, y0, side = crop_master
    S = 512
    nch = full_mask.shape[0]
    crop = np.zeros((nch, S, S), np.float32)
    fx0, fy0 = int(round(x0)), int(round(y0))
    fs = int(round(side))
    sx0, sy0 = max(0, fx0), max(0, fy0)
    sx1, sy1 = min(1024, fx0 + fs), min(600, fy0 + fs)
    if sx1 > sx0 and sy1 > sy0:
        sub = full_mask[:, sy0:sy1, sx0:sx1]
        sub_t = torch.from_numpy(sub)[None]
        sub_r = F.interpolate(sub_t, size=(S, S), mode='bilinear',
                              align_corners=False)[0].numpy()
        dx = int(round((sx0 - fx0) / fs * S)); dy = int(round((sy0 - fy0) / fs * S))
        cw = int(round((sx1 - sx0) / fs * S)); ch = int(round((sy1 - sy0) / fs * S))
        crop[:, dy:dy + ch, dx:dx + cw] = sub_r[:, :ch, :cw]
    x = torch.from_numpy(crop)[None]
    pv = torch.from_numpy(np.asarray(pose_vec, np.float32))[None, :, None, None].expand(1, 12, S, S)
    return torch.cat([x, pv], 1), (fx0, fy0, fs)

def composite(out, box):
    import torch
    from PIL import Image
    rgb = out[:3].clamp(0, 1).numpy().transpose(1, 2, 0)
    alpha = torch.sigmoid(out[3]).numpy()
    fx0, fy0, fs = box
    crop_img = Image.fromarray((rgb * 255).astype(np.uint8))
    big = crop_img.resize((fs, fs), Image.LANCZOS)
    biga = Image.fromarray((alpha * 255).astype(np.uint8)).resize((fs, fs),
                                                                  Image.LANCZOS)
    master = Image.new('RGB', (1024, 600), 'white')
    amaster = Image.new('L', (1024, 600), 0)
    master.paste(big, (fx0, fy0))
    amaster.paste(biga, (fx0, fy0))
    white = Image.new('RGB', (1024, 600), 'white')
    return Image.composite(master, white, amaster), rgb, alpha

def leg_widths_safe(master_rgb, kp, masks):
    """measure_fix.leg_widths with the scanline fetched only after a
    correct bounds check (MF's own guard uses the line length, which
    lets an out-of-frame knee/foot row crash the run — hit on oneleg's
    tucked frames). Identical math for every in-frame scanline."""
    lum = master_rgb.mean(axis=2)
    out = {}
    for leg in ('n', 'f'):
        legmask_master = masks[leg]
        hip = np.array(kp[f'hip_{leg}'], float)
        knee = np.array(kp[f'knee_{leg}'], float)
        foot = np.array(kp[f'foot_{leg}'], float)
        widths, ref = [], []
        vertical = abs(foot[1] - knee[1]) >= abs(foot[0] - knee[0])
        for t in np.linspace(0.15, 0.85, 8):
            cx, cy = knee + (foot - knee) * t
            if vertical:
                if not (0 <= int(round(cy)) < lum.shape[0]):
                    continue
                line = lum[int(round(cy))]
                mline = legmask_master[int(round(cy))] > 0.5
            else:
                if not (0 <= int(round(cx)) < lum.shape[1]):
                    continue
                line = lum[:, int(round(cx))]
                mline = legmask_master[:, int(round(cx))] > 0.5
            n = len(line)
            dark = line < 0.80
            xs = np.where(mline)[0]
            if len(xs) == 0:
                continue
            xc = int(round(xs.mean()))
            ref.append(float(xs.max() - xs.min() + 1))
            if not dark[xc]:
                cand = [xc + d for d in range(-40, 41)
                        if 0 <= xc + d < n and dark[xc + d]]
                if not cand:
                    widths.append(0.0); continue
                xc = min(cand, key=lambda c: abs(c - xc))
            l = xc
            while l > 0 and dark[l - 1]:
                l -= 1
            r = xc
            while r < n - 1 and dark[r + 1]:
                r += 1
            widths.append(float(r - l + 1))
        if widths:
            out[leg] = (float(np.median(widths)), float(np.median(ref)))
    return out

def frame_qa(rgb_crop, alpha_crop, full_mask, crop_master, master_img, kp_m):
    """QA numbers for one frame, measure_fix code paths."""
    head_c = MF.crop_of(full_mask[2], list(crop_master))
    body_c = np.clip(MF.crop_of(full_mask[0], list(crop_master))
                     + MF.crop_of(full_mask[3], list(crop_master)), 0, 1)
    te, ci = MF.body_texture(rgb_crop, body_c)
    hm = head_c > 0.5
    occ = float((alpha_crop[hm] > 0.5).mean()) if hm.sum() > 20 else None
    master_f = np.asarray(master_img, np.float32) / 255.0
    lw = leg_widths_safe(master_f, kp_m, {'n': full_mask[4], 'f': full_mask[5]})
    return {'texture': None if te is None else round(float(te), 4),
            'checker': None if ci is None else round(float(ci), 4),
            'head_alpha_occ': None if occ is None else round(occ, 4),
            'leg_n': None if 'n' not in lw else round(lw['n'][0], 1),
            'leg_f': None if 'f' not in lw else round(lw['f'][0], 1)}

def load_model(ckpt):
    import torch
    sys.path.insert(0, HERE)
    from train_decoder_fix import UNet
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = UNet(in_ch=20).to(dev)
    model.load_state_dict(torch.load(ckpt, map_location=dev))
    model.eval()
    return model, dev

def render_frames(model, dev, items, outdir, batch=16):
    """items: list of (tag, full_mask, pose_vec, crop_master, kp_m).
    Saves <tag>.png per frame; returns {tag: qa}."""
    import torch
    from PIL import Image
    os.makedirs(outdir, exist_ok=True)
    qa = {}
    with torch.no_grad():
        for s in range(0, len(items), batch):
            chunk = items[s:s + batch]
            xs, boxes = [], []
            for tag, full, pv, cm, kpm in chunk:
                x, box = build_input(full, pv, cm)
                xs.append(x); boxes.append(box)
            xb = torch.cat(xs, 0).to(dev)
            with torch.autocast('cuda', dtype=torch.bfloat16,
                                enabled=(dev == 'cuda')):
                out = model(xb).float()
            for j, (tag, full, pv, cm, kpm) in enumerate(chunk):
                master, rgb, alpha = composite(out[j].cpu(), boxes[j])
                master.save(os.path.join(outdir, f'{tag}.png'))
                qa[tag] = frame_qa(rgb, alpha, full, cm, master, kpm)
            print(f'  {min(s + batch, len(items))}/{len(items)}', flush=True)
    return qa

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tracks')
    ap.add_argument('--ckpt', required=True)
    ap.add_argument('--outdir', required=True)
    ap.add_argument('--charts', default='')
    ap.add_argument('--batch', type=int, default=16)
    ap.add_argument('--smoke', action='store_true')
    ap.add_argument('--art2', default=HERE)
    a = ap.parse_args()
    model, dev = load_model(a.ckpt)
    print('device', dev)
    if a.smoke:
        pj = json.load(open(os.path.join(a.art2, 'poses_art2.json')))
        items = []
        for name, pd in pj['poses'].items():
            z = np.load(os.path.join(a.art2, 'targets', f'mask_{name}.npz'))
            items.append((f'master_{name}', z['mask'].astype(np.float32) / 255.0,
                          z['pose'], pd['crop_master'],
                          pd['keypoints_master']))
        qa = render_frames(model, dev, items, a.outdir, a.batch)
        print(json.dumps(qa, indent=1))
        return
    tracks = json.load(open(a.tracks))
    want = [c.strip() for c in a.charts.split(',') if c.strip()] \
        or list(tracks.keys())
    all_qa = {}
    for chart in want:
        poses = tracks[chart]
        items = []
        for i, pose in enumerate(poses):
            pose = copy.deepcopy(pose)
            for leg in ('leg_near', 'leg_far'):
                pose[leg] = dict(pose[leg])
            kpm = kp_master(pose)
            scalars = dict(neck_w=float(pose['neck_w']),
                           bulge_pos=float(pose['bulge_pos']),
                           bulge_amp=float(pose['bulge_amp']),
                           px_per_unit=U)
            stack = M.build_mask_stack(kpm, scalars, (1024, 600))
            full = stack.astype(np.float32) / 255.0
            crop = M.crop_spec(M.all_points(kpm))
            items.append((f'f{i:04d}', full, pose_vector(pose), crop, kpm))
        outdir = os.path.join(a.outdir, chart)
        print(f'{chart}: {len(items)} frames -> {outdir}', flush=True)
        qa = render_frames(model, dev, items, outdir, a.batch)
        all_qa[chart] = qa
        with open(os.path.join(a.outdir, f'qa_{chart}.json'), 'w') as f:
            json.dump(qa, f)
    print('DONE')

if __name__ == '__main__':
    main()
