"""QA on the FINAL v1.1 episode: palette exactness, ink discipline, zones, fish
sizes, joins, body pitch, plus export of the four gate frames."""
import json, os, subprocess, sys
import numpy as np
from PIL import Image
import rig

FFMPEG = '/home/jim/wedding/tools/ffmpeg-7.0.2-arm64-static/ffmpeg'
SURF = rig.SURF_ROW
FPS = 24
BAND = int(round(6 * rig.H / 120.0))

def water_ink(g):
    return int((g[SURF - BAND:SURF + BAND + 1] == rig.INK).sum())

def body_axis_deg(g):
    """PCA axis of the slate body mass (neck is PALE, legs are below the clip):
    returns the body's pitch in degrees from horizontal (descent toward tail)."""
    m = np.isin(g, [rig.SLATE, rig.DARKSLATE])
    ys, xs = np.nonzero(m)
    if len(xs) < 50:
        return None
    X = np.stack([xs - xs.mean(), ys - ys.mean()], axis=1).astype(float)
    cov = X.T @ X / len(X)
    evals, evecs = np.linalg.eigh(cov)
    v = evecs[:, -1]
    return round(float(np.degrees(np.arctan2(abs(v[1]), abs(v[0])))), 1)

def centroid(g):
    ys, xs = np.nonzero(g != rig.WHITE)
    return float(xs.mean()) if len(xs) else -1.0

def fish_cells(g):
    return int(np.isin(g, [rig.FISH, rig.FISH2, 11]).sum())

def main(mp4='/home/jim/heron/preview_heron_v1_1.mp4', tag='11'):
    G = np.load(f'/home/jim/heron/episode_grids_{tag}.npy')
    log = json.load(open(f'/home/jim/heron/episode_log_{tag}.json'))
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
    out['ink_final_idle_last2.5s_max'] = max(water_ink(G[i]) for i in range(b - int(2.5 * FPS), b))
    a, b = seg_range('idle_L_0')
    out['ink_first_idle_last3s_max'] = max(water_ink(G[i]) for i in range(b - 3 * FPS, b))
    a, b = seg_range('empty')
    out['ink_empty_after_1.7s_max'] = max(water_ink(G[i]) for i in range(a + int(1.7 * FPS), b))
    step_frames = [e['f'] for e in log['events'] if e['type'] == 'step']
    hits = sum(1 for f in step_frames if max(water_ink(G[j]) for j in range(max(0, f - 2), min(len(G), f + 9))) > 0)
    out['step_events'] = len(step_frames)
    out['step_events_with_ink'] = hits
    splash = [e for e in log['events'] if e['type'] in ('splash', 'takeoff', 'landing')]
    out['big_events'] = len(splash)
    out['big_events_with_ink'] = sum(1 for e in splash
                                     if max(water_ink(G[j]) for j in range(e['f'], min(len(G), e['f'] + 13))) > 0)
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
    out['episode_seconds'] = round(len(G) / FPS, 1)
    # body pitch on idle stance frames (start, middle, final idle)
    pitches = []
    for nm in ('idle_L_0', 'idle_C_3'):
        s = segs[nm]
        for fr in (0.3, 0.55, 0.8):
            d = body_axis_deg(G[s['start'] + int(s['count'] * fr)])
            if d is not None:
                pitches.append(d)
    out['body_axis_deg_samples'] = pitches
    print(json.dumps(out, indent=1))
    with open(f'/home/jim/heron/qa_results_{tag}.json', 'w') as f:
        json.dump(out, f, indent=1)
    # ---- gate frames: idle stance / flight / strike / at-rest
    gdir = f'/home/jim/heron/qa_frames_{tag}'
    os.makedirs(gdir, exist_ok=True)
    def seg_frame(name, frac):
        s = segs[name]
        return s['start'] + int(s['count'] * frac)
    splash_f = next(e['f'] for e in log['events'] if e['type'] == 'splash')
    gates = {
        'gate_idle_stance': seg_frame('idle_L_0', 0.45),
        'gate_flight_flyin': seg_frame('flyin_L_0', 0.30),
        'gate_flight_takeoff': seg_frame('takeoff_R_0', 0.62),
        'gate_strike': min(splash_f + 3, len(G) - 1),
        'gate_alert': seg_frame('alert_L_0', 0.5),
        'gate_rest_final': len(G) - 1,
    }
    up = max(1, 960 // rig.W)
    for nm, fi in gates.items():
        Image.fromarray(rig.PALETTE[G[fi]]).resize((rig.W * up, rig.H * up), Image.NEAREST).save(f'{gdir}/{nm}.png')
    out['gate_frames'] = gates
    print('gate frames saved:', gates)
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
    sheet.save(f'/home/jim/heron/qa_contact_sheet_{tag}.jpg', quality=88)
    print('contact sheet saved:', [p[0] for p in picks])

if __name__ == '__main__':
    args = sys.argv[1:]
    main(*(args[:1]), **({'tag': args[1]} if len(args) > 1 else {}))
