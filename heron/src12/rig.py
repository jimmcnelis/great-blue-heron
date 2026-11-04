"""Heron rig v1.2 — POSE-SPACE rig with a yaw-aware drawing path.

Pose dict -> palette-index grid, same design space (120x90), palette, grid
mapping and supersample/majority-downsample discipline as v1.1. What v1.2 adds
(movement study §11 / movement-charts.yaml rig requirements):

- yaw (0..180) + head_yaw + head_roll: the body is DRAWN through five authored
  orientation stops (0 profile / 45 three-quarter / 90 front / 135 / 180).
  Part positions are functions of yaw anchored at the stops — body width,
  neck-base migration, tail swing, hip spread, wing-patch migration, side
  wing bulges at front — never a scaled or flipped finished drawing.
- beak_open: a real gape (upper/lower mandible split at the hinge).
- fish from (fish_grip, fish_orient, free-arc) in ALL phases: grip point
  along the bill, orientation crosswise<->head-first, authored free arc.
- neck_bulge_pos/amp: a localized bulge that travels down the neck tube.
- flap_tip: wingtip angle tracked separately from the root angle.
- leg_*.toe: toe pitch (trailing in swing, flat at plant, curled in tuck).
- smear: authored strike smear (multiples + elongated neck) for 1 frame.
- drawn one-leg tuck (no hide_near), drawn head turns (no look_back).

Facing convention: yaw 0 = profile facing right, 90 = front, 180 = profile
facing left. head world yaw = yaw + head_yaw (same convention).
"""
import os
import numpy as np
from PIL import Image, ImageDraw

W = int(os.environ.get('HERON_W', 320))
H = int(os.environ.get('HERON_H', 240))
SS = 4
WATER_Y = 74
S = H / 90.0
def _mx(x): return (x - 60.0) * S + W / 2.0
def _my(y): return y * S
SURF_ROW = int(round(_my(WATER_Y)))

WHITE, INK, OUTLINE, SLATE, DARKSLATE, PALE, ORANGE, RUSTY, LEGC, FISH, FISH2, FISHBELLY = range(12)
PALETTE = np.array([
    (255, 255, 255), (0, 0, 0), (30, 48, 74), (105, 130, 155),
    (66, 93, 122), (176, 203, 224), (240, 133, 36), (154, 82, 60),
    (74, 48, 36), (150, 163, 105), (94, 110, 66), (216, 222, 182),
], dtype=np.uint8)
NPAL = 12

# ---------------------------------------------------------------- yaw stops
# Authored orientation stops: (yaw, body_rx_factor, body_ry_factor, bulge)
# bulge = side folded-wing bulge size at front-ish views (keeps the front
# silhouette's area on-model — see the +-5% area gate in the charts).
_YAW_STOPS = [(0.0, 1.00, 1.00, 0.0), (45.0, 0.80, 1.06, 0.45),
              (90.0, 0.565, 1.31, 1.0), (135.0, 0.80, 1.06, 0.45),
              (180.0, 1.00, 1.00, 0.0)]

def _stop_interp(yaw, col):
    yaw = float(np.clip(yaw, 0.0, 180.0))
    for (y0, *v0), (y1, *v1) in zip(_YAW_STOPS, _YAW_STOPS[1:]):
        if y0 <= yaw <= y1:
            t = (yaw - y0) / max(y1 - y0, 1e-9)
            return v0[col] * (1 - t) + v1[col] * t
    return _YAW_STOPS[-1][1 + col]

def _bez(p0, p1, p2, p3, n=14):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = [np.asarray(p, float) for p in (p0, p1, p2, p3)]
    return ((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 +
            3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3)

def _tube(dr, pts, w0, w1, color, outline=True, bulge_pos=None, bulge_amp=0.0):
    pts = np.asarray(pts, float)
    d = np.gradient(pts, axis=0)
    n = np.hypot(d[:, 0], d[:, 1]); n[n == 0] = 1
    nrm = np.stack([-d[:, 1] / n, d[:, 0] / n], axis=1)
    w = np.linspace(w0, w1, len(pts)) / 2.0
    if bulge_amp > 0.01 and bulge_pos is not None:
        # s = 0 at the head (top) end, 1 at the body/base end — matches the
        # charts' neck_bulge_pos convention (0 = gape, 1 = body)
        s = 1.0 - np.linspace(0, 1, len(pts))
        w = w * (1.0 + bulge_amp * 1.15 * np.exp(-((s - bulge_pos) / 0.14) ** 2))
    w = w[:, None]
    poly = np.concatenate([pts + nrm * w, (pts - nrm * w)[::-1]])
    dr.polygon([(_mx(px) * SS, _my(py) * SS) for px, py in poly], fill=color,
               outline=OUTLINE if outline else None, width=int(0.8 * S * SS))

def _line(dr, pts, color, width):
    dr.line([(_mx(float(p[0])) * SS, _my(float(p[1])) * SS) for p in pts], fill=color,
            width=max(1, int(width * SS * S)), joint='curve')

def _poly(dr, pts, color, outline=True):
    dr.polygon([(_mx(float(p[0])) * SS, _my(float(p[1])) * SS) for p in pts], fill=color,
               outline=OUTLINE if outline else None, width=int(0.8 * S * SS))

def _ell(dr, cx, cy, rx, ry, color, outline=True):
    dr.ellipse([(_mx(cx) - rx * S) * SS, (_my(cy) - ry * S) * SS,
                (_mx(cx) + rx * S) * SS, (_my(cy) + ry * S) * SS],
               fill=color, outline=OUTLINE if outline else None, width=int(0.8 * S * SS))

def _ell_rot(dr, cx, cy, rx, ry, ang_deg, color, outline=False):
    a = np.deg2rad(ang_deg)
    t = np.linspace(0, 2 * np.pi, 22)
    pts = np.stack([cx + rx * np.cos(t) * np.cos(a) - ry * np.sin(t) * np.sin(a),
                    cy + rx * np.cos(t) * np.sin(a) + ry * np.sin(t) * np.cos(a)], axis=1)
    _poly(dr, pts, color, outline=outline)

def _rot(pts, c, ang_deg):
    a = np.deg2rad(ang_deg)
    R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    return [tuple(np.asarray(c, float) + R @ (np.asarray(p, float) - np.asarray(c, float)))
            for p in pts]

def default_pose():
    return dict(
        root_x=30.0, root_y=0.0,
        body_tilt=0.0,
        neck_coil=0.0, neck_extend=0.0, neck_sway=0.0, neck_retract=0.0,
        head_pitch=0.0, plume_sway=0.0, blink=0.0,
        yaw=0.0, head_yaw=0.0, head_roll=0.0, beak_open=0.0,
        wing_amt=0.0, flap=0.0, flap_tip=0.0, flying=0.0, warble=0.0,
        leg_far=dict(fx=-2.0, fy=86.0, toe=0.0),
        leg_near=dict(fx=5.0, fy=86.0, toe=0.0),
        tail_ang=0.0, smear=0.0,
        neck_bulge_pos=0.0, neck_bulge_amp=0.0,
        fish='none', fish_size='tiny',
        fish_grip=0.35, fish_orient=90.0,
        fish_x=0.0, fish_y=0.0, fish_free_ang=0.0,
    )

def _ik(hip, foot, a, b, pole):
    hip = np.asarray(hip, float); foot = np.asarray(foot, float)
    d = foot - hip; dist = np.hypot(*d)
    dist = min(max(dist, 0.5), a + b - 0.01)
    dirv = d / max(np.hypot(*d), 1e-9)
    x = (a * a - b * b + dist * dist) / (2 * dist)
    h = np.sqrt(max(a * a - x * x, 0.0))
    nrm = np.array([-dirv[1], dirv[0]]) * pole
    return hip + dirv * x + nrm * h

def _draw_leg(dr, hip, foot, toe_deg, dirx, fold=0.0):
    """Thinned stilt leg: rusty thigh -> shin -> ANKLE (intertarsal joint,
    bulging backward) -> tarsus -> toes pitched by toe_deg. fold (0..1) tucks
    the tarsus further back/up as the foot lifts (the stalk fold)."""
    hip = np.asarray(hip, float); foot = np.asarray(foot, float)
    thigh_end = hip + np.array([(foot[0] - hip[0]) * 0.18, 9.0])
    ankle = _ik(thigh_end, foot, 13.5, 15.5, -1.0)
    if fold > 0.01:
        ankle = ankle + np.array([-dirx * fold * 3.2, -fold * 2.0])
    _line(dr, [hip, thigh_end], RUSTY, 2.9)
    _line(dr, [thigh_end, ankle], LEGC, 1.15)
    _ell(dr, ankle[0], ankle[1], 0.95, 0.95, LEGC, outline=False)
    _line(dr, [ankle, foot], LEGC, 1.05)
    if foot[1] < WATER_Y - 1:  # toes visible only above the surface
        a = np.deg2rad(toe_deg)
        base = np.array([np.sin(a) * (dirx if dirx != 0 else 1.0), np.cos(a)])
        for spread in (-0.35, 0.0, 0.35):
            aa = a + spread
            td = np.array([np.sin(aa) * (dirx if dirx != 0 else 1.0), np.cos(aa)])
            _line(dr, [foot, foot + td * 3.1], LEGC, 0.55)

def _draw_leg_stream(dr, hip, foot):
    hip = np.asarray(hip, float); foot = np.asarray(foot, float)
    _line(dr, [hip, foot], LEGC, 1.0)
    d = foot - hip; d = d / max(np.hypot(*d), 1e-6)
    _line(dr, [foot, foot + d * 2.6], LEGC, 0.6)

def _draw_fish(dr, cx, cy, length, ang_deg, flip=1):
    a = np.deg2rad(ang_deg)
    R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    L, h = length, length * 0.42
    body = np.array([[L * 0.5, 0], [L * 0.18, -h * 0.5], [-L * 0.28, -h * 0.46],
                     [-L * 0.5, 0], [-L * 0.28, h * 0.46], [L * 0.18, h * 0.5]])
    tail = np.array([[-L * 0.42, 0], [-L * 0.72, -h * 0.55], [-L * 0.72, h * 0.55]])
    back = np.array([[L * 0.5, 0], [L * 0.18, -h * 0.5], [-L * 0.28, -h * 0.46],
                     [-L * 0.2, -h * 0.1], [L * 0.2, -h * 0.08]])
    def xf(pts):
        return [tuple(np.array([cx, cy]) + R @ (p * np.array([flip, 1]))) for p in pts]
    _poly(dr, xf(tail), FISH2, outline=False)
    _poly(dr, xf(body), FISH, outline=False)
    _poly(dr, xf(back), FISH2, outline=False)
    eye = np.array([cx, cy]) + R @ (np.array([L * 0.32, -h * 0.08]) * np.array([flip, 1]))
    _ell(dr, eye[0], eye[1], 0.55, 0.55, INK, outline=False)

def render(pose):
    """Returns (index grid uint8 (H,W), info dict)."""
    p = {**default_pose(), **pose}
    img = Image.new('L', (W * SS, H * SS), WHITE)
    dr = ImageDraw.Draw(img)
    bx, by = p['root_x'], 38.0 + p['root_y']
    yaw = float(np.clip(p['yaw'], 0.0, 180.0))
    dirx = np.cos(np.deg2rad(yaw))                    # +1 facing right, -1 left
    adirx = abs(dirx)
    wfac = _stop_interp(yaw, 0)                       # body rx factor
    ryfac = _stop_interp(yaw, 1)                      # body ry factor
    bulge = _stop_interp(yaw, 2)                      # front wing-bulge amount
    fdir = 1.0 if dirx >= 0 else -1.0
    # The tilt flips sign with facing: call sites pass x already scaled by
    # dirx, so rotating by tilt*dirx is what makes yaw 180 a TRUE mirror of
    # yaw 0 (measured: fixed tilt put the neck base 11 units lower and 260
    # PALE cells heavier facing left). At front dirx->0 the body levels out.
    tilt = np.deg2rad(p['body_tilt']) * dirx
    def bt(pt):  # body-local -> world (rotate about body centre); x in facing terms
        v = np.asarray(pt, float)
        R = np.array([[np.cos(tilt), -np.sin(tilt)], [np.sin(tilt), np.cos(tilt)]])
        return np.array([bx, by]) + R @ v

    spread = 1.0 - adirx
    hip_far = bt([-4.0 - 2.0 * spread, 8.5])
    hip_near = bt([3.0 + 3.0 * spread, 8.5])
    stream = p['flying'] > 0.5
    # ---- far leg (behind body)
    if stream:
        _draw_leg_stream(dr, hip_far, [bx + p['leg_far']['fx'], p['leg_far']['fy']])
    else:
        lift_f = max(0.0, 86.0 - p['leg_far']['fy']) / 40.0
        _draw_leg(dr, hip_far, [bx + p['leg_far']['fx'], p['leg_far']['fy']],
                  p['leg_far'].get('toe', 0.0), dirx, fold=min(1.0, lift_f))
    # ---- tail: swings to the far side as yaw grows; hidden behind body at front
    ta = np.deg2rad(p['tail_ang'])
    tail_pts = [bt([-12 * dirx - 0 * spread, -2]), bt([-19.5 * dirx, 0.5 + 3 * np.sin(ta)]),
                bt([-20.5 * dirx, 4.5]), bt([-13 * dirx, 5])]
    if adirx > 0.15:
        _poly(dr, tail_pts, DARKSLATE)
    # ---- wing: flight / stretch / warble (behind body)
    shoulder = bt([6 * dirx if adirx > 0.15 else 0.0, -3])
    if p['wing_amt'] > 0.03:
        amt = p['wing_amt']
        if p['flying'] > 0.5:
            # two-segment wing: root by flap, tip by flap_tip (the lag lives here)
            a1 = np.deg2rad(p['flap']); a2 = np.deg2rad(p['flap_tip'])
            d1 = np.array([-np.cos(a1) * fdir, -np.sin(a1)])
            d2 = np.array([-np.cos(a2) * fdir, -np.sin(a2)])
            J = shoulder + d1 * 16.0
            T = J + d2 * 17.0
            wing = [shoulder + np.array([3 * fdir, 1]), shoulder + np.array([-6 * fdir, -4]),
                    J, T, T + np.array([10 * fdir, 4]), shoulder + np.array([-2 * fdir, 5])]
            _poly(dr, wing, SLATE)
            tipd = [J, T, T + np.array([10 * fdir, 4]), J + np.array([8 * fdir, 5])]
            _poly(dr, tipd, DARKSLATE, outline=False)
        elif p['warble'] > 0.5:
            # both-wings-up form suggested by the near wing raised high
            s = amt
            base = [shoulder, shoulder + np.array([-14 * s * fdir, -20 * s]),
                    shoulder + np.array([-24 * s * fdir, -14 * s]),
                    shoulder + np.array([-16 * s * fdir, 0]),
                    shoulder + np.array([-2 * fdir, 4])]
            _poly(dr, base, SLATE)
            _poly(dr, [base[1], base[2], base[3], shoulder + np.array([-9 * s * fdir, -2])],
                  DARKSLATE, outline=False)
        else:
            # same-side stretch: wing extends DOWN and OUT, scalloped fan
            s = amt
            base = [shoulder,
                    shoulder + np.array([-16 * s * fdir, 9 * s]),
                    shoulder + np.array([-27 * s * fdir, 13 * s]),
                    shoulder + np.array([-21 * s * fdir, 5 * s]),
                    shoulder + np.array([-14 * s * fdir, 8 * s]),
                    shoulder + np.array([-9 * s * fdir, 3 * s]),
                    shoulder + np.array([-2 * fdir, 4])]
            _poly(dr, base, SLATE)
            tip = [base[1], base[2], base[3], shoulder + np.array([-11 * s * fdir, 5 * s])]
            _poly(dr, tip, DARKSLATE, outline=False)
    # ---- body
    body_poly = []
    for t in np.linspace(0, 2 * np.pi, 26, endpoint=False):
        ex, ey = 16.5 * wfac * np.cos(t), 7.6 * ryfac * np.sin(t)
        ey += 1.2 * np.cos(t)
        # ex flipped by facing SIGN (not scaled by dirx — wfac owns the
        # width) so the plump front-bottom follows the facing: true mirror
        body_poly.append(bt([ex * fdir - 0.5 * dirx, ey]))
    _poly(dr, body_poly, SLATE)
    # front-view side bulges: the folded wings seen from the front (area keepers)
    if bulge > 0.03:
        for sx in (-1, 1):
            cx = bx + sx * (16.5 * wfac + 1.5) * 0.92
            _ell(dr, cx, by + 0.5, 3.7 * bulge + 0.8, 6.4 * ryfac * (0.5 + 0.5 * bulge),
                 DARKSLATE)
    # folded wing patch on the flank; migrates toward the far edge with yaw
    if p['wing_amt'] < 0.5:
        mig = (1.0 - wfac) * 6.0
        fw = [bt([-14 * dirx - mig * dirx, -2.0]), bt([2 * dirx - mig * dirx, -3.2]),
              bt([7.5 * dirx - mig * dirx, 0.5]), bt([1 * dirx - mig * dirx, 4.2]),
              bt([-3 * dirx - mig * dirx, 2.8]), bt([-5.5 * dirx - mig * dirx, 4.8]),
              bt([-9 * dirx - mig * dirx, 2.8]), bt([-11.5 * dirx - mig * dirx, 4.6]),
              bt([-15 * dirx - mig * dirx, 1.0])]
        _poly(dr, fw, DARKSLATE)
    # ---- neck
    coil, ext = p['neck_coil'], p['neck_extend']
    retract = p['neck_retract']
    nb = bt([10.5 * dirx, 2.5])
    up = dict(c1=(bx + 17.5 * dirx, by - 9), c2=(bx - 0.5 * dirx, by - 20),
              top=(bx + (7.5 - retract * 5) * dirx, by - 22.5))
    co = dict(c1=(bx + 14 * dirx, by - 1), c2=(bx + 18 * dirx, by - 8),
              top=(bx + 15.0 * dirx, by - 11.0))
    if adirx < 0.35:  # near front: neck rises centred in front of the chest
        k = (0.35 - adirx) / 0.35
        for d in (up, co):
            for key in ('c1', 'c2', 'top'):
                d[key] = (d[key][0] * (1 - k) + bx * k, d[key][1])
    def lerp2(a, b, t): return tuple(np.array(a) * (1 - t) + np.array(b) * t)
    c1 = lerp2(up['c1'], co['c1'], coil); c2 = lerp2(up['c2'], co['c2'], coil)
    top = np.array(lerp2(up['top'], co['top'], coil), float)
    top[0] += p['neck_sway'] * adirx if adirx > 0.2 else p['neck_sway'] * 0.2
    strike_pt = np.array([bx + 27 * (dirx if adirx > 0.2 else fdir), WATER_Y - 1.5])
    if ext > 0:
        top = top * (1 - ext) + strike_pt * ext
        c1 = np.array(c1) * (1 - ext) + (nb + (strike_pt - nb) * 0.35) * ext
        c2 = np.array(c2) * (1 - ext) + (nb + (strike_pt - nb) * 0.7) * ext
    if p['flying'] > 0:
        fly = p['flying']
        top_fold = np.array(nb) + np.array([5.5 * fdir, -9.5])
        c2_fold = np.array(nb) + np.array([-4.0 * fdir, -6.0])
        top = top * (1 - 0.72 * fly) + top_fold * (0.72 * fly)
        c2 = np.array(c2) * (1 - 0.6 * fly) + c2_fold * (0.6 * fly)
    neck_pts = _bez(nb, c1, c2, top, 14)
    # chest fringe: the shaggy breast-plume "beard" (footage batch 2 — it
    # hangs the full chest and reads at every range, widest at front views)
    fw_ = 1.0 + 0.9 * bulge
    fx = np.linspace(nb[0] - 3.0 * fw_, nb[0] + 4.0 * fw_, 6)
    fr = [(fx[0], nb[1] - 0.5), (fx[-1], nb[1] - 0.5)]
    for i, x in enumerate(fx[::-1]):
        fr.append((x, nb[1] + (6.0 if i % 2 == 0 else 3.0) * (1.0 + 0.35 * bulge)))
    _poly(dr, fr, PALE)
    _tube(dr, neck_pts, 6.6, 4.8, PALE,
          bulge_pos=p['neck_bulge_pos'], bulge_amp=p['neck_bulge_amp'])
    patch = [bt([6.8 * dirx, -5.2]), bt([11.4 * dirx, -3.4]), bt([11.8 * dirx, 1.8]),
             bt([8.0 * dirx, 3.2]), bt([6.4 * dirx, -1.0])]
    if adirx > 0.15:
        _poly(dr, patch, INK, outline=False)
    # ---- smear ghosts (authored multiples along the strike path; drawn under head)
    hx, hy = top
    hw = yaw + p['head_yaw']          # head world yaw, same convention as yaw
    hcos = np.cos(np.deg2rad(hw)); hsin = np.sin(np.deg2rad(hw))
    hdir = 1.0 if hcos >= 0 else -1.0
    if p['smear'] > 0 and ext > 0.5:
        for frac in (0.45, 0.72):
            gx = nb[0] + (strike_pt[0] - nb[0]) * frac
            gy = nb[1] + (strike_pt[1] - nb[1]) * frac - 2
            _ell_rot(dr, gx, gy, 6.5, 2.6, 55 * fdir, PALE, outline=False)
            tip_g = np.array([gx, gy]) + np.array([np.cos(np.deg2rad(55)) * 15 * fdir,
                                                   np.sin(np.deg2rad(55)) * 15])
            _poly(dr, [(gx, gy - 1.6), tuple(tip_g), (gx, gy + 1.6)], ORANGE, outline=False)
    # ---- head (drawn through its own yaw stops, rolled by head_roll)
    head_c = np.array([hx + hdir * 1.5 * abs(hcos), hy - 1.0])
    hwfac = 0.55 + 0.45 * abs(hcos)   # head narrows toward front view
    head_parts = []
    def _H(pts):  # head-local points -> rolled around head centre
        return _rot(pts, head_c, p['head_roll']) if abs(p['head_roll']) > 0.01 else [tuple(q) for q in pts]
    _ell(dr, head_c[0], head_c[1], 5.0 * hwfac + 0.6, 3.4, WHITE)
    cap = [(head_c[0] - 4.6 * hcos, head_c[1] - 0.9), (head_c[0] - 2.8 * hcos, head_c[1] - 3.1),
           (head_c[0] + 1.2 * hcos, head_c[1] - 3.4), (head_c[0] + 4.8 * hcos, head_c[1] - 1.8),
           (head_c[0] + 4.4 * hcos, head_c[1] - 0.9), (head_c[0] + 1.0 * hcos, head_c[1] - 1.7),
           (head_c[0] - 2.4 * hcos, head_c[1] - 1.5)]
    _poly(dr, _H(cap), INK, outline=False)
    # plume: strands trailing opposite the head's forward direction
    for k, (ln, droop) in enumerate([(13.5, 2.2), (11.0, 3.6)]):
        sway = p['plume_sway'] * (1 + 0.3 * k)
        pp = _bez(head_c + np.array([-3.4 * hcos, -2.4]),
                  head_c + np.array([-3.4 * hcos - ln * 0.45 * hcos, -3.4 - k * 0.7 + sway * 0.3]),
                  head_c + np.array([-3.4 * hcos - ln * 0.8 * hcos, -2.2 + droop * 0.4 + sway * 0.7]),
                  head_c + np.array([-3.4 * hcos - ln * hcos, -0.6 + droop + sway]), 10)
        _line(dr, _H(pp), INK, 0.85)
    # beak: hinge at b0; upper mandible along pitch, lower rotated by the gape
    pitch = np.deg2rad(16 + p['head_pitch'] + (38 * ext))
    bl = 13.5 * max(abs(hcos), 0.12)
    b0 = head_c + np.array([3.9 * hcos, 0.3])
    bdir = np.array([np.cos(pitch) * hdir, np.sin(pitch)])
    tip = b0 + bdir * bl
    perp = np.array([-np.sin(pitch) * hdir, np.cos(pitch)]) * 1.8
    _poly(dr, _H([b0 + perp, tip, b0 - perp * 0.30]), ORANGE, outline=False)
    if p['beak_open'] > 0.02:
        ga = np.deg2rad(16 + p['head_pitch'] + (38 * ext) + 26 * p['beak_open'])
        d2 = np.array([np.cos(ga) * hdir, np.sin(ga)])
        tip2 = b0 + d2 * bl * 0.94
        perp2 = np.array([-np.sin(ga) * hdir, np.cos(ga)]) * 1.8
        _poly(dr, _H([b0 + perp2 * 0.30, tip2, b0 - perp2]), ORANGE, outline=False)
    # eyes: near eye always; far eye appears as the head turns toward front
    ex_, ey_ = head_c + np.array([2.1 * hcos + 1.9 * hsin, -0.1])
    if hsin > 0.3:
        fx2 = head_c + np.array([2.1 * hcos - 1.9 * hsin, -0.1])
        if p['blink'] <= 0.5:
            _ell(dr, fx2[0], fx2[1], 0.8, 0.8, INK, outline=False)
    if p['blink'] > 0.75:
        _line(dr, _H([(ex_ - 1.1, ey_), (ex_ + 1.1, ey_)]), OUTLINE, 0.8)
    elif p['blink'] > 0.25:
        _ell(dr, ex_, ey_, 1.05, 0.5, INK, outline=False)
    else:
        _ell(dr, ex_, ey_, 1.05, 1.05, INK, outline=False)
    # ---- near leg (in front of body bottom) — ALWAYS drawn (tuck is a drawing)
    if stream:
        _draw_leg_stream(dr, hip_near, [bx + p['leg_near']['fx'], p['leg_near']['fy']])
    else:
        lift_n = max(0.0, 86.0 - p['leg_near']['fy']) / 40.0
        _draw_leg(dr, hip_near, [bx + p['leg_near']['fx'], p['leg_near']['fy']],
                  p['leg_near'].get('toe', 0.0), dirx, fold=min(1.0, lift_n))
    # ---- fish: from (grip, orient) when held; authored arc when free
    if p['fish'] == 'held':
        fl = 5.5 if p['fish_size'] == 'tiny' else 10.5
        G = tip + (b0 - tip) * float(np.clip(p['fish_grip'], 0, 1))
        orient = float(p['fish_orient'])
        aligned = np.cos(np.deg2rad(orient)); cross = np.sin(np.deg2rad(orient))
        fc = G + bdir * (fl * 0.30 * aligned) + np.array([0.0, fl * 0.24 * cross])
        fang = np.degrees(np.arctan2(bdir[1], bdir[0])) + 180.0 - orient
        _draw_fish(dr, fc[0], fc[1], fl, fang, flip=hdir)
    elif p['fish'] == 'free':
        fl = 5.5 if p['fish_size'] == 'tiny' else 10.5
        _draw_fish(dr, p['fish_x'], p['fish_y'], fl, p['fish_free_ang'], flip=hdir)
    # ---- clip below the implied surface; majority downsample
    arr = np.array(img, dtype=np.uint8).reshape(H, SS, W, SS)
    arr[SURF_ROW:, :, :, :] = WHITE
    blocks = arr.transpose(0, 2, 1, 3).reshape(H, W, SS * SS)
    counts = np.stack([(blocks == k).sum(-1) for k in range(NPAL)], axis=-1)
    grid = counts.argmax(-1).astype(np.uint8)
    info = dict(beak_tip=(float(_mx(tip[0])), float(_my(tip[1]))),
                head=(float(_mx(head_c[0])), float(_my(head_c[1]))),
                gape=(float(_mx(b0[0])), float(_my(b0[1]))))
    return grid, info

if __name__ == '__main__':
    g, info = render({})
    print('grid:', g.shape, 'nonwhite cells:', int((g != WHITE).sum()), 'beak tip:', info['beak_tip'])
    rgb = PALETTE[g]
    Image.fromarray(rgb).resize((800, 480), Image.NEAREST).save('/tmp/rig12_test.png')
