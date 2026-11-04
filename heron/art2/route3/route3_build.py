"""Route 3: part-composite proof. Real-frame part textures, TPS-warped by the
rig keypoints (poses_art2.json), composited in rig draw order on white.
Pipeline steps (the ONLY steps): rembg alpha -> part polygon masks -> TPS warp
(scipy RBFInterpolator thin_plate_spline) -> alpha feather 5px at part edges ->
global slate harmonization for IR donors -> alpha-over composite -> waterline
clip on standing legs. No retouching."""
import json, os, sys
import numpy as np
import cv2
sys.path.insert(0, os.path.expanduser('~/workspace/heron/art2'))
from maskrender import fish_profile

HERE = os.path.expanduser('~/workspace/heron/art2/route3')
WORK = f'{HERE}/work'
OUT = f'{HERE}/out'
os.makedirs(OUT, exist_ok=True)
W, H = 1024, 600
WATER_Y = 493
U = 6.6667

poses = json.load(open(os.path.expanduser('~/workspace/heron/art2/poses_art2.json')))['poses']

# ---------- donors ----------
def load_rgba(path, alpha_path):
    im = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB).astype(np.float32)
    a = cv2.imread(alpha_path, cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255.0
    return im, a

B_img, B_a = load_rgba(os.path.expanduser('~/workspace/heron/reference/real-heron-b.jpg'), f'{WORK}/alpha_b.png')
P_img, P_a = load_rgba(f'{WORK}/src_patio.png', f'{WORK}/alpha_patio.png')      # crop offset (1000,250)
N_img, N_a = load_rgba(f'{WORK}/src_night5.png', f'{WORK}/alpha_night5.png')    # crop offset (300,0)
PO = np.array([1000., 250.]); NO = np.array([300., 0.])

# global harmonization: IR gray -> slate, scaled so IR mean maps to donor-B torso mean colour
def poly_mask(shape, poly):
    m = np.zeros(shape[:2], np.uint8)
    cv2.fillPoly(m, [np.asarray(poly, np.int32)], 1)
    return m.astype(bool)

# donor B keypoints (donor px, read off 50px grids)
B = dict(
    torso=[(95,735),(115,600),(155,480),(215,410),(285,382),(320,400),(328,455),(315,560),(285,680),(235,760),(175,795),(125,800),(100,780)],
    spine=[(302,418),(292,335),(288,255),(302,182),(332,128)],
    spine_hw=[31,32,30,26,20],
    head_ctrl=[(302,118),(315,95),(345,85),(372,95),(388,112),(390,130),(372,146),(340,150),(312,140),(385,110),(548,116),(388,134)],
    head_mask=[(302,118),(315,95),(345,85),(372,95),(388,112),(548,116),(388,134),(372,146),(340,150),(312,140)],
    wing=[(150,470),(215,425),(275,430),(295,470),(280,580),(245,690),(190,735),(145,720),(125,600),(130,520)],
    tail=[(88,720),(92,805),(150,800)],
    leg_n=[(243,690),(252,792),(258,878)], leg_f=[(205,705),(198,795),(192,872)],
)
torso_ref = B_img[poly_mask(B_img.shape, B['torso']) & (B_a > 0.5)]
REF_RGB = torso_ref.mean(axis=0); REF_GRAY = float(torso_ref.mean())
TINT = REF_RGB / REF_GRAY
print('harmonization tint (IR gray -> RGB):', np.round(TINT, 3), 'ref RGB', np.round(REF_RGB, 1))

def tint_ir(img):
    g = img.mean(axis=2, keepdims=True)
    return np.clip(g * TINT[None, None, :], 0, 255).astype(np.float32)

P_img_c = tint_ir(P_img); N_img_c = tint_ir(N_img)

# patio donor keypoints (full-frame coords minus offset applied at use)
P = dict(
    torso=[(1068,400),(1078,372),(1105,358),(1135,360),(1158,378),(1165,410),(1163,455),(1152,495),(1132,518),(1108,525),(1088,518),(1072,485),(1065,440)],
    spine=[(1112,385),(1110,352),(1109,326),(1110,306),(1112,288)],
    spine_hw=[19,18,17,16,14],
    # order matched to target front bill_poly semantics: skull loop, inner skull,
    # then the downward bill spike (the rig's front pose carries the bill as a
    # downward spike, pts 9-10) -> donor's downward-hanging frontal bill tip.
    head_ctrl=[(1096,300),(1102,283),(1120,280),(1131,295),(1124,322),(1104,324),(1094,310),(1106,312),(1116,312),(1112,352),(1102,352)],
    head_mask=[(1092,295),(1100,278),(1125,278),(1135,295),(1130,325),(1115,330),(1105,352),(1098,330),(1094,315)],
    wing=[(1112,365),(1128,378),(1148,395),(1160,425),(1160,465),(1148,498),(1130,518),(1120,485),(1115,440),(1113,400)],
    tail=[(1088,518),(1132,518),(1110,535)],
    leg_n=[(1128,512),(1122,560),(1122,620)], leg_f=[(1090,508),(1086,552),(1078,602)],
)
for k in ('torso','spine','head_ctrl','head_mask','wing','tail','leg_n','leg_f'):
    P[k] = [(x - PO[0], y - PO[1]) for x, y in P[k]]

# night5 right fan wing (crop coords). Control order follows the target
# wing_poly semantics: root -> up the inner (centre-seam) edge -> tip ->
# down the outer edge -> along the fingered bottom edge back to root.
# Outline-only points (v1 used interior points and the TPS folded into swirls).
NW_ctrl = [(235,338),(242,295),(248,255),(252,215),(258,175),(265,140),(280,105),(310,80),(365,60),
           (390,90),(400,130),(403,170),(400,210),(390,250),(365,285),(320,315),(275,330)]
NW_mask = NW_ctrl

# ---------- warp ----------
from scipy.interpolate import RBFInterpolator

def warp_part(img, alpha, src_ctrl, tgt_ctrl, pad=30):
    """TPS (target->source) remap of the part over its target bbox."""
    S = np.asarray(src_ctrl, float); T = np.asarray(tgt_ctrl, float)
    lo = T.min(axis=0) - pad; hi = T.max(axis=0) + pad
    x0, y0 = np.maximum(lo, 0).astype(int); x1, y1 = np.minimum(hi, [W, H]).astype(int)
    if x1 <= x0 or y1 <= y0: return None
    gy, gx = np.mgrid[y0:y1, x0:x1]
    pts = np.stack([gx.ravel(), gy.ravel()], axis=1).astype(float)
    fx = RBFInterpolator(T, S[:, 0], kernel='thin_plate_spline', smoothing=1.5)
    fy = RBFInterpolator(T, S[:, 1], kernel='thin_plate_spline', smoothing=1.5)
    mx = fx(pts).reshape(gx.shape).astype(np.float32); my = fy(pts).reshape(gx.shape).astype(np.float32)
    rgba = np.dstack([img, alpha * 255]).astype(np.float32)
    out = cv2.remap(rgba, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    return (x0, y0, out)

def tube_edges(spine, hw):
    sp = np.asarray(spine, float); hw = np.asarray(hw, float)
    d = np.gradient(sp, axis=0); n = np.hypot(d[:, 0], d[:, 1]); n[n == 0] = 1
    nrm = np.stack([-d[:, 1] / n, d[:, 0] / n], axis=1)
    return [tuple(p) for p in sp + nrm * hw[:, None]] + [tuple(p) for p in (sp - nrm * hw[:, None])[::-1]]

def tube_mask(shape, spine, hw_full):
    return poly_mask(shape, tube_edges(spine, np.asarray(hw_full) / 2))

def target_neck_widths(scalars):
    t = np.linspace(0, 1, 5)
    w = (6.4 - 3.0 * t) * float(scalars.get('neck_w', 1.0)) * U
    amp = float(scalars.get('bulge_amp', 0.0))
    if amp > 0.01:
        s = 1.0 - t
        w = w * (1.0 + amp * 0.95 * fish_profile(s - float(scalars.get('bulge_pos', 0.0))))
    return w

def seg_poly(a, b, w0, w1):
    a = np.asarray(a, float); b = np.asarray(b, float)
    d = b - a; L = max(np.hypot(*d), 1e-9); d = d / L; p = np.array([-d[1], d[0]])
    return [tuple(a + p * w0 / 2), tuple(b + p * w1 / 2), tuple(b - p * w1 / 2), tuple(a - p * w0 / 2)]

def leg_ctrl(src_leg, tgt_leg):
    s_hw = [9, 5.5, 2.5]; t_hw = [9.7, 5.5, 2.0]
    def edges(leg, hw):
        out = []
        for (a, b), h in zip([(leg[0], leg[1]), (leg[1], leg[2]), (leg[2], leg[2])], hw):
            d = np.asarray(b, float) - np.asarray(a, float)
            if np.hypot(*d) < 1e-6: d = np.array([0., 1.])
            d = d / np.hypot(*d); p = np.array([-d[1], d[0]])
            out.append(tuple(np.asarray(a if h != hw[-1] else leg[2], float) + p * h))
        return out
    sc = list(src_leg) + edges(src_leg, s_hw) + [tuple(np.asarray(src_leg[1]) - (np.array(edges(src_leg, s_hw)[1]) - np.asarray(src_leg[1])))]
    tc = list(tgt_leg) + edges(tgt_leg, t_hw) + [tuple(np.asarray(tgt_leg[1]) - (np.array(edges(tgt_leg, t_hw)[1]) - np.asarray(tgt_leg[1])))]
    return sc, tc

def leg_mask(shape, alpha, leg):
    m = poly_mask(shape, seg_poly(leg[0], leg[1], 20, 13)) | poly_mask(shape, seg_poly(leg[1], leg[2], 9, 6))
    both = m & (alpha > 0.35)
    # thin IR/B legs can fall out of rembg alpha; fall back to the bare tube if alpha keeps <40%
    return both if both.sum() > 0.4 * m.sum() else m

report = {}

def build(pose_name):
    PZ = poses[pose_name]; kp = PZ['keypoints_master']; sc = PZ['scalars']
    canvas = np.full((H, W, 3), 255, np.float32)
    donor = B; img, al = B_img, B_a
    if pose_name == 'front':
        donor = P; img, al = P_img_c, P_a
    parts = []  # (name, img, alpha_masked, src_ctrl, tgt_ctrl, darken, clip_water)
    def masked(mask_poly=None, mask_arr=None):
        m = mask_arr if mask_arr is not None else poly_mask(img.shape, mask_poly)
        a = al.copy(); a[~m] = 0
        return a
    # far leg
    s_c, t_c = leg_ctrl(donor['leg_f'], [kp['hip_f'], kp['knee_f'], kp['foot_f']])
    parts.append(('leg_far', img, masked(mask_arr=leg_mask(img.shape, al, donor['leg_f'])), s_c, t_c, 0.85, pose_name != 'flight'))
    # tail
    tc_src = donor['tail'] + [tuple(np.mean(donor['tail'], axis=0))]
    tc_tgt = kp['tail_poly'] + [tuple(np.mean(kp['tail_poly'], axis=0))]
    parts.append(('tail', img, masked(donor['tail']), tc_src, tc_tgt, 1.0, False))
    # torso
    parts.append(('torso', img, masked(donor['torso']), donor['torso'], kp['torso_poly'], 1.0, False))
    # flight far wing + near wing from night5 fan
    if pose_name == 'flight':
        root = np.array([549.4, 281.0])
        far = []
        for p in kp['wing_poly']:
            q = (np.asarray(p) - root) * 0.92
            th = np.deg2rad(-14); R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
            far.append(tuple(R @ q + root))
        a = N_a.copy(); a[~poly_mask(N_img.shape, NW_mask)] = 0
        parts.append(('wing_far', N_img_c, a, NW_ctrl, far, 0.8, False))
        parts.append(('wing', N_img_c, a, NW_ctrl, kp['wing_poly'], 1.0, False))
    else:
        parts.append(('wing', img, masked(donor['wing']), donor['wing'], kp['wing_poly'], 1.0, False))
    # neck
    tw = target_neck_widths(sc)
    s_neck = list(donor['spine']) + tube_edges(donor['spine'], donor['spine_hw'])
    t_neck = list(kp['spine']) + tube_edges(kp['spine'], tw / 2)
    nmask = tube_mask(img.shape, donor['spine'], np.asarray(donor['spine_hw']) * 2)
    a = al.copy(); a[~nmask] = 0
    parts.append(('neck', img, a, s_neck, t_neck, 1.0, False))
    # head
    hc_src = donor['head_ctrl']; hc_tgt = kp['bill_poly']
    if len(hc_src) > len(hc_tgt): hc_src = hc_src[:len(hc_tgt)]
    parts.append(('head', img, masked(donor['head_mask']), hc_src, hc_tgt, 1.0, False))
    # near leg
    s_c, t_c = leg_ctrl(donor['leg_n'], [kp['hip_n'], kp['knee_n'], kp['foot_n']])
    parts.append(('leg_near', img, masked(mask_arr=leg_mask(img.shape, al, donor['leg_n'])), s_c, t_c, 1.0, pose_name != 'flight'))

    rep = {}
    for name, pim, pal, s_c2, t_c2, darken, clip in parts:
        res = warp_part(pim, pal, s_c2, t_c2)
        if res is None: continue
        x0, y0, out = res
        rgb, a = out[:, :, :3] * darken, out[:, :, 3] / 255.0
        a = cv2.GaussianBlur(a, (5, 5), 0)  # disclosed seam feather, part boundaries only in effect
        if clip:
            yy = np.arange(y0, y0 + a.shape[0])[:, None]
            a = a * (yy < WATER_Y)
        reg = canvas[y0:y0 + a.shape[0], x0:x0 + a.shape[1]]
        canvas[y0:y0 + a.shape[0], x0:x0 + a.shape[1]] = rgb * a[:, :, None] + reg * (1 - a[:, :, None])
        # upscale factor: warped alpha bbox vs donor mask bbox
        ys, xs = np.where(pal > 0.3)
        tys, txs = np.where(a > 0.05)
        if len(xs) and len(txs):
            rep[name] = round(float(np.sqrt(((txs.max()-txs.min()+1)*(tys.max()-tys.min()+1)) / ((xs.max()-xs.min()+1)*(ys.max()-ys.min()+1)))), 2)
    cv2.imwrite(f'{OUT}/master_{pose_name}.png', cv2.cvtColor(canvas.astype(np.uint8), cv2.COLOR_RGB2BGR))
    report[pose_name] = rep
    print(pose_name, 'done', rep)

for pn in ('rest', 'front', 'swallow', 'flight'):
    build(pn)
json.dump(report, open(f'{WORK}/upscale_report.json', 'w'), indent=1)
print('BUILD_DONE')
