"""Episode renderer + QA for v1.3 phase 1.
Renders the single authored performance twice (naturalist / storybook)
from identical pose data, encodes both mp4s, and writes QA artifacts:
contact strips + audit numbers (floor only — the eye review is separate).
"""
import os, sys, pickle, subprocess, time
import numpy as np
from multiprocessing import Pool
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig13 as R
import cycles13 as C
import ink13 as I

OUT = os.path.expanduser('~/workspace/heron')
TMP = '/tmp/heron13_frames'

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
    out = f'{OUT}/preview_heron_v1_3_{style}.mp4'
    subprocess.run(['ffmpeg', '-y', '-framerate', '24', '-i', f'{TMP}/{style}/f%04d.png',
                    '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p',
                    '-movflags', '+faststart', out], check=True,
                   capture_output=True)
    return out

def strip(style, frames, name, sel):
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
    # held fraction in the closing statue (pure holds + 3 event beats)
    same = sum(1 for f in range(449, C.N) if frames[f] == frames[f - 1])
    a['closing_statue_held_fraction'] = round(same / (C.N - 449), 3)
    same = sum(1 for f in range(1, 132) if frames[f] == frames[f - 1])
    a['opening_statue_held_fraction'] = round(same / 131, 3)
    # anticipation: bill-tip travel during loaded hold vs release peak speed
    tips = [R.bill_tip(frames[f]) for f in range(300, 332)]
    path = [float(np.hypot(*(tips[i + 1] - tips[i]))) for i in range(len(tips) - 1)]
    a['loaded_hold_tip_path_max_per_frame'] = round(max(path[6:22]), 2)   # f306-321
    a['release_tip_peak_speed'] = round(max(path[22:26]), 2)              # f322-325
    a['spacing_ratio'] = round(max(path[22:26]) / max(max(path[6:22]), 0.01), 1)
    a['strike_contact_tip'] = [round(float(v), 1) for v in R.bill_tip(frames[326])]
    a['ink_events'] = len(ink)
    a['fish_airborne_frames'] = sum(1 for f in range(C.N) if frames[f]['fish_mode'] == 'free')
    return a

def main():
    os.makedirs(TMP, exist_ok=True)
    frames, ink = C.build_episode()
    assert all(f is not None for f in frames)
    with open(f'{TMP}/episode.pkl', 'wb') as fh:
        pickle.dump((frames, ink), fh)
    np.savez_compressed(f'{OUT}/src13/episode13_poses.npz',
                        frames=np.array([repr(f) for f in frames]))
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
    strip('naturalist', frames, 'v1_3_strip_naturalist.jpg',
          [60, 141, 160, 312, 326, 340, 352, 364, 385, 410, 440, 560])
    strip('storybook', frames, 'v1_3_strip_storybook.jpg',
          [60, 141, 160, 312, 326, 340, 352, 364, 385, 410, 440, 560])
    a = audits(frames, ink)
    # ink at rest: frame 60 has no live events by construction; verify pixels
    g = np.array(Image.open(f'{TMP}/naturalist/f0060.png'))
    ink_rgb = (g == np.array([0, 0, 0], dtype=np.uint8)).all(axis=2)
    a['ink_pixels_at_rest_f60'] = int(ink_rgb.sum())
    # silhouette stop areas
    areas = {}
    for yaw, kw in ((0, {}), (45, dict(hx=13, hy=-27)),
                    (90, dict(hx=-2, hy=-27, body_tilt=4, coil=0.3))):
        p = R.default_pose(); p['root_x'] = 58.0; p['yaw'] = yaw; p.update(kw)
        gg = R.render(p, 'silhouette')
        areas[yaw] = int((gg == R.INK).sum())
    areas[135] = areas[45]; areas[180] = areas[0]
    m = np.mean(list(areas.values()))
    a['silhouette_stop_areas'] = areas
    a['silhouette_stop_max_dev_pct'] = round(100 * max(abs(v - m) / m for v in areas.values()), 1)
    import json
    with open(f'{OUT}/src13/qa13.json', 'w') as fh:
        json.dump(a, fh, indent=1)
    print(json.dumps(a, indent=1))

if __name__ == '__main__':
    main()
