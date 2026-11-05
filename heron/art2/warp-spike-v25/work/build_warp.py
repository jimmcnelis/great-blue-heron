#!/usr/bin/env python3
"""Heron warp spike — build warp_coil.png + warp_peak.png from the APPROVED
alert plate, warped through the v2.5 mechanism correspondence.

Jimmy's rulings (2026-11-04 11:13 / 11:14):
- keyframe_alert.png is the ONLY donor (settled plate; coil donor + identity
  donor + plume/strands source). keyframe_peak.png is REJECTED — unused.
- Peak geometry = mechanism canon spear; peak head = alert head, eye-anchored,
  pitched to the spear line (mechanism head frame, bill 53.7 deg) — the
  attitude real strike frames show (qpYk t=1.70s; 57Y f90; 6bc t=59.42s).
- Plume is its own layer: preserved from the alert plate, never pasted over
  as a mass; the warped tube passes in front only where anatomy puts it there.

Method: base = alert plate with old neck/head erased by inpainting where the
target pose does not keep them; neck tube warped station-by-station
(arc-fraction u, cross-fraction v) from the donor's DRAWN centreline to the
target visible chain; per-region quantile luminance remap (donor tube -> warped
tube); head pasted as one assembly, eye-anchored; plume zone of the base kept.

One build per frame. Bookkeeping masks recorded for the gate measurements.
"""
import json, math
import numpy as np
import cv2
from scipy.spatial import cKDTree

ROOT = '/home/hatch/workspace/heron/art2'
W = f'{ROOT}/warp-spike-v25/work'
TORSO_GATE = 496.3

mech = json.load(open(f'{W}/mech.json'))
don = json.load(open(f'{W}/donors.json'))
alert = cv2.cvtColor(cv2.imread(f'{ROOT}/keyframes-v25/keyframe_alert.png'),
                     cv2.COLOR_BGR2RGB).astype(np.float32)
H, Wd = alert.shape[:2]

# ---------- shared helpers ----------
def paper_of(img):
    cs = []
    for y0, x0 in [(0, 0), (0, Wd - 60), (H - 60, 0), (H - 60, Wd - 60)]:
        cs.append(np.median(img[y0:y0 + 60, x0:x0 + 60].reshape(-1, 3), axis=0))
    return np.median(np.array(cs), axis=0)

def content_mask(img, paper):
    return (np.abs(img - paper).sum(axis=2) > 55)

def amber_find(img, cx, cy, box=22):
    x0, x1 = max(0, cx - box), min(Wd, cx + box + 1)
    y0, y1 = max(0, cy - box), min(H, cy + box + 1)
    sub = img[y0:y1, x0:x1]
    r, g, b = sub[:, :, 0], sub[:, :, 1], sub[:, :, 2]
    m = ((r > 150) & (r < 230) & (g > 90) & (g < 180) & (b < 120)
         & (r - b > 60)).astype(np.uint8)
    n, lab, stats, cents = cv2.connectedComponentsWithStats(m, 8)
    best = None
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] >= 3:
            if best is None or stats[i, cv2.CC_STAT_AREA] > stats[best, cv2.CC_STAT_AREA]:
                best = i
    if best is None:
        return None
    return (float(cents[best][0] + x0), float(cents[best][1] + y0),
            int(stats[best, cv2.CC_STAT_AREA]))

def resample_chain(pts, step=2.0):
    pts = np.asarray(pts, float)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    cum = np.concatenate([[0], np.cumsum(seg)])
    total = cum[-1]
    s = np.arange(0, total, step)
    if s[-1] < total - 1e-6:
        s = np.append(s, total)
    x = np.interp(s, cum, pts[:, 0]); y = np.interp(s, cum, pts[:, 1])
    return np.stack([x, y], axis=1), s, total

def frames_of(chain):
    t = np.gradient(chain, axis=0)
    t /= (np.linalg.norm(t, axis=1, keepdims=True) + 1e-12)
    n = np.stack([-t[:, 1], t[:, 0]], axis=1)   # left of travel
    return t, n

def heading_series(chain):
    t, _ = frames_of(chain)
    return np.degrees(np.arctan2(t[:, 1], t[:, 0]))

# ---------- donor (alert) centreline, resampled ----------
d = don['alert']
dchain_raw = np.array(d['centreline'], float)
dhw_neg = np.array(d['hw_neg'], float)
dhw_pos = np.array(d['hw_pos'], float)
dchain, ds, dL = resample_chain(dchain_raw)
# halfwidths interpolated on the same arc grid
seg = np.linalg.norm(np.diff(dchain_raw, axis=0), axis=1)
cum_raw = np.concatenate([[0], np.cumsum(seg)])
dhn = np.interp(ds, cum_raw, dhw_neg); dhp = np.interp(ds, cum_raw, dhw_pos)
dtan, dnrm = frames_of(dchain)
dhead = heading_series(dchain)
DONOR_EYE = np.array(d['eye']); DONOR_BILL = math.radians(d['bill_dir_deg'])
# donor tube content luminance distribution (for the quantile remap)
yy, xx = np.mgrid[0:H, 0:Wd]
tree_d = cKDTree(dchain)
dist_d, idx_d = tree_d.query(np.stack([xx.ravel(), yy.ravel()], axis=1))
# side sign for donor pixels
rel = np.stack([xx.ravel() - dchain[idx_d, 0], yy.ravel() - dchain[idx_d, 1]], axis=1)
side = np.sign(rel[:, 0] * dnrm[idx_d, 0] + rel[:, 1] * dnrm[idx_d, 1])
hw_d_pix = np.where(side >= 0, dhp[idx_d], dhn[idx_d])
donor_tube = (dist_d <= hw_d_pix).reshape(H, Wd)
paper_alert = paper_of(alert)
donor_tube_content = donor_tube & content_mask(alert, paper_alert)
lum_alert = alert.mean(axis=2)
donor_lums = np.sort(lum_alert[donor_tube_content])

# donor content mask (for head patch alpha)
donor_content = content_mask(alert, paper_alert)

# ---------- geometry keep pieces (base) ----------
def poly_mask(poly, dil=0):
    m = np.zeros((H, Wd), np.uint8)
    cv2.fillPoly(m, [np.array(poly, np.int32)], 1)
    if dil:
        m = cv2.dilate(m, np.ones((2 * dil + 1, 2 * dil + 1), np.uint8))
    return m.astype(bool)

def corridor_mask(pts, dil):
    m = np.zeros((H, Wd), np.uint8)
    cv2.polylines(m, [np.array(pts, np.int32)], False, 1, 1)
    return cv2.dilate(m, np.ones((2 * dil + 1, 2 * dil + 1), np.uint8)).astype(bool)

keep_static = poly_mask(mech['TORSO_LOOP'], 12)
for _hip, _knee, _foot in mech['LEGS']:
    keep_static |= corridor_mask([_hip, _knee, _foot], 13)
    keep_static |= corridor_mask([_foot, (_foot[0] + 55, _foot[1])], 9)
water = np.zeros((H, Wd), bool); water[496:, :] = True
keep_static |= water

# ---------- tube warp ----------
def warp_tube(target):
    chain_raw = np.array(target['visible'], float)
    widths_raw = np.array(target['widths_vis'], float)
    cum_vis = np.array(target['s_vis'], float)
    chain, s, tL = resample_chain(chain_raw)
    wid = np.interp(s, cum_vis, widths_raw)
    hw_t = wid / 2.0
    ttan, tnrm = frames_of(chain)
    thead = heading_series(chain)
    pad = int(hw_t.max()) + 10
    x0 = max(0, int(chain[:, 0].min()) - pad); x1 = min(Wd, int(chain[:, 0].max()) + pad + 1)
    y0 = max(0, int(chain[:, 1].min()) - pad); y1 = min(H, int(chain[:, 1].max()) + pad + 1)
    gy, gx = np.mgrid[y0:y1, x0:x1]
    pts = np.stack([gx.ravel(), gy.ravel()], axis=1).astype(float)
    tree = cKDTree(chain)
    dist, idx = tree.query(pts)
    rel = pts - chain[idx]
    sdist = rel[:, 0] * tnrm[idx, 0] + rel[:, 1] * tnrm[idx, 1]
    hwt = hw_t[idx]
    v = sdist / np.maximum(hwt, 1e-6)
    u = s[idx] / tL
    # donor lookup
    du = np.clip(u * dL, 0, dL)
    di = np.searchsorted(ds, du)
    di = np.clip(di, 0, len(ds) - 1)
    lo = np.clip(di - 1, 0, len(ds) - 1)
    frac = np.clip((du - ds[lo]) / np.maximum(ds[di] - ds[lo], 1e-9), 0, 1)
    dc = dchain[lo] * (1 - frac[:, None]) + dchain[di] * frac[:, None]
    dn = dnrm[lo] * (1 - frac[:, None]) + dnrm[di] * frac[:, None]
    hwd = np.where(v >= 0, dhp[lo] * (1 - frac) + dhp[di] * frac,
                   dhn[lo] * (1 - frac) + dhn[di] * frac)
    src = dc + dn * (v * hwd)[:, None]
    mapx = src[:, 0].reshape(gy.shape).astype(np.float32)
    mapy = src[:, 1].reshape(gy.shape).astype(np.float32)
    warped = cv2.remap(alert, mapx, mapy, cv2.INTER_LINEAR,
                       borderMode=cv2.BORDER_REPLICATE)
    alpha = np.clip((hwt + 4.0 - np.abs(sdist)) / 6.0, 0, 1).reshape(gy.shape)
    # quantile luminance remap: warped tube -> donor tube distribution
    inside = alpha > 0.35
    wl = warped.mean(axis=2)
    vals = wl[inside]
    if len(vals) > 200:
        qs = np.linspace(0, 1, 512)
        src_q = np.quantile(vals, qs)
        dst_q = np.quantile(donor_lums, qs)
        newlum = np.interp(wl, src_q, dst_q)
        ratio = np.where(wl > 1.0, newlum / np.maximum(wl, 1.0), 1.0)
        warped = np.clip(warped * ratio[:, :, None], 0, 255)
    tube_full = np.zeros((H, Wd), np.float32)
    tube_full[y0:y1, x0:x1] = alpha
    return warped, (y0, y1, x0, x1), tube_full, dict(
        chain=chain, s=s, tL=float(tL), hw_t=hw_t, thead=thead,
        u_of_idx=None)

# ---------- head patch ----------
def head_patch(target_bill_deg, falloff_start_along):
    """Donor head as one assembly in an RGBA canvas, eye-anchored rotation."""
    T = TORSO_GATE
    ex, ey = DONOR_EYE
    ca, sa = math.cos(DONOR_BILL), math.sin(DONOR_BILL)
    # donor-frame coords of every pixel
    rx = xx - ex; ry = yy - ey
    along = rx * ca + ry * sa
    up = rx * sa - ry * ca          # perp = (sin, -cos): up positive = -up screen? use rig conv below
    # rig convention: perp = (dvec.y, -dvec.x) -> offset = along*dvec + off*perp,
    # off = rx*dvec.y - ry*dvec.x with sign such that perp points screen-up for
    # a rightward bill. off here = rx*sa - ry*ca == that. Good.
    in_box = ((along >= -0.37 * T) & (along <= 0.30 * T)
              & (up >= -0.15 * T) & (up <= 0.15 * T))
    alpha = np.where(in_box & donor_content, 1.0, 0.0)
    dark = np.clip((165.0 - lum_alert) / 115.0, 0, 1)
    fall = np.where(along < falloff_start_along,
                    0.30 + 0.70 * dark, 1.0)
    alpha = alpha * fall
    rgba = np.dstack([alert, alpha * 255]).astype(np.uint8)
    # rotate about the donor eye by delta, then translate eye -> target anchor
    return rgba

def place_head(rgba, target_eye, target_bill_deg):
    delta = math.radians(target_bill_deg) - DONOR_BILL
    ex, ey = DONOR_EYE
    M = cv2.getRotationMatrix2D((float(ex), float(ey)),
                                -math.degrees(delta), 1.0)  # cv2: +angle = CCW in image coords -> negate for screen-clockwise
    M[0, 2] += target_eye[0] - ex
    M[1, 2] += target_eye[1] - ey
    out = cv2.warpAffine(rgba, M, (Wd, H), flags=cv2.INTER_LINEAR,
                         borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    return out

# ---------- build one frame ----------
def build(name, pose_key, plume_x1, falloff_start):
    tgt = mech[pose_key]
    warped, (y0, y1, x0, x1), tube_alpha, tinfo = warp_tube(tgt)
    # head patch (donor head re-pitched to the target bill direction)
    rgba = head_patch(tgt['bill_dir_deg'], falloff_start)
    placed = place_head(rgba, tgt['eye'], tgt['bill_dir_deg'])
    head_alpha = placed[:, :, 3].astype(np.float32) / 255.0
    # keep mask
    keep = keep_static.copy()
    plume = np.zeros((H, Wd), bool); plume[225:366, 330:plume_x1] = True
    keep |= plume
    keep |= tube_alpha > 0.02
    keep |= head_alpha > 0.02
    # erase old content not kept, inpaint
    base_content = content_mask(alert, paper_alert)
    erase = base_content & (~keep)
    erase_u8 = cv2.dilate(erase.astype(np.uint8),
                          np.ones((5, 5), np.uint8))
    keep_core = cv2.erode(keep.astype(np.uint8),
                          np.ones((7, 7), np.uint8)).astype(bool)
    erase_u8[keep_core] = 0
    base8 = np.clip(alert, 0, 255).astype(np.uint8)
    filled = cv2.inpaint(base8, erase_u8 * 255, 6, cv2.INPAINT_TELEA)
    out = filled.astype(np.float32)
    # paste tube
    a = tube_alpha[y0:y1, x0:x1][:, :, None]
    out[y0:y1, x0:x1] = warped * a + out[y0:y1, x0:x1] * (1 - a)
    # paste head
    ha = head_alpha[:, :, None]
    out = placed[:, :, :3].astype(np.float32) * ha + out * (1 - ha)
    out8 = np.clip(out, 0, 255).astype(np.uint8)
    cv2.imwrite(f'{ROOT}/warp-spike-v25/warp_{name}.png',
                cv2.cvtColor(out8, cv2.COLOR_RGB2BGR))
    # ---- bookkeeping measurements ----
    paper_out = paper_of(out)
    cm = content_mask(out, paper_out)
    black = float((cm & (out.mean(axis=2) < 70)).sum() / max(cm.sum(), 1))
    eye_t = tgt['eye']
    af = amber_find(out, int(round(eye_t[0])), int(round(eye_t[1])))
    eye_err = (None if af is None else
               float(np.hypot(af[0] - eye_t[0], af[1] - eye_t[1])))
    # corridor walk: content fraction across the tube at 40 stations
    chain = tinfo['chain']; s = tinfo['s']; hw = tinfo['hw_t']
    ttan, tnrm = frames_of(chain)
    fr = []
    for i in np.linspace(2, len(chain) - 3, 40).astype(int):
        offs = np.linspace(-0.7, 0.7, 15) * hw[i]
        xs = np.clip((chain[i, 0] + tnrm[i, 0] * offs).astype(int), 0, Wd - 1)
        ys = np.clip((chain[i, 1] + tnrm[i, 1] * offs).astype(int), 0, H - 1)
        fr.append(float(cm[ys, xs].mean()))
    # head coverage: rig head region (skull ellipse + bill tri + plume spike)
    dv = np.array(tgt['dvec']); pp = np.array([dv[1], -dv[0]])
    sk = np.array(tgt['skull'])
    ell = np.zeros((H, Wd), np.uint8)
    cv2.ellipse(ell, (int(sk[0]), int(sk[1])),
                (int(0.070 * TORSO_GATE), int(0.045 * TORSO_GATE)),
                math.degrees(math.atan2(dv[1], dv[0])), 0, 360, 1, -1)
    tip = sk + dv * (0.27 * TORSO_GATE)   # bill tip reach from skull (animal spec)
    perp_h = pp * (0.016 * TORSO_GATE)
    bill = poly_mask([tuple(sk + perp_h), tuple(tip), tuple(sk - perp_h)])
    spike_pts = [tuple(sk - dv * (k * TORSO_GATE) + pp * (w * TORSO_GATE))
                 for k, w in [(0, 0.028), (0.35, 0.032), (0.42, 0.0),
                              (0.30, -0.030), (0, -0.026)]]
    spike = poly_mask(spike_pts)
    solid = (ell.astype(bool) | bill)
    covered_solid = solid & ((head_alpha >= 0.5) | (tube_alpha >= 0.5))
    covered_all = (solid | spike) & ((head_alpha >= 0.5) | (tube_alpha >= 0.5))
    # stretch: per 10 u-bins
    bins = []
    uu = s / tinfo['tL']
    for b in range(10):
        m = (uu >= b / 10) & (uu < (b + 1) / 10 + 1e-9)
        if m.sum() < 2:
            continue
        di2 = np.clip((np.linspace(b / 10, (b + 1) / 10, 24)) * dL, 0, dL)
        dhw_b = np.interp(di2, ds, (dhn + dhp) / 2)
        dh_b = np.interp(di2, ds, dhead)
        bins.append(dict(
            u=[b / 10, (b + 1) / 10],
            arc_ratio=float(tinfo['tL'] / dL),
            cross_ratio=float(hw[m].mean() / max(dhw_b.mean(), 1e-6)),
            turn_target_deg=float(tinfo['thead'][m].max() - tinfo['thead'][m].min()),
            turn_donor_deg=float(dh_b.max() - dh_b.min())))
    # centreline radius of curvature (target), min
    th = np.unwrap(np.radians(tinfo['thead']))
    dth = np.abs(np.gradient(th))
    ds_step = np.gradient(s)
    R = np.where(dth > 1e-6, ds_step / np.maximum(dth, 1e-9), 1e9)
    book = dict(frame=name, black_fraction=black,
                eye_found=af, eye_err_px=eye_err,
                corridor_min=float(np.min(fr)), corridor_mean=float(np.mean(fr)),
                corridor_low=[float(x) for x in fr if x < 0.6],
                head_coverage_solid=float(covered_solid.sum() / max(solid.sum(), 1)),
                head_coverage_with_spike=float(covered_all.sum() / max((solid | spike).sum(), 1)),
                stretch_bins=bins,
                min_radius_centreline=float(np.min(R)),
                erase_px=int(erase_u8.sum()))
    json.dump(book, open(f'{W}/book_{name}.json', 'w'), indent=1, default=str)
    print(name, json.dumps({k: book[k] for k in
          ['black_fraction', 'eye_err_px', 'corridor_min', 'corridor_mean',
           'head_coverage_solid', 'head_coverage_with_spike',
           'min_radius_centreline', 'erase_px']}, indent=1))
    return book

if __name__ == '__main__':
    build('coil', 'deep_coil', plume_x1=712, falloff_start=-0.13 * TORSO_GATE)
    build('peak', 'strike_peak', plume_x1=626, falloff_start=-0.06 * TORSO_GATE)
