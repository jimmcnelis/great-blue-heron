"""Cheap measurable checks from the cartoon-animation-craft skill, run on the
finished episode + corpus: anticipation depth/hold, strike spacing (accelerate
in), held fraction and still stretches in idles, beak-tip aliveness in holds,
follow-through proxy after the landing and the swallow, strike beak speed
(smear audit input). Prints JSON."""
import json, sys
import numpy as np

def beak_speeds(beaks, f0, f1):
    seg = beaks[f0:f1].astype(np.float64)
    d = np.hypot(*np.diff(seg, axis=0).T)
    return d

def main(corpus_pfx='/home/jim/heron/corpus11', tag='11', model_pfx=None):
    clips = {c['name']: c for c in json.load(open(corpus_pfx + '_clips.json'))}
    beaks = np.load(corpus_pfx + '_beaks.npy')
    poses = np.load(corpus_pfx + '_poses.npz')
    P, cols = poses['data'], list(poses['columns'])
    ci = {c: i for i, c in enumerate(cols)}
    G = np.load(f'/home/jim/heron/episode_grids_{tag}.npy')
    log = json.load(open(f'/home/jim/heron/episode_log_{tag}.json'))
    segs = {s['name']: s for s in log['segments']}
    out = {}
    # ---- anticipation + spacing on every strike clip (corpus side)
    rows = []
    for name, c in clips.items():
        if c['kind'] != 'strike':
            continue
        sp = next((e for e in c['events'] if e['type'] == 'splash'), None)
        if sp is None:
            continue
        f = c['start'] + sp['f']
        coil = P[c['start']:f + 1, ci['neck_coil']]
        depth = float(coil.max())
        deep = np.nonzero(coil >= 0.92 * depth)[0]
        hold_frames = int(f - c['start'] - deep[0] + 1) if len(deep) else 0
        bk = beaks[f - 4:f + 1].astype(np.float64)
        beak_move_last4 = float(np.hypot(*np.diff(bk, axis=0).T).sum())
        d = beak_speeds(beaks, f - 6, f + 1)
        rows.append(dict(clip=name, coil_depth=round(depth, 2),
                         frames_at_depth_before_release=hold_frames,
                         beak_move_final4_cells=round(beak_move_last4, 1),
                         dist_final2=round(float(d[-2:].sum()), 1),
                         dist_prev2=round(float(d[-4:-2].sum()), 1),
                         peak_beak_speed_cpf=round(float(d.max()), 1)))
    out['strike_audits'] = rows
    # ---- held fraction + still stretches + beak aliveness in episode idles
    import sim as simmod
    _lat, ep_beaks, _ev, _segs, _pr = simmod.build_episode(
        model_pfx or f'/home/jim/heron/model{tag}', corpus_pfx)
    idle_stats = {}
    for nm, s in segs.items():
        if not nm.startswith('idle'):
            continue
        a, b = s['start'], s['start'] + s['count']
        ch = (G[a + 1:b] != G[a:b - 1]).reshape(s['count'] - 1, -1).sum(1)
        held = ch < 30
        # longest unbroken held stretch
        best = cur = 0
        for h in held:
            cur = cur + 1 if h else 0
            best = max(best, cur)
        bk = ep_beaks[a:b].astype(np.float64)
        path = float(np.hypot(*np.diff(bk, axis=0).T).sum())
        idle_stats[nm] = dict(held_fraction=round(float(held.mean()), 3),
                              longest_still_s=round(best / 24.0, 2),
                              beak_path_cells_per_s=round(path / (s['count'] / 24.0), 2))
    out['idle_holds'] = idle_stats
    # ---- follow-through proxy: bird-region change decay after a stop
    def decay_after(frame, label):
        ch = []
        for t in range(frame, min(frame + 14, len(G) - 1)):
            ch.append(int((G[t + 1] != G[t]).sum()))
        out[label] = ch
    land = next(e for e in log['events'] if e['type'] == 'landing')
    decay_after(land['f'], 'change_after_landing_14f')
    sp = next(e for e in log['events'] if e['type'] == 'splash')
    decay_after(sp['f'] + 30, 'change_after_first_strike_swallow_14f')
    print(json.dumps(out, indent=1))

if __name__ == '__main__':
    args = sys.argv[1:]
    kw = {}
    if len(args) > 1: kw['tag'] = args[1]
    if len(args) > 2: kw['model_pfx'] = args[2]
    main(*(args[:1]), **kw)
