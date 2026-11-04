"""Firefly clips: drifting flight paths + a glow pulse vocabulary."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from engine.anim import Anim, sample, smoothstep  # noqa: E402

DEFAULTS = dict(root_x=20.0, root_y=30.0, glow=0.5, wing=0.0)


def drift_clip(x0=0.0, y0=30.0, x1=60.0, y1=32.0, dur=6.0, seed=0, ctx=None):
    rng = np.random.default_rng(seed)
    a = Anim(dur)
    ph = rng.uniform(0, 6.28)
    a.fn('root_x', lambda t: x0 + (x1 - x0) * smoothstep(t / dur))
    a.fn('root_y', lambda t: y0 + (y1 - y0) * smoothstep(t / dur)
         + 2.2 * np.sin(2 * np.pi * t / 2.9 + ph))
    a.fn('glow', lambda t: 0.45 + 0.35 * np.sin(2 * np.pi * t / 2.3 + ph))
    a.const('wing', 1.0)
    return sample(a, DEFAULTS, ctx['fps'], life_layer=(), rng=rng), []


def pulse_clip(x=60.0, y=32.0, dur=3.0, seed=0, ctx=None):
    rng = np.random.default_rng(seed)
    a = Anim(dur)
    a.const('root_x', x)
    a.const('root_y', y)
    a.set('glow', [(0, 0.15), (0.5, 0.15), (0.9, 1.0), (1.5, 1.0), (2.0, 0.15), (dur, 0.15)])
    a.const('wing', 0.0)
    return sample(a, DEFAULTS, ctx['fps'], life_layer=(), rng=rng), []


def exit_clip(x=60.0, y=32.0, dur=2.5, seed=0, ctx=None):
    rng = np.random.default_rng(seed)
    a = Anim(dur)
    a.fn('root_x', lambda t: x + 16.0 * smoothstep(t / dur))
    a.fn('root_y', lambda t: y - 44.0 * smoothstep(t / dur))
    a.const('wing', 1.0)
    a.set('glow', [(0, 0.5), (dur, 0.1)])
    return sample(a, DEFAULTS, ctx['fps'], life_layer=(), rng=rng), []


def gone_clip(dur=2.0, ctx=None, **kw):
    return [dict(DEFAULTS, root_x=-100.0) for _ in range(int(dur * ctx['fps']))], []


BUILDERS = {'drift': drift_clip, 'pulse': pulse_clip, 'exit': exit_clip, 'gone': gone_clip}


def build_clip(kind, kwargs, ctx):
    return BUILDERS[kind](ctx=ctx, **kwargs)
