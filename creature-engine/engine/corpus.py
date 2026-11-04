"""Corpus builder — roster (data) -> poses -> rig frames + events.

Generalizes heron v1 corpus_build.py. The v1 special cases keyed on clip
kind inside the builder (the ballistic 'toss' patch, the 'turn' squash) are
now PACKAGE HOOKS: functions named in the roster entry, living in the
species' clips module, called as hook(frames, poses, events, render, ctx).
The engine itself knows no species' names.
"""
import json
from pathlib import Path

import numpy as np


def _render_poses(sp, poses, ctx):
    frames = np.empty((len(poses), ctx['grid_h'], ctx['grid_w']), dtype=np.uint8)
    anchor_names = [a['name'] for a in sp.data.get('anchors', [])]
    anchors = np.zeros((len(poses), max(len(anchor_names), 1), 2), dtype=np.float32)
    for i, p in enumerate(poses):
        g, info = sp.render_fn(p, ctx)
        frames[i] = g
        for j, name in enumerate(anchor_names):
            if name in info:
                anchors[i, j] = info[name]
    return frames, anchors, anchor_names


def _design_to_grid_x(ctx, x):
    s = ctx['grid_h'] / ctx['design_h']
    return (x - ctx['design_w'] / 2.0) * s + ctx['grid_w'] / 2.0


def build_character(scene, char_id, out_dir, only=None, log=print):
    sp = scene.characters[char_id]
    ctx = scene.ctx(char_id)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    all_frames, all_anchors, metas = [], [], []
    anchor_names = [a['name'] for a in sp.data.get('anchors', [])]

    def render(poses):
        return _render_poses(sp, poses, ctx)

    for entry in sp.roster:
        name, kind = entry['name'], entry['kind']
        kwargs = dict(entry.get('kwargs', {}))
        if only and kind not in only and name not in only:
            continue
        poses, events = sp.clips_module.build_clip(kind, kwargs, ctx)
        events = [dict(e) for e in events]
        for e in events:  # events are authored in design coords; store grid x/y
            if 'x' in e:
                e['x_design'] = e['x']
                e['x'] = float(_design_to_grid_x(ctx, e['x']))
            if 'y' in e:
                e['y_design'] = e['y']
                e['y'] = float(e['y'] * ctx['grid_h'] / ctx['design_h'])
        frames, anchors, _ = render(poses)
        for hook_name in entry.get('hooks', []):
            hook = getattr(sp.clips_module, hook_name)
            frames, anchors, events = hook(frames, anchors, poses, events, entry, render, ctx)
        variants = [(name, frames, anchors, events, 1)]
        if entry.get('mirror', True):
            mf = np.ascontiguousarray(frames[:, :, ::-1])
            ma = anchors.copy()
            if len(anchor_names):
                ma[:, :, 0] = (ctx['grid_w'] - 1) - ma[:, :, 0]
            me = []
            for e in events:
                e2 = dict(e)
                if 'x' in e2:
                    e2['x'] = float((ctx['grid_w'] - 1) - e2['x'])
                me.append(e2)
            variants.append((name + '_m', mf, ma, me, -1))
        for vname, vframes, vanchors, vevents, facing in variants:
            meta = dict(name=vname, kind=kind, facing=facing, count=len(vframes),
                        start=int(sum(m['count'] for m in metas)), events=vevents,
                        split=entry.get('split', 'train'),
                        ambient=bool(entry.get('ambient', False)),
                        kwargs=kwargs)
            metas.append(meta)
            all_frames.append(vframes)
            all_anchors.append(vanchors)
            log(f"  clip {vname}: {len(vframes)} frames")
    F = np.concatenate(all_frames) if all_frames else np.zeros((0, ctx['grid_h'], ctx['grid_w']), np.uint8)
    A = np.concatenate(all_anchors) if all_anchors else np.zeros((0, 1, 2), np.float32)
    np.save(out_dir / f'{char_id}_frames.npy', F)
    np.save(out_dir / f'{char_id}_anchors.npy', A)
    with open(out_dir / f'{char_id}_clips.json', 'w') as f:
        json.dump(dict(anchor_names=anchor_names, clips=metas), f)
    log(f"  TOTAL {char_id}: {len(F)} frames / {len(metas)} clips")
    return metas
