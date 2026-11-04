"""Simulation player v1.1: behavior state machine over corpus latent trajectories.
Decodes an episode at 24 fps, composites the PROCEDURAL ink layer from physics
events, renders the preview mp4 at the corpus grid's native size (up = integer
upscale for the product render). The net never sees ink; ink is drawn from
events only. Decode honors the palette snap chosen at training time."""
import json, os, subprocess, sys
import numpy as np
import torch
import torch.nn.functional as Fn
from PIL import Image
import rig
from train import AE

FPS = 24
WATER_Y = rig.SURF_ROW
INK = rig.INK
SC = rig.W / 160.0          # ink geometry scale vs the v1 160-wide tuning grid

# ---------------------------------------------------------------- ink layer
class InkSim:
    def __init__(self):
        self.ripples = []   # (x, t0, rmax, dur)
        self.splashes = []  # (x, t0, scale, seed)
        self.drips = []     # (x, y, vy, t_spawn)
    def ripple(self, x, t, rmax=7.0, dur=1.1):
        self.ripples.append((x, t, rmax * SC, dur))
    def splash(self, x, t, scale=1.0, seed=0):
        self.splashes.append((x, t, scale, seed))
        self.ripple(x, t, 11 * scale, 1.4)
        self.ripple(x, t + 0.25, 7 * scale, 1.1)
    def draw(self, grid, t, beak_xy=None):
        g = grid
        H, W = g.shape
        band = max(1, int(round(0.8 * SC)))
        ywin = int(round(5 * SC))
        for (x, t0, rmax, dur) in self.ripples:
            age = t - t0
            if age < 0 or age > dur:
                continue
            r = rmax * (1 - (1 - age / dur) ** 2)
            if r < 0.8 * SC:
                continue
            xs = np.arange(max(0, int(x - rmax - 2)), min(W, int(x + rmax + 3)))
            for xx in xs:
                for yy in range(WATER_Y - ywin, WATER_Y + ywin + 1):
                    d = np.hypot(xx - x, (yy - WATER_Y) * 3.1)
                    if abs(d - r) < band and g[yy, xx] == rig.WHITE:
                        g[yy, xx] = INK
        for (x, t0, scale, seed) in self.splashes:
            age = t - t0
            if age < 0 or age > 0.5:
                continue
            rng = np.random.default_rng(seed)
            for k in range(9):
                vx = rng.uniform(-9, 9) * scale * SC
                vy = rng.uniform(-26, -13) * scale * SC
                px = x + vx * age
                py = WATER_Y - 1 + vy * age + 60 * SC * age * age
                if 0 <= int(px) < W and 0 <= int(py) < H and g[int(py), int(px)] == rig.WHITE:
                    g[int(py), int(px)] = INK
        alive = []
        for (x, y, vy, ts) in self.drips:
            yy = y + vy * (t - ts) + 30 * SC * (t - ts) ** 2
            if yy >= WATER_Y:
                self.ripple(x, t, 3.2, 0.7)
                continue
            alive.append((x, y, vy, ts))
            if 0 <= int(yy) < H and 0 <= int(x) < W and g[int(yy), int(x)] == rig.WHITE:
                g[int(yy), int(x)] = INK
        self.drips = alive

# ---------------------------------------------------------------- episode
def build_episode(model_pfx='/home/jim/heron/model11', corpus_pfx='/home/jim/heron/corpus11'):
    clips = json.load(open(corpus_pfx + '_clips.json'))
    by_name = {c['name']: c for c in clips}
    lat = np.load(model_pfx + '_latents.npy')
    beaks_all = np.load(corpus_pfx + '_beaks.npy')
    dyn = np.load(model_pfx + '_dynamics.npz')
    mean, comps, a1, a2, innov = dyn['mean'], dyn['comps'], dyn['a1'], dyn['a2'], dyn['innov']

    # Same arc as v1 (segment lengths doubled for the 24 fps timebase).
    script = [
        ('idle_L_0',    0, 264, 'idle', 'empty'),
        ('walk_LC_0',   0, None, None, 'empty'),
        ('strike_tiny_0', 0, None, None, 'empty'),
        ('idle_C_1',    0, 96, 'idle', 'empty'),
        ('stretch_1',   0, None, None, 'empty'),
        ('walk_CR_0',   0, None, None, 'empty'),
        ('turn_R_0',    0, None, None, 'empty'),
        ('idle_L_1_m',  0, 168, 'idle', 'empty'),
        ('turn_L_0_m',  0, None, None, 'empty'),
        ('takeoff_R_0', 0, None, None, 'empty'),
        ('empty',       0, 96, None, 'empty'),
        ('flyin_L_0',   0, None, None, 'empty'),
        ('idle_L_2',    0, 72, 'idle', 'empty'),
        ('alert_L_0',   0, None, None, 'approach'),   # APPROACH: notices the viewer
        ('walk_LC_1',   0, None, None, 'sustained'),  # fishes for its audience
        ('strike_big_0', 0, None, None, 'sustained'),
        ('idle_C_3',    0, 144, 'idle', 'sustained'),
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
            ramp = np.minimum(1.0, np.minimum(np.arange(len(seg_lat)), np.arange(len(seg_lat))[::-1]) / float(FPS))
            amp = float(os.environ.get('HERON_NOISE', '0.55'))
            seg_lat += (n * (amp * ramp[:, None])) @ comps
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

def decode_all(model, lat, snap_mode='argmax', bs=192):
    grids = np.empty((len(lat), rig.H, rig.W), dtype=np.uint8)
    palette = torch.tensor(rig.PALETTE, dtype=torch.float32).cuda()
    with torch.no_grad():
        for i in range(0, len(lat), bs):
            z = torch.from_numpy(lat[i:i + bs]).cuda()
            logits = model.decode(z)
            if snap_mode == 'rgb':
                p = torch.softmax(logits, dim=1)
                rgb = torch.einsum('bkhw,kc->bhwc', p, palette)
                d = ((rgb[:, :, :, None, :] - palette[None, None, None, :, :]) ** 2).sum(-1)
                pred = d.argmin(-1)
            else:
                pred = logits.argmax(1)
            grids[i:i + bs] = pred.cpu().numpy().astype(np.uint8)
    return grids

# ---------------------------------------------------------------- hygiene
def _label_same_color(g):
    """Two-pass union-find labeling of 4-connected same-color non-white cells.
    Returns (labels int32 HxW, sizes dict label->count)."""
    H, W = g.shape
    lab = np.zeros((H, W), dtype=np.int32)
    parent = [0]
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)
    coords = np.argwhere(g != rig.WHITE)   # row-major, subject cells only
    nxt = 1
    for y, x in coords:
        c = g[y, x]
        ups = []
        if y > 0 and g[y - 1, x] == c and lab[y - 1, x]:
            ups.append(lab[y - 1, x])
        if x > 0 and g[y, x - 1] == c and lab[y, x - 1]:
            ups.append(lab[y, x - 1])
        if not ups:
            lab[y, x] = nxt
            parent.append(nxt)
            nxt += 1
        else:
            m = min(ups)
            lab[y, x] = m
            for u in ups:
                union(m, u)
    sizes = {}
    for y, x in coords:
        r = find(int(lab[y, x]))
        lab[y, x] = r
        sizes[r] = sizes.get(r, 0) + 1
    return lab, sizes

def hygiene(grids, segments, beaks):
    """Rendering hygiene in service of the drawn look, in fixed order:
    (1) orphan absorption: small same-color components that touch neither the
        main subject mass nor the beak zone (eye, beak tip live there) are
        reassigned to their dominant neighboring color;
    (2) deflicker: A-B-A single-frame flips inside held segments (idle, alert,
        empty) are snapped back, except inside the beak zone (blinks live
        there). Returns (clean_grids, stats). Ink is composited later and is
        never touched by either pass."""
    N, H, W = grids.shape
    R = max(6, int(round(16 * W / 320.0)))     # beak-zone radius in cells
    max_orphan = 6
    out = grids.copy()
    orphans_removed = 0
    # ---- pass 1: orphans
    for t in range(N):
        g = out[t]
        lab, sizes = _label_same_color(g)
        if not sizes:
            continue
        main_lab = max(sizes, key=sizes.get)
        main_mask = lab == main_lab
        near_main = np.zeros((H, W), bool)
        near_main[1:, :] |= main_mask[:-1, :]; near_main[:-1, :] |= main_mask[1:, :]
        near_main[:, 1:] |= main_mask[:, :-1]; near_main[:, :-1] |= main_mask[:, 1:]
        bx, by = (beaks[t] if t < len(beaks) else (-99, -99))
        yy, xx = np.mgrid[0:H, 0:W]
        beak_zone = (xx - bx) ** 2 + (yy - by) ** 2 <= R * R if bx >= 0 else np.zeros((H, W), bool)
        protected = near_main | beak_zone
        for l, sz in sizes.items():
            if l == main_lab or sz > max_orphan:
                continue
            cells = lab == l
            if protected[cells].any():
                continue
            ring = np.zeros((H, W), bool)
            ring[1:, :] |= cells[:-1, :]; ring[:-1, :] |= cells[1:, :]
            ring[:, 1:] |= cells[:, :-1]; ring[:, :-1] |= cells[:, 1:]
            ring[1:, 1:] |= cells[:-1, :-1]; ring[:-1, :-1] |= cells[1:, 1:]
            ring[1:, :-1] |= cells[:-1, 1:]; ring[:-1, 1:] |= cells[1:, :-1]
            ring &= ~cells
            vals = g[ring]
            if len(vals) == 0:
                continue
            newc = np.bincount(vals, minlength=12).argmax()
            g[cells] = newc
            orphans_removed += sz
    # ---- pass 2: deflicker inside held segments
    held = np.zeros(N, bool)
    for s in segments:
        if s['name'].startswith(('idle', 'alert', 'empty')):
            held[s['start']:s['start'] + s['count']] = True
    def aba_count(G):
        if N < 3:
            return 0
        flip = (G[1:-1] != G[:-2]) & (G[2:] == G[:-2])
        flip &= held[1:-1, None, None]
        return int(flip.sum())
    aba_before = aba_count(out)
    fixed = 0
    for t in range(1, N - 1):
        if not held[t]:
            continue
        A, B, C = out[t - 1], out[t], out[t + 1]
        cand = (A == C) & (A != B)
        if not cand.any():
            continue
        bx, by = (beaks[t] if t < len(beaks) else (-99, -99))
        if bx >= 0:
            yy, xx = np.mgrid[0:H, 0:W]
            cand &= ~((xx - bx) ** 2 + (yy - by) ** 2 <= R * R)
        if not cand.any():
            continue
        # the flipped cell must sit in a stable neighborhood of A on both sides
        Ap = np.pad(A, 1, mode='edge')
        stab = np.zeros((H, W), int)
        for dy in range(3):
            for dx in range(3):
                if dx == 1 and dy == 1:
                    continue
                stab += (Ap[dy:dy + H, dx:dx + W] == A)
        cand &= stab >= 4
        if cand.any():
            B[cand] = A[cand]
            fixed += int(cand.sum())
    aba_after = aba_count(out)
    stats = dict(orphan_cells_removed=int(orphans_removed),
                 orphan_cells_per_frame=round(orphans_removed / max(N, 1), 3),
                 aba_flips_held_before=aba_before, aba_flips_held_after=aba_after,
                 aba_cells_fixed=int(fixed))
    print('hygiene:', stats, flush=True)
    return out, stats

def main(corpus_pfx='/home/jim/heron/corpus11', model_pfx='/home/jim/heron/model11',
         out='/home/jim/heron/preview_heron_v1_1.mp4', tag='11', up=1,
         ffmpeg='/home/jim/wedding/tools/ffmpeg-7.0.2-arm64-static/ffmpeg'):
    cfg = json.load(open(model_pfx + '_config.json'))
    model = AE(cfg['H'], cfg['W'], latent=cfg['latent'], chans=tuple(cfg['chans'])).cuda()
    model.load_state_dict(torch.load(model_pfx + '.pt'))
    model.eval()
    lat, beaks, events, segments, presence_events = build_episode(model_pfx, corpus_pfx)
    print('episode frames:', len(lat), '=', len(lat) / FPS, 's', flush=True)
    print('presence events:', presence_events)
    grids = decode_all(model, lat, snap_mode=cfg.get('snap_mode', 'argmax'))
    grids, hyg = hygiene(grids, segments, beaks)
    ink = InkSim()
    drip_beak = {}
    for e in events:
        if e['type'] == 'drips':
            for f in range(e['f'], e['f_end']):
                drip_beak[f] = beaks[f]
    out_grids = []
    drip_every = max(1, FPS // 4)
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
        if i in drip_beak and i % drip_every == 0:
            bx, by = drip_beak[i]
            ink.drips.append((float(bx), float(by + 1), 2.0, t))
        g = grids[i].copy()
        ink.draw(g, t)
        out_grids.append(g)
    np.save(f'/home/jim/heron/episode_grids_{tag}.npy', np.stack(out_grids))
    with open(f'/home/jim/heron/episode_log_{tag}.json', 'w') as f:
        json.dump(dict(segments=segments, events=events, presence=presence_events,
                       hygiene=hyg), f)
    ow, oh = rig.W * up, rig.H * up
    proc = subprocess.Popen([ffmpeg, '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                             '-s', f'{ow}x{oh}', '-r', str(FPS), '-i', '-',
                             '-c:v', 'libx264', '-crf', '10', '-pix_fmt', 'yuv420p', out],
                            stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for g in out_grids:
        rgb = rig.PALETTE[g]
        frame = np.asarray(Image.fromarray(rgb).resize((ow, oh), Image.NEAREST), dtype=np.uint8)
        proc.stdin.write(frame.tobytes())
    proc.stdin.close(); proc.wait()
    print('wrote', out)

if __name__ == '__main__':
    args = sys.argv[1:]
    kw = {}
    if len(args) > 0: kw['corpus_pfx'] = args[0]
    if len(args) > 1: kw['model_pfx'] = args[1]
    if len(args) > 2: kw['out'] = args[2]
    if len(args) > 3: kw['tag'] = args[3]
    if len(args) > 4: kw['up'] = int(args[4])
    main(**kw)
