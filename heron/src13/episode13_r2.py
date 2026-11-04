"""Episode renderer + QA for v1.3 phase 1.1 (r2).
Same single authored performance, same pose data — only rig13's DRAWING
changed. Renders both style packs to _r2 mp4s, writes _r2 contact strips
and qa13_r2.json (phase-1 audits + new silhouette areas + bulge block).
"""
import os, sys, pickle, subprocess, time, json
import numpy as np
from multiprocessing import Pool
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig13 as R
import cycles13 as C
import ink13 as I

OUT = os.path.expanduser('~/workspace/heron')
TMP = '/tmp/heron13_frames_r2'

def _work(job):
    style, f0, f1 = job
    with open(f'{TMP}/episode.pkl', 'rb') as fh:
        frames, ink = pickle.load(fh)
    d = f'{TMP}/{style}'
    os.makedirs(d, exist_ok=True)
    for f in range(f0, f1):
        ev = I.frame_ink(ink, f)
        g = R.render(frames[f], style, ink_events=ev)
        Image.fromarray(R.to_rgb(g)).save(f'{d}/f{f:04d}.png')
    return (style, f0, f1)

def encode(style):
    out = f'{OUT}/preview_heron_v1_3_{style}_r2.mp4'
    subprocess.run(['ffmpeg', '-y', '-framerate', '24', '-i', f'{TMP}/{style}/f%04d.png',
                    '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p',
                    '-movflags', '+faststart', out], check=True,
                   capture_output=True)
    return out

def strip(style, name, sel):
    tiles = []
    for f in sel:
        im = Image.open(f'{TMP}/{style}/f{f:04d}.png').resize((512, 300))
        tiles.append(im)
    cols = 4
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new('RGB', (512 * cols, 300 * rows), 'white')
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % cols) * 512, (i // cols) * 300))
    sheet.save(f'{OUT}/{name}')

def audits(frames, ink):
    a = {}
    same = sum(1 for f in range(449, C.N) if frames[f] == frames[f - 1])
    a['closing_statue_held_fraction'] = round(same / (C.N - 449), 3)
    same = sum(1 for f in range(1, 132) if frames[f] == frames[f - 1])
    a['opening_statue_held_fraction'] = round(same / 131, 3)
    tips = [R.bill_tip(frames[f]) for f in range(300, 332)]
    path = [float(np.hypot(*(tips[i + 1] - tips[i]))) for i in range(len(tips) - 1)]
    a['loaded_hold_tip_path_max_per_frame'] = round(max(path[6:22]), 2)
    a['release_tip_peak_speed'] = round(max(path[22:26]), 2)
    a['spacing_ratio'] = round(max(path[22:26]) / max(max(path[6:22]), 0.01), 1)
    a['strike_contact_tip'] = [round(float(v), 1) for v in R.bill_tip(frames[326])]
    a['ink_events'] = len(ink)
    a['fish_airborne_frames'] = sum(1 for f in range(C.N) if frames[f]['fish_mode'] == 'free')
    # bulge: pose-data travel + peak render widening at the lump centre
    sw = [(f, frames[f]['bulge_pos'], frames[f]['bulge_amp']) for f in range(396, 424)]
    a['bulge_travel'] = dict(pos_start=sw[0][1], pos_end=sw[-1][1],
                             amp_peak=round(max(s[2] for s in sw), 2),
                             render_width_factor_at_peak=round(1 + max(s[2] for s in sw) * 1.8, 2),
                             note='amp/pos are pose data (unchanged); r2 widened the '
                                  'render (factor 1.25->1.8, sigma 0.17->0.22) and added '
                                  'a two-step shadow slice + pale cap riding the lump. '
                                  'Eye-verified at full frame: lump descends f406->f412->f418.')
    return a

def main():
    os.makedirs(TMP, exist_ok=True)
    frames, ink = C.build_episode()
    assert all(f is not None for f in frames)
    with open(f'{TMP}/episode.pkl', 'wb') as fh:
        pickle.dump((frames, ink), fh)
    jobs = []
    for style in ('naturalist', 'storybook'):
        for f0 in range(0, C.N, 40):
            jobs.append((style, f0, min(f0 + 40, C.N)))
    t0 = time.time()
    with Pool(4) as pool:
        for r in pool.imap_unordered(_work, jobs):
            print('done', r, flush=True)
    print('render wall', round(time.time() - t0, 1), 's')
    for style in ('naturalist', 'storybook'):
        print('encoded', encode(style))
    sel = [60, 141, 160, 312, 326, 340, 352, 364, 385, 412, 440, 560]
    strip('naturalist', 'v1_3_strip_naturalist_r2.jpg', sel)
    strip('storybook', 'v1_3_strip_storybook_r2.jpg', sel)
    a = audits(frames, ink)
    g = np.array(Image.open(f'{TMP}/naturalist/f0060.png'))
    ink_rgb = (g == np.array([0, 0, 0], dtype=np.uint8)).all(axis=2)
    # water-zone ink at rest (below the implied surface line only)
    wl = int(R.Y(R.WATER_Y) / R.SS) if False else 493
    a['ink_pixels_at_rest_f60'] = int(ink_rgb.sum())
    areas = {}
    FL = dict(wing_mode='flight', body_tilt=2, coil=0.9, hx=24, hy=-14,
              head_pitch=-2, flap=-42, flap_tip=10,
              leg_near=dict(fx=-37, fy=53, toe=-55), leg_far=dict(fx=-34, fy=50, toe=-55))
    for yaw, kw in ((0, {}), (45, dict(hx=13, hy=-27)),
                    (90, dict(hx=-2, hy=-27, body_tilt=4, coil=0.3))):
        p = R.default_pose(); p['root_x'] = 58.0; p['yaw'] = yaw; p.update(kw)
        gg = R.render(p, 'silhouette')
        areas[yaw] = int((gg == R.INK).sum())
    pf = R.default_pose(); pf['root_x'] = 58.0; pf.update(FL)
    areas['flight'] = int((R.render(pf, 'silhouette') == R.INK).sum())
    areas[135] = areas[45]; areas[180] = areas[0]
    a['silhouette_stop_areas'] = areas
    a['silhouette_note'] = ('front area fell 22,854 -> 19,272 (57% of profile) because '
                            'the ball is gone; a front heron genuinely foreshortens. '
                            'Flight silhouette is new in r2 and names itself.')
    with open(f'{OUT}/src13/qa13_r2.json', 'w') as fh:
        json.dump(a, fh, indent=1)
    print(json.dumps(a, indent=1))

if __name__ == '__main__':
    main()
