"""Bird-completion geometry round (rig v2.3): shared harness.

Same certified protocol as every prior round: measure_v2.aligned_iou
(rot 0/+/-3/+/-6, scales 0.8-1.35, translation +/-24 step 6) of the
mask-stack union vs the approved rest mask. Two scores are carried
throughout: RAW IoU (the standing protocol number) and BIRD-ONLY IoU
(the same fitted placement, scenery band y>=558 excluded from both
masks -- Jimmy's steering number; the scenery is not bird and the rig
is forbidden to draw it).
"""
import copy, json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

HOME = os.path.expanduser('~')
ART2 = f'{HOME}/workspace/heron/art2'
FS = f'{ART2}/finished-art-stills'
RIGV2 = f'{FS}/rig-v2'
BP = f'{RIGV2}/body-placement'
OUT = f'{RIGV2}/geometry-round'
HA = f'{RIGV2}/head-anchor'
sys.path.insert(0, ART2)
sys.path.insert(0, f'{HOME}/workspace/heron/src13')
sys.path.insert(0, f'{FS}/refinish-corpus/work')
sys.path.insert(0, f'{RIGV2}/work')
import measure_v2 as MV
import roster_charts as RC
import maskrender_v2 as M2

W, H = 1024, 600
REST = np.asarray(Image.open(f'{RIGV2}/masks/approved_rest_mask.png')) > 0
SCEN_ROWS = 558  # scenery band: y >= 558 (verify_v22 convention)

def sil_stack(RR, pose):
    kpm = RR.kp_master(pose)
    scalars = dict(neck_w=float(pose['neck_w']), bulge_pos=float(pose['bulge_pos']),
                   bulge_amp=float(pose['bulge_amp']), px_per_unit=RR.U)
    stack = M2.build_mask_stack(kpm, scalars, (W, H))
    return np.any(stack > 0, axis=0), stack, kpm

def hold_pose(RRmod_tracks_pose):
    return copy.deepcopy(RRmod_tracks_pose)

def placed_mask(target, src, prm):
    Mc = ndimage.center_of_mass(target)
    S0 = ndimage.rotate(src.astype(float), prm['rot'], reshape=False, order=1) > 0.5
    sy, sx = np.nonzero(S0)
    crop = S0[sy.min():sy.max() + 1, sx.min():sx.max() + 1].astype(float)
    z = ndimage.zoom(crop, float(prm['scale']), order=1) > 0.5
    zh, zw = z.shape
    top = int(round(Mc[0] - zh / 2 + prm['dy'])); left = int(round(Mc[1] - zw / 2 + prm['dx']))
    canvas = np.zeros_like(target)
    ys0, ys1 = max(0, top), min(H, top + zh); xs0, xs1 = max(0, left), min(W, left + zw)
    canvas[ys0:ys1, xs0:xs1] = z[ys0 - top:ys1 - top, xs0 - left:xs1 - left]
    return canvas

def bird_iou_at_fit(sil, prm):
    placed = placed_mask(REST, sil, prm)
    bird = np.ones_like(REST); bird[SCEN_ROWS:, :] = False
    inter = int((REST & placed & bird).sum()); union = int(((REST | placed) & bird).sum())
    return float(inter / max(union, 1)), placed

def score(sil):
    """Full protocol: returns (raw_iou, fit_params, bird_iou, placed)."""
    raw, prm = MV.aligned_iou(REST, sil)
    bird, placed = bird_iou_at_fit(sil, prm)
    return float(raw), prm, bird, placed

# ---- decomposition (zones/channels, verbatim conventions of verify_v22)
def seg_dist(shape, a, b):
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]]
    a = np.asarray(a, float); b = np.asarray(b, float)
    d = b - a; L2 = float(d @ d)
    t = np.clip(((xx - a[0]) * d[0] + (yy - a[1]) * d[1]) / L2, 0, 1)
    return np.hypot(xx - (a[0] + t * d[0]), yy - (a[1] + t * d[1]))

def _zones():
    B = np.array([565.0, 221.0]); A = np.array([660.8, 53.3]); TIP = np.array([828.0, 63.0])
    yy, xx = np.mgrid[0:600, 0:1024]
    neck_zone = seg_dist(REST.shape, B, A) < 50
    head_zone = (np.hypot(xx - A[0], yy - A[1]) < 0.20 * 562.0) | (seg_dist(REST.shape, A, TIP) < 15)
    plume_a = np.load(f'{BP}/approved_plume_strands.npy')
    leg_a = np.load(f'{BP}/approved_leg_mask.npy')
    zones = {}
    zones['head'] = head_zone
    zones['neck'] = neck_zone & ~head_zone
    zones['legs'] = ndimage.binary_dilation(leg_a, iterations=8) & ~zones['head'] & ~zones['neck']
    zones['plume'] = ndimage.binary_dilation(plume_a, iterations=8) & ~zones['legs'] & ~zones['neck'] & ~zones['head']
    scen = np.zeros_like(REST); scen[SCEN_ROWS:, :] = True
    zones['scenery'] = scen & ~zones['legs'] & ~zones['plume'] & ~zones['neck'] & ~zones['head']
    used = np.zeros_like(REST)
    for z in zones.values():
        used |= z
    zones['torso_rest'] = ~used
    return zones

ZONES = _zones()
CH = ['torso', 'neck', 'head', 'wing', 'leg_near', 'leg_far', 'tail', 'plume']

def decompose(sil, stack, prm):
    placed = placed_mask(REST, sil, prm)
    pstack = np.stack([placed_mask(REST, stack[i] > 0, prm) for i in range(8)])
    miss = REST & ~placed; extra = placed & ~REST
    dz = {}
    for name, z in ZONES.items():
        dz[name] = dict(approved=int((REST & z).sum()), miss=int((miss & z).sum()),
                        extra=int((extra & z).sum()))
    dch = {}
    for i, nm in enumerate(CH):
        pm = pstack[i] > 0
        dch[nm] = dict(placed=int(pm.sum()), extra=int((pm & ~REST).sum()))
    bird = np.ones_like(REST); bird[SCEN_ROWS:, :] = False
    iou_bird = float(((REST & placed & bird).sum()) / max(((REST | placed) & bird).sum(), 1))
    return dict(total=dict(miss=int(miss.sum()), extra=int(extra.sum()),
                           inter=int((REST & placed).sum()), union=int((REST | placed).sum())),
                by_zone=dz, by_channel=dch, iou_excluding_scenery_band=round(iou_bird, 4),
                placed=placed)

def overlay(placed, path):
    img = np.ones((H, W, 3), np.uint8) * 255
    img[REST & placed] = (255, 200, 0)
    img[REST & ~placed] = (230, 40, 30)
    img[placed & ~REST] = (40, 90, 220)
    Image.fromarray(img).save(path)

# ---- body measures (measure_body2 instruments, as in verify_v22)
def body_measures(stack, sil, kpm, Href):
    Br = np.array(kpm['spine'][0], float)
    torso_ch = (stack[0] > 0) | (stack[3] > 0) | (stack[6] > 0)
    s = Href / 562.0
    core = torso_ch & (ndimage.distance_transform_edt(torso_ch) >= 13 * s)
    ys, xs = np.nonzero(core)
    out = {'torso_core_centroid_minus_breast_over_H':
           [round(float((xs.mean() - Br[0]) / Href), 4), round(float((ys.mean() - Br[1]) / Href), 4)]}
    y0, y1 = ys.min(), ys.max()
    bands = {}
    for i, (lo, hi) in enumerate(((0.0, 1 / 3), (1 / 3, 2 / 3), (2 / 3, 1.0))):
        m = core[int(y0 + lo * (y1 - y0)):int(y0 + hi * (y1 - y0)) + 1, :]
        bands[f'band{i}'] = round(float(m.sum() / core.sum()), 4)
    out['torso_core_row_bands'] = bands
    plume = stack[7] > 0
    pys, pxs = np.nonzero(plume)
    out['plume'] = dict(
        centroid_minus_breast_over_H=[round(float((pxs.mean() - Br[0]) / Href), 4),
                                      round(float((pys.mean() - Br[1]) / Href), 4)],
        drop_max_over_H=round(float((pys.max() - Br[1]) / Href), 4),
        drop_p95_over_H=round(float((np.percentile(pys, 95) - Br[1]) / Href), 4))
    return out
