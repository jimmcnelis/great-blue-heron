"""QA on the FINAL episode: palette exactness, ink discipline, zones, fish sizes, joins."""
import json, subprocess, sys
import numpy as np
from PIL import Image
import rig

FFMPEG = '/home/jim/wedding/tools/ffmpeg-7.0.2-arm64-static/ffmpeg'
SURF = rig.SURF_ROW

def water_ink(g):
    return int((g[SURF - 6:SURF + 7] == rig.INK).sum())

def centroid(g):
    ys, xs = np.nonzero(g != rig.WHITE)
    return float(xs.mean()) if len(xs) else -1.0

def fish_cells(g):
    return int(np.isin(g, [rig.FISH, rig.FISH2, 11]).sum())

def main(mp4='/home/jim/heron/preview_heron_v1.mp4'):
    G = np.load('/home/jim/heron/episode_grids.npy')
    log = json.load(open('/home/jim/heron/episode_log.json'))
    segs = {s['name']: s for s in log['segments']}
    out = {}
    # 1 palette exactness (index domain)
    out['grid_values'] = sorted(np.unique(G).tolist())
    out['palette_exact_index_domain'] = all(0 <= v < 12 for v in out['grid_values'])
    # mp4 near-palette fraction
    fr = subprocess.run([FFMPEG, '-y', '-v', 'error', '-i', mp4, '-vf', 'fps=1/8',
                         '/tmp/qa_mp4_%02d.png'], capture_output=True)
    import glob
    near = tot = 0
    for fn in sorted(glob.glob('/tmp/qa_mp4_*.png')):
        im = np.asarray(Image.open(fn).convert('RGB'), dtype=np.int32)
        d = np.min(((im[:, :, None, :] - rig.PALETTE[None, None, :, :].astype(np.int32)) ** 2).sum(-1), axis=2)
        near += int((d <= 14 ** 2).sum()); tot += d.size
    out['mp4_near_palette_frac'] = round(near / max(tot, 1), 4)
    # 2 ink discipline
    def seg_range(name):
        s = segs[name]; return s['start'], s['start'] + s['count']
    a, b = seg_range('idle_C_3')
    out['ink_final_idle_last2.5s_max'] = max(water_ink(G[i]) for i in range(b - 30, b))
    a, b = seg_range('idle_L_0')
    out['ink_first_idle_last3s_max'] = max(water_ink(G[i]) for i in range(b - 36, b))
    a, b = seg_range('empty')
    out['ink_empty_after_1.7s_max'] = max(water_ink(G[i]) for i in range(a + 20, b))
    step_frames = [e['f'] for e in log['events'] if e['type'] == 'step']
    hits = sum(1 for f in step_frames if max(water_ink(G[j]) for j in range(max(0, f - 1), min(len(G), f + 4))) > 0)
    out['step_events'] = len(step_frames)
    out['step_events_with_ink'] = hits
    splash = [e for e in log['events'] if e['type'] in ('splash', 'takeoff', 'landing')]
    out['big_events'] = len(splash)
    out['big_events_with_ink'] = sum(1 for e in splash
                                     if max(water_ink(G[j]) for j in range(e['f'], min(len(G), e['f'] + 6))) > 0)
    # 3 zones
    def seg_centroid(name, frac=0.5):
        s = segs[name]; i = s['start'] + int(s['count'] * frac)
        return round(centroid(G[i]), 1)
    out['centroid_idle_L'] = seg_centroid('idle_L_0')
    out['centroid_strike_tiny'] = seg_centroid('strike_tiny_0', 0.25)
    out['centroid_idle_R'] = seg_centroid('idle_L_1_m')
    out['centroid_alert'] = seg_centroid('alert_L_0')
    out['centroid_final_idle_C'] = seg_centroid('idle_C_3')
    # 4 fish sizes in-episode
    def seg_fish_max(name):
        s = segs[name]
        return max(fish_cells(G[i]) for i in range(s['start'], s['start'] + s['count']))
    out['fish_cells_tiny_episode'] = seg_fish_max('strike_tiny_0')
    out['fish_cells_big_episode'] = seg_fish_max('strike_big_0')
    # 5 presence
    out['presence_events'] = log['presence']
    # 6 join smoothness (decoded-domain): cell-change at joins vs median change
    changes = np.array([int((G[i] != G[i - 1]).sum()) for i in range(1, len(G))])
    joins = [s['start'] for s in log['segments'][1:]]
    out['median_frame_change'] = float(np.median(changes))
    out['max_join_change'] = int(max(changes[j - 1] for j in joins))
    out['episode_frames'] = len(G)
    out['episode_seconds'] = round(len(G) / 12, 1)
    print(json.dumps(out, indent=1))
    with open('/home/jim/heron/qa_results.json', 'w') as f:
        json.dump(out, f, indent=1)
    # contact sheet: segment midpoints + event frames
    picks = []
    for s in log['segments']:
        picks.append((s['name'], s['start'] + s['count'] // 2))
    for e in log['events']:
        if e['type'] in ('splash', 'landing', 'takeoff'):
            picks.append((e['type'], min(e['f'] + 2, len(G) - 1)))
    picks = picks[:16]
    cols = 4
    rows = int(np.ceil(len(picks) / cols))
    sheet = Image.new('RGB', (400 * cols, 300 * rows), (255, 255, 255))
    for i, (nm, fi) in enumerate(picks):
        im = Image.fromarray(rig.PALETTE[G[fi]]).resize((400, 300), Image.NEAREST)
        sheet.paste(im, ((i % cols) * 400, (i // cols) * 300))
    sheet.save('/home/jim/heron/qa_contact_sheet.jpg', quality=88)
    print('contact sheet saved:', [p[0] for p in picks])

if __name__ == '__main__':
    main(*sys.argv[1:])
