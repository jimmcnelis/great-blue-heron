"""Cycles v1.3 phase 1 — ONE performance, authored per frame at 24 fps.
Poses are built segment by segment; holds are literal copies of one pose
(held fraction is real, flicker is zero). Walk is generated in world
coordinates: feet plant at fixed world x, root passes under them, and the
head's world x is held while the body passes (steadiness by construction).
The strike target sits in the middle third; ink events are returned with
the frames so the world's causality stays in the performance data.
"""
import copy
import numpy as np
import rig13 as R

FPS = 24
N = 624  # 26.0 s

def P(**kw):
    p = R.default_pose()
    for k, v in kw.items():
        if k in ('leg_near', 'leg_far'):
            p[k].update(v)
        else:
            p[k] = v
    return p

def statue(root):
    return P(root_x=root)

def coil_pose(root):
    return P(root_x=root, body_tilt=24, coil=1.0, root_y=1.5,
             hx=25, hy=-15, head_pitch=16)

def lerp(a, b, t):
    if t <= 0:
        return copy.deepcopy(a)
    if t >= 1:
        return copy.deepcopy(b)
    out = copy.deepcopy(a)
    for k in a:
        if k in ('leg_near', 'leg_far'):
            for s in a[k]:
                out[k][s] = a[k][s] + (b[k][s] - a[k][s]) * t
        elif k in ('wing_mode', 'fish_mode'):
            out[k] = b[k] if t >= 0.5 else a[k]
        elif k == 'fish_pos':
            if a[k] is not None and b[k] is not None:
                out[k] = tuple(a[k][i] + (b[k][i] - a[k][i]) * t for i in range(2))
            else:
                out[k] = b[k] if t >= 0.5 else a[k]
        elif isinstance(a[k], (int, float)):
            bv = b.get(k, a[k])
            out[k] = a[k] + (bv - a[k]) * t
    return out

EASE = {
    'lin': lambda t: t,
    'inout': lambda t: t * t * (3 - 2 * t),
    'in': lambda t: t * t,
    'out': lambda t: 1 - (1 - t) ** 2,
    'snap': lambda t: t ** 0.4,
}

def fill(frames, f0, f1, pa, pb, ease='lin'):
    e = EASE[ease]
    for f in range(f0, min(f1, N)):
        frames[f] = lerp(pa, pb, e((f - f0) / max(f1 - f0, 1)))

def hold(frames, f0, f1, p):
    for f in range(f0, min(f1, N)):
        frames[f] = copy.deepcopy(p)

def build_episode():
    frames = [None] * N
    ink = []
    R0, R1 = 26.0, 40.0   # left third -> middle edge (fishing in the middle)

    # ---------- 0-132: statue in the left third (event beats only)
    st = statue(R0)
    hold(frames, 0, 132, st)
    for f in (53, 54):
        frames[f]['blink'] = 1.0
    sac = copy.deepcopy(st); sac['head_pitch'] = -3.0; sac['hx'] = 20.5
    fill(frames, 88, 92, st, sac, 'snap')
    hold(frames, 92, 106, sac)
    fill(frames, 106, 111, sac, st, 'out')
    for f in range(20, 61):  # plume sway, slow pendulum
        frames[f]['plume_sway'] = 1.6 * np.sin((f - 20) / 40 * np.pi)

    # ---------- 132-288: stalk walk, 3 steps with freezes
    feet = {'near': R0 + 6.0, 'far': R0 - 5.0}     # world x of planted feet
    head_world = R0 + 19.0
    root = R0
    steps = [(132, 'near'), (186, 'far'), (240, 'near')]
    stride_total = (R1 - R0) / len(steps)
    cur = statue(R0)
    for (s, leg) in steps:
        other = 'far' if leg == 'near' else 'near'
        swing_fx0 = feet[leg] - root
        for f in range(s, s + 18):
            u = (f - s) / 17
            p = copy.deepcopy(cur)
            # body pass: second half of the swing
            bu = np.clip((u - 0.35) / 0.65, 0, 1)
            bu = bu * bu * (3 - 2 * bu)
            r_now = root + stride_total * bu
            p['root_x'] = r_now
            # swinging foot: overshoot plant ahead of support foot
            plant_world = feet[other] + 13.5
            fu = u * u * (3 - 2 * u)
            p['leg_' + leg]['fx'] = (feet[leg] + (plant_world - feet[leg]) * fu) - r_now
            p['leg_' + leg]['fy'] = R.BOTTOM - 7.0 * np.sin(np.pi * u)
            p['leg_' + leg]['toe'] = -40.0 * np.sin(np.pi * u)
            p['leg_' + other]['fx'] = feet[other] - r_now
            p['hx'] = head_world - r_now          # head holds its world x
            p['root_y'] = 0.5 * np.sin(np.pi * bu)
            p['body_tilt'] = 16 + 1.2 * np.sin(np.pi * u)
            frames[f] = p
        feet[leg] = feet[other] + 13.5
        root = root + stride_total
        ink.append((s + 17, 'ripple', feet[leg], R.WATER_Y, 0.8))
        # freeze: statue at new root; head eases forward in first 10 f
        cur = statue(root)
        cur['leg_near']['fx'] = feet['near'] - root
        cur['leg_far']['fx'] = feet['far'] - root
        fz_end = s + 54 if s < 240 else 288
        hold(frames, s + 18, fz_end, cur)
        hend = root + 19.0
        for f in range(s + 18, min(s + 28, fz_end)):
            t = (f - (s + 18)) / 9
            frames[f]['hx'] = (head_world + (hend - head_world) * (t * t * (3 - 2 * t))) - root
        head_world = hend
    frames[210]['blink'] = 1.0; frames[211]['blink'] = 1.0

    # ---------- 288-447: strike + BIG-fish eat (shapes per CHART_NOTES)
    stC = statue(R1)
    stC['leg_near']['fx'] = feet['near'] - R1
    stC['leg_far']['fx'] = feet['far'] - R1
    co = coil_pose(R1)
    co['leg_near']['fx'] = feet['near'] - R1
    co['leg_far']['fx'] = feet['far'] - R1
    fill(frames, 288, 304, stC, co, 'inout')                    # deepen coil
    loaded = copy.deepcopy(co)
    loaded.update(coil=1.06, hx=26.5, hy=-13.8, head_pitch=19, body_tilt=25.5)
    fill(frames, 304, 322, co, loaded, 'lin')                   # loaded hold
    contact = P(root_x=R1 + 3, body_tilt=31, root_y=2.5, coil=0.06,
                hx=30, hy=20, head_pitch=56, gape=0.55)
    contact['neck_w'] = 0.62
    contact['leg_near']['fx'] = feet['near'] - (R1 + 3)
    contact['leg_far']['fx'] = feet['far'] - (R1 + 3)
    fill(frames, 322, 326, loaded, contact, 'in')               # release: 4 f
    frames[325]['smear'] = 1.0
    hold(frames, 326, 330, contact)                             # grab dwell
    ink.append((326, 'splash', 79.0, R.WATER_Y, 1.15))
    ink.append((326, 'ring', 79.0, R.WATER_Y, 0.8))
    withdraw = P(root_x=R1 + 1, body_tilt=22, root_y=1.0, coil=0.55,
                 hx=24, hy=-6, head_pitch=6, fish_mode='held',
                 fish_orient=88, fish_grip=0.4, fish_size=1.15)
    withdraw['neck_w'] = 0.9
    withdraw['leg_near']['fx'] = feet['near'] - (R1 + 1)
    withdraw['leg_far']['fx'] = feet['far'] - (R1 + 1)
    fill(frames, 330, 346, contact, withdraw, 'out')            # withdrawal
    for f in range(330, 346):
        frames[f]['fish_mode'] = 'held'
        frames[f]['fish_size'] = 1.15
        frames[f]['fish_orient'] = 88
    for (df, dx, dy) in ((332, 81, 68), (336, 80, 66), (340, 79, 65)):
        ink.append((df, 'drip', dx, dy, 0.8))
    # secure-shake: authored head-roll oscillation
    for f in range(346, 358):
        p = copy.deepcopy(withdraw)
        p['head_roll'] = 7.0 * np.sin((f - 346) / 11 * 2 * np.pi * 1.5) * (1 - (f - 346) / 12)
        p['head_pitch'] = 6 + 2.5 * np.sin((f - 346) / 11 * 2 * np.pi * 1.5 + 1.0)
        frames[f] = p
    dip = copy.deepcopy(withdraw); dip.update(hx=26, hy=8, head_pitch=30)
    fill(frames, 358, 366, withdraw, dip, 'inout')              # dip
    ink.append((365, 'splash', 77.0, R.WATER_Y, 0.5))
    fill(frames, 366, 374, dip, withdraw, 'inout')
    # toss-flip: windup, release, free arc computed from real bill tips
    windup = copy.deepcopy(withdraw); windup.update(hx=21, hy=-11, head_pitch=-6)
    fill(frames, 374, 380, withdraw, windup, 'inout')
    rel = copy.deepcopy(windup); rel.update(head_pitch=22, gape=0.7)
    fill(frames, 380, 382, windup, rel, 'snap')
    tip0 = R.bill_tip(frames[381])
    headback = P(root_x=R1 + 1, body_tilt=20, root_y=1.0, coil=0.7,
                 hx=20, hy=-13, head_pitch=-16, fish_mode='held',
                 fish_orient=8, fish_grip=0.15, fish_size=1.15)
    headback['leg_near']['fx'] = feet['near'] - (R1 + 1)
    headback['leg_far']['fx'] = feet['far'] - (R1 + 1)
    tip1 = R.bill_tip(headback) + np.array([-6.0, 2.0])
    for f in range(382, 390):                                   # fish airborne ~8 f
        u = (f - 382) / 7
        p = copy.deepcopy(lerp(rel, headback, u))
        pos = tip0 * (1 - u) + tip1 * u + np.array([0.0, -8.5 * 4 * u * (1 - u)])
        p['fish_mode'] = 'free'; p['fish_pos'] = tuple(pos)
        p['fish_ang'] = 80 - 74 * u
        p['gape'] = 0.7 * (1 - u) + 0.1
        frames[f] = p
    fill(frames, 390, 396, headback, headback, 'lin')
    # swallow: bulge travels gape->body, sized to READ at 1024x600
    sw = copy.deepcopy(headback); sw['fish_mode'] = 'none'
    for f in range(396, 424):
        u = (f - 396) / 27
        p = copy.deepcopy(headback)
        p['fish_mode'] = 'held' if u < 0.3 else 'none'
        p['fish_orient'] = 8
        p['bulge_pos'] = 0.05 + 0.87 * u
        p['bulge_amp'] = 0.9 * np.sin(np.pi * min(u * 1.15, 1.0)) ** 0.7
        p['head_pitch'] = -16 + 3.0 * np.sin(u * 2 * np.pi * 2)
        if f in (399, 411):
            p['gape'] = 0.25
        frames[f] = p
    stE = statue(R1)
    stE['leg_near']['fx'] = feet['near'] - R1
    stE['leg_far']['fx'] = feet['far'] - R1
    fill(frames, 424, 448, headback, stE, 'inout')              # settle

    # ---------- 448-624: closing statue, complete arc (never sliced)
    hold(frames, 448, N, stE)
    for f in (470, 545, 546, 590):
        frames[f]['blink'] = 1.0
    sac2 = copy.deepcopy(stE); sac2['head_pitch'] = -2.0; sac2['hx'] = 20.0
    fill(frames, 498, 502, stE, sac2, 'snap')
    hold(frames, 502, 516, sac2)
    fill(frames, 516, 521, sac2, stE, 'out')
    for f in range(448, N):
        if frames[f] is not None and f >= 560:
            frames[f]['plume_sway'] = 1.3 * np.sin((f - 560) / 63 * np.pi)
    return frames, ink

if __name__ == '__main__':
    fr, ink = build_episode()
    assert all(f is not None for f in fr), 'unfilled frames!'
    print('frames', len(fr), 'ink events', len(ink), ink)
