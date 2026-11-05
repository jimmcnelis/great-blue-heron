"""Donor-side DRAWN landmarks + neck centrelines for the warp spike.
Eye/bill tip by pixel tests (amber / yellow classes); neck centrelines by
iterative cross-section run-midpoint refinement on the content mask —
anchored on the drawings, not on any rig pose (the fill-test lesson)."""
import json, math
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

W = '/home/hatch/workspace/heron/art2/warp-spike-v25/work'
MECH = json.load(open(f'{W}/mech.json'))
TORSO = np.array(MECH['TORSO_LOOP'], float)
TGATE = 496.3  # gate torso constant used by all prior measurement reports


def paper_and_content(img):
    a = np.asarray(img).astype(int)
    corners = np.concatenate([a[:40, :40].reshape(-1, 3), a[:40, -40:].reshape(-1, 3),
                                a[-40:, :40].reshape(-1, 3), a[-40:, -40:].reshape(-1, 3)])
    paper = np.median(corners, axis=0)
    diff = np.abs(a - paper).sum(axis=2)
    return paper, diff > 55


def clusters(mask, minpx=8):
    lab, n = ndimage.label(mask)
    out = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if len(xs) >= minpx:
            out.append((len(xs), xs.mean(), ys.mean(), xs, ys))
    return sorted(out, reverse=True)


def amber_eye(img, box, near):
    """Amber clusters in a tight box around the grounded eye; pick a compact
    one nearest the grounded point (the bill's orange section is also amber
    by the colour test but forms a long thin cluster - reject by bbox)."""
    a = np.asarray(img).astype(int)
    R, G, B = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    m = (R > 110) & (G > 55) & (G < 195) & (B < 115) & (R - B > 45) & (R >= G)
    x0, y0, x1, y1 = box
    sub = np.zeros_like(m); sub[y0:y1, x0:x1] = m[y0:y1, x0:x1]
    lab, n = ndimage.label(sub)
    best = None
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if len(xs) < 12: continue
        bw, bh = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
        if max(bw, bh) > 34: continue  # bill section is elongated
        c = (xs.mean(), ys.mean())
        d = math.hypot(c[0] - near[0], c[1] - near[1])
        if best is None or d < best[0]:
            best = (d, len(xs), c)
    if best is None: return None
    return (best[1], best[2][0], best[2][1], None, None)


def bill_tip(img, eye, box):
    a = np.asarray(img).astype(int)
    R, G, B = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    m = (R > 150) & (G > 105) & (B < 115) & (R - B > 70) & (G - B > 35)
    x0, y0, x1, y1 = box
    sub = np.zeros_like(m); sub[y0:y1, x0:x1] = m[y0:y1, x0:x1]
    cs = clusters(sub, minpx=40)
    if not cs:
        return None, None
    _, _, _, xs, ys = cs[0]
    d = np.hypot(xs - eye[0], ys - eye[1])
    k = int(np.argmax(d))
    return (float(xs[k]), float(ys[k])), len(xs)


def point_in_poly(p, poly):
    x, y = p; inside = False; n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xin = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < xin: inside = not inside
    return inside


def smooth(v, k=5):
    if len(v) < k: return v
    ker = np.ones(k) / k
    return np.convolve(np.pad(v, (k // 2, k // 2), mode='edge'), ker, mode='valid')


def extract_centreline(content, guide, halfwin=58, step=6.0, iters=3):
    """Iterative cross-section refinement. Returns stations (x,y), halfwidths
    per side (neg, pos along normal), and the refined guide."""
    guide = np.array(guide, float)
    for _ in range(iters):
        # resample guide at ~step px
        seg = np.hypot(*np.diff(guide, axis=0).T)
        s = np.concatenate([[0], np.cumsum(seg)])
        n = max(int(s[-1] / step), 4)
        su = np.linspace(0, s[-1], n + 1)
        gx = np.interp(su, s, guide[:, 0]); gy = np.interp(su, s, guide[:, 1])
        pts = np.stack([gx, gy], axis=1)
        tang = np.gradient(pts, axis=0); tang /= np.hypot(tang[:, 0], tang[:, 1])[:, None]
        nrm = np.stack([-tang[:, 1], tang[:, 0]], axis=1)
        centres, hw_neg, hw_pos, ok = [], [], [], []
        H, Wd = content.shape
        for i, p in enumerate(pts):
            ts = np.linspace(-halfwin, halfwin, 233)
            xs = np.clip((p[0] + nrm[i, 0] * ts).astype(int), 0, Wd - 1)
            ys = np.clip((p[1] + nrm[i, 1] * ts).astype(int), 0, H - 1)
            line = content[ys, xs]
            # runs of content
            runs = []
            j = 0
            while j < len(ts):
                if line[j]:
                    k = j
                    while k + 1 < len(ts) and line[k + 1]: k += 1
                    runs.append((ts[j], ts[k])); j = k + 1
                else: j += 1
            if not runs:
                centres.append(p); hw_neg.append(20.0); hw_pos.append(20.0); ok.append(False); continue
            # run whose interval contains 0 (guide), else nearest run
            cand = [r for r in runs if r[0] - 6 <= 0 <= r[1] + 6]
            r = cand[0] if cand else min(runs, key=lambda r: min(abs(r[0]), abs(r[1])))
            mid = 0.5 * (r[0] + r[1])
            centres.append(p + nrm[i] * mid)
            hw_neg.append(mid - r[0]); hw_pos.append(r[1] - mid); ok.append(True)
        centres = np.array(centres)
        centres[:, 0] = smooth(centres[:, 0]); centres[:, 1] = smooth(centres[:, 1])
        guide = centres
    hw_neg = np.clip(smooth(np.array(hw_neg)), 5, 70)
    hw_pos = np.clip(smooth(np.array(hw_pos)), 5, 70)
    return guide, hw_neg, hw_pos, np.array(ok)


def trim_to_visible(centres, hw_n, hw_p, ok):
    """Drop stations inside the torso polygon; visible tube starts at the
    first station outside it (walking from the root)."""
    idx = [i for i, p in enumerate(centres) if not point_in_poly(p, TORSO)]
    if not idx: return centres, hw_n, hw_p, ok
    i0 = idx[0]
    return centres[i0:], hw_n[i0:], hw_p[i0:], ok[i0:]


def arc_len(pts):
    return float(np.hypot(*np.diff(pts, axis=0).T).sum())


result = {}

# ---------------- ALERT donor (for COIL)
img = Image.open('/home/hatch/workspace/heron/art2/keyframes-v25/keyframe_alert.png').convert('RGB')
paper, content = paper_and_content(img)
eye_c = amber_eye(img, (705, 8, 835, 85), (768.0, 39.0))  # near = grounded eye
eye = (eye_c[1], eye_c[2])
tip, billpx = bill_tip(img, eye, (680, 5, 1024, 130))
bdir = math.degrees(math.atan2(tip[1] - eye[1], tip[0] - eye[0]))
guide0 = np.array(MECH['alert']['visible'], float)
cen, hwn, hwp, ok = extract_centreline(content, guide0)
cen, hwn, hwp, ok = trim_to_visible(cen, hwn, hwp, ok)
result['alert'] = dict(eye=eye, eye_cluster_px=int(eye_c[0]), bill_tip=tip, bill_px=int(billpx),
                       bill_dir_deg=bdir, centreline=cen.tolist(),
                       hw_neg=hwn.tolist(), hw_pos=hwp.tolist(), ok=ok.tolist(),
                       arc_px=arc_len(cen))
print('ALERT donor: eye', np.round(eye, 1), 'tip', np.round(tip, 1), 'bill_dir', round(bdir, 1),
      'neck arc', round(arc_len(cen), 1), 'stations', len(cen), 'ok frac', round(float(ok.mean()), 2))
dr = ImageDraw.Draw(img)
dr.line([tuple(p) for p in cen], fill=(255, 0, 0), width=2)
for p in cen[::4]: dr.ellipse([p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3], outline=(255, 200, 0))
dr.ellipse([eye[0] - 6, eye[1] - 6, eye[0] + 6, eye[1] + 6], outline=(0, 255, 0), width=2)
dr.ellipse([tip[0] - 6, tip[1] - 6, tip[0] + 6, tip[1] + 6], outline=(0, 255, 255), width=2)
img.save(f'{W}/donor_alert_debug.png')

# ---------------- PEAK donor (for PEAK)
img2 = Image.open('/home/hatch/workspace/heron/art2/keyframes-v25/keyframe_peak.png').convert('RGB')
paper2, content2 = paper_and_content(img2)
eye_c2 = amber_eye(img2, (685, 385, 815, 495), (747.0, 437.0))  # near = grounded/crop eye
eye2 = (eye_c2[1], eye_c2[2])
tip2, billpx2 = bill_tip(img2, eye2, (640, 380, 830, 600))
bdir2 = math.degrees(math.atan2(tip2[1] - eye2[1], tip2[0] - eye2[0]))
guide0p = np.array([[600, 228], [632, 282], [660, 330], [678, 368], [688, 390]], float)
cen2, hwn2, hwp2, ok2 = extract_centreline(content2, guide0p)
cen2, hwn2, hwp2, ok2 = trim_to_visible(cen2, hwn2, hwp2, ok2)
result['peak'] = dict(eye=eye2, eye_cluster_px=int(eye_c2[0]), bill_tip=tip2, bill_px=int(billpx2),
                      bill_dir_deg=bdir2, centreline=cen2.tolist(),
                      hw_neg=hwn2.tolist(), hw_pos=hwp2.tolist(), ok=ok2.tolist(),
                      arc_px=arc_len(cen2))
print('PEAK donor: eye', np.round(eye2, 1), 'tip', np.round(tip2, 1), 'bill_dir', round(bdir2, 1),
      'neck arc', round(arc_len(cen2), 1), 'stations', len(cen2), 'ok frac', round(float(ok2.mean()), 2))
dr = ImageDraw.Draw(img2)
dr.line([tuple(p) for p in cen2], fill=(255, 0, 0), width=2)
for p in cen2[::4]: dr.ellipse([p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3], outline=(255, 200, 0))
dr.ellipse([eye2[0] - 6, eye2[1] - 6, eye2[0] + 6, eye2[1] + 6], outline=(0, 255, 0), width=2)
dr.ellipse([tip2[0] - 6, tip2[1] - 6, tip2[0] + 6, tip2[1] + 6], outline=(0, 255, 255), width=2)
img2.save(f'{W}/donor_peak_debug.png')

json.dump(result, open(f'{W}/donors.json', 'w'), indent=1)
print('donors.json written')
