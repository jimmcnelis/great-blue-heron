"""Heron rig v1.3 r4 — fine-art naturalist surface pass on the r3 rig.

r4 changes (Jimmy 2026-11-02: "bulges a little too much — it's a fish
not a ball"; "the bottom feathers look like drawn triangles"; "make
the art better"; "more like a fine art drawing, less like cartoon —
turn that dial"). Pose geometry, choreography and timings are FROZEN
from r3; only the drawn surface moves:
  - swallow bulge: spherical Gaussian lump -> an elongated fish
    profile (blunt leading/head end, long tail taper) riding the same
    solved UPRIGHT neck; peak width multiplier 2.44x -> ~1.76x.
  - plumage: every triangular fringe primitive replaced by layered
    individual feathers (curved shaft, rounded soft tip, irregular
    lengths, barb suggestion) — breast beard restored as a shaggy
    layered plume mass, belly skirt, tail fan, front hem, shoulder
    tips, thigh feathering.
  - fine-art modeling: hatched tonal modeling (lit back / shadowed
    belly / nape hatch), tone-matched internal separations instead of
    hard cartoon outlines, scallop "petals" rebuilt as real covert
    feathers with shafts and barbs, subtly irregular hand-drawn
    contour on the torso/wing loops.

Design space 120x90 (x right, y down, bird faces +x). WATER_Y=74 (surface
just below the intertarsal joint), foot plant BOTTOM=88 (under the blank:
planted legs are clipped at the waterline, a stepping leg emerges whole).
Master render 1024x600, SS=3, majority downsample to a palette-index grid.
"""
import numpy as np
from PIL import Image, ImageDraw

# ------------------------------------------------------------------ palette
WHITE, INK, OUTLINE, SLATE, DARKSLATE, PALE, ORANGE, RUSTY, LEGC, \
    FISH, FISH2, FISHBELLY, DEEP, LIGHT, BLACK, CREAM, FARUSTY, GOLD = range(18)
PALETTE = np.array([
    (255, 255, 255),   # 0 WHITE (scene blank)
    (0, 0, 0),         # 1 INK (caused water marks only)
    (26, 42, 66),      # 2 OUTLINE
    (100, 126, 152),   # 3 SLATE (C body)
    (62, 88, 118),     # 4 DARKSLATE
    (172, 200, 222),   # 5 PALE (neck/face light, plume strands)
    (240, 133, 36),    # 6 ORANGE (bill)
    (150, 80, 58),     # 7 RUSTY (thighs, shoulder speck)
    (70, 46, 34),      # 8 LEGC (bare stilt)
    (150, 163, 105),   # 9 FISH
    (94, 110, 66),     # 10 FISH2
    (216, 222, 182),   # 11 FISHBELLY
    (42, 62, 88),      # 12 DEEP (darkest feather row / flight feathers)
    (138, 162, 184),   # 13 LIGHT (light scallop tone)
    (14, 18, 26),      # 14 BLACK (shoulder patch, brow)
    (243, 240, 230),   # 15 CREAM (face white, distinct from scene blank)
    (120, 60, 42),     # 16 FARUSTY (far thigh, darker)
    (232, 181, 44),    # 17 GOLD (eye glint ring accent, naturalist eye)
], dtype=np.uint8)
NPAL = len(PALETTE)

W_PX, H_PX = 1024, 600
SS = 3
DS_W, DS_H = 120.0, 90.0
SCALE = W_PX / DS_W            # 8.533 px per design unit at master
WATER_Y = 74.0
BOTTOM = 88.0
HIP_Y = 47.0
GIRTH = 0.88   # r3: torso girth scale (1.0 = r2). Length axis unscaled.

def X(x): return x * SCALE * SS
def Y(y): return y * (H_PX / DS_H) * SS
SY = H_PX / DS_H               # 6.667 px per unit vertical
# NOTE: design space is anisotropic at master (8.533 x 6.667 px/unit) --
# the frame is 1024x600 = 1.707 aspect vs design 1.333. Compensate by
# mapping design through a uniform scale and centering: use U = 600/90.
U = H_PX / DS_H                # uniform px per unit = 6.667
XOFF = (W_PX - DS_W * U) / 2.0  # letterbox the design space, centered
def X(x): return (XOFF + x * U) * SS
def Y(y): return y * U * SS

# ------------------------------------------------------------------ helpers
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

def bez(p0, p1, p2, p3, n=24):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = [np.asarray(q, float) for q in (p0, p1, p2, p3)]
    return ((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 +
            3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3)

def rot(pts, c, deg):
    a = np.deg2rad(deg)
    R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    c = np.asarray(c, float)
    return [tuple(c + R @ (np.asarray(p, float) - c)) for p in pts]

def rot1(p, c, deg):
    return rot([p], c, deg)[0]

class Canvas:
    """Palette-index canvas at supersample; majority downsample at end."""
    def __init__(self):
        self.img = Image.new('L', (W_PX * SS, H_PX * SS), WHITE)
        self.dr = ImageDraw.Draw(self.img)

    def poly(self, pts, fill, outline=None, ow=0.55):
        q = [(X(float(p[0])), Y(float(p[1]))) for p in pts]
        self.dr.polygon(q, fill=int(fill),
                        outline=int(outline) if outline is not None else None,
                        width=max(1, int(ow * U * SS)))

    def line(self, pts, fill, w=0.4):
        q = [(X(float(p[0])), Y(float(p[1]))) for p in pts]
        self.dr.line(q, fill=int(fill), width=max(1, int(w * U * SS)), joint='curve')

    def disc(self, c, r, fill, outline=None, ow=0.3):
        self.dr.ellipse([X(c[0] - r), Y(c[1] - r * U / U), X(c[0] + r), Y(c[1] + r)],
                        fill=int(fill), outline=int(outline) if outline is not None else None,
                        width=max(1, int(ow * U * SS)))

    def grid(self):
        a = np.asarray(self.img, dtype=np.int64)
        h, w = H_PX, W_PX
        blocks = a.reshape(h, SS, w, SS).transpose(0, 2, 1, 3).reshape(h, w, SS * SS)
        off = (np.arange(h * w) * NPAL)[:, None]
        counts = np.bincount((blocks + off).ravel(), minlength=h * w * NPAL)
        return counts.reshape(h * w, NPAL).argmax(1).reshape(h, w).astype(np.uint8)

    def clip_below(self, y_units, keep_mask_img=None):
        """Blank everything below y_units (the implied water plane)."""
        row = int(Y(y_units))
        self.dr.rectangle([0, row, W_PX * SS, H_PX * SS], fill=WHITE)

    def blit_masked(self, other, mask_pts):
        m = Image.new('L', self.img.size, 0)
        md = ImageDraw.Draw(m)
        md.polygon([(X(float(p[0])), Y(float(p[1]))) for p in mask_pts], fill=255)
        self.img.paste(other.img, (0, 0), m)
        self.dr = ImageDraw.Draw(self.img)

def tapered_strand(cv, base, dirv, length, w0, fill, bend=0.35, n=7):
    """A single plume/feather strand: tapered curved sliver."""
    b = np.asarray(base, float); d = np.asarray(dirv, float)
    d = d / max(np.hypot(*d), 1e-9)
    perp = np.array([-d[1], d[0]])
    spine = []
    for i in range(n + 1):
        t = i / n
        spine.append(b + d * (length * t) + perp * (bend * length * t * t))
    spine = np.array(spine)
    wdt = (w0 * (1 - np.linspace(0, 1, n + 1)) ** 0.8)[:, None]
    left = spine + perp * wdt / 2
    right = (spine - perp * wdt / 2)[::-1]
    cv.poly(np.concatenate([left, right]), fill, outline=None)

# ------------------------------------------------------------------ r4:
# fine-art feather system. One feather = a curved shaft carrying an
# asymmetric vane: near-zero width at the base, fullest just past the
# middle, closing to a ROUNDED soft tip — never a triangle. Lengths and
# widths are jittered deterministically (seeded by index) so a drawn
# row is irregular like a real feather bed but identical frame to frame.
def _jit(i, salt=0.0):
    v = np.sin(i * 127.1 + salt * 311.7) * 43758.5453
    return float(v - np.floor(v))

def feather_pts(c, dirv, L, W, bend=0.22, asym=0.22, n=9):
    b = np.asarray(c, float); d = np.asarray(dirv, float)
    d = d / max(np.hypot(*d), 1e-9)
    perp = np.array([-d[1], d[0]])
    ts = np.linspace(0, 1, n + 1)
    shaft = np.array([b + d * (L * t) + perp * (bend * L * t * t) for t in ts])
    prof = np.sin(np.pi * (0.10 + 0.90 * ts)) ** 0.75     # 0 at base, round tip
    prof[-1] = 0.055
    half = (W / 2.0) * prof
    left = shaft + perp * (half * (1 + asym))[:, None]
    right = shaft - perp * (half * (1 - asym))[:, None]
    return np.concatenate([left, right[::-1]]), shaft, d, perp

def draw_feather(cv, c, dirv, L, W, fill, outline=None, ow=0.26,
                 shaft_tone=None, barbs=0, barb_tone=None, bend=0.22,
                 asym=0.22):
    poly, shaft, d, perp = feather_pts(c, dirv, L, W, bend=bend, asym=asym)
    cv.poly(poly, fill, outline=outline, ow=ow)
    if shaft_tone is not None:
        cv.line([tuple(p) for p in shaft[1:-1:2]], shaft_tone, w=0.20)
    if barbs and barb_tone is not None:
        for k in range(1, barbs + 1):
            t = 0.30 + 0.52 * k / (barbs + 0.5)
            i = min(int(t * (len(shaft) - 1)), len(shaft) - 2)
            p0 = shaft[i]
            for sgn in (1, -1):
                tip = p0 - d * (L * 0.16) + perp * sgn * (W * 0.30)
                cv.line([tuple(p0), tuple(tip)], barb_tone, w=0.16)

def fringe(cv, anchors_dirs, L0, W0, tones, bend=0.22, seed=0,
           shaft_tone=None, barbs=0, barb_tone=None, outline=None,
           embed=0.0):
    """A row of overlapping individual feathers along (anchor, dir)
    pairs, lengths/widths irregular by index — a feather-bed hem, not
    a zigzag. Drawn in the order given. embed>0 pulls each anchor back
    along its own direction so the feather bodies merge with the mass
    behind and only their rounded tips break the edge line — plumage
    reads as a ragged hem, never as separate paddles on stalks."""
    for j, (a, dv) in enumerate(anchors_dirs):
        L = L0 * (0.86 + 0.30 * _jit(j, seed))
        W = W0 * (0.88 + 0.24 * _jit(j, seed + 7))
        tone = tones[j % len(tones)]
        a = np.asarray(a, float); dv = np.asarray(dv, float)
        if embed:
            a = a - dv / max(np.hypot(*dv), 1e-9) * embed
        draw_feather(cv, a, dv, L, W, tone, outline=outline,
                     shaft_tone=shaft_tone,
                     barbs=barbs if (j % 2 == 0) else 0,
                     barb_tone=barb_tone, bend=bend * (0.8 + 0.5 * _jit(j, seed + 13)))

def _wdir(xf, c, dv):
    """Local (anchor, direction) -> world (anchor, direction) through a
    body transform: direction by finite difference."""
    a = np.array(xf(c), float)
    b = np.array(xf((c[0] + dv[0], c[1] + dv[1])), float)
    return tuple(a), tuple(b - a)

def _rough(pts, amp=0.10, seed=3):
    """Subtle hand-drawn irregularity on a closed loop's sample points:
    deterministic per index, tiny amplitude — the contour stops being
    a perfect spline without moving the pose."""
    p = np.asarray(pts, float)
    if len(p) < 8:
        return pts
    d = np.gradient(p, axis=0)
    n = np.hypot(d[:, 0], d[:, 1]); n[n == 0] = 1
    nrm = np.stack([-d[:, 1] / n, d[:, 0] / n], axis=1)
    off = np.array([(_jit(i, seed) - 0.5) * 2 * amp for i in range(len(p))])
    k = np.array([0.25, 0.5, 0.25])
    off = np.convolve(np.concatenate([off[-1:], off, off[:1]]), k, 'valid')
    return p + nrm * off[:, None]

# ------------------------------------------------------------------ pose
def default_pose():
    return dict(
        root_x=30.0, root_y=0.0, body_tilt=16.0,   # tail-up diagonal
        hx=19.0, hy=-28.0,            # head anchor rel. to hip pivot (world = root + this)
        coil=0.85,                    # neck S depth (1 deep coil, 0 straight)
        neck_w=1.0,                   # neck width scale (narrows at full extension)
        head_pitch=4.0, head_roll=0.0, gape=0.0, blink=0.0,
        bulge_pos=0.0, bulge_amp=0.0,
        plume_sway=0.0,
        yaw=0.0,
        wing_mode='folded', flap=0.0, flap_tip=0.0, wing_amt=0.0,
        leg_near=dict(fx=6.0, fy=BOTTOM, toe=0.0),
        leg_far=dict(fx=-5.0, fy=BOTTOM, toe=0.0),
        tail_fan=0.0, smear=0.0,
        fish_mode='none', fish_grip=0.35, fish_orient=90.0,
        fish_pos=None, fish_ang=0.0, fish_size=1.0,
    )

# Torso outline, body-local frame: origin at hip pivot, +x toward breast.
# One continuous loop: tail wedge -> back -> shoulder -> breast -> keel ->
# belly -> tail underside. The folded wing lives INSIDE this loop's rear.
TORSO = [
         (-23, -0.5), (-16.5, -1), (-9, -5.6), (-1, -7.4),
         (7, -7.8), (12.5, -4.6), (15.4, -1), (14.8, 8.8),
         (11, 12.8), (1.6, 9), (-4, 9.8), (-11, 5.8),
         (-17, 4.4)]
# Wing region (body-local), the folded wing mass inset on the torso.
WING = [
         (-15.8, -3.6), (-8.5, -2.2), (-0.5, -2.6), (6, -1.4),
         (10.2, -2.4), (8.6, 1.2), (2.5, 4.2), (-5.5, 5),
         (-12, 3.6), (-16.2, 0.4)]
BREAST_LOCAL = (14.0, 1.8)     # neck base anchor in body frame
                               # rig-v2: attachment moved forward/up on
                               # the torso per the approved drawing (was
                               # (12.5, 3.2)); the anchor is rig anatomy,
                               # not chart data
HIP_NEAR = (2, 2.6)
HIP_FAR = (1.5, 2.8)    # rig-v2.2 body-placement round: far-leg IK base
                               # moved +3.0 local x (measured: the far leg's
                               # silhouette exit sat ~0.10 H too far back/low
                               # relative to its foot after the breast-pivot
                               # rotation; HIP_NEAR unchanged)

# Yaw stop adjustments: (torso x-scale about pivot, y-scale, neck-base dx,
# head variant, leg spread factor, side bulge)
YAW_STOPS = {
    0:   dict(wx=1.00, wy=1.00, ndx=0.0, head='profile', spread=1.0, bulge=0.0),
    45:  dict(wx=0.80, wy=1.04, ndx=-3.5, head='tq', spread=0.72, bulge=0.5),
    90:  dict(wx=0.52, wy=1.10, ndx=-11.5, head='front', spread=0.34, bulge=1.0),
    135: dict(wx=0.80, wy=1.04, ndx=-3.5, head='tq', spread=0.72, bulge=0.5),
    180: dict(wx=1.00, wy=1.00, ndx=0.0, head='profile', spread=1.0, bulge=0.0),
}

def body_xform(pose):
    """Return function mapping body-local -> world design coords."""
    piv = np.array([pose['root_x'], HIP_Y + pose['root_y']])
    tilt = pose['body_tilt']
    st = YAW_STOPS[int(round(pose['yaw']))] if pose['yaw'] in YAW_STOPS else None

    def base_xf(p):
        q = np.asarray(p, float).copy()
        if st is not None and int(round(pose['yaw'])) != 90:
            q[0] *= st['wx']; q[1] *= st['wy']
        # r3 leanness (Jimmy 2026-11-02: "leaner, not longer"): girth only.
        # Profile/three-quarter: scale local Y (the girth axis) about the
        # hip pivot; local X (length) untouched. Front stop: girth reads
        # as width, so scale local X there instead.
        if int(round(pose['yaw'])) == 90:
            q[0] *= GIRTH
        else:
            q[1] *= GIRTH
        # rig-v2 proportion rebuild (approved-bird spec, 2026-11-03):
        # body length x1.62 about local x=-2, body depth x1.45. Applies
        # to every body-local element (torso, wing, breast, hips) so the
        # drawn bird carries the approved drawing's proportions; pose
        # trajectories (charts) are untouched.
        q[0] = -2.0 + (q[0] + 2.0) * 1.62
        q[1] = q[1] * 1.45
        return tuple(rot1(q, (0, 0), -tilt) + piv)

    # rig-v2.2 (body-placement round, 2026-11-03): optional rigid
    # rotation of ALL body-local outputs about the transformed BREAST
    # point, pose-gated by 'body_rot_b' (degrees, default 0 = v2.1
    # behaviour). The breast is the neck's lower endpoint and the head
    # anchor is root-relative, so this placement move cannot move
    # either neck endpoint: the v2.1 neck settlement is invariant
    # under it. Feet are pose-absolute and likewise unmoved; hips
    # ride with the body and the legs re-IK.
    th = float(pose.get('body_rot_b', 0.0))
    if th:
        if int(round(pose['yaw'])) == 90:
            bl = (0.0, -5.0)
        else:
            bl = (BREAST_LOCAL[0] + (st['ndx'] if st else 0.0), BREAST_LOCAL[1])
        bp = np.array(base_xf(bl))

        def xf(p):
            return tuple(rot1(np.asarray(base_xf(p), float), bp, th))
        return xf, piv
    return base_xf, piv

# Front stop gets its own authored torso: NARROW and tall, per the clip-01
# front frames — a front heron is ~40% of its profile width: shoulders
# tucked, max breadth at the folded-wing sides, belly tapering below.
FRONT_TORSO = [(-2.6, -8.8), (2.6, -8.8), (5.2, -6.0), (6.6, -2.0),
               (7.2, 1.5), (6.3, 5.0), (4.2, 8.0), (0.0, 9.2),
               (-4.2, 8.0), (-6.3, 5.0), (-7.2, 1.5), (-6.6, -2.0),
               (-5.2, -6.0)]

def torso_loop(pose, xf):
    if int(round(pose['yaw'])) == 90:
        pts = [(p[0], p[1] * 1.12) for p in FRONT_TORSO]
        return _rough(catmull_rom([xf(p) for p in pts], n_per=8, closed=True),
                      amp=0.09, seed=5)
    pts = [xf(p) for p in TORSO]
    return _rough(catmull_rom(pts, n_per=8, closed=True), amp=0.10, seed=3)


# ------------------------------------------------------------------ builders
def tube(cv, spine, widths, fill, outline=None, ow=0.5):
    sp = np.asarray(spine, float)
    d = np.gradient(sp, axis=0)
    n = np.hypot(d[:, 0], d[:, 1]); n[n == 0] = 1
    nrm = np.stack([-d[:, 1] / n, d[:, 0] / n], axis=1)
    w = np.asarray(widths, float)[:, None] / 2.0
    poly = np.concatenate([sp + nrm * w, (sp - nrm * w)[::-1]])
    cv.poly(poly, fill, outline=outline, ow=ow)
    return sp + nrm * w, sp - nrm * w   # throat(+n side), nape

# rig-v2.1 (head-anchor branch, 2026-11-03): neck-curve control
# points are placed in the breast->head CHORD frame: T = fraction
# along the chord, K = perpendicular offset toward the nape side
# as a fraction of chord length (K scaled by coil/0.85, so the fit
# is exact at the hold's coil 0.85 and proportional elsewhere).
# Fitted so the hold neck traces the approved bird's measured
# centreline at its measured length (Jimmy's long-neck ruling:
# the length is species truth, held, not traded away). The v2
# world-frame offsets could only make length by bowing deep
# backward; the approved neck makes its length by rising steeply
# and bending forward, which needs the chord frame. Everything
# else in this file is rig13_r4_v2 verbatim.
NECK_T1, NECK_K1 = 0.53, 0.364
NECK_T2, NECK_K2 = 0.395, -0.805

def neck_spine(pose, breast):
    H = np.array([pose['root_x'] + pose['hx'], HIP_Y + pose['root_y'] + pose['hy']])
    B = np.asarray(breast, float)
    coil = pose['coil']
    d = H - B
    L = max(float(np.hypot(*d)), 1e-9)
    ua = d / L
    va = np.array([-ua[1], ua[0]])
    ks = coil / 0.85
    p1 = B + ua * (NECK_T1 * L) + va * (NECK_K1 * L * ks)
    p2 = H - ua * (NECK_T2 * L) + va * (NECK_K2 * L * ks)
    spine = bez(B, p1, p2, H, n=30)
    return spine, H

def _fish_profile(ds):
    """Swallowed-fish cross-section along the neck axis. ds = s - pos,
    +ds toward the body (the fish's leading/head end). Head end: blunt
    and full, rounding off over 0.20. Tail end: a long thinning taper
    over 0.36. Elongated mass, NOT a sphere (Jimmy r4: "it's a fish
    not a ball"). Returns 0..1, peak 1.0 at ds=0 (the fish's front
    third, its widest point)."""
    ds = np.asarray(ds, float)
    out = np.zeros_like(ds)
    head = ds >= 0
    x = np.clip(ds[head] / 0.20, 0, 1)
    out[head] = (1 - x * x) ** 0.55
    x = np.clip(-ds[~head] / 0.36, 0, 1)
    out[~head] = (1 - x) ** 1.35
    return out

def draw_neck(cv, pose, breast, style):
    spine, H = neck_spine(pose, breast)
    t = np.linspace(0, 1, len(spine))
    wscale = pose.get('neck_w', 1.0)
    widths = (6.4 - 3.0 * t) * wscale
    prof = None
    if pose['bulge_amp'] > 0.01:
        s = 1.0 - t
        prof = _fish_profile(s - pose['bulge_pos'])
        widths = widths * (1.0 + pose['bulge_amp'] * 0.95 * prof)
    base = OUTLINE if style != 'silhouette' else None
    throat, nape = tube(cv, spine, widths, INK if style == 'silhouette' else SLATE,
                        outline=base, ow=0.5 if style == 'naturalist' else 0.8)
    if style == 'silhouette':
        return throat, spine, H
    # two-tone: lighter throat band (C's pale front neck)
    d = np.gradient(spine, axis=0)
    n = np.hypot(d[:, 0], d[:, 1]); n[n == 0] = 1
    nrm = np.stack([-d[:, 1] / n, d[:, 0] / n], axis=1)
    band_c = spine + nrm * (widths * 0.16)[:, None]
    tube(cv, band_c, widths * 0.60, LIGHT, outline=None)
    if pose['bulge_amp'] > 0.15:
        # the travelling FISH must read at FULL frame, not just in
        # crops: silhouette widening (above) + a shadowed slice riding
        # the fish's profile and a pale cap on the nape side. The slice
        # now follows the fish profile (core where prof >= 0.75, halo
        # where >= 0.40) so the shading is as elongated as the shape.
        s_arr = 1.0 - t
        m2 = prof >= 0.40
        m1 = prof >= 0.75
        if m1.sum() >= 3:
            tube(cv, band_c[m2], widths[m2] * 0.62, SLATE, outline=None)
            core = DARKSLATE if pose['bulge_amp'] > 0.5 else SLATE
            tube(cv, band_c[m1], widths[m1] * 0.62, core, outline=None)
            cap_c = spine[m1] - nrm[m1] * (widths[m1] * 0.18)[:, None]
            tube(cv, cap_c, widths[m1] * 0.55, PALE, outline=None)
    if style == 'naturalist':
        # fine-art neck modeling: the throat side carries the light in
        # two long drawn lines following the curve; the nape side is
        # modeled with dense fine hatching angled along the feather
        # flow — tonal drawing, not a flat tube with a band.
        for off, tone, wln in ((0.34, LIGHT, 0.22), (0.58, PALE, 0.18)):
            pts = spine[3:-3] + nrm[3:-3] * (widths[3:-3] * off)[:, None]
            cv.line([tuple(p) for p in pts], tone, w=wln)
        tang0 = np.gradient(spine, axis=0)
        tn0 = np.hypot(tang0[:, 0], tang0[:, 1]); tn0[tn0 == 0] = 1
        tang0 = tang0 / tn0[:, None]
        for i in range(3, len(spine) - 3, 2):
            edge = spine[i] - nrm[i] * widths[i] * 0.46
            tip = edge + nrm[i] * widths[i] * 0.34 + tang0[i] * 0.9
            cv.line([tuple(edge), tuple(tip)], DARKSLATE, w=0.20)
    if style == 'naturalist':
        # nape hatch strokes lie INSIDE the silhouette, along the edge
        tang = np.gradient(spine, axis=0)
        tn = np.hypot(tang[:, 0], tang[:, 1]); tn[tn == 0] = 1
        tang = tang / tn[:, None]
        for i in range(4, len(spine) - 3, 3):
            p = nape[i] + (spine[i] - nape[i]) * 0.45
            cv.line([p, p + tang[i] * 1.7 + (spine[i] - nape[i]) * 0.2], DARKSLATE, w=0.30)
        for i, tt in enumerate(np.linspace(0.55, 0.8, 4)):
            k = int(tt * (len(spine) - 1))
            p = spine[k] + nrm[k] * widths[k] * 0.30
            tone = [INK, CREAM, RUSTY, INK][i]
            cv.line([p, p + np.array([0.2, 1.7])], tone, w=0.30)
    # ---- plume beard along the throat/breast edge (centre-front at yaw 90)
    front = YAW_STOPS.get(int(round(pose['yaw'])), {}).get('head') == 'front'
    anchor_src = spine if front else throat
    sway = np.deg2rad(pose['plume_sway'])
    rotm = np.array([[np.cos(sway), -np.sin(sway)], [np.sin(sway), np.cos(sway)]])
    ts = np.linspace(0.02, 0.60, 26)
    if style == 'storybook':
        # the beard as a union of FAT flat strands: the naturalist mane's
        # own construction restyled — few, wide, one pale tone. Their
        # overlap is the shaped mass; their tips are the ragged hem.
        # (Three offset-polygon attempts collapsed into ribbons: the
        # throat runs nearly parallel to any downward offset, so a band
        # between throat and tips-line has ~zero width. Strands cannot
        # fold, and their union is the mass.)
        for j, tt in enumerate(ts):
            if j % 3:
                continue
            k = tt * (len(spine) - 1)
            i0, fr = int(k), k - int(k)
            p0 = anchor_src[min(i0 + 1, len(anchor_src) - 1)] * fr + anchor_src[i0] * (1 - fr)
            ln = 6.5 + 11.5 * np.sin(np.pi * j / (len(ts) - 1)) ** 0.8
            if front:
                ln *= 0.75
                fan = (j - (len(ts) - 1) / 2) * 0.09
                dv = rotm @ np.array([fan, 1.0])
            elif pose['wing_mode'] == 'flight':
                dv = rotm @ np.array([-0.85, 0.42]); ln *= 0.8
            else:
                dv = rotm @ np.array([0.6, 1.0])
            tapered_strand(cv, p0 + np.array([0.0 if front else 0.5, 0.2]),
                           dv, ln, 2.6, PALE, bend=0.30)
    else:
        # the BEARD (naturalist): the great blue heron's shaggy breast
        # plumes — a layered mass of individual feathers, longest mid-
        # throat, irregular lengths, three depth layers (dark behind,
        # pale in front), each feather a curved vane with a shaft, not
        # a 0.6-wide sliver. Silhouette keeps the plain strand read.
        for j, tt in enumerate(ts):
            k = tt * (len(spine) - 1)
            i0, fr = int(k), k - int(k)
            p = anchor_src[min(i0 + 1, len(anchor_src) - 1)] * fr + anchor_src[i0] * (1 - fr)
            ln = 5.5 + 8.5 * np.sin(np.pi * j / (len(ts) - 1)) ** 0.8
            if front:
                ln *= 0.75
            fan = (j - (len(ts) - 1) / 2) * 0.05 if front else 0.75
            if pose['wing_mode'] == 'flight':
                dv = rotm @ np.array([-0.85, 0.42]); ln *= 0.8
            else:
                dv = rotm @ np.array([fan, 1.0])
            if style == 'naturalist':
                # per-feather direction jitter: a real plume bed never
                # hangs in parallel icicles
                ja = np.deg2rad((_jit(j, 37) - 0.5) * 11.0)
                dv = np.array(rot1(tuple(dv), (0, 0), np.rad2deg(ja)))
            if style == 'silhouette':
                tapered_strand(cv, p, dv, ln, 0.6, INK, bend=0.30)
            elif style == 'naturalist':
                sh = 0.84 + 0.34 * _jit(j, 31)          # irregular length
                # back layer: shorter, darker, wider — the mass behind
                draw_feather(cv, p + np.array([-0.4, -0.5]), dv,
                             ln * 0.78 * sh, 1.55, DARKSLATE if j % 2 else SLATE,
                             bend=0.30)
                # front layer: the visible shaggy plumes, pale, shafted
                draw_feather(cv, p, dv, ln * sh, 1.30,
                             PALE if j % 3 else LIGHT,
                             shaft_tone=LIGHT if j % 3 else SLATE,
                             barbs=2 if j % 2 == 0 else 0, barb_tone=SLATE,
                             bend=0.30)
            else:
                tapered_strand(cv, p, dv, ln, 0.6, LIGHT, bend=0.30)
    return throat, spine, H

BILL_LEN = 11.8   # rig-v2: bill shortened as skull grows (was 13.8)
HINGE = (3.3, 0.15)
HEAD_S = 1.45   # rig-v2: skull scale up from 1.22 per approved-bird spec;
                # head->bill-tip stays at the spec ratio (~0.30 H)

def head_group(pose):
    H = np.array([pose['root_x'] + pose['hx'], HIP_Y + pose['root_y'] + pose['hy']])
    return H, pose['head_pitch']

def bill_tip(pose):
    H, pitch = head_group(pose)
    tip_local = ((HINGE[0] + BILL_LEN) * HEAD_S, 0.75 * HEAD_S)
    return np.array(rot1(tip_local, (0, 0), pitch)) + H

def draw_head(cv, pose, style):
    H, pitch = head_group(pose)
    st = YAW_STOPS.get(int(round(pose['yaw'])), YAW_STOPS[0])
    variant = st['head']
    sil = style == 'silhouette'
    fillc = INK if sil else None

    def W(p):  # head-local -> world
        return tuple(np.array(rot1(p, (0, 0), pitch)) + H)

    if variant == 'front':
        skull = [(-3.4, -2.2), (0, -3.3), (3.4, -2.2), (3.9, 0.4),
                 (2.3, 2.7), (-2.3, 2.7), (-3.9, 0.4)]
        cv.poly([W(p) for p in catmull_rom(skull, n_per=6, closed=True)],
                fillc or CREAM, outline=None if sil else OUTLINE, ow=0.5)
        cap = [(-3.4, -2.2), (0, -3.3), (3.4, -2.2), (3.0, -1.0), (0, -1.7), (-3.0, -1.0)]
        cv.poly([W(p) for p in cap], fillc or BLACK, outline=None)
        for sx in (-1, 1):
            for ln, wd in ((6.8, 0.34), (5.4, 0.28)):
                tapered_strand(cv, W((sx * 3.2, -1.9)), (sx * 1.0, -0.30), ln, wd,
                               fillc or BLACK, bend=-0.25)
            e = W((sx * 1.75, -0.55))
            if sil:
                continue
            if style == 'naturalist':
                cv.disc(e, 0.92, PALE, outline=OUTLINE, ow=0.25)
                cv.disc(e, 0.5, INK)
                cv.disc((e[0] + 0.18, e[1] - 0.18), 0.16, WHITE)
            else:
                cv.disc(e, 0.78, INK)
                cv.disc((e[0] + 0.2, e[1] - 0.2), 0.17, WHITE)
        # foreshortened bill: wedge toward the viewer, gape splits it
        g = pose['gape'] * 1.1
        bill = [(-1.05, 0.7), (1.05, 0.7), (0.5 + g, 5.4), (-0.5 - g, 5.4)]
        cv.poly([W(p) for p in bill], fillc or ORANGE, outline=None if sil else OUTLINE, ow=0.45)
        return
    # profile / three-quarter
    xs = 0.74 if variant == 'tq' else 1.0

    def L(p):
        return (p[0] * xs * HEAD_S, p[1] * HEAD_S)

    skull = [(-4, -1.1), (-3.5, -1.15), (-0.6, -2.7), (2.1, -2.3), (3.6, -0.9), (3.9, 0.5), (2.1, 2.35), (-0.8, 2.9), (-3.1, 1.5)]
    cv.poly([W(L(p)) for p in catmull_rom(skull, n_per=6, closed=True)],
            fillc or SLATE, outline=None if sil else OUTLINE,
            ow=0.5 if style == 'naturalist' else 0.8)
    face = [(0.1, -2.05), (2.1, -2.3), (3.6, -0.9), (3.9, 0.5), (2.1, 1.9),
            (-0.7, 1.7), (-0.5, -0.5)]
    cv.poly([W(L(p)) for p in face], fillc or CREAM, outline=None)
    brow = [(-0.7, -2.3), (2.1, -2.35), (3.55, -1.15), (2.3, -0.95), (0.1, -1.25)]
    cv.poly([W(L(p)) for p in brow], fillc or BLACK, outline=None)
    nape_w = [(-4.6, -1.1), (-3.5, -2.8), (-0.9, -2.5), (-1.9, -0.7), (-4.3, 0.4)]
    cv.poly([W(L(p)) for p in nape_w], fillc or BLACK, outline=None)
    # plumes sweeping back from behind the eye
    pb = W(L((-4.1, -1.7)))
    if style == 'storybook':
        tapered_strand(cv, pb, (-1.0, -0.16), 8.2, 0.62, fillc or BLACK, bend=-0.22)
        tapered_strand(cv, pb, (-1.0, 0.10), 6.0, 0.4, fillc or BLACK, bend=-0.1)
    elif style == 'naturalist':
        # occipital plumes as narrow real feathers, irregular lengths
        for m, (dv, ln, wd) in enumerate((((-1.0, -0.30), 8.8, 0.52),
                                          ((-1.0, -0.04), 7.2, 0.46),
                                          ((-1.0, 0.20), 5.6, 0.40))):
            draw_feather(cv, pb, dv, ln * (0.9 + 0.2 * _jit(m, 41)), wd,
                         fillc or BLACK, shaft_tone=None, bend=-0.2, asym=0.3)
    else:
        for dv, ln, wd in (((-1.0, -0.30), 8.6, 0.30), ((-1.0, -0.04), 7.4, 0.27),
                           ((-1.0, 0.20), 5.8, 0.24)):
            tapered_strand(cv, pb, dv, ln, wd, fillc or BLACK, bend=-0.2)
    if style == 'naturalist' and not sil:
        # drawn modeling on the skull: fine strokes following the cap
        # curve and the cheek — observed feather direction, not decals
        for a, b in (((-3.3, -2.2), (-0.9, -2.75)), ((-0.6, -2.8), (1.7, -2.15)),
                     ((-3.9, -0.6), (-2.2, 0.9)), ((-1.6, 1.9), (0.6, 2.15))):
            cv.line([W(L(a)), W(L(b))], DARKSLATE, w=0.20)
    if variant == 'tq' and not sil:
        cv.disc(W((-1.3, -0.75)), 0.42, INK)   # far eye hint
    # eye
    e = W(L((1.55, -0.92)))
    if not sil:
        if pose['blink'] > 0.5:
            cv.line([W(L((0.7, -0.85))), W(L((2.4, -0.8)))], OUTLINE, w=0.35)
        elif style == 'naturalist':
            cv.disc(e, 0.95, PALE, outline=OUTLINE, ow=0.25)
            cv.disc(e, 0.52, INK)
            cv.disc((e[0] + 0.2, e[1] - 0.2), 0.17, WHITE)
        else:
            cv.disc(e, 0.8, INK)
            cv.disc((e[0] + 0.22, e[1] - 0.22), 0.18, WHITE)
    # bill: upper mandible (head frame), lower hinged by gape
    up = [(2.5, -1.55), (HINGE[0] + BILL_LEN, 0.5), (3.25, 0.8)]
    cv.poly([W(L(p)) for p in up], fillc or ORANGE, outline=None if sil else OUTLINE,
            ow=0.45 if style == 'naturalist' else 0.7)
    low = [(3.25, 0.8), (HINGE[0] + BILL_LEN - 0.7, 0.95), (3.45, 1.55)]
    low = rot(low, HINGE, pose['gape'] * 15.0)
    cv.poly([W(L(p)) for p in low], fillc or ORANGE, outline=None if sil else OUTLINE, ow=0.4)
    if style == 'naturalist' and not sil:
        cv.line([W(L((3.1, -0.85))), W(L((HINGE[0] + BILL_LEN - 1.2, 0.32)))], RUSTY, w=0.3)
        cv.line([W(L((4.3, -0.55))), W(L((6.4, -0.28)))], OUTLINE, w=0.25)

def leg_ik(hip, foot, l1=20.4, l2=19.2):   # rig-v2 segment ratio per spec (was 21.5/17.5)
    hip = np.asarray(hip, float); foot = np.asarray(foot, float)
    d = foot - hip
    dist = min(np.hypot(*d), l1 + l2 - 0.01)
    a = (l1 ** 2 - l2 ** 2 + dist ** 2) / (2 * dist)
    h = np.sqrt(max(l1 ** 2 - a ** 2, 0.0))
    mid = hip + d * (a / max(np.hypot(*d), 1e-9))
    perp = np.array([-d[1], d[0]]) / max(np.hypot(*d), 1e-9)
    j1 = mid + perp * h
    j2 = mid - perp * h
    return j1 if j1[0] < j2[0] else j2   # joint = rearmost point

def draw_leg(cv, pose, leg, hip_local, xf, rusty_tone, style):
    st = YAW_STOPS.get(int(round(pose['yaw'])), YAW_STOPS[0])
    hip = np.array(xf(hip_local))
    foot = np.array([pose['root_x'] + leg['fx'] * st['spread'], leg['fy']])
    sil = style == 'silhouette'
    if leg['fx'] < -18:
        # trailing flight leg: two near-straight tapered segments, no IK bow
        d = foot - hip; L = np.hypot(*d); d = d / max(L, 1e-9)
        perp = np.array([-d[1], d[0]])
        mid = hip + d * L * 0.52 + perp * 0.8
        for a_, b_, w0, w1, tone in ((hip, mid, 2.05, 0.95, rusty_tone),
                                     (mid, foot, 0.85, 0.44, LEGC)):
            dd = b_ - a_; nn = np.hypot(*dd); dd = dd / max(nn, 1e-9)
            pp = np.array([-dd[1], dd[0]])
            cv.poly([tuple(a_ + pp * w0 / 2), tuple(b_ + pp * w1 / 2),
                     tuple(b_ - pp * w1 / 2), tuple(a_ - pp * w0 / 2)],
                    INK if sil else tone, outline=None)
        tip = foot + d * 3.4
        cv.line([tuple(foot), tuple(tip)], INK if sil else LEGC, w=0.5)
        return foot
    joint = leg_ik(hip, foot)
    # feathered thigh: the outline is a smoothed filled path hip->joint
    # (front edge bellied like a real feathered thigh, top tucked into
    # the belly); in naturalist it carries scalloped feather line-work
    # — the rusty thigh is plumage, not a bare quad (r4 fine-art pass).
    d = joint - hip; n = np.hypot(*d); d = d / max(n, 1e-9)
    perp = np.array([-d[1], d[0]])
    w_top, w_bot = 2.9, 1.65
    a0 = hip - d * 3
    hw = lambda tt: (w_top + (w_bot - w_top) * tt) / 2
    thigh = [tuple(a0 + perp * w_top / 2),
             tuple(hip + d * n * 0.45 + perp * hw(0.45) * 1.05),
             tuple(joint + perp * w_bot / 2),
             tuple(joint - perp * w_bot / 2),
             tuple(hip + d * n * 0.45 - perp * hw(0.45) * 0.95),
             tuple(a0 - perp * w_top / 2)]
    thigh = [tuple(p) for p in catmull_rom(thigh, n_per=6, closed=True)]
    cv.poly(thigh, INK if sil else rusty_tone, outline=None if sil else OUTLINE, ow=0.45)
    if style == 'naturalist' and not sil:
        tick = FARUSTY if rusty_tone == RUSTY else OUTLINE
        for r in range(3):
            tt = 0.30 + 0.24 * r
            cen = hip + d * (n * tt)
            wid = (w_top + (w_bot - w_top) * tt) * 0.36
            arc = []
            for k in range(7):
                u = k / 6
                ang = np.pi * u
                arc.append(tuple(cen + perp * (wid * np.cos(ang)) * 1.0
                                 + d * (np.sin(ang) * 1.05 - 0.3 * r)))
            cv.line(arc, tick, w=0.20)
    # bare stilt: joint -> foot
    d2 = foot - joint; n2 = np.hypot(*d2); d2 = d2 / max(n2, 1e-9)
    perp2 = np.array([-d2[1], d2[0]])
    shin = [tuple(joint + perp2 * 0.47), tuple(foot + perp2 * 0.30),
            tuple(foot - perp2 * 0.30), tuple(joint - perp2 * 0.47)]
    cv.poly(shin, INK if sil else LEGC, outline=None)
    cv.disc(tuple(joint), 0.72, INK if sil else LEGC)
    # toes
    toe_ang = np.deg2rad(leg['toe'])
    for base_ang, ln in ((8, 3.6), (38, 2.9), (-52, 2.2)):
        a = np.deg2rad(base_ang) + toe_ang
        tip = foot + np.array([np.cos(a), np.sin(a)]) * ln * np.array([1, 0.45])
        cv.line([tuple(foot), tuple(tip)], INK if sil else LEGC, w=0.5)
    return foot

def draw_shoulder_patch(cv, xf, style):
    """Shoulder: rusty speck over the black patch, the patch shaped as a
    feather-flow wedge (long axis along the scallop rows) with a scalloped
    lower edge, feathered in by DEEP tips overlapping that edge — never a
    hard rectangle."""
    speck = [(5.7, -6.5), (9.4, -5.9), (9.0, -4.0), (5.5, -4.6)]
    sil = style == 'silhouette'
    cv.poly([xf(p) for p in speck], INK if sil else RUSTY, outline=None)
    upper = [(4.7, -5.4), (6.8, -5.9), (9.2, -5.0), (9.9, -3.8)]
    lower = [(9.3, -2.0), (8.0, -1.4), (7.2, -2.5), (6.0, -1.7),
             (5.1, -2.7), (4.4, -3.6)]
    patch = upper + lower
    # RAW polygon, no spline: at 5x4 units a Catmull-Rom melts the
    # scalloped lower edge into a round button; the steps must stay steps
    cv.poly([xf(p) for p in patch], INK if sil else BLACK, outline=None)
    if sil:
        return
    for cx, cy in ((8.6, -1.9), (7.0, -1.3), (5.5, -2.0)):
        wa, wd = _wdir(xf, (cx, cy), (0.3, 1.0))
        draw_feather(cv, wa, wd, 1.9, 1.5, DEEP, shaft_tone=DARKSLATE,
                     bend=0.12, asym=0.3)

def draw_wing_detail(cv, pose, xf, style):
    """Folded wing: inset mass + scallop rows + shoulder patch (body-local).
    Detail is drawn on a temp layer and clipped to the wing loop."""
    sil = style == 'silhouette'
    loop_pts = _rough(catmull_rom([xf(p) for p in WING], n_per=8, closed=True),
                      amp=0.09, seed=11)
    tmp = Canvas()
    tmp.poly(loop_pts, INK if sil else DARKSLATE,
             outline=None if sil else OUTLINE, ow=0.5 if style == 'naturalist' else 0.85)
    if sil:
        cv.blit_masked(tmp, loop_pts)
        return
    if style == 'naturalist':
        # covert rows as REAL feathers (r4): each old "petal" is now an
        # individual feather — curved shaft, rounded tip, tone-matched
        # separation, barb ticks — overlapping like a feather bed.
        rows = [(8, 5.6, 4.6, LIGHT), (8, 5.4, 4.4, SLATE),
                (7, 5.1, 4.2, DARKSLATE), (7, 4.8, 4.0, DEEP)]
        darker = {LIGHT: SLATE, SLATE: DARKSLATE, DARKSLATE: DEEP, DEEP: OUTLINE}
        for r, (count, pw, pl, tone) in enumerate(rows):
            y0 = -4.5 + r * 2.35
            for i in range(count):
                u = i / max(count - 1, 1)
                cx = -14.2 + u * 24.5 + r * 0.8
                cy = y0 + 1.15 * np.sin(u * np.pi * 0.72)
                ang = np.deg2rad(50 + 16 * u + r * 3)
                dv = np.array([np.cos(ang), np.sin(ang)])
                anch = np.array([cx, cy]) - dv * pl * 0.45
                wa, wd = _wdir(xf, tuple(anch), tuple(dv))
                draw_feather(tmp, wa, wd, pl * (0.9 + 0.2 * _jit(i + r * 20, 51)),
                             pw * 0.94, tone, outline=None,
                             shaft_tone=darker[tone],
                             barbs=2 if (i + r) % 2 == 0 else 0,
                             barb_tone=darker[tone], bend=0.16, asym=0.30)
    else:
        rows = [(5, 9.6, 3.9, SLATE), (5, 9.0, 3.6, DEEP)]
        for r, (count, pw, ph, tone) in enumerate(rows):
            y0 = -4.5 + r * 2.35
            for i in range(count):
                u = i / max(count - 1, 1)
                cx = -14.2 + u * 24.5 + r * 0.8
                cy = y0 + 1.15 * np.sin(u * np.pi * 0.72)
                ang = 5 + 30 * u + r * 3
                petal = [(cx - pw / 2, cy - ph * 0.34), (cx - pw * 0.16, cy - ph * 0.58),
                         (cx + pw * 0.30, cy - ph * 0.5), (cx + pw / 2, cy - ph * 0.05),
                         (cx + pw * 0.26, cy + ph * 0.4), (cx - pw * 0.14, cy + ph * 0.46),
                         (cx - pw * 0.44, cy + ph * 0.2)]
                petal = rot(petal, (cx, cy), ang)
                petal = [(cx + (px - cx) * (1 + 0.18 * u), py) for px, py in petal]
                tmp.poly([xf(p) for p in petal], tone, outline=None, ow=0.32)
    cv.blit_masked(tmp, loop_pts)
    # tail fan: layered individual tail feathers, slightly fanned
    if style == 'naturalist':
        for k, (dy, fang) in enumerate(((-2.2, 0.08), (-1.2, 0.15), (-0.2, 0.22),
                                        (0.8, 0.29), (1.8, 0.36), (2.7, 0.43))):
            wa, wd = _wdir(xf, (-16.6, dy), (-1.0, fang))
            draw_feather(cv, wa, wd, 3.6 - 0.45 * abs(k - 2.5) + 0.5 * _jit(k, 97),
                         2.8, DEEP, shaft_tone=None, bend=0.10, asym=0.3)
    else:
        for k, dy in enumerate((-1.5, 0.2, 1.8)):
            tapered_strand(cv, xf((-17.8, dy)), (-1.0, 0.28), 4.2 - k * 0.5, 2.3,
                           DARKSLATE, bend=0.15)
    # shoulder: rusty speck over the black patch (C), feathered into the rows
    draw_shoulder_patch(cv, xf, style)
    if style == 'naturalist':
        # belly fringe: overlapping feathers hanging off the torso's
        # lower edge — layered, irregular (replaces the 5 triangles)
        _belly = [(9.5, 7.6), (8.3, 8.1), (7.2, 8.5), (6.0, 8.8), (4.8, 9.1),
                  (3.6, 9.3), (2.4, 9.5), (1.2, 9.6), (0.0, 9.7), (-1.2, 9.7),
                  (-2.4, 9.7), (-3.6, 9.6), (-4.8, 9.5), (-6.0, 9.3),
                  (-7.2, 9.1), (-8.4, 8.8), (-9.6, 8.5), (-10.8, 8.1),
                  (-12.0, 7.7), (-13.1, 7.1), (-14.2, 6.5)]
        anch = []
        for i in range(len(_belly) - 1):
            anch.append(_belly[i])
            anch.append(((_belly[i][0] + _belly[i + 1][0]) / 2,
                         (_belly[i][1] + _belly[i + 1][1]) / 2))
        anch.append(_belly[-1])
        pairs = [_wdir(xf, a, (0.30 - 0.03 * i, 1.0)) for i, a in enumerate(anch)]
        fringe(cv, pairs, 2.2, 2.6, [DARKSLATE, DARKSLATE, SLATE], bend=0.08,
               seed=61, shaft_tone=None, embed=1.5)

def _wing_outline(flap, tip_lag, scale=1.0, extra_rot=0.0):
    """Closed outline of the flight wing, root at origin, design coords
    (x fwd, y down). Broad by construction — deep chord, fingered trailing
    edge — per the footage: clip-05's frontal braking fan (primaries
    splayed) and clip-06's mantled dome. LE runs root->wrist->tip; TE
    returns with primary notches, then the secondaries sweep home.
    tip_lag bends the hand (past the wrist) backward; flap + extra_rot
    rotate the whole wing about the root."""
    LE = [(2.6, 1.2), (1.6, -6.0), (0.2, -12.5), (-2.2, -17.5),
          (-4.6, -21.0), (-6.8, -23.2)]
    TE = [(-9.6, -21.2), (-8.0, -19.9), (-10.6, -17.6), (-9.0, -16.4),
          (-11.2, -13.8), (-9.6, -12.7), (-11.0, -10.2), (-9.8, -7.2),
          (-7.6, -3.4), (-4.2, 0.2), (-1.2, 1.6)]
    wrist = np.array([0.2, -12.5])
    pts = []
    for p in LE + TE:
        q = np.array(p, float) * scale
        if p[1] < -11.0:      # hand section: lag bends it back about the wrist
            q = wrist * scale + np.array(
                rot1(tuple(q - wrist * scale), (0, 0), -tip_lag))
        pts.append(q)
    th = flap * 0.3 + extra_rot
    if abs(th) > 0.01:
        pts = [np.array(rot1(tuple(q), (0, 0), th)) for q in pts]
    return pts, wrist

def draw_flight_wing(cv, pose, xf, style, far=False):
    """Broad layered flight wing: covert rows over a dark base, primaries
    as a deep-tone fingered zone at the trailing edge. Far wing is the
    same outline, smaller, darker, rotated further back, behind the body."""
    sil = style == 'silhouette'
    root = np.array(xf((5.0, -6.0))) + (np.array([-3.0, 0.5]) if far
                                        else np.array([0.0, 0.0]))
    pts, _ = _wing_outline(pose['flap'], pose['flap_tip'],
                           scale=0.92 if far else 1.0,
                           extra_rot=-14.0 if far else 0.0)
    world = [tuple(root + q) for q in pts]
    base = DEEP if far else DARKSLATE
    cv.poly(world, INK if sil else base, outline=None if sil else OUTLINE, ow=0.5)
    if sil or far:
        return
    # detail on a clipped temp layer: coverts along the arm, deep primaries.
    # The temp MUST be base-filled first — blit_masked pastes it wholesale.
    tmp = Canvas()
    tmp.poly(world, base)
    if style == 'naturalist':
        # covert rows as individual feathers laid along the arm (r4)
        darker = {LIGHT: SLATE, SLATE: DARKSLATE}
        rows = [(5, 4.5, 5.0, LIGHT), (5, 4.3, 4.7, SLATE)]
        for r, (count, pw, pl, tone) in enumerate(rows):
            for i in range(count):
                u = i / max(count - 1, 1)
                c = root + np.array([1.8 - 2.6 * u, -1.5 - 10.5 * u])
                dv = np.array([-0.72, -0.50 - 0.25 * u])
                dv = dv / np.hypot(*dv)
                anch = c - dv * pl * 0.40
                draw_feather(tmp, tuple(anch), tuple(dv),
                             pl * (0.9 + 0.2 * _jit(i + r * 9, 83)), pw, tone,
                             outline=None, shaft_tone=darker[tone],
                             barbs=2 if i % 2 == 0 else 0,
                             barb_tone=darker[tone], bend=0.14, asym=0.3)
        # primary separation strokes, wrist -> trailing notches
        for tt in (0.25, 0.5, 0.75):
            a = root + np.array([-1.5 - 2.0 * tt, -12.0 - 3.0 * tt])
            b = root + np.array([-9.9 + 1.2 * tt, -17.5 + 7.0 * tt])
            tmp.line([tuple(a), tuple(b)], OUTLINE, w=0.32)
        # fine hatching along the primary zone, feather direction (r4)
        for k in range(6):
            u = k / 5
            a = root + np.array([-4.4 - 1.4 * u, -15.2 - 4.4 * u])
            b = root + np.array([-8.8 + 0.8 * u, -11.4 + 3.4 * u])
            tmp.line([tuple(a), tuple(b)], OUTLINE, w=0.20)
    else:
        mass = [tuple(root + q) for q in
                [(2.4, 0.6), (0.6, -11.5), (-2.4, -16.5), (-4.4, -13.5),
                 (-3.4, -6.0), (-1.2, -0.6)]]
        tmp.poly(mass, SLATE, outline=None)
    # deep primary zone: the outer/trailing third of the outline
    zone = [tuple(root + q) for q in
            [(-4.6, -21.0), (-6.8, -23.2), (-9.6, -21.2), (-8.0, -19.9),
             (-10.6, -17.6), (-9.0, -16.4), (-11.2, -13.8), (-9.6, -12.7),
             (-11.0, -10.2), (-9.8, -7.2), (-8.6, -8.6), (-6.4, -13.0),
             (-4.9, -17.2)]]
    tmp.poly(zone, DEEP, outline=None)
    cv.blit_masked(tmp, world)

def draw_fish(cv, pose, style):
    if pose['fish_mode'] == 'none':
        return
    sil = style == 'silhouette'
    size = pose['fish_size']
    if pose['fish_mode'] == 'free':
        c = np.asarray(pose['fish_pos'], float)
        ang = np.deg2rad(pose['fish_ang'])
    else:
        H, pitch = head_group(pose)
        bdir = np.array([np.cos(np.deg2rad(pitch)), np.sin(np.deg2rad(pitch))])
        tip = np.array(bill_tip(pose))
        grip_pt = tip - bdir * (pose['fish_grip'] * 4.2)
        ang = np.deg2rad(pitch + pose['fish_orient'])
        axis = np.array([np.cos(ang), np.sin(ang)])
        c = grip_pt - axis * (0.5 - pose['fish_grip']) * 5.0 * size + np.array([0, 0.8])
    L, Hh = 11.0 * size, 3.7 * size
    axis = np.array([np.cos(ang), np.sin(ang)])
    perp = np.array([-axis[1], axis[0]])
    body = [c - axis * L * 0.5, c - axis * L * 0.18 + perp * Hh * 0.5,
            c + axis * L * 0.28 + perp * Hh * 0.46, c + axis * L * 0.5,
            c + axis * L * 0.28 - perp * Hh * 0.46, c - axis * L * 0.18 - perp * Hh * 0.5]
    cv.poly(catmull_rom(body, n_per=5, closed=True), INK if sil else FISH,
            outline=None if sil else OUTLINE, ow=0.4)
    if not sil:
        belly = [c - axis * L * 0.34, c + axis * L * 0.3,
                 c + axis * L * 0.26 - perp * Hh * 0.44, c - axis * L * 0.2 - perp * Hh * 0.46]
        cv.poly(belly, FISHBELLY, outline=None)
        tail = [c - axis * L * 0.48, c - axis * L * 0.72 + perp * Hh * 0.42,
                c - axis * L * 0.66, c - axis * L * 0.72 - perp * Hh * 0.42]
        cv.poly(tail, FISH2, outline=None)
        cv.disc(tuple(c + axis * L * 0.34), 0.32, INK)

def draw_torso_modeling(cv, pose, xf, loop):
    """Fine-art tonal modeling of the torso (naturalist, profile):
    light modeled like a drawing — a lit band under the back edge, a
    hatched shadow mass along the belly — clipped to the torso loop.
    Sits under the wing detail; what shows at the margins (back,
    breast, belly) stops being flat fill."""
    tmp = Canvas()
    # CRITICAL: tmp must start as a copy of the body — blit_masked
    # pastes tmp wholesale inside the mask, so a white-based tmp
    # ERASES the torso wherever no modeling shape covers it (this
    # whitened a strip above the belly and visually detached the
    # belly fringe in early r4 renders).
    tmp.img = Image.fromarray(np.asarray(cv.img).copy())
    tmp.dr = ImageDraw.Draw(tmp.img)
    lit = [(-19.5, -1.0), (-12.0, -7.6), (-2.0, -9.4), (8.0, -8.6),
           (14.5, -4.6), (15.6, -0.8), (10.5, -3.2), (1.0, -5.2),
           (-11.0, -4.6), (-18.0, -2.6)]
    tmp.poly([xf(p) for p in lit], LIGHT, outline=None)
    breast = [(15.6, -0.8), (14.5, -4.6), (11.5, -4.4), (13.8, 0.5),
              (12.6, 4.6), (15.0, 3.6)]
    tmp.poly([xf(p) for p in breast], PALE, outline=None)
    shadow = [(14.8, 4.6), (11.5, 7.9), (4.0, 10.0), (-4.0, 10.2),
              (-11.0, 8.6), (-16.6, 5.4), (-11.5, 7.3), (-2.0, 8.4),
              (7.0, 7.2), (13.2, 6.0)]
    tmp.poly([xf(p) for p in shadow], DARKSLATE, outline=None)
    # hatch strokes inside the belly shadow, following the body curve
    for i, bx in enumerate(np.arange(-14.5, 12.5, 1.7)):
        y0 = 9.9 - 0.55 * np.cos((bx + 2) / 15.0) ** 2 - (0.35 if bx > 6 else 0.0)
        a = np.array(xf((bx, y0 - 2.6)))
        b = np.array(xf((bx + 0.9, y0 - 0.4)))
        tmp.line([tuple(a), tuple(b)], DEEP, w=0.20)
    # fine hatch under the back light, sparse, feather-flow direction
    for i, bx in enumerate(np.arange(-15.0, 10.0, 2.6)):
        a = np.array(xf((bx, -6.4 + 0.9 * np.sin(bx / 6.0))))
        b = np.array(xf((bx + 1.6, -5.2 + 0.9 * np.sin(bx / 6.0))))
        tmp.line([tuple(a), tuple(b)], SLATE, w=0.18)
    cv.blit_masked(tmp, loop)

def _fx90(xf):
    """Front-stop local -> world, with the torso's 1.12 vertical stretch."""
    return lambda p: xf((p[0], p[1] * 1.12))

def draw_front_panels(cv, pose, xf, style):
    """Yaw-90 anatomy (clip-01 front frames): the folded wings read as two
    vertical side panels, the breast is a centred plume column continuous
    with the throat beard, belly skirt ragged below. No ball, no totem."""
    sil = style == 'silhouette'
    f = _fx90(xf)
    for sx in (-1, 1):   # folded-wing side panels
        panel = [(sx * 4.3, -4.6), (sx * 6.4, -3.2), (sx * 6.8, 0.8),
                 (sx * 6.1, 4.8), (sx * 4.5, 6.2), (sx * 3.8, 0.6),
                 (sx * 3.9, -2.6)]
        cv.poly([f(p) for p in catmull_rom(panel, n_per=6, closed=True)],
                INK if sil else DARKSLATE,
                outline=None if sil else OUTLINE,
                ow=0.5 if style == 'naturalist' else 0.85)
        if style == 'naturalist' and not sil:
            for yy in (-1.0, 1.6, 4.0):   # scallop hints across the panel
                cv.line([f((sx * 4.3, yy)), f((sx * 5.4, yy + 0.55)),
                         f((sx * 6.3, yy + 0.25))], DEEP, w=0.35)
    if sil:
        return
    # breast plume column: light teardrop down the centre
    col = [(-1.9, -5.4), (1.9, -5.4), (2.5, -0.5), (1.6, 3.4),
           (0.0, 5.9), (-1.6, 3.4), (-2.5, -0.5)]
    cv.poly([f(p) for p in catmull_rom(col, n_per=6, closed=True)],
            LIGHT, outline=OUTLINE, ow=0.4)
    if style == 'naturalist':   # feather fringe at the column's hem
        pairs = []
        for j, xx in enumerate(np.linspace(-1.5, 1.5, 7)):
            pairs.append(_wdir(f, (xx, 5.0 + 0.5 * (1 - abs(xx) / 1.6)),
                               (xx * 0.12, 1.0)))
        fringe(cv, pairs, 3.4, 1.15, [PALE, LIGHT], bend=0.15, seed=71,
               shaft_tone=SLATE)
    else:                       # storybook: shaped zigzag hem mass
        hem = [(-1.6, 5.4), (1.6, 5.4), (1.25, 8.6), (0.45, 7.1),
               (-0.35, 8.9), (-1.2, 7.0)]
        cv.poly([f(p) for p in hem], LIGHT, outline=OUTLINE, ow=0.7)
    if style == 'naturalist':   # belly skirt: feathers, not strands
        pairs = [_wdir(f, (bx, 8.3), (bx * 0.06, 1.0)) for bx in (-3.4, -1.7, 0.0, 1.7, 3.4)]
        fringe(cv, pairs, 3.1, 2.0, [DARKSLATE, DEEP], bend=0.12, seed=73,
               shaft_tone=DARKSLATE, embed=1.3)
    else:
        for bx in (-3.4, 0.0, 3.4):   # ragged belly skirt
            tapered_strand(cv, f((bx, 8.5)), (bx * 0.06, 1.0), 2.3, 1.6,
                           DARKSLATE, bend=0.1)

def draw_flight_back(cv, pose, xf, style):
    """In flight the torso keeps its feather structure: scallop rows lie
    along the back inside the torso loop (the folded wing is gone, its
    feathering is not), plus tail feather tips at the rear."""
    sil = style == 'silhouette'
    if sil:
        return
    loop_pts = torso_loop(pose, xf)
    tmp = Canvas()
    tmp.poly(loop_pts, SLATE)   # base-filled: blit_masked pastes wholesale
    if style == 'naturalist':
        rows = [(8, 5.5, 4.5, LIGHT), (8, 5.3, 4.3, DARKSLATE),
                (7, 5.0, 4.1, DEEP)]
        darker = {LIGHT: SLATE, DARKSLATE: DEEP, DEEP: OUTLINE}
        for r, (count, pw, pl, tone) in enumerate(rows):
            y0 = -6.9 + r * 2.3
            for i in range(count):
                u = i / max(count - 1, 1)
                cx = -14.0 + u * 23.0 + r * 0.8
                cy = y0 + 1.0 * np.sin(u * np.pi * 0.72)
                ang = np.deg2rad(48 + 16 * u + r * 3)
                dv = np.array([np.cos(ang), np.sin(ang)])
                anch = np.array([cx, cy]) - dv * pl * 0.45
                wa, wd = _wdir(xf, tuple(anch), tuple(dv))
                draw_feather(tmp, wa, wd, pl * (0.9 + 0.2 * _jit(i + r * 20, 91)),
                             pw * 0.94, tone, outline=None,
                             shaft_tone=darker[tone],
                             barbs=2 if (i + r) % 2 == 0 else 0,
                             barb_tone=darker[tone], bend=0.16, asym=0.3)
    else:
        rows = [(5, 9.4, 3.7, DEEP)]
        for r, (count, pw, ph, tone) in enumerate(rows):
            y0 = -6.9 + r * 2.3
            for i in range(count):
                u = i / max(count - 1, 1)
                cx = -14.0 + u * 23.0 + r * 0.8
                cy = y0 + 1.0 * np.sin(u * np.pi * 0.72)
                ang = 5 + 28 * u + r * 3
                petal = [(cx - pw / 2, cy - ph * 0.34), (cx - pw * 0.16, cy - ph * 0.58),
                         (cx + pw * 0.30, cy - ph * 0.5), (cx + pw / 2, cy - ph * 0.05),
                         (cx + pw * 0.26, cy + ph * 0.4), (cx - pw * 0.14, cy + ph * 0.46),
                         (cx - pw * 0.44, cy + ph * 0.2)]
                petal = rot(petal, (cx, cy), ang)
                tmp.poly([xf(p) for p in petal], tone, outline=None, ow=0.3)
    cv.blit_masked(tmp, loop_pts)
    if style == 'naturalist':
        for k, (dy, fang) in enumerate(((-2.2, 0.08), (-1.2, 0.15), (-0.2, 0.22),
                                        (0.8, 0.29), (1.8, 0.36), (2.7, 0.43))):
            wa, wd = _wdir(xf, (-16.6, dy), (-1.0, fang))
            draw_feather(cv, wa, wd, 3.6 - 0.45 * abs(k - 2.5) + 0.5 * _jit(k, 97),
                         2.8, DEEP, shaft_tone=None, bend=0.10, asym=0.3)
        anch = [(6.0, 8.6), (3.5, 9.2), (1.0, 9.5), (-1.5, 9.6),
                (-4.0, 9.5), (-6.5, 9.0), (-9.0, 8.4)]
        pairs = [_wdir(xf, a, (0.28 - 0.03 * i, 1.0)) for i, a in enumerate(anch)]
        fringe(cv, pairs, 2.2, 2.6, [DARKSLATE, DARKSLATE, SLATE], bend=0.08,
               seed=93, shaft_tone=None, embed=1.5)
    elif not sil:
        for k, dy in enumerate((-1.5, 0.2, 1.8)):
            tapered_strand(cv, xf((-17.8, dy)), (-1.0, 0.28), 4.2 - k * 0.5, 2.3,
                           DARKSLATE, bend=0.15)

# ------------------------------------------------------------------ render
def render(pose, style='naturalist', ink_events=None, return_layers=False):
    """pose -> palette-index grid (H_PX, W_PX). ink_events drawn last."""
    xf, piv = body_xform(pose)
    body = Canvas(); legs_far = Canvas(); legs_near = Canvas()
    # legs on their own layers (waterline clip applied per leg at composite)
    foot_far = draw_leg(legs_far, pose, pose['leg_far'], HIP_FAR, xf, FARUSTY, style)
    foot_near = draw_leg(legs_near, pose, pose['leg_near'], HIP_NEAR, xf, RUSTY, style)
    # flight far wing behind the torso
    if pose['wing_mode'] == 'flight':
        draw_flight_wing(body, pose, xf, style, far=True)
    # torso: one continuous loop
    sil = style == 'silhouette'
    loop = torso_loop(pose, xf)
    body.poly(loop, INK if sil else SLATE, outline=None if sil else OUTLINE,
              ow=0.55 if style == 'naturalist' else 0.9)
    if style == 'naturalist' and pose['wing_mode'] == 'folded' \
            and int(round(pose['yaw'])) != 90:
        draw_torso_modeling(body, pose, xf, loop)
    if pose['wing_mode'] == 'folded':
        if int(round(pose['yaw'])) == 90:
            draw_front_panels(body, pose, xf, style)
        else:
            draw_wing_detail(body, pose, xf, style)
    elif pose['wing_mode'] == 'flight':
        draw_flight_wing(body, pose, xf, style, far=False)
        draw_flight_back(body, pose, xf, style)
        draw_shoulder_patch(body, xf, style)
    # breast anchor -> neck -> head
    st = YAW_STOPS.get(int(round(pose['yaw'])), YAW_STOPS[0])
    if int(round(pose['yaw'])) == 90:
        breast = xf((0.0, -5.0))
    else:
        breast = xf((BREAST_LOCAL[0] + st['ndx'], BREAST_LOCAL[1]))
    draw_neck(body, pose, breast, style)
    draw_head(body, pose, style)
    draw_fish(body, pose, style)
    # composite: legs under body; planted legs clipped at the waterline
    arr = np.full((H_PX * SS, W_PX * SS), WHITE, dtype=np.uint8)
    wl = int(Y(WATER_Y))
    for layer, foot in ((legs_far, foot_far), (legs_near, foot_near)):
        la = np.asarray(layer.img)
        mask = la != WHITE
        if foot[1] >= WATER_Y - 0.5:      # planted: hide below the surface
            rows = np.zeros_like(mask); rows[:wl, :] = True
            mask &= rows
        arr[mask] = la[mask]
    ba = np.asarray(body.img)
    mask = ba != WHITE
    arr[mask] = ba[mask]
    if ink_events:
        ic = Canvas(); ic.img = Image.fromarray(arr)
        ic.dr = ImageDraw.Draw(ic.img)
        for ev in ink_events:
            ev(ic)
        arr = np.asarray(ic.img)
    # majority downsample
    h, w = H_PX, W_PX
    blocks = arr.astype(np.int32).reshape(h, SS, w, SS).transpose(0, 2, 1, 3).reshape(h * w, SS * SS)
    off = (np.arange(h * w) * NPAL).astype(np.int32)[:, None]
    counts = np.bincount((blocks + off).ravel(), minlength=h * w * NPAL)
    return counts.reshape(h * w, NPAL).argmax(1).reshape(h, w).astype(np.uint8)

def to_rgb(grid):
    return PALETTE[grid]
