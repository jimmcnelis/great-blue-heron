"""Great Blue Heron clips — ADAPTER over the v1 clip authors, plus the two
corpus HOOKS the v1 builder had hard-coded by clip kind (toss, turn).

v1 locations: corpus_build._patch_toss and the kind=='turn' squash block.
Here they are package code, named in the roster, invisible to the engine.
"""
import sys

import numpy as np

sys.path.insert(0, '/home/hatch/workspace/heron/src')
import clips as _v1_clips  # noqa: E402
import corpus_build as _v1_cb  # noqa: E402

FPS = _v1_clips.FPS


def build_clip(kind, kwargs, ctx):
    # 'alert' was never in v1's BUILDERS registry — alert_append.py called
    # clips.alert_clip directly. The roster makes it a normal kind here.
    if kind == 'alert':
        return _v1_clips.alert_clip(**kwargs)
    return _v1_clips.build_clip(kind, kwargs)


def _beaks(anchors, ctx):
    return anchors[:, 0, :]     # anchor 0 = beak_tip (species.yaml order)


def toss_patch(frames, anchors, poses, events, entry, render, ctx):
    """Ballistic fish toss, patched in once beak tips are measurable.
    v1 re-rendered the clip after patching poses; so do we."""
    if not any(e['type'] == 'toss' for e in events):
        return frames, anchors, events
    _v1_cb._patch_toss(poses, events, _beaks(anchors, ctx))
    frames, anchors, _ = render(poses)
    return frames, anchors, events


def turn_squash(frames, anchors, poses, events, entry, render, ctx):
    """Horizontal squash sweep 1 -> -1 around the root column: the v1 turn.
    Palette-exact nearest-column remap; |f| clamped so the bird never vanishes."""
    zone = entry.get('kwargs', {}).get('zone', 'R')
    # design->grid x for the zone root, using the engine mapping rule
    zx = _v1_clips.ZONE[zone]
    s = ctx['grid_h'] / ctx['design_h']
    cx = (zx - ctx['design_w'] / 2.0) * s + ctx['grid_w'] / 2.0
    n = len(frames)
    jj = np.arange(ctx['grid_w'])
    out = np.empty_like(frames)
    for i in range(n):
        if i < 3:
            f = 1.0
        elif i < 13:
            f = float(np.cos(np.pi * (i - 3) / 10.0))
        else:
            f = -1.0
        if abs(f) < 0.14:
            f = 0.14 if f >= 0 else -0.14
        src = np.clip(np.round(cx + (jj - cx) / f).astype(int), 0, ctx['grid_w'] - 1)
        out[i] = frames[i][:, src]
    return out, anchors, events
