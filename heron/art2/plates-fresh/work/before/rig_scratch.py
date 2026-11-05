"""Herons rig v2.5 — mechanism-first geometry (ITER2 build: denser torso re-trace + deepened coil; see iter2/ITER2_REPORT.md).

One animal definition (animal_v25.json): a 20-link neck chain with a fixed
arc budget, per-joint angle limits in two bend zones, a width profile from
the approved stills, and a head assembly (skull + bill + eye anchor) riding
the chain's distal end. Poses are heading-profile states of the chain.

Renders BARE MASKS (black silhouette on white, 1024x600) for the gate:
alert rest, deep coil, standing strike peak + peak overlay/side-by-side
against the approved strike still. Also prints DESIGN values (integrated
chain geometry, joint-limit usage, outline-crossing neckbase, visible
chords) — the gate verdict itself comes from an independent measurement
pass over the PNGs (see GATE_REPORT.md).
"""
import json, math
import numpy as np
if not hasattr(np, 'trapezoid'): np.trapezoid = np.trapz  # numpy<2 compat shim (pure rename, gate environment had numpy>=2)
from PIL import Image, ImageDraw
from scipy.interpolate import PchipInterpolator

HERE = '/home/hatch/workspace/heron/art2/plates-fresh/work/before'
ANIMAL = json.load(open(f'{HERE}/animal_v25.json'))
W_PX, H_PX = 1024, 600

# ------------------------------------------------------------ frame / torso
# Torso landmarks grounded on audubon_strike.png (visual grounding,
# 0-1000 -> px on the 1024x600 canvas). Torso = hull diameter over these
# four points (the study's definition).
LM = dict(tail=(119.8, 321.0), backtop=(443.4, 49.8),
          chest=(602.1, 214.8), belly=(456.7, 340.2))
TORSO_PX = max(math.hypot(a[0] - b[0], a[1] - b[1])
               for i, a in enumerate(LM.values()) for b in list(LM.values())[i + 1:])
T = TORSO_PX                      # px per torso unit
ROOT = np.array([598.0, 214.0])   # chain root = breast anchor, ON the torso
                                  # outline (chest point). First draft put it
                                  # 46 px deep inside the silhouette, which
                                  # made the canon visible arc unreachable by
                                  # construction; corrected before the gate.

# Torso outline loop (px), traced on the approved strike still.
# ITER2 RE-TRACE (53 pts, vs the gate's 15): back and belly extracted
# per-column from audubon_strike.png (topmost-bird / solid-core-bottom
# reads, debug-checked against the still), hand-cleaned. Back line rides
# the wing's top edge (peaks y=66 at the shoulder, NOT the gate trace's
# smoothed dome). Belly follows the STRUCTURAL underside: undertail and
# body core, two solid thigh-feathering dips (front dip bottom 328 keeps
# leg 1's traced hip (232,322) buried), plume-strand envelope excluded
# (plume is its own layer - PLUME LAW). Minimal smoothing (n_per=3).
TORSO_LOOP = [(125, 299), (140, 258), (150, 222), (157, 200), (172, 180),
              (195, 171), (220, 163), (245, 153), (268, 139), (290, 126),
              (315, 117), (340, 105), (365, 94), (390, 84), (415, 76),
              (440, 70), (465, 67), (490, 66), (512, 68), (532, 75),
              (550, 84), (568, 97), (582, 116), (593, 145), (601, 180),
              (605, 212), (596, 236), (580, 264), (556, 290), (530, 303),
              (512, 307), (485, 299), (455, 289), (425, 280), (395, 273),
              (365, 267), (335, 263), (305, 260), (278, 259), (258, 260),
              (248, 278), (242, 300), (236, 320), (230, 327), (222, 326),
              (215, 312), (208, 290), (200, 293), (196, 290), (192, 308),
              (188, 319), (181, 319), (175, 306), (168, 288),
              (160, 297), (150, 305), (138, 308)]

# Legs: (hip, knee, foot) px, traced on the strike still.
LEGS = [((232, 322), (224, 428), (236, 548)),
        ((296, 252), (300, 432), (288, 548))]
# Iter2 leg note: leg 2's traced top (292,326) was the point where the
# black leg emerges from the PLUME envelope; under the structural belly
# (y~260 there) it would float detached, so its top anchor moves up to
# the body core (296,252). Knee (300,432) and foot (288,548) unchanged -
# the stick still passes within ~5 px of the traced emergence point.
# Leg 1 is untouched: the front thigh dip (bottom 328) keeps its traced
# hip (232,322) buried.

# ------------------------------------------------------------ chain build
N = ANIMAL['neck_chain']['n_links']
ARC = ANIMAL['neck_chain']['arc_total']          # in torso units
_w = np.array([0.75 + 0.60 * math.sin(math.pi * (i + 0.5) / N) for i in range(N)])
SEG = ARC * _w / _w.sum()                        # segment lengths (torso units)
SEG_PX = SEG * T

# Joint limits (deg). One documented revision during construction, before
# any gate measurement: accumulated turning in the deepest measured coils
# is ~300-340 deg; with bends concentrated in the two zones the mid joints
# still carry ~18-22 deg in the reversals' tails, so the first-draft mid
# cap (16) made the canon coil unreachable by construction. Caps now:
# throat 26 / mid 20 / hinge 30 / distal 22. Poses are authored to <=90%.
LIMITS = np.array([26] * 6 + [20] * 6 + [30] * 5 + [22] * 2, dtype=float)  # joints 1..19

WP_U = np.array(ANIMAL['width_profile_rest']['u'])
WP_W = np.array(ANIMAL['width_profile_rest']['width'])
SL_U = np.array(ANIMAL['slimming_field_at_full_extension']['u'])
SL_M = np.array(ANIMAL['slimming_field_at_full_extension']['mult'])
width_rest = PchipInterpolator(WP_U, WP_W)
slim_mult = PchipInterpolator(SL_U, SL_M)


def build_chain(pose_name):
    spec = ANIMAL['poses'][pose_name]
    knots = np.array(spec['knots'], dtype=float)
    prof = PchipInterpolator(knots[:, 0], knots[:, 1])
    # segment heading = mean of profile over the segment (8 sub-samples)
    heads = []
    s_edges = np.concatenate([[0], np.cumsum(SEG) / ARC])
    for i in range(N):
        ss = np.linspace(s_edges[i], s_edges[i + 1], 9)
        heads.append(float(np.trapezoid(prof(ss), ss) / (ss[-1] - ss[0])))
    heads = np.array(heads)
    pts = [ROOT.copy()]
    for i in range(N):
        a = math.radians(heads[i])
        pts.append(pts[-1] + SEG_PX[i] * np.array([math.cos(a), math.sin(a)]))
    pts = np.array(pts)
    joints = np.array([((heads[i + 1] - heads[i] + 180) % 360) - 180
                       for i in range(N - 1)])
    return pts, heads, joints, spec


def point_in_poly(p, poly):
    x, y = p
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xin = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < xin:
                inside = not inside
    return inside


def dense_chain(pts, step=1.5):
    """Resample the chain polyline at ~step px."""
    out = [pts[0]]
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        L = np.hypot(*(b - a))
        n = max(int(L / step), 1)
        for k in range(1, n + 1):
            out.append(a + (b - a) * (k / n))
    return np.array(out)


def visible_chain(pts):
    """Chain from where the centreline exits the torso outline (neckbase)
    to the skull. Root starts inside the torso polygon."""
    dense = dense_chain(pts)
    torso = np.array(TORSO_LOOP, dtype=float)
    idx = None
    for i, p in enumerate(dense):
        if not point_in_poly(p, torso):
            idx = i
            break
    if idx is None:
        return dense, None
    if idx == 0:
        return dense, dense[0]
    return dense[idx - 1:], dense[idx - 1]


def pt_at_frac(chain, f):
    """Point at fraction f of the polyline length (chain order as given)."""
    seg = np.hypot(*np.diff(chain, axis=0).T)
    total = seg.sum()
    target = f * total
    acc = 0.0
    for i, L in enumerate(seg):
        if acc + L >= target:
            t = 0 if L == 0 else (target - acc) / L
            return chain[i] + t * (chain[i + 1] - chain[i])
        acc += L
    return chain[-1]


def design_values(pose_name):
    pts, heads, joints, spec = build_chain(pose_name)
    vis, neckbase = visible_chain(pts)
    skull = pts[-1]
    arc_vis = float(np.hypot(*np.diff(vis, axis=0).T).sum()) / T
    chain_from_skull = vis[::-1]
    s1 = pt_at_frac(chain_from_skull, 0.76)
    chord_base = float(np.hypot(*(skull - neckbase))) / T
    chord76 = float(np.hypot(*(skull - s1))) / T
    return dict(pose=pose_name, pts=pts, heads=heads, joints=joints,
                neckbase=neckbase, skull=skull, arc_vis=arc_vis,
                chord_base=chord_base, chord76=chord76,
                max_joint=float(np.abs(joints).max()),
                over_limit=[(int(i + 1), float(joints[i]), float(LIMITS[i]))
                            for i in range(N - 1) if abs(joints[i]) > LIMITS[i]])


# ------------------------------------------------------------ rendering
def catmull_rom(pts, n_per=10, closed=False):
    p = [np.asarray(q, float) for q in pts]
    if closed:
        p = [p[-1]] + p + [p[0], p[1]]
    else:
        p = [p[0]] + p + [p[-1]]
    out = []
    for i in range(len(p) - 3):
        p0, p1, p2, p3 = p[i:i + 4]
        t = np.linspace(0, 1, n_per)[:, None]
        seg = (0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t ** 2
                      + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
        out.append(seg[:-1] if i < len(p) - 4 else seg)
    return np.concatenate(out)


def tube_poly(dense, widths_px):
    d = np.gradient(dense, axis=0)
    n = np.hypot(d[:, 0], d[:, 1]); n[n == 0] = 1
    nrm = np.stack([-d[:, 1] / n, d[:, 0] / n], axis=1)
    w = np.asarray(widths_px)[:, None] / 2.0
    return np.concatenate([dense + nrm * w, (dense - nrm * w)[::-1]])


def render(pose_name):
    dv = design_values(pose_name)
    pts, spec = dv['pts'], ANIMAL['poses'][pose_name]
    img = Image.new('L', (W_PX, H_PX), 255)
    dr = ImageDraw.Draw(img)
    # torso
    loop = catmull_rom(TORSO_LOOP, n_per=3, closed=True)  # iter2: minimal smoothing
    dr.polygon([tuple(p) for p in loop], fill=0)
    # legs
    for hip, knee, foot in LEGS:
        for a, b, w0, w1 in ((hip, knee, 16, 11), (knee, foot, 7, 5)):
            a, b = np.array(a, float), np.array(b, float)
            d = b - a; d = d / max(np.hypot(*d), 1e-9)
            pp = np.array([-d[1], d[0]])
            dr.polygon([tuple(a + pp * w0 / 2), tuple(b + pp * w1 / 2),
                        tuple(b - pp * w1 / 2), tuple(a - pp * w0 / 2)], fill=0)
        for ang, ln in ((8, 26), (38, 20), (-52, 15)):
            a = math.radians(ang)
            tip = np.array(foot, float) + np.array([math.cos(a), math.sin(a) * 0.45]) * ln
            dr.line([tuple(foot), tuple(tip)], fill=0, width=3)
    # neck tube (full chain; the torso union covers the buried root)
    dense = dense_chain(pts)
    s_cum = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(dense, axis=0).T))])
    u = s_cum / s_cum[-1]
    widths = width_rest(np.clip(u, 0, 1)) * T
    if spec.get('slimming'):
        widths = widths * slim_mult(np.clip(u, 0, 1))
    dr.polygon([tuple(p) for p in tube_poly(dense, widths)], fill=0)
    # head assembly
    skull = pts[-1]
    final_head = dv['heads'][-1] + spec['head_pitch_offset_deg']
    a = math.radians(final_head)
    dvec = np.array([math.cos(a), math.sin(a)])
    perp = np.array([dvec[1], -dvec[0]])           # 'up' side of the bill line
    ha = ANIMAL['head_assembly']
    # skull ellipse
    ell = []
    for th in np.linspace(0, 2 * math.pi, 40):
        ell.append(skull + (dvec * math.cos(th) * ha['skull_semi_major'] * T
                            + np.array([-dvec[1], dvec[0]]) * math.sin(th)
                            * ha['skull_semi_minor'] * T))
    dr.polygon([tuple(p) for p in ell], fill=0)
    # occipital plume: thin swept spike behind the skull
    plume_tip = skull + (dvec * -0.115 + perp * -0.030) * T
    plume_b = skull + (dvec * -0.01 + perp * 0.018) * T
    plume_c = skull + (dvec * -0.03 + perp * -0.022) * T
    dr.polygon([tuple(plume_b), tuple(plume_tip), tuple(plume_c)], fill=0)
    # bill: tapered triangle
    base_c = skull + dvec * ha['bill_base_offset_from_skull_centre'] * T
    tip = skull + dvec * ha['bill_tip_reach_from_skull_centre'] * T
    bw = 0.0135 * T
    dr.polygon([tuple(base_c + perp * bw), tuple(tip), tuple(base_c - perp * bw)], fill=0)
    # eye anchor (geometry record; not drawn on the bare mask)
    eye = (skull + dvec * ha['eye_anchor_in_head_frame']['along_bill'] * T
           + perp * ha['eye_anchor_in_head_frame']['up'] * T)
    return img, dv, eye


def main():
    recs = {}
    for pose in ('alert', 'deep_coil', 'strike_peak'):
        img, dv, eye = render(pose)
        out = f'{HERE}/mask_{pose}.png'
        img.save(out)
        recs[pose] = (dv, eye)
        print(f"== {pose}: neckbase={np.round(dv['neckbase'], 1)} "
              f"skull={np.round(dv['skull'], 1)} eye={np.round(eye, 1)}")
        print(f"   design: chord_base={dv['chord_base']:.3f} chord76={dv['chord76']:.3f} "
              f"arc_vis={dv['arc_vis']:.3f} arc:chord={dv['arc_vis'] / dv['chord_base']:.2f} "
              f"max_joint={dv['max_joint']:.1f}deg over_limit={dv['over_limit']}")

if __name__ == '__main__':
    main()
