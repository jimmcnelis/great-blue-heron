"""Heron v1.2 corpus: the authored canon, banked as pose trajectories.

The corpus IS the pose data (the rig renders deterministically), so this
banks: per-clip flat pose frames, clip table, and rendered anchors
(beak tip / head, grid coords) for the canon at nominal root. Training
variety comes from scheduling: zone-offset copies of the grounded clips
are added as extra pose rows (same authored motion, different root_x —
the offset is applied to root_x and fish_x only).
"""
import json
import numpy as np
import rig
import clips

POSE_KEYS = clips.FLAT_KEYS
FISH_CODE = {'none': 0, 'held': 1, 'free': 2}
SIZE_CODE = {'tiny': 0, 'big': 1}
# held-out ENTIRE clips: the pose model never trains on these
VAL_CLIPS = {'swallow_tiny', 'turn_reverse', 'glide', 'balance_flick',
             'idle_hunt_c'}

def offset_frames(frames, dx):
    out = []
    for f in frames:
        g = dict(f)
        g['root_x'] = f['root_x'] + dx
        if f['fish'] == 'free':
            g['fish_x'] = f['fish_x'] + dx
        out.append(g)
    return out

def main():
    canon = clips.all_clips()
    rows, table = [], []
    anchors = {}
    for name, frames in canon.items():
        start = len(rows)
        for f in frames:
            rows.append([f[k] for k in POSE_KEYS] +
                        [FISH_CODE[f['fish']], SIZE_CODE[f['fish_size']]])
        table.append({'clip': name, 'start': start, 'n': len(frames),
                      'split': 'val' if name in VAL_CLIPS else 'train'})
        # anchors for the canon at nominal root
        tips, heads = [], []
        for f in frames:
            _g, info = rig.render(clips.unflatten(f))
            tips.append(info['beak_tip'])
            heads.append(info['head'])
        anchors[name] = {'beak_tip': tips, 'head': heads}
        print(f"{name:16s} {len(frames):4d}  ({table[-1]['split']})")
    # zone-offset copies (train split only): grounded clips at L and R
    grounded = ['idle_hunt_a', 'idle_hunt_b', 'strike', 'swallow', 'walk',
                'step_cycle', 'alert', 'stretch', 'preen', 'scratch',
                'ruffle', 'oneleg_enter', 'doze', 'head_turn', 'turn']
    for name in grounded:
        for dx in (-32.0, 32.0):
            frames = offset_frames(canon[name], dx)
            start = len(rows)
            for f in frames:
                rows.append([f[k] for k in POSE_KEYS] +
                            [FISH_CODE[f['fish']], SIZE_CODE[f['fish_size']]])
            table.append({'clip': f'{name}@{"L" if dx < 0 else "R"}',
                          'start': start, 'n': len(frames), 'split': 'train'})
    X = np.array(rows, dtype=np.float32)
    print("pose matrix:", X.shape)
    np.savez_compressed('corpus12_poses.npz', X=X,
                        keys=np.array(POSE_KEYS + ['fish_code', 'size_code']),
                        table=np.array([json.dumps(t) for t in table]))
    with open('anchors12.json', 'w') as fh:
        json.dump(anchors, fh)
    print("banked corpus12_poses.npz + anchors12.json")

if __name__ == '__main__':
    main()
