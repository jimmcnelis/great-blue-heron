"""Heron adapter parity: engine corpus path vs direct v1 code, same clips."""
import sys
sys.path.insert(0, '/home/hatch/workspace/creature-engine')
sys.path.insert(0, '/home/hatch/workspace/heron/src')
import numpy as np
from engine.package import Scene
from engine import corpus as corpus_mod
import clips as v1_clips
import rig as v1_rig

sc = Scene('/home/hatch/workspace/creature-engine/packages/heron-scene',
           '/home/hatch/workspace/creature-engine/packages')
out = '/home/hatch/workspace/creature-engine/plugtest-out/heron-corpus'
metas = corpus_mod.build_character(sc, 'heron', out,
                                   only=['idle_L_0', 'strike_tiny_0', 'turn_R_0'],
                                   log=lambda *a: None)
frames = np.load(out + '/heron_frames.npy')
by_name = {m['name']: m for m in metas}

# 1) idle_L_0 frame 0: byte-parity with a direct v1 render of the same pose
poses, _ = v1_clips.build_clip('idle', dict(zone='L', dur=20.0, seed=100))
g_direct, _ = v1_rig.render(poses[0])
m = by_name['idle_L_0']
g_engine = frames[m['start']]
print('idle_L_0 frame0 byte-identical to direct v1 render:', bool((g_engine == g_direct).all()))

# 2) mirrored variant is the exact horizontal flip
mm = by_name['idle_L_0_m']
print('idle_L_0_m == fliplr(idle_L_0):',
      bool((frames[mm['start']] == g_engine[:, ::-1]).all()))

# 3) strike: toss hook consumed the toss event; fish appears after the catch
sm = by_name['strike_tiny_0']
ev_types = [e['type'] for e in sm['events']]
fish = frames[sm['start']:sm['start'] + sm['count']]
fish_cells = np.isin(fish, [9, 10, 11]).sum(axis=(1, 2))
print('strike events after hooks:', ev_types)
print('strike fish cells: max', int(fish_cells.max()), '| frames with fish:',
      int((fish_cells > 0).sum()), 'of', sm['count'])

# 4) turn: squash hook narrowed the bird mid-turn
tm = by_name['turn_R_0']
tf = frames[tm['start']:tm['start'] + tm['count']]
widths = [int((tf[i] != 0).any(axis=0).sum()) for i in range(len(tf))]
print('turn widths: first', widths[0], '| mid', widths[len(widths) // 2], '| last', widths[-1])
print('turn squash applied:', widths[len(widths) // 2] < widths[0] * 0.6)
