"""Before/after measurement for the Route-2 fix build. Same code path for
proof and fix renders; all regions come from the kept TARGET mask stacks
(art2/targets/mask_<pose>.npz) so regions are identical across versions.

Metrics:
 texture_energy  mean |lum - blur5(lum)| inside the torso+wing region of
                 the raw 512 crop (render alpha proxied by darkness);
                 corpus reference = same statistic per training sample.
 checker_index   (-1)^(i+j)-weighted share of the high-frequency residual
                 in the body region: ~1 for pure checkerboard, ~0 natural.
 head_occupancy  fraction of target head-channel pixels (crop coords)
                 where the render is dark (lum < 0.85) = head is drawn.
 leg_width_px    median dark-run width across scanlines through the shin
                 segment of each leg, at master scale; also target-mask
                 leg width for the geometric reference.
 marks           mean RGB in face / thigh / torso regions (identity drift
                 spot-check across poses).
"""
import argparse, json, os, sys
import numpy as np
from PIL import Image

def blur5(a):
    k = np.array([1., 4., 6., 4., 1.]); k /= k.sum()
    p = np.pad(a, 2, mode='edge')
    tmp = np.apply_along_axis(lambda r: np.convolve(r, k, mode='same'), 1, p)
    out = np.apply_along_axis(lambda r: np.convolve(r, k, mode='same'), 0, tmp)
    return out[2:-2, 2:-2]

def crop_of(arr_master, crop_master, S=512):
    x0, y0, side = [int(round(v)) for v in crop_master]
    h, w = arr_master.shape[:2]
    sx0, sy0 = max(0, x0), max(0, y0)
    sx1, sy1 = min(w, x0 + side), min(h, y0 + side)
    sub = arr_master[sy0:sy1, sx0:sx1]
    im = Image.fromarray((np.clip(sub, 0, 1) * 255).astype(np.uint8))
    full = Image.new('L', (S, S), 0)
    r = im.resize((max(1, round((sx1 - sx0) / side * S)),
                   max(1, round((sy1 - sy0) / side * S))), Image.BILINEAR)
    full.paste(r, (round((sx0 - x0) / side * S), round((sy0 - y0) / side * S)))
    return np.asarray(full, np.float32) / 255.0

def body_texture(rgb_crop, body_mask):
    lum = rgb_crop.mean(axis=2)
    hf = np.abs(lum - blur5(lum))
    reg = body_mask > 0.5
    if reg.sum() < 100:
        return None, None
    yy, xx = np.mgrid[0:512, 0:512]
    parity = ((xx + yy) % 2) * 2 - 1
    signed = (lum - blur5(lum)) * parity
    return float(hf[reg].mean()), float(signed[reg].mean() / (hf[reg].mean() + 1e-9))

def leg_widths(master_rgb, kp, masks):
    lum = master_rgb.mean(axis=2)
    out = {}
    for leg in ('n', 'f'):
        legmask_master = masks[leg]
        hip = np.array(kp[f'hip_{leg}'], float); knee = np.array(kp[f'knee_{leg}'], float)
        foot = np.array(kp[f'foot_{leg}'], float)
        widths, ref = [], []
        vertical = abs(foot[1] - knee[1]) >= abs(foot[0] - knee[0])
        for t in np.linspace(0.15, 0.85, 8):
            cx, cy = knee + (foot - knee) * t
            # scan perpendicular-ish to the segment: rows for upright legs,
            # columns for near-horizontal (trailing flight) legs
            line = lum[int(round(cy))] if vertical else lum[:, int(round(cx))]
            mline = (legmask_master[int(round(cy))] if vertical
                     else legmask_master[:, int(round(cx))]) > 0.5
            n = len(line)
            if not (0 <= (cy if vertical else cx) < n):
                continue
            dark = line < 0.80
            xs = np.where(mline)[0]
            if len(xs) == 0:
                continue
            xc = int(round(xs.mean()))
            ref.append(float(xs.max() - xs.min() + 1))
            if not dark[xc]:
                # renders sit up to ~30px off the conditioning sticks;
                # take the nearest dark run within +/-40px of the mask line
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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--proof-dir', required=True)
    ap.add_argument('--fix-dir', required=True)
    ap.add_argument('--art2', required=True)
    ap.add_argument('--corpus', nargs='+', required=True)
    a = ap.parse_args()
    pj = json.load(open(os.path.join(a.art2, 'poses_art2.json')))
    # corpus texture reference (per-sample body-region HF energy)
    corp = []
    for d in a.corpus:
        for f in sorted(os.listdir(d)):
            if not f.endswith('.npz'):
                continue
            z = np.load(os.path.join(d, f))
            body = (z['mask'][0] + z['mask'][3]) > 127
            rgb = z['rgb'].astype(np.float32) / 255.0
            te, ci = body_texture(rgb, body.astype(np.float32))
            if te is not None:
                corp.append(te)
    print(f'corpus body texture energy: median {np.median(corp):.4f} '
          f'(n={len(corp)}, p25 {np.percentile(corp,25):.4f}, p75 {np.percentile(corp,75):.4f})')
    res = {}
    for tag, d in (('proof', a.proof_dir), ('fix', a.fix_dir)):
        res[tag] = {}
        for pose in ('rest', 'front', 'swallow', 'flight'):
            z = np.load(os.path.join(a.art2, 'targets', f'mask_{pose}.npz'))
            full = z['mask'].astype(np.float32) / 255.0
            pd = pj['poses'][pose]
            cm = pd['crop_master']
            raw = Image.open(os.path.join(d, f'raw_{pose}.png')).convert('RGB')
            raw = np.asarray(raw, np.float32) / 255.0
            head_c = crop_of(full[2], cm)
            body_c = np.clip(crop_of(full[0], cm) + crop_of(full[3], cm), 0, 1)
            lum = raw.mean(axis=2)
            occ = float((lum[head_c > 0.5] < 0.85).mean())
            apath = os.path.join(d, f'alpha_{pose}.png')
            aocc = None
            if os.path.exists(apath):
                al = np.asarray(Image.open(apath).convert('L'),
                                np.float32) / 255.0
                aocc = round(float((al[head_c > 0.5] > 0.5).mean()), 3)
            te, ci = body_texture(raw, body_c)
            master = np.asarray(Image.open(os.path.join(d, f'master_{pose}.png'))
                                .convert('RGB'), np.float32) / 255.0
            kp = pd['keypoints_master']
            lw = leg_widths(master, kp, {'n': full[4], 'f': full[5]})
            # identity marks on the master, regions from target masks
            def region_mean(mask2d, val=None):
                m = mask2d > 0.5
                dark = master.mean(axis=2) < 0.9
                mm = m & dark
                return (master[mm].mean(axis=0).round(3).tolist()
                        if mm.sum() > 30 else None)
            marks = {
                'face_rgb': region_mean(full[2]),
                'torso_rgb': region_mean(full[0]),
            }
            res[tag][pose] = {'head_occupancy': round(occ, 3),
                              'head_alpha_occupancy': aocc,
                              'texture_energy': None if te is None else round(te, 4),
                              'checker_index': None if ci is None else round(ci, 3),
                              'leg_widths': {k: [round(v[0], 1), round(v[1], 1)]
                                             for k, v in lw.items()},
                              'marks': marks}
            print(tag, pose, json.dumps(res[tag][pose]))
    json.dump(res, open('measure_fix_out.json', 'w'), indent=1)
    print('wrote measure_fix_out.json')

if __name__ == '__main__':
    main()
