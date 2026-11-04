"""Heron rig: palette + layered 2D renderer. Pose dict -> 90x120 palette-index grid."""
import numpy as np
from PIL import Image, ImageDraw

W, H = 160, 120
SS = 4                      # supersample
WATER_Y = 74                # design-space surface (never drawn; bird clipped at SURF_ROW)
# NORMALIZED design space: 120x90 (the tuned character proportions).
# Grid mapping: uniform scale S = H/90 (bird size follows frame height), stage centred.
# Master v1 grid 160x120 (x2 -> 320x240 BOX-3, full-bleed). The 800x480 product frame
# is the same corpus re-rendered with W,H = 160,96 — a re-render, not a redesign.
S = H / 90.0
def _mx(x): return (x - 60.0) * S + W / 2.0
def _my(y): return y * S
SURF_ROW = int(round(_my(WATER_Y)))   # implied surface row on the real grid

# palette indices
WHITE, INK, OUTLINE, SLATE, DARKSLATE, PALE, ORANGE, RUSTY, LEGC, FISH, FISH2, FISHBELLY = range(12)
PALETTE = np.array([
    (255, 255, 255),  # 0 white
    (0, 0, 0),        # 1 ink black (water ink, eye, shoulder patch, plume)
    (30, 48, 74),     # 2 outline dark navy
    (105, 130, 155),  # 3 slate body
    (66, 93, 122),    # 4 dark slate flight feathers
    (176, 203, 224),  # 5 pale neck
    (240, 133, 36),   # 6 orange beak
    (154, 82, 60),    # 7 rusty thighs
    (74, 48, 36),     # 8 leg dark brown
    (150, 163, 105),  # 9 fish body
    (94, 110, 66),    # 10 fish back
    (216, 222, 182),  # 11 fish belly
], dtype=np.uint8)
NPAL = 12

def _bez(p0, p1, p2, p3, n=14):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = [np.asarray(p, float) for p in (p0, p1, p2, p3)]
    return ((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 +
            3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3)

def _tube(dr, pts, w0, w1, color, outline=True):
    pts = np.asarray(pts, float)
    d = np.gradient(pts, axis=0)
    n = np.hypot(d[:, 0], d[:, 1]); n[n == 0] = 1
    nrm = np.stack([-d[:, 1] / n, d[:, 0] / n], axis=1)
    w = np.linspace(w0, w1, len(pts))[:, None] / 2.0
    left = pts + nrm * w
    right = pts - nrm * w
    poly = np.concatenate([left, right[::-1]])
    dr.polygon([(_mx(px) * SS, _my(py) * SS) for px, py in poly], fill=color,
               outline=OUTLINE if outline else None, width=int(0.8 * S * SS))

def _line(dr, pts, color, width):
    dr.line([(_mx(float(p[0])) * SS, _my(float(p[1])) * SS) for p in pts], fill=color,
            width=int(width * SS * S), joint='curve')

def _poly(dr, pts, color, outline=True):
    dr.polygon([(_mx(float(p[0])) * SS, _my(float(p[1])) * SS) for p in pts], fill=color,
               outline=OUTLINE if outline else None, width=int(0.8 * S * SS))

def _ell(dr, cx, cy, rx, ry, color, outline=True):
    dr.ellipse([(_mx(cx) - rx * S) * SS, (_my(cy) - ry * S) * SS,
                (_mx(cx) + rx * S) * SS, (_my(cy) + ry * S) * SS],
               fill=color, outline=OUTLINE if outline else None, width=int(0.8 * S * SS))

def default_pose():
    return dict(
        root_x=30.0, root_y=0.0,        # body centre = (root_x, 38 + root_y)
        body_tilt=0.0,                  # degrees, + = tail down
        neck_coil=0.0, neck_extend=0.0, neck_sway=0.0, neck_retract=0.0,
        head_pitch=0.0,                 # extra degrees down
        plume_sway=0.0, blink=0.0, look_back=0.0,
        wing_amt=0.0,                   # 0 folded, 1 stretch (standing) or flight wing out
        flap=0.0,                       # flight wing angle deg (used when flying)
        flying=0.0,                     # 0 standing, 1 flight body config
        leg_far=dict(fx=-2.0, fy=86.0),   # foot targets: fx rel. to body centre, fy absolute y
        leg_near=dict(fx=5.0, fy=86.0),
        tail_ang=0.0,
        hide_near=0.0,
        fish='none', fish_size='tiny', fish_ang=-65.0, fish_slide=0.0,
        fish_x=0.0, fish_y=0.0, fish_free_ang=0.0,  # for toss (absolute)
    )

def _ik(hip, foot, a, b, pole):
    """2-bone IK in 2D. Returns joint point. pole: +1 joint bulges toward +x of hip->foot dir normal."""
    hip = np.asarray(hip, float); foot = np.asarray(foot, float)
    d = foot - hip; dist = np.hypot(*d); dist = min(dist, a + b - 0.01); dist = max(dist, 0.5)
    dirv = d / np.hypot(*d)
    x = (a * a - b * b + dist * dist) / (2 * dist)
    h = np.sqrt(max(a * a - x * x, 0.0))
    nrm = np.array([-dirv[1], dirv[0]]) * pole
    return hip + dirv * x + nrm * h

def _draw_leg(dr, hip, foot, pole):
    """hip -> rusty thigh -> dark shin -> knee knob -> dark tarsus -> toes (if foot above water)."""
    hip = np.asarray(hip, float); foot = np.asarray(foot, float)
    # thigh end: 9 cells along toward a point below hip
    thigh_end = hip + np.array([foot[0] - hip[0], abs(foot[1] - hip[1])]) * 0.0 + np.array([(foot[0] - hip[0]) * 0.18, 9.0])
    knee = _ik(thigh_end, foot, 13.5, 15.5, -pole)
    _line(dr, [hip, thigh_end], RUSTY, 3.4)
    _line(dr, [thigh_end, knee], LEGC, 2.1)
    _ell(dr, knee[0], knee[1], 1.5, 1.5, LEGC, outline=False)
    _line(dr, [knee, foot], LEGC, 1.9)
    if foot[1] < WATER_Y - 1:  # foot visible: toes dangle downward on a lifted foot
        for dx, dy in [(1.0, 3.4), (2.6, 2.8), (-0.2, 3.9)]:
            _line(dr, [foot, foot + np.array([dx, dy])], LEGC, 0.9)

def _draw_fish(dr, cx, cy, length, ang_deg, flip=1):
    """Flat fish centred at (cx,cy), nose toward +x rotated by ang."""
    a = np.deg2rad(ang_deg)
    R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    L, h = length, length * 0.42
    body = np.array([[L * 0.5, 0], [L * 0.18, -h * 0.5], [-L * 0.28, -h * 0.46],
                     [-L * 0.5, 0], [-L * 0.28, h * 0.46], [L * 0.18, h * 0.5]])
    tail = np.array([[-L * 0.42, 0], [-L * 0.72, -h * 0.55], [-L * 0.72, h * 0.55]])
    back = np.array([[L * 0.5, 0], [L * 0.18, -h * 0.5], [-L * 0.28, -h * 0.46], [-L * 0.2, -h * 0.1], [L * 0.2, -h * 0.08]])
    def xf(pts):
        return [tuple(np.array([cx, cy]) + R @ (p * np.array([flip, 1]))) for p in pts]
    _poly(dr, xf(tail), FISH2, outline=False)
    _poly(dr, xf(body), FISH, outline=False)
    _poly(dr, xf(back), FISH2, outline=False)
    eye = np.array([cx, cy]) + R @ (np.array([L * 0.32, -h * 0.08]) * np.array([flip, 1]))
    _ell(dr, eye[0], eye[1], 0.55, 0.55, INK, outline=False)

def render(pose):
    """Returns (index grid uint8 (90,120), info dict with beak tip etc.). Facing: +1 right (root on left side)."""
    p = {**default_pose(), **pose}
    img = Image.new('L', (W * SS, H * SS), WHITE)
    dr = ImageDraw.Draw(img)
    bx, by = p['root_x'], 38.0 + p['root_y']
    tilt = np.deg2rad(p['body_tilt'])
    def bt(pt):  # body-local -> world (rotate about body centre)
        v = np.asarray(pt, float)
        R = np.array([[np.cos(tilt), -np.sin(tilt)], [np.sin(tilt), np.cos(tilt)]])
        return np.array([bx, by]) + R @ v

    hip_far = bt([-4, 8.5]); hip_near = bt([3, 8.5])
    # ---- far leg (behind body)
    _draw_leg(dr, hip_far, [bx + p['leg_far']['fx'], p['leg_far']['fy']], pole=-1)
    # ---- tail
    ta = np.deg2rad(p['tail_ang'])
    tail_base = bt([-12.5, 1.5])
    tail_pts = [bt([-12, -2]), bt([-19.5, 0.5 + 3 * np.sin(ta)]), bt([-20.5, 4.5]), bt([-13, 5])]
    _poly(dr, tail_pts, DARKSLATE)
    # ---- wing: stretch or flight (behind body)
    shoulder = bt([6, -3])
    if p['wing_amt'] > 0.03:
        amt = p['wing_amt']
        if p['flying'] > 0.5:
            ph = np.sin(np.deg2rad(p['flap']))  # -1..1, + = wing raised
            tip = shoulder + np.array([-31.0, -25.0 * ph - 2.0])
            wing = [shoulder + np.array([3, 1]), shoulder + np.array([-8, -5]),
                    tip, tip + np.array([14, 4.5]), shoulder + np.array([-3, 5.5])]
            _poly(dr, wing, SLATE)
            tipd = [wing[2], wing[3], shoulder + np.array([-1, 5]),
                    shoulder + np.array([-16, -12.0 * ph - 1.0])]
            _poly(dr, tipd, DARKSLATE, outline=False)
        else:
            # standing stretch: wing extends up-back, scalloped trailing edge
            s = amt
            base = [shoulder,
                    shoulder + np.array([-18 * s, -16 * s]),
                    shoulder + np.array([-28 * s, -10 * s]),
                    shoulder + np.array([-22 * s, 1]),
                    shoulder + np.array([-15 * s, -1]),
                    shoulder + np.array([-10 * s, 4]),
                    shoulder + np.array([-2, 4])]
            _poly(dr, base, SLATE)
            tip = [base[1], base[2], base[3], shoulder + np.array([-12 * s, 0])]
            _poly(dr, tip, DARKSLATE, outline=False)
    # ---- body
    body_poly = []
    for t in np.linspace(0, 2 * np.pi, 26, endpoint=False):
        ex, ey = 16.5 * np.cos(t), 7.6 * np.sin(t)
        ey += 1.2 * np.cos(t)  # teardrop: fuller rear-top
        body_poly.append(bt([ex - 0.5, ey]))
    _poly(dr, body_poly, SLATE)
    # folded wing on body (skip when wing deployed): rear-lower dark feathers w/ scallops
    if p['wing_amt'] < 0.5:
        fw = [bt([-14, -2.0]), bt([2, -3.2]), bt([7.5, 0.5]), bt([1, 4.2]),
              bt([-3, 2.8]), bt([-5.5, 4.8]), bt([-9, 2.8]), bt([-11.5, 4.6]), bt([-15, 1.0])]
        _poly(dr, fw, DARKSLATE)
    # ---- neck
    coil, ext = p['neck_coil'], p['neck_extend']
    retract = p['neck_retract']
    nb = bt([10.5, 2.5])                       # neck base at chest
    up = dict(c1=(bx + 17.5, by - 9), c2=(bx - 0.5, by - 20), top=(bx + 7.5 - retract * 5, by - 22.5))
    co = dict(c1=(bx + 14, by - 1), c2=(bx + 18, by - 8), top=(bx + 15.0, by - 11.0))
    def lerp2(a, b, t): return tuple(np.array(a) * (1 - t) + np.array(b) * t)
    c1 = lerp2(up['c1'], co['c1'], coil); c2 = lerp2(up['c2'], co['c2'], coil)
    top = np.array(lerp2(up['top'], co['top'], coil), float)
    top[0] += p['neck_sway']
    strike_pt = np.array([bx + 27, WATER_Y - 1.5])
    if ext > 0:
        top = top * (1 - ext) + strike_pt * ext
        c1 = np.array(c1) * (1 - ext) + (nb + (strike_pt - nb) * 0.35) * ext
        c2 = np.array(c2) * (1 - ext) + (nb + (strike_pt - nb) * 0.7) * ext
    neck_pts = _bez(nb, c1, c2, top, 14)
    # chest fringe (pale zigzag) hanging at chest below neck base
    fx = np.linspace(nb[0] - 3.0, nb[0] + 4.0, 6)
    fr = [(fx[0], nb[1] - 0.5), (fx[-1], nb[1] - 0.5)]
    for i, x in enumerate(fx[::-1]):
        fr.append((x, nb[1] + (6.0 if i % 2 == 0 else 3.0)))
    _poly(dr, fr, PALE)
    _tube(dr, neck_pts, 6.6, 4.8, PALE)
    # black shoulder patch at neck/body junction (drawn over tube edge, as in sheet)
    patch = [bt([6.8, -5.2]), bt([11.4, -3.4]), bt([11.8, 1.8]), bt([8.0, 3.2]), bt([6.4, -1.0])]
    _poly(dr, patch, INK, outline=False)
    # ---- head
    hx, hy = top
    look = p['look_back']
    hdir = -1.0 if look > 0.5 else 1.0
    head_c = np.array([hx + hdir * 1.5, hy - 1.0])
    _ell(dr, head_c[0], head_c[1], 5.0, 3.4, WHITE)
    # cap: black brow band over the top of the head only (face stays white below)
    cap = [(head_c[0] - 4.6 * hdir, head_c[1] - 0.9), (head_c[0] - 2.8 * hdir, head_c[1] - 3.1),
           (head_c[0] + 1.2 * hdir, head_c[1] - 3.4), (head_c[0] + 4.8 * hdir, head_c[1] - 1.8),
           (head_c[0] + 4.4 * hdir, head_c[1] - 0.9), (head_c[0] + 1.0 * hdir, head_c[1] - 1.7),
           (head_c[0] - 2.4 * hdir, head_c[1] - 1.5)]
    _poly(dr, cap, INK, outline=False)
    # plume: 2 strands trailing behind head
    for k, (ln, droop) in enumerate([(13.5, 2.2), (11.0, 3.6)]):
        sway = p['plume_sway'] * (1 + 0.3 * k)
        pp = _bez(head_c + np.array([-3.4 * hdir, -2.4]),
                  head_c + np.array([-3.4 * hdir - ln * 0.45 * hdir, -3.4 - k * 0.7 + sway * 0.3]),
                  head_c + np.array([-3.4 * hdir - ln * 0.8 * hdir, -2.2 + droop * 0.4 + sway * 0.7]),
                  head_c + np.array([-3.4 * hdir - ln * hdir, -0.6 + droop + sway]), 10)
        _line(dr, pp, INK, 0.85)
    # beak
    pitch = np.deg2rad(16 + p['head_pitch'] + (38 * ext))
    if look > 0.5: pitch = np.deg2rad(10 + p['head_pitch'])
    bl = 13.5
    b0 = head_c + np.array([3.9 * hdir, 0.3])
    tip = b0 + np.array([np.cos(pitch) * bl * hdir, np.sin(pitch) * bl])
    perp = np.array([-np.sin(pitch) * hdir, np.cos(pitch)]) * 1.8
    _poly(dr, [b0 + perp, tip, b0 - perp * 0.75], ORANGE, outline=False)
    # eye
    ex_, ey_ = head_c + np.array([2.1 * hdir, -0.1])
    if p['blink'] > 0.5:
        _line(dr, [(ex_ - 1.1, ey_), (ex_ + 1.1, ey_)], OUTLINE, 0.8)
    else:
        _ell(dr, ex_, ey_, 1.05, 1.05, INK, outline=False)
    # ---- near leg (in front of body bottom)
    if p['hide_near'] < 0.5:
        _draw_leg(dr, hip_near, [bx + p['leg_near']['fx'], p['leg_near']['fy']], pole=-1)
    # ---- fish
    if p['fish'] == 'held':
        fl = 5.5 if p['fish_size'] == 'tiny' else 10.5
        fc = tip + np.array([np.cos(np.deg2rad(p['fish_ang'])) * fl * 0.28,
                             -np.sin(np.deg2rad(p['fish_ang'])) * fl * 0.1 + 1.2])
        if p['fish_slide'] > 0:  # swallow: fish slides along the beak toward the mouth
            mouth = b0 + np.array([np.cos(pitch) * 2.0 * hdir, np.sin(pitch) * 2.0])
            fc = fc * (1 - p['fish_slide']) + mouth * p['fish_slide']
        _draw_fish(dr, fc[0], fc[1], fl, p['fish_ang'], flip=hdir)
    elif p['fish'] == 'free':
        fl = 5.5 if p['fish_size'] == 'tiny' else 10.5
        _draw_fish(dr, p['fish_x'], p['fish_y'], fl, p['fish_free_ang'], flip=hdir)
    # ---- clip below implied water surface: the water is never drawn
    arr = np.array(img, dtype=np.uint8).reshape(H, SS, W, SS)
    arr[SURF_ROW:, :, :, :] = WHITE
    # majority downsample
    blocks = arr.transpose(0, 2, 1, 3).reshape(H, W, SS * SS)
    counts = np.stack([(blocks == k).sum(-1) for k in range(NPAL)], axis=-1)
    grid = counts.argmax(-1).astype(np.uint8)
    info = dict(beak_tip=(float(_mx(tip[0])), float(_my(tip[1]))),
                head=(float(_mx(head_c[0])), float(_my(head_c[1]))))
    return grid, info

if __name__ == '__main__':
    g, info = render({})
    print('grid:', g.shape, 'nonwhite cells:', int((g != WHITE).sum()), 'beak tip:', info['beak_tip'])
    rgb = PALETTE[g]
    Image.fromarray(rgb).resize((800, 480), Image.NEAREST).save('/tmp/rig_test.png')
