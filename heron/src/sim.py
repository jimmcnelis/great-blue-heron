"""Simulation player: behavior state machine over corpus latent trajectories.
Decodes an episode, composites the PROCEDURAL ink layer from physics events,
renders the preview mp4. The net never sees ink; ink is drawn from events only.
"""
import json, subprocess, sys
import numpy as np
import torch
import torch.nn.functional as Fn
from PIL import Image
import rig
from train import AE

FPS = 12
WATER_Y = rig.SURF_ROW
INK = rig.INK

# ---------------------------------------------------------------- ink layer
class InkSim:
    def __init__(self):
        self.ripples = []   # (x, t0, rmax, dur)
        self.splashes = []  # (x, t0, scale, seed)
        self.drips = []     # (x, y, vy, t_spawn)
    def ripple(self, x, t, rmax=7.0, dur=1.1):
        self.ripples.append((x, t, rmax, dur))
    def splash(self, x, t, scale=1.0, seed=0):
        self.splashes.append((x, t, scale, seed))
        self.ripple(x, t, 11 * scale, 1.4)
        self.ripple(x, t + 0.25, 7 * scale, 1.1)
    def draw(self, grid, t, beak_xy=None):
        g = grid
        H, W = g.shape
        # ripples: expanding squashed rings on the implied surface
        for (x, t0, rmax, dur) in self.ripples:
            age = t - t0
            if age < 0 or age > dur:
                continue
            r = rmax * (1 - (1 - age / dur) ** 2)
            if r < 0.8:
                continue
            xs = np.arange(max(0, int(x - rmax - 2)), min(W, int(x + rmax + 3)))
            for xx in xs:
                for yy in range(WATER_Y - 4, WATER_Y + 5):
                    d = np.hypot(xx - x, (yy - WATER_Y) * 3.1)
                    if abs(d - r) < 0.8 and g[yy, xx] == rig.WHITE:
                        g[yy, xx] = INK
        # splashes: deterministic droplet arcs above the point
        for (x, t0, scale, seed) in self.splashes:
            age = t - t0
            if age < 0 or age > 0.5:
                continue
            rng = np.random.default_rng(seed)
            for k in range(9):
                vx = rng.uniform(-9, 9) * scale
                vy = rng.uniform(-26, -13) * scale
                px = x + vx * age
                py = WATER_Y - 1 + vy * age + 60 * age * age
                if 0 <= int(px) < W and 0 <= int(py) < H and g[int(py), int(px)] == rig.WHITE:
                    g[int(py), int(px)] = INK
        # drips: fall from beak to surface, tiny ring on arrival
        alive = []
        for (x, y, vy, ts) in self.drips:
            yy = y + vy * (t - ts) + 30 * (t - ts) ** 2
            if yy >= WATER_Y:
                self.ripple(x, t, 3.2, 0.7)
                continue
            alive.append((x, y, vy, ts))
            if 0 <= int(yy) < H and 0 <= int(x) < W and g[int(yy), int(x)] == rig.WHITE:
                g[int(yy), int(x)] = INK
        self.drips = alive

# ---------------------------------------------------------------- episode
def build_episode(model_pfx='/home/jim/heron/model', corpus_pfx='/home/jim/heron/corpus'):
    clips = json.load(open(corpus_pfx + '_clips.json'))
    by_name = {c['name']: c for c in clips}
    lat = np.load(model_pfx + '_latents.npy')
    beaks_all = np.load(corpus_pfx + '_beaks.npy')
    dyn = np.load(model_pfx + '_dynamics.npz')
    mean, comps, a1, a2, innov = dyn['mean'], dyn['comps'], dyn['a1'], dyn['a2'], dyn['innov']

    # (clip, f0, f1, noise, presence) — presence is a first-class state-machine input:
    # 'empty' = ROOM_EMPTY baseline life; 'approach' fires the APPROACH response at
    # segment start; 'sustained' = PRESENCE_SUSTAINED (someone is watching).
    script = [
        ('idle_L_0',    0, 132, 'idle', 'empty'),
        ('walk_LC_0',   0, None, None, 'empty'),
        ('strike_tiny_0', 0, None, None, 'empty'),
        ('idle_C_1',    0, 48, 'idle', 'empty'),
        ('stretch_1',   0, None, None, 'empty'),
        ('walk_CR_0',   0, None, None, 'empty'),
        ('turn_R_0',    0, None, None, 'empty'),
        ('idle_L_1_m',  0, 84, 'idle', 'empty'),
        ('turn_L_0_m',  0, None, None, 'empty'),
        ('takeoff_R_0', 0, None, None, 'empty'),
        ('empty',       0, 48, None, 'empty'),
        ('flyin_L_0',   0, None, None, 'empty'),
        ('idle_L_2',    0, 36, 'idle', 'empty'),
        ('alert_L_0',   0, None, None, 'approach'),   # APPROACH: notices the viewer
        ('walk_LC_1',   0, None, None, 'sustained'),  # fishes for its audience
        ('strike_big_0', 0, None, None, 'sustained'),
        ('idle_C_3',    0, 72, 'idle', 'sustained'),
    ]
    presence_events = [dict(frame=0, event='ROOM_EMPTY',
                            response='unwatched baseline: idle/doze weights armed, fishing at base rate')]
    rng = np.random.default_rng(42)
    ep_lat, ep_beak, ep_events, segments = [], [], [], []
    t_cursor = 0
    for name, f0, f1, noise, presence in script:
        if presence == 'approach':
            presence_events.append(dict(frame=t_cursor, event='APPROACH',
                                        response='alert/head-up acknowledgment, then walk to center and fish for the audience'))
        if presence == 'sustained' and presence_events[-1]['event'] == 'APPROACH':
            presence_events.append(dict(frame=t_cursor, event='PRESENCE_SUSTAINED',
                                        response='watched: fishing probability raised, doze suppressed'))
        c = by_name[name]
        f1 = c['count'] if f1 is None else min(f1, c['count'])
        seg_lat = lat[c['start'] + f0: c['start'] + f1].copy()
        seg_beak = beaks_all[c['start'] + f0: c['start'] + f1]
        if noise == 'idle':
            npc = comps.shape[0]
            n = np.zeros((len(seg_lat), npc), dtype=np.float32)
            state = np.zeros((2, npc), dtype=np.float32)
            for i in range(len(seg_lat)):
                new = a1 * state[0] + a2 * state[1] + rng.normal(0, 1, npc) * innov
                state[1] = state[0]; state[0] = new
                n[i] = new
            ramp = np.minimum(1.0, np.minimum(np.arange(len(seg_lat)), np.arange(len(seg_lat))[::-1]) / 12.0)
            seg_lat += (n * (0.55 * ramp[:, None])) @ comps
        for e in c['events']:
            if f0 <= e['f'] < f1:
                ee = dict(e); ee['f'] = e['f'] - f0 + t_cursor
                if 'f_end' in e:
                    ee['f_end'] = min(e['f_end'], f1) - f0 + t_cursor
                ep_events.append(ee)
        segments.append(dict(name=name, start=t_cursor, count=len(seg_lat), presence=presence))
        ep_lat.append(seg_lat); ep_beak.append(seg_beak)
        t_cursor += len(seg_lat)
    return np.concatenate(ep_lat), np.concatenate(ep_beak), ep_events, segments, presence_events

def decode_all(model, lat, bs=256):
    grids = np.empty((len(lat), rig.H, rig.W), dtype=np.uint8)
    with torch.no_grad():
        for i in range(0, len(lat), bs):
            z = torch.from_numpy(lat[i:i + bs]).cuda()
            grids[i:i + bs] = model.decode(z).argmax(1).cpu().numpy().astype(np.uint8)
    return grids

def main(ffmpeg='/home/jim/wedding/tools/ffmpeg-7.0.2-arm64-static/ffmpeg',
         out='/home/jim/heron/preview_heron_v1.mp4',
         corpus_pfx='/home/jim/heron/corpus120', model_pfx='/home/jim/heron/model120'):
    model = AE().cuda()
    model.load_state_dict(torch.load(model_pfx + '.pt'))
    model.eval()
    lat, beaks, events, segments, presence_events = build_episode(model_pfx, corpus_pfx)
    print('episode frames:', len(lat), '=', len(lat) / FPS, 's')
    print('presence events:', presence_events)
    grids = decode_all(model, lat)
    ink = InkSim()
    drip_until = -1
    drip_beak = {}
    for e in events:
        if e['type'] == 'drips':
            drip_until = e['f_end']
            for f in range(e['f'], e['f_end']):
                drip_beak[f] = beaks[f]
    out_grids = []
    for i in range(len(grids)):
        t = i / FPS
        for e in events:
            if e['f'] != i:
                continue
            if e['type'] == 'step':
                ink.ripple(e['x'], t, 6.5, 1.05)
            elif e['type'] == 'splash':
                ink.splash(e['x'], t, 1.0, seed=i)
            elif e['type'] == 'takeoff':
                ink.splash(e['x'], t, 1.25, seed=i); ink.ripple(e['x'], t + 0.15, 13, 1.6)
            elif e['type'] == 'landing':
                ink.splash(e['x'], t, 1.1, seed=i); ink.ripple(e['x'], t + 0.1, 12, 1.5)
        if i in drip_beak and i % 3 == 0:
            bx, by = drip_beak[i]
            ink.drips.append((float(bx), float(by + 1), 2.0, t))
        g = grids[i].copy()
        ink.draw(g, t)
        out_grids.append(g)
    np.save('/home/jim/heron/episode_grids.npy', np.stack(out_grids))
    with open('/home/jim/heron/episode_log.json', 'w') as f:
        json.dump(dict(segments=segments, events=events, presence=presence_events), f)
    # presence interface contract for the firmware port (hardware binding happens there)
    iface = dict(
        inputs=dict(
            approach='rising edge of presence (LD2410-class mmWave OUT pin / UART presence flag 0->1)',
            presence_sustained='presence flag held high',
            room_empty='presence flag low continuously for > 120 s',
            ambient_light='BH1750-class lux sensor; below night threshold -> dim palette + sleep weights (no camera, no microphone, ever)'),
        state_machine_contract=dict(
            APPROACH='interrupt idle/doze -> alert clip (head-up acknowledgment); raise fishing probability while sustained',
            PRESENCE_SUSTAINED='doze suppressed; fishing probability raised; alert re-arms on re-approach',
            ROOM_EMPTY='settle/doze weights armed (one-leg rest, long stillness); fishing at base rate'),
        preview_note='v1 preview scripts the presence track: ROOM_EMPTY until the marked APPROACH frame, PRESENCE_SUSTAINED after; see episode_log.json')
    with open('/home/jim/heron/presence_interface.json', 'w') as f:
        json.dump(iface, f, indent=1)
    # render mp4: 12 fps sim -> 24 fps video (each frame x2), exact x2 upscale of the
    # 160x120 master grid = 320x240, the bench BOX-3's native resolution, full-bleed
    proc = subprocess.Popen([ffmpeg, '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                             '-s', '320x240', '-r', '24', '-i', '-',
                             '-c:v', 'libx264', '-crf', '10', '-pix_fmt', 'yuv420p', out],
                            stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for g in out_grids:
        rgb = rig.PALETTE[g]
        frame = np.asarray(Image.fromarray(rgb).resize((320, 240), Image.NEAREST), dtype=np.uint8)
        proc.stdin.write(frame.tobytes()); proc.stdin.write(frame.tobytes())
    proc.stdin.close(); proc.wait()
    print('wrote', out)

if __name__ == '__main__':
    main(*sys.argv[1:])
