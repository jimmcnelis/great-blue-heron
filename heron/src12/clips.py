"""Heron v1.2 — signature-cycle clip library (pose space).

Every behavior is authored ONCE as a timing chart (movement-charts.yaml,
with measured corrections from the pier/kayak/patio footage library) and
rendered verbatim. No rng, no noise, no universal ease: each segment names
its own spacing. The player schedules clips; it never perturbs them.

Conventions:
- Poses are flat dicts here ('leg_near.fx'); unflatten() restores the rig's
  nested pose dict.
- Segments: (n_frames, targets, sets). A target is (value, spacing) or a
  plain value (segment default spacing 'eio' is FORBIDDEN — every segment
  passes its spacing explicitly; default here is 'lin').
- Spacings: 'lin', 'ein' (t^2), 'eout' (1-(1-t)^2), 'eio' (smoothstep),
  ('frac', [cumulative fractions per frame]) for authored step spacing.
- Frame-exact events (smear frame, shakes, claps, the toss arc) are applied
  as per-frame patches after segment interpolation — chart data, not code
  patches in the renderer.
"""
import copy
import numpy as np
import rig

# ------------------------------------------------------------------ engine
FLAT_KEYS = ['root_x', 'root_y', 'body_tilt', 'neck_coil', 'neck_extend',
             'neck_sway', 'neck_retract', 'head_pitch', 'plume_sway', 'blink',
             'yaw', 'head_yaw', 'head_roll', 'beak_open', 'wing_amt', 'flap',
             'flap_tip', 'flying', 'warble', 'tail_ang', 'smear',
             'neck_bulge_pos', 'neck_bulge_amp', 'fish_grip', 'fish_orient',
             'fish_x', 'fish_y', 'fish_free_ang',
             'leg_far.fx', 'leg_far.fy', 'leg_far.toe',
             'leg_near.fx', 'leg_near.fy', 'leg_near.toe']
DISCRETE = ['fish', 'fish_size']

def flatten(pose):
    out = {}
    for k in FLAT_KEYS:
        if '.' in k:
            leg, sub = k.split('.')
            out[k] = float(pose[leg][sub])
        else:
            out[k] = float(pose[k])
    for k in DISCRETE:
        out[k] = pose[k]
    return out

def unflatten(flat):
    pose = rig.default_pose()
    for k, v in flat.items():
        if '.' in k:
            leg, sub = k.split('.')
            pose[leg][sub] = v
        else:
            pose[k] = v
    return pose

def base_flat(**over):
    """idle_hunt base pose (chart): coil .85, tilt -33, at nominal root 60."""
    p = flatten(rig.default_pose())
    p.update(dict(root_x=60.0, root_y=0.0, body_tilt=-33.0, neck_coil=0.85,
                  head_pitch=18.0, leg_far_fx=None))
    p.pop('leg_far_fx', None)
    p.update({'leg_far.fx': -2.0, 'leg_far.fy': 86.0, 'leg_far.toe': 0.0,
              'leg_near.fx': 5.0, 'leg_near.fy': 86.0, 'leg_near.toe': 0.0})
    p.update(over)
    return p

def _space(kind, t):
    if kind == 'lin':
        return t
    if kind == 'ein':
        return t * t
    if kind == 'eout':
        return 1.0 - (1.0 - t) ** 2
    if kind == 'eio':
        return t * t * (3.0 - 2.0 * t)
    raise ValueError(kind)

def build(start, segments, patches=None):
    """segments: list of dicts {n, to:{key:(val,spacing)|val}, set:{}, hold:bool}
    Returns a list of flat pose dicts (length = sum of n)."""
    frames = []
    cur = dict(start)
    for seg in segments:
        n = seg['n']
        if seg.get('set'):
            cur.update(seg['set'])
        targets = seg.get('to', {})
        starts = {k: cur[k] for k in targets}
        for i in range(n):
            t = (i + 1) / n
            f = dict(cur)
            for k, spec in targets.items():
                if isinstance(spec, tuple) and spec and spec[0] == 'frac':
                    f[k] = starts[k] + (spec[1][i] - 0.0) * 1.0 if False else \
                        starts[k] + (spec[2] - starts[k]) * spec[1][i]
                elif isinstance(spec, tuple):
                    val, sp = spec
                    f[k] = starts[k] + (val - starts[k]) * _space(sp, t)
                else:
                    f[k] = starts[k] + (spec - starts[k]) * t
            frames.append(f)
        for k, spec in targets.items():
            if isinstance(spec, tuple) and spec and spec[0] == 'frac':
                cur[k] = spec[2]
            elif isinstance(spec, tuple):
                cur[k] = spec[0]
            else:
                cur[k] = spec
    if patches:
        for idx, patch in patches.items():
            frames[idx].update(patch)
    return frames

def S(n, to=None, set_=None, **kw):
    d = {'n': n, 'to': to or {}}
    if set_:
        d['set'] = set_
    d.update(kw)
    return d

def HOLD(n):
    return {'n': n, 'to': {}}

def osc_patch(frames, start, param, values):
    """Authored per-frame values (shakes, claps, blips) as patches."""
    return {start + i: {param: v} for i, v in enumerate(values)}

def merge_patches(*patch_dicts):
    out = {}
    for d in patch_dicts:
        for k, v in d.items():
            out.setdefault(k, {}).update(v)
    return out

# ------------------------------------------------------------------ idle
def idle_hunt(variant='a'):
    """480f held statue with a discrete event script (chart: idle_hunt).
    NO continuous motion anywhere — holds are literal frame repeats."""
    b = base_flat()
    if variant == 'a':
        segs = [HOLD(71), S(2, {'blink': (1.0, 'lin')}), S(1, {'blink': (0.0, 'lin')}),
                HOLD(66), S(3, {'head_yaw': (35.0, 'lin')}), HOLD(93),
                S(6, {'head_roll': (14.0, 'eio')}), HOLD(66),
                S(6, {'head_roll': (0.0, 'eio')}), S(3, {'head_yaw': (0.0, 'lin')}),
                HOLD(97), S(2, {'blink': (1.0, 'lin')}), S(1, {'blink': (0.0, 'lin')}),
                HOLD(63)]
    elif variant == 'b':
        segs = [HOLD(149), S(2, {'blink': (1.0, 'lin')}), S(1, {'blink': (0.0, 'lin')}),
                HOLD(57), S(3, {'head_yaw': (-35.0, 'lin')}), HOLD(189),
                S(2, {'blink': (1.0, 'lin')}), S(1, {'blink': (0.0, 'lin')}),
                HOLD(76)]
    else:  # c: the one eased head move in the canon — a slow scan
        segs = [HOLD(299), S(24, {'head_yaw': (-50.0, 'eio')}), HOLD(48),
                S(3, {'head_yaw': (0.0, 'lin')}), HOLD(103),
                S(2, {'blink': (1.0, 'lin')}), S(1, {'blink': (0.0, 'lin')})]
    frames = build(b, segs)
    assert len(frames) == 480, len(frames)
    return frames

def head_turn():
    """18f: head-only facing change through the head's 3/4 stops."""
    b = base_flat()
    segs = [S(3, {'head_pitch': (22.0, 'eio')}),
            S(6, {'head_yaw': (150.0, 'lin')}),
            HOLD(6),
            S(3, {'head_yaw': (0.0, 'lin'), 'head_pitch': (18.0, 'lin')})]
    return build(b, segs)

# ------------------------------------------------------------------ strike
def _strike(size='tiny', miss=False, big=False):
    b = base_flat()
    deepen = 16 if big else 12
    holdn = 16 if big else 12
    segs = [S(deepen, {'neck_coil': (1.0, 'eio'), 'body_tilt': (-30.0, 'eio'),
                       'head_pitch': (17.0, 'eio')}),
            HOLD(holdn),
            # release: authored accelerating fractions; frame 3 = smear +
            # beak opening; frame 4 = contact
            S(4, {'neck_extend': ('frac', [0.25, 0.60, 1.0, 1.0], 1.0),
                  'neck_coil': (0.15, 'lin')}),
            S(2, {}, set_={'fish': 'none' if miss else 'held',
                           'fish_size': size, 'fish_grip': 0.35,
                           'fish_orient': 90.0}),
            S(12, {'neck_extend': (0.0, 'eout'), 'neck_coil': (0.7, 'eout'),
                   'head_pitch': (6.0, 'eout'), 'beak_open': (0.0, 'lin')}),
            S(10, {'neck_coil': (0.85, 'eio'), 'head_pitch': (18.0, 'eio'),
                   'body_tilt': (-33.0, 'eio')})]
    if miss:
        # head_shake replaces recover: 12f decaying sway, then settle 10
        segs = segs[:-1] + [
            S(12, {'head_pitch': (10.0, 'eio')}),
            S(10, {'neck_coil': (0.85, 'eio'), 'head_pitch': (18.0, 'eio'),
                   'body_tilt': (-33.0, 'eio'), 'neck_sway': (0.0, 'lin')})]
    frames = build(b, segs)
    rel = deepen + holdn  # release segment start frame
    patches = {rel + 2: {'smear': 1.0, 'beak_open': 0.55},
               rel + 3: {'beak_open': 1.0},
               rel + 4: {'beak_open': 0.0}}
    if miss:
        shake0 = rel + 4 + 2 + 12
        sway = [1.6, -1.6, 1.6, -1.2, 1.2, -1.2, 0.8, -0.8, 0.8, -0.4, 0.4, -0.2]
        patches = merge_patches(patches, osc_patch(frames, shake0, 'neck_sway', sway))
    for i, p in patches.items():
        frames[i].update(p)
    return frames

def strike():
    return _strike('tiny')

def strike_big():
    return _strike('big', big=True)

def strike_miss():
    return _strike('tiny', miss=True)

# ------------------------------------------------------------------ swallow
def _toss_patches(frames, start, size, quick=False):
    """The toss-flip as chart data: flick up-back, fish FREE on a small
    ballistic arc rotating ~180 deg, re-caught HEAD-FIRST (orient 0).
    Airborne window compressed to ~6 frames per the MEASURED toss on
    Jimmy's kayak bird (~0.2 s airborne, footage #6). Anchor = the beak
    tip of the flick-end pose, measured through the rig."""
    flick = frames[start + 3]
    _g, info = rig.render(unflatten(flick))
    tipx = (info['beak_tip'][0] - rig.W / 2.0) / rig.S + 60.0
    tipy = info['beak_tip'][1] / rig.S
    fl = 5.5 if size == 'tiny' else 10.5
    patches = {}
    arc = 6 if quick else 8
    for i in range(arc):
        t = i / max(arc - 1, 1)
        cx = tipx + 2.0 - 5.0 * t            # drifts back toward the gape side
        cy = tipy - 1.0 - 5.0 * np.sin(np.pi * t) + 2.0 * t
        patches[start + 4 + i] = {'fish': 'free', 'fish_x': float(cx),
                                  'fish_y': float(cy),
                                  'fish_free_ang': float(200.0 - 170.0 * t)}
    patches[start + 4 + arc] = {'fish': 'held', 'fish_orient': 0.0,
                                'fish_grip': 0.30, 'beak_open': 0.4}
    patches[start + 5 + arc] = {'beak_open': 0.0}
    return patches

def swallow(size='big'):
    """118f canonical (chart), with the measured redistribution: toss
    airborne ~6f, head-work (work_back+head_back) tightened 26f -> 20f,
    settle absorbs the difference. Bulge stays chart-canonical (the
    footage could not resolve it — flagged in the report)."""
    b = base_flat()
    # starts EXACTLY on the strike's end pose (idle base + fish held)
    b.update({'fish': 'held', 'fish_size': size, 'fish_grip': 0.35,
              'fish_orient': 90.0, 'neck_coil': 0.85, 'head_pitch': 18.0})
    segs = [S(12, {}),                                            # secure_shake
            S(9, {'head_pitch': (44.0, 'eio'), 'neck_coil': (0.55, 'eio')}),   # dip down
            S(9, {'head_pitch': (18.0, 'eio'), 'neck_coil': (0.7, 'eio')}),    # dip up
            S(4, {'head_pitch': (-8.0, 'eout'), 'neck_coil': (0.6, 'eio')}),   # toss flick
            S(12, {'head_pitch': (2.0, 'eio')}),                               # toss arc + re-catch
            S(14, {'fish_grip': (0.85, 'lin'), 'head_pitch': (18.0, 'eio')}),  # work_back
            S(6, {'head_pitch': (-24.0, 'eio'), 'neck_coil': (0.35, 'eio')}),  # head_back
            S(22, {'neck_bulge_pos': (1.0, 'lin'), 'head_pitch': (6.0, 'eio'),
                   'neck_coil': (0.6, 'eio')}),                                # swallow_travel
            S(30, {'head_pitch': (18.0, 'eio'), 'neck_coil': (0.85, 'eio'),
                   'body_tilt': (-33.0, 'eio')})]                              # settle
    frames = build(b, segs)
    assert len(frames) == 118, len(frames)
    patches = {}
    # secure_shake: 3 shakes, head_yaw +-6 at 4-frame spacing (authored list)
    shake = [6, 6, -6, -6, 6, 6, -6, -6, 3, 3, -3, -3]
    patches = merge_patches(patches, osc_patch(frames, 0, 'head_yaw', shake))
    # toss arc anchored at the flick (toss phase starts at frame 30)
    patches = merge_patches(patches, _toss_patches(frames, 30, size))
    # work_back jerks: small head_pitch pulses at phase frames 1, 7, 13
    wb = 30 + 16
    for j, f in enumerate((wb + 1, wb + 7, wb + 13)):
        patches[f] = {**patches.get(f, {}), 'head_pitch': 22.0}
        patches[f + 1] = {**patches.get(f + 1, {}), 'head_pitch': 18.0}
    # swallow_travel: bulge envelope + peristaltic blips + shimmy; fish
    # becomes 'none' at phase frame 4 (it is inside now)
    st = wb + 14 + 6
    amp = []
    for i in range(22):
        if i < 8:
            a = (i + 1) / 8.0
        elif i < 18:
            a = 1.0
        else:
            a = 1.0 - (i - 17) / 5.0
        if i in (9, 15):
            a = min(1.15, a + 0.15)
        amp.append(a)
    patches = merge_patches(patches, osc_patch(frames, st, 'neck_bulge_amp', amp))
    shimmy = [0.8 * np.sin(2 * np.pi * 2 * i / 22.0) for i in range(22)]
    patches = merge_patches(patches, osc_patch(frames, st, 'neck_sway',
                                               [float(v) for v in shimmy]))
    patches[st + 4] = {**patches.get(st + 4, {}), 'fish': 'none'}
    # settle beak claps at phase frames 4 and 11 (2f each)
    se = st + 22
    for f in (se + 4, se + 11):
        patches[f] = {**patches.get(f, {}), 'beak_open': 0.5}
        patches[f + 1] = {**patches.get(f + 1, {}), 'beak_open': 0.5}
    for i, p in patches.items():
        if i < len(frames):
            frames[i].update(p)
    # the fish is INSIDE from travel frame 4 to the end of the clip
    for i in range(st + 4, len(frames)):
        frames[i]['fish'] = 'none'
    # from the re-catch (frame 42) the fish is HEAD-FIRST and stays that
    # way — segment frames don't know about the toss patches, so persist
    # the orientation (and the fresh grip) explicitly
    for i in range(42, st + 4):
        if frames[i]['fish'] == 'held':
            frames[i]['fish_orient'] = 0.0
    for i in range(42, 46):
        frames[i]['fish_grip'] = 0.30
    return frames

def swallow_tiny():
    """84f: no dip, toss 12, work_back 12, travel 16 (chart variant)."""
    b = base_flat()
    b.update({'fish': 'held', 'fish_size': 'tiny', 'fish_grip': 0.35,
              'fish_orient': 90.0, 'neck_coil': 0.85, 'head_pitch': 18.0})
    segs = [S(12, {}),
            S(4, {'head_pitch': (-8.0, 'eout'), 'neck_coil': (0.6, 'eio')}),
            S(8, {'head_pitch': (2.0, 'eio')}),
            S(12, {'fish_grip': (0.85, 'lin'), 'head_pitch': (18.0, 'eio')}),
            S(8, {'head_pitch': (-24.0, 'eio'), 'neck_coil': (0.35, 'eio')}),
            S(16, {'neck_bulge_pos': (1.0, 'lin'), 'head_pitch': (6.0, 'eio'),
                   'neck_coil': (0.6, 'eio')}),
            S(24, {'head_pitch': (18.0, 'eio'), 'neck_coil': (0.85, 'eio')})]
    frames = build(b, segs)
    assert len(frames) == 84, len(frames)
    patches = {}
    shake = [6, 6, -6, -6, 6, 6, -6, -6, 3, 3, -3, -3]
    patches = merge_patches(patches, osc_patch(frames, 0, 'head_yaw', shake))
    patches = merge_patches(patches, _toss_patches(frames, 12, 'tiny', quick=True))
    wb = 12 + 12
    for f in (wb + 1, wb + 6, wb + 11):
        patches[f] = {**patches.get(f, {}), 'head_pitch': 22.0}
        patches[f + 1] = {**patches.get(f + 1, {}), 'head_pitch': 18.0}
    st = wb + 12 + 8
    amp = []
    for i in range(16):
        if i < 6:
            a = (i + 1) / 6.0
        elif i < 12:
            a = 1.0
        else:
            a = 1.0 - (i - 11) / 5.0
        if i in (7, 11):
            a = min(1.15, a + 0.15)
        amp.append(a)
    patches = merge_patches(patches, osc_patch(frames, st, 'neck_bulge_amp', amp))
    patches[st + 3] = {**patches.get(st + 3, {}), 'fish': 'none'}
    se = st + 16
    for f in (se + 4, se + 11):
        patches[f] = {**patches.get(f, {}), 'beak_open': 0.5}
        patches[f + 1] = {**patches.get(f + 1, {}), 'beak_open': 0.5}
    for i, p in patches.items():
        if i < len(frames):
            frames[i].update(p)
    for i in range(st + 3, len(frames)):
        frames[i]['fish'] = 'none'
    # head-first from the re-catch (frame 22) onward, as in the big swallow
    for i in range(22, st + 3):
        if frames[i]['fish'] == 'held':
            frames[i]['fish_orient'] = 0.0
    for i in range(22, 24):
        frames[i]['fish_grip'] = 0.30
    return frames

# ------------------------------------------------------------------ step / walk
def _step_segs(step_leg, stance_leg, with_pass, stride=14.0):
    """One step_cycle (24f) for step_leg. If with_pass, root_x advances by
    `stride` across the NEXT cycle's commit+lift window — implemented here
    as: this cycle's commit+lift carry the pass for the PREVIOUS step
    (the caller chains: first step has no pass). Head-lock: neck_sway
    compensates the root advance 1:1 through the pass window."""
    sf, fy, toe = f'{step_leg}.fx', f'{step_leg}.fy', f'{step_leg}.toe'
    tf = f'{stance_leg}.fx'
    segs = []
    if with_pass:
        # weight_commit (4f) + lift_fold (6f): root advances, stance foot's
        # relative fx falls by the same amount (it stays world-planted),
        # neck_sway cancels the head's world motion.
        segs += [S(4, {'root_y': (0.3, 'eio'), 'root_x': ('rel', stride * 0.4),
                       tf: ('rel', -stride * 0.4), 'neck_sway': ('rel', -stride * 0.4)}),
                 S(6, {fy: (79.0, 'eout'), toe: (-55.0, 'eio'),
                       'root_x': ('rel', stride * 0.6), tf: ('rel', -stride * 0.6),
                       'neck_sway': ('rel', -stride * 0.6), 'root_y': (0.0, 'eio')})]
    else:
        segs += [S(4, {'root_y': (0.3, 'eio')}),
                 S(6, {fy: (79.0, 'eout'), toe: (-55.0, 'eio'), 'root_y': (0.0, 'eio')})]
    segs += [S(8, {sf: ('rel', stride)}),                       # advance (root still)
             S(6, {fy: (86.0, 'ein'), toe: (0.0, 'eio')})]      # place, toe-first
    return segs

def step_cycle():
    """The atomic 24f near-leg step (chart: step_cycle), root static."""
    b = base_flat()
    segs = [S(4, {'root_y': (0.3, 'eio')}),
            S(6, {'leg_near.fy': (79.0, 'eout'), 'leg_near.toe': (-55.0, 'eio'),
                  'root_y': (0.0, 'eio')}),
            S(8, {'leg_near.fx': (19.0, 'eio')}),
            S(6, {'leg_near.fy': (86.0, 'ein'), 'leg_near.toe': (0.0, 'eio')})]
    return build(b, segs)

def walk(n_passes=2, freeze=14):
    """A stalk walk to the right: first step free, then each step carries
    the body-pass for the previous plant. Ends with the head-thrust +
    freeze (the chart's step...freeze...step rhythm). Legs alternate;
    feet tracked in world terms via relative fx bookkeeping in _step_segs
    ('rel' targets are resolved by build_walk below)."""
    # custom build: segments with 'rel' deltas need sequential resolution
    b = base_flat()
    plan = []
    legs = [('leg_near', 'leg_far'), ('leg_far', 'leg_near'),
            ('leg_near', 'leg_far'), ('leg_far', 'leg_near')]
    n_steps = n_passes + 1
    for i in range(n_steps):
        sl, tl = legs[i % 2]
        plan += _step_segs(sl, tl, with_pass=(i > 0))
        if i < n_steps - 1:
            plan.append(HOLD(6))  # inter-step freeze (short, mid-walk)
    plan.append(S(3, {'neck_sway': (0.0, 'lin')}))   # head thrust to new fixation
    plan.append(HOLD(freeze - 3))
    # arrive: a small placement step returns the feet to the base stance
    # (near 5 / far -2) so the next clip's authored start pose matches
    plan.append(S(6, {'leg_near.fy': (81.0, 'eout'), 'leg_near.toe': (-30.0, 'eio')}))
    plan.append(S(6, {'leg_near.fx': (5.0, 'eio'), 'leg_near.fy': (86.0, 'ein'),
                      'leg_near.toe': (0.0, 'eio')}))
    # resolve: expand segments frame by frame with 'rel' support
    frames = []
    cur = dict(b)
    for seg in plan:
        n = seg['n']
        targets = seg.get('to', {})
        starts = {}
        finals = {}
        for k, spec in targets.items():
            if isinstance(spec, tuple) and spec and spec[0] == 'rel':
                starts[k] = cur[k]
                finals[k] = cur[k] + spec[1]
            elif isinstance(spec, tuple):
                starts[k] = cur[k]
                finals[k] = spec[0]
            else:
                starts[k] = cur[k]
                finals[k] = spec
        for i in range(n):
            t = (i + 1) / n
            f = dict(cur)
            for k in targets:
                spec = targets[k]
                sp = spec[1] if (isinstance(spec, tuple) and spec and
                                 spec[0] != 'rel' and len(spec) > 1) else 'lin'
                if isinstance(spec, tuple) and spec and spec[0] == 'rel':
                    sp = 'lin'
                f[k] = starts[k] + (finals[k] - starts[k]) * _space(sp, t)
            frames.append(f)
        cur.update(finals)
    return frames

# ------------------------------------------------------------------ turn
def _turn(reverse=False):
    """72f drawn turnaround (chart: turn). Gaze saccades first; the body
    walks around on four pivot steps through the authored yaw stops; the
    head counter-stabilizes (world yaw ~constant after the saccade)."""
    y0, y1 = (180.0, 0.0) if reverse else (0.0, 180.0)
    sac = -150.0 if reverse else 150.0
    world_t = y0 + sac  # the gaze target in world yaw: 150 fwd, 30 reverse
    b = base_flat(yaw=y0, head_yaw=0.0)
    if reverse:
        b['leg_near.fx'], b['leg_far.fx'] = -5.0, 2.0
    mid = [45.0, 90.0, 135.0] if not reverse else [135.0, 90.0, 45.0]
    # head counter-stabilization: head_yaw = world_t - yaw at every stop,
    # so the head's WORLD yaw is constant through the pivots (chart-exact)
    segs = [S(4, {'head_yaw': (sac, 'lin')}),
            S(15, {'yaw': (mid[0], 'eio'), 'head_yaw': (world_t - mid[0], 'eio')}),
            S(15, {'yaw': (mid[1], 'eio'), 'head_yaw': (world_t - mid[1], 'eio')}),
            S(15, {'yaw': (mid[2], 'eio'), 'head_yaw': (world_t - mid[2], 'eio')}),
            S(11, {'yaw': (y1, 'eio'), 'head_yaw': (world_t - y1, 'eio')}),
            S(12, {'head_yaw': (0.0, 'eio'), 'plume_sway': (0.0, 'eio')})]
    frames = build(b, segs)
    assert len(frames) == 72, len(frames)
    # pivot steps: a small foot re-plant inside each pivot phase (lift <= 5,
    # alternating legs), authored as patches so the yaw track stays clean
    patches = {}
    phase_starts = [4, 19, 34, 49]
    for pi, st in enumerate(phase_starts):
        leg = 'leg_near' if pi % 2 == 0 else 'leg_far'
        base_fy = 86.0
        lift = [84.5, 82.5, 81.0, 82.5, 84.5, 86.0]
        for i, v in enumerate(lift):
            patches[st + 2 + i] = {f'{leg}.fy': v, f'{leg}.toe': -30.0 if i in (1, 2, 3) else 0.0}
        # foot lands slightly rotated around the body: shift fx toward the
        # new facing side across the step
        cur_fx = frames[st + 7][f'{leg}.fx']
        patches[st + 7] = {**patches.get(st + 7, {}), f'{leg}.fx': cur_fx}
    # plume follow-through in the settle: overshoot decay
    plume = [1.8, 1.5, 1.2, 0.9, 0.7, 0.5, 0.35, 0.2, 0.1, 0.05, 0.0, 0.0]
    patches = merge_patches(patches, osc_patch(frames, 60, 'plume_sway', plume))
    for i, p in patches.items():
        frames[i].update(p)
    return frames

def turn():
    return _turn(False)

def turn_reverse():
    return _turn(True)

# ------------------------------------------------------------------ alert
def alert():
    """61f take (chart: alert): check, snap, held accent with one gaze
    saccade inside, eased settle back to idle base."""
    b = base_flat()
    segs = [S(4, {'head_pitch': (23.0, 'eio'), 'neck_coil': (0.8, 'eio')}),
            S(3, {'body_tilt': (-39.0, 'lin'), 'neck_coil': (0.25, 'lin'),
                  'root_y': (-0.9, 'lin'), 'head_pitch': (10.0, 'lin')}),
            HOLD(36),
            S(18, {'body_tilt': (-33.0, 'eio'), 'neck_coil': (0.85, 'eio'),
                   'root_y': (0.0, 'eio'), 'head_pitch': (18.0, 'eio')})]
    frames = build(b, segs)
    assert len(frames) == 61, len(frames)
    # the one permitted saccade: accent_hold frames 20-22 (clip frames 27-29)
    for i, v in enumerate((12.0, 24.0, 35.0)):
        frames[27 + i]['head_yaw'] = v
    return frames

# ------------------------------------------------------------------ flight
def _flap_track(n_beats, amp=1.0, tip_lag=2):
    """Authored flap curves: downstroke 5f / upstroke 7f per 12f beat.
    flap_tip = the root curve delayed by tip_lag frames (chart-exact)."""
    # one beat: +34 (top) -> -52 (bottom) in 5f, back to +34 in 7f; the
    # curve is periodic so the tip track can lag by wrapping the cycle
    top, bot = 34.0 * amp, -52.0 * amp
    down = [top + (bot - top) * (i + 1) / 5.0 for i in range(5)]
    up = [bot + (top - bot) * (i + 1) / 7.0 for i in range(7)]
    beat = down + up
    root_curve = beat * n_beats
    tip = []
    for i in range(len(root_curve)):
        v = root_curve[(i - tip_lag) % len(beat)] if i < len(beat) else \
            root_curve[i - tip_lag]
        # tip amplitude: -38..30 vs root -52..34 (chart), rescaled root curve
        tip.append(v * (38.0 / 52.0) if v < 0 else v * (30.0 / 34.0))
    return root_curve, tip

def flight_cycle():
    b = base_flat(body_tilt=-3.0, neck_coil=0.6, neck_retract=1.0,
                  flying=1.0, wing_amt=1.0, head_pitch=8.0,
                  leg_far_fx=-16.0, leg_near_fx=-13.0)
    b.update({'leg_far.fx': -16.0, 'leg_far.fy': 52.0, 'leg_near.fx': -13.0,
              'leg_near.fy': 50.0})
    frames = build(b, [HOLD(12)])
    root_curve, tip = _flap_track(1)
    for i in range(12):
        frames[i]['flap'] = root_curve[i]
        frames[i]['flap_tip'] = tip[i]
        if i in (10, 11):
            frames[i]['wing_amt'] = 0.92
    return frames

def glide():
    b = base_flat(body_tilt=-6.0, neck_coil=0.6, neck_retract=1.0,
                  flying=1.0, wing_amt=1.0, head_pitch=8.0, flap=12.0,
                  flap_tip=12.0)
    b.update({'leg_far.fx': -16.0, 'leg_far.fy': 52.0, 'leg_near.fx': -13.0,
              'leg_near.fy': 50.0})
    return build(b, [HOLD(24)])

def takeoff(facing=1):
    """96f (chart), with the MEASURED launch (footage #7): brief gather,
    neck STRETCHES STRAIGHT during the first beat before folding, feet
    clear ~0.7-0.9 s after the beat starts, legs trail with drips.
    facing=-1 authors the same chart toward profile-left (yaw 180)."""
    f = float(facing)
    b = base_flat(yaw=0.0 if facing > 0 else 180.0)
    if facing < 0:
        b['leg_near.fx'], b['leg_far.fx'] = -5.0, 2.0
    segs = [S(12, {'root_y': (2.6, 'eio'), 'neck_coil': (0.3, 'eio')}),
            # leap + first beat: flying ramps in over frames 5-8; the neck
            # extends straight (extend pulse) before the fold takes over
            S(12, {'flying': (1.0, 'lin'), 'wing_amt': (1.0, 'eout'),
                   'neck_extend': (0.45, 'eout'), 'neck_coil': (0.2, 'eio'),
                   'root_y': (-6.0, 'eout'), 'body_tilt': (-18.0, 'eio')}),
            S(30, {'neck_retract': (1.0, 'eio'), 'neck_coil': (0.6, 'eio'),
                   'neck_extend': (0.0, 'eio'), 'root_y': (-26.0, 'lin'),
                   'body_tilt': (-8.0, 'eio'), 'root_x': (60.0 + f * 14.0, 'lin')}),
            S(42, {'root_y': (-52.0, 'lin'), 'root_x': (60.0 + f * 30.0, 'lin'),
                   'body_tilt': (-3.0, 'eio')})]
    frames = build(b, segs)
    assert len(frames) == 96, len(frames)
    # legs: planted during crouch; extend + leave at leap frame 5; dangle
    # (feet below body, toes down) frames 17-36; then trail as thin lines
    patches = {}
    for i in range(12, 17):
        patches[i] = {'leg_near.fy': 86.0, 'leg_far.fy': 86.0}
    for i in range(17, 37):
        t = (i - 16) / 20.0
        patches[i] = {'leg_near.fy': 86.0 - 30.0 * t, 'leg_near.fx': f * (5.0 - 8.0 * t),
                      'leg_near.toe': -70.0, 'leg_far.fy': 86.0 - 32.0 * t,
                      'leg_far.fx': f * (-2.0 - 9.0 * t), 'leg_far.toe': -70.0}
    for i in range(37, 96):
        patches[i] = {'leg_near.fy': 50.0, 'leg_near.fx': f * -13.0, 'leg_near.toe': 0.0,
                      'leg_far.fy': 52.0, 'leg_far.fx': f * -16.0, 'leg_far.toe': 0.0}
    # flap beats across leap+dangle+climb (deep amplitude, decaying)
    root_curve, tip = _flap_track(7, amp=1.0)
    for i in range(12, 96):
        patches[i] = {**patches.get(i, {}), 'flap': root_curve[i - 12],
                      'flap_tip': tip[i - 12]}
    for i, p in patches.items():
        frames[i].update(p)
    return frames

def landing():
    """84f — MEASURED-tightened (footage #1/#4/#5): the real bird lands in
    ~2.3-3.5 s, not the 120f canonical. Structure kept: glide in, flare,
    legs reach, touchdown, wings MANTLED ~0.7 s for balance (footage #5),
    momentum step, fold last."""
    b = base_flat(body_tilt=-12.0, neck_coil=0.6, neck_retract=1.0,
                  flying=1.0, wing_amt=1.0, head_pitch=8.0, flap=12.0,
                  flap_tip=12.0, root_y=-46.0, root_x=44.0)
    b.update({'leg_far.fx': -16.0, 'leg_far.fy': 52.0, 'leg_near.fx': -13.0,
              'leg_near.fy': 50.0})
    segs = [S(16, {'root_y': (-18.0, 'lin'), 'root_x': (52.0, 'lin'),
                   'body_tilt': (-16.0, 'eio')}),                     # approach glide
            S(10, {'flap': (48.0, 'eout'), 'flap_tip': (44.0, 'eout'),
                   'body_tilt': (-18.0, 'eio'), 'root_y': (-8.0, 'lin'),
                   'tail_ang': (14.0, 'eio')}),                       # flare (braking fan)
            S(12, {'root_y': (-1.0, 'lin'), 'root_x': (57.0, 'lin')}),  # legs reach
            S(8, {'flying': (0.0, 'lin'), 'root_y': (0.8, 'eio')}),    # touchdown + compress
            S(12, {'wing_amt': (0.85, 'lin'), 'root_y': (0.0, 'eio')}),  # MANTLE hold
            S(12, {'neck_retract': (0.4, 'eio'), 'neck_coil': (0.75, 'eio')}),  # momentum step window
            S(14, {'wing_amt': (0.0, 'eio'), 'neck_retract': (0.0, 'eio'),
                   'neck_coil': (0.85, 'eio'), 'body_tilt': (-33.0, 'eio'),
                   'head_pitch': (18.0, 'eio'), 'flap': (0.0, 'eio'),
                   'flap_tip': (0.0, 'eio'), 'tail_ang': (0.0, 'eio'),
                   'root_x': (60.0, 'eio')})]                          # fold + unfold
    frames = build(b, segs)
    assert len(frames) == 84, len(frames)
    patches = {}
    # legs: trail -> dangle (flare end) -> reach forward -> plant at touch
    for i in range(20, 26):
        t = (i - 19) / 6.0
        patches[i] = {'leg_near.fy': 50.0 + 26.0 * t, 'leg_near.fx': -13.0 + 14.0 * t,
                      'leg_far.fy': 52.0 + 24.0 * t, 'leg_far.fx': -16.0 + 12.0 * t}
    for i in range(26, 38):
        t = (i - 25) / 12.0
        patches[i] = {'leg_near.fy': 76.0 + 10.0 * t, 'leg_near.fx': 1.0 + 5.0 * t,
                      'leg_near.toe': -20.0, 'leg_far.fy': 76.0 + 10.0 * t,
                      'leg_far.fx': -4.0 + 3.0 * t, 'leg_far.toe': -20.0}
    for i in range(38, 84):
        patches[i] = {**patches.get(i, {}), 'leg_near.fy': 86.0, 'leg_near.fx': 6.0,
                      'leg_near.toe': 0.0, 'leg_far.fy': 86.0, 'leg_far.fx': -1.0,
                      'leg_far.toe': 0.0}
    # one momentum step (near leg) inside its window: frames 58-69
    step_fy = [86.0, 83.0, 80.5, 79.5, 80.5, 83.0, 86.0, 86.0, 86.0, 86.0, 86.0, 86.0]
    for i, v in enumerate(step_fy):
        patches[58 + i] = {**patches.get(58 + i, {}), 'leg_near.fy': v,
                           'leg_near.fx': 6.0 + (i / 11.0) * 6.0}
    for i, p in patches.items():
        frames[i].update(p)
    return frames

# ------------------------------------------------------------------ stretch / rest
def stretch(warble_form=False):
    if warble_form:
        b = base_flat()
        segs = [S(24, {'wing_amt': (1.0, 'eio'), 'warble': (1.0, 'lin'),
                       'neck_coil': (0.1, 'eio'), 'head_pitch': (-6.0, 'eio'),
                       'body_tilt': (-38.0, 'eio')}),
                HOLD(36),
                S(30, {'wing_amt': (0.0, 'eio'), 'warble': (0.0, 'lin'),
                       'neck_coil': (0.6, 'eio'), 'head_pitch': (10.0, 'eio'),
                       'body_tilt': (-33.0, 'eio')}),
                S(30, {'neck_coil': (0.85, 'eio'), 'head_pitch': (18.0, 'eio')})]
        frames = build(b, segs)
        assert len(frames) == 120
        return frames
    b = base_flat()
    segs = [S(18, {'root_x': (62.0, 'eio'), 'root_y': (-0.4, 'eio')}),
            S(12, {'neck_coil': (0.95, 'eio'), 'head_pitch': (28.0, 'eio')}),
            S(24, {'wing_amt': (1.0, 'eio')}),
            S(18, {'leg_near.fx': (-20.0, 'eio'), 'leg_near.fy': (52.0, 'eio'),
                   'leg_near.toe': (25.0, 'eio')}),
            HOLD(48),
            S(12, {'leg_near.fx': (5.0, 'eio'), 'leg_near.fy': (86.0, 'eio'),
                   'leg_near.toe': (0.0, 'eio')}),
            S(18, {'wing_amt': (0.0, 'eio')}),
            S(18, {'neck_coil': (0.85, 'eio'), 'head_pitch': (18.0, 'eio'),
                   'root_x': (60.0, 'eio'), 'root_y': (0.0, 'eio')})]
    frames = build(b, segs)
    assert len(frames) == 168, len(frames)
    plume = [1.5, 1.2, 0.9, 0.65, 0.4, 0.2, 0.1, 0.0]
    patches = osc_patch(frames, 150, 'plume_sway', plume + [0.0] * 10)
    for i, p in patches.items():
        if i < len(frames):
            frames[i].update(p)
    return frames

def oneleg_enter():
    b = base_flat()
    segs = [S(12, {'root_y': (0.4, 'eio')}),
            S(24, {'leg_near.fy': (48.0, 'eio'), 'leg_near.fx': (3.0, 'eio'),
                   'leg_near.toe': (-70.0, 'eio'), 'neck_coil': (0.7, 'eio')})]
    return build(b, segs)

def oneleg_exit():
    b = base_flat(neck_coil=0.7)
    b.update({'leg_near.fy': 48.0, 'leg_near.fx': 3.0, 'leg_near.toe': -70.0,
              'root_y': 0.4})
    segs = [S(24, {'leg_near.fy': (86.0, 'eio'), 'leg_near.fx': (5.0, 'eio'),
                   'leg_near.toe': (0.0, 'eio'), 'neck_coil': (0.85, 'eio')}),
            S(12, {'root_y': (0.0, 'eio')})]
    return build(b, segs)

def doze():
    b = base_flat()
    segs = [S(36, {'neck_retract': (0.85, 'eio'), 'neck_coil': (0.9, 'eio'),
                   'head_pitch': (32.0, 'eio'), 'root_y': (0.6, 'eio')}),
            S(12, {'blink': (1.0, 'eio')}),
            HOLD(48)]
    frames = build(b, segs)
    assert len(frames) == 96
    return frames

# ------------------------------------------------------------------ preen / scratch / ruffle / flick
def preen():
    b = base_flat()
    segs = [S(24, {'head_yaw': (120.0, 'eio'), 'neck_coil': (0.95, 'eio'),
                   'head_pitch': (36.0, 'eio')}),
            HOLD(8), HOLD(16),
            HOLD(8),
            S(20, {'beak_open': (0.4, 'eio'), 'head_yaw': (105.0, 'eio')}),
            S(18, {'head_yaw': (60.0, 'eio'), 'head_pitch': (42.0, 'eio'),
                   'beak_open': (0.0, 'eio')}),
            HOLD(16),
            S(18, {'wing_amt': (0.45, 'eio')}),
            HOLD(16),
            S(12, {'wing_amt': (0.0, 'lin')}),
            S(24, {'head_yaw': (0.0, 'eio'), 'head_pitch': (18.0, 'eio'),
                   'neck_coil': (0.85, 'eio')}),
            HOLD(60)]
    frames = build(b, segs)
    assert len(frames) == 240, len(frames)
    patches = {}
    # nibble beats: head_pitch +-3 at 3-frame spacing inside the beat windows
    for start in (24, 48, 94, 128):
        nib = [3.0, 0.0, 3.0, 0.0, 3.0, 0.0, 0.0, 0.0]
        base_hp = frames[start]['head_pitch']
        for i, v in enumerate(nib):
            patches[start + i] = {'head_pitch': base_hp + v}
    # shake at frames 144-155: root_x +-0.7 decaying + plume follow-through
    shake = [0.7, -0.7, 0.7, -0.5, 0.5, -0.5, 0.3, -0.3, 0.15, 0.0, 0.0, 0.0]
    patches = merge_patches(patches, osc_patch(frames, 144, 'root_x',
                                               [60.0 + v for v in shake]))
    plume = [2.0, 1.7, 1.4, 1.1, 0.85, 0.6, 0.4, 0.25, 0.12, 0.0, 0.0, 0.0]
    patches = merge_patches(patches, osc_patch(frames, 144, 'plume_sway', plume))
    for i, p in patches.items():
        frames[i].update(p)
    return frames

def scratch():
    b = base_flat()
    segs = [S(14, {'leg_near.fy': (28.0, 'eout'), 'leg_near.fx': (12.0, 'eio'),
                   'leg_near.toe': (-40.0, 'eio')}),
            S(8, {'head_pitch': (40.0, 'eio'), 'neck_coil': (0.8, 'eio')}),
            HOLD(12),
            S(14, {'leg_near.fy': (86.0, 'eio'), 'leg_near.fx': (5.0, 'eio'),
                   'leg_near.toe': (0.0, 'eio'), 'head_pitch': (18.0, 'eio'),
                   'neck_coil': (0.85, 'eio')})]
    frames = build(b, segs)
    assert len(frames) == 48
    # scratch beats: 3 quick foot strokes (fy +-2) against the head
    beats = [-2.0, 2.0, -2.0, 0.0] * 3
    patches = osc_patch(frames, 22, 'leg_near.fy', [28.0 + v for v in beats])
    for i, p in patches.items():
        frames[i].update(p)
    return frames

def ruffle():
    """72f — MEASURED behavior (patio footage #3, ~23-26 s): a full feather
    ruffle/shake mid-patrol. Hunch, plumage fluffs, whole-body shake,
    plume follow-through, back to statue."""
    b = base_flat()
    segs = [S(6, {'root_y': (0.4, 'eio'), 'neck_coil': (0.92, 'eio'),
                  'neck_retract': (0.3, 'eio'), 'head_pitch': (26.0, 'eio')}),
            S(24, {'wing_amt': (0.16, 'lin')}),
            S(18, {'wing_amt': (0.0, 'eio'), 'neck_retract': (0.0, 'eio'),
                   'neck_coil': (0.85, 'eio'), 'head_pitch': (18.0, 'eio'),
                   'root_y': (0.0, 'eio')}),
            HOLD(24)]
    frames = build(b, segs)
    assert len(frames) == 72
    patches = {}
    shake = []
    for i in range(24):
        a = 0.8 * (1.0 - i / 24.0)
        shake.append(a if i % 2 == 0 else -a)
    patches = merge_patches(patches, osc_patch(frames, 6, 'root_x',
                                               [60.0 + v for v in shake]))
    yaw_shake = [8.0 * (1.0 - i / 24.0) * (1 if i % 2 == 0 else -1) for i in range(24)]
    patches = merge_patches(patches, osc_patch(frames, 6, 'head_yaw', yaw_shake))
    plume = [2.2 * (1.0 - i / 18.0) for i in range(18)]
    patches = merge_patches(patches, osc_patch(frames, 30, 'plume_sway', plume))
    for i, p in patches.items():
        frames[i].update(p)
    return frames

def balance_flick():
    """36f — MEASURED micro-behavior (kayak footage #5, ~31 s): a half-open
    wing-flick for balance while repositioning a step."""
    b = base_flat()
    segs = [S(6, {'root_y': (0.3, 'eio')}),
            S(4, {'wing_amt': (0.5, 'eout'), 'flap': (-20.0, 'eout'),
                  'leg_near.fy': (80.0, 'eout'), 'leg_near.toe': (-50.0, 'eio')}),
            S(6, {'leg_near.fx': (15.0, 'eio')}),
            S(4, {'leg_near.fy': (86.0, 'ein'), 'leg_near.toe': (0.0, 'eio')}),
            S(8, {'wing_amt': (0.0, 'eio'), 'flap': (0.0, 'eio'),
                  'root_y': (0.0, 'eio')}),
            HOLD(8)]
    frames = build(b, segs)
    assert len(frames) == 36, len(frames)
    return frames

# ------------------------------------------------------------------ registry
CANON = {
    'idle_hunt_a': lambda: idle_hunt('a'),
    'idle_hunt_b': lambda: idle_hunt('b'),
    'idle_hunt_c': lambda: idle_hunt('c'),
    'head_turn': head_turn,
    'strike': strike,
    'strike_big': strike_big,
    'strike_miss': strike_miss,
    'swallow': lambda: swallow('big'),
    'swallow_tiny': swallow_tiny,
    'step_cycle': step_cycle,
    'walk': lambda: walk(2),
    'turn': turn,
    'turn_reverse': turn_reverse,
    'alert': alert,
    'takeoff': takeoff,
    'flight_cycle': flight_cycle,
    'glide': glide,
    'landing': landing,
    'stretch': lambda: stretch(False),
    'stretch_warble': lambda: stretch(True),
    'oneleg_enter': oneleg_enter,
    'oneleg_exit': oneleg_exit,
    'doze': doze,
    'preen': preen,
    'scratch': scratch,
    'ruffle': ruffle,
    'balance_flick': balance_flick,
}

def all_clips():
    return {name: fn() for name, fn in CANON.items()}

if __name__ == '__main__':
    tot = 0
    for name, frames in all_clips().items():
        tot += len(frames)
        print(f"{name:16s} {len(frames):4d} frames")
    print("TOTAL", tot)
