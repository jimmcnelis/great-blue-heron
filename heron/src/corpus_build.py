"""Build the behavior corpus: render all clips (+ mirrored variants) to palette-index frames."""
import json, sys
import numpy as np
from multiprocessing import Pool
import rig, clips

FPS = clips.FPS

def _render_clip(poses):
    frames = np.empty((len(poses), rig.H, rig.W), dtype=np.uint8)
    beaks = np.zeros((len(poses), 2), dtype=np.float32)
    for i, p in enumerate(poses):
        g, info = rig.render(p)
        frames[i] = g
        beaks[i] = info['beak_tip']
    return frames, beaks

def _patch_toss(poses, events, beaks):
    """Ballistic fish toss using measured beak tips."""
    toss = next((e for e in events if e['type'] == 'toss'), None)
    if toss is None:
        return
    f0 = toss['f']
    dur_f = 6  # 0.5 s airborne
    x0, y0 = beaks[f0]
    vx, vy, g = 6.0, -16.0, 58.0
    for k in range(dur_f):
        i = f0 + k
        if i >= len(poses):
            break
        t = k / FPS
        poses[i]['fish'] = 'free'
        poses[i]['fish_x'] = float(x0 + vx * t)
        poses[i]['fish_y'] = float(y0 + vy * t + 0.5 * g * t * t)
        poses[i]['fish_free_ang'] = float(-60 + 260 * (k / dur_f))
    events.remove(toss)

def _job(job):
    name, kind, kwargs, mirror = job
    poses, events = clips.build_clip(kind, kwargs)
    if kind == 'empty':
        frames = np.zeros((len(poses), rig.H, rig.W), dtype=np.uint8)
        beaks = np.zeros((len(poses), 2), dtype=np.float32)
    else:
        frames, beaks = _render_clip(poses)
        if any(e['type'] == 'toss' for e in events):
            _patch_toss(poses, events, beaks)
            frames, beaks = _render_clip(poses)
        if kind == 'turn':
            # horizontal squash sweep 1 -> -1 around the root column (palette-exact:
            # nearest column remap of index grids; |f| clamped so the bird never vanishes)
            cx = float(rig._mx(clips.ZONE[kwargs['zone']]))
            n = len(frames)
            jj = np.arange(rig.W)
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
                src = np.clip(np.round(cx + (jj - cx) / f).astype(int), 0, rig.W - 1)
                out[i] = frames[i][:, src]
            frames = out
    zf = kwargs.get('zone') or kwargs.get('x_from')
    zt = kwargs.get('zone') or kwargs.get('x_to')
    facing = 1
    for e in events:  # design-space x -> grid x
        e['x'] = float(rig._mx(e['x']))
    if mirror:
        frames = np.ascontiguousarray(frames[:, :, ::-1])
        beaks = beaks.copy(); beaks[:, 0] = (rig.W - 1) - beaks[:, 0]
        for e in events:
            e['x'] = float((rig.W - 1) - e['x'])
        swap = {'L': 'R', 'R': 'L', 'C': 'C'}
        zf, zt = swap.get(zf, zf), swap.get(zt, zt)
        facing = -1
        name = name + '_m'
    meta = dict(name=name, kind=kind, facing=facing, zone_from=zf, zone_to=zt,
                count=len(frames), events=events)
    return frames, beaks, meta

def main(out_prefix='corpus'):
    specs = clips.clip_specs()
    jobs = []
    for name, kind, kwargs in specs:
        jobs.append((name, kind, kwargs, False))
        if kind != 'empty':
            jobs.append((name, kind, kwargs, True))
    print(f'{len(jobs)} clip jobs')
    all_frames, all_beaks, metas = [], [], []
    with Pool(16) as pool:
        for frames, beaks, meta in pool.imap(_job, jobs):
            meta['start'] = int(sum(m['count'] for m in metas))
            metas.append(meta)
            all_frames.append(frames); all_beaks.append(beaks)
            print('done', meta['name'], meta['count'], flush=True)
    F = np.concatenate(all_frames); B = np.concatenate(all_beaks)
    np.save(f'{out_prefix}_frames.npy', F)
    np.save(f'{out_prefix}_beaks.npy', B)
    with open(f'{out_prefix}_clips.json', 'w') as f:
        json.dump(metas, f)
    print('TOTAL frames:', len(F), 'clips:', len(metas))

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'corpus')
