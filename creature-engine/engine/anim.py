"""Keyframe animation engine — generalized from heron v1 clips.Anim.

Differences from v1: no global FPS (time is seconds; sampling takes fps),
no built-in pose vocabulary (params come from the species package), and the
micro-motion 'life layer' is DATA from the species package, not hard-coded
sine terms with heron semantics baked in.
"""
import numpy as np


def smoothstep(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


class Anim:
    """param -> keyframe track [(t_sec, value)] with smoothstep interpolation,
    or ('fn', f(t)) for procedural tracks (gaits, arcs)."""

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
                return v0 + (v1 - v0) * smoothstep((t - t0) / max(t1 - t0, 1e-6))
        return tr[-1][1]


def blink_track(anim, rng, every=(2.5, 6.0)):
    """A reusable blink pattern (was _blink_track in v1 clips.py)."""
    t = rng.uniform(*every) * 0.5
    keys = [(0.0, 0.0)]
    while t < anim.dur - 0.3:
        keys += [(t, 0.0), (t + 0.04, 1.0), (t + 0.13, 1.0), (t + 0.17, 0.0)]
        t += rng.uniform(*every)
    keys.append((anim.dur, 0.0))
    anim.set('blink', keys)


def sample(anim, defaults, fps, life_layer=(), rng=None, apply_life=True):
    """Sample an Anim into per-frame pose dicts.

    defaults: the species pose_params defaults (flat dict; dotted keys expand
    into sub-dicts, as in v1). life_layer: species-declared micro-motion terms
    [{param, waveform, period_s, amplitude, damped_by?, skip_when?}] — each
    term's phase is drawn from rng so variants differ.
    """
    rng = rng or np.random.default_rng(0)
    n = int(round(anim.dur * fps))
    phases = [rng.uniform(0, 2 * np.pi) for _ in life_layer]
    poses = []
    for i in range(n):
        t = i / fps
        pose = {}
        for key, dv in defaults.items():
            v = anim.value(key, t, dv) if key in anim.tracks else dv
            _assign(pose, key, v)
        for key in anim.tracks:
            if key not in defaults:
                _assign(pose, key, anim.value(key, t))
        if apply_life:
            for term, ph in zip(life_layer, phases):
                param = term['param']
                cur = _fetch(pose, param, 0.0)
                amp = term['amplitude']
                if term.get('damped_by'):
                    amp *= (1.0 - 0.75 * _fetch(pose, term['damped_by'], 0.0))
                if term.get('skip_when') and _fetch(pose, term['skip_when'], 0.0) > 0.5:
                    continue
                w = np.sin(2 * np.pi * t / term['period_s'] + ph)
                _assign(pose, param, cur + amp * w)
        poses.append(pose)
    return poses


def _assign(pose, dotted, v):
    if '.' in dotted:
        a, b = dotted.split('.', 1)
        pose.setdefault(a, {})[b] = v
    else:
        pose[dotted] = v


def _fetch(pose, dotted, default=0.0):
    if '.' in dotted:
        a, b = dotted.split('.', 1)
        return pose.get(a, {}).get(b, default)
    return pose.get(dotted, default)
