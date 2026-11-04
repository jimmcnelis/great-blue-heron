"""Pond Frog clips — authored with the engine Anim, nothing heron-shaped.

Clip contract: build_clip(kind, kwargs, ctx) -> (poses, events); events in
DESIGN coordinates (the engine converts). Zones come from the environment
package through ctx — clips never hard-code stage positions.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from engine.anim import Anim, blink_track, sample, smoothstep  # noqa: E402

DEFAULTS = dict(root_x=48.0, root_y=0.0, squash=1.0, throat=0.0, blink=0.0,
                mouth_open=0.0, tongue=0.0, tongue_dx=14.0, tongue_dy=-5.0,
                leg_stretch=0.0, eye_look=0.0)


def _base(dur, zone_x):
    a = Anim(dur)
    a.const('root_x', zone_x)
    return a


def _sample(a, ctx, rng, life=True):
    return sample(a, DEFAULTS, ctx['fps'],
                  life_layer=_life(ctx) if life else (), rng=rng)


def _life(ctx):
    return ctx.get('life_layer', ())


def idle_clip(zone='perch_mid', dur=6.0, seed=0, ctx=None):
    rng = np.random.default_rng(seed)
    zx = ctx['zones'][zone]['x']
    a = _base(dur, zx)
    keys = [(0.0, 0.12)]
    t = rng.uniform(1.2, 2.4)
    while t < dur - 1.2:
        keys += [(t, 0.12), (t + 0.3, 0.30), (t + 0.8, 0.30), (t + 1.1, 0.12)]
        t += rng.uniform(1.8, 3.2)
    keys.append((dur, 0.12))
    a.set('throat', keys)
    a.set('eye_look', [(0, 0), (dur * 0.4, 0.8), (dur * 0.55, 0.8), (dur * 0.8, -0.6), (dur, 0)])
    blink_track(a, rng)
    return _sample(a, ctx, rng), []


def doze_clip(zone='perch_mid', dur=6.0, seed=0, ctx=None):
    rng = np.random.default_rng(seed)
    zx = ctx['zones'][zone]['x']
    a = _base(dur, zx)
    a.const('root_y', 0.7)
    a.set('blink', [(0, 1), (dur * 0.45, 1), (dur * 0.5, 0), (dur * 0.55, 1), (dur, 1)])
    a.const('throat', 0.10)
    return _sample(a, ctx, rng), []


def alert_clip(zone='perch_mid', seed=0, ctx=None):
    rng = np.random.default_rng(seed)
    zx = ctx['zones'][zone]['x']
    dur = 1.4
    a = _base(dur, zx)
    a.set('root_y', [(0, 0.4), (0.18, -1.1), (1.1, -1.1), (dur, -0.4)])
    a.set('squash', [(0, 0.96), (0.18, 1.04), (1.1, 1.04), (dur, 1.0)])
    a.set('blink', [(0, 0), (0.55, 0), (0.6, 1), (0.7, 1), (0.75, 0), (dur, 0)])
    return _sample(a, ctx, rng, life=False), []


def croak_clip(zone='perch_mid', seed=0, ctx=None):
    rng = np.random.default_rng(seed)
    zx = ctx['zones'][zone]['x']
    dur = 2.4
    a = _base(dur, zx)
    a.set('throat', [(0, 0.05), (0.35, 0.05), (0.75, 1.0), (1.25, 1.0), (1.55, 0.25),
                     (1.8, 0.8), (2.05, 0.8), (dur, 0.05)])
    a.set('mouth_open', [(0, 0), (0.7, 0), (0.8, 0.8), (1.5, 0.8), (1.6, 0),
                         (1.85, 0.6), (2.0, 0.6), (2.1, 0), (dur, 0)])
    blink_track(a, rng, every=(3.0, 5.0))
    return _sample(a, ctx, rng), []


def hop_clip(from_zone='perch_mid', to_zone='perch_left', seed=0, ctx=None):
    rng = np.random.default_rng(seed)
    xa, xb = ctx['zones'][from_zone]['x'], ctx['zones'][to_zone]['x']
    dist = abs(xb - xa)
    air = dist / 26.0                     # ~26 design units/s in the air
    dur = 0.30 + air + 0.35
    a = _base(dur, xa)
    t0, t1 = 0.30, 0.30 + air
    a.fn('root_x', lambda t: xa + (xb - xa) * smoothstep((t - t0) / max(air, 1e-6))
         if t0 <= t <= t1 else (xa if t < t0 else xb))
    a.fn('root_y', lambda t: -9.5 * np.sin(np.pi * (t - t0) / air)
         if t0 <= t <= t1 else 0.0)
    a.set('squash', [(0, 1.0), (t0 - 0.08, 0.74), (t0 + 0.06, 1.10),
                     (t1 - 0.04, 1.06), (t1 + 0.10, 0.78), (t1 + 0.28, 1.0), (dur, 1.0)])
    a.set('leg_stretch', [(0, 0), (t0, 0), (t0 + air * 0.4, 1.0), (t1, 0.25), (dur, 0)])
    blink_track(a, rng, every=(4.0, 6.0))
    poses = _sample(a, ctx, rng, life=False)
    land_f = int(round(t1 * ctx['fps']))
    return poses, [{'f': land_f, 'type': 'land', 'x': float(xb)}]


def tongue_snap_clip(zone='perch_mid', target_dx=15.0, target_dy=-6.0, seed=0, ctx=None):
    rng = np.random.default_rng(seed)
    zx = ctx['zones'][zone]['x']
    dur = 1.2
    a = _base(dur, zx)
    a.const('tongue_dx', target_dx)
    a.const('tongue_dy', target_dy)
    a.set('tongue', [(0, 0), (0.30, 0), (0.38, 1.0), (0.48, 1.0), (0.66, 0), (dur, 0)])
    a.set('mouth_open', [(0, 0), (0.28, 0), (0.34, 1.0), (0.6, 1.0), (0.7, 0), (dur, 0)])
    a.set('eye_look', [(0, 0.6), (dur, 0.6)])
    poses = _sample(a, ctx, rng, life=False)
    snap_f = int(round(0.42 * ctx['fps']))
    return poses, [{'f': snap_f, 'type': 'snap',
                    'x': float(zx + 11.2 + target_dx), 'y': float(44.0 - 2.2 + target_dy)}]


def empty_clip(ctx=None, **kw):
    return [dict(DEFAULTS, root_x=-100.0) for _ in range(int(4 * ctx['fps']))], []


BUILDERS = {'idle': idle_clip, 'doze': doze_clip, 'alert': alert_clip,
            'croak': croak_clip, 'hop': hop_clip, 'tongue_snap': tongue_snap_clip,
            'empty': empty_clip}


def build_clip(kind, kwargs, ctx):
    return BUILDERS[kind](ctx=ctx, **kwargs)
