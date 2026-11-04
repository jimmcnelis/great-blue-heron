"""Build the behavior corpus: render all clips (+ mirrored variants) to palette-index frames."""
import json, sys
import numpy as np
from multiprocessing import Pool
import rig, clips

FPS = clips.FPS

# ---- pose banking (v1.2 pose-space seed): the authored per-frame parameter
# stream, frame-aligned with the rendered corpus. Poses are banked in AUTHORED
# orientation; mirrored clips pair with facing=-1 in the clips json (mirror
# root_x/fish_x against the design width to recover the rendered side).
POSE_COLUMNS = ['root_x', 'root_y', 'body_tilt', 'neck_coil', 'neck_extend',
                'neck_sway', 'neck_retract', 'head_pitch', 'plume_sway',
                'blink', 'look_back', 'wing_amt', 'flap', 'flying',
                'leg_far_fx', 'leg_far_fy', 'leg_near_fx', 'leg_near_fy',
                'tail_ang', 'hide_near', 'fish_ang', 'fish_slide',
                'fish_x', 'fish_y', 'fish_free_ang', 'turn_f',
                'fish_code', 'fish_size_code']
FISH_CODE = {'none': 0.0, 'held': 1.0, 'free': 2.0}
FISH_SIZE_CODE = {'tiny': 0.0, 'big': 1.0}

def _flatten_poses(poses, turn_fs=None):
    out = np.zeros((len(poses), len(POSE_COLUMNS)), dtype=np.float32)
    for i, p in enumerate(poses):
        base = rig.default_pose()
        base.update(p)
        row = {}
        for k, v in base.items():
            if isinstance(v, dict):
                for kk, vv in v.items():
                    row[f'{k}_{kk}'] = float(vv)
            elif k == 'fish':
                row['fish_code'] = FISH_CODE.get(v, -1.0)
            elif k == 'fish_size':
                row['fish_size_code'] = FISH_SIZE_CODE.get(v, -1.0)
            else:
                row[k] = float(v)
        row['turn_f'] = 1.0 if turn_fs is None else float(turn_fs[i])
        for j, c in enumerate(POSE_COLUMNS):
            out[i, j] = row.get(c, 0.0)
    return out

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
    dur_f = FPS // 2  # 0.5 s airborne
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
    turn_fs = None
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
            turn_fs = np.ones(n, dtype=np.float32)
            for i in range(n):
                u = i / max(n - 1, 1)  # phase-based squash (fps-independent)
                if u < 0.18:
                    f = 1.0
                elif u < 0.75:
                    f = float(np.cos(np.pi * (u - 0.18) / 0.57))
                else:
                    f = -1.0
                if abs(f) < 0.14:
                    f = 0.14 if f >= 0 else -0.14
                turn_fs[i] = f
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
    return frames, beaks, meta, _flatten_poses(poses, turn_fs)

def main(out_prefix='corpus'):
    specs = clips.clip_specs()
    jobs = []
    for name, kind, kwargs in specs:
        jobs.append((name, kind, kwargs, False))
        if kind != 'empty':
            jobs.append((name, kind, kwargs, True))
    print(f'{len(jobs)} clip jobs')
    all_frames, all_beaks, metas, all_poses = [], [], [], []
    with Pool(16) as pool:
        for frames, beaks, meta, pose_arr in pool.imap(_job, jobs):
            meta['start'] = int(sum(m['count'] for m in metas))
            metas.append(meta)
            all_frames.append(frames); all_beaks.append(beaks); all_poses.append(pose_arr)
            print('done', meta['name'], meta['count'], flush=True)
    F = np.concatenate(all_frames); B = np.concatenate(all_beaks)
    P = np.concatenate(all_poses)
    assert len(P) == len(F)
    np.save(f'{out_prefix}_frames.npy', F)
    np.save(f'{out_prefix}_beaks.npy', B)
    np.savez_compressed(f'{out_prefix}_poses.npz', data=P,
                        columns=np.array(POSE_COLUMNS))
    with open(f'{out_prefix}_poses.json', 'w') as f:
        json.dump(dict(columns=POSE_COLUMNS, fish_code=FISH_CODE,
                       fish_size_code=FISH_SIZE_CODE, fps=FPS,
                       design_space='120x90 (normalized rig units)',
                       orientation='authored; mirrored clips carry facing=-1 in the clips json',
                       turn_f='per-frame horizontal squash factor (1.0 except turn clips)',
                       frames=len(F)), f, indent=1)
    with open(f'{out_prefix}_clips.json', 'w') as f:
        json.dump(metas, f)
    print('TOTAL frames:', len(F), 'clips:', len(metas), 'poses banked:', P.shape)

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'corpus')
