"""Episode player: corpus trajectories + effects compositing.

The v1 sim's job, generalized: an episode script (scene data) sequences
clips PER CHARACTER on parallel tracks; clip events resolve through the
environment's effect_map; characters composite in scene order onto one
merged palette. Corpora store LOCAL palette indices per character; the
merge rule is: index 0 (background) is shared, each character's remaining
entries append in scene order.
"""
import json
from pathlib import Path

import numpy as np

from .effects import Effects


def merged_palette(scene):
    pal = [None]
    offsets = {}
    for cid in scene.char_order:
        sp = scene.characters[cid]
        offsets[cid] = len(pal) - 1          # local i>0 -> merged offsets+i
        for rgb in sp.palette_rgb[1:]:
            pal.append(tuple(rgb))
    # objects append after characters, same rule (index 0 shared canvas)
    obj_offsets = {}
    for oid in scene.object_order:
        so = scene.objects[oid]
        obj_offsets[oid] = len(pal) - 1
        for rgb in so.palette_rgb[1:]:
            pal.append(tuple(rgb))
    pal[0] = tuple(scene.characters[scene.char_order[0]].palette_rgb[0])
    return np.array(pal, dtype=np.uint8), offsets, obj_offsets


def world_ink_index(scene, offsets):
    """Effect marks use the 'ink' palette entry of the first character that
    defines one (heron: its own ink black; the convention is documented in
    ARCHITECTURE.md)."""
    for cid in scene.char_order:
        sp = scene.characters[cid]
        if 'ink' in sp.index:
            return offsets[cid] + sp.index['ink']
    return 1


def load_corpus(corpus_dir, char_id):
    corpus_dir = Path(corpus_dir)
    frames = np.load(corpus_dir / f'{char_id}_frames.npy')
    anchors = np.load(corpus_dir / f'{char_id}_anchors.npy')
    meta = json.loads((corpus_dir / f'{char_id}_clips.json').read_text())
    return frames, anchors, meta


def build_tracks(scene, corpus_dir):
    """Returns (tracks, events, total_frames, segments).
    tracks: char_id -> {frame: local grid}; events: absolute-frame event list
    with 'char' attached; segments: per-segment record for QA."""
    corpora = {cid: load_corpus(corpus_dir, cid) for cid in scene.char_order}
    tracks = {cid: {} for cid in scene.char_order}
    events, segments = [], []
    cursors = {cid: 0 for cid in scene.char_order}
    for seg in scene.data.get('episode_script', []):
        cid = seg['of']
        frames, anchors, meta = corpora[cid]
        by_name = {c['name']: c for c in meta['clips']}
        c = by_name[seg['clip']]
        start = seg.get('at_frame', cursors[cid])
        n = c['count'] if not seg.get('frames') else min(seg['frames'], c['count'])
        for k in range(n):
            tracks[cid][start + k] = frames[c['start'] + k]
        for e in c['events']:
            if e['f'] < n:
                ee = dict(e)
                ee['f'] = e['f'] + start
                ee['char'] = cid
                ee['anchor_pos'] = None
                if meta['anchor_names'] and e['type']:
                    ai = c['start'] + e['f']
                    ee['anchor_pos'] = anchors[ai, 0].tolist()
                if 'f_end' in e:
                    ee['f_end'] = min(e['f_end'], n) + start
                events.append(ee)
        segments.append(dict(char=cid, clip=seg['clip'], start=start, count=n,
                             presence=seg.get('presence')))
        cursors[cid] = max(cursors[cid], start + n)
    total = max(cursors.values()) if cursors else 0
    return tracks, events, total, segments, corpora


def render_episode(scene, corpus_dir):
    tracks, events, total, segments, corpora = build_tracks(scene, corpus_dir)
    palette, offsets, obj_offsets = merged_palette(scene)
    ink_idx = world_ink_index(scene, offsets)
    # objects render ONCE per episode from their placed state (state is
    # scene/bus-set, not per-frame animated in the scripted player; the
    # real-time player re-renders on set_state). Back layer draws under the
    # creature tracks, front layer over them.
    obj_layers = {'back': [], 'front': []}
    for oid in scene.object_order:
        so = scene.objects[oid]
        grid_o, anchors_o = so.render(scene)
        so._anchor_cache = anchors_o
        obj_layers[so.layer].append((grid_o, obj_offsets[oid]))
    # surface band centre: env effect_region or first clip plane, design -> grid
    s = scene.grid_h / scene.design_h
    er = scene.environment.data.get('effect_region')
    if er:
        surface_row = int(round(er['y_center'] * s))
        half = max(2, int(round(er.get('half_height', 4) * s)))
    else:
        planes = scene.environment.canvas_law.get('clip_planes', [])
        surface_row = int(round(planes[0]['at'] * s)) if planes else scene.grid_h // 2
        half = 6
    fx = Effects(scene.environment.effect_map, ink_idx, bg_index=0,
                 surface_row=surface_row, effect_region={'half_height': half})
    # static environment marks (design -> grid), drawn every frame onto bg
    statics = []
    for mark in scene.environment.canvas_law.get('static_marks', []):
        if mark['kind'] == 'hline':
            row = int(round(mark['y'] * s))
            thick = max(1, int(round(mark.get('thickness', 1) * s)))
            # resolve color name against the first palette that defines it
            for cid in scene.char_order:
                sp = scene.characters[cid]
                if mark['color'] in sp.index:
                    statics.append((row, thick, offsets[cid] + sp.index[mark['color']]))
                    break
    out = np.zeros((total, scene.grid_h, scene.grid_w), dtype=np.uint8)
    drip_windows = [e for e in events if 'f_end' in e]
    for f in range(total):
        g = out[f]
        for row, thick, color in statics:
            g[row:row + thick, :] = color
        for grid_o, off in obj_layers['back']:
            mask = grid_o != 0
            g[mask] = grid_o[mask] + off
        for cid in scene.char_order:
            local = tracks[cid].get(f)
            if local is None:
                continue
            mask = local != 0
            g[mask] = local[mask] + offsets[cid]
        for grid_o, off in obj_layers['front']:
            mask = grid_o != 0
            g[mask] = grid_o[mask] + off
        t = f / scene.fps
        for e in events:
            if e['f'] == f:
                fx.fire(e, t, seed=f)
        for e in drip_windows:
            if e['f'] <= f < e['f_end'] and (f - e['f']) % 3 == 0 and e.get('anchor_pos'):
                frames_c, anchors_c, meta_c = corpora[e['char']]
                by_name = {c['name']: c for c in meta_c['clips']}
                seg = next(sg for sg in segments if sg['char'] == e['char']
                           and sg['start'] <= f < sg['start'] + sg['count'])
                c = by_name[seg['clip']]
                ax, ay = anchors_c[c['start'] + (f - seg['start']), 0]
                fx.start_drips(float(ax), float(ay + 1), t)
        fx.draw(g, t)
    log = dict(segments=segments,
               events=[{k: v for k, v in e.items() if k != 'anchor_pos'} for e in events],
               total_frames=total, fps=scene.fps)
    return out, palette, log
