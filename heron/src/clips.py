"""Behavior clip authoring: keyframe tracks -> per-frame pose dicts + ink events.
All clips authored facing RIGHT (+1). Corpus builder mirrors for -1.
Timebase: FPS = 12.
"""
import numpy as np

FPS = 12
WATER_Y = 74
ZONE = {'L': 27.0, 'C': 60.0, 'R': 93.0}

def _ss(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)

class Anim:
    """Keyframe tracks: param -> [(t_sec, value)] with smoothstep interp; or ('fn', f)."""
    def __init__(self, dur):
        self.dur = float(dur)
        self.tracks = {}
    def set(self, param, keys):
        self.tracks[param] = sorted(keys)
        return self
    def const(self, param, v):
        self.tracks[param] = [(0.0, v), (self.dur, v)]
        return self
    def fn(self, param, f):
        self.tracks[param] = ('fn', f)
        return self
    def value(self, param, t, default=0.0):
        tr = self.tracks.get(param)
        if tr is None:
            return default
        if isinstance(tr, tuple):
            return tr[1](t)
        if t <= tr[0][0]:
            return tr[0][1]
        if t >= tr[-1][0]:
            return tr[-1][1]
        for (t0, v0), (t1, v1) in zip(tr, tr[1:]):
            if t0 <= t <= t1:
                return v0 + (v1 - v0) * _ss((t - t0) / max(t1 - t0, 1e-6))
        return tr[-1][1]

POSE_PARAMS = ['root_x', 'root_y', 'body_tilt', 'neck_coil', 'neck_extend', 'neck_sway',
               'neck_retract', 'head_pitch', 'plume_sway', 'blink', 'look_back',
               'wing_amt', 'flap', 'flying', 'tail_ang', 'hide_near',
               'leg_far.fx', 'leg_far.fy', 'leg_near.fx', 'leg_near.fy',
               'fish_ang', 'fish_slide', 'fish_x', 'fish_y', 'fish_free_ang']
FISH_PARAMS = ['fish', 'fish_size']

def sample_clip(anim, consts, rng, micro=True, micro_scale=1.0):
    """Returns (poses, events, beak) — beak filled later by renderer pass (None here)."""
    n = int(round(anim.dur * FPS))
    ph1, ph2, ph3 = rng.uniform(0, 6.28, 3)
    poses = []
    for i in range(n):
        t = i / FPS
        p = dict(consts)
        for par in POSE_PARAMS:
            if par in anim.tracks:
                v = anim.value(par, t)
                if '.' in par:
                    a, b = par.split('.')
                    p.setdefault(a, {})[b] = v
                else:
                    p[par] = v
        if micro:
            ms = micro_scale
            still = (1.0 - 0.75 * p.get('neck_coil', 0.0)) * ms      # statuesque while aiming
            fly = p.get('flying', 0.0)
            if fly < 0.5:
                p['root_y'] = p.get('root_y', 0.0) + 0.30 * np.sin(2 * np.pi * t / 4.1 + ph1) * still
            p['neck_sway'] = p.get('neck_sway', 0.0) + 0.45 * np.sin(2 * np.pi * t / 5.7 + ph2) * still
            p['plume_sway'] = p.get('plume_sway', 0.0) + 0.9 * np.sin(2 * np.pi * t / 3.3 + ph3) * ms
            p['head_pitch'] = p.get('head_pitch', 0.0) + 1.1 * np.sin(2 * np.pi * t / 6.9 + ph1) * still
        poses.append(p)
    return poses

def _blink_track(anim, rng, every=(2.5, 6.0)):
    t = rng.uniform(*every) * 0.5
    keys = [(0.0, 0.0)]
    while t < anim.dur - 0.3:
        keys += [(t, 0.0), (t + 0.04, 1.0), (t + 0.13, 1.0), (t + 0.17, 0.0)]
        t += rng.uniform(*every)
    keys.append((anim.dur, 0.0))
    anim.set('blink', keys)

def base_anim(dur, zone_x):
    a = Anim(dur)
    a.const('root_x', zone_x)
    for par, v in [('root_y', 0.0), ('body_tilt', 0.0), ('neck_coil', 0.0), ('neck_extend', 0.0),
                   ('neck_sway', 0.0), ('neck_retract', 0.0), ('head_pitch', 0.0), ('plume_sway', 0.0),
                   ('look_back', 0.0), ('wing_amt', 0.0), ('flap', 0.0), ('flying', 0.0),
                   ('tail_ang', 0.0), ('hide_near', 0.0), ('fish_ang', -60.0), ('fish_slide', 0.0),
                   ('leg_far.fx', -2.0), ('leg_far.fy', 86.0), ('leg_near.fx', 5.0), ('leg_near.fy', 86.0)]:
        a.const(par, v)
    return a

# ---------------------------------------------------------------- idle
def idle_clip(zone='L', dur=20.0, seed=0, oneleg=False):
    rng = np.random.default_rng(seed)
    zx = ZONE[zone]
    a = base_anim(dur, zx)
    # head turns: neck_sway excursions
    keys = [(0.0, 0.0)]
    t = rng.uniform(2.0, 5.0)
    while t < dur - 3.0:
        amp = rng.uniform(1.2, 2.6) * rng.choice([-1, 1])
        hold = rng.uniform(1.2, 3.2)
        keys += [(t, 0.0), (t + 0.7, amp), (t + 0.7 + hold, amp), (t + 1.4 + hold, 0.0)]
        t += hold + rng.uniform(3.0, 7.0)
    keys.append((dur, 0.0))
    a.set('neck_sway', keys)
    # look-backs
    if rng.random() < 0.8:
        t0 = rng.uniform(3.0, max(4.0, dur - 6.0))
        hold = rng.uniform(1.8, 3.6)
        a.set('look_back', [(0, 0), (t0, 0), (t0 + 0.45, 1), (t0 + 0.45 + hold, 1),
                            (t0 + 0.9 + hold, 0), (dur, 0)])
    # head dips (scanning the water)
    if rng.random() < 0.7:
        t0 = rng.uniform(2.0, max(3.0, dur - 5.0))
        a.set('head_pitch', [(0, 0), (t0, 0), (t0 + 0.6, rng.uniform(8, 16)),
                             (t0 + 2.2, rng.uniform(8, 16)), (t0 + 2.9, 0), (dur, 0)])
    _blink_track(a, rng)
    consts = {'fish': 'none', 'fish_size': 'tiny'}
    if oneleg:
        t_in, t_out = 1.6, dur - 1.6
        a.set('hide_near', [(0, 0), (t_in - 0.4, 0), (t_in, 1), (t_out, 1), (t_out + 0.4, 0), (dur, 0)])
        a.set('leg_far.fx', [(0, -2), (t_in, 1.5), (t_out, 1.5), (dur, -2)])
        a.set('root_y', [(0, 0), (t_in, 0.9), (t_out, 0.9), (dur, 0)])
    poses = sample_clip(a, consts, rng)
    return poses, []

# ---------------------------------------------------------------- walk
def walk_clip(x_from='L', x_to='C', seed=0):
    rng = np.random.default_rng(seed)
    xa, xb = ZONE[x_from], ZONE[x_to]
    dist = abs(xb - xa)
    speed = rng.uniform(8.6, 10.4)          # cells/sec, deliberate
    travel = dist / speed
    dur = travel + 1.6
    cyc_t = 1.6
    duty = 0.62
    stride = speed * duty * cyc_t           # rel. foot travel during stance (zero slip)
    dirn = np.sign(xb - xa)
    a = base_anim(dur, xa)
    def rootx(t):
        s = _ss(np.clip((t - 0.8) / travel, 0, 1)) if travel > 0 else 1.0
        return xa + (xb - xa) * s
    a.fn('root_x', rootx)
    events = []
    n = int(round(dur * FPS))
    # procedural gait per frame
    consts = {'fish': 'none', 'fish_size': 'tiny'}
    poses = []
    prev_swing = {'far': False, 'near': False}
    for i in range(n):
        t = i / FPS
        p = dict(consts)
        rx = rootx(t)
        p['root_x'] = rx
        moving = 0.15 < ((t - 0.8) / travel if travel > 0 else 1) < 0.98
        amp = 1.0 if moving else 0.0
        phase = (t - 0.8) / cyc_t
        for name, off in [('far', 0.0), ('near', 0.5)]:
            cyc = (phase + off) % 1.0
            if cyc < (1 - duty):            # swing
                s = cyc / (1 - duty)
                fxr = (-stride / 2 + stride * _ss(s)) * dirn
                fy = 86 - 21 * np.sin(np.pi * np.clip(s, 0, 1)) ** 0.85 * amp
                fxr = fxr if amp > 0 else (-2.0 if name == 'far' else 5.0)
                if amp == 0: fy = 86.0
                swing = True
            else:                            # stance
                s = (cyc - (1 - duty)) / duty
                fxr = (stride / 2 - stride * s) * dirn
                fy = 86.0
                swing = False
                if prev_swing[name] and amp > 0:
                    events.append({'f': i, 'type': 'step', 'x': float(rx + fxr)})
            prev_swing[name] = swing
            p[f'leg_{name}'] = {'fx': float(fxr), 'fy': float(fy)}
        p['root_y'] = 0.45 * np.sin(2 * np.pi * phase * 2) * amp - 0.3 * amp
        p['neck_sway'] = -1.1 * np.sin(2 * np.pi * phase + 0.7) * amp
        p['plume_sway'] = 0.8 * np.sin(2 * np.pi * phase * 2 + 1.2) * amp
        p['blink'] = 1.0 if (i % 47 == 30) else 0.0
        poses.append(p)
    return poses, events

# ---------------------------------------------------------------- strike
def strike_clip(size='tiny', seed=0, miss=False):
    rng = np.random.default_rng(seed)
    zx = ZONE['C']
    aim_t = rng.uniform(1.6, 2.6)
    strike_t = aim_t + 0.55
    dur = strike_t + (3.9 if not miss else 2.2)
    a = base_anim(dur, zx)
    a.set('neck_coil', [(0, 0), (aim_t - 0.6, 0), (aim_t, 1.0), (strike_t, 0.92),
                        (strike_t + 0.5, 0.55), (strike_t + 1.6, 0.3), (dur - 0.7, 0.12), (dur, 0.0)])
    a.set('head_pitch', [(0, 0), (aim_t, 17), (strike_t, 20), (strike_t + 0.5, 6),
                         (strike_t + 1.5, -9), (strike_t + 2.2, -9), (dur, 0)])
    a.set('neck_extend', [(0, 0), (strike_t - 0.09, 0), (strike_t - 0.03, 0.55),
                          (strike_t + 0.03, 1.0), (strike_t + 0.30, 0.25), (strike_t + 0.55, 0.0), (dur, 0)])
    if miss:
        a.set('neck_sway', [(0, 0), (strike_t + 0.4, 0), (strike_t + 0.55, 1.6),
                            (strike_t + 0.7, -1.6), (strike_t + 0.85, 0.8), (strike_t + 1.05, 0), (dur, 0)])
    _blink_track(a, rng, every=(3.5, 7.0))
    consts = {'fish': 'none', 'fish_size': size}
    poses = sample_clip(a, consts, rng, micro=True)
    n = len(poses)
    events = [{'f': int(strike_t * FPS), 'type': 'splash', 'x': float(zx + 27)}]
    if not miss:
        f0 = int((strike_t + 0.30) * FPS)
        toss_t = strike_t + rng.uniform(0.9, 1.4)
        gulp_t = toss_t + 0.85
        for i, p in enumerate(poses):
            t = i / FPS
            if i >= f0:
                p['fish'] = 'held'
                # pendulum sway of the catch, decaying
                p['fish_ang'] = -62 + 16 * np.sin(2 * np.pi * (t - strike_t) * 1.6) * np.exp(-(t - strike_t) / 1.1)
            if t >= gulp_t:
                s = np.clip((t - gulp_t) / 0.45, 0, 1)
                p['fish_slide'] = float(s)
                p['fish_ang'] = -25.0
            if t >= gulp_t + 0.5:
                p['fish'] = 'none'
        # drip window: from catch until just after the gulp
        events.append({'f': f0, 'f_end': int((gulp_t + 0.9) * FPS), 'type': 'drips', 'x': 0.0})
        # toss is patched in by the corpus builder (needs beak tips): mark it
        events.append({'f': int(toss_t * FPS), 'type': 'toss', 'x': 0.0})
    return poses, events

def aim_relax_clip(seed=0):
    rng = np.random.default_rng(seed)
    dur = rng.uniform(4.5, 6.0)
    a = base_anim(dur, ZONE['C'])
    a.set('neck_coil', [(0, 0), (1.4, 0), (2.2, 1.0), (dur - 1.6, 1.0), (dur - 0.7, 0), (dur, 0)])
    a.set('head_pitch', [(0, 0), (2.2, 15), (dur - 1.6, 15), (dur - 0.7, 0), (dur, 0)])
    _blink_track(a, rng)
    return sample_clip(a, {'fish': 'none', 'fish_size': 'tiny'}, rng), []

# ---------------------------------------------------------------- stretch
def stretch_clip(seed=0):
    rng = np.random.default_rng(seed)
    zone = rng.choice(['L', 'R', 'C'])
    dur = rng.uniform(4.6, 5.8)
    a = base_anim(dur, ZONE[zone])
    a.set('wing_amt', [(0, 0), (1.2, 0), (2.0, 1.0), (dur - 1.6, 1.0), (dur - 0.7, 0), (dur, 0)])
    a.set('body_tilt', [(0, 0), (2.0, -2.5), (dur - 1.6, -2.5), (dur - 0.7, 0), (dur, 0)])
    _blink_track(a, rng)
    return sample_clip(a, {'fish': 'none', 'fish_size': 'tiny'}, rng), []

# ---------------------------------------------------------------- flight
def takeoff_clip(zone='R', seed=0):
    rng = np.random.default_rng(seed)
    zx = ZONE[zone]
    dur = 4.6
    a = base_anim(dur, zx)
    launch = 0.9
    a.set('root_y', [(0, 0), (launch - 0.35, 2.6), (launch, 1.0), (launch + 1.5, -13),
                     (dur, -15)])
    a.fn('root_x', lambda t: zx + 78 * _ss(np.clip((t - launch) / (dur - launch - 0.3), 0, 1)))
    a.set('flying', [(0, 0), (launch + 0.15, 0), (launch + 0.45, 1), (dur, 1)])
    a.set('neck_coil', [(0, 0), (launch, 0.3), (launch + 0.7, 0.6), (dur, 0.6)])
    a.set('neck_retract', [(0, 0), (launch + 0.7, 1.0), (dur, 1.0)])
    a.fn('flap', lambda t: 58 * np.sin(2 * np.pi * 2.1 * max(t - launch, 0)) if t > launch else 0.0)
    a.set('wing_amt', [(0, 0), (launch, 0), (launch + 0.3, 1.0), (dur, 1.0)])
    # legs: dangle below the rising body, then streamline trailing behind it
    a.set('leg_far.fx', [(0, -2), (1.2, -4), (2.4, -23), (dur, -23)])
    a.set('leg_near.fx', [(0, 5), (1.2, 3), (2.4, -26), (dur, -26)])
    a.set('leg_far.fy', [(0, 86), (1.3, 78), (2.2, 44), (3.2, 33), (dur, 32)])
    a.set('leg_near.fy', [(0, 86), (1.3, 80), (2.2, 46), (3.2, 35), (dur, 34)])
    _blink_track(a, rng)
    poses = sample_clip(a, {'fish': 'none', 'fish_size': 'tiny'}, rng)
    events = [{'f': int(launch * FPS), 'type': 'takeoff', 'x': float(zx + 2)}]
    return poses, events

def flyin_clip(zone='L', seed=0):
    rng = np.random.default_rng(seed)
    zx = ZONE[zone]
    dur = 5.4
    touch = 3.6
    a = base_anim(dur, zx)
    a.fn('root_x', lambda t: zx - 82 * (1 - _ss(np.clip(t / (touch - 0.2), 0, 1))))
    a.set('root_y', [(0, -14), (touch - 1.1, -13), (touch, 0.8), (touch + 0.35, -0.4), (dur, 0)])
    a.set('flying', [(0, 1), (touch - 0.1, 1), (touch + 0.25, 0), (dur, 0)])
    a.set('neck_coil', [(0, 0.6), (touch - 0.5, 0.45), (touch + 0.4, 0.1), (dur, 0)])
    a.set('neck_retract', [(0, 1.0), (touch - 0.3, 0.6), (touch + 0.4, 0), (dur, 0)])
    a.fn('flap', lambda t: (58 * np.sin(2 * np.pi * 2.1 * t) if t < touch - 0.3
                            else 58 * np.sin(2 * np.pi * 2.1 * (touch - 0.3)) * max(0.0, 1 - (t - touch + 0.3) / 0.5)))
    a.set('wing_amt', [(0, 1), (touch + 0.45, 1), (touch + 0.95, 0), (dur, 0)])
    a.set('body_tilt', [(0, -3), (touch - 0.5, -8), (touch + 0.3, 0), (dur, 0)])
    # legs trail streamlined behind the body, then swing down late to plant
    a.set('leg_far.fx', [(0, -24), (2.6, -23), (3.3, -8), (touch, -2), (dur, -2)])
    a.set('leg_near.fx', [(0, -26), (2.6, -25), (3.3, -2), (touch, 5), (dur, 5)])
    a.set('leg_far.fy', [(0, 31), (2.6, 34), (3.3, 66), (touch, 86), (dur, 86)])
    a.set('leg_near.fy', [(0, 33), (2.6, 36), (3.3, 68), (touch, 86), (dur, 86)])
    a.set('plume_sway', [(0, 0), (touch, 0), (touch + 0.15, 2.6), (touch + 0.6, -1.4),
                         (touch + 1.1, 0.6), (dur, 0)])
    _blink_track(a, rng)
    poses = sample_clip(a, {'fish': 'none', 'fish_size': 'tiny'}, rng)
    events = [{'f': int(touch * FPS), 'type': 'landing', 'x': float(zx + 2)}]
    return poses, events

# ---------------------------------------------------------------- alert (presence response)
def alert_clip(zone='L', seed=0):
    """APPROACH response: the bird notices the viewer — stands tall, head up, freezes.
    ~2.3 s. Ends near-canonical so the state machine can chain walk/strike after it."""
    rng = np.random.default_rng(seed)
    dur = 2.3
    a = base_anim(dur, ZONE[zone])
    a.set('root_y', [(0, 0), (0.28, -0.9), (1.9, -0.9), (dur, -0.3)])
    a.set('head_pitch', [(0, 0), (0.28, -8), (1.9, -8), (dur, -3)])
    a.set('neck_sway', [(0, 0), (0.2, 0.9), (0.5, 0.2), (dur, 0)])
    a.set('plume_sway', [(0, 0), (0.35, 2.0), (0.9, -0.8), (1.5, 0.3), (dur, 0)])
    a.set('blink', [(0, 0), (1.55, 0), (1.6, 1), (1.72, 1), (1.78, 0), (dur, 0)])
    return sample_clip(a, {'fish': 'none', 'fish_size': 'tiny'}, rng, micro_scale=0.22), []

# ---------------------------------------------------------------- turn (facing change)
def turn_clip(zone='R', seed=0):
    """Standing turn in place. Poses are a plain idle; corpus_build applies a
    horizontal squash sweep (1 -> -1) around the root column, which reads as a
    quick flat-storybook turn and lands exactly on the mirrored standing pose."""
    return idle_clip(zone=zone, dur=1.4, seed=seed)

# ---------------------------------------------------------------- registry
def clip_specs():
    specs = []
    for zone in ['L', 'C']:
        for s in range(10):
            specs.append((f'idle_{zone}_{s}', 'idle', dict(zone=zone, dur=20.0, seed=100 + s * 7 + (0 if zone == 'L' else 3))))
        for s in range(6):
            specs.append((f'oneleg_{zone}_{s}', 'idle', dict(zone=zone, dur=18.0, seed=300 + s * 11 + (0 if zone == 'L' else 5), oneleg=True)))
    for a_, b_ in [('L', 'C'), ('C', 'R'), ('L', 'R')]:
        for s in range(5):
            specs.append((f'walk_{a_}{b_}_{s}', 'walk', dict(x_from=a_, x_to=b_, seed=500 + s * 13)))
    for s in range(6):
        specs.append((f'strike_tiny_{s}', 'strike', dict(size='tiny', seed=700 + s * 17)))
    for s in range(4):
        specs.append((f'strike_big_{s}', 'strike', dict(size='big', seed=760 + s * 19)))
    for s in range(2):
        specs.append((f'strike_miss_{s}', 'strike', dict(size='tiny', seed=790 + s, miss=True)))
    for s in range(4):
        specs.append((f'aimrelax_{s}', 'aim', dict(seed=820 + s * 7)))
    for s in range(5):
        specs.append((f'stretch_{s}', 'stretch', dict(seed=900 + s * 23)))
    for zone in ['L', 'C', 'R']:
        for s in range(2):
            specs.append((f'takeoff_{zone}_{s}', 'takeoff', dict(zone=zone, seed=1000 + s * 29)))
    for zone in ['L', 'C', 'R']:
        for s in range(2):
            specs.append((f'flyin_{zone}_{s}', 'flyin', dict(zone=zone, seed=1200 + s * 31)))
    for zone in ['L', 'R']:
        for s in range(2):
            specs.append((f'turn_{zone}_{s}', 'turn', dict(zone=zone, seed=1400 + s * 37)))
    specs.append(('empty', 'empty', {}))
    return specs

BUILDERS = {'idle': idle_clip, 'walk': walk_clip, 'strike': strike_clip,
            'aim': aim_relax_clip, 'stretch': stretch_clip,
            'takeoff': takeoff_clip, 'flyin': flyin_clip, 'turn': turn_clip}

def build_clip(kind, kwargs):
    if kind == 'empty':
        return [dict(fish='none', fish_size='tiny') for _ in range(240)], []
    return BUILDERS[kind](**kwargs)
