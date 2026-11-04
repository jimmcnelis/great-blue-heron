"""Simulated day — run the Track B scheduler for one accelerated day,
measure it against the deep-dive's targets, and assemble a watchable
preview from the roster frames.

The measurement is taken off the scheduler's frame-level timeline
(every sim-frame classified held/motion from the charts' own phase
data, holds counted arithmetically) — never off the preview, which
is a sampled viewing copy.

Preview convention (disclosed): action clips play at full 24 fps;
ambient cycles (idle_hunt, doze) are sampled 1 frame per 4 s of
cycle; scheduler holds are sampled 1 frame per 30 sim-seconds. A
small caption (sim clock + behavior + light/tide) is burned into the
top-left corner — this is a proof render, not device art. The bird
layer only: ink effects are the episode player's layer and are not
composited here (see TRACKB_REPORT.md).
"""
import json, math, os, subprocess, sys, collections
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scheduler_trackb as S

ROSTER = os.path.expanduser('~/workspace/heron/art2/route2/roster')
CANON = {'head_turn', 'body_shake', 'strike', 'swallow', 'strike_miss',
         'relocate', 'takeoff', 'flight_cycle', 'glide', 'landing'}


def clip_folder(name):
    base = ROSTER if name in CANON else os.path.join(ROSTER, 'sim_assets')
    return os.path.join(base, 'frames', name)


def frame_path(name, idx):
    return os.path.join(clip_folder(name), f'f{idx:04d}.png')


def measure(day, tl):
    ev = day.events
    seg_frames = lambda s: len(s['frames']) if s['kind'] == 'clip' \
        else s['count']
    per_behav = collections.defaultdict(int)
    for s in tl.segments:
        per_behav[s['behavior']] += seg_frames(s)
    strikes = [e for e in ev if e['kind'] == 'strike']
    hits = [e for e in strikes if e['hit']]
    reloc = [e for e in ev if e['kind'] == 'relocate']
    maint = [e for e in ev if e['kind'] == 'bout_end'
             and e.get('behavior') == 'maintenance']
    bouts = collections.Counter(e['behavior'] for e in ev
                                if e['kind'] == 'bout_start')
    # hunting time = wall time inside hunt bouts (segments whose t0
    # falls in a bout interval)
    intervals, open_t = [], None
    for e in ev:
        if e['kind'] == 'bout_start' and e.get('behavior') == 'hunt':
            open_t = e['t']
        elif e['kind'] == 'bout_end' and e.get('behavior') == 'hunt' \
                and open_t is not None:
            intervals.append((open_t, e['t']))
            open_t = None
    hunt_s = sum(b - a for a, b in intervals)
    wake_s = (day.cfg['world']['light']['night'] -
              day.cfg['world']['light']['dawn']) * 3600
    # inter-bout gaps measured bout_end -> next bout_start from the
    # event stream (timeline hold segments are chunked at clip
    # length, so per-segment durations are not bout gaps)
    marks = [(e['t'], e['kind']) for e in ev
             if e['kind'] in ('bout_start', 'bout_end')]
    gaps = []
    last_end = None
    for t, kind in marks:
        if kind == 'bout_end':
            last_end = t
        elif kind == 'bout_start' and last_end is not None:
            gaps.append((t - last_end) / 60.0)
            last_end = None
    m = {
        'total_frames': tl.total_frames,
        'held_frames': tl.held_frames,
        'held_share': round(tl.held_frames / tl.total_frames, 4),
        'per_behavior_min': {k: round(v / S.FPS / 60, 1)
                             for k, v in sorted(per_behav.items())},
        'bouts': dict(bouts),
        'strikes': len(strikes),
        'hits': len(hits),
        'misses': len(strikes) - len(hits),
        'success': round(len(hits) / len(strikes), 3) if strikes else None,
        'big_hits': sum(1 for e in hits if e['big']),
        'strikes_per_hunt_hour': round(len(strikes) / (hunt_s / 3600), 2),
        'hunting_min': round(hunt_s / 60, 1),
        'hunt_share_waking': round(hunt_s / wake_s, 3),
        'relocations': dict(collections.Counter(
            e['mode'] for e in reloc)),
        'relocate_share': round(
            sum(1 for e in reloc if e['mode'] != 'none') /
            max(1, len(strikes)), 3),
        'maintenance_bouts': len(maint),
        'maintenance_sequences': [e['sequence'] for e in maint],
        'flights_by_label': dict(collections.Counter(
            e['label'] for e in ev if e['kind'] == 'flight')),
        'drinks': sum(1 for e in ev if e['kind'] == 'drink'),
        'shakes_after_landing': sum(
            1 for e in ev if e['kind'] == 'shake_after_landing'),
        'ladder': [(e['step'], e['disturbance']) for e in ev
                   if e['kind'] == 'ladder'],
        'gap_min_median': round(float(np.median(gaps)), 1)
        if gaps else None,
        'gap_min_p90': round(float(np.percentile(gaps, 90)), 1)
        if gaps else None,
        'gap_min_max': round(max(gaps), 1) if gaps else None,
    }
    return m


TARGETS = [
    ('held_share', '>= 0.90 of all frames held (deep-dive §3.1)',
     lambda m: m['held_share'] >= 0.90),
    ('success', '~0.56 strike success [Documented Hodgens] (band 0.46-0.66 for a single day)',
     lambda m: 0.46 <= m['success'] <= 0.66),
    ('strikes_per_hunt_hour', '~4/h of hunting [Documented] (design band 3-6)',
     lambda m: 3.0 <= m['strikes_per_hunt_hour'] <= 6.0),
    ('hunt_share_waking', '0.30-0.50 of waking hours [Documented Brandman]',
     lambda m: 0.30 <= m['hunt_share_waking'] <= 0.50),
    ('relocate_share', 'relocation after ~every strike [Documented Warrick] (>= 0.80)',
     lambda m: m['relocate_share'] >= 0.80),
    ('maintenance_bouts', '2-5 bouts/day, order stretch->shake->preen',
     lambda m: 2 <= m['maintenance_bouts'] <= 5),
]


def comparisons(m):
    out = []
    for key, desc, fn in TARGETS:
        out.append({'metric': key, 'target': desc,
                    'measured': m[key], 'verdict': 'PASS' if fn(m)
                    else 'MISS'})
    return out


AMBIENT = {'idle_hunt_at_stand', 'doze_at_stand'}


def build_preview(day, tl, out_mp4, workdir):
    from PIL import Image, ImageDraw, ImageFont
    os.makedirs(workdir, exist_ok=True)
    try:
        font = ImageFont.truetype(
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 17)
    except Exception:
        font = ImageFont.load_default()
    cache = {}

    def load(path):
        if path not in cache:
            cache.clear()
            cache[path] = Image.open(path).convert('RGB')
        return cache[path]

    def caption(im, t_s, seg):
        h = int(t_s // 3600)
        mi = int((t_s % 3600) // 60)
        phase = day.world.light_phase(t_s)
        _, ebb = day.world.tide_state(t_s)
        tide = 'ebb' if ebb > 0.05 else 'flood'
        txt = (f"SIM DAY 10-15  {h:02d}:{mi:02d}  ·  {seg['behavior']}"
               f"{(' — ' + seg['label']) if seg.get('label') else ''}"
               f"  ·  {phase} / {tide}")
        dr = ImageDraw.Draw(im)
        dr.rectangle([8, 8, 8 + 8 * len(txt) + 12, 34], fill=(255, 255, 255))
        dr.text((14, 12), txt, fill=(90, 90, 90), font=font)
        return im

    n_out = 0
    for seg in tl.segments:
        if seg['kind'] == 'clip':
            idxs = seg['frames']
            stride = 96 if seg['clip'] in AMBIENT else 1
            for j in range(0, len(idxs), stride):
                im = load(frame_path(seg['clip'], idxs[j])).copy()
                caption(im, seg['t0'] + idxs[j] / S.FPS, seg)
                im.save(os.path.join(workdir, f'f{n_out:06d}.png'))
                n_out += 1
        else:
            dur_s = seg['count'] / S.FPS
            reps = max(1, int(round(dur_s / 30.0)))
            src = load(frame_path(seg['clip'], seg['frame']))
            for r in range(reps):
                im = src.copy()
                caption(im, seg['t0'] + dur_s * r / reps, seg)
                im.save(os.path.join(workdir, f'f{n_out:06d}.png'))
                n_out += 1
    subprocess.run(['ffmpeg', '-y', '-framerate', '24', '-i',
                    os.path.join(workdir, 'f%06d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                    '-crf', '21', out_mp4],
                   check=True, capture_output=True)
    return n_out


if __name__ == '__main__':
    day, tl = S.run_day()
    m = measure(day, tl)
    m['comparisons'] = comparisons(m)
    m['events'] = day.events
    out_json = os.path.join(ROSTER, 'sim_day_log.json')
    with open(out_json, 'w') as f:
        json.dump(m, f, indent=1)
    print(json.dumps({k: v for k, v in m.items() if k != 'events'},
                     indent=1))
    print('wrote', out_json)
    if '--preview' in sys.argv:
        workdir = os.path.expanduser(
            '~/workspace/heron/art2/.sim_frames')
        import shutil
        shutil.rmtree(workdir, ignore_errors=True)
        n = build_preview(day, tl, os.path.join(ROSTER,
                                                 'sim_day_preview.mp4'),
                          workdir)
        print(f'preview: {n} frames = {n / 24:.1f} s')
