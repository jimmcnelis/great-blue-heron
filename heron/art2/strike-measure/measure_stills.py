#!/usr/bin/env python3
"""Pose-free landmarking for standalone drawings (the approved stills).
v2: bill (yellow) -> head centre from bill geometry -> eye (amber,
searched near the head centre only) -> skull (content centroid near
eye, spike-3 semantics) -> neck centreline = shortest skeleton path
from skull to the torso DT-core -> station-1 at the width flare.
Validated against drawn_landmarks on the corpus golds (f0027 chord
200.8, idle_f0030 chord 126.5) before being trusted on the stills."""
import json
import numpy as np
from scipy import ndimage
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
from skimage.morphology import skeletonize
import measure_core as MC
import drawn_landmarks as DL

def bill_and_head(img, cm):
    yel = DL.yellow_mask(img)
    cs = DL.comps(yel)
    if not cs or cs[0][0] < 60:
        return None, 'no yellow bill component'
    yP = cs[0][2]; ycen = yP.mean(axis=0)
    Z = yP - ycen
    evals, evecs = np.linalg.eigh(Z.T @ Z / len(Z))
    ax = evecs[:, -1]; proj = Z @ ax
    e1, e2 = yP[np.argmax(proj)], yP[np.argmin(proj)]
    # provisional: base is the end nearer the big content mass centroid
    ys, xs = np.mgrid[0:MC.H, 0:MC.W]
    body_c = np.array([xs[cm].mean(), ys[cm].mean()])
    base, tip = (e1, e2) if np.hypot(*(e1 - body_c)) < np.hypot(*(e2 - body_c)) \
        else (e2, e1)
    near = np.hypot(*(yP - base).T) <= 14
    base = yP[near].mean(axis=0) if near.sum() else base
    back = base - tip; back /= max(np.hypot(*back), 1e-9)
    head_est = base + back * 30
    return (base, tip, head_est), None

def standalone(img, mask=None):
    if mask is None:
        mask = MC.S1.content_mask(img)
    cm = mask
    notes = {}
    bh, err = bill_and_head(img, cm)
    if err:
        return None, {'fatal': err}
    base, tip, head_est = bh
    ys, xs = np.mgrid[0:MC.H, 0:MC.W]
    # --- eye: amber cluster within 70 px of the head estimate
    near_h = (xs - head_est[0]) ** 2 + (ys - head_est[1]) ** 2 <= 70 ** 2
    eye, eye_best = None, 1e9
    for minsz in (8, 3):
        for size, cen, P in DL.comps(DL.iris_mask(img) & near_h & ~DL.yellow_mask(img)):
            if minsz <= size <= 200 and np.hypot(*(cen - head_est)) < eye_best:
                eye_best = np.hypot(*(cen - head_est)); eye = cen
                notes['eye_px'] = int(size)
        if eye is not None:
            break
    if eye is None:
        return None, {'fatal': 'eye not found'}
    near_eye = (xs - eye[0]) ** 2 + (ys - eye[1]) ** 2 <= 55 ** 2
    m = cm & near_eye
    if m.sum() < 60:
        return None, {'fatal': 'no head mass near eye'}
    skull = np.array([xs[m].mean(), ys[m].mean()])
    bill_ax = tip - base; bill_ax /= max(np.hypot(*bill_ax), 1e-9)
    head_disk = cm & ((xs - skull[0]) ** 2 + (ys - skull[1]) ** 2 <= 80 ** 2)
    crest = DL.march_exit(ndimage.binary_dilation(head_disk, iterations=2),
                          skull, -bill_ax)
    # --- torso DT-core (largest thick component away from the head)
    dt = ndimage.distance_transform_edt(cm)
    core = cm & (dt >= 0.55 * dt.max())
    lab, n = ndimage.label(core)
    torso_c, torso_core_m, best = None, None, -1
    for i in range(1, n + 1):
        mm = lab == i
        if np.hypot(*(np.array([xs[mm].mean(), ys[mm].mean()]) - skull)) < 60:
            continue
        if mm.sum() > best:
            best = mm.sum(); torso_c = np.array([xs[mm].mean(), ys[mm].mean()])
            torso_core_m = mm
    if torso_c is None:
        return None, {'fatal': 'no torso core'}
    # --- skeleton shortest path skull -> torso
    skel = skeletonize(cm)
    sy, sx = np.nonzero(skel)
    idx = -np.ones((MC.H, MC.W), int); idx[sy, sx] = np.arange(len(sx))
    start = idx[sy[np.argmin(np.hypot(sx - skull[0], sy - skull[1]))],
                sx[np.argmin(np.hypot(sx - skull[0], sy - skull[1]))]]
    dd = np.hypot(sx - torso_c[0], sy - torso_c[1]); end = int(np.argmin(dd))
    rows, cols, data = [], [], []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            sh = np.roll(np.roll(idx, dy, axis=0), dx, axis=1)
            valid = (idx >= 0) & (sh >= 0)
            # kill wrap-around edges
            if dx == 1: valid[:, -1] = False
            if dx == -1: valid[:, 0] = False
            if dy == 1: valid[-1, :] = False
            if dy == -1: valid[0, :] = False
            a = idx[valid]; b = sh[valid]
            step = np.hypot(dx, dy)
            wgt = np.full(len(a), step)
            rows.append(a); cols.append(b); data.append(wgt)
    G = csr_matrix((np.concatenate(data),
                    (np.concatenate(rows), np.concatenate(cols))),
                   shape=(len(sx), len(sx)))
    dist, pred = dijkstra(G, indices=start, return_predecessors=True)
    if not np.isfinite(dist[end]):
        return None, {'fatal': 'no skeleton path'}
    chain = []
    cur = end
    while cur != start and cur >= 0:
        chain.append(cur); cur = pred[cur]
    chain.append(start)
    path = np.array([[sx[i], sy[i]] for i in reversed(chain)], float)
    # smooth (moving average, window 9) for stable tangents
    if len(path) > 11:
        ker = np.ones(9) / 9
        sm = np.stack([np.convolve(np.pad(path[:, j], (4, 4), mode='edge'),
                                   ker, mode='valid') for j in (0, 1)], axis=1)
        path = sm
    # arc-length parameterisation from the skull end
    seg = np.hypot(*(path[1:] - path[:-1]).T) if len(path) > 1 else np.array([])
    arc_cum = np.concatenate([[0.0], np.cumsum(seg)])
    total = float(arc_cum[-1])
    # width + DT profiles every ~4 px of arc
    sample_arc = np.arange(0, total, 4.0)
    wp, dp = [], []
    for a in sample_arc:
        i = int(np.searchsorted(arc_cum, a))
        i = min(max(i, 1), len(path) - 1)
        p = path[i]; tan = path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]
        w, _, _ = MC.scan_width(cm, p, tan)
        wp.append(w); dp.append(dt[int(round(p[1])), int(round(p[0]))])
    wp = np.array(wp); dp = np.array(dp)
    mid = (sample_arc > 0.25 * total) & (sample_arc < 0.60 * total)
    w_neck = float(np.median(wp[mid])) if mid.any() else float(np.median(wp))
    d_neck = float(np.median(dp[mid])) if mid.any() else float(np.median(dp))
    # tube entry: first sample where the width settles to tube-like
    entry = 0
    for j in range(len(wp)):
        if wp[j] <= 1.30 * w_neck:
            entry = j; break
    # tube end B: first sustained STRONG flare (2.2x tube width / 2.2x DT)
    B_arc = total
    for j in range(entry, len(wp)):
        if sample_arc[j] < sample_arc[entry] + 10:
            continue
        w_ok = np.all(wp[j:j + 5] > 2.2 * w_neck) if j + 5 <= len(wp) else False
        d_ok = np.all(dp[j:j + 5] > 2.2 * d_neck) if j + 5 <= len(dp) else False
        if w_ok or d_ok:
            B_arc = float(sample_arc[j]); break
    notes['base_rule'] = 'B at 2.2x flare; s1 = B - 0.24*(B->skull arc) (rig station def)'
    notes['B_arc'] = round(B_arc, 1)
    base_arc = 0.76 * B_arc
    notes['tube_entry_arc'] = round(float(sample_arc[entry]), 1)
    notes.update(w_neck=round(w_neck, 1), d_neck=round(d_neck, 1),
                 path_total=round(total, 1), base_arc=round(base_arc, 1))
    # interpolate the base point + widths base->skull
    i = int(np.searchsorted(arc_cum, base_arc)); i = min(max(i, 1), len(path) - 1)
    t = (base_arc - arc_cum[i - 1]) / max(arc_cum[i] - arc_cum[i - 1], 1e-9)
    s1 = path[i - 1] + t * (path[i] - path[i - 1])
    run_arc = base_arc + float(np.hypot(*(path[0] - skull)))
    chord = float(np.hypot(*(skull - s1)))
    keep = arc_cum <= base_arc
    rev = path[keep][::-1]
    if len(rev) < 2:
        rev = path[::-1]
    widths, _ = MC.centerline_widths(cm, list(rev), (0.0, 0.25, 0.5, 0.75))
    torso, _ = MC.torso_hull_from_mask(cm, s1, skull - s1)
    return dict(skull=skull, eye=eye, bill_base=base, bill_tip=tip,
                crest_root=crest, neck_s1=s1, path=path, base_arc=base_arc,
                run_straight=chord, run_arc=float(run_arc),
                widths_frac={str(k): round(v[0], 1) for k, v in widths.items()},
                width_pts={str(k): v for k, v in widths.items()},
                torso_uniform=torso, notes=notes), None

def run_one(name, img, mask=None):
    res, err = standalone(img, mask)
    if err:
        print(name, 'FAILED:', err); return None
    tor = res['torso_uniform']
    print(f"{name}: chord {res['run_straight']:.1f} arc {res['run_arc']:.1f} "
          f"torso {tor:.1f} norm {res['run_straight']/tor if tor else float('nan'):.3f} "
          f"widths {res['widths_frac']} notes {res['notes']}")
    return res

if __name__ == '__main__':
    out = {}
    for pid in ('strike_f0027', 'idle_f0030'):
        img = MC.load(f'{MC.FM3}/corpus/target/{pid}.png')
        r = run_one(f'VALIDATE {pid}', img)
        if r:
            out[f'validate_{pid}'] = {k: r[k] for k in
                ('run_straight', 'run_arc', 'torso_uniform', 'widths_frac', 'notes')}
    def plate_mask(a, thr=100):
        pc = MC.bc.paper_color(a)
        cm0 = np.abs(a - pc).sum(axis=2) > thr
        lab0, n0 = ndimage.label(cm0)
        if n0 == 0:
            return cm0
        sizes = ndimage.sum(cm0, lab0, range(1, n0 + 1))
        keep = lab0 == (1 + int(np.argmax(sizes)))
        dil = ndimage.binary_dilation(keep, iterations=5)
        for i in range(1, n0 + 1):
            if i != 1 + int(np.argmax(sizes)) and sizes[i - 1] >= 200 and (dil & (lab0 == i)).any():
                keep |= lab0 == i
        keep[594:, :] = False
        return keep
    for name, fn in (('approved_strike', 'audubon_strike.png'),
                     ('approved_rest', 'audubon_rest.png')):
        img = MC.load(f'{MC.FS}/{fn}')
        r = run_one(name, img, plate_mask(img))
        if r:
            out[name] = dict(
                run_straight=r['run_straight'], run_arc=r['run_arc'],
                torso_uniform=r['torso_uniform'],
                norm_straight=r['run_straight'] / r['torso_uniform'] if r['torso_uniform'] else None,
                norm_arc=r['run_arc'] / r['torso_uniform'] if r['torso_uniform'] else None,
                widths_frac=r['widths_frac'], notes=r['notes'],
                pts={k: [round(float(v), 1) for v in r[k]] for k in
                     ('skull', 'eye', 'bill_base', 'bill_tip', 'crest_root', 'neck_s1')})
            from PIL import Image, ImageDraw
            ov = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert('RGB')
            dr = ImageDraw.Draw(ov)
            keep = np.linspace(0, 1, len(r['path']))
            # draw path up to base_arc
            seg = np.hypot(*(r['path'][1:] - r['path'][:-1]).T)
            ac = np.concatenate([[0.0], np.cumsum(seg)])
            pts = [tuple(q) for q in r['path'][ac <= r['base_arc']]]
            if len(pts) > 1:
                dr.line(pts, fill=(0, 200, 0), width=3)
            for k, v in r['width_pts'].items():
                dr.line([tuple(v[1]), tuple(v[2])], fill=(0, 200, 255), width=3)
            for k in ('skull', 'eye', 'bill_base', 'bill_tip', 'crest_root', 'neck_s1'):
                p = r[k]
                dr.ellipse([p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6], fill=(255, 0, 0))
                dr.text((p[0] + 8, p[1] - 6), k, fill=(255, 0, 0))
            ov.save(f'{MC.ART2}/strike-measure/landmarks_{name}.png')
            print('overlay saved', name)
    json.dump(out, open(f'{MC.ART2}/strike-measure/stills_results.json', 'w'),
              indent=1, default=str)
    print('stills_results.json written')
