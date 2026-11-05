"""HERON parts-built ALERT plate (post-reset, design ART_DESIGN.md).

Builds the bird from its six parts, each under structural control, on the
mechanism's layout (rig_v25 geometry imported, never re-derived):
  torso  - silhouette locked to the mechanism 57-pt trace; engraved
           scalloped wing + slate body texture painted INSIDE it only
  neck   - the design's (u,v) station sheet mapped onto the alert chain
           by centreline correspondence (width profile from the mechanism)
  head   - one assembly in the head frame; eye PLACED at the anchor
  plume  - individual strand curves, fixed roots, hanging curtain
  legs   - corrected LEG_CANON traces; end AT the intertarsal joint;
           one ink ripple ring per leg at the joint; nothing below
  tail   - rigid with the torso (integral to the torso sheet)
No pre-reset image is an input. No whole-bird generation anywhere.
Deterministic: all randomness seeded.
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PKG = '/home/hatch/workspace/creature-engine/packages/great-blue-heron'
sys.path.insert(0, PKG)
import rig_v25 as R

OUT = '/home/hatch/workspace/heron/art2/plates-fresh/parts'
SS = 3                                   # supersample factor
W, H = 1024, 600
rng = np.random.RandomState(20261104)

# ---------------------------------------------------------------- palette
PAPER    = (239, 233, 216)
INK      = (0, 0, 0)
OUTLINE  = (30, 48, 74)
SLATE    = (105, 130, 155)
DARKSLATE= (66, 93, 122)
PALE     = (176, 203, 224)
ORANGE   = (240, 133, 36)
RUSTY    = (154, 82, 60)
LEG      = (74, 48, 36)
WHITE    = (252, 252, 248)

def blend(c, d, f):
    return tuple(int(round(c[i] + (d[i] - c[i]) * f)) for i in range(3))

DEEPWING   = blend(DARKSLATE, INK, 0.35)     # (43,60,79)  engraved shadow
MIDWING    = blend(DARKSLATE, INK, 0.18)     # (54,76,100)
SLATESHADOW= blend(SLATE, INK, 0.25)         # (79,98,116)
SLATELIGHT = blend(SLATE, WHITE, 0.30)
PALEDEEP   = blend(PALE, SLATE, 0.35)
PALELIGHT  = blend(PALE, WHITE, 0.30)
RUSTYDARK  = blend(RUSTY, INK, 0.30)         # (108,57,42)
LEGDEEP    = blend(LEG, INK, 0.35)
AMBER      = (240, 170, 40)

def S(p):    # native -> supersampled point
    return (p[0] * SS, p[1] * SS)
def layer():
    return Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))

def tapered_poly(pts, w0, w1):
    """Polygon of a tapering band along a polyline (native coords in/out SS)."""
    pts = [np.asarray(p, float) for p in pts]
    left, right = [], []
    n = len(pts)
    for i, p in enumerate(pts):
        if i == 0:   d = pts[1] - pts[0]
        elif i == n - 1: d = pts[-1] - pts[-2]
        else:        d = pts[i + 1] - pts[i - 1]
        L = max(np.hypot(*d), 1e-9); d = d / L
        nrm = np.array([-d[1], d[0]])
        w = (w0 + (w1 - w0) * (i / (n - 1))) / 2.0
        left.append(p + nrm * w); right.append(p - nrm * w)
    poly = left + right[::-1]
    return [S(p) for p in poly]

def curve(pts, steps=40):
    """Quadratic/cubic Bezier through control points (Catmull-Rom)."""
    return R.catmull_rom([np.asarray(p, float) for p in pts], n_per=max(steps // len(pts), 4))

# ---------------------------------------------------------------- geometry
T = R.T
dv = R.design_values('alert')
CHAIN = R.dense_chain(dv['pts'], step=1.5)          # full chain from ROOT
SKULL = dv['skull']
NECKBASE = dv['neckbase']
TORSO_SMOOTH = R.catmull_rom(R.TORSO_LOOP, n_per=3, closed=True)
LEGS = R.LEGS_BY_POSE['alert']                       # (hip, joint, foot)
WATER_Y = 382.0

def seg_exit(p_in, p_out):
    """First point on segment p_in->p_out outside the (smoothed) torso."""
    for f in np.linspace(0, 1, 400):
        p = p_in + (p_out - p_in) * f
        if not R.point_in_poly(p, TORSO_SMOOTH):
            return p
    return p_out

# ================================================================ LEGS
def build_leg(hip, joint, muted=False):
    hip, joint = np.array(hip, float), np.array(joint, float)
    E = seg_exit(hip, joint)                          # visible emergence
    d = joint - E; L = np.hypot(*d); d = d / L
    feather_end = E + d * (0.58 * L)
    lay = layer(); dr = ImageDraw.Draw(lay)
    rusty = blend(RUSTY, PAPER, 0.10) if muted else RUSTY
    rustyd = blend(RUSTYDARK, PAPER, 0.10) if muted else RUSTYDARK
    legc = blend(LEG, PAPER, 0.08) if muted else LEG
    # scaly shin first (under thigh tip): feather_end -> joint
    dr.polygon(tapered_poly([feather_end - d * 6, joint], 9.5, 6.5), fill=legc + (255,))
    # scale arcs across the shin
    n_sc = int((L * 0.42) / 5.0)
    for i in range(n_sc):
        c = feather_end + d * (i * 5.0)
        nrm = np.array([-d[1], d[0]])
        w = 4.6 - i * 0.06
        arc = [c + nrm * w * math.sin(a) + d * 2.2 * math.cos(a)
               for a in np.linspace(-1.2, 1.2, 9)]
        dr.line([S(p) for p in arc], fill=LEGDEEP + (200,), width=int(1.1 * SS))
    # feathered thigh: E -> feather_end (+ skirt stub above E, torso covers it)
    dr.polygon(tapered_poly([E - d * 14, feather_end + d * 4], 16.5, 10.0), fill=rusty + (255,))
    # thigh feather scallops
    n_th = int((0.58 * L + 14) / 7.0)
    for i in range(n_th):
        c = E - d * 10 + d * (i * 7.0)
        nrm = np.array([-d[1], d[0]])
        w = 7.6 - i * 0.22
        arc = [c + nrm * w * math.sin(a) + d * 3.0 * math.cos(a)
               for a in np.linspace(-1.25, 1.25, 9)]
        dr.line([S(p) for p in arc], fill=rustyd + (170,), width=int(1.2 * SS))
    # knuckle at the joint
    dr.ellipse([S(joint - (6, 4)), S(joint + (6, 4))], fill=LEGDEEP + (255,))
    return lay, E, feather_end

# ================================================================ NECK
def build_neck():
    dense = CHAIN
    seg = np.hypot(*np.diff(dense, axis=0).T)
    s_cum = np.concatenate([[0], np.cumsum(seg)])
    u_all = s_cum / s_cum[-1]
    widths = R.width_rest(np.clip(u_all, 0, 1)) * T
    d = np.gradient(dense, axis=0)
    n = np.hypot(d[:, 0], d[:, 1]); n[n == 0] = 1
    nrm = np.stack([-d[:, 1] / n, d[:, 0] / n], axis=1)   # rig convention
    # dorsal side = -nrm (assert crown-side at the tip via head perp)
    ha = R.ANIMAL['poses']['alert']['head_pitch_offset_deg']
    fh = math.radians(dv['heads'][-1] + ha)
    perp_up = np.array([math.sin(fh), -math.cos(fh)])
    dorsal_sign = -1.0
    if np.dot(-nrm[-1], perp_up) < 0:
        dorsal_sign = 1.0
    # v: -1 dorsal .. +1 ventral(front/pale)
    def edge(v):
        return dense + (nrm * dorsal_sign * -v) * (widths / 2.0)[:, None]
    lay = layer(); dr = ImageDraw.Draw(lay)
    # cross-section zone bands (dorsal -> ventral)
    zones = [(-1.00, -0.55, SLATESHADOW), (-0.55, -0.15, SLATE),
             (-0.15,  0.25, blend(SLATE, PALE, 0.45)),
             ( 0.25,  0.65, PALE), (0.65, 1.00, PALELIGHT)]
    for v0, v1, col in zones:
        poly = np.concatenate([edge(v0), edge(v1)[::-1]])
        dr.polygon([S(p) for p in poly], fill=col + (255,))
    # hatch: constant-v lines running along the tube
    for v in (-0.86, -0.62, -0.38, -0.14, 0.10, 0.34, 0.58, 0.80):
        pts = edge(v)
        dr.line([S(p) for p in pts[::2]], fill=OUTLINE + (70,), width=int(0.8 * SS))
    # cross ticks (broken bands at constant u) - engraved segmentation
    for i in range(6, len(dense) - 4, 5):
        v_lo, v_hi = (-0.92, 0.1) if (i // 5) % 2 == 0 else (-0.1, 0.92)
        a = dense[i] + nrm[i] * dorsal_sign * -v_lo * widths[i] / 2
        b = dense[i] + nrm[i] * dorsal_sign * -v_hi * widths[i] / 2
        dr.line([S(a), S(b)], fill=OUTLINE + (52,), width=int(0.7 * SS))
    # foreneck centre streak: broken dark dashes near the front-centre
    v_streak = 0.52
    pts = edge(v_streak)
    for i in range(10, len(pts) - 12, 7):
        a, b = pts[i], pts[i + 3]
        dr.line([S(a), S(b)], fill=OUTLINE + (150,), width=int(1.1 * SS))
    # dorsal stipple
    for _ in range(260):
        i = rng.randint(4, len(dense) - 4)
        v = rng.uniform(-0.95, -0.15)
        p = dense[i] + nrm[i] * dorsal_sign * -v * widths[i] / 2
        r = rng.uniform(0.5, 1.1)
        dr.ellipse([S(p - r), S(p + r)], fill=OUTLINE + (60,))
    # outline both edges
    for v in (-1.0, 1.0):
        dr.line([S(p) for p in edge(v)[::2]], fill=OUTLINE + (210,), width=int(1.2 * SS))
    return lay, dict(u=u_all, widths=widths)

def build_neck_sheet():
    """The flat (u,v) sheet - the rig's future texture source (record copy)."""
    img = Image.new('RGB', (720, 220), PAPER)
    dr = ImageDraw.Draw(img, 'RGBA')
    zones = [(0.00, 0.225, SLATESHADOW), (0.225, 0.425, SLATE),
             (0.425, 0.625, blend(SLATE, PALE, 0.45)),
             (0.625, 0.825, PALE), (0.825, 1.00, PALELIGHT)]
    for f0, f1, col in zones:   # f: 0 = dorsal(top) .. 1 = ventral(bottom)
        dr.rectangle([0, f0 * 220, 720, f1 * 220], fill=col)
    for f in (0.07, 0.19, 0.31, 0.43, 0.55, 0.67, 0.79, 0.90):
        dr.line([(0, f * 220), (720, f * 220)], fill=OUTLINE + (70,), width=1)
    for x in range(14, 720, 26):
        f0, f1 = (0.04, 0.54) if (x // 26) % 2 == 0 else (0.46, 0.96)
        dr.line([(x, f0 * 220), (x, f1 * 220)], fill=OUTLINE + (52,), width=1)
    for x in range(20, 700, 34):   # foreneck streak column (ventral-centre)
        dr.line([(x, 0.735 * 220), (x + 12, 0.735 * 220)], fill=OUTLINE + (150,), width=2)
    r2 = np.random.RandomState(7)
    for _ in range(500):
        x, y = r2.uniform(0, 720), r2.uniform(0, 90)
        dr.ellipse([x - 1, y - 1, x + 1, y + 1], fill=OUTLINE + (60,))
    return img

# ================================================================ TORSO (+tail)
def build_torso():
    lay = layer(); dr = ImageDraw.Draw(lay)
    poly = [S(p) for p in TORSO_SMOOTH]
    dr.polygon(poly, fill=SLATE + (255,))
    # ---- wing region: torso above the dividing curve
    div = [(606, 226), (520, 246), (420, 256), (300, 260), (200, 268), (128, 292)]
    wing_mask = Image.new('L', (W * SS, H * SS), 0)
    wm = ImageDraw.Draw(wing_mask)
    wm.polygon(poly, fill=255)
    under = [S(p) for p in div] + [(128 * SS, H * SS), (606 * SS, H * SS)]
    wm.polygon(under, fill=0)
    wing = layer(); wd = ImageDraw.Draw(wing)
    wd.polygon(poly, fill=DEEPWING + (255,))
    # scalloped feather rows
    shades = [DEEPWING, MIDWING, blend(DARKSLATE, INK, 0.28), MIDWING]
    row = 0
    y = 62.0
    while y < 268:
        r = 12.5
        off = (row % 2) * r
        x = 118.0 + off
        k = 0
        while x < 618:
            col = shades[(row + k) % len(shades)]
            wd.ellipse([S((x - r, y - r * 0.78)), S((x + r, y + r * 0.78))], fill=col + (255,))
            wd.arc([S((x - r, y - r * 0.78)), S((x + r, y + r * 0.78))],
                   start=300, end=240, fill=OUTLINE + (190,), width=int(1.3 * SS))
            wd.arc([S((x - r * 0.66, y - r * 0.5)), S((x + r * 0.66, y + r * 0.5))],
                   start=300, end=240, fill=OUTLINE + (90,), width=int(0.8 * SS))
            x += 2 * r; k += 1
        y += 13.5; row += 1
    # long flight feathers sweeping to the tail (rear third)
    for i, (x0, y0, x1, y1, wdt) in enumerate([
            (360, 128, 168, 268, 15), (385, 152, 185, 282, 14),
            (405, 178, 205, 292, 13), (420, 205, 232, 298, 12),
            (330, 108, 155, 250, 13)]):
        pts = curve([(x0, y0), ((x0 + x1) / 2, (y0 + y1) / 2 - 12), (x1, y1)], steps=24)
        wd.polygon(tapered_poly(pts, wdt, 2.5), fill=blend(DARKSLATE, INK, 0.22) + (255,))
        wd.line([S(p) for p in pts], fill=OUTLINE + (160,), width=int(1.0 * SS))
    wing.putalpha(Image.composite(wing.getchannel('A'), Image.new('L', (W * SS, H * SS), 0), wing_mask))
    lay.alpha_composite(wing)
    # wing trailing edge line
    dr.line([S(p) for p in curve(div, steps=60)], fill=OUTLINE + (200,), width=int(1.4 * SS))
    # ---- belly / chest feather hatch (below the wing)
    belly = layer(); bd = ImageDraw.Draw(belly)
    for gx in range(140, 610, 7):
        for gy in range(238, 330, 6):
            if R.point_in_poly((gx, gy), TORSO_SMOOTH) and gy > (250 + (gx - 140) * 0.03):
                ln = rng.uniform(4.5, 8.0)
                bd.line([S((gx, gy)), S((gx + ln * 0.30, gy + ln))],
                        fill=SLATESHADOW + (110,), width=int(0.9 * SS))
    lay.alpha_composite(belly)
    # chest-front pale fringe ticks
    for gy in range(196, 300, 6):
        gx = 596 - (gy - 196) * 0.22
        bd2 = ImageDraw.Draw(lay)
        bd2.line([S((gx, gy)), S((gx + 5, gy + 6))], fill=PALEDEEP + (130,), width=int(1.0 * SS))
    # tail feather separations at the rear tip
    for (x0, y0, x1, y1) in [(150, 262, 128, 292), (168, 248, 138, 282), (190, 240, 152, 272)]:
        dr.line([S(p) for p in curve([(x0, y0), ((x0 + x1) / 2 + 4, (y0 + y1) / 2), (x1, y1)], steps=16)],
                fill=OUTLINE + (170,), width=int(1.2 * SS))
    # silhouette outline
    dr.line(poly + [poly[0]], fill=OUTLINE + (225,), width=int(1.5 * SS), joint='curve')
    return lay

# ================================================================ HEAD
def build_head():
    lay = layer(); dr = ImageDraw.Draw(lay)
    ha = R.ANIMAL['head_assembly']
    fh = math.radians(dv['heads'][-1] + R.ANIMAL['poses']['alert']['head_pitch_offset_deg'])
    dvec = np.array([math.cos(fh), math.sin(fh)])
    up = np.array([dvec[1], -dvec[0]])
    def P(a, b):      # head-frame: a along bill, b up  -> plate point
        return SKULL + dvec * a + up * b
    smaj, smin = ha['skull_semi_major'] * T, ha['skull_semi_minor'] * T
    # skull (white face)
    ell = [P(smaj * math.cos(t), smin * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 60)]
    dr.polygon([S(p) for p in ell], fill=WHITE + (255,))
    # lower-skull pale shade
    shade = [P(smaj * math.cos(t), smin * math.sin(t)) for t in np.linspace(math.pi * 1.05, math.pi * 1.95, 30)]
    shade += [P(smaj * 0.55 * math.cos(t), smin * 0.55 * math.sin(t)) for t in np.linspace(math.pi * 1.95, math.pi * 1.05, 30)]
    dr.polygon([S(p) for p in shade], fill=PALEDEEP + (110,))
    # occipital plume strands (2, per the mechanism spike, trailing back-down)
    for tip, w0, ph in [((-57, -13), 2.6, 0.0), ((-48, -21), 2.2, 1.4)]:
        mid = (-30 + 3 * math.sin(ph), tip[1] * 0.35 + 2 * math.cos(ph))
        pts = curve([(-19, 1), mid, tip], steps=22)
        dr.polygon(tapered_poly([P(*q) for q in pts], w0, 0.4), fill=INK + (235,))
    # black brow band over the skull top
    outer = [P(smaj * math.cos(t), smin * math.sin(t)) for t in np.linspace(0.30, 2.75, 30)]
    inner = [P(smaj * 0.70 * math.cos(t), smin * 0.70 * math.sin(t) + 2.2) for t in np.linspace(2.75, 0.30, 30)]
    dr.polygon([S(p) for p in outer + inner], fill=INK + (255,))
    # lore patch (bill base -> eye)
    dr.polygon([S(p) for p in [P(19.5, -1.5), P(15.5, 5.0), P(9.0, 3.4)]], fill=INK + (220,))
    # bill: tapered dagger
    base_c = ha['bill_base_offset_from_skull_centre'] * T
    tip_d = ha['bill_tip_reach_from_skull_centre'] * T
    bw = 0.0135 * T
    bill = [P(base_c, bw), P(tip_d, 0), P(base_c, -bw)]
    dr.polygon([S(p) for p in bill], fill=ORANGE + (255,))
    dr.line([S(P(base_c, -bw * 0.25)), S(P(tip_d - 6, -0.4))], fill=blend(ORANGE, INK, 0.35) + (200,), width=int(1.0 * SS))
    dr.line([S(P(base_c, bw)), S(P(tip_d, 0))], fill=OUTLINE + (200,), width=int(1.1 * SS))
    dr.line([S(P(base_c, -bw)), S(P(tip_d, 0))], fill=OUTLINE + (160,), width=int(1.0 * SS))
    # the EYE - placed structure at the mechanism anchor
    ea = ha['eye_anchor_in_head_frame']
    eye = P(ea['along_bill'] * T, ea['up'] * T)
    r_iris, r_pupil = 3.6, 1.9
    dr.ellipse([S(eye - r_iris - 0.9), S(eye + r_iris + 0.9)], fill=OUTLINE + (255,))
    dr.ellipse([S(eye - r_iris), S(eye + r_iris)], fill=AMBER + (255,))
    dr.ellipse([S(eye - r_pupil), S(eye + r_pupil)], fill=INK + (255,))
    dr.ellipse([S(eye + (-1.6, -1.6) - 0.8), S(eye + (-1.6, -1.6) + 0.8)], fill=WHITE + (255,))
    # skull outline
    dr.line([S(p) for p in ell] + [S(ell[0])], fill=OUTLINE + (200,), width=int(1.2 * SS))
    return lay, eye

# ================================================================ PLUME
def build_plume():
    lay = layer(); dr = ImageDraw.Draw(lay)
    # roots: (a) along the neck's lower-front, (b) along the chest front edge
    roots = []
    dense = CHAIN
    seg = np.hypot(*np.diff(dense, axis=0).T)
    s_cum = np.concatenate([[0], np.cumsum(seg)]); u_all = s_cum / s_cum[-1]
    widths = R.width_rest(np.clip(u_all, 0, 1)) * T
    d = np.gradient(dense, axis=0); n = np.hypot(d[:, 0], d[:, 1]); n[n == 0] = 1
    nrm = np.stack([-d[:, 1] / n, d[:, 0] / n], axis=1)
    for f in (0.05, 0.09, 0.13, 0.17):
        i = int(np.argmin(np.abs(u_all - f)))
        # ventral edge point (front side = +nrm at the root reach)
        roots.append(dense[i] + nrm[i] * (widths[i] / 2 - 2))
    for k in range(9):
        f = k / 8.0
        roots.append(np.array([612 - 46 * f - 6 * math.sin(f * math.pi), 236 + 74 * f]))
    strands = []
    for i, r0 in enumerate(roots):
        back = i % 3 == 2
        L = rng.uniform(58, 118) * (0.82 if back else 1.0)
        drift = rng.uniform(-13, 3)
        bow = rng.uniform(-7, 7)
        mid = r0 + np.array([drift * 0.4 + bow, L * 0.52])
        tip = r0 + np.array([drift, L])
        pts = curve([r0, mid, tip], steps=26)
        strands.append((pts, back, rng.uniform(2.0, 3.1)))
    # back row first (slate), then front row (pale), each with a darker under-stroke
    for pts, back, w0 in strands:
        if not back: continue
        dr.polygon(tapered_poly([p + (1.1, 1.1) for p in pts], w0, 0.4), fill=SLATESHADOW + (200,))
        dr.polygon(tapered_poly(pts, w0, 0.4), fill=SLATE + (235,))
    for pts, back, w0 in strands:
        if back: continue
        dr.polygon(tapered_poly([p + (1.1, 1.1) for p in pts], w0, 0.4), fill=PALEDEEP + (200,))
        dr.polygon(tapered_poly(pts, w0, 0.4), fill=blend(PALE, WHITE, 0.12) + (240,))
    return lay, len(strands)

# ================================================================ RIPPLES
def build_ripples():
    lay = layer(); dr = ImageDraw.Draw(lay)
    for hip, joint, foot in LEGS:
        cx, cy = joint[0], WATER_Y
        for rx, ry, a in [(17, 3.8, 235), (27, 6.2, 190)]:
            dr.ellipse([S((cx - rx, cy - ry)), S((cx + rx, cy + ry))], outline=INK + (a,), width=int(1.6 * SS))
        # two small broken outer arcs
        for (cxo, rrx, rry, st, en) in [(-30, 9, 2.2, 200, 320), (31, 10, 2.4, 220, 340)]:
            dr.arc([S((cx + cxo - rrx, cy - rry)), S((cx + cxo + rrx, cy + rry))],
                   start=st, end=en, fill=INK + (150,), width=int(1.3 * SS))
    return lay

# ================================================================ ASSEMBLE
def main():
    canvas = Image.new('RGBA', (W * SS, H * SS), PAPER + (255,))
    leg_far, E_far, _ = build_leg(*LEGS[1][:2], muted=True)
    leg_near, E_near, _ = build_leg(*LEGS[0][:2], muted=False)
    neck, neck_info = build_neck()
    torso = build_torso()
    head, eye_pt = build_head()
    plume, n_strands = build_plume()
    ripples = build_ripples()
    for part in (leg_far, leg_near, neck, torso):
        canvas.alpha_composite(part)
    # thigh skirts over the belly edge at each emergence (seam softening)
    dr = ImageDraw.Draw(canvas)
    for E, hip in [(E_near, LEGS[0][0]), (E_far, LEGS[1][0])]:
        for k in range(6):
            x = E[0] - 7 + k * 2.8
            pts = curve([(x, E[1] - 3), (x - 1.5, E[1] + 7), (x - 3.5, E[1] + 13)], steps=10)
            dr.line([S(p) for p in pts], fill=RUSTYDARK + (150,), width=int(1.3 * SS))
    # shoulder patch: ink cap over the neck root / chest junction
    nb = NECKBASE
    patch_c = nb + np.array([-13, 7])
    angs = np.linspace(0, 2 * math.pi, 40)
    patch = [(patch_c[0] + 21 * math.cos(a) * 1.0 - 6 * math.sin(a),
              patch_c[1] + 12.5 * math.sin(a)) for a in angs]
    dr.polygon([S(p) for p in patch], fill=INK + (255,))
    for a in np.linspace(0.3, 2.6, 7):     # patch feather fringe
        p0 = (patch_c[0] + 19 * math.cos(a), patch_c[1] + 11 * math.sin(a))
        p1 = (p0[0] - 3, p0[1] + 7)
        dr.line([S(p0), S(p1)], fill=INK + (180,), width=int(1.2 * SS))
    canvas.alpha_composite(head)
    canvas.alpha_composite(plume)
    canvas.alpha_composite(ripples)
    final = canvas.convert('RGB').resize((W, H), Image.LANCZOS)
    final.save(f'{OUT}/alert_parts_plate.png')
    # part sheets (plate coordinates, on paper)
    for name, part in [('torso', torso), ('neck', neck), ('head', head),
                       ('plume', plume)]:
        bg = Image.new('RGBA', (W * SS, H * SS), PAPER + (255,))
        bg.alpha_composite(part)
        bg.convert('RGB').resize((W, H), Image.LANCZOS).save(f'{OUT}/parts/{name}.png')
    legs_bg = Image.new('RGBA', (W * SS, H * SS), PAPER + (255,))
    legs_bg.alpha_composite(leg_far); legs_bg.alpha_composite(leg_near); legs_bg.alpha_composite(ripples)
    legs_bg.convert('RGB').resize((W, H), Image.LANCZOS).save(f'{OUT}/parts/legs.png')
    build_neck_sheet().save(f'{OUT}/parts/neck_uv_sheet.png')
    # side-by-side vs the mechanism mask
    mask = Image.open(f'{OUT}/work/mask_alert.png').convert('RGB')
    sbs = Image.new('RGB', (W * 2, H), PAPER)
    sbs.paste(final, (0, 0)); sbs.paste(mask, (W, 0))
    sbs.save(f'{OUT}/sidebyside/plate_vs_mask.png')
    # bookkeeping for the report
    info = dict(T=float(T), neckbase=NECKBASE.tolist(), skull=SKULL.tolist(),
                eye_built=eye_pt.tolist(), eye_anchor=[754.7, 35.7],
                emergence_near=E_near.tolist(), emergence_far=E_far.tolist(),
                plume_strands=n_strands, chord_base_design=float(dv['chord_base']),
                arc_vis=float(dv['arc_vis']))
    json.dump(info, open(f'{OUT}/work/build_info.json', 'w'), indent=1)
    print(json.dumps(info, indent=1))

if __name__ == '__main__':
    main()
