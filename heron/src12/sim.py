"""Heron v1.2 episode player: schedules canon clips verbatim (the axiom —
variety lives here, never inside a clip), applies zone offsets, runs the
procedural ink layer (every mark caused; zero ink at rest), and renders.

Ink events:
- step plants (pose-detected): a foot's fy reaches >= 85.5 after being
  below -> ripple ring at the foot's world x.
- strike splash (chart event): neck_extend crosses 0.95 -> splash cluster
  + ring at the beak-tip x.
- drips (chart event): while neck_extend falls through 0.7/0.45/0.25
  after a strike -> drip dots under the beak.
- dip splash: head_pitch peaks (>40) inside a swallow -> small ring.
- takeoff churn (MEASURED, footage #7): flying crosses 0.5 upward ->
  churned patch + expanding ring persisting ~7 s (168 frames).
- landing ring: flying crosses 0.5 downward -> ring + small splash.
Ink draws only on white cells at/below the surface row — it never
overwrites the bird or the fish.
"""
import json
import subprocess
import sys
import numpy as np
from PIL import Image
import rig
import clips

SURF = rig.SURF_ROW

# ------------------------------------------------------------------ ink
class InkSim:
    def __init__(self):
        self.marks = []   # dicts: kind, x (grid), birth, life, r0, r1
        self.prev = None
        self.events = []  # (frame, kind, x) — the causality log

    def _add(self, kind, x, frame, life, r0=1.0, r1=13.0):
        self.marks.append({'kind': kind, 'x': float(x), 'birth': frame,
                           'life': life, 'r0': r0, 'r1': r1})
        self.events.append((frame, kind, float(x)))

    def observe(self, frame, pose, info):
        p = pose
        prev = self.prev
        if prev is not None:
            for leg in ('leg_near', 'leg_far'):
                if prev[leg]['fy'] < 85.5 <= p[leg]['fy'] and p['flying'] < 0.5:
                    gx = (p['root_x'] + p[leg]['fx'] - 60.0) * rig.S + rig.W / 2
                    self._add('ripple', gx, frame, 60)
            if prev['neck_extend'] < 0.95 <= p['neck_extend']:
                self._add('splash', info['beak_tip'][0], frame, 46)
                self._add('ring', info['beak_tip'][0], frame, 90, 2.0, 16.0)
                self._peak = 30  # drips armed for the withdrawal window
            if getattr(self, '_peak', 0) > 0:
                self._peak -= 1
                for thr in (0.7, 0.45, 0.25):
                    if prev['neck_extend'] > thr >= p['neck_extend']:
                        self._add('drip', info['beak_tip'][0], frame, 26, 0.5, 3.0)
            if prev['head_pitch'] < 40.0 <= p['head_pitch']:
                self._add('ring', info['beak_tip'][0], frame, 60, 1.0, 8.0)
            if prev['flying'] < 0.5 <= p['flying']:
                gx = (p['root_x'] - 60.0) * rig.S + rig.W / 2
                self._add('churn', gx, frame, 168, 3.0, 10.0)
                self._add('ring', gx, frame, 168, 2.0, 22.0)
            if prev['flying'] >= 0.5 > p['flying']:
                gx = (p['root_x'] - 60.0) * rig.S + rig.W / 2
                self._add('ring', gx, frame, 90, 2.0, 15.0)
                self._add('splash', gx, frame, 40)
        self.prev = p

    def draw(self, grid, frame):
        g = grid
        alive = []
        for m in self.marks:
            age = frame - m['birth']
            if age < 0 or age >= m['life']:
                continue
            alive.append(m)
            t = age / m['life']
            cx = m['x']
            if m['kind'] in ('ripple', 'ring'):
                r = m['r0'] + (m['r1'] - m['r0']) * (1 - (1 - t) ** 2)
                _ring(g, cx, r, dash=age)
            elif m['kind'] == 'splash':
                _splash(g, cx, age)
            elif m['kind'] == 'drip':
                _drip(g, cx, age)
            elif m['kind'] == 'churn':
                _churn(g, cx, age, m['life'])
        self.marks = alive
        self.last_alive = len(alive)
        return g

def _put(g, x, y):
    xi, yi = int(round(x)), int(round(y))
    if 0 <= xi < rig.W and SURF - 1 <= yi < rig.H and g[yi, xi] == rig.WHITE:
        g[yi, xi] = rig.INK

def _ring(g, cx, r, dash=0):
    # flat ellipse ring on the surface (perspective-squashed), dashed as
    # it ages so the fade reads as dissolution, not a grey fade (palette
    # is exact — there is no grey)
    for a_deg in range(0, 360, 3):
        if dash > 18 and (a_deg // 12 + dash // 6) % 2 == 0:
            continue
        a = np.deg2rad(a_deg)
        _put(g, cx + r * 1.9 * np.cos(a), SURF + 2 + r * 0.30 * np.sin(a))

def _splash(g, cx, age):
    # a small crown of dots that rises and falls over ~0.4 s
    h = np.sin(np.pi * min(age / 10.0, 1.0)) if age < 10 else 0.0
    for dx, dy in ((-6, 2), (-3, -2), (0, -4), (3, -2), (6, 2), (-1, 1), (2, 0)):
        _put(g, cx + dx, SURF + 1 + dy * (0.4 + h))

def _drip(g, cx, age):
    _put(g, cx, SURF + 1 + (age % 3 == 0))
    _ring(g, cx, 0.5 + age * 0.12, dash=age)

def _churn(g, cx, age, life):
    # churned patch: a cluster of short arcs that slowly settles
    rng = np.random.default_rng(7)
    for i in range(14):
        ox = rng.normal(0, 7)
        oy = rng.normal(0, 1.2)
        if (i + age // 9) % 3 == 0:
            continue
        for dxx in (-1.5, 0.0, 1.5):
            _put(g, cx + ox + dxx, SURF + 2 + oy)

# ------------------------------------------------------------------ episode
def offset_clip(frames, dx):
    out = []
    for f in frames:
        g = dict(f)
        g['root_x'] = f['root_x'] + dx
        if f['fish'] == 'free':
            g['fish_x'] = f['fish_x'] + dx
        out.append(g)
    return out

def build_episode():
    """Returns (poses list [flat dict or None for empty], events, spans).
    Zones: L root 28, C root 56-60, R root 84 (design units). Canon clips
    are authored at nominal root 60 / base stance; offsets chain so each
    clip starts where the previous one ended."""
    C = clips.all_clips()
    ep, spans, events = [], [], []

    def play(name, frames, note=''):
        start = len(ep)
        ep.extend(frames)
        spans.append({'clip': name, 'start': start, 'n': len(frames),
                      'note': note})
        return start

    cur = 28.0  # current root (design)
    def off(frames):
        return offset_clip(frames, cur - 60.0)

    play('idle_hunt_a@L', off(C['idle_hunt_a'][:264]), 'opening statue, left third')
    play('walk@L-C', off(C['walk']), 'stalk walk to the middle')
    cur = 56.0
    play('strike@C', off(C['strike']), 'tiny strike')
    play('swallow_tiny@C', off(C['swallow_tiny']), 'full eating sequence, tiny')
    play('idle_hunt_b@C', off(C['idle_hunt_b'][:96]), 'watched stillness')
    play('stretch@C', off(C['stretch']), 'same-side stretch')
    play('walk@C-R', off(C['walk']), 'walk to the right third (verbatim cycle)')
    cur = 84.0
    play('turn@R', off(C['turn']), 'THE TURN — drawn through the stops')
    tk = clips.takeoff(facing=-1)
    play('takeoff@R', offset_clip(tk, cur - 60.0), 'departure, facing left')
    empty_start = len(ep)
    ep.extend([None] * 96)
    spans.append({'clip': 'empty', 'start': empty_start, 'n': 96,
                  'note': 'the water settles; churn ring persists'})
    events.append((empty_start, 'ROOM_EMPTY'))
    ld = C['landing']  # canon landing runs root 44 -> 60; offset to land at L
    play('landing@L', offset_clip(ld, 28.0 - 60.0), 'measured landing, left third')
    cur = 28.0
    play('ruffle@L', off(C['ruffle']), 'post-landing ruffle (measured behavior)')
    play('idle_hunt_a@L2', off(C['idle_hunt_a'][264:312]), 'brief statue')
    a0 = play('alert@L', off(C['alert']), 'APPROACH — the take')
    events.append((a0, 'APPROACH'))
    events.append((a0 + 24, 'PRESENCE_SUSTAINED'))
    play('walk@L-C2', off(C['walk']), 'watched walk to the middle')
    cur = 56.0
    play('strike_big@C', off(C['strike_big']), 'big strike, deeper load')
    play('swallow@C', off(C['swallow']), 'THE eating sequence — flip, work-back, bulge')
    play('idle_hunt_c@C', off(C['idle_hunt_c'][:240]), 'closing statue with the slow scan')
    return ep, events, spans

def render_episode(out_mp4='preview_heron_v1_2.mp4', out_big=None,
                   contact=None):
    ep, events, spans = build_episode()
    ink = InkSim()
    frames_rgb = []
    ink_log_start = len(ink.events)
    for i, flat in enumerate(ep):
        if flat is None:
            grid = np.full((rig.H, rig.W), rig.WHITE, dtype=np.uint8)
            info = {'beak_tip': (0.0, 0.0), 'head': (0.0, 0.0)}
            pose = None
        else:
            pose = clips.unflatten(flat)
            grid, info = rig.render(pose)
            ink.observe(i, pose, info)
        grid = ink.draw(np.array(grid), i)
        frames_rgb.append(rig.PALETTE[grid])
    _write_mp4(frames_rgb, out_mp4, rig.W, rig.H)
    if out_big:
        _write_mp4(frames_rgb, out_big, 800, 480)
    meta = {'frames': len(ep), 'fps': 24, 'events': events, 'spans': spans,
            'ink_events': ink.events}
    with open('episode12_meta.json', 'w') as fh:
        json.dump(meta, fh, indent=1)
    print(f"episode: {len(ep)} frames ({len(ep)/24:.1f} s), "
          f"{len(ink.events)} ink events, {len(events)} presence events")
    return meta

def _write_mp4(frames_rgb, path, w, h):
    import os
    cmd = [os.environ.get('HERON_FFMPEG', 'ffmpeg'), '-y', '-loglevel', 'error', '-f', 'rawvideo',
           '-pix_fmt', 'rgb24', '-s', f'{frames_rgb[0].shape[1]}x{frames_rgb[0].shape[0]}',
           '-r', '24', '-i', '-', '-vf', f'scale={w}:{h}:flags=neighbor',
           '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', path]
    pr = subprocess.run(cmd, input=b''.join(f.tobytes() for f in frames_rgb))
    if pr.returncode != 0:
        raise RuntimeError(f'ffmpeg failed for {path}')

if __name__ == '__main__':
    render_episode()
