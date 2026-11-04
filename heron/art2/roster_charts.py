"""Roster chart evaluator — movement-charts.yaml -> rig13_r4 pose tracks.

Implements every chart in movement-charts.yaml (canonical cycles only,
24 fps) as sequences of rig13_r4 pose dicts, using the KEPT v1.3 rig
vocabulary. Chart-to-rig mapping (documented in ROSTER_REPORT.md):

  neck_coil      -> coil (1:1; anchors: idle 0.85 = rig statue, strike
                    max 1.0/1.06 = rig coil/loaded poses)
  head_pitch     -> head_pitch (1:1; anchors: strike 17 ~ rig coil 16,
                    withdrawal 6 = rig 6, dip 26 ~ rig 30)
  body_tilt      -> rig body_tilt via two-anchor linear map:
                    chart -33 (idle diagonal) = rig 16 (statue),
                    chart -3 (flight) = rig 2 (kept flight pose).
                    rig = 16 - 0.4667 * (chart + 33). (Strike rock under
                    this map is +1.4 deg, inside the chart's own <=3 deg
                    lead/lag cap.)
  beak_open      -> gape (1:1)
  neck_bulge_*   -> bulge_* (1:1)
  flap/flap_tip  -> flap/flap_tip (1:1; flight target -42 sits inside
                    the chart's -52..+34 range)
  yaw            -> yaw (rig draws through its authored stops)
  head_roll      -> head_roll (1:1)
  root_x/root_y  -> 1:1 design units
  leg fy keys    -> RELATIVE to ground: rig fy = BOTTOM + key
  neck_extend / neck_retract / head_yaw / neck_sway have no rig param:
    - neck extension/retraction is keyframed through the rig's proven
      neck anchors (statue / coil / loaded / contact / withdraw /
      headback / upright / flight), the same poses the kept episode
      (cycles13_r4) uses; generic coil-only keys get hx/hy from the
      coil->anchor curve below.
    - head_yaw becomes a gesture (hx shift + head_roll lean); the kept
      bridge (prep_poses.keypoints_for) draws head orientation from
      BODY yaw stops only, so a head-only turn is not drawable as a
      turn. Noted per chart in the report.
    - neck_sway becomes an hx overlay.
  fish_*, blink, smear are tracked in the pose dicts (chart data) but
  have no channel in the art2 conditioning bridge; they do not change
  the bird render. Fish/ink are the procedural layer's, excluded by
  the environment law (bird-only renders).
"""
import copy, json, math, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', 'src13'))
import rig13_r4 as R

BOTTOM = R.BOTTOM

EASE = {
    'lin': lambda t: t,
    'inout': lambda t: t * t * (3 - 2 * t),
    'in': lambda t: t * t,
    'out': lambda t: 1 - (1 - t) ** 2,
    'snap': lambda t: t ** 0.4,
}

# ---- proven neck anchors (hx, hy) from cycles13_r4 / prep_poses --------
ANCH = {
    'statue':   dict(hx=19.0, hy=-28.0),
    'coil':     dict(hx=25.0, hy=-15.0),
    'loaded':   dict(hx=26.5, hy=-13.8),
    'contact':  dict(hx=30.0, hy=20.0),
    'withdraw': dict(hx=24.0, hy=-6.0),
    'headback': dict(hx=20.0, hy=-13.0),
    'upright':  dict(hx=13.2, hy=-25.7),
    'dip':      dict(hx=26.0, hy=8.0),
    'flight':   dict(hx=24.0, hy=-14.0),
    'flightS':  dict(hx=23.0, hy=-17.0),   # takeoff fold, chart coil 0.6
    'doze':     dict(hx=10.0, hy=-16.0),
}
COIL_CURVE = [  # (coil, hx, hy) generic neck solve for coil-only keys
    (0.03, 13.2, -25.7), (0.25, 15.0, -26.6), (0.85, 19.0, -28.0),
    (1.00, 25.0, -15.0), (1.06, 26.5, -13.8),
]

def coil_anchor(coil):
    c = COIL_CURVE
    if coil <= c[0][0]:
        return c[0][1], c[0][2]
    for (c0, x0, y0), (c1, x1, y1) in zip(c, c[1:]):
        if coil <= c1:
            t = (coil - c0) / (c1 - c0)
            return x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
    return c[-1][1], c[-1][2]

def tilt(chart_tilt):
    return 16.0 - 0.4667 * (chart_tilt + 33.0)

def statue(root_x, chart_tilt=-33.0, pitch=4.0):
    p = R.default_pose()
    p['root_x'] = float(root_x)
    p['body_tilt'] = tilt(chart_tilt)
    p['head_pitch'] = float(pitch)
    return p

def flight_pose(root_x):
    p = statue(root_x)
    p.update(wing_mode='flight', body_tilt=2.0, coil=0.9, hx=24.0, hy=-14.0,
             head_pitch=-2.0, flap=-42.0, flap_tip=10.0,
             leg_near=dict(fx=-37.0, fy=53.0, toe=-55.0),
             leg_far=dict(fx=-34.0, fy=50.0, toe=-55.0))
    return p

# ---- track machinery ----------------------------------------------------
def _leaves(partial, prefix=()):
    for k, v in partial.items():
        if isinstance(v, dict):
            yield from _leaves(v, prefix + (k,))
        else:
            yield prefix + (k,), v

def _get(state, path):
    d = state
    for k in path:
        d = d[k]
    return d

def _set(state, path, val):
    d = state
    for k in path[:-1]:
        d = d[k]
    d[path[-1]] = val

class Track:
    def __init__(self, start):
        self.state = copy.deepcopy(start)
        self.frames = []

    def seg(self, n, target=None, ease='inout', overlay=None, switch_at=None):
        """Append n frames interpolating state -> target (partial, nested).
        Frame i uses t=(i+1)/n eased, so the last frame lands on target.
        String/None leaves switch once the eased t passes switch_at
        (default 0.5; pass 0.0 to switch from the first frame)."""
        start = copy.deepcopy(self.state)
        tgt = copy.deepcopy(self.state)
        if target:
            for path, v in _leaves(target):
                _set(tgt, path, v)
        ez = EASE[ease]
        sw = 0.5 if switch_at is None else switch_at
        for i in range(n):
            t = ez((i + 1) / n)
            p = copy.deepcopy(start)
            if target:
                for path, v in _leaves(target):
                    a = _get(start, path)
                    if isinstance(a, (int, float)) and isinstance(v, (int, float)):
                        _set(p, path, a + (v - a) * t)
                    else:
                        _set(p, path, v if t >= sw else a)
            if overlay:
                overlay(p, i, n)
            self.frames.append(p)
        self.state = tgt
        return self

    def hold(self, n, overlay=None):
        return self.seg(n, None, 'lin', overlay)

    def keys(self, **kw):
        """Instantly set state leaves (dotted paths via __)."""
        for k, v in kw.items():
            _set(self.state, tuple(k.split('__')), v)
        return self

def with_coil_anchor(state_partial):
    """If a partial keys coil but not hx/hy, add the anchor-curve hx/hy."""
    if 'coil' in state_partial and 'hx' not in state_partial:
        hx, hy = coil_anchor(state_partial['coil'])
        state_partial = dict(state_partial, hx=hx, hy=hy)
    return state_partial

def pulse_overlay(param, frames_at, amp, width=2):
    """Overlay factory: adds amp to pose[param] on frames_at (+width-1)."""
    def ov(p, i, n):
        for f0 in frames_at:
            if f0 <= i < f0 + width:
                _set(p, tuple(param.split('__')),
                     _get(p, tuple(param.split('__'))) + amp)
    return ov

def sine_overlay(param, amp, cycles, decay=0.0, phase=0.0):
    def ov(p, i, n):
        u = (i + 1) / n
        _set(p, tuple(param.split('__')),
             _get(p, tuple(param.split('__')))
             + amp * math.sin(2 * math.pi * cycles * u + phase) * (1 - decay * u))
    return ov

# ==========================================================================
# CHART BUILDERS — one function per chart in movement-charts.yaml.
# Each returns a Track. Frame counts asserted against canonical_frames.
# ==========================================================================

def ch_idle_hunt():
    """480f held statue with the chart's discrete event script.
    head_yaw events render as the episode's saccade gesture (hx/pitch);
    blink has no conditioning channel (tracked only)."""
    tr = Track(statue(26.0))
    sac_on = {'hx': 20.5, 'head_pitch': -3.0}   # episode saccade gesture
    tr.hold(71)
    tr.seg(3, {'blink': 1.0}, 'lin'); tr.keys(blink=0.0)
    tr.hold(66)
    tr.seg(3, sac_on, 'lin')                    # gaze_saccade_right (ballistic)
    tr.hold(93)
    tr.seg(6, {'head_roll': 14.0}, 'inout')      # head_roll_tilt (a lean)
    tr.hold(66)
    tr.seg(6, {'head_roll': 0.0}, 'inout')       # head_roll_release
    tr.seg(3, {'hx': 19.0, 'head_pitch': 4.0}, 'lin')  # saccade back
    tr.hold(97)
    tr.seg(3, {'blink': 1.0}, 'lin'); tr.keys(blink=0.0)
    tr.hold(63)
    assert len(tr.frames) == 480, len(tr.frames)
    return tr

def ch_head_saccade():
    """3f atomic gaze shift (canonical 35 deg gesture, as idle_hunt's)."""
    tr = Track(statue(26.0))
    tr.seg(3, {'hx': 20.5, 'head_pitch': -3.0}, 'lin')
    assert len(tr.frames) == 3
    return tr

def ch_head_turn():
    """18f head-only turn. head_yaw 150 has no bridge path: rendered as
    the maximal drawable gesture (hx drawn in, head_roll lean). The
    anticipate dip is a RELATIVE +4 (chart keys pitch 4; read as the
    dip its name announces)."""
    tr = Track(statue(40.0))
    tr.seg(3, {'head_pitch': 8.0}, 'inout')                       # anticipate_dip
    tr.seg(6, {'hx': 12.0, 'head_roll': 8.0, 'head_pitch': 0.0},
           'inout')                                              # travel_out
    tr.hold(6)                                                   # hold_look
    tr.seg(3, {'hx': 19.0, 'head_roll': 0.0, 'head_pitch': 4.0},
           'snap')                                               # travel_back
    assert len(tr.frames) == 18
    return tr

def ch_strike():
    """52f. Starts at idle coil (statue pose in the middle third)."""
    tr = Track(statue(40.0))
    # coil_deepen 12f: chart keys coil 1.0, tilt -30, pitch 17
    tr.seg(12, with_coil_anchor({'coil': 1.0, 'body_tilt': tilt(-30.0),
                                 'head_pitch': 17.0}), 'inout')
    # loaded_hold 12f: chart holds coil; note + episode settle DEEPER
    tr.seg(12, {'coil': 1.06, 'hx': 26.5, 'hy': -13.8,
                'head_pitch': 19.0}, 'lin')
    # release 4f: authored spacing 25/60/100% of neck travel, contact f4;
    # beak_open ramps across frames 3-4 (chart); smear frame = phase f3.
    start = copy.deepcopy(tr.state)
    contact = copy.deepcopy(start)
    for path, v in _leaves({'coil': 0.15, 'hx': 30.0, 'hy': 20.0,
                            'head_pitch': 56.0, 'neck_w': 0.62,
                            'root_x': 43.0, 'body_tilt': tilt(-27.0),
                            'root_y': 2.5}):
        _set(contact, path, v)
    cum = [0.25, 0.60, 1.0, 1.0]
    for i in range(4):
        p = copy.deepcopy(start)
        for path, v in _leaves({'coil': 0.15, 'hx': 30.0, 'hy': 20.0,
                                'head_pitch': 56.0, 'neck_w': 0.62,
                                'root_x': 43.0, 'body_tilt': tilt(-27.0),
                                'root_y': 2.5}):
            a = _get(start, path)
            _set(p, path, a + (v - a) * cum[i])
        p['gape'] = (0.0, 0.0, 0.5, 1.0)[i]     # chart: opens ~1/30s pre-impact
        if i == 2:
            p['smear'] = 1.0                    # the one authored smear frame
        tr.frames.append(p)
    tr.state = contact
    tr.keys(gape=1.0)
    # grab_dwell 2f: bill closes ON the prey
    tr.seg(2, {'gape': 0.0, 'fish_mode': 'held', 'fish_orient': 90.0,
               'fish_grip': 0.35, 'fish_size': 1.15}, 'lin', switch_at=0.0)
    # withdrawal 12f: chart keys coil 0.7, pitch 6; decelerating (ease out)
    tr.seg(12, {'coil': 0.7, 'hx': 24.0, 'hy': -6.0, 'head_pitch': 6.0,
                'neck_w': 0.9, 'root_x': 41.0, 'root_y': 1.0,
                'body_tilt': tilt(-31.0)}, 'out')
    # recover_to_coil 10f: chart keys coil 0.85, pitch 0
    tr.seg(10, with_coil_anchor({'coil': 0.85, 'head_pitch': 0.0,
                                 'neck_w': 1.0, 'root_x': 40.0,
                                 'root_y': 0.0, 'body_tilt': tilt(-33.0)}),
           'inout')
    assert len(tr.frames) == 52, len(tr.frames)
    return tr

def _withdraw_state():
    p = statue(41.0)
    p.update(coil=0.7, hx=24.0, hy=-6.0, head_pitch=6.0, neck_w=0.9,
             root_y=1.0, body_tilt=tilt(-31.0), fish_mode='held',
             fish_orient=90.0, fish_grip=0.35, fish_size=1.15)
    return p

def ch_swallow():
    """118f, starting from the strike's withdrawal pose (fish held)."""
    tr = Track(_withdraw_state())
    # secure_shake 12f: episode's authored head-roll oscillation
    def shake(p, i, n):
        u = (i + 1) / n
        p['head_roll'] = 7.0 * math.sin(u * 2 * math.pi * 1.5) * (1 - 0.3 * u)
        p['head_pitch'] = 6.0 + 2.5 * math.sin(u * 2 * math.pi * 1.5 + 1.0)
    tr.hold(12, overlay=shake)
    # dip 18f: down 9 / up 9 (chart keys pitch 26, coil 0.55 at the dip)
    tr.seg(9, {'hx': 26.0, 'hy': 8.0, 'head_pitch': 26.0, 'coil': 0.55},
           'inout')
    tr.seg(9, {'hx': 24.0, 'hy': -6.0, 'head_pitch': 6.0, 'coil': 0.7},
           'inout')
    # toss_flip 16f: flick up-back (pitch -> -14, snap, 4f), then arc to
    # headback; fish free at f4, re-caught head-first at f14, bill
    # closes f15-16 (gape track authored on the frames).
    tr.seg(4, {'hx': 21.0, 'hy': -11.0, 'head_pitch': -14.0}, 'snap')
    tr.seg(12, {'hx': 20.0, 'hy': -13.0, 'head_pitch': -16.0,
                'coil': 0.7}, 'inout')
    for i in range(16):
        f = tr.frames[12 + 18 + i]
        if i >= 3:
            f['fish_mode'] = 'free'
            f['gape'] = 0.7
        if i >= 13:
            f['fish_mode'] = 'held'; f['fish_orient'] = 0.0
            f['gape'] = (0.35, 0.1, 0.0)[min(i - 13, 2)]
    # work_back 18f: 3 head jerks (frames 1, 7, 13) walk the fish back
    jerk = pulse_overlay('hx', [0, 6, 12], 1.5)
    jerkp = pulse_overlay('head_pitch', [0, 6, 12], 3.0)
    def both(p, i, n):
        jerk(p, i, n); jerkp(p, i, n)
        p['fish_grip'] = 0.35 + 0.5 * (i + 1) / n
    tr.hold(18, overlay=both)
    # head_back 8f: chart keys pitch -24, coil 0.35
    tr.seg(8, {'hx': 17.0, 'hy': -20.0, 'head_pitch': -24.0,
               'coil': 0.35}, 'inout')
    # swallow_travel 22f: -> UPRIGHT; bulge envelope per the chart note
    # (amp 0->1 f1-8, hold, ->0 f18-22; pos 0->1 across; +0.15 pulses
    # at f9 and f15; neck shimmy = hx overlay, 2 cycles).
    def travel(p, i, n):
        f = i + 1
        if f <= 8:
            amp = f / 8.0
        elif f <= 17:
            amp = 1.0
        else:
            amp = max(0.0, 1.0 - (f - 17) / 5.0)
        if f in (9, 15):
            amp = min(1.0, amp + 0.15)
        p['bulge_amp'] = amp
        p['bulge_pos'] = f / 22.0
        p['hx'] += 0.8 * math.sin(2 * math.pi * 2 * f / 22.0)
        if f >= 4:
            p['fish_mode'] = 'none'
    tr.seg(22, {'hx': 13.2, 'hy': -25.7, 'head_pitch': 2.0,
                'coil': 0.05, 'neck_w': 0.95}, 'inout', overlay=travel)
    tr.keys(bulge_amp=0.0, bulge_pos=0.0)
    # settle 24f: -> idle base (chart keys pitch 0, coil 0.85); beak
    # claps at f4 and f11 (0.5, 2f each); plume follow-through decays.
    clap = pulse_overlay('gape', [3, 10], 0.5)
    def settle_ov(p, i, n):
        clap(p, i, n)
        if i < 10:
            p['plume_sway'] = 1.5 * math.sin(2 * math.pi * (i + 1) / 10) \
                * (1 - (i + 1) / 10)
    tr.seg(24, with_coil_anchor({'coil': 0.85, 'head_pitch': 0.0,
                                 'neck_w': 1.0, 'root_x': 40.0,
                                 'root_y': 0.0, 'body_tilt': tilt(-33.0)}),
           'inout', overlay=settle_ov)
    tr.keys(root_x=40.0)
    assert len(tr.frames) == 118, len(tr.frames)
    return tr

def ch_step_cycle():
    """24f, near leg steps. Body pass (root +14) is distributed across
    weight_commit + lift_fold per the chart's body_pass note; the head
    is world-locked through the pass (hx compensates root advance).
    Loop: end state == start state with root translated +14."""
    tr = Track(statue(26.0))
    root0 = 26.0
    near_plant = root0 + 6.0    # world x of near foot at cycle start
    far_plant = root0 - 5.0
    head_world = root0 + 19.0

    def frame(u_pass, near_fx_mode, near_fy, near_toe):
        p = copy.deepcopy(tr.state)
        root = root0 + 14.0 * u_pass
        p['root_x'] = root
        p['hx'] = head_world - root
        p['leg_far']['fx'] = far_plant - root
        if near_fx_mode == 'planted':
            p['leg_near']['fx'] = near_plant - root
        elif near_fx_mode == 'advance':
            pass
        p['leg_near']['fy'] = near_fy
        p['leg_near']['toe'] = near_toe
        return p

    # weight_commit 4f: pass begins (root advances, smoothstepped over
    # the 10 pass frames), root_y -> +0.3, stepping foot still planted
    pass_frames = []
    for i in range(4):
        u = EASE['inout']((i + 1) / 10)
        p = frame(u, 'planted', BOTTOM, 0.0)
        p['root_y'] = 0.3 * (i + 1) / 4
        pass_frames.append(p)
    # lift_fold 6f: pass completes; foot folds up (-7, toe -55)
    for i in range(6):
        u = EASE['inout']((4 + i + 1) / 10)
        q = (i + 1) / 6
        p = frame(u, 'planted', BOTTOM - 7.0 * EASE['inout'](q),
                  -55.0 * EASE['inout'](q))
        p['root_y'] = 0.3
        pass_frames.append(p)
    tr.frames.extend(pass_frames)
    st = copy.deepcopy(pass_frames[-1])
    tr.state = st
    # advance 8f: folded leg swings +14 world; root still
    adv0 = copy.deepcopy(tr.state)
    for i in range(8):
        p = copy.deepcopy(adv0)
        q = EASE['inout']((i + 1) / 8)
        p['leg_near']['fx'] = adv0['leg_near']['fx'] + 14.0 * q
        tr.frames.append(p)
    tr.state = copy.deepcopy(tr.frames[-1])
    # place 6f: unfold, descend toe-first, root_y settles back
    pl0 = copy.deepcopy(tr.state)
    for i in range(6):
        p = copy.deepcopy(pl0)
        q = EASE['inout']((i + 1) / 6)
        p['leg_near']['fy'] = pl0['leg_near']['fy'] + (BOTTOM - pl0['leg_near']['fy']) * q
        p['leg_near']['toe'] = pl0['leg_near']['toe'] * (1 - q)
        p['root_y'] = 0.3 * (1 - q)
        tr.frames.append(p)
    tr.state = copy.deepcopy(tr.frames[-1])
    assert len(tr.frames) == 24, len(tr.frames)
    return tr

def ch_turn():
    """72f, yaw 0 -> 180 through the authored stops. head_yaw counter-
    rotation renders as a fading gesture (hx/roll) — the head's world
    yaw is constant in the chart; the gesture tracks head_yaw/150."""
    tr = Track(statue(26.0))
    def gesture(hyaw):
        return {'hx': 19.0 - 5.0 * hyaw / 150.0,
                'head_roll': 5.0 * hyaw / 150.0}
    g = gesture(150.0)
    tr.seg(4, g, 'lin')                                        # gaze_saccade
    for yaw_t, hyaw_t in ((45.0, 105.0), (90.0, 60.0), (135.0, 15.0)):
        tgt = {'yaw': yaw_t}; tgt.update(gesture(hyaw_t))
        tr.seg(15, tgt, 'lin')                                 # pivot steps
    tgt = {'yaw': 180.0}; tgt.update(gesture(0.0))
    tr.seg(11, tgt, 'lin')                                     # pivot_step_4
    def plume(p, i, n):
        if i < 10:
            p['plume_sway'] = 2.0 * math.sin(2 * math.pi * (i + 1) / 10) \
                * (1 - (i + 1) / 12)
    tr.seg(12, {'hx': 19.0, 'head_roll': 0.0}, 'inout',
           overlay=plume)                                      # realign_settle
    assert len(tr.frames) == 72, len(tr.frames)
    return tr

def ch_alert():
    """61f: check, snap, held accent (one gaze saccade inside), settle."""
    tr = Track(statue(26.0))
    tr.seg(4, with_coil_anchor({'coil': 0.8, 'head_pitch': 5.0}),
           'inout')                                            # check_dip
    tr.seg(3, {'coil': 0.25, 'hx': 15.0, 'hy': -26.6,
               'body_tilt': tilt(-39.0), 'root_y': -0.9,
               'head_pitch': -8.0}, 'snap')                    # snap_tall
    sac = pulse_overlay('hx', [19], 1.5)
    sacp = pulse_overlay('head_pitch', [19], -3.0)
    def hold_ov(p, i, n):
        if i in (19, 20, 21):
            p['hx'] += 1.5; p['head_pitch'] -= 3.0
    tr.hold(36, overlay=hold_ov)                               # accent_hold
    tr.seg(18, with_coil_anchor({'coil': 0.85, 'body_tilt': tilt(-33.0),
                                 'root_y': 0.0, 'head_pitch': 0.0}),
           'inout')                                            # settle
    assert len(tr.frames) == 61, len(tr.frames)
    return tr

def _flap_curve(f, down=5, up=7, hi=34.0, lo=-52.0, tip_hi=30.0,
                tip_lo=-38.0, env=1.0):
    """One flight beat sampled at frame f (0-based, start-inclusive so
    the curve is exactly periodic): down `down` frames hi->lo, up `up`
    frames lo->hi. Returns (flap, flap_tip) with the tip following the
    root's normalised curve delayed 2 frames, on the tip's own range.
    env scales the stroke amplitude around the top value."""
    n = down + up
    def norm(g):
        g %= n
        if g < down:
            return EASE['inout'](g / down)
        return 1.0 - EASE['inout']((g - down) / up)
    flap = hi + (lo - hi) * norm(f)
    tip = tip_hi + (tip_lo - tip_hi) * norm(f - 2)
    return hi + (flap - hi) * env, tip_hi + (tip - tip_hi) * env

def ch_flight_cycle():
    """12f loop. Fixed pose = the kept flight target (folded S neck,
    trailing legs); flap curve authored 5f down / 7f up, tip lag 2f."""
    tr = Track(flight_pose(58.0))
    for f in range(12):
        p = copy.deepcopy(tr.state)
        flap, tip = _flap_curve(f)
        p['flap'], p['flap_tip'] = flap, tip
        if f in (9, 10):
            pass  # wing_amt dip has no conditioning path (folded wing)
        tr.frames.append(p)
    assert len(tr.frames) == 12
    return tr

def ch_glide():
    """24f held glide: flap +12 shallow dihedral on the flight pose."""
    p = flight_pose(58.0)
    p['flap'] = 12.0; p['flap_tip'] = 12.0
    tr = Track(p)
    tr.frames = [copy.deepcopy(p) for _ in range(24)]
    tr.state = copy.deepcopy(p)
    assert len(tr.frames) == 24
    return tr

def ch_takeoff():
    """96f: crouch, leap (first beat begins feet-planted), dangle/fold,
    3.5 climb beats with the chart's amplitude envelope."""
    tr = Track(statue(40.0))
    tr.seg(12, with_coil_anchor({'coil': 0.3, 'root_y': 2.6}),
           'inout')                                            # crouch_deepen
    # leap_first_beat 12f: one flight beat; feet planted f1-4, legs
    # extend and leave at f5; neck extends straight.
    leap0 = copy.deepcopy(tr.state)
    for i in range(12):
        p = copy.deepcopy(leap0)
        flap, tip = _flap_curve(i)
        p['wing_mode'] = 'flight'
        p['flap'], p['flap_tip'] = flap, tip
        u = (i + 1) / 12
        p['coil'] = 0.3 + (0.15 - 0.3) * u
        hx, hy = coil_anchor(p['coil'])
        p['hx'], p['hy'] = hx, hy
        if i >= 4:
            v = (i - 3) / 8
            p['root_y'] = 2.6 + (-2.0 - 2.6) * v
            p['leg_near']['fy'] = BOTTOM + 4.0 * v
            p['leg_far']['fy'] = BOTTOM + 4.0 * v
        tr.frames.append(p)
    tr.state = copy.deepcopy(tr.frames[-1])
    # dangle_and_fold 30f: legs dangle (f1-12) then swing back to
    # trail (f13-30); neck folds to the chart's coil 0.6 flight S.
    d0 = copy.deepcopy(tr.state)
    for i in range(30):
        p = copy.deepcopy(d0)
        u = (i + 1) / 30
        p['root_y'] = -2.0 + (-10.0 + 2.0) * EASE['inout'](u)
        p['coil'] = 0.15 + (0.6 - 0.15) * u
        p['hx'] = d0['hx'] + (23.0 - d0['hx']) * u
        p['hy'] = d0['hy'] + (-17.0 - d0['hy']) * u
        p['head_pitch'] = -2.0
        if i < 12:
            v = (i + 1) / 12
            p['leg_near']['fy'] = (BOTTOM + 4.0) - 30.0 * v
            p['leg_far']['fy'] = (BOTTOM + 4.0) - 30.0 * v
        else:
            v = (i - 11) / 18
            p['leg_near']['fy'] = 62.0 + (53.0 - 62.0) * v
            p['leg_far']['fy'] = 62.0 + (50.0 - 62.0) * v
            p['leg_near']['fx'] = 6.0 + (-37.0 - 6.0) * v
            p['leg_far']['fx'] = -5.0 + (-34.0 + 5.0) * v
            p['leg_near']['toe'] = -55.0 * v
            p['leg_far']['toe'] = -55.0 * v
        flap, tip = _flap_curve(i % 12)
        p['flap'], p['flap_tip'] = flap, tip
        tr.frames.append(p)
    tr.state = copy.deepcopy(tr.frames[-1])
    # climb_beats 42f: 3.5 beats, envelope 1.0/1.0/0.9/0.8; neck settles
    # to the full flight anchor; body rises, stays in frame.
    c0 = copy.deepcopy(tr.state)
    for i in range(42):
        p = copy.deepcopy(c0)
        beat = i // 12
        env = (1.0, 1.0, 0.9, 0.8)[min(beat, 3)]
        flap, tip = _flap_curve(i % 12, env=env)
        p['flap'], p['flap_tip'] = flap, tip
        u = (i + 1) / 42
        p['root_y'] = -10.0 + (-22.0 + 10.0) * u
        p['coil'] = 0.6 + (0.9 - 0.6) * u
        p['hx'] = 23.0 + (24.0 - 23.0) * u
        p['hy'] = -17.0 + (-14.0 + 17.0) * u
        p['body_tilt'] = 2.0
        tr.frames.append(p)
    tr.state = copy.deepcopy(tr.frames[-1])
    assert len(tr.frames) == 96, len(tr.frames)
    return tr

def ch_landing():
    """120f: glide approach, flare, legs reach, touchdown (root_y
    keyframe blips per the chart note), two momentum steps, fold."""
    tr = Track(flight_pose(26.0))
    tr.state['root_y'] = -12.0
    tr.state['flap'] = 12.0; tr.state['flap_tip'] = 12.0
    tr.frames = []
    start = copy.deepcopy(tr.state)
    # approach_glide 24f: descend, tilt -> chart -12
    tr.state = copy.deepcopy(start)
    tr.seg(24, {'root_y': -4.0, 'body_tilt': tilt(-12.0)}, 'inout')
    # flare 12f: one braking stroke, wings high and held; tail fan has
    # no conditioning channel (tracked only)
    tr.seg(12, {'flap': 48.0, 'flap_tip': 40.0, 'body_tilt': tilt(-18.0),
                'root_y': -1.0, 'tail_fan': 1.0}, 'inout')
    # legs_reach 18f: dangle (f1-8) then reach forward (f9-18)
    lr0 = copy.deepcopy(tr.state)
    for i in range(18):
        p = copy.deepcopy(lr0)
        if i < 8:
            v = (i + 1) / 8
            p['leg_near']['fy'] = 53.0 + (88.0 - 53.0) * v
            p['leg_far']['fy'] = 50.0 + (88.0 - 50.0) * v
            p['root_y'] = -1.0 + 1.0 * v
        else:
            v = (i - 7) / 10
            p['leg_near']['fx'] = -37.0 + (12.0 + 37.0) * v
            p['leg_far']['fx'] = -34.0 + (8.0 + 34.0) * v
            p['leg_near']['fy'] = 88.0; p['leg_far']['fy'] = 88.0
            p['root_y'] = 0.0
        p['leg_near']['toe'] = -55.0 + 55.0 * (i + 1) / 18
        p['leg_far']['toe'] = p['leg_near']['toe']
        tr.frames.append(p)
    tr.state = copy.deepcopy(tr.frames[-1])
    # touchdown 12f: root_y +0.8 at f2, -0.4 at f7, 0 at f12 (chart note)
    td0 = copy.deepcopy(tr.state)
    blips = {1: 0.8, 6: -0.4}
    for i in range(12):
        p = copy.deepcopy(td0)
        if i in blips:
            p['root_y'] = blips[i]
        elif 2 <= i <= 5:
            p['root_y'] = 0.8 * (1 - (i - 1) / 5)
        elif 7 <= i <= 11:
            p['root_y'] = -0.4 * (1 - (i - 6) / 5)
        tr.frames.append(p)
    tr.state = copy.deepcopy(tr.frames[-1])
    tr.state['root_y'] = 0.0
    # momentum_steps 24f: two short steps (near, then far), root +7 ea,
    # head world-locked via hx as in step_cycle
    head_world = tr.state['root_x'] + tr.state['hx']
    plants = {'leg_near': tr.state['root_x'] + tr.state['leg_near']['fx'],
              'leg_far': tr.state['root_x'] + tr.state['leg_far']['fx']}
    for s, leg in enumerate(('leg_near', 'leg_far')):
        other = 'leg_far' if leg == 'leg_near' else 'leg_near'
        s0 = copy.deepcopy(tr.state)
        for i in range(12):
            p = copy.deepcopy(s0)
            q = EASE['inout']((i + 1) / 12)
            root = s0['root_x'] + 7.0 * q
            p['root_x'] = root
            p['hx'] = head_world - root
            p[other]['fx'] = plants[other] - root
            # swing: lift and advance together, set down at the end
            p[leg]['fx'] = (plants[leg] - root) + 10.0 * q
            p[leg]['fy'] = BOTTOM - 5.0 * math.sin(math.pi * q)
            p[leg]['toe'] = -30.0 * math.sin(math.pi * q)
            tr.frames.append(p)
        tr.state = copy.deepcopy(tr.frames[-1])
        plants[leg] = tr.state['root_x'] + tr.state[leg]['fx']
    # fold_and_unfold 30f: wing folds (flight outline until f19, folded
    # from f20 — fold completes 20f in, >= 10f after touchdown), neck
    # unfolds flight S -> hunting coil across the whole phase.
    fu0 = copy.deepcopy(tr.state)
    for i in range(30):
        p = copy.deepcopy(fu0)
        u = (i + 1) / 30
        p['coil'] = 0.9 + (0.85 - 0.9) * u
        p['hx'] = fu0['hx'] + (19.0 - fu0['hx']) * u
        p['hy'] = fu0['hy'] + (-28.0 - fu0['hy']) * u
        p['head_pitch'] = -2.0 + (4.0 + 2.0) * u
        p['body_tilt'] = 2.0 + (tilt(-33.0) - 2.0) * u
        if i < 19:
            p['wing_mode'] = 'flight'
            p['flap'] = 48.0 + (12.0 - 48.0) * (i + 1) / 19
            p['flap_tip'] = 40.0 + (12.0 - 40.0) * (i + 1) / 19
        else:
            p['wing_mode'] = 'folded'
            p['flap'] = 0.0; p['flap_tip'] = 0.0
        tr.frames.append(p)
    tr.state = copy.deepcopy(tr.frames[-1])
    assert len(tr.frames) == 120, len(tr.frames)
    return tr

def ch_stretch():
    """168f: same-side (near) wing + leg stretch. Weight shifts toward
    the stance (far) side: root_x -2 (documented reading of the
    chart's '+2 toward stance side' in profile coords). The wing
    extension renders through the flight outline at droop flap —
    wing_amt itself has no folded-mode channel in the bridge."""
    tr = Track(statue(26.0))
    tr.seg(18, {'root_x': 24.0}, 'inout')                       # weight_shift
    tr.seg(12, with_coil_anchor({'coil': 0.95, 'head_pitch': 10.0}),
           'inout')                                            # tuck_head
    tr.seg(24, {'wing_mode': 'flight', 'flap': 46.0,
                'flap_tip': 30.0}, 'inout', switch_at=0.0)     # wing_extend
    tr.seg(18, {'leg_near': {'fx': -20.0, 'fy': BOTTOM - 34.0,
                             'toe': 25.0}}, 'inout')           # leg_extend
    tr.hold(48)                                                # full_hold
    tr.seg(12, {'leg_near': {'fy': BOTTOM}}, 'inout')          # leg_retract
    tr.seg(18, {'wing_mode': 'folded', 'flap': 0.0,
                'flap_tip': 0.0}, 'inout', switch_at=1.0)      # wing_fold
    def plume(p, i, n):
        if i < 8:
            p['plume_sway'] = 1.5 * math.sin(2 * math.pi * (i + 1) / 8) \
                * (1 - (i + 1) / 18)
    # settle: chart keys neck only; the leg's fx also returns so the
    # chart's stated end state (idle base pose) is actually reached.
    tr.seg(18, with_coil_anchor({'coil': 0.85, 'head_pitch': 0.0,
                                 'leg_near': {'fx': 6.0, 'toe': 0.0}}),
           'inout', overlay=plume)
    assert len(tr.frames) == 168, len(tr.frames)
    return tr

def ch_oneleg():
    """36f ENTER chart: near leg folds up under the belly, tucked.
    Bridge-geometry correction (documented): the chart's literal
    fold target (fx 3, fy -38) puts the foot within 0.1 units of the
    hip pivot (fy 50 == hip height), where the rig's leg IK is
    singular and the knee explodes off-frame. Target moved to the
    chart's stated DRAWING — foot tucked FORWARD under the belly,
    visible against the body feathers: fx 8, fy -34 (d(hip,foot)
    ~6.6, a deep but finite fold)."""
    tr = Track(statue(26.0))
    tr.seg(12, {'root_y': 0.4}, 'inout')                       # weight_shift
    tr.seg(24, {'leg_near': {'fx': 8.0, 'fy': BOTTOM - 34.0,
                             'toe': -70.0}}, 'inout')          # fold_up
    assert len(tr.frames) == 36, len(tr.frames)
    return tr

def ch_doze():
    """96f ENTER chart: sink into the doze S, slow eye-close (blink
    tracked only — no conditioning channel), held doze."""
    tr = Track(statue(26.0))
    tr.seg(36, {'coil': 0.9, 'hx': 10.0, 'hy': -16.0,
                'head_pitch': 14.0, 'root_y': 0.6}, 'inout')   # sink
    tr.seg(12, {'blink': 1.0}, 'lin')                          # eye_close
    tr.hold(48)                                                # doze_hold
    assert len(tr.frames) == 96, len(tr.frames)
    return tr

def _nibble(param='head_pitch', amp=3.0):
    def ov(p, i, n):
        p[param] += amp * math.sin(2 * math.pi * (i + 1) / 6.0)
    return ov

def ch_preen():
    """240f bout. Head-yaw reaches render as hx/hy gestures toward the
    tract being worked (no head-yaw channel in the bridge)."""
    tr = Track(statue(26.0))
    def dip(p, i, n):
        if i < 4:
            p['head_pitch'] += 3.0 * math.sin(math.pi * (i + 1) / 4)
    tr.seg(24, with_coil_anchor({'coil': 0.95, 'head_pitch': 18.0,
                                 'hx': 12.0, 'hy': -19.0}),
           'inout', overlay=dip)                               # reach_shoulder
    tr.hold(8, overlay=_nibble())                              # nibble_beat_1
    tr.hold(16)                                                # hold_pose
    tr.hold(8, overlay=_nibble())                              # nibble_beat_2
    def draw_ov(p, i, n):
        u = (i + 1) / n
        p['gape'] = 0.4 * math.sin(math.pi * u)
    tr.hold(20, overlay=draw_ov)                               # draw_through
    tr.seg(18, {'head_pitch': 24.0, 'hx': 15.0, 'hy': -21.0},
           'inout')                                            # reposition
    tr.hold(16, overlay=_nibble())                             # nibble_chest
    tr.seg(18, {'wing_mode': 'flight', 'flap': 20.0,
                'flap_tip': 14.0}, 'inout', switch_at=0.0)     # wing_half_open
    tr.hold(16, overlay=_nibble())                             # nibble_wing
    def shake(p, i, n):
        u = (i + 1) / n
        p['root_x'] += 0.7 * math.sin(2 * math.pi * (i + 1) / 6.0) * (1 - u)
        if i >= 8:
            p['plume_sway'] = 1.2 * math.sin(2 * math.pi * (i - 7) / 8)
    tr.seg(12, {'wing_mode': 'folded', 'flap': 0.0,
                'flap_tip': 0.0}, 'lin', overlay=shake,
           switch_at=1.0)                                      # shake
    tr.seg(24, with_coil_anchor({'coil': 0.85, 'head_pitch': 0.0}),
           'inout')                                            # settle
    tr.hold(60)                                                # tail_hold
    assert len(tr.frames) == 240, len(tr.frames)
    return tr

def ch_scratch():
    """48f: near leg up beside the body, head lowers to meet it,
    3 quick foot strokes, withdraw."""
    tr = Track(statue(26.0))
    tr.seg(14, {'leg_near': {'fx': 9.0, 'fy': BOTTOM - 52.0}},
           'inout')                                            # leg_raise
    tr.seg(8, with_coil_anchor({'coil': 0.8, 'head_pitch': 22.0}),
           'inout')                                            # head_lower
    def strokes(p, i, n):
        s = i % 4
        p['leg_near']['fy'] -= 3.0 * math.sin(math.pi * s / 3.0) \
            if s else 0.0
    tr.hold(12, overlay=strokes)                               # scratch_beats
    tr.seg(14, with_coil_anchor({'coil': 0.85, 'head_pitch': 0.0,
                                 'leg_near': {'fx': 6.0, 'fy': BOTTOM}}),
           'inout')                                            # withdraw
    assert len(tr.frames) == 48, len(tr.frames)
    return tr

CHARTS = {
    'idle_hunt': ch_idle_hunt,
    'head_saccade': ch_head_saccade,
    'head_turn': ch_head_turn,
    'strike': ch_strike,
    'swallow': ch_swallow,
    'step_cycle': ch_step_cycle,
    'turn': ch_turn,
    'alert': ch_alert,
    'takeoff': ch_takeoff,
    'flight_cycle': ch_flight_cycle,
    'glide': ch_glide,
    'landing': ch_landing,
    'stretch': ch_stretch,
    'oneleg': ch_oneleg,
    'doze': ch_doze,
    'preen': ch_preen,
    'scratch': ch_scratch,
}

CANONICAL = {'idle_hunt': 480, 'head_saccade': 3, 'head_turn': 18,
             'strike': 52, 'swallow': 118, 'step_cycle': 24, 'turn': 72,
             'alert': 61, 'takeoff': 96, 'flight_cycle': 12, 'glide': 24,
             'landing': 120, 'stretch': 168, 'oneleg': 36, 'doze': 96,
             'preen': 240, 'scratch': 48}

def build_all():
    out = {}
    for name, fn in CHARTS.items():
        tr = fn()
        assert len(tr.frames) == CANONICAL[name], (name, len(tr.frames))
        out[name] = tr.frames
        print(f'{name}: {len(tr.frames)} frames')
    print('total', sum(len(v) for v in out.values()))
    return out

if __name__ == '__main__':
    tracks = build_all()
    dst = sys.argv[1] if len(sys.argv) > 1 else 'pose_tracks.json'
    def safe(p):
        return {k: ({kk: float(vv) for kk, vv in v.items()}
                    if isinstance(v, dict) else
                    ([float(x) for x in v] if isinstance(v, tuple) else
                     (float(v) if isinstance(v, (int, float)) else v)))
                for k, v in p.items()}
    with open(dst, 'w') as f:
        json.dump({k: [safe(p) for p in v] for k, v in tracks.items()}, f)
    print('wrote', dst)
