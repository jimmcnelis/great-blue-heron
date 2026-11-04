#!/usr/bin/env python3
"""FILL SPIKE v2 — per-part head warps (Jimmy's go, 2026-11-04 06:57).

ONE change over spike v1, everything else carried over verbatim
(instruments imported from fill-spike-v1/spike_fill.py, unmodified):

  PARTS replace flat regions for the head end of the bird.
  HEAD PART = neck (ch 1) + head (ch 2), treated as one part:
   * Texture: ONE donor for the whole part, warped by a similarity
     fit anchored on the head's OWN rig keypoints (spine[1..3],
     head_c, bill-base midpoint, bill tip — Umeyama) instead of the
     whole-silhouette warp. This replaces spike 1's consensus-centroid
     residual shift for this part: keypoint anchoring IS the alignment.
     The part's footprint extends over the crest zone (off-body,
     behind the head), feathered by distance from the part labels.
   * Ink: the part carries ONE ink target — the gold black fraction
     over the union head+neck region — and the final global trim
     treats the part as protected (like spike 1's bill/eye), so the
     target the part carries is the target it keeps. (Spike 1's
     numbers show why: its global trim re-inked the strike neck
     from its 0.088 target to 0.254 in the final frame.)
   * Crest reinforcement no longer touches the part's own labels
     (spike 1's zone was defined 'off the body channels' but only
     excluded torso/wing/tail; measured cost: the hold's neck-front
     black ran 0.071 vs gold 0.013).
  SADDLE PART = torso (ch 0) + wing (ch 3) for INK only: one union
  ink target and one remap set, so the cross-region saddle is owned
  by one part. Body texture composite stays spike 1 (per-region
  donors, silhouette warps, consensus shifts).
  Legs, tail, plume, overhang: spike 1 verbatim.
  Global trim: iterates (cap 12) solving each pass for the set
  fraction the OVERALL band centre requires given the protected
  pixels — spike 1's trim stopped at its 3-pass cap unconverged
  (0.3605 vs band floor 0.361); this one runs to convergence or
  reports a stall.
Deterministic: fixed rules, no RNG, SVD sign fixed by determinant
correction, exact quantile remaps.
"""
import csv, hashlib, json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

HOME = os.path.expanduser('~')
ART2 = f'{HOME}/workspace/heron/art2'
FS = f'{ART2}/finished-art-stills'
FM3 = f'{FS}/finish-model-v3'
SPIKE = f'{ART2}/fill-spike-v2'
sys.path.insert(0, ART2)
sys.path.insert(0, f'{HOME}/workspace/heron/src13')
sys.path.insert(0, FM3)
sys.path.insert(0, f'{ART2}/fill-spike-v1')
import build_corpus as bc
import roster_render_v24 as RR
import spike_fill as S1   # spike 1 instruments, verbatim

W, H = 1024, 600
ORDER = S1.ORDER
NAMES = S1.NAMES
HEAD_CH = (1, 2)          # neck, head
SADDLE_CH = (0, 3)        # torso, wing (ink union only)
BODY_CH = [0, 3, 6, 5, 4, 7]   # spike-1 relative order, part channels removed

load = S1.load
content_mask = S1.content_mask
color_fracs = S1.color_fracs
iou = S1.iou

# ---------- head anchors + Umeyama similarity ----------
def head_anchors(kp):
    bp = [np.array(p, float) for p in kp['bill_poly']]
    base_mid = (bp[9] + bp[11]) / 2.0
    pts = [np.array(kp['spine'][1], float), np.array(kp['spine'][2], float),
           np.array(kp['spine'][3], float), np.array(kp['head_c'], float),
           base_mid, np.array(kp['bill_tip'], float)]
    return np.stack(pts)

def umeyama(donor_pts, target_pts):
    """Similarity (s, th_deg, dx, dy) in bc's forward convention
    p' = s*R(th)*p + (dx,dy), p in (x,y); least squares donor->target."""
    d = donor_pts - donor_pts.mean(axis=0)
    t = target_pts - target_pts.mean(axis=0)
    Hm = (t.T @ d) / len(donor_pts)
    U, sv, Vt = np.linalg.svd(Hm)
    det = np.linalg.det(Vt.T @ U.T)
    Dg = np.diag([1.0, np.sign(det)])
    R = Vt.T @ Dg @ U.T
    var_d = (d ** 2).sum() / len(donor_pts)
    s = float((sv * np.array([1.0, np.sign(det)])).sum() / var_d)
    tr = target_pts.mean(axis=0) - s * R @ donor_pts.mean(axis=0)
    th = float(np.degrees(np.arctan2(R[1, 0], R[0, 0])))
    pred = (s * (R @ donor_pts.T)).T + tr
    rms = float(np.sqrt(((pred - target_pts) ** 2).sum(axis=1).mean()))
    return (s, th, float(tr[0]), float(tr[1])), rms

# ---------- frame builder (spike 2) ----------
def build2(target_key, pose, donors, tgt, band, band_centre, kp_t, prof):
    """donors: list of (pid, img, stack, pose). tgt: dict with keys
    'part', 'saddle', per-channel ints for 4,5,6,7, 'overhang'."""
    tstack = bc.stack_for(pose)
    tlab = S1.labelmap(tstack)
    tsil = np.any(tstack > 0, axis=0)
    part_lab = (tlab == HEAD_CH[0]) | (tlab == HEAD_CH[1])
    anchors_t = head_anchors(kp_t)
    # --- silhouette warps (body) + head warps (part), per donor ---
    D = []
    for pid, img, stack, dpose in donors:
        dsil = np.any(stack > 0, axis=0)
        if np.array_equal(dsil, tsil):
            prm = (1.0, 0.0, 0.0, 0.0); wimg = img; wstack = stack
            sil_iou = 1.0
        else:
            _, s, th, dx, dy = bc.fit(dsil, tsil)
            prm = (s, th, dx, dy)
            wimg = S1.warp_img(img, prm)
            wstack = np.stack([S1.warp_mask(stack[c] > 0, prm) for c in range(8)])
            sil_iou = iou(np.any(wstack > 0, axis=0), tsil)
        kp_d = RR.kp_master(dpose)
        hprm, hrms = umeyama(head_anchors(kp_d), anchors_t)
        if np.allclose(hprm, (1.0, 0.0, 0.0, 0.0), atol=1e-9):
            himg = img
        else:
            himg = S1.warp_img(img, hprm)
        D.append(dict(pid=pid, img=wimg, stack=wstack, sil_iou=sil_iou,
                      himg=himg, hprm=hprm, hrms=hrms))
    # base donor: spike-1 rule verbatim
    if target_key == 'idle':
        vals = [color_fracs(d['img'], content_mask(d['img']))['black'] for d in D]
        med = float(np.median(vals))
        base = min(D, key=lambda d: (abs(color_fracs(d['img'], content_mask(d['img']))['black'] - med), d['pid']))
    else:
        base = max(D, key=lambda d: (d['sil_iou'], d['pid']))
    img = base['img'].copy()
    log = dict(base_donor=base['pid'], regions={}, part={})
    # --- body per-region composite: spike 1 verbatim ---
    for ch in BODY_CH:
        tm = tlab == ch
        if tm.sum() == 0:
            continue
        cents = [S1.centroid(d['stack'][ch] > 0) for d in D]
        cents = [c for c in cents if c is not None]
        cons = np.median(np.stack(cents), axis=0) if cents else None
        tgt_ch = tgt['saddle'] if ch in SADDLE_CH else tgt[ch]
        def regblack(d, tm=tm):
            return float((d['img'].mean(axis=2)[tm] < 70).mean())
        pick = min(D, key=lambda d: (abs(regblack(d) - tgt_ch), d['pid']))
        src = pick['img']
        cen = S1.centroid(pick['stack'][ch] > 0)
        if cons is not None and cen is not None:
            shift = np.round(cons - cen).astype(int)
            shift = np.clip(shift, -10, 10)
            if shift.any():
                src = ndimage.shift(src, (shift[1], shift[0], 0), order=1,
                                    mode='nearest')
        dist = ndimage.distance_transform_edt(tm)
        alpha = np.clip(dist / 3.0, 0, 1)[:, :, None]
        img = img * (1 - alpha) + src * alpha
        log['regions'][NAMES[ch]] = dict(donor=pick['pid'],
                                         donor_black=round(regblack(pick), 4))
    # --- HEAD PART composite: one donor, head-keypoint warp ---
    def partblack(d):
        return float((d['himg'].mean(axis=2)[part_lab] < 70).mean())
    ppick = min(D, key=lambda d: (abs(partblack(d) - tgt['part']), d['pid']))
    # crest zone: spike-1 definition verbatim
    hc = np.array(kp_t['head_c'], float); tip = np.array(kp_t['bill_tip'], float)
    ax = tip - hc; ax = ax / np.hypot(*ax)
    ys, xs = np.mgrid[0:H, 0:W]
    rel = np.stack([xs - hc[0], ys - hc[1]], axis=2)
    proj = rel @ ax
    crest_zone = (np.hypot(rel[:, :, 0], rel[:, :, 1]) < 250) & (proj < 25) \
        & ~((tstack[0] > 0) | (tstack[3] > 0) | (tstack[6] > 0))
    dist_in = ndimage.distance_transform_edt(part_lab)
    dist_out = ndimage.distance_transform_edt(~part_lab)
    alpha = np.zeros((H, W))
    alpha[part_lab] = np.clip(dist_in[part_lab] / 3.0, 0, 1)
    cz = crest_zone & ~part_lab
    alpha[cz] = np.clip(1.0 - dist_out[cz] / 60.0, 0, 1)
    img = img * (1 - alpha[:, :, None]) + ppick['himg'] * alpha[:, :, None]
    log['part'] = dict(donor=ppick['pid'],
                       donor_part_black=round(partblack(ppick), 4),
                       target=round(tgt['part'], 4),
                       warp=[round(float(v), 4) for v in ppick['hprm']],
                       anchor_rms=round(ppick['hrms'], 2))
    # --- structural ink: part-owned remap sets ---
    img = S1.ink_remap(img, part_lab, tgt['part'])
    saddle_lab = (tlab == SADDLE_CH[0]) | (tlab == SADDLE_CH[1])
    img = S1.ink_remap(img, saddle_lab, tgt['saddle'])
    for ch in (4, 5, 6, 7):
        img = S1.ink_remap(img, tlab == ch, tgt[ch])
    over = (tlab < 0) & content_mask(img)
    img = S1.ink_remap(img, over, tgt['overhang'])
    # --- explicit structures: spike 1 verbatim ---
    img, bill_m = S1.draw_bill(img, kp_t, prof)
    img = S1.draw_eye(img, kp_t, prof)
    # crest reinforcement: spike 1, but the part's own labels are the
    # part's — reinforcement works the off-body zone only
    img = S1.reinforce_strands(img, crest_zone & ~part_lab)
    # plume reinforcement: spike 1 verbatim
    plume = tstack[7] > 0
    zone = plume.copy()
    for k in range(1, 41):
        zone[k:] |= plume[:-k]
    zone = ndimage.binary_dilation(zone, iterations=2)
    img = S1.reinforce_strands(img, zone, core_lum=115, dark_mul=0.55)
    # --- global trim: part + bill/eye protected; iterate to converge ---
    prot = bill_m.copy() | part_lab
    if prof['eye_uv'] is not None:
        perp = np.array([-ax[1], ax[0]])
        c = hc + prof['eye_uv'][0] * ax + prof['eye_uv'][1] * perp
        prot |= np.hypot(xs - c[0], ys - c[1]) <= 7
    trim_log = []
    prev_b = None
    stall = 0
    for it in range(12):
        cm = content_mask(img)
        b = color_fracs(img, cm)['black']
        trim_log.append(round(b, 4))
        if band[0] <= b <= band[1]:
            break
        setm = cm & ~prot
        n_set = int(setm.sum()); n_cm = int(cm.sum())
        black_prot = int((cm & prot & (img.mean(axis=2) < 70)).sum())
        need = (band_centre * n_cm - black_prot) / max(n_set, 1)
        need = float(np.clip(need, 0.0, 0.98))
        img = S1.ink_remap(img, setm, need)
        if prev_b is not None and abs(b - prev_b) < 0.0002:
            stall += 1
            if stall >= 2:
                break
        prev_b = b
    cm = content_mask(img)
    log['trim'] = dict(iters=trim_log,
                       final_black=round(color_fracs(img, cm)['black'], 4),
                       part_black_final=round(float(
                           (img.mean(axis=2)[part_lab] < 70).mean()), 4))
    return img, log

# ---------- diagnostics ----------
def front_back_black(img, gold, tlab, kp):
    sp = np.array(kp['spine'], float)
    d = sp[4] - sp[0]
    perp = np.array([d[1], -d[0]])
    mid = sp[2]
    if np.dot(np.array(kp['bill_tip'], float) - mid, perp) < 0:
        perp = -perp
    ys, xs = np.nonzero(tlab == 1)
    side = (xs - mid[0]) * perp[0] + (ys - mid[1]) * perp[1]
    front = np.zeros((H, W), bool); back = np.zeros((H, W), bool)
    front[ys, xs] = side > 0; back[ys, xs] = side <= 0
    def bf(a, m):
        return round(float((m & (a.mean(axis=2) < 70)).sum() / max(m.sum(), 1)), 4)
    return dict(front=dict(mine=bf(img, front), gold=bf(gold, front)),
                back=dict(mine=bf(img, back), gold=bf(gold, back)))

def part_metrics(img, gold, tlab):
    part = (tlab == 1) | (tlab == 2)
    gm = content_mask(gold); mm = content_mask(img)
    sub_i = iou(mm & part, gm & part)
    mad = float(np.abs(img - gold)[part & (mm | gm)].mean())
    return dict(part_iou_vs_gold=round(sub_i, 4), part_mad=round(mad, 2))

def main():
    os.makedirs(f'{SPIKE}/work', exist_ok=True)
    man = {r['pair_id']: r for r in csv.DictReader(open(f'{FM3}/corpus_manifest.csv'))}
    tracks24 = json.load(open(f'{FS}/rig-v2/band-pass/pose_tracks_v24.json'))
    tracks2 = json.load(open(f'{FS}/rig-v2/work/pose_tracks_v2.json'))
    prof = S1.extract_bill_profile()
    out = {}

    # ---------- GATE A: the standing hold ----------
    idle_pose = tracks24['idle'][0]
    istack = bc.stack_for(idle_pose)
    donorsA = [(pid, load(f'{FM3}/corpus/target/{pid}.png'), istack, idle_pose)
               for pid, r in man.items()
               if r['family'] == 'idle' and pid != 'idle_f0030']
    goldA = load(f'{FM3}/corpus/target/idle_f0030.png')
    labA = S1.labelmap(istack)
    lumA = goldA.mean(axis=2); cmA = content_mask(goldA)
    corr = 0.2593 / 0.2389
    def goldfrac(mask, arr_lum):
        return float((mask & (arr_lum < 70)).sum() / max(mask.sum(), 1))
    tgtA = {'part': goldfrac((labA == 1) | (labA == 2), lumA) * corr,
            'saddle': goldfrac((labA == 0) | (labA == 3), lumA) * corr}
    for ch in (4, 5, 6, 7):
        tgtA[ch] = goldfrac(labA == ch, lumA) * corr
    tgtA['overhang'] = goldfrac((labA < 0) & cmA, lumA) * corr
    kpA = RR.kp_master(idle_pose)
    imgA, logA = build2('idle', idle_pose, donorsA, tgtA,
                        (0.252, 0.272), 0.262, kpA, prof)
    Image.fromarray(np.clip(imgA, 0, 255).astype(np.uint8)).save(f'{SPIKE}/hold_fill.png')
    mA = S1.measure(imgA, f'{FM3}/corpus/target/idle_f0030.png')
    fbA = front_back_black(imgA, goldA, labA, kpA)
    pmA = part_metrics(imgA, goldA, labA)
    S1.sidebyside(imgA, goldA, load(f'{FS}/audubon_rest.png'),
                  f'{SPIKE}/sidebyside_hold.png', None)
    print('GATE A log:', json.dumps(logA))
    print('GATE A measure:', json.dumps(mA))
    print('GATE A neck front/back:', json.dumps(fbA), 'part:', json.dumps(pmA))

    # determinism: rebuild the hold
    imgA2, _ = build2('idle', idle_pose, donorsA, tgtA,
                      (0.252, 0.272), 0.262, kpA, prof)
    h1 = hashlib.md5(np.clip(imgA, 0, 255).astype(np.uint8).tobytes()).hexdigest()
    h2 = hashlib.md5(np.clip(imgA2, 0, 255).astype(np.uint8).tobytes()).hexdigest()
    print('determinism hold:', h1 == h2)

    # ---------- GATE B: full-extension strike f0027 ----------
    poseB = tracks2['strike'][27]
    donorsB = []
    for i in list(range(18, 27)) + list(range(28, 37)):
        pid = f'strike_f{i:04d}'
        donorsB.append((pid, load(f'{FM3}/corpus/target/{pid}.png'),
                        bc.stack_for(tracks2['strike'][i]), tracks2['strike'][i]))
    goldB = load(f'{FM3}/corpus/target/strike_f0027.png')
    stackB = bc.stack_for(poseB)
    labB = S1.labelmap(stackB)
    lumB = goldB.mean(axis=2); cmB = content_mask(goldB)
    tgtB = {'part': goldfrac((labB == 1) | (labB == 2), lumB),
            'saddle': goldfrac((labB == 0) | (labB == 3), lumB)}
    for ch in (4, 5, 6, 7):
        tgtB[ch] = goldfrac(labB == ch, lumB)
    tgtB['overhang'] = goldfrac((labB < 0) & cmB, lumB)
    kpB = RR.kp_master(poseB)
    imgB, logB = build2('strike', poseB, donorsB, tgtB,
                        (0.361, 0.381), 0.371, kpB, prof)
    Image.fromarray(np.clip(imgB, 0, 255).astype(np.uint8)).save(f'{SPIKE}/strike_f0027_fill.png')
    mB = S1.measure(imgB, f'{FM3}/corpus/target/strike_f0027.png')
    pmB = part_metrics(imgB, goldB, labB)
    S1.sidebyside(imgB, goldB, load(f'{FS}/audubon_strike.png'),
                  f'{SPIKE}/sidebyside_strike_f0027.png', None)
    print('GATE B log:', json.dumps(logB))
    print('GATE B measure:', json.dumps(mB))
    print('GATE B part:', json.dumps(pmB))

    json.dump(dict(gateA=mA, gateB=mB, logA=logA, logB=logB,
                   neck_frontback_A=fbA, part_A=pmA, part_B=pmB,
                   targetsA={str(k): round(v, 4) for k, v in tgtA.items()},
                   targetsB={str(k): round(v, 4) for k, v in tgtB.items()},
                   determinism_hold=bool(h1 == h2)),
              open(f'{SPIKE}/work/metrics_spike2.json', 'w'), indent=1)
    print('WROTE metrics_spike2.json')

if __name__ == '__main__':
    main()
